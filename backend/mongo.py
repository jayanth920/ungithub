from pymongo import MongoClient
import certifi
import os
from dotenv import load_dotenv

load_dotenv()

client = MongoClient(os.getenv("MONGODB_URI"), tlsCAFile=certifi.where())
collection = client["unrepo"]["code_chunks"]

def insert_chunks_with_embeddings(chunks, repo_name: str, embed_fn):
    docs = []
    for chunk in chunks:
        embedding = embed_fn(chunk["content"])
        doc = {
            "content": chunk["content"],
            "filepath": chunk["filepath"],
            "language": chunk["language"],
            "repo": repo_name,
            "embedding": embedding,
        }
        docs.append(doc)

    if docs:
        collection.insert_many(docs)
        print(f"✅ Inserted {len(docs)} chunks with embeddings into MongoDB")
