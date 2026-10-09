"""Embedding helpers for the RAG system."""

from openai import OpenAI

client = OpenAI()

EMBEDDING_MODEL = "text-embedding-3-small"


def embed(text: str) -> list[float]:
    """Return the embedding vector for a piece of text."""
    response = client.embeddings.create(model=EMBEDDING_MODEL, input=text)
    return response.data[0].embedding
