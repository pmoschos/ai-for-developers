"""
hitl_search_agent.infrastructure.llm
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

LLM client factory.

Provides a ``create_llm()`` factory function instead of a module-level
singleton, making the client easy to test and reconfigure.
"""

from __future__ import annotations

import logging

from langchain_openai import ChatOpenAI

from hitl_search_agent.config import Settings, get_settings

logger = logging.getLogger(__name__)


def create_llm(settings: Settings | None = None) -> ChatOpenAI:
    """
    Create and return a configured ChatOpenAI instance.

    Parameters
    ----------
    settings:
        Optional ``Settings`` override (useful in tests).
        Defaults to the application singleton.
    """
    s = settings or get_settings()

    logger.info("Creating LLM client: model=%s, temperature=%s", s.llm_model, s.llm_temperature)

    return ChatOpenAI(
        model=s.llm_model,
        temperature=s.llm_temperature,
    )
