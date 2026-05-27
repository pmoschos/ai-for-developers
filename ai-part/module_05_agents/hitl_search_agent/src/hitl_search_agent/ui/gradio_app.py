"""
hitl_search_agent.ui.gradio_app
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Gradio Blocks layout and wiring.
"""

from __future__ import annotations

import gradio as gr

from hitl_search_agent.ui.handlers import (
    ui_generate_proposal,
    ui_approve_and_search,
    ui_reject,
    ui_clear,
)


def build_ui() -> gr.Blocks:
    """
    Build the Gradio Blocks application.
    """

    with gr.Blocks(
        title="HITL Web Search Agent",
    ) as demo:

        gr.Markdown(
            """
# Human-in-the-Loop Web Search Agent

This app lets the AI propose a web-search action, while the human reviewer remains in control.

**Workflow:** user request → proposed query → approve/edit/reject → real web search → answer + images.

> Built with LangGraph's native `interrupt()` + `MemorySaver` checkpointer for production-grade HITL.
"""
        )

        # State: workflow state dict + thread_id string
        app_state = gr.State({})
        thread_id = gr.State("")

        with gr.Row():
            with gr.Column(scale=1):
                user_request_box = gr.Textbox(
                    label="User Request",
                    placeholder=(
                        "Example: Show me the latest LangGraph "
                        "human-in-the-loop features with images."
                    ),
                    lines=4,
                    max_lines=8,
                )

                generate_btn = gr.Button(
                    "Generate Search Proposal",
                    variant="primary",
                )

                edited_query_box = gr.Textbox(
                    label="Editable Search Query",
                    placeholder="The agent's proposed query will appear here...",
                    lines=2,
                    interactive=True,
                )

                human_feedback_box = gr.Textbox(
                    label="Human Feedback / Instructions",
                    placeholder=(
                        "Optional: add feedback before approving or rejecting."
                    ),
                    lines=3,
                )

                with gr.Row():
                    approve_btn = gr.Button(
                        "Approve & Search",
                        variant="primary",
                        interactive=False,
                    )

                    reject_btn = gr.Button(
                        "Reject",
                        variant="stop",
                        interactive=False,
                    )

                clear_btn = gr.Button(
                    "Clear",
                    interactive=False,
                )

            with gr.Column(scale=2):
                proposal_output = gr.Markdown(
                    label="Proposal / Status",
                )

                final_answer_output = gr.Markdown(
                    label="Final Answer",
                )

                image_gallery = gr.Gallery(
                    label="Related Images",
                    columns=3,
                    height=420,
                    object_fit="cover",
                    show_label=True,
                )

        # --------------------------------------------------------------
        # Event wiring
        # --------------------------------------------------------------

        generate_btn.click(
            fn=ui_generate_proposal,
            inputs=[user_request_box],
            outputs=[
                app_state,
                thread_id,
                proposal_output,
                edited_query_box,
                human_feedback_box,
                approve_btn,
                reject_btn,
                clear_btn,
                final_answer_output,
                image_gallery,
            ],
        )

        approve_btn.click(
            fn=ui_approve_and_search,
            inputs=[
                app_state,
                thread_id,
                edited_query_box,
                human_feedback_box,
            ],
            outputs=[
                app_state,
                proposal_output,
                final_answer_output,
                image_gallery,
            ],
        )

        reject_btn.click(
            fn=ui_reject,
            inputs=[
                app_state,
                thread_id,
                human_feedback_box,
            ],
            outputs=[
                app_state,
                proposal_output,
                final_answer_output,
                image_gallery,
            ],
        )

        clear_btn.click(
            fn=ui_clear,
            inputs=[],
            outputs=[
                app_state,
                thread_id,
                proposal_output,
                edited_query_box,
                human_feedback_box,
                approve_btn,
                reject_btn,
                clear_btn,
                final_answer_output,
                image_gallery,
            ],
        )

    return demo
