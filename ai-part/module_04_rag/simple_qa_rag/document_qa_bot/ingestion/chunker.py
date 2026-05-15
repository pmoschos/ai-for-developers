"""
Text Chunker
============
Split documents into chunks for embedding.
"""

from typing import List, Dict, Optional
import re


class TextChunker:
    """Split text into overlapping chunks"""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        """
        Initialize the chunker.
        
        Args:
            chunk_size: Target size of each chunk in characters
            chunk_overlap: Number of characters to overlap between chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def chunk(self, text: str, metadata: Optional[Dict] = None) -> List[Dict]:
        """
        Split text into chunks with overlap.
        
        Args:
            text: Text to split
            metadata: Metadata to attach to each chunk
            
        Returns:
            List of chunk dictionaries with 'content' and 'metadata'
        """
        if not text.strip():
            return []
        
        # Try to split on paragraphs first
        chunks = self._recursive_split(text)
        
        # Add metadata to each chunk
        result = []
        for i, chunk_text in enumerate(chunks):
            chunk_metadata = dict(metadata or {})
            chunk_metadata["chunk_index"] = i
            chunk_metadata["chunk_count"] = len(chunks)
            
            result.append({
                "content": chunk_text.strip(),
                "metadata": chunk_metadata
            })
        
        return result
    
    def _recursive_split(self, text: str) -> List[str]:
        """
        Recursively split text using different separators.
        
        Priority: double newline > single newline > sentence > space
        """
        separators = ["\n\n", "\n", ". ", " "]
        
        return self._split_with_separators(text, separators)
    
    def _split_with_separators(self, text: str, separators: List[str]) -> List[str]:
        """Split text trying each separator in order"""
        if not separators or len(text) <= self.chunk_size:
            return [text] if text.strip() else []
        
        separator = separators[0]
        remaining_separators = separators[1:]
        
        # Split by current separator
        parts = text.split(separator)
        
        chunks = []
        current_chunk = ""
        
        for part in parts:
            # If adding this part would exceed chunk size
            test_chunk = current_chunk + separator + part if current_chunk else part
            
            if len(test_chunk) > self.chunk_size:
                # Save current chunk if it has content
                if current_chunk:
                    chunks.append(current_chunk)
                
                # If the part itself is too large, split it further
                if len(part) > self.chunk_size:
                    sub_chunks = self._split_with_separators(part, remaining_separators)
                    chunks.extend(sub_chunks)
                    current_chunk = ""
                else:
                    current_chunk = part
            else:
                current_chunk = test_chunk
        
        # Add the last chunk
        if current_chunk:
            chunks.append(current_chunk)
        
        # Add overlap between chunks
        if self.chunk_overlap > 0 and len(chunks) > 1:
            chunks = self._add_overlap(chunks)
        
        return chunks
    
    def _add_overlap(self, chunks: List[str]) -> List[str]:
        """Add overlap from the end of each chunk to the start of the next"""
        result = [chunks[0]]
        
        for i in range(1, len(chunks)):
            prev_chunk = chunks[i - 1]
            curr_chunk = chunks[i]
            
            # Get overlap from previous chunk
            overlap = prev_chunk[-self.chunk_overlap:] if len(prev_chunk) > self.chunk_overlap else prev_chunk
            
            # Prepend overlap to current chunk
            result.append(overlap + " " + curr_chunk)
        
        return result
