"""
Sentiment Analysis Router
=========================
Endpoint for sentiment classification using LLM.
"""

import json
import logging
from fastapi import APIRouter, Request, HTTPException

from app.models import SentimentRequest, SentimentResponse, SentimentLabel
from app.llm_client import get_llm_client

logger = logging.getLogger(__name__)
router = APIRouter()


SENTIMENT_SYSTEM_PROMPT = """You are an expert sentiment analyst. You classify text sentiment accurately and provide confidence scores.

You must respond with valid JSON in exactly this format:
{
    "sentiment": "positive" | "negative" | "neutral" | "mixed",
    "confidence": 0.0 to 1.0,
    "reasoning": "Brief explanation of classification"
}

Guidelines:
- positive: Clearly expresses satisfaction, happiness, approval
- negative: Clearly expresses dissatisfaction, anger, disappointment
- neutral: No strong emotional content, factual statements
- mixed: Contains both positive and negative sentiments
- confidence: How certain you are (0.5 = unsure, 0.9+ = very confident)"""


@router.post("", response_model=SentimentResponse)
async def analyze_sentiment(request: SentimentRequest, req: Request):
    """
    Analyze the sentiment of the provided text.
    
    - **text**: The text to analyze
    - **include_reasoning**: Whether to include explanation for the classification
    """
    logger.info(f"Sentiment analysis request: {len(request.text)} chars")
    
    try:
        llm = get_llm_client()
        
        messages = [
            {"role": "system", "content": SENTIMENT_SYSTEM_PROMPT},
            {"role": "user", "content": f'Analyze the sentiment of this text:\n\n"{request.text}"'}
        ]
        
        response = llm.complete(
            messages=messages,
            max_tokens=200,
            temperature=0  # Deterministic for classification
        )
        
        # Track cost
        tracker = req.app.state.cost_tracker
        tracker.add_request(
            endpoint="/sentiment",
            tokens=response.total_tokens,
            cost=response.estimated_cost
        )
        
        # Parse JSON response
        try:
            result = json.loads(response.content)
        except json.JSONDecodeError:
            # Try to extract from markdown code block if present
            content = response.content
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
            result = json.loads(content.strip())
        
        # Map to enum
        sentiment_map = {
            "positive": SentimentLabel.POSITIVE,
            "negative": SentimentLabel.NEGATIVE,
            "neutral": SentimentLabel.NEUTRAL,
            "mixed": SentimentLabel.MIXED
        }
        
        sentiment = sentiment_map.get(
            result.get("sentiment", "neutral").lower(),
            SentimentLabel.NEUTRAL
        )
        
        return SentimentResponse(
            sentiment=sentiment,
            confidence=float(result.get("confidence", 0.5)),
            reasoning=result.get("reasoning") if request.include_reasoning else None,
            tokens_used=response.total_tokens,
            estimated_cost=response.estimated_cost
        )
        
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse sentiment response: {e}")
        raise HTTPException(status_code=500, detail="Failed to parse AI response")
    except Exception as e:
        logger.error(f"Sentiment analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
