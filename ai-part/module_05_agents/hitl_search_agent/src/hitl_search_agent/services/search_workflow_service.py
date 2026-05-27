"""
hitl_search_agent.services.search_workflow_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

High-level orchestration for the HITL search workflow.

This service owns the compiled LangGraph application and exposes
simple methods that the UI layer calls. It uses thread-based
checkpointing so each conversation has its own persistent state.
"""

from __future__ import annotations

import logging
import uuid

from langgraph.types import Command

from hitl_search_agent.domain.state import HITLSearchState, make_initial_state
from hitl_search_agent.graph.builder import build_app
from hitl_search_agent.utils.errors import ProposalError, SearchError, ResumeError

logger = logging.getLogger(__name__)


class SearchWorkflowService:
    """
    Facade that drives the unified HITL search workflow.

    Phase 1 — ``generate_proposal``:
        Runs the graph until the ``human_review`` node calls
        ``interrupt()``. Returns the proposal and a ``thread_id``
        that identifies this conversation.

    Phase 2 — ``resume_with_decision``:
        Resumes the interrupted graph with the human's decision
        (approve/edit/reject). If approved, the search and
        summarization nodes run automatically.
    """

    def __init__(self) -> None:
        self._app = build_app()

    # ------------------------------------------------------------------
    # Phase 1: Generate proposal (runs until interrupt)
    # ------------------------------------------------------------------

    def generate_proposal(self, user_request: str) -> tuple[dict, str]:
        """
        Run the graph until the human_review interrupt.

        Returns
        -------
        tuple[dict, str]
            A tuple of (state_snapshot, thread_id).

        Raises
        ------
        ProposalError
            If the proposal generation fails.
        """
        thread_id = str(uuid.uuid4())
        config = {"configurable": {"thread_id": thread_id}}

        logger.info("Starting proposal: thread=%s, request=%s", thread_id, user_request[:80])

        try:
            state = make_initial_state(user_request)
            result = self._app.invoke(state, config=config)

            logger.info("Proposal complete: thread=%s, query=%s", thread_id, result.get("search_query"))
            return result, thread_id

        except Exception as exc:
            logger.exception("Proposal failed: thread=%s", thread_id)
            raise ProposalError(f"Failed to generate proposal: {exc}") from exc

    # ------------------------------------------------------------------
    # Phase 2: Resume with human decision
    # ------------------------------------------------------------------

    def resume_with_decision(
        self,
        thread_id: str,
        decision: dict,
    ) -> dict:
        """
        Resume the interrupted graph with the human's decision.

        Parameters
        ----------
        thread_id:
            The thread ID returned by ``generate_proposal``.
        decision:
            Dict with keys: ``approved`` (bool), ``edited_query`` (str),
            ``feedback`` (str).

        Returns
        -------
        dict
            The final state after the graph completes.

        Raises
        ------
        ResumeError
            If resuming the graph fails.
        """
        config = {"configurable": {"thread_id": thread_id}}

        logger.info(
            "Resuming graph: thread=%s, approved=%s, query=%s",
            thread_id,
            decision.get("approved"),
            decision.get("edited_query"),
        )

        try:
            result = self._app.invoke(
                Command(resume=decision),
                config=config,
            )

            logger.info("Graph completed: thread=%s, approved=%s", thread_id, result.get("approved"))
            return result

        except Exception as exc:
            logger.exception("Resume failed: thread=%s", thread_id)
            raise ResumeError(f"Failed to resume workflow: {exc}") from exc
