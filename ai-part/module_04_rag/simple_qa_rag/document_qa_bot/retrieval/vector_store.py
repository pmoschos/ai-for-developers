"""
Vector Store
=============
ChromaDB wrapper for storing and searching embeddings.
"""

from typing import List, Dict, Optional
import uuid
import logging

try:
    import chromadb
    from chromadb.config import Settings
except ImportError:
    raise ImportError("chromadb is required. Install with: pip install chromadb")

logger = logging.getLogger(__name__)


class VectorStore:
    """ChromaDB vector store for document embeddings"""
    
    def __init__(self, persist_directory: str = "./chroma_db", collection_name: str = "documents"):
        """
        Initialize the vector store.
        
        Args:
            persist_directory: Directory to persist the database
            collection_name: Name of the collection
        """
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        
        # Initialize ChromaDB client with persistence
        self.client = chromadb.PersistentClient(path=persist_directory)
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}  # Use cosine similarity
        )
        
        logger.info(f"Vector store initialized at {persist_directory}")
    
    def add_documents(self, documents: List[Dict], embedder) -> List[str]:
        """
        Add documents to the vector store.
        
        Args:
            documents: List of dicts with 'content' and 'metadata'
            embedder: Embedder instance to generate embeddings
            
        Returns:
            List of document IDs
        """
        if not documents:
            return []
        
        # Extract content and generate embeddings
        contents = [doc["content"] for doc in documents]
        embeddings = embedder.embed_batch(contents)
        
        # Generate IDs
        ids = [str(uuid.uuid4()) for _ in documents]
        
        # Prepare metadata (ChromaDB requires simple types)
        metadatas = []
        for doc in documents:
            meta = doc.get("metadata", {})
            # Convert all values to strings for ChromaDB compatibility
            clean_meta = {k: str(v) for k, v in meta.items()}
            metadatas.append(clean_meta)
        
        # Add to collection
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=contents,
            metadatas=metadatas
        )
        
        logger.info(f"Added {len(documents)} documents to vector store")
        
        return ids
    
    def search(self, query_embedding: List[float], top_k: int = 4) -> List[Dict]:
        """
        Search for similar documents.
        
        Args:
            query_embedding: Query embedding vector
            top_k: Number of results to return
            
        Returns:
            List of search results with content, metadata, and score
        """
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=["documents", "metadatas", "distances"]
        )
        
        # Format results
        formatted_results = []
        
        if results["documents"] and results["documents"][0]:
            for i in range(len(results["documents"][0])):
                formatted_results.append({
                    "content": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                    "score": 1 - results["distances"][0][i]  # Convert distance to similarity
                })
        
        return formatted_results
    
    def get_stats(self) -> Dict:
        """Get statistics about the vector store"""
        count = self.collection.count()
        
        # Get unique sources
        sources = set()
        if count > 0:
            results = self.collection.get(include=["metadatas"])
            for meta in results["metadatas"]:
                if "source" in meta:
                    sources.add(meta["source"])
        
        return {
            "total_chunks": count,
            "unique_sources": len(sources),
            "sources": list(sources)
        }
    
    def clear(self):
        """Clear all documents from the collection"""
        self.client.delete_collection(self.collection_name)
        self.collection = self.client.create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        logger.info("Vector store cleared")
