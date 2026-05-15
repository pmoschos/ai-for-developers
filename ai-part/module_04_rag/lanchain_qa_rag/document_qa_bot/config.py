"""
Configuration for Document Q&A Bot
===================================
"""

import os
from pathlib import Path
from dataclasses import dataclass
from functools import lru_cache


@dataclass
class Config:
    """Application configuration"""
    
    # Paths
    base_path: Path = Path(__file__).parent
    chroma_db_path: Path = None
    sample_docs_path: Path = None
    
    # Chunking
    chunk_size: int = 1000
    chunk_overlap: int = 200
    
    # Retrieval
    top_k: int = 4
    min_relevance_score: float = 0.15
    
    # Embedding
    embedding_model: str = "text-embedding-3-small"
    
    # Generation
    llm_model: str = "gpt-4o-mini"
    max_tokens: int = 500
    temperature: float = 0.3
    
    def __post_init__(self):
        if self.chroma_db_path is None:
            self.chroma_db_path = self.base_path / "chroma_db"
        if self.sample_docs_path is None:
            self.sample_docs_path = self.base_path / "sample_docs"
        
        # Create directories if they don't exist
        self.chroma_db_path.mkdir(exist_ok=True)
        self.sample_docs_path.mkdir(exist_ok=True)


@lru_cache()
def get_config() -> Config:
    """Get cached configuration instance"""
    return Config()
