from embedding import get_embedding
from mongo import insert_chunks_with_embeddings
from load_jsonl import load_chunks_from_jsonl

if __name__ == "__main__":
    repo_name = "example-repo"
    chunks = load_chunks_from_jsonl("data/chunks.jsonl")
    insert_chunks_with_embeddings(chunks, repo_name, get_embedding)
