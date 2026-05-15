"""
RAG Evaluation Framework
=========================
A standalone tool to evaluate your RAG pipeline's quality.

Measures three critical dimensions:
    1. Retrieval quality — Did we find the right documents?
    2. Answer relevance — Is the answer on-topic?
    3. Faithfulness — Is the answer grounded in the retrieved context?

Usage:
    python 01_final_rag_evaluator.py
    python 01_final_rag_evaluator.py --export results.json
"""

import os
import sys
import json
import argparse
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import List, Optional

from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import track

# Navigate to project root for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
load_dotenv(project_root.parent / ".env")

from openai import OpenAI

console = Console()
client = OpenAI()


# ─────────────────────────────────────────────────────────
# Test Case Definitions
# ─────────────────────────────────────────────────────────

@dataclass
class TestCase:
    """A single evaluation test case."""
    question: str
    expected_keywords: List[str]  # Keywords that SHOULD appear in retrieved context
    reference_answer: str         # Gold-standard answer for comparison
    category: str = "general"


@dataclass
class EvalResult:
    """Evaluation results for a single test case."""
    question: str
    category: str
    keyword_coverage: float = 0.0   # % of keywords found in retrieved context
    relevance_score: float = 0.0    # LLM-scored 1-5
    faithfulness_score: float = 0.0 # LLM-scored 1-5
    overall: float = 0.0
    notes: str = ""


# Sample test cases — students should customize these for their documents!
SAMPLE_TEST_CASES = [
    TestCase(
        question="What is retrieval augmented generation?",
        expected_keywords=["retrieval", "generation", "context", "documents", "knowledge"],
        reference_answer="RAG is a technique that combines document retrieval with language model generation, allowing the model to ground its answers in specific documents.",
        category="concept"
    ),
    TestCase(
        question="How does chunking affect RAG performance?",
        expected_keywords=["chunks", "splitting", "overlap", "size", "context window"],
        reference_answer="Chunking strategy affects RAG by determining the granularity of retrieval. Smaller chunks give more precise context but may miss broader information. Overlap between chunks helps maintain continuity.",
        category="technical"
    ),
    TestCase(
        question="What embedding models are commonly used?",
        expected_keywords=["embedding", "vector", "openai", "similarity", "dimension"],
        reference_answer="Common embedding models include OpenAI's text-embedding-ada-002, sentence-transformers, and Cohere embeddings. They convert text into dense vectors for similarity search.",
        category="technical"
    ),
    TestCase(
        question="How do you evaluate RAG system quality?",
        expected_keywords=["evaluation", "metrics", "relevance", "faithfulness", "retrieval"],
        reference_answer="RAG quality is evaluated through retrieval metrics (precision, recall, MRR), answer relevance, and faithfulness to source documents.",
        category="evaluation"
    ),
]


# ─────────────────────────────────────────────────────────
# 1 — Keyword Coverage (Retrieval Quality)
# ─────────────────────────────────────────────────────────

def evaluate_keyword_coverage(expected_keywords: List[str], retrieved_context: str) -> float:
    """
    Measure what percentage of expected keywords appear in retrieved context.
    
    This is a simple but effective retrieval quality proxy.
    Score: 0.0 to 1.0
    """
    if not expected_keywords or not retrieved_context:
        return 0.0
    
    context_lower = retrieved_context.lower()
    found = sum(1 for kw in expected_keywords if kw.lower() in context_lower)
    return round(found / len(expected_keywords), 2)


# ─────────────────────────────────────────────────────────
# 2 — Answer Relevance (LLM-scored)
# ─────────────────────────────────────────────────────────

def evaluate_relevance(question: str, answer: str) -> float:
    """
    Use an LLM judge to score answer relevance (1-5).
    
    Does the answer actually address the question?
    """
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an evaluation judge. Score the answer's RELEVANCE to the question "
                    "on a scale of 1-5. Only output a single number."
                    "\n1 = Completely irrelevant"
                    "\n2 = Tangentially related"
                    "\n3 = Partially relevant"
                    "\n4 = Mostly relevant"
                    "\n5 = Perfectly relevant and on-topic"
                )
            },
            {"role": "user", "content": f"Question: {question}\n\nAnswer: {answer}\n\nScore (1-5):"}
        ],
        max_tokens=5,
        temperature=0.0
    )
    
    try:
        return float(response.choices[0].message.content.strip())
    except ValueError:
        return 0.0


# ─────────────────────────────────────────────────────────
# 3 — Faithfulness (Is the answer grounded in context?)
# ─────────────────────────────────────────────────────────

def evaluate_faithfulness(answer: str, context: str) -> float:
    """
    Use an LLM judge to score faithfulness (1-5).
    
    Can every claim in the answer be traced back to the context?
    """
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a faithfulness evaluator. Score how well the answer is "
                    "GROUNDED in the provided context. Only output a single number."
                    "\n1 = Completely fabricated, not from context"
                    "\n2 = Mostly hallucinated with some context"
                    "\n3 = Partially grounded"
                    "\n4 = Mostly grounded, minor extrapolation"
                    "\n5 = Fully grounded in the context"
                )
            },
            {
                "role": "user",
                "content": f"Context:\n{context}\n\nAnswer:\n{answer}\n\nScore (1-5):"
            }
        ],
        max_tokens=5,
        temperature=0.0
    )
    
    try:
        return float(response.choices[0].message.content.strip())
    except ValueError:
        return 0.0


# ─────────────────────────────────────────────────────────
# Simulated RAG Pipeline (for demonstration)
# ─────────────────────────────────────────────────────────

def simulated_rag_pipeline(question: str) -> tuple[str, str]:
    """
    Simulate a RAG pipeline for evaluation purposes.
    
    In a real scenario, this would:
    1. Embed the question
    2. Search the vector database
    3. Retrieve top-k chunks
    4. Generate an answer with context
    
    For this demo, we use the LLM to generate both a simulated
    "retrieved context" and an answer.
    
    Returns: (retrieved_context, generated_answer)
    """
    # Simulate retrieval + generation
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are simulating a RAG system. Given a question, provide:\n"
                    "1. CONTEXT: A realistic retrieved document chunk (2-3 sentences)\n"
                    "2. ANSWER: An answer based on that context (2-3 sentences)\n\n"
                    "Format:\n<context>your context here</context>\n<answer>your answer here</answer>"
                )
            },
            {"role": "user", "content": question}
        ],
        max_tokens=300,
        temperature=0.3
    )
    
    raw = response.choices[0].message.content
    
    import re
    context_match = re.search(r'<context>(.*?)</context>', raw, re.DOTALL)
    answer_match = re.search(r'<answer>(.*?)</answer>', raw, re.DOTALL)
    
    context = context_match.group(1).strip() if context_match else raw[:150]
    answer = answer_match.group(1).strip() if answer_match else raw[150:]
    
    return context, answer


# ─────────────────────────────────────────────────────────
# Main Evaluation Loop
# ─────────────────────────────────────────────────────────

def run_evaluation(test_cases: List[TestCase]) -> List[EvalResult]:
    """Run the full evaluation pipeline."""
    results = []
    
    for tc in track(test_cases, description="Evaluating..."):
        # Step 1: Run the RAG pipeline
        context, answer = simulated_rag_pipeline(tc.question)
        
        # Step 2: Measure keyword coverage
        kw_coverage = evaluate_keyword_coverage(tc.expected_keywords, context)
        
        # Step 3: Score relevance
        relevance = evaluate_relevance(tc.question, answer)
        
        # Step 4: Score faithfulness
        faithfulness = evaluate_faithfulness(answer, context)
        
        # Calculate overall (weighted average)
        overall = round((kw_coverage * 5 * 0.3 + relevance * 0.35 + faithfulness * 0.35), 2)
        
        results.append(EvalResult(
            question=tc.question,
            category=tc.category,
            keyword_coverage=kw_coverage,
            relevance_score=relevance,
            faithfulness_score=faithfulness,
            overall=overall
        ))
    
    return results


def display_results(results: List[EvalResult]):
    """Display evaluation results in a color-coded table."""
    
    def colorize(score: float, max_val: float = 5.0) -> str:
        pct = score / max_val
        if pct >= 0.8:
            return f"[green]{score:.1f}[/green]"
        elif pct >= 0.6:
            return f"[yellow]{score:.1f}[/yellow]"
        else:
            return f"[red]{score:.1f}[/red]"
    
    table = Table(title="RAG Evaluation Results")
    table.add_column("Question (truncated)", style="cyan", width=35)
    table.add_column("Category", width=12)
    table.add_column("KW Coverage", justify="center", width=12)
    table.add_column("Relevance", justify="center", width=10)
    table.add_column("Faithful", justify="center", width=10)
    table.add_column("Overall", justify="center", width=10)
    
    for r in results:
        table.add_row(
            r.question[:35] + "..." if len(r.question) > 35 else r.question,
            r.category,
            colorize(r.keyword_coverage * 5, 5.0),
            colorize(r.relevance_score),
            colorize(r.faithfulness_score),
            colorize(r.overall),
        )
    
    # Averages
    n = len(results)
    avg_kw = sum(r.keyword_coverage for r in results) / n
    avg_rel = sum(r.relevance_score for r in results) / n
    avg_faith = sum(r.faithfulness_score for r in results) / n
    avg_overall = sum(r.overall for r in results) / n
    
    table.add_section()
    table.add_row(
        "[bold]AVERAGE[/bold]", "",
        colorize(avg_kw * 5, 5.0),
        colorize(avg_rel),
        colorize(avg_faith),
        f"[bold]{colorize(avg_overall)}[/bold]"
    )
    
    console.print("\n")
    console.print(table)
    
    # Category-level breakdown
    categories = set(r.category for r in results)
    if len(categories) > 1:
        console.print("\n[bold]Per-Category Averages:[/bold]")
        for cat in sorted(categories):
            cat_results = [r for r in results if r.category == cat]
            cat_avg = sum(r.overall for r in cat_results) / len(cat_results)
            console.print(f"  {cat}: {colorize(cat_avg)}")


# ─────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="RAG Evaluator")
    parser.add_argument("--export", help="Export results to JSON")
    args = parser.parse_args()
    
    console.print(Panel.fit(
        "[bold blue]📏 RAG Evaluation Framework[/bold blue]\n"
        "Measuring retrieval quality, relevance, and faithfulness",
        border_style="blue"
    ))
    
    try:
        console.print("\n[dim]Using sample test cases. Customize SAMPLE_TEST_CASES for your documents![/dim]\n")
        
        results = run_evaluation(SAMPLE_TEST_CASES)
        display_results(results)
        
        if args.export:
            export_data = [asdict(r) for r in results]
            Path(args.export).write_text(json.dumps(export_data, indent=2))
            console.print(f"\n[dim]Results exported to {args.export}[/dim]")
        
        console.print("\n[bold]How to improve your RAG pipeline:[/bold]")
        console.print("  1. Low keyword coverage → improve chunking strategy or embedding model")
        console.print("  2. Low relevance → improve prompt engineering for the generation step")
        console.print("  3. Low faithfulness → strengthen context grounding in the system prompt")
        console.print()
        
    except Exception as e:
        console.print(f"\n[bold red]Error:[/bold red] {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
