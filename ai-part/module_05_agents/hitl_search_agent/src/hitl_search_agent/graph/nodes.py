"""
hitl_search_agent.graph.nodes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

LangGraph node functions.

Each function receives the shared ``HITLSearchState`` and returns a
partial dict that LangGraph merges back into state.
"""

from __future__ import annotations

import logging

from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langgraph.types import interrupt
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from hitl_search_agent.domain.state import HITLSearchState
from hitl_search_agent.domain.models import ProposalOutput
from hitl_search_agent.infrastructure.llm import create_llm
from hitl_search_agent.infrastructure.web_search import create_web_search_tool
from hitl_search_agent.prompts.proposal_prompts import PROPOSAL_SYSTEM_PROMPT
from hitl_search_agent.prompts.summary_prompts import (
    SUMMARY_SYSTEM_PROMPT,
    build_summary_user_message,
)
from hitl_search_agent.utils.image_utils import extract_image_urls

logger = logging.getLogger(__name__)


# ------------------------------------------------------------------
# Lazy-initialised singletons (created on first call, not at import)
# ------------------------------------------------------------------

_llm = None
_web_search_tool = None


def _get_llm():
    global _llm
    if _llm is None:
        _llm = create_llm()
    return _llm


def _get_web_search_tool():
    global _web_search_tool
    if _web_search_tool is None:
        _web_search_tool = create_web_search_tool()
    return _web_search_tool


# ------------------------------------------------------------------
# Node 1: Propose Search Action
# ------------------------------------------------------------------

def propose_action(state: HITLSearchState) -> dict:
    """
    The agent proposes a search query and explains the planned action.

    Uses structured output (Pydantic model) so the LLM is forced to
    return valid data — no fragile JSON parsing needed.

    Important:
    This node does NOT perform the search.
    It only prepares something for human review.
    """
    user_request = state["user_request"]
    llm = _get_llm()

    logger.info("Generating proposal for: %s", user_request[:80])

    structured_llm = llm.with_structured_output(ProposalOutput)

    proposal: ProposalOutput = structured_llm.invoke(
        [
            SystemMessage(content=PROPOSAL_SYSTEM_PROMPT),
            HumanMessage(content=user_request),
        ]
    )

    logger.info("Proposal generated: query=%s", proposal.search_query)

    return {
        "search_query": proposal.search_query,
        "proposed_action": proposal.proposed_action,
        "messages": [
            AIMessage(
                content=(
                    f"Proposed web search:\n\n{proposal.proposed_action}\n\n"
                    f"Search query:\n{proposal.search_query}"
                )
            )
        ],
    }


# ------------------------------------------------------------------
# Node 2: Human Review (interrupt)
# ------------------------------------------------------------------

def human_review(state: HITLSearchState) -> dict:
    """
    Interrupt the graph and wait for human input.

    The Gradio UI will resume the graph with
    ``Command(resume={"approved": ..., "edited_query": ..., "feedback": ...})``.

    The ``interrupt()`` call suspends execution and returns the
    human's decision payload when the graph is resumed.
    """
    logger.info("Awaiting human review for query: %s", state["search_query"])

    decision = interrupt(
        {
            "proposed_action": state["proposed_action"],
            "search_query": state["search_query"],
            "message": "Please review the proposed search query.",
        }
    )

    # 'decision' is whatever the human passed via Command(resume=...)
    approved = decision.get("approved", False)
    edited_query = decision.get("edited_query", state["search_query"])
    feedback = decision.get("feedback", "")

    logger.info("Human decision: approved=%s, query=%s", approved, edited_query)

    return {
        "approved": approved,
        "search_query": edited_query,
        "human_feedback": feedback,
        "messages": [
            HumanMessage(
                content=(
                    f"Human decision: {'Approved' if approved else 'Rejected'}\n"
                    f"Query: {edited_query}\n"
                    f"Feedback: {feedback}"
                )
            )
        ],
    }


# ------------------------------------------------------------------
# Node 3: Execute Web Search (with retry)
# ------------------------------------------------------------------

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    retry=retry_if_exception_type(Exception),
    before_sleep=lambda retry_state: logger.warning(
        "Web search attempt %d failed, retrying...",
        retry_state.attempt_number,
    ),
)
def _search_with_retry(tool, query: str) -> dict:
    """Execute Tavily search with automatic retry on failure."""
    return tool.invoke(
        {
            "query": query,
            "include_images": True,
        }
    )


def execute_web_search(state: HITLSearchState) -> dict:
    """
    Execute the approved Tavily web search with retry logic.
    """
    search_query = state["search_query"]
    tool = _get_web_search_tool()

    logger.info("Executing web search: %s", search_query)

    raw_results = _search_with_retry(tool, search_query)
    image_urls = extract_image_urls(raw_results)

    logger.info(
        "Search completed: %d results, %d images",
        len(raw_results.get("results", [])) if isinstance(raw_results, dict) else 0,
        len(image_urls),
    )

    return {
        "search_results": raw_results,
        "image_urls": image_urls,
        "messages": [
            AIMessage(content=f"Web search completed for query:\n\n{search_query}")
        ],
    }


# ------------------------------------------------------------------
# Node 4: Summarize Search Results
# ------------------------------------------------------------------

def summarize_search_results(state: HITLSearchState) -> dict:
    """
    Summarize Tavily results into a readable final answer.
    """
    user_request = state["user_request"]
    search_query = state["search_query"]
    raw_results = state["search_results"]
    image_urls = state.get("image_urls", [])
    human_feedback = state.get("human_feedback") or "No human feedback provided."
    llm = _get_llm()

    logger.info("Summarizing results for: %s", search_query)

    user_message = build_summary_user_message(
        user_request=user_request,
        search_query=search_query,
        human_feedback=human_feedback,
        num_images=len(image_urls),
        raw_results=raw_results,
    )

    response = llm.invoke(
        [
            SystemMessage(content=SUMMARY_SYSTEM_PROMPT),
            HumanMessage(content=user_message),
        ]
    )

    logger.info("Summary generated: %d characters", len(response.content))

    return {
        "result": response.content,
        "messages": [
            AIMessage(content=response.content)
        ],
    }


# ------------------------------------------------------------------
# Routing function
# ------------------------------------------------------------------

def route_after_review(state: HITLSearchState) -> str:
    """
    Conditional edge: route to search if approved, or END if rejected.
    """
    from langgraph.graph import END

    if state.get("approved"):
        logger.info("Routing to web search (approved)")
        return "execute_web_search"

    logger.info("Routing to END (rejected)")
    return END
