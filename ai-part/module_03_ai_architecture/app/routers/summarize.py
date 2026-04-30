"""
Summarization Router
====================
Endpoint for text summarization using LLM.
"""

import logging
from fastapi import APIRouter, Request, HTTPException

from app.models import SummarizeRequest, SummarizeResponse
from app.llm_client import get_llm_client

logger = logging.getLogger(__name__)
router = APIRouter()


SUMMARIZE_SYSTEM_PROMPT = """You are an expert at summarizing text. Your summaries are:
- Accurate and faithful to the original
- Concise and well-structured
- Written in clear, accessible language

You will be given text to summarize along with style instructions."""


def build_user_prompt(request: SummarizeRequest) -> str:
    """Build the user prompt for summarization"""
    style_instructions = {
        "concise": "Provide a brief, to-the-point summary in paragraph form.",
        "detailed": "Provide a comprehensive summary that captures all key points.",
        "bullet_points": "Provide the summary as a bulleted list of key points."
    }
    
    style = style_instructions.get(request.style, style_instructions["concise"])
    
    return f"""Please summarize the following text.

Style: {style}
Maximum length: {request.max_length} words

Text to summarize:
\"\"\"
{request.text}
\"\"\"

Summary:"""


@router.post("", response_model=SummarizeResponse)
async def summarize_text(request: SummarizeRequest, req: Request):
    """
    Summarize the provided text.
    
    - **text**: The text to summarize (minimum 10 characters)
    - **max_length**: Maximum summary length in words (20-500)
    - **style**: Summary style (concise, detailed, or bullet_points)
    """
    logger.info(f"Summarization request: {len(request.text)} chars, style={request.style}")
    
    try:
        llm = get_llm_client()
        
        # Build messages
        messages = [
            {"role": "system", "content": SUMMARIZE_SYSTEM_PROMPT},
            {"role": "user", "content": build_user_prompt(request)}
        ]
        
        # Get completion
        response = llm.complete(
            messages=messages,
            max_tokens=request.max_length * 2,  # Buffer for tokens vs words
            temperature=0.3  # Lower temperature for accuracy
        )
        
        # Track cost in app state
        tracker = req.app.state.cost_tracker
        tracker.add_request(
            endpoint="/summarize",
            tokens=response.total_tokens,
            cost=response.estimated_cost
        )
        
        # Calculate metrics
        original_words = len(request.text.split())
        summary_words = len(response.content.split())
        compression = 1 - (summary_words / original_words) if original_words > 0 else 0
        
        return SummarizeResponse(
            summary=response.content,
            original_length=original_words,
            summary_length=summary_words,
            compression_ratio=round(compression, 2),
            tokens_used=response.total_tokens,
            estimated_cost=response.estimated_cost
        )
        
    except Exception as e:
        logger.error(f"Summarization failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
