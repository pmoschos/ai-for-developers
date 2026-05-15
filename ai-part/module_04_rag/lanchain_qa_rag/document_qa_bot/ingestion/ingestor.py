"""
ingestion/ingestor.py
---------------------
Responsible for: loading files + splitting into chunks + storing in vector DB.
"""

from pathlib import Path
from typing import List
import logging

# pyrefly: ignore [missing-import]
from langchain_community.document_loaders import (
    PyPDFLoader, TextLoader, Docx2txtLoader, UnstructuredMarkdownLoader,
)
# pyrefly: ignore [missing-import]
from langchain_text_splitters import RecursiveCharacterTextSplitter

from ..config import get_config

logger = logging.getLogger(__name__)


class DocumentIngestor:
    """
    Loads a document, splits it into chunks, and stores them in the vector store.
    Accepts any vectorstore compatible with LangChain's add_documents() API.
    """

    def __init__(self, vectorstore):
        self.vectorstore = vectorstore

    def ingest(self, file_path: str) -> int:
        """
        Full ingestion pipeline: Load → Split → Store.
        Returns the number of chunks added.
        """
        config = get_config()
        docs = self._load(file_path)
        if not docs:
            raise ValueError(f"No content extracted from: {file_path}")

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=config.chunk_size,
            chunk_overlap=config.chunk_overlap,
            separators=["\n\n", "\n", ". ", " "],
        )
        chunks = splitter.split_documents(docs)

        # Normalize source metadata → just filename (not full temp path)
        filename = Path(file_path).name
        for chunk in chunks:
            chunk.metadata["source"] = filename

        # Duplicate detection — skip if this file is already in the DB
        existing = self.vectorstore._collection.get(
            where={"source": filename}, limit=1
        )
        if existing["ids"]:
            raise ValueError(f"**{filename}** is already in the knowledge base.")

        self.vectorstore.add_documents(chunks)
        logger.info(f"Ingested {len(chunks)} chunks from {filename}")
        return len(chunks)

    def _load(self, file_path: str) -> List:
        """Route file to the correct LangChain Document Loader."""
        path = Path(file_path)
        loaders = {
            ".pdf":  PyPDFLoader,
            ".txt":  TextLoader,
            ".md":   UnstructuredMarkdownLoader,
            ".docx": Docx2txtLoader,
        }
        loader_cls = loaders.get(path.suffix.lower())
        if not loader_cls:
            raise ValueError(f"Unsupported format: {path.suffix}")
        return loader_cls(str(path)).load()
