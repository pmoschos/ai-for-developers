#!/usr/bin/env python
import sys
import warnings

from datetime import datetime

from ai_researcher.crew import AiResearcher
from pathlib import Path

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# This main file is intended to be a way for you to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information

from dotenv import load_dotenv
load_dotenv(override=True)

def run():
    """
    Run the crew.
    """

    Path("output").mkdir(exist_ok=True)

    inputs = {
        "topic": "How can i learn Python in 1 week?"
    }

    result = AiResearcher().crew().kickoff(inputs=inputs)

    print("\n\n=== FINAL RESULT ===\n")
    print(result.raw)
    print("\n\nReport saved to output/report.md")


if __name__ == "__main__":
    run()