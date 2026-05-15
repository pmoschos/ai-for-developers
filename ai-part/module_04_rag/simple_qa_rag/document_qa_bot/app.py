"""
Document Q&A Bot - Main Application
====================================
A RAG-powered chatbot that answers questions based on your documents.

Usage:
    python app.py ingest <file_or_directory>   # Ingest documents
    python app.py ask "Your question here"     # Ask a single question
    python app.py chat                         # Interactive chat mode
    python app.py list                         # List ingested documents
    python app.py clear                        # Clear the database
"""

import os
import sys
import argparse
from pathlib import Path
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.table import Table

# Load environment variables
load_dotenv(Path(__file__).parent.parent.parent / ".env", override=True)

from config import get_config
from ingestion.loader import DocumentLoader
from ingestion.chunker import TextChunker
from ingestion.embedder import Embedder
from retrieval.vector_store import VectorStore
from retrieval.retriever import Retriever
from generation.qa_chain import QAChain

console = Console()


class DocumentQABot:
    """Main application class for the Document Q&A Bot"""
    
    def __init__(self):
        self.config = get_config()
        self.loader = DocumentLoader()
        self.chunker = TextChunker(
            chunk_size=self.config.chunk_size,
            chunk_overlap=self.config.chunk_overlap
        )
        self.embedder = Embedder()
        self.vector_store = VectorStore(
            persist_directory=str(self.config.chroma_db_path)
        )
        self.retriever = Retriever(
            vector_store=self.vector_store,
            embedder=self.embedder,
            top_k=self.config.top_k
        )
        self.qa_chain = QAChain(retriever=self.retriever)
    
    def ingest_document(self, file_path: str) -> int:
        """
        Ingest a single document into the vector store.
        
        Returns the number of chunks created.
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        console.print(f"[dim]Loading {path.name}...[/dim]")
        
        # Load document
        documents = self.loader.load(path)
        
        if not documents:
            console.print(f"[yellow]No content extracted from {path.name}[/yellow]")
            return 0
        
        console.print(f"[dim]Chunking ({len(documents)} documents)...[/dim]")
        
        # Chunk documents
        chunks = []
        for doc in documents:
            doc_chunks = self.chunker.chunk(doc["content"], doc["metadata"])
            chunks.extend(doc_chunks)
        
        console.print(f"[dim]Embedding {len(chunks)} chunks...[/dim]")
        
        # Embed and store
        self.vector_store.add_documents(chunks, self.embedder)
        
        console.print(f"[green]✓[/green] Ingested {len(chunks)} chunks from {path.name}")
        
        return len(chunks)
    
    def ingest_directory(self, dir_path: str) -> int:
        """Ingest all supported documents from a directory"""
        path = Path(dir_path)
        
        if not path.is_dir():
            raise NotADirectoryError(f"Not a directory: {dir_path}")
        
        total_chunks = 0
        supported_extensions = {".pdf", ".txt", ".md", ".docx"}
        
        for file_path in path.iterdir():
            if file_path.suffix.lower() in supported_extensions:
                try:
                    chunks = self.ingest_document(str(file_path))
                    total_chunks += chunks
                except Exception as e:
                    console.print(f"[red]Error processing {file_path.name}: {e}[/red]")
        
        return total_chunks
    
    def ask(self, question: str, show_sources: bool = True) -> str:
        """Ask a question and get an answer based on the documents"""
        result = self.qa_chain.answer(question)
        
        return result
    
    def chat(self):
        """Interactive chat mode"""
        console.print(Panel(
            "[bold blue]📚 Document Q&A Chat[/bold blue]\n\n"
            "Ask questions about your ingested documents.\n"
            "Type 'quit' to exit, 'sources' to toggle source display.",
            border_style="blue"
        ))
        
        show_sources = True
        
        while True:
            try:
                question = console.input("\n[green]You:[/green] ")
                
                if question.lower() in ['quit', 'exit', 'q']:
                    break
                
                if question.lower() == 'sources':
                    show_sources = not show_sources
                    console.print(f"[dim]Source display: {'on' if show_sources else 'off'}[/dim]")
                    continue
                
                if not question.strip():
                    continue
                
                console.print("[dim]Thinking...[/dim]")
                
                result = self.ask(question, show_sources)
                
                console.print(f"\n[blue]Assistant:[/blue]")
                console.print(Panel(Markdown(result["answer"]), border_style="blue"))
                
                if show_sources and result.get("sources"):
                    console.print("\n[dim]Sources:[/dim]")
                    for i, source in enumerate(result["sources"], 1):
                        console.print(f"  {i}. {source['source']} (score: {source['score']:.3f})")
                
            except KeyboardInterrupt:
                break
        
        console.print("\n[dim]Goodbye![/dim]")
    
    def list_documents(self):
        """List all ingested documents"""
        stats = self.vector_store.get_stats()
        
        table = Table(title="Ingested Documents")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Total Chunks", str(stats["total_chunks"]))
        table.add_row("Unique Sources", str(stats["unique_sources"]))
        table.add_row("Storage Path", str(self.config.chroma_db_path))
        
        console.print(table)
        
        if stats["sources"]:
            console.print("\n[bold]Sources:[/bold]")
            for source in stats["sources"]:
                console.print(f"  • {source}")
    
    def clear_database(self):
        """Clear all documents from the database"""
        self.vector_store.clear()
        console.print("[green]✓[/green] Database cleared")


def main():
    parser = argparse.ArgumentParser(
        description="Document Q&A Bot - Ask questions about your documents"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Ingest command
    ingest_parser = subparsers.add_parser("ingest", help="Ingest documents")
    ingest_parser.add_argument("path", help="File or directory to ingest")
    
    # Ask command
    ask_parser = subparsers.add_parser("ask", help="Ask a question")
    ask_parser.add_argument("question", help="Question to ask")
    ask_parser.add_argument("--no-sources", action="store_true", help="Hide sources")
    
    # Chat command
    subparsers.add_parser("chat", help="Interactive chat mode")
    
    # List command
    subparsers.add_parser("list", help="List ingested documents")
    
    # Clear command
    subparsers.add_parser("clear", help="Clear the database")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        bot = DocumentQABot()
        
        if args.command == "ingest":
            path = Path(args.path)
            if path.is_dir():
                total = bot.ingest_directory(args.path)
            else:
                total = bot.ingest_document(args.path)
            console.print(f"\n[bold green]✓ Total chunks ingested: {total}[/bold green]")
        
        elif args.command == "ask":
            result = bot.ask(args.question, not args.no_sources)
            console.print(Panel(Markdown(result["answer"]), title="Answer", border_style="green"))
            
            if not args.no_sources and result.get("sources"):
                console.print("\n[dim]Sources:[/dim]")
                for i, source in enumerate(result["sources"], 1):
                    console.print(f"  {i}. {source['source']}")
        
        elif args.command == "chat":
            bot.chat()
        
        elif args.command == "list":
            bot.list_documents()
        
        elif args.command == "clear":
            confirm = console.input("Are you sure you want to clear all documents? (y/n): ")
            if confirm.lower() == 'y':
                bot.clear_database()
        
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
