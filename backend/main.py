from fastapi import FastAPI
from dotenv import load_dotenv
import shutil
import os
import sys
import json
import certifi
import tempfile
import logging
from pymongo import MongoClient
from urllib.parse import urlparse


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

def get_repo_id(repo_url: str) -> str:
    parts = urlparse(repo_url).path.strip("/").split("/")
    if len(parts) != 2:
        raise ValueError("Invalid GitHub repo URL")
    owner, repo = parts
    return f"{owner}/{repo}"


def process_repo(repo_url):
    repo_id = get_repo_id(repo_url)  # e.g., "owner/repo"
    sanitized_repo_id = repo_id.replace("/", "__")  # safe for folder names

    # Create a temporary working directory
    with tempfile.TemporaryDirectory() as temp_dir:
        repo_dir = clone_repo(repo_url, dest_dir=os.path.join(temp_dir, sanitized_repo_id))

        files = get_code_files(repo_dir)
        all_chunks = []

        for file_path in files:
            meta = read_and_metadata(file_path, repo_dir, repo_id)
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

        # Save JSONL to a unique path
        jsonl_path = os.path.join(temp_dir, f"{sanitized_repo_id}_chunks.jsonl")
        save_chunks_jsonl(all_chunks, path=jsonl_path)

        # Insert chunks into MongoDB
        inserted_count = 0
        with open(jsonl_path, "r") as f:
            for line in f:
                chunk = json.loads(line)
                embedding = get_embedding(chunk["content"]).values

                doc = {
                    "repo_id": repo_id,
                    "content": chunk["content"],
                    "filepath": chunk["filepath"],
                    "language": chunk["language"],
                    "embedding": embedding
                }
                collection.insert_one(doc)
                inserted_count += 1

        logger.info(f"✅ Inserted {inserted_count} chunks into MongoDB for repo '{repo_id}'")
        print(f"✅ Inserted {inserted_count} chunks into MongoDB for repo '{repo_id}'")

    # All temp files auto cleaned here ✅

# CLI entry
if __name__ == "__main__":
    if len(sys.argv) == 2:
        repo_url = sys.argv[1]
        process_repo(repo_url)
    else:
        logger.info("💡 To process a GitHub repo: python main.py <github_repo_url>")
        print("💡 To process a GitHub repo: python main.py <github_repo_url>")
        logger.info("💡 To run API server: uvicorn main:app --reload")
        print("💡 To run API server: uvicorn main:app --reload")
