"""
hitl_search_agent.prompts.summary_prompts
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

System prompt for the summarization node.
"""

SUMMARY_SYSTEM_PROMPT = """\
You are an assistant that summarizes web search results.

Your job:
- Answer the user's original request using the provided search results.
- Be clear, concise, and useful.
- Mention the most relevant source URLs when available.
- If images were returned, mention that related images are displayed below.
- If the search results are insufficient, say so clearly.
- Do not invent sources.
"""


def build_summary_user_message(
    user_request: str,
    search_query: str,
    human_feedback: str,
    num_images: int,
    raw_results: object,
) -> str:
    """
    Build the user message for the summarization LLM call.
    """
    return (
        f"Original user request:\n{user_request}\n\n"
        f"Approved search query:\n{search_query}\n\n"
        f"Human feedback:\n{human_feedback}\n\n"
        f"Number of returned image URLs:\n{num_images}\n\n"
        f"Raw web search results:\n{raw_results}"
    )
