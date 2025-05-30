
from google import genai
import os
import logging
from dotenv import load_dotenv
from google.genai import types

logger = logging.getLogger("uvicorn")

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def get_embeddings(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []

    try:
        response = client.models.embed_content(
            model="text-embedding-004",
            contents=texts,
            config=types.EmbedContentConfig(task_type="SEMANTIC_SIMILARITY")
        )
        return [embedding.values for embedding in response.embeddings]
    except Exception as e:
        logger.error(f"Embedding failed: {e}")
        raise

def get_question_embedding(question: str) -> list[float]:
    """
    Generates a single embedding vector for the given question string.
    """
    if not question.strip():
        raise ValueError("Question cannot be empty.")

    try:
        response = client.models.embed_content(
            model="text-embedding-004",
            contents=[question],
            config=types.EmbedContentConfig(task_type="SEMANTIC_SIMILARITY")
        )
        return response.embeddings[0].values
    except Exception as e:
        logger.error(f"Failed to get question embedding: {e}")
        raise



# if __name__ == "__main__":
#     sample_texts = [
#         "How does a hash map work?",
#         "Explain quicksort algorithm.",
#         "This is a random sentence about dogs."
#     ]

#     try:
#         logger.info("🔍 Getting embeddings for sample texts...")
#         embeddings = get_embeddings(sample_texts)
#         for i, emb in enumerate(embeddings):
#             print(f"\nEmbedding {i+1} ({sample_texts[i][:40]}...):")
#             print(emb[:10], "...")  # Print first 10 dimensions
#         logger.info("✅ Done generating embeddings.")
#     except Exception as e:
#         logger.error("❌ Failed to get embeddings.")
