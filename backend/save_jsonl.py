import json
import os
import logging

logger = logging.getLogger("uvicorn")

def save_chunks_jsonl(data, path="data/chunks.jsonl"):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for entry in data:
            f.write(json.dumps(entry) + "\n")
    logger.info(f"✅ Saved {len(data)} chunks to {path}")
