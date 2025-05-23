import certifi
from pymongo import MongoClient
import os
from dotenv import load_dotenv
from pymongo.errors import ConnectionFailure

load_dotenv()
client = MongoClient(os.getenv("MONGODB_URI"),tlsCAFile=certifi.where())

try:
    print("Got the client")
    db = client.get_database("unrepo")
    print("Got the database")
    collection = db.get_collection("code_chunks")
    print("Got the collection")

    print("✅ Successfully connected to MongoDB!")
    print("📄 Document count in code_chunks:", collection.estimated_document_count())

except ConnectionFailure as e:
    print("❌ Could not connect to MongoDB:", e)
except Exception as e:
    print("⚠️ An error occurred:", e)
