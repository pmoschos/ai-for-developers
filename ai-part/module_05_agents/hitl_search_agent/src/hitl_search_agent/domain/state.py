"""
hitl_search_agent.domain.state
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Shared workflow state used by LangGraph.
"""

from __future__ import annotations

import operator
from typing import Optional, Any

from typing_extensions import TypedDict, Annotated


class HumanDecision(TypedDict):
    """
    Payload the human sends when resuming the graph after the
    ``interrupt()`` in the ``human_review`` node.
    """

    approved: bool
    edited_query: str
    feedback: str


class HITLSearchState(TypedDict):
    """
    Shared state used by the LangGraph workflow.

    messages:
        Conversation messages. Annotated with operator.add so node
        updates append messages instead of replacing the list.

    user_request:
        The original request written by the user.

    proposed_action:
        A human-readable explanation of what the agent proposes to do.

    search_query:
        The actual web-search query proposed by the agent and editable
        by the human reviewer.

    approved:
        Human decision. True means execute the search, False means reject.

    human_feedback:
        Optional human feedback from the reviewer.

    human_decision:
        The structured payload received from the human via
        ``Command(resume=...)``.

    search_results:
        Raw response returned by Tavily.

    image_urls:
        Image URLs extracted from Tavily results.

    result:
        Final summarized answer.
    """

    messages: Annotated[list, operator.add]
    user_request: str
    proposed_action: str
    search_query: str
    approved: Optional[bool]
    human_feedback: Optional[str]
    human_decision: Optional[HumanDecision]
    search_results: Optional[Any]
    image_urls: list[str]
    result: str


def make_initial_state(user_request: str) -> HITLSearchState:
    """
    Build a fresh state object for one user request.
    """
    from langchain_core.messages import HumanMessage

    messages = [HumanMessage(content=user_request)] if user_request else []

    return {
        "messages": messages,
        "user_request": user_request,
        "proposed_action": "",
        "search_query": "",
        "approved": None,
        "human_feedback": None,
        "human_decision": None,
        "search_results": None,
        "image_urls": [],
        "result": "",
    }
