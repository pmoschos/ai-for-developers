"""
QA Chain — Enhanced
====================
Features:
  1. Conversation memory (history passed to LLM)
  2. Relevance threshold (I-don't-know guard)
  3. Streaming responses (token-by-token)
  4. Custom system prompt (settable at runtime)
  5. Token / cost tracking
"""

from typing import Dict, List, Generator
import logging
from openai import OpenAI

from .prompts import QA_SYSTEM_PROMPT, QA_USER_PROMPT

logger = logging.getLogger(__name__)

# Minimum cosine similarity to include a chunk (0-1)
RELEVANCE_THRESHOLD = 0.35

# gpt-4o-mini pricing (input + output blended estimate)
COST_PER_TOKEN = 0.00000015

# Used when no relevant document chunks are found
NO_CONTEXT_SYSTEM_PROMPT = """You are a helpful document assistant.
No relevant information was found in the uploaded documents for this message.
- If the user is greeting you or making small talk, respond in a friendly and natural way.
- If the user is asking a factual question, politely explain that you couldn't find
  relevant information in the available documents and suggest they upload a relevant
  document or rephrase their question.
Never make up document content."""


class QAChain:
    """RAG chain for question answering"""

    def __init__(self, retriever, model: str = "gpt-4o-mini"):
        self.retriever = retriever
        self.model = model
        self.client = OpenAI()
        self._system_prompt = QA_SYSTEM_PROMPT

    # ── Public API ─────────────────────────────────────────

    def set_system_prompt(self, prompt: str):
        """Update the system prompt at runtime (Feature #5)."""
        self._system_prompt = prompt.strip() if prompt.strip() else QA_SYSTEM_PROMPT

    def answer(self, question: str, history: List[Dict] = None, top_k: int = 4) -> Dict:
        """
        Answer a question using RAG.
        Falls back to LLM-only (no context) for greetings / small talk.
        """
        results = self.retriever.retrieve(question, top_k)
        relevant = [r for r in results if r["score"] >= RELEVANCE_THRESHOLD]

        if not relevant:
            # Fallback: call LLM without document context
            messages = [{"role": "system", "content": NO_CONTEXT_SYSTEM_PROMPT}]
            for msg in (history or [])[-6:]:
                if msg.get("role") in ("user", "assistant") and msg.get("content"):
                    messages.append({"role": msg["role"], "content": msg["content"]})
            messages.append({"role": "user", "content": question})

            response = self.client.chat.completions.create(
                model=self.model, messages=messages, max_tokens=300, temperature=0.5
            )
            tokens = response.usage.total_tokens
            return {
                "answer": response.choices[0].message.content,
                "sources": [],
                "tokens_used": tokens,
                "cost_usd": tokens * COST_PER_TOKEN,
            }

        context = self._build_context(relevant)
        messages = self._build_messages(context, question, history)

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=500,
            temperature=0.3,
        )

        tokens = response.usage.total_tokens
        return {
            "answer": response.choices[0].message.content,
            "sources": self._format_sources(relevant),
            "tokens_used": tokens,
            "cost_usd": tokens * COST_PER_TOKEN,
        }

    def answer_stream(self, question: str, history: List[Dict] = None, top_k: int = 4, use_hyde: bool = False):
        """
        Stream the answer token-by-token.
        Falls back to LLM-only (no context) for greetings / small talk.
        If use_hyde=True, retrieves via HyDE instead of direct query embedding.
        """
        # ── Retrieval (standard or HyDE) ───────────────────
        hypothetical_doc = None
        if use_hyde:
            results, hypothetical_doc = self.retriever.retrieve_with_hyde(question, top_k)
        else:
            results = self.retriever.retrieve(question, top_k)

        relevant = [r for r in results if r["score"] >= RELEVANCE_THRESHOLD]

        if not relevant:
            # Fallback: stream LLM response without document context
            messages = [{"role": "system", "content": NO_CONTEXT_SYSTEM_PROMPT}]
            for msg in (history or [])[-6:]:
                if msg.get("role") in ("user", "assistant") and msg.get("content"):
                    messages.append({"role": msg["role"], "content": msg["content"]})
            messages.append({"role": "user", "content": question})

            stream = self.client.chat.completions.create(
                model=self.model, messages=messages,
                max_tokens=300, temperature=0.5, stream=True
            )
            collected = ""
            for chunk in stream:
                delta = chunk.choices[0].delta.content
                if delta:
                    collected += delta
                    yield {"type": "token", "content": delta}

            est_tokens = (len(question) + len(collected)) // 4
            yield {"type": "done", "sources": [], "token_info": f"~{est_tokens} tokens | ~${est_tokens * COST_PER_TOKEN:.10f}", "hypothetical_doc": hypothetical_doc}
            return

        context = self._build_context(relevant)
        messages = self._build_messages(context, question, history)

        stream = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=500,
            temperature=0.3,
            stream=True,
        )

        collected = ""
        for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                collected += delta
                yield {"type": "token", "content": delta}

        # Estimate cost (streaming doesn't return usage)
        prompt_chars = sum(len(m.get("content", "")) for m in messages)
        est_tokens = (prompt_chars + len(collected)) // 4
        est_cost = est_tokens * COST_PER_TOKEN

        yield {
            "type": "done",
            "sources": self._format_sources(relevant),
            "token_info": f"~{est_tokens} tokens | ~${est_cost:.5f}",
            "hypothetical_doc": hypothetical_doc,
        }

    # ── Private helpers ────────────────────────────────────

    def _build_messages(self, context: str, question: str, history: List[Dict] = None) -> List[Dict]:
        """Build message list with system prompt + history + current question (Feature #1)."""
        messages = [{"role": "system", "content": self._system_prompt}]

        # Include last 6 messages (= 3 exchanges) from conversation history
        for msg in (history or [])[-6:]:
            if msg.get("role") in ("user", "assistant") and msg.get("content"):
                messages.append({"role": msg["role"], "content": msg["content"]})

        messages.append({
            "role": "user",
            "content": QA_USER_PROMPT.format(context=context, question=question),
        })
        return messages

    def _build_context(self, results: List[Dict]) -> str:
        parts = []
        for i, doc in enumerate(results, 1):
            source = doc["metadata"].get("source", "Unknown")
            parts.append(f"[Source {i}: {source}]\n{doc['content']}")
        return "\n\n---\n\n".join(parts)

    def _format_sources(self, results: List[Dict]) -> List[Dict]:
        return [
            {
                "source": doc["metadata"].get("source", "Unknown"),
                "score": doc["score"],
                "preview": doc["content"][:200] + "...",
            }
            for doc in results
        ]
