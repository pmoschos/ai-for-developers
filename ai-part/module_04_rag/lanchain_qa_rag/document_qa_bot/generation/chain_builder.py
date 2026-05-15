"""
generation/chain_builder.py
---------------------------
Responsible for: building the LCEL chain + streaming answers.

Supports two retrieval modes:
  Standard : history-aware retrieval (reformulates follow-up questions)
  HyDE     : generates a hypothetical document → embeds it → retrieves
"""

from typing import List, Dict, Generator
import logging

# pyrefly: ignore [missing-import]
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
# pyrefly: ignore [missing-import]
from langchain_core.messages import HumanMessage, AIMessage
# pyrefly: ignore [missing-import]
from langchain_core.output_parsers import StrOutputParser
# pyrefly: ignore [missing-import]
from langchain_core.runnables import RunnableParallel, RunnableLambda

from .prompts import QA_SYSTEM_PROMPT, CONTEXTUALIZE_PROMPT
from ..config import get_config

logger = logging.getLogger(__name__)

COST_PER_TOKEN = 0.00000015

# Relevance threshold now lives in config.py (min_relevance_score)
# so it can be changed in one place without touching this file.

# Prompt used to generate the hypothetical document in HyDE mode
HYDE_PROMPT_TEMPLATE = (
    "Write a short, factual passage (2-4 sentences) that directly answers "
    "the following question. Imagine this is an excerpt from a relevant document.\n\n"
    "Question: {question}\n\nPassage:"
)


class ChainBuilder:
    """
    Builds and owns the LCEL retrieval chain.
    Supports Standard and HyDE retrieval modes.
    """

    def __init__(self, llm, vectorstore):
        self.llm            = llm
        self.vectorstore    = vectorstore
        self._system_prompt = QA_SYSTEM_PROMPT
        self.chain          = None
        self.build()

    # ── Chain Construction ────────────────────────────────────────

    def build(self, system_prompt: str = None):
        """
        Update the system prompt.
        Called on startup and when the user changes persona in Settings.
        """
        if system_prompt is not None:
            self._system_prompt = system_prompt

        # History-aware reformulation prompt (used in _stream_standard)
        self._ctx_prompt = ChatPromptTemplate.from_messages([
            ("system", CONTEXTUALIZE_PROMPT),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ])

    # ── Public streaming entry point ──────────────────────────────

    def answer_stream(
        self,
        question: str,
        history: List[Dict] = None,
        use_hyde: bool = False,
    ) -> Generator:
        """
        Stream the answer token-by-token.

        use_hyde=False → Standard history-aware LCEL chain
        use_hyde=True  → HyDE: hypothetical doc → embed → retrieve → generate

        Yields:
          {"type": "token",  "content": "<text>"}
          {"type": "done",   "sources": [...], "token_info": "...",
                             "hypothetical_doc": str | None}
        """
        lc_history = self._to_lc_messages(history or [])

        if use_hyde:
            yield from self._stream_hyde(question, lc_history)
        else:
            yield from self._stream_standard(question, lc_history)

    # ── Standard RAG ──────────────────────────────────────────

    def _stream_standard(self, question: str, lc_history: list) -> Generator:
        """History-aware retrieval + generation with relevance scores."""
        config = get_config()

        # Step 1: Reformulate question if there is chat history
        search_query = question
        if lc_history:
            search_query = (
                self._ctx_prompt | self.llm | StrOutputParser()
            ).invoke({"input": question, "chat_history": lc_history})

        # Step 2: Retrieve with scores, filter by threshold
        results = self.vectorstore.similarity_search_with_relevance_scores(
            search_query, k=config.top_k
        )
        retrieved_docs = [doc   for doc, score in results if score >= config.min_relevance_score]
        doc_scores     = [score for _,   score in results if score >= config.min_relevance_score]
        sources  = self._extract_sources(retrieved_docs, doc_scores)
        context  = self._format_docs(retrieved_docs)

        # Step 3: Build prompt and stream answer
        qa_prompt = ChatPromptTemplate.from_messages([
            ("system", self._system_prompt + "\n\nContext:\n" + context),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ])

        collected = ""
        for token in (qa_prompt | self.llm | StrOutputParser()).stream({
            "input":        question,
            "chat_history": lc_history,
        }):
            collected += token
            yield {"type": "token", "content": token}

        yield self._done_event(question, collected, sources, hypothetical_doc=None)

    # ── HyDE RAG ─────────────────────────────────────────────────

    def _stream_hyde(self, question: str, lc_history: list) -> Generator:
        """
        HyDE: generate hypothetical doc → embed → retrieve → generate.
        """
        config = get_config()

        # Signal the UI immediately so it shows a status (not a frozen screen)
        yield {"type": "status", "message": "⚗️ Generating hypothetical document…"}

        # Step 1 — Generate hypothetical document
        logger.info("HyDE: generating hypothetical document…")
        hypothetical_doc = self._generate_hypothetical_doc(question)
        logger.info(f"HyDE doc: {hypothetical_doc[:80]}…")

        # Step 2 — Retrieve using hypothetical doc, filtered by relevance score
        threshold = config.min_relevance_score
        results = self.vectorstore.similarity_search_with_relevance_scores(
            hypothetical_doc, k=config.top_k
        )
        retrieved_docs = [doc   for doc, score in results if score >= threshold]
        doc_scores     = [score for _,   score in results if score >= threshold]
        sources  = self._extract_sources(retrieved_docs, doc_scores)
        context  = self._format_docs(retrieved_docs)

        # Step 3 — Build a one-shot prompt (no chain needed, context is already ready)
        qa_prompt = ChatPromptTemplate.from_messages([
            ("system", self._system_prompt + "\n\nContext:\n" + context),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ])

        # Step 4 — Stream the answer
        collected = ""
        for token in (qa_prompt | self.llm | StrOutputParser()).stream({
            "input":        question,
            "chat_history": lc_history,
        }):
            collected += token
            yield {"type": "token", "content": token}

        yield self._done_event(question, collected, sources, hypothetical_doc)

    # ── Helpers ───────────────────────────────────────────────────

    def _generate_hypothetical_doc(self, question: str) -> str:
        """Ask the LLM to write a passage that would answer the question."""
        prompt = ChatPromptTemplate.from_template(HYDE_PROMPT_TEMPLATE)
        return (prompt | self.llm | StrOutputParser()).invoke({"question": question})

    @staticmethod
    def _format_docs(docs) -> str:
        return "\n\n---\n\n".join(
            f"[Source: {d.metadata.get('source', '?')}]\n{d.page_content}"
            for d in docs
        )

    @staticmethod
    def _extract_sources(docs, scores=None) -> list:
        """Extract source metadata. Scores are available only in HyDE mode."""
        _scores = scores if scores is not None else [None] * len(docs)
        return [
            {
                "source": doc.metadata.get("source", "Unknown"),
                "page":   doc.metadata.get("page", ""),
                "chunk":  doc.page_content,
                "score":  round(score, 2) if score is not None else None,
            }
            for doc, score in zip(docs, _scores)
        ]

    @staticmethod
    def _done_event(question: str, collected: str, sources: list,
                    hypothetical_doc: str | None) -> dict:
        est_tokens = (len(question) + len(collected)) // 4
        return {
            "type":             "done",
            "sources":          sources,
            "token_info":       f"~{est_tokens} tokens | ~${est_tokens * COST_PER_TOKEN:.5f}",
            "hypothetical_doc": hypothetical_doc,
        }

    @staticmethod
    def _to_lc_messages(history: List[Dict]):
        """Convert Gradio {role, content} dicts → LangChain message objects."""
        messages = []
        for msg in history[-6:]:
            role    = msg.get("role", "")
            content = msg.get("content", "")
            if "---\n📚" in content:
                content = content.split("---\n📚")[0].strip()
            if not content:
                continue
            if role == "user":
                messages.append(HumanMessage(content=content))
            elif role == "assistant":
                messages.append(AIMessage(content=content))
        return messages
