"""
hitl_search_agent.infrastructure.web_search
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Tavily web search tool factory.
"""

from __future__ import annotations

import logging

try:
    from langchain_tavily import TavilySearch
except ModuleNotFoundError as exc:
    raise ModuleNotFoundError(
        "Missing package: langchain-tavily\n\n"
        "Install it with:\n"
        "    pip install -U langchain-tavily\n"
    ) from exc

from hitl_search_agent.config import Settings, get_settings

logger = logging.getLogger(__name__)


def create_web_search_tool(settings: Settings | None = None) -> TavilySearch:
    """
    Create and return a configured TavilySearch instance.

    Parameters
    ----------
    settings:
        Optional ``Settings`` override (useful in tests).
        Defaults to the application singleton.
    """
    s = settings or get_settings()

    logger.info(
        "Creating Tavily search tool: max_results=%d, topic=%s",
        s.tavily_max_results,
        s.tavily_topic,
    )

    return TavilySearch(
        max_results=s.tavily_max_results,
        topic=s.tavily_topic,
        include_answer=True,
        include_raw_content=False,
        include_images=True,
    )
