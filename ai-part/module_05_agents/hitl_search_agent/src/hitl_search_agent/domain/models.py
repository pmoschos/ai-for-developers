"""
hitl_search_agent.domain.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Pydantic models used for LLM structured output and human decisions.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class ProposalOutput(BaseModel):
    """
    Schema the LLM must return for the proposal step.

    Used with ``llm.with_structured_output(ProposalOutput)`` so the
    LLM is *forced* to return valid structured data — no JSON parsing needed.
    """

    search_query: str = Field(
        description="The exact web search query to execute.",
    )
    proposed_action: str = Field(
        description=(
            "A clear, human-readable explanation of what will be "
            "searched and why."
        ),
    )
