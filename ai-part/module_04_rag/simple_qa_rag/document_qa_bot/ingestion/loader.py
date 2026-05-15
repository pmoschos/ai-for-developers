"""
Document Loader
===============
Load documents from various file formats.
"""

from pathlib import Path
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class DocumentLoader:
    """Load documents from files into a standard format"""
    
    def load(self, path: Path) -> List[Dict]:
        """
        Load a document and return its content.
        
        Args:
            path: Path to the document
            
        Returns:
            List of dictionaries with 'content' and 'metadata' keys
        """
        suffix = path.suffix.lower()
        
        loaders = {
            ".txt": self._load_text,
            ".md": self._load_text,
            ".pdf": self._load_pdf,
            ".docx": self._load_docx,
        }
        
        loader = loaders.get(suffix)
        if not loader:
            logger.warning(f"Unsupported file type: {suffix}")
            return []
        
        try:
            return loader(path)
        except Exception as e:
            logger.error(f"Error loading {path}: {e}")
            raise
    
    def _load_text(self, path: Path) -> List[Dict]:
        """Load plain text or markdown file"""
        content = path.read_text(encoding='utf-8')
        return [{
            "content": content,
            "metadata": {
                "source": path.name,
                "type": "text"
            }
        }]
    
    def _load_pdf(self, path: Path) -> List[Dict]:
        """Load PDF file"""
        try:
            # pyrefly: ignore [missing-import]
            from pypdf import PdfReader
        except ImportError:
            raise ImportError("pypdf is required for PDF loading. Install with: pip install pypdf")
        
        reader = PdfReader(path)
        documents = []
        
        for i, page in enumerate(reader.pages):
            text = page.extract_text()
            if text.strip():
                documents.append({
                    "content": text,
                    "metadata": {
                        "source": path.name,
                        "page": i + 1,
                        "type": "pdf"
                    }
                })
        
        return documents
    
    def _load_docx(self, path: Path) -> List[Dict]:
        """Load Word document"""
        try:
            from docx import Document
        except ImportError:
            raise ImportError("python-docx is required for DOCX loading. Install with: pip install python-docx")
        
        doc = Document(path)
        content = "\n\n".join(para.text for para in doc.paragraphs if para.text.strip())
        
        return [{
            "content": content,
            "metadata": {
                "source": path.name,
                "type": "docx"
            }
        }]
