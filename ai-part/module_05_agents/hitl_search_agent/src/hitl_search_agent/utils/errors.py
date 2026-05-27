"""
hitl_search_agent.utils.errors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Custom exception classes and error formatting helpers.
"""

from __future__ import annotations

import logging
import traceback

logger = logging.getLogger(__name__)


# ------------------------------------------------------------------
# Custom exceptions
# ------------------------------------------------------------------

class HITLError(Exception):
    """Base exception for all HITL search agent errors."""


class ProposalError(HITLError):
    """Raised when the proposal generation fails."""


class SearchError(HITLError):
    """Raised when the web search execution fails."""


class ResumeError(HITLError):
    """Raised when resuming an interrupted graph fails."""


# ------------------------------------------------------------------
# Error formatting
# ------------------------------------------------------------------

def format_exception(error: BaseException, *, include_traceback: bool = True) -> str:
    """
    Convert exceptions to readable Markdown for the Gradio UI.

    Parameters
    ----------
    error:
        The exception to format.
    include_traceback:
        Whether to include the full traceback. Set to ``False``
        in production to avoid exposing internal paths.
    """
    logger.exception("UI error: %s", error)

    parts = [
        "## Error\n\n",
        f"```text\n{type(error).__name__}: {error}\n```\n",
    ]

    if include_traceback:
        parts.append(
            "\n### Traceback\n\n"
            f"```text\n{traceback.format_exc()}\n```"
        )

    return "".join(parts)
