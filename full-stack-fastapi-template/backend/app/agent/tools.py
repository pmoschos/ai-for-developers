import os
import json
from typing import Any

from langchain_core.tools import tool
from langchain_tavily import TavilySearch

from app.core.config import settings


if settings.TAVILY_API_KEY:
    os.environ["TAVILY_API_KEY"] = settings.TAVILY_API_KEY


_tavily_search = TavilySearch(
    max_results=3,
    topic="general",
    include_answer=True,
    include_raw_content=False,
    include_images=False,
)


@tool
def web_search(query: str) -> str:
    """
    Search the web using Tavily and return JSON-serialized results.
    Use this when fresh or external information is needed.
    """

    if not query or not query.strip():
        return json.dumps(
            {"error": "No query provided"},
            ensure_ascii=False,
        )
    try:
        result: Any = _tavily_search.invoke({"query": query})
        return json.dumps(
            result,
            ensure_ascii=False,
            default=str,
        )

    except Exception as exc:
        return json.dumps(
            {
                "error": "Tavily search failed",
                "details": str(exc),
            },
            ensure_ascii=False,
        )
