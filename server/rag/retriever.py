"""Retrieval layer: finds relevant context for a query.

This is a placeholder. Swap in a real vector store (Chroma, FAISS, pgvector,
etc.) and use `rag.embeddings.embed` to build and query the index.
"""

from rag.embeddings import embed


class Retriever:
    def __init__(self) -> None:
        # TODO: connect to a vector store under rag/store/.
        self._documents: list[str] = []

    def add(self, text: str) -> None:
        """Index a document."""
        self._documents.append(text)

    def search(self, query: str, k: int = 4) -> list[str]:
        """Return the top-k most relevant documents for the query."""
        _ = embed(query)  # TODO: use the embedding for a real similarity search.
        return self._documents[:k]
