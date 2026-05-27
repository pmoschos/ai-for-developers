"""
hitl_search_agent.graph.builder
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Compiles the unified LangGraph workflow with checkpointing.

Single graph:
    START → propose_action → human_review (interrupt)
          → route: approved  → execute_web_search → summarize → END
          → route: rejected  → END
"""

from __future__ import annotations

import logging

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from hitl_search_agent.domain.state import HITLSearchState
from hitl_search_agent.graph.nodes import (
    propose_action,
    human_review,
    execute_web_search,
    summarize_search_results,
    route_after_review,
)

logger = logging.getLogger(__name__)


def build_app():
    """
    Build and compile the unified HITL search workflow.

    The graph uses:
    - ``interrupt()`` in the ``human_review`` node for native HITL
    - ``MemorySaver`` checkpointer for state persistence across interrupts
    - Conditional edges to route based on human approval/rejection

    Returns
    -------
    CompiledGraph
        A compiled LangGraph application ready to ``invoke()`` and
        resume with ``Command(resume=...)``.
    """
    logger.info("Building unified HITL search graph")

    graph = StateGraph(HITLSearchState)

    # Register nodes
    graph.add_node("propose_action", propose_action)
    graph.add_node("human_review", human_review)
    graph.add_node("execute_web_search", execute_web_search)
    graph.add_node("summarize_search_results", summarize_search_results)

    # Wire edges
    graph.add_edge(START, "propose_action")
    graph.add_edge("propose_action", "human_review")

    # Conditional routing after human review
    graph.add_conditional_edges(
        "human_review",
        route_after_review,
        {
            "execute_web_search": "execute_web_search",
            END: END,
        },
    )

    graph.add_edge("execute_web_search", "summarize_search_results")
    graph.add_edge("summarize_search_results", END)

    # Compile with checkpointer for state persistence
    checkpointer = MemorySaver()
    compiled = graph.compile(checkpointer=checkpointer)

    logger.info("Graph compiled successfully with MemorySaver checkpointer")

    return compiled
