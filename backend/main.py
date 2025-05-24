from fastapi import FastAPI
from dotenv import load_dotenv
import shutil
import os
import sys
import json
import certifi
import logging
from pymongo import MongoClient

# Local modules
from repo_cloner import clone_repo
from file_scanner import get_code_files, read_and_metadata
from chunker import split_into_chunks
from save_jsonl import save_chunks_jsonl
from embedding import get_embedding

# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MONGODB_URI = os.getenv("MONGODB_URI")

# MongoDB setup
client = MongoClient(MONGODB_URI, tlsCAFile=certifi.where())
collection = client["unrepo"]["code_chunks"]

# FastAPI app
app = FastAPI()

# Logger setup
logger = logging.getLogger("uvicorn")

@app.get("/ping")
def ping():
    return {"message": "pong"}

def process_repo(repo_url):
    # Step 1: Clone and chunk
    repo_name = repo_url.rstrip("/").split("/")[-1]
    repo_dir = clone_repo(repo_url)

    files = get_code_files(repo_dir)
    all_chunks = []

    for file_path in files:
        meta = read_and_metadata(file_path, repo_name)
        if not meta:
            continue
        chunks = split_into_chunks(meta["content"])
        for i, chunk in enumerate(chunks):
            all_chunks.append({
                "content": chunk,
                "filepath": meta["filepath"],
                "repo": meta["repo"],
                "language": meta["language"],
                "chunk_id": i
            })

    save_chunks_jsonl(all_chunks)

    # Step 2: Populate DB
    # collection.delete_many({}) # FOR NOW I'LL EMPTY THE DB FOR SPACE, so we basically can have only 1 repo
    # logger.info("🧹 Cleared collection")
    
    inserted_count = 0
    with open("data/chunks.jsonl", "r") as f:
        for line in f:
            chunk = json.loads(line)
            embedding = get_embedding(chunk["content"]).values

            doc = {
                "repo_id": repo_name,
                "content": chunk["content"],
                "filepath": chunk["filepath"],
                "language": chunk["language"],
                "embedding": embedding
            }
            collection.insert_one(doc)
            inserted_count += 1

    logger.info(f"✅ Inserted {inserted_count} chunks into MongoDB for repo '{repo_name}'")
    
    # Clean up cloned repo folder
    try:
        shutil.rmtree(repo_dir)
        logger.info(f"🧹 Deleted cloned repo folder: {repo_dir}")
    except Exception as e:
        logger.warning(f"⚠️ Failed to delete cloned folder '{repo_dir}': {e}")
        
    # Clean up chunks file and data directory
    try:
        shutil.rmtree("data")
        logger.info("🧹 Deleted 'data/' directory after uploading chunks")
    except Exception as e:
        logger.warning(f"⚠️ Failed to delete 'data/' directory: {e}")

# CLI entry
if __name__ == "__main__":
    if len(sys.argv) == 2:
        repo_url = sys.argv[1]
        process_repo(repo_url)
    else:
        logger.info("💡 To process a GitHub repo: python main.py <github_repo_url>")
        logger.info("💡 To run API server: uvicorn main:app --reload")
