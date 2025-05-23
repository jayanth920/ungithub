from fastapi import FastAPI
from dotenv import load_dotenv
import os
import sys

# Local modules
from repo_cloner import clone_repo
from file_scanner import get_code_files, read_and_metadata
from chunker import split_into_chunks
from save_jsonl import save_chunks_jsonl

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

app = FastAPI()

@app.get("/ping")
def ping():
    return {"message": "pong"}

def process_repo(repo_url):
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

# CLI entry
if __name__ == "__main__":
    if len(sys.argv) == 2:
        repo_url = sys.argv[1]
        process_repo(repo_url)
    else:
        print("💡 To process a GitHub repo: python main.py <github_repo_url>")
        print("💡 To run API server: uvicorn main:app --reload")
