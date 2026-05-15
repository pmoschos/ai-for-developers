"""
Query Enhancement for RAG
===========================
Improve retrieval quality by transforming user queries BEFORE searching.

Techniques covered:
    1. Query expansion — generate alternative phrasings
    2. Keyword extraction — find key terms for hybrid search
    3. HyDE — Hypothetical Document Embedding
    4. Comparison mode — see how each strategy affects retrieval

Usage:
    python query_enhancer.py
    python query_enhancer.py --query "How do I use vector databases?"
"""

import os
import sys
import argparse
from pathlib import Path
from typing import List

from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

# Navigate to project root for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
load_dotenv(project_root.parent.parent / ".env")

from openai import OpenAI

console = Console()
client = OpenAI()


class QueryEnhancer:
    """
    Enhance user queries using multiple strategies to improve retrieval.
    
    In a real RAG pipeline, you'd run these enhanced queries against
    your vector store and combine/rerank the results.
    """
    
    def __init__(self, model: str = "gpt-4o-mini"):
        self.model = model
    
    # ─── Strategy 1: Query Expansion ──────────────────────
    
    def expand_query(self, query: str, num_variants: int = 3) -> List[str]:
        """
        Generate alternative phrasings of the same question.
        
        Why: Different phrasings may match different document chunks.
        A user asking 'How does X work?' and 'Explain X' should get the same results.
        """
        response = client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Generate alternative phrasings of the user's question. "
                        "Each variant should preserve the original intent but use different words. "
                        "Output one variant per line, no numbering or bullets."
                    )
                },
                {
                    "role": "user",
                    "content": f"Generate {num_variants} alternative phrasings of:\n{query}"
                }
            ],
            max_tokens=200,
            temperature=0.7
        )
        
        raw = response.choices[0].message.content
        variants = [line.strip() for line in raw.strip().split("\n") if line.strip()]
        return variants[:num_variants]
    
    # ─── Strategy 2: Keyword Extraction ───────────────────
    
    def extract_keywords(self, query: str) -> List[str]:
        """
        Extract the most important search keywords from the query.
        
        Why: Keyword-based search (BM25) can complement vector search.
        This gives you the best of both worlds (hybrid search).
        """
        response = client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Extract the 3-5 most important search keywords from the query. "
                        "Include technical terms, specific concepts, and core nouns. "
                        "Output keywords separated by commas, nothing else."
                    )
                },
                {"role": "user", "content": query}
            ],
            max_tokens=50,
            temperature=0.0
        )
        
        raw = response.choices[0].message.content
        keywords = [kw.strip() for kw in raw.split(",") if kw.strip()]
        return keywords
    
    # ─── Strategy 3: HyDE (Hypothetical Document) ────────
    
    def generate_hyde(self, query: str) -> str:
        """
        Generate a hypothetical document that would answer the query.
        
        Why: Search using the hypothetical doc's embedding instead of the query's.
        This often retrieves more relevant chunks because the hypothesis is
        closer in embedding space to actual documents than a question is.
        
        Paper: https://arxiv.org/abs/2212.10496
        """
        response = client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Write a short paragraph (3-4 sentences) that would be a perfect "
                        "document chunk for answering the given question. Write it as if it's "
                        "from a textbook or documentation — factual, informative, and direct. "
                        "Do not start with 'This document' or similar meta-references."
                    )
                },
                {"role": "user", "content": query}
            ],
            max_tokens=150,
            temperature=0.3
        )
        
        return response.choices[0].message.content.strip()
    
    # ─── Full Enhancement Pipeline ────────────────────────
    
    def enhance(self, query: str) -> dict:
        """
        Run all enhancement strategies on a query.
        
        Returns a dict with all enhanced query variants.
        """
        return {
            "original": query,
            "expanded": self.expand_query(query),
            "keywords": self.extract_keywords(query),
            "hyde": self.generate_hyde(query),
        }


# ─────────────────────────────────────────────────────────
# Demo & Visualization
# ─────────────────────────────────────────────────────────

def demo_query_enhancement(query: str):
    """Show all enhancement strategies for a single query."""
    enhancer = QueryEnhancer()
    
    console.print(Panel(
        f"[bold]Original Query:[/bold] {query}",
        border_style="green"
    ))
    
    result = enhancer.enhance(query)
    
    # Display expanded queries
    console.print("\n[bold cyan]Strategy 1: Query Expansion[/bold cyan]")
    console.print("[dim]Generate alternative phrasings to match more chunks[/dim]")
    for i, v in enumerate(result["expanded"], 1):
        console.print(f"  {i}. {v}")
    
    # Display keywords
    console.print("\n[bold cyan]Strategy 2: Keyword Extraction[/bold cyan]")
    console.print("[dim]Key terms for hybrid search (BM25 + vector)[/dim]")
    console.print(f"  Keywords: [yellow]{', '.join(result['keywords'])}[/yellow]")
    
    # Display HyDE
    console.print("\n[bold cyan]Strategy 3: HyDE (Hypothetical Document)[/bold cyan]")
    console.print("[dim]A hypothetical document that would answer the question[/dim]")
    console.print(Panel(result["hyde"], border_style="dim"))
    
    return result


def compare_strategies():
    """Compare enhancement results across multiple queries."""
    queries = [
        "What are the benefits of using RAG?",
        "How do I handle large documents that don't fit in context?",
        "What's the difference between dense and sparse retrieval?",
    ]
    
    enhancer = QueryEnhancer()
    
    table = Table(title="Query Enhancement Comparison")
    table.add_column("Original Query", style="cyan", width=35)
    table.add_column("# Expansions", justify="center", width=12)
    table.add_column("Keywords", width=30)
    table.add_column("HyDE Length", justify="center", width=12)
    
    for q in queries:
        console.print(f"[dim]Enhancing: {q[:40]}...[/dim]")
        result = enhancer.enhance(q)
        table.add_row(
            q[:35] + "..." if len(q) > 35 else q,
            str(len(result["expanded"])),
            ", ".join(result["keywords"][:3]),
            f"{len(result['hyde'].split())} words"
        )
    
    console.print("\n")
    console.print(table)


# ─────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Query Enhancement for RAG")
    parser.add_argument("--query", "-q", type=str, help="Query to enhance")
    args = parser.parse_args()
    
    console.print(Panel.fit(
        "[bold blue]🔍 Query Enhancement for RAG[/bold blue]\n"
        "Transform queries to improve retrieval quality",
        border_style="blue"
    ))
    
    try:
        if args.query:
            demo_query_enhancement(args.query)
        else:
            # Demo with a sample query
            demo_query_enhancement("How do vector databases store and search embeddings?")
            
            console.print("\n" + "=" * 50)
            console.print("\n[bold]Multi-Query Comparison:[/bold]\n")
            compare_strategies()
        
        console.print("\n[bold]When to use each strategy:[/bold]")
        console.print("  • [cyan]Query Expansion[/cyan] → when users ask questions in varied ways")
        console.print("  • [cyan]Keyword Extraction[/cyan] → for hybrid search (BM25 + vector)")
        console.print("  • [cyan]HyDE[/cyan] → when questions are very different from document style")
        console.print()
        
    except Exception as e:
        console.print(f"\n[bold red]Error:[/bold red] {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
