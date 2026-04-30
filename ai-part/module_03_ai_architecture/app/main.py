"""
Module 3: FastAPI Application - Main Entry Point
================================================
A production-ready AI-powered API with multiple endpoints.
"""

import os
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

# Load environment variables
load_dotenv(Path(__file__).parent.parent / ".env", override=True)

print(Path(Path(__file__).parent.parent))

# Import routers
from app.routers import summarize, sentiment, copywriter, stream, batch
from app.middleware.cost_tracker import CostTracker
from app.middleware.error_handler import setup_error_handlers

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Cost tracker instance
cost_tracker = CostTracker()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    logger.info("🚀 Starting AI API Server...")
    logger.info(f"📊 Cost tracking enabled")
    yield
    logger.info("👋 Shutting down...")
    # Log final cost summary
    summary = cost_tracker.get_summary()
    logger.info(f"💰 Total session cost: ${summary['total_cost']:.6f}")
    logger.info(f"📈 Total requests: {summary['total_requests']}")


# Create FastAPI app
app = FastAPI(
    title="AI-Powered API",
    description="""
    A production-ready API that wraps LLM capabilities.
    
    ## Features
    - **Summarization**: Condense long text into key points
    - **Sentiment Analysis**: Classify text sentiment with confidence scores
    - **Copywriting**: Generate marketing copy variants
    
    ## Technical Features
    - Automatic retry with exponential backoff
    - Cost tracking per request
    - Rate limiting
    - Comprehensive error handling
    """,
    version="1.0.0",
    lifespan=lifespan
)

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup error handlers
setup_error_handlers(app)

# Store cost tracker in app state
app.state.cost_tracker = cost_tracker

# Include routers
app.include_router(summarize.router, prefix="/summarize", tags=["Summarization"])
app.include_router(sentiment.router, prefix="/sentiment", tags=["Sentiment Analysis"])
app.include_router(copywriter.router, prefix="/copywriter", tags=["Copywriting"])
app.include_router(stream.router, prefix="/stream", tags=["Streaming"])
app.include_router(batch.router, prefix="/batch", tags=["Batch Processing"])


@app.get("/", tags=["Health"])
async def root():
    """Root endpoint with API information"""
    return {
        "name": "AI-Powered API",
        "version": "1.0.0",
        "status": "healthy",
        "endpoints": {
            "summarize": "/summarize",
            "sentiment": "/sentiment",
            "copywriter": "/copywriter",
            "docs": "/docs",
            "health": "/health",
            "stats": "/stats"
        }
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "openai_configured": bool(os.getenv("OPENAI_API_KEY"))
    }


@app.get("/stats", tags=["Monitoring"])
async def get_stats(request: Request):
    """Get usage statistics and cost tracking"""
    tracker = request.app.state.cost_tracker
    return tracker.get_summary()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
