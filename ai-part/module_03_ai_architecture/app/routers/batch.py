"""
Batch Processing Router
========================
Process multiple texts in parallel — a key production pattern.
Demonstrates asyncio.gather for concurrent LLM calls.
"""

import asyncio
import logging
import time
from fastapi import APIRouter, Request, HTTPException

from app.models import BatchRequest, BatchResponse, BatchItemResult
from app.llm_client import get_llm_client

logger = logging.getLogger(__name__)
router = APIRouter()


BATCH_SYSTEM_PROMPT = """You are a concise text analyzer.
Given a piece of text, provide a one-sentence summary.
Keep it under 30 words."""


async def process_single_item(text: str, index: int) -> BatchItemResult:
    """Process a single text item. Runs in the event loop executor."""
    try:
        llm = get_llm_client()
        response = llm.simple_complete(
            prompt=f"Summarize this text in one sentence:\n\n{text}",
            system=BATCH_SYSTEM_PROMPT,
            max_tokens=60,
            temperature=0.3
        )
        return BatchItemResult(
            index=index,
            status="completed",
            result=response.content,
            tokens_used=response.total_tokens,
            estimated_cost=response.estimated_cost
        )
    except Exception as e:
        logger.error(f"Batch item {index} failed: {e}")
        return BatchItemResult(
            index=index,
            status="failed",
            result=f"Error: {str(e)[:100]}",
            tokens_used=0,
            estimated_cost=0.0
        )


@router.post("", response_model=BatchResponse)
async def batch_process(request: BatchRequest, req: Request):
    """
    Process multiple texts in a single request.

    - **texts**: List of texts to process (1-10 items)
    - Each text is summarized concurrently for speed

    Returns individual results plus aggregate statistics.
    """
    logger.info(f"Batch request: {len(request.texts)} items")
    start_time = time.time()

    # Process all items concurrently using asyncio
    loop = asyncio.get_event_loop()
    tasks = [
        loop.run_in_executor(None, lambda i=i, t=t: process_single_item_sync(t, i))
        for i, t in enumerate(request.texts)
    ]
    results = await asyncio.gather(*tasks)

    elapsed_ms = (time.time() - start_time) * 1000

    # Aggregate stats
    total_tokens = sum(r.tokens_used for r in results)
    total_cost = sum(r.estimated_cost for r in results)
    completed = sum(1 for r in results if r.status == "completed")
    failed = sum(1 for r in results if r.status == "failed")

    # Track cost
    tracker = req.app.state.cost_tracker
    tracker.add_request(
        endpoint="/batch",
        tokens=total_tokens,
        cost=total_cost
    )

    return BatchResponse(
        results=results,
        total_items=len(request.texts),
        completed=completed,
        failed=failed,
        total_tokens=total_tokens,
        total_cost=total_cost,
        processing_time_ms=round(elapsed_ms, 2)
    )


def process_single_item_sync(text: str, index: int) -> BatchItemResult:
    """Synchronous wrapper for use in executor."""
    try:
        llm = get_llm_client()
        response = llm.simple_complete(
            prompt=f"Summarize this text in one sentence:\n\n{text}",
            system=BATCH_SYSTEM_PROMPT,
            max_tokens=60,
            temperature=0.3
        )
        return BatchItemResult(
            index=index,
            status="completed",
            result=response.content,
            tokens_used=response.total_tokens,
            estimated_cost=response.estimated_cost
        )
    except Exception as e:
        logger.error(f"Batch item {index} failed: {e}")
        return BatchItemResult(
            index=index,
            status="failed",
            result=f"Error: {str(e)[:100]}",
            tokens_used=0,
            estimated_cost=0.0
        )
