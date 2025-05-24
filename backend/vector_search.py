from pymongo import MongoClient
import os
from dotenv import load_dotenv
import certifi
from embedding import get_embedding

load_dotenv()
client = MongoClient(os.getenv("MONGODB_URI"), tlsCAFile=certifi.where())
collection = client["unrepo"]["code_chunks"]

def semantic_search(query: str, k: int = 5):
    embedding = get_embedding(query).values
    print("")
    results = collection.aggregate([
        {
            "$vectorSearch": {
                "index": "default",  # Make sure this matches your actual index name
                "path": "embedding",
                "queryVector": embedding,
                "numCandidates": 100,
                "limit": k
            }
        }
    ])
    print(list(results))
    return list(results)

if __name__ == "__main__":
    query = "authentication middleware"
    results = semantic_search(query)
    for r in results:
        print(f"\n📄 {r['filepath']} ({r['language']})\n---\n{r['content'][:500]}\n---")
