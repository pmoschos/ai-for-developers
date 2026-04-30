"""
Pydantic Models
===============
Request and response models for the AI API.
"""

from typing import Optional, List
from pydantic import BaseModel, Field
from enum import Enum


# ==================== Summarization ====================

class SummarizeRequest(BaseModel):
    """Request model for text summarization"""
    text: str = Field(..., min_length=10, description="The text to summarize")
    max_length: Optional[int] = Field(
        default=150,
        ge=20,
        le=500,
        description="Maximum length of summary in words"
    )
    style: Optional[str] = Field(
        default="concise",
        description="Summary style: concise, detailed, or bullet_points"
    )
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "text": "Artificial intelligence (AI) is transforming industries worldwide...",
                "max_length": 100,
                "style": "concise"
            }
        }
    }


class SummarizeResponse(BaseModel):
    """Response model for text summarization"""
    summary: str = Field(..., description="The generated summary")
    original_length: int = Field(..., description="Word count of original text")
    summary_length: int = Field(..., description="Word count of summary")
    compression_ratio: float = Field(..., description="Compression ratio achieved")
    tokens_used: int = Field(..., description="Total tokens used")
    estimated_cost: float = Field(..., description="Estimated cost in USD")


# ==================== Sentiment Analysis ====================

class SentimentLabel(str, Enum):
    """Possible sentiment labels"""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    MIXED = "mixed"


class SentimentRequest(BaseModel):
    """Request model for sentiment analysis"""
    text: str = Field(..., min_length=1, description="Text to analyze")
    include_reasoning: Optional[bool] = Field(
        default=False,
        description="Whether to include reasoning for the classification"
    )
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "text": "I absolutely love this product! The quality is amazing.",
                "include_reasoning": True
            }
        }
    }


class SentimentResponse(BaseModel):
    """Response model for sentiment analysis"""
    sentiment: SentimentLabel = Field(..., description="Detected sentiment")
    confidence: float = Field(..., ge=0, le=1, description="Confidence score")
    reasoning: Optional[str] = Field(
        default=None,
        description="Explanation for the classification"
    )
    tokens_used: int = Field(..., description="Total tokens used")
    estimated_cost: float = Field(..., description="Estimated cost in USD")


# ==================== Copywriting ====================

class CopyTone(str, Enum):
    """Available tones for copy"""
    PROFESSIONAL = "professional"
    CASUAL = "casual"
    PLAYFUL = "playful"
    URGENT = "urgent"
    LUXURIOUS = "luxurious"


class CopywriterRequest(BaseModel):
    """Request model for copywriting"""
    product_name: str = Field(..., min_length=1, description="Name of the product")
    description: str = Field(..., min_length=10, description="Product description")
    tone: Optional[CopyTone] = Field(
        default=CopyTone.PROFESSIONAL,
        description="Desired tone of the copy"
    )
    target_audience: Optional[str] = Field(
        default=None,
        description="Target audience description"
    )
    num_variants: Optional[int] = Field(
        default=3,
        ge=1,
        le=5,
        description="Number of copy variants to generate"
    )
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "product_name": "CloudSync Pro",
                "description": "A cloud storage solution with AI-powered file organization",
                "tone": "professional",
                "target_audience": "small business owners",
                "num_variants": 3
            }
        }
    }


class CopyVariant(BaseModel):
    """A single copy variant"""
    headline: str = Field(..., description="Attention-grabbing headline")
    body: str = Field(..., description="Main body copy")
    cta: str = Field(..., description="Call to action")


class CopywriterResponse(BaseModel):
    """Response model for copywriting"""
    variants: List[CopyVariant] = Field(..., description="Generated copy variants")
    tokens_used: int = Field(..., description="Total tokens used")
    estimated_cost: float = Field(..., description="Estimated cost in USD")


# ==================== Common ====================

class ErrorResponse(BaseModel):
    """Standard error response"""
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[dict] = Field(default=None, description="Additional details")


# ==================== Batch Processing ====================

class BatchRequest(BaseModel):
    """Request model for batch text processing"""
    texts: List[str] = Field(
        ...,
        min_length=1,
        max_length=10,
        description="List of texts to process (1-10 items)"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "texts": [
                    "AI is transforming healthcare by enabling faster diagnoses.",
                    "The stock market saw significant gains this quarter.",
                    "Climate change continues to affect global weather patterns."
                ]
            }
        }
    }


class BatchItemResult(BaseModel):
    """Result for a single batch item"""
    index: int = Field(..., description="Position in the original batch")
    status: str = Field(..., description="Processing status: completed or failed")
    result: str = Field(..., description="Summary or error message")
    tokens_used: int = Field(default=0, description="Tokens used for this item")
    estimated_cost: float = Field(default=0.0, description="Estimated cost for this item")


class BatchResponse(BaseModel):
    """Response model for batch processing"""
    results: List[BatchItemResult] = Field(..., description="Individual item results")
    total_items: int = Field(..., description="Number of items processed")
    completed: int = Field(..., description="Successfully completed items")
    failed: int = Field(..., description="Failed items")
    total_tokens: int = Field(..., description="Total tokens used across all items")
    total_cost: float = Field(..., description="Total cost across all items")
    processing_time_ms: float = Field(..., description="Total processing time in ms")
