"""
hitl_search_agent.main
~~~~~~~~~~~~~~~~~~~~~~

Application entry point.

Run with::

    python -m hitl_search_agent
"""

from __future__ import annotations

from hitl_search_agent.logging_config import setup_logging
from hitl_search_agent.config import get_settings


def main() -> None:
    """Build and launch the Gradio application."""
    settings = get_settings()

    # Set up logging before anything else
    setup_logging(level=settings.log_level)

    # Import after logging is configured so all loggers pick it up
    import gradio as gr
    from hitl_search_agent.ui.gradio_app import build_ui

    demo = build_ui()

    demo.launch(
        server_name=settings.server_host,
        server_port=settings.server_port,
        share=False,
        theme=gr.themes.Soft(),
    )


if __name__ == "__main__":
    main()
