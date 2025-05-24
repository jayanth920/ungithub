import json
import os
import logging

logger = logging.getLogger("uvicorn")

def save_chunks_jsonl(data, filename="data/chunks.jsonl"):
    os.makedirs("data", exist_ok=True)
    with open(filename, "w", encoding="utf-8") as f:
        for entry in data:
            f.write(json.dumps(entry) + "\n")
    logger.info(f"✅ Saved {len(data)} chunks to {filename}")
