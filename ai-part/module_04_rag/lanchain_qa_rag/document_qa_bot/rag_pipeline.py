"""
rag_pipeline.py — Orchestrator
-------------------------------
Wires together the three components:
  ingestion.ingestor.DocumentIngestor   → load + split + store
  retrieval.retriever.VectorRetriever   → search + stats + clear
  generation.chain_builder.ChainBuilder → LCEL chain + streaming

LangSmith traces automatically when LANGCHAIN_TRACING_V2=true in .env.
"""

from typing import List, Dict, Generator
import logging

from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_chroma import Chroma

from .config import get_config
from .generation.prompts import QA_SYSTEM_PROMPT
from .ingestion.ingestor import DocumentIngestor
from .retrieval.retriever import VectorRetriever
from .generation.chain_builder import ChainBuilder

logger = logging.getLogger(__name__)


class RAGPipeline:
    """
    Top-level orchestrator.
    Delegates every responsibility to a specialised component.
    """

    def __init__(self):
        config = get_config()

        # ── Shared infrastructure ────────────────────────────────
        self.embeddings  = OpenAIEmbeddings(model=config.embedding_model)
        self.vectorstore = Chroma(
            collection_name="documents",
            embedding_function=self.embeddings,
            persist_directory=str(config.chroma_db_path),
        )
        self.llm = ChatOpenAI(
            model=config.llm_model,
            temperature=config.temperature,
            max_tokens=config.max_tokens,
            streaming=True,
        )

        # ── Components ───────────────────────────────────────────
        self.ingestor      = DocumentIngestor(self.vectorstore)
        self.v_retriever   = VectorRetriever(self.vectorstore, self.embeddings)
        self.chain_builder = ChainBuilder(self.llm, self.vectorstore)

    # ── Public API (delegates to components) ─────────────────────

    def set_system_prompt(self, prompt: str):
        self.chain_builder.build(system_prompt=prompt.strip() or QA_SYSTEM_PROMPT)

    def ingest(self, file_path: str) -> int:
        return self.ingestor.ingest(file_path)

    def answer_stream(self, question: str, history: List[Dict] = None, use_hyde: bool = False) -> Generator:
        return self.chain_builder.answer_stream(question, history, use_hyde)

    def get_stats(self) -> Dict:
        return self.v_retriever.get_stats()

    def clear(self):
        self.v_retriever.clear()
        # ── Sync the NEW vectorstore to ALL components ────────────────
        new_vs = self.v_retriever.vectorstore
        self.vectorstore                = new_vs
        self.ingestor.vectorstore       = new_vs   # ← was missing! caused the error
        self.chain_builder.vectorstore  = new_vs
        self.chain_builder.build()
