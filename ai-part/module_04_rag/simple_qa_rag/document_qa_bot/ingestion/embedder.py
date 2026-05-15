"""
Embedder
========
Generate embeddings using OpenAI's API.
"""

from typing import List
import logging
from openai import OpenAI

logger = logging.getLogger(__name__)


class Embedder:
    """Generate embeddings for text using OpenAI"""
    
    def __init__(self, model: str = "text-embedding-3-small"):
        """
        Initialize the embedder.
        
        Args:
            model: OpenAI embedding model to use
        """
        self.model = model
        self.client = OpenAI()
        self.dimensions = 1536  # Default for text-embedding-3-small
    
    def embed(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.
        
        Args:
            text: Text to embed
            
        Returns:
            List of floats representing the embedding
        """
        response = self.client.embeddings.create(
            input=text,
            model=self.model
        )
        return response.data[0].embedding
    
    def embed_batch(self, texts: List[str], batch_size: int = 100) -> List[List[float]]:
        """
        Generate embeddings for multiple texts.
        
        Args:
            texts: List of texts to embed
            batch_size: Number of texts to embed per API call
            
        Returns:
            List of embeddings
        """
        all_embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            
            response = self.client.embeddings.create(
                input=batch,
                model=self.model
            )
            
            # Sort by index to maintain order
            sorted_embeddings = sorted(response.data, key=lambda x: x.index)
            batch_embeddings = [e.embedding for e in sorted_embeddings]
            
            all_embeddings.extend(batch_embeddings)
            
            logger.debug(f"Embedded batch {i // batch_size + 1}, total: {len(all_embeddings)}")
        
        return all_embeddings
