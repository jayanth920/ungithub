import json
import os
import logging
from dotenv import load_dotenv
from pymongo import MongoClient
import certifi
from embedding import get_embedding  # Gemini embedding

logger = logging.getLogger("uvicorn")

load_dotenv()

client = MongoClient(os.getenv("MONGODB_URI"), tlsCAFile=certifi.where())
collection = client["unrepo"]["code_chunks"]

# Clear collection (optional for testing)
collection.delete_many({})

# Set a repo_id (can be dynamic later)
REPO_ID = "jayanth920/s2t-t2s"  # or extract dynamically based on repo you cloned

inserted_count = 0

# Read and insert each line (chunk)
with open("data/chunks.jsonl", "r") as f:
    for line in f:
        chunk = json.loads(line)
        content = chunk["content"]
        embedding = get_embedding(content).values  # Use .values to get raw floats

        doc = {
            "repo_id": REPO_ID,  # ✅ Add repo_id
            "content": content,
            "filepath": chunk["filepath"],
            "language": chunk["language"],
            "embedding": embedding
        }
        collection.insert_one(doc)
        inserted_count += 1

logger.info(f"✅ Inserted {inserted_count} chunks into MongoDB")
