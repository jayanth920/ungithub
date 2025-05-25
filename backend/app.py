import os
import time
import certifi
import logging
import tiktoken
from google import genai
from main import process_repo
from pydantic import BaseModel
from dotenv import load_dotenv
from pymongo import MongoClient
from urllib.parse import urlparse
from embedding import get_embedding
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException, Request, BackgroundTasks


load_dotenv()

# Logger setup
logger = logging.getLogger("uvicorn")

# MongoDB setup
client = MongoClient(os.getenv("MONGODB_URI"), tlsCAFile=certifi.where())
collection = client["unrepo"]["code_chunks"]

# Gemini setup
genai_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# FastAPI app
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or ["http://localhost:3000"] for more security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
    # Basic field validation
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")
    if not request.repo_url.strip():
        raise HTTPException(status_code=400, detail="Repo URL cannot be empty.")

    # GitHub URL format check
    if not is_valid_github_repo_url(request.repo_url):
        raise HTTPException(
            status_code=400,
            detail="Invalid GitHub repo URL. Must be of the form https://github.com/owner/repo",
        )

    # ✅ Token and length checks BEFORE any indexing
    MAX_QUESTION_CHARS = 1000
    MAX_EMBEDDING_TOKENS = 2048
    encoding = tiktoken.get_encoding("cl100k_base")

    def count_tokens(text: str) -> int:
        return len(encoding.encode(text))

    if len(request.question) > MAX_QUESTION_CHARS:
        raise HTTPException(
            status_code=400,
            detail=f"Question too long. Limit is {MAX_QUESTION_CHARS} characters.",
        )
    if count_tokens(request.question) > MAX_EMBEDDING_TOKENS:
        raise HTTPException(
            status_code=400,
            detail=f"Your question is too long. Please shorten it to stay under {MAX_EMBEDDING_TOKENS} tokens.",
        )

    # Then proceed to indexing
    repo_id = request.repo_url.rstrip("/").split("/")[-1]
    repo_exists = collection.find_one({"repo_id": repo_id})

    if not repo_exists:
        try:
            logger.info(f"🔍 Indexing repo: {request.repo_url}")
            process_repo(request.repo_url)
            # wait a short time to see if it's quickly indexed
            time.sleep(3)
            repo_exists = collection.find_one({"repo_id": repo_id})
            if not repo_exists:
                # Still not found after processing → tell frontend to wait/retry
                return JSONResponse(
                    status_code=202,
                    content={
                        "status": "indexing",
                        "message": "Repository is being indexed. Please try again shortly.",
                    },
                )

        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to index repo: {str(e)}"
            )
    else:
        logger.info(f"✅ Repo already indexed: {request.repo_url}")

    # Step 1: Get embedding for the user's question
    embedding_obj = get_embedding(request.question)
    embedding = embedding_obj.values  # ContentEmbedding object

    # Step 2: Perform vector search
    results = collection.aggregate(
        [
            {
                "$vectorSearch": {
                    "index": "default",
                    "path": "embedding",
                    "queryVector": embedding,
                    "filter": {"repo_id": repo_id},
                    "numCandidates": 100,
                    "limit": 5,
                }
            }
        ]
    )
    top_chunks = list(results)

    if not top_chunks:
        raise HTTPException(status_code=404, detail="No relevant chunks found.")

    # Step 3: Combine retrieved chunks
    context = "\n\n".join(
        [f"{chunk['content']} (from {chunk['filepath']})" for chunk in top_chunks]
    )

    # Step 4: Ask Gemini to summarize/answer using the context
    prompt = f"""You are a codebase expert. Based on the following code snippets, answer the question:

Context:
{context}

Question:
{request.question}

Answer:"""

    response = genai_client._models.generate_content(
        model="gemini-2.0-flash", contents=prompt
    )

    return {
        "answer": response.text,
        "citations": list(set(chunk["filepath"] for chunk in top_chunks)),
    }


from fastapi import Query

@app.get("/repo-status")
def check_repo_status(repo_id: str = Query(..., description="The repo ID (usually the repo name)")):
    """
    Check whether a repository has been indexed.
    """
    repo_exists = collection.find_one({"repo_id": repo_id})
    if repo_exists:
        return {"status": "indexed"}
    return JSONResponse(status_code=202, content={"status": "indexing"})
