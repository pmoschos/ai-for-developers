"""
Copywriting Router
==================
Endpoint for generating marketing copy using LLM.
"""

import json
import logging
from typing import List
from fastapi import APIRouter, Request, HTTPException

from app.models import CopywriterRequest, CopywriterResponse, CopyVariant
from app.llm_client import get_llm_client

logger = logging.getLogger(__name__)
router = APIRouter()


COPYWRITER_SYSTEM_PROMPT = """You are an expert marketing copywriter with years of experience writing compelling copy that converts.

You create:
- Attention-grabbing headlines
- Persuasive body copy
- Effective calls to action

You must respond with valid JSON containing an array of copy variants."""


def build_copywriter_prompt(request: CopywriterRequest) -> str:
    """Build the prompt for copywriting"""
    audience = request.target_audience or "general audience"
    
    return f"""Create {request.num_variants} marketing copy variants for:

Product: {request.product_name}
Description: {request.description}
Tone: {request.tone.value}
Target Audience: {audience}

Return your response as JSON in this exact format:
{{
    "variants": [
        {{
            "headline": "Attention-grabbing headline",
            "body": "Persuasive body copy (2-3 sentences)",
            "cta": "Call to action button text"
        }}
    ]
}}

Generate exactly {request.num_variants} unique variants with different approaches."""


@router.post("", response_model=CopywriterResponse)
async def generate_copy(request: CopywriterRequest, req: Request):
    """
    Generate marketing copy variants for a product.
    
    - **product_name**: Name of the product
    - **description**: Product description
    - **tone**: Desired tone (professional, casual, playful, urgent, luxurious)
    - **target_audience**: Target audience description
    - **num_variants**: Number of variants to generate (1-5)
    """
    logger.info(f"Copywriting request: {request.product_name}, tone={request.tone}")
    
    try:
        llm = get_llm_client()
        
        messages = [
            {"role": "system", "content": COPYWRITER_SYSTEM_PROMPT},
            {"role": "user", "content": build_copywriter_prompt(request)}
        ]
        
        response = llm.complete(
            messages=messages,
            max_tokens=800,
            temperature=0.8  # Higher creativity for marketing
        )
        
        # Track cost
        tracker = req.app.state.cost_tracker
        tracker.add_request(
            endpoint="/copywriter",
            tokens=response.total_tokens,
            cost=response.estimated_cost
        )
        
        # Parse JSON response
        try:
            content = response.content
            # Clean up markdown if present
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
            
            result = json.loads(content.strip())
        except json.JSONDecodeError as e:
            logger.error(f"JSON parse error: {e}\nContent: {response.content}")
            raise HTTPException(status_code=500, detail="Failed to parse AI response")
        
        # Build response
        variants = [
            CopyVariant(
                headline=v.get("headline", ""),
                body=v.get("body", ""),
                cta=v.get("cta", "")
            )
            for v in result.get("variants", [])
        ]
        
        if not variants:
            raise HTTPException(status_code=500, detail="No variants generated")
        
        return CopywriterResponse(
            variants=variants,
            tokens_used=response.total_tokens,
            estimated_cost=response.estimated_cost
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Copywriting failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
