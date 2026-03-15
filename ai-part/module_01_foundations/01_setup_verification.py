"""
Module 1 · Lesson 01: Setup Verification
=========================================
Run this FIRST before any other script or notebook!

This script checks that your development environment is correctly
configured with all necessary API keys, packages, and connectivity.

What it verifies:
    1. Python version (≥ 3.10)
    2. .env file with API keys
    3. OpenAI API connectivity
    4. Anthropic API connectivity (optional)
    5. Required packages installed
    6. Disk space availability
    7. Network connectivity to API endpoints

Usage:
    python 01_setup_verification.py
    python 01_setup_verification.py --export results.json
"""

import os
import sys
import json
import shutil
import argparse
from pathlib import Path
from datetime import datetime

from dotenv import load_dotenv

env_path = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(env_path, override=True)

api_key = os.getenv("OPENAI_API_KEY", "").strip().strip('"').strip("'")

# ──────────────────────────────────────────────────────────────
#  Configuration
# ──────────────────────────────────────────────────────────────

# Load .env from project root
ENV_PATH = Path(__file__).parent.parent / ".env"
# load_dotenv(ENV_PATH)

REQUIRED_PACKAGES = [
    "openai", "tiktoken", "python-dotenv", "gradio",
]

OPTIONAL_PACKAGES = [
    "anthropic", "chromadb", "fastapi", "uvicorn",
]

# ──────────────────────────────────────────────────────────────
#  Helper
# ──────────────────────────────────────────────────────────────

results = []  # Collect all check outcomes


def record(name: str, status: str, detail: str = ""):
    """Record a check result: PASS / WARN / FAIL."""
    icon = {"PASS": "✅", "WARN": "⚠️", "FAIL": "❌"}[status]
    results.append({"check": name, "status": status, "detail": detail})
    print(f"  {icon}  {name}: {detail}" if detail else f"  {icon}  {name}")


# ──────────────────────────────────────────────────────────────
#  Checks
# ──────────────────────────────────────────────────────────────

def check_python_version():
    """Python ≥ 3.10 is required for modern type hints."""
    v = sys.version_info
    version_str = f"{v.major}.{v.minor}.{v.micro}"
    if (v.major, v.minor) >= (3, 10):
        record("Python version", "PASS", version_str)
    else:
        record("Python version", "FAIL", f"{version_str} — need ≥ 3.10")


def check_env_file():
    """Verify .env file exists."""
    if ENV_PATH.exists():
        record(".env file", "PASS", str(ENV_PATH))
    else:
        record(".env file", "FAIL", f"Not found at {ENV_PATH}")


def check_api_key(key_name: str):
    """Check if an API key is set and not a placeholder."""
    value = os.getenv(key_name, "")
    if not value:
        record(key_name, "WARN", "Not set (some features may be unavailable)")
    elif value.startswith("sk-") or value.startswith("your"):
        if "your" in value.lower():
            record(key_name, "FAIL", "Still a placeholder — replace with real key")
        else:
            record(key_name, "PASS", f"{value[:8]}...{value[-4:]}")
    else:
        record(key_name, "PASS", f"{value[:8]}...")


def test_openai_connection():
    """Test actual OpenAI API connectivity."""
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Say 'hello'"}],
            max_tokens=5,
        )
        answer = response.choices[0].message.content.strip()
        record("OpenAI API call", "PASS", f"Response: '{answer}'")
    except Exception as e:
        record("OpenAI API call", "FAIL", str(e)[:120])


def test_anthropic_connection():
    """Test Anthropic API connectivity (optional)."""
    if not os.getenv("ANTHROPIC_API_KEY"):
        record("Anthropic API call", "WARN", "ANTHROPIC_API_KEY not set — skipping")
        return
    try:
        import anthropic
        client = anthropic.Anthropic()
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=10,
            messages=[{"role": "user", "content": "Say 'hello'"}],
        )
        answer = response.content[0].text.strip()
        record("Anthropic API call", "PASS", f"Response: '{answer}'")
    except ImportError:
        record("Anthropic API call", "WARN", "anthropic package not installed")
    except Exception as e:
        record("Anthropic API call", "FAIL", str(e)[:120])


def check_packages():
    """Check that required and optional packages are installed."""
    import importlib.metadata as meta

    for pkg in REQUIRED_PACKAGES:
        try:
            version = meta.version(pkg)
            record(f"Package: {pkg}", "PASS", f"v{version}")
        except meta.PackageNotFoundError:
            record(f"Package: {pkg}", "FAIL", "Not installed — pip install " + pkg)

    for pkg in OPTIONAL_PACKAGES:
        try:
            version = meta.version(pkg)
            record(f"Package: {pkg}", "PASS", f"v{version}")
        except meta.PackageNotFoundError:
            record(f"Package: {pkg}", "WARN", "Not installed (optional)")


def check_disk_space():
    """At least 500 MB free is recommended."""
    usage = shutil.disk_usage(Path(__file__).parent)
    free_gb = usage.free / (1024 ** 3)
    if free_gb >= 0.5:
        record("Disk space", "PASS", f"{free_gb:.1f} GB free")
    else:
        record("Disk space", "WARN", f"Only {free_gb:.2f} GB free — may be tight")




# ──────────────────────────────────────────────────────────────
#  Main
# ──────────────────────────────────────────────────────────────

def main(export_path: str = None):
    print()
    print("=" * 60)
    print("  🔧  AI for Developers — Environment Verification")
    print("=" * 60)
    print()

    # --- Section 1: Basics ---
    print("── 1. System Basics ──")
    check_python_version()
    check_env_file()
    check_disk_space()
    print()

    # --- Section 2: API Keys ---
    print("── 2. API Keys ──")
    check_api_key("OPENAI_API_KEY")
    check_api_key("ANTHROPIC_API_KEY")
    print()

    # --- Section 3: Packages ---
    print("── 3. Installed Packages ──")
    check_packages()
    print()

    # --- Section 4: Connectivity ---
    print("── 4. API Connectivity ──")
    test_openai_connection()
    test_anthropic_connection()
    print()

    # --- Summary ---
    passes = sum(1 for r in results if r["status"] == "PASS")
    warns  = sum(1 for r in results if r["status"] == "WARN")
    fails  = sum(1 for r in results if r["status"] == "FAIL")
    total  = len(results)

    print("=" * 60)
    print(f"  Results:  ✅ {passes} passed  ⚠️ {warns} warnings  ❌ {fails} failed")
    print(f"  Total checks: {total}")
    print("=" * 60)

    if fails == 0:
        print("\n  🎉 Your environment is ready! You can proceed to the course.\n")
    else:
        print("\n  ⚠️  Please fix the failed checks above before proceeding.\n")

    # --- Optional JSON export ---
    if export_path:
        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {"pass": passes, "warn": warns, "fail": fails},
            "checks": results,
        }
        Path(export_path).write_text(json.dumps(report, indent=2))
        print(f"  📄 Results exported to {export_path}\n")

    return 1 if fails > 0 else 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AI for Developers — Setup Verification")
    parser.add_argument("--export", help="Export results to JSON file")
    args = parser.parse_args()
    exit(main(export_path=args.export))
"""
End of Module 1, Lesson 01.

Key Takeaways:
  • Always verify your environment before starting a new project.
  • API keys should never be hardcoded — use .env files.
  • Check both required and optional dependencies.
"""
