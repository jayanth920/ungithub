from fastapi import FastAPI
from dotenv import load_dotenv
import shutil
import os
import sys
import json
import math
import logging
import certifi
import tempfile
import tiktoken
import time
from pymongo import MongoClient
from urllib.parse import urlparse
from more_itertools import chunked


# Local modules
from repo_cloner import clone_repo
from file_scanner import get_code_files, read_and_metadata
from chunker import split_into_chunks
from save_jsonl import save_chunks_jsonl
from embedding import get_embeddings  # Updated to batch embeddings

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
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("uvicorn")

# Token truncation setup
MAX_EMBED_TOKENS = 2048
encoding = tiktoken.get_encoding("cl100k_base")

def safe_truncate(text: str, max_tokens=MAX_EMBED_TOKENS) -> str:
    tokens = encoding.encode(text)
    if len(tokens) <= max_tokens:
        return text
    truncated = encoding.decode(tokens[:max_tokens])
    return truncated

def get_repo_id(repo_url: str) -> str:
    parts = urlparse(repo_url).path.strip("/").split("/")
    if len(parts) != 2:
        raise ValueError("Invalid GitHub repo URL")
    owner, repo = parts
    return f"{owner}/{repo}"

def process_repo(repo_url):
    repo_id = get_repo_id(repo_url)  # e.g., "owner/repo"
    sanitized_repo_id = repo_id.replace("/", "__")  # safe for folder names

    with tempfile.TemporaryDirectory() as temp_dir:
        repo_dir = clone_repo(repo_url, dest_dir=os.path.join(temp_dir, sanitized_repo_id))
        files = get_code_files(repo_dir)
        logger.info("📂 Got all files")

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

        jsonl_path = os.path.join(temp_dir, f"{sanitized_repo_id}_chunks.jsonl")
        save_chunks_jsonl(all_chunks, path=jsonl_path)

        # Insert to MongoDB with batching
        inserted_count = 0
        BATCH_SIZE = 50
        with open(jsonl_path, "r") as f:
            lines = [json.loads(line) for line in f]
        
        for batch in chunked(lines, BATCH_SIZE):
            contents = [safe_truncate(chunk["content"]) for chunk in batch]
            try:
                embeddings = get_embeddings(contents)
            except Exception as e:
                logger.warning(f"⚠️ Skipping batch due to embedding error: {e}")
                time.sleep(1)
                continue

            for chunk, embedding in zip(batch, embeddings):
                try:
                    doc = {
                        "repo_id": repo_id,
                        "content": chunk["content"],
                        "filepath": chunk["filepath"],
                        "language": chunk["language"],
                        "embedding": embedding
                    }
                    collection.insert_one(doc)
                    inserted_count += 1
                except Exception as e:
                    logger.warning(f"❌ Failed to insert chunk: {e}")
            time.sleep(0.5)  # gentle pacing between batches

        logger.info(f"✅ Inserted {inserted_count} chunks into MongoDB for repo '{repo_id}'")
        print(f"✅ Inserted {inserted_count} chunks into MongoDB for repo '{repo_id}'")

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
