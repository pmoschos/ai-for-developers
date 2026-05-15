"""
retrieval/retriever.py
----------------------
Responsible for: vector store queries, stats, and database management.
"""

from typing import Dict
import logging

# pyrefly: ignore [missing-import]
from langchain_chroma import Chroma

from ..config import get_config

logger = logging.getLogger(__name__)


class VectorRetriever:
    """
    Wraps the ChromaDB vector store with retrieval, stats, and clear operations.
    Decoupled from the LLM — pure vector search layer.
    """

    def __init__(self, vectorstore, embeddings):
        self.vectorstore = vectorstore
        self.embeddings  = embeddings

    def as_retriever(self, k: int = 3):
        """Return a LangChain-compatible retriever for use in LCEL chains."""
        return self.vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": k},
        )

    def get_stats(self) -> Dict:
        """Return chunk count and unique document sources."""
        collection = self.vectorstore._collection
        count = collection.count()
        sources = set()
        if count > 0:
            data = collection.get(include=["metadatas"])
            for m in (data.get("metadatas") or []):
                if m and "source" in m:
                    sources.add(m["source"])
        return {
            "total_chunks":    count,
            "unique_sources":  len(sources),
            "sources":         sorted(sources),
        }

    def clear(self):
        """Delete all documents and recreate an empty collection."""
        config = get_config()
        self.vectorstore.delete_collection()
        self.vectorstore = Chroma(
            collection_name="documents",
            embedding_function=self.embeddings,
            persist_directory=str(config.chroma_db_path),
        )
        logger.info("Vector store cleared.")
