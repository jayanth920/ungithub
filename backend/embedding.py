from google import genai
import os
import logging
from dotenv import load_dotenv

logger = logging.getLogger("uvicorn")

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def get_embedding(text: str) -> list[float]:
    response = client.models.embed_content(
        model="text-embedding-004",
        contents=text,
    )
    return response.embeddings[0]

# Test it out
if __name__ == "__main__":
    sample_text = "How does a binary search algorithm work?"
    embedding = get_embedding(sample_text)
    logger.info(f"Embedding: {embedding}")
