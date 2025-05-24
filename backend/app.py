# app.py

import time
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from pymongo import MongoClient
from dotenv import load_dotenv
import os
import certifi
from embedding import get_embedding
from google import genai
from main import process_repo
from urllib.parse import urlparse

load_dotenv()

# MongoDB setup
client = MongoClient(os.getenv("MONGODB_URI"), tlsCAFile=certifi.where())
collection = client["unrepo"]["code_chunks"]

# Gemini setup
genai_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# FastAPI app
app = FastAPI()

class QueryRequest(BaseModel):
    question: str
    repo_url: str
    
def is_valid_github_repo_url(url: str) -> bool:
    """
    Returns True if the URL is a valid GitHub repo URL like https://github.com/owner/repo
    """
    try:
        parsed = urlparse(url)
        if parsed.scheme != "https" or parsed.netloc != "github.com":
            return False
        parts = parsed.path.strip("/").split("/")
        return len(parts) == 2
    except Exception:
        return False

@app.get("/ping")
def ping():
    return {"message": "pong"}

@app.post("/query")
def query_codebase(request: QueryRequest):
    
    # Validating fields
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")
    if not request.repo_url.strip():
        raise HTTPException(status_code=400, detail="Repo URL cannot be empty.")
    
    # Validate GitHub URL
    if not is_valid_github_repo_url(request.repo_url):
        raise HTTPException(status_code=400, detail="Invalid GitHub repo URL. Must be of the form https://github.com/owner/repo")
    
    repo_id = request.repo_url.rstrip("/").split("/")[-1]
    
    # Step 0: Check if repo is indexed
    repo_exists = collection.find_one({"repo_id": repo_id})

    if not repo_exists:
        try:
            process_repo(request.repo_url)  # repo_id is the full GitHub URL now
            time.sleep(2)  # optional short wait to let MongoDB settle
            repo_exists = collection.find_one({"repo_id": repo_id})
            if not repo_exists:
                raise HTTPException(status_code=404, detail="Repo could not be indexed or found.")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to index repo: {str(e)}")

    # Step 1: Get embedding for the user's question
    embedding_obj = get_embedding(request.question)
    embedding = embedding_obj.values  # assuming ContentEmbedding object

    # Step 2: Perform vector search
    results = collection.aggregate([
        {
            "$vectorSearch": {
                "index": "default",
                "path": "embedding",
                "queryVector": embedding,
                "filter": {"repo_id": repo_id},
                "numCandidates": 100,
                "limit": 5
            }
        }
    ])
    top_chunks = list(results)

    if not top_chunks:
        raise HTTPException(status_code=404, detail="No relevant chunks found.")

    # Step 3: Combine retrieved chunks
    context = "\n\n".join([f"{chunk['content']} (from {chunk['filepath']})" for chunk in top_chunks])

    # Step 4: Ask Gemini to summarize/answer using the context
    prompt = f"""You are a codebase expert. Based on the following code snippets, answer the question:

Context:
{context}

Question:
{request.question}

Answer:"""

    response = genai_client._models.generate_content(model="gemini-2.0-flash",contents=prompt)

    return {
        "answer": response.text,
        "citations": list(set(chunk["filepath"] for chunk in top_chunks))

    }