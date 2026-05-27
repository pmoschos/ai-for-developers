#!/usr/bin/env python
"""
JobRadar — CLI Entry Point
Usage: uv run python -m ai_research_crew.main
"""
import os
import sys
import warnings
from pathlib import Path
from datetime import datetime

# Suppress noisy third-party deprecation warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")

from dotenv import load_dotenv
load_dotenv(override=True)

# ── Banner ─────────────────────────────────────────────────────────────────────
BANNER = """
+------------------------------------------------------------------+
|  JobRadar  --  AI Job Market Intelligence & Career Gap Analyser  |
|         Scan the market. Find your gaps. Learn what matters.     |
+------------------------------------------------------------------+
"""

# ── Quick-start example CVs ───────────────────────────────────────────────────
EXAMPLE_JOB_TITLES = [
    "Python Backend Developer",
    "Frontend React Developer",
    "Data Analyst",
    "DevOps / Cloud Engineer",
]

EXAMPLE_CV = """Skills: Python, Flask, MySQL, basic Docker, HTML/CSS, Git.
Projects: Built a REST API for a university task management system (Python + Flask + MySQL).
          Created a simple personal portfolio website (HTML/CSS/JavaScript).
Experience: 6-month internship as a junior web developer (PHP/MySQL).
Education: BSc Computer Science (final year).
Languages: English (fluent), Greek (native).
"""

# Environment validation
REQUIRED_KEYS = ["OPENAI_API_KEY", "TAVILY_API_KEY"]
OPTIONAL_KEYS = {
    "NTFY_TOPIC":    "Push notifications (ntfy.sh — free, no signup for public topics)",
    "NTFY_TOKEN":    "Push notifications — only needed for private ntfy topics",
    "RESEND_API_KEY": "Email delivery (Resend — https://resend.com free tier)",
    "REPORT_FROM":   "Email sender address (must be verified in Resend)",
    "REPORT_TO":     "Email recipient address",
}


def validate_env() -> None:
    missing = [k for k in REQUIRED_KEYS if not os.getenv(k)]
    if missing:
        print(f"\nERROR: Missing required environment variable(s): {', '.join(missing)}")
        print("  Copy .env.example -> .env and fill in your keys.\n")
        sys.exit(1)

    missing_optional = [
        f"  * {k}  ({desc})"
        for k, desc in OPTIONAL_KEYS.items()
        if not os.getenv(k)
    ]
    if missing_optional:
        print("Optional keys not set (notifications will be skipped):")
        print("\n".join(missing_optional))
        print()


def setup_directories() -> None:
    for d in ["output", "memory"]:
        Path(d).mkdir(exist_ok=True)


def collect_inputs() -> dict:
    """Interactive prompt to collect job title, location, and CV."""
    print(BANNER)
    print("Quick-start job titles:")
    for i, title in enumerate(EXAMPLE_JOB_TITLES, 1):
        print(f"  [{i}] {title}")

    choice = input("\nChoose a job title [1-4] or press Enter to type your own: ").strip()
    if choice in ("1", "2", "3", "4"):
        job_title = EXAMPLE_JOB_TITLES[int(choice) - 1]
        print(f"\nSelected: {job_title}")
    else:
        job_title = input("Job title you are targeting: ").strip()
        if not job_title:
            print("ERROR: Job title is required.")
            sys.exit(1)

    location = input("\nLocation / Remote preference (e.g. 'Remote - Europe' or 'London'): ").strip()
    if not location:
        location = "Remote - Europe"
        print(f"Using default: {location}")

    print("\nPaste your CV / skills summary below.")
    print("Press Enter twice when done, or type 'example' to use the built-in example CV:")
    print("-" * 60)

    first_line = input()
    if first_line.strip().lower() == "example":
        my_cv = EXAMPLE_CV
        print("Using example CV.")
    else:
        lines = [first_line]
        while True:
            line = input()
            if line == "" and lines and lines[-1] == "":
                break
            lines.append(line)
        my_cv = "\n".join(lines).strip()

    if not my_cv:
        print("No CV provided - using the example CV.")
        my_cv = EXAMPLE_CV

    return {
        "job_title": job_title,
        "location":  location,
        "my_cv":     my_cv,
    }


def print_output_summary() -> None:
    output_dir = Path("output")
    files = sorted(output_dir.glob("*.json")) + sorted(output_dir.glob("*.md"))
    if not files:
        return
    print("\nOutput files:")
    for f in files:
        size = f.stat().st_size
        print(f"  {f.name:<45}  {size:>8,} bytes")


def run() -> None:
    validate_env()
    setup_directories()
    inputs = collect_inputs()

    divider = "-" * 66
    print(f"\n{divider}")
    print(f"Starting JobRadar analysis...")
    print(f"  Job title : {inputs['job_title']}")
    print(f"  Location  : {inputs['location']}")
    print(f"  Started   : {datetime.now():%Y-%m-%d  %H:%M:%S}")
    print(f"{divider}\n")

    from ai_research_crew.crew import JobRadar

    try:
        JobRadar().crew().kickoff(inputs=inputs)

        print(f"\n{'=' * 66}")
        print("JobRadar Analysis Complete!")
        print_output_summary()
        print(f"\nNotifications dispatched (if configured).")
        print(f"{'=' * 66}\n")

    except KeyboardInterrupt:
        print("\n\nAnalysis interrupted by user.")
        sys.exit(0)
    except Exception as exc:
        print(f"\nAnalysis failed: {type(exc).__name__}: {exc}")
        raise


if __name__ == "__main__":
    run()
