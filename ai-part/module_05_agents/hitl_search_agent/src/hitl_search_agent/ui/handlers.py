"""
hitl_search_agent.ui.handlers
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Gradio event-handler functions.

Each function is wired to a Gradio button click and returns tuples
that map to the declared ``outputs`` list.
"""

from __future__ import annotations

import logging

import gradio as gr

from hitl_search_agent.domain.state import make_initial_state
from hitl_search_agent.services.search_workflow_service import SearchWorkflowService
from hitl_search_agent.utils.errors import format_exception

logger = logging.getLogger(__name__)


# Module-level service instance shared by all handlers.
_service = SearchWorkflowService()


# ------------------------------------------------------------------
# Step 1 — Generate Proposal
# ------------------------------------------------------------------

def ui_generate_proposal(user_request: str):
    """
    User enters request.
    Agent proposes search query/action.
    Graph runs until interrupt() in human_review node.
    """
    try:
        user_request = user_request.strip()

        if not user_request:
            return (
                {},                              # app_state
                "",                              # thread_id
                "Please enter a request first.", # proposal_output
                "",                              # edited_query_box
                "",                              # human_feedback_box
                gr.update(interactive=False),    # approve_btn
                gr.update(interactive=False),    # reject_btn
                gr.update(interactive=False),    # clear_btn
                "",                              # final_answer_output
                [],                              # image_gallery
            )

        if len(user_request) > 2000:
            return (
                {},
                "",
                "Request too long. Please keep it under 2000 characters.",
                "",
                "",
                gr.update(interactive=False),
                gr.update(interactive=False),
                gr.update(interactive=False),
                "",
                [],
            )

        updated_state, thread_id = _service.generate_proposal(user_request)

        proposal_md = f"""\
## Proposed Web Search

### Proposed Action

{updated_state.get("proposed_action", "")}

### Search Query

```text
{updated_state.get("search_query", "")}
```

Review the proposal. You can approve it, edit the query first, or reject it."""

        logger.info("Proposal displayed: thread=%s", thread_id)

        return (
            updated_state,                                  # app_state
            thread_id,                                      # thread_id
            proposal_md,                                    # proposal_output
            updated_state.get("search_query", ""),          # edited_query_box
            "",                                             # human_feedback_box
            gr.update(interactive=True),                    # approve_btn
            gr.update(interactive=True),                    # reject_btn
            gr.update(interactive=True),                    # clear_btn
            "",                                             # final_answer_output
            [],                                             # image_gallery
        )

    except Exception as error:
        logger.exception("Proposal handler failed")
        return (
            {},
            "",
            format_exception(error),
            "",
            "",
            gr.update(interactive=False),
            gr.update(interactive=False),
            gr.update(interactive=True),
            "",
            [],
        )


# ------------------------------------------------------------------
# Step 2A — Approve & Search
# ------------------------------------------------------------------

def ui_approve_and_search(
    state: dict,
    thread_id: str,
    edited_query: str,
    human_feedback: str,
):
    """
    Human approves the search.

    Resumes the interrupted graph with Command(resume={...}).
    The graph then executes web search → summarization automatically.
    """
    try:
        if not thread_id:
            return (
                state,
                "No active request. Generate a proposal first.",
                "",
                [],
            )

        edited_query = edited_query.strip()

        if not edited_query:
            return (
                state,
                "Search query cannot be empty.",
                "",
                [],
            )

        decision = {
            "approved": True,
            "edited_query": edited_query,
            "feedback": human_feedback.strip(),
        }

        final_state = _service.resume_with_decision(
            thread_id=thread_id,
            decision=decision,
        )

        images = final_state.get("image_urls", [])

        final_md = f"""\
## Final Answer

{final_state.get("result", "")}

---

### Approved Query

```text
{final_state.get("search_query", "")}
```

### Images Found

{len(images)}"""

        logger.info("Approve completed: thread=%s, images=%d", thread_id, len(images))

        return (
            final_state,
            final_md,
            final_state.get("result", ""),
            images,
        )

    except Exception as error:
        logger.exception("Approve handler failed")
        return (
            state,
            format_exception(error),
            "",
            [],
        )


# ------------------------------------------------------------------
# Step 2B — Reject
# ------------------------------------------------------------------

def ui_reject(state: dict, thread_id: str, human_feedback: str):
    """
    Human rejects the proposed search.

    Resumes the interrupted graph with approved=False.
    The graph routes to END — no search is executed.
    """
    try:
        if not thread_id:
            return (
                state,
                "No active request. Generate a proposal first.",
                "",
                [],
            )

        feedback = human_feedback.strip() or "Rejected by the human reviewer."

        decision = {
            "approved": False,
            "edited_query": state.get("search_query", ""),
            "feedback": feedback,
        }

        final_state = _service.resume_with_decision(
            thread_id=thread_id,
            decision=decision,
        )

        rejection_md = f"""\
## Search Rejected

The proposed web search was rejected.

### Human Feedback

{feedback}"""

        logger.info("Rejection completed: thread=%s", thread_id)

        return (
            final_state,
            rejection_md,
            final_state.get("result", f"Search rejected.\n\nFeedback: {feedback}"),
            [],
        )

    except Exception as error:
        logger.exception("Reject handler failed")
        return (
            state,
            format_exception(error),
            "",
            [],
        )


# ------------------------------------------------------------------
# Clear
# ------------------------------------------------------------------

def ui_clear():
    """
    Reset the UI and internal state.
    """
    logger.info("UI cleared")

    return (
        {},                              # app_state
        "",                              # thread_id
        "",                              # proposal_output
        "",                              # edited_query_box
        "",                              # human_feedback_box
        gr.update(interactive=False),    # approve_btn
        gr.update(interactive=False),    # reject_btn
        gr.update(interactive=False),    # clear_btn
        "",                              # final_answer_output
        [],                              # image_gallery
    )
