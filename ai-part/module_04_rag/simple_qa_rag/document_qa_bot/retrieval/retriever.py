"""
Retriever
=========
Semantic search over the vector store.
"""

from typing import List, Dict, Tuple
import logging

logger = logging.getLogger(__name__)


class Retriever:
    """Retrieve relevant documents using semantic search"""

    def __init__(self, vector_store, embedder, top_k: int = 4):
        self.vector_store = vector_store
        self.embedder = embedder
        self.top_k = top_k

    # ── Standard retrieval ─────────────────────────────────

    def retrieve(self, query: str, top_k: int = None) -> List[Dict]:
        """Embed the query directly and search ChromaDB."""
        k = top_k or self.top_k
        query_embedding = self.embedder.embed(query)
        results = self.vector_store.search(query_embedding, top_k=k)
        logger.debug(f"Retrieved {len(results)} docs for: {query[:50]}")
        return results

    # ── HyDE retrieval ─────────────────────────────────────

    def retrieve_with_hyde(self, query: str, top_k: int = None) -> Tuple[List[Dict], str]:
        """
        HyDE — Hypothetical Document Embedding.

        Instead of embedding the question, we:
          1. Ask GPT to write a short hypothetical answer
          2. Embed THAT hypothetical document
          3. Search with the hypothetical embedding

        Why: Questions and answers live in different embedding spaces.
        A hypothetical answer is semantically closer to real document chunks
        than the question itself.

        Returns: (results, hypothetical_doc_text)
        """
        from openai import OpenAI
        client = OpenAI()

        # Step 1 — Generate a hypothetical document
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Write a short paragraph (3-4 sentences) that would be a perfect "
                        "document chunk for answering the given question. Write it as if it's "
                        "from a textbook or documentation — factual, informative, and direct. "
                        "Do not start with 'This document' or similar meta-references."
                    ),
                },
                {"role": "user", "content": query},
            ],
            max_tokens=150,
            temperature=0.3,
        )
        hypothetical_doc = response.choices[0].message.content.strip()
        logger.debug(f"HyDE hypothetical doc: {hypothetical_doc[:80]}...")

        # Step 2 — Embed the hypothetical document (not the question!)
        k = top_k or self.top_k
        hyde_embedding = self.embedder.embed(hypothetical_doc)

        # Step 3 — Search with that embedding
        results = self.vector_store.search(hyde_embedding, top_k=k)
        logger.debug(f"HyDE retrieved {len(results)} docs")

        return results, hypothetical_doc

    # ── Formatted context ──────────────────────────────────

    def retrieve_with_context(self, query: str, top_k: int = None) -> str:
        """Retrieve and format documents as a context string."""
        results = self.retrieve(query, top_k)
        if not results:
            return "No relevant documents found."
        parts = []
        for i, doc in enumerate(results, 1):
            source = doc["metadata"].get("source", "Unknown")
            parts.append(f"[Document {i} - {source}]\n{doc['content']}")
        return "\n\n---\n\n".join(parts)
