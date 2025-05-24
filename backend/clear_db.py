# clear_db.py

from pymongo import MongoClient
from dotenv import load_dotenv
import os
import certifi

# Load environment variables
load_dotenv()

# Connect to MongoDB
client = MongoClient(os.getenv("MONGODB_URI"), tlsCAFile=certifi.where())
collection = client["unrepo"]["code_chunks"]

# Delete all documents in the collection
result = collection.delete_many({})

print(f"🧹 Cleared {result.deleted_count} documents from the 'code_chunks' collection.")
