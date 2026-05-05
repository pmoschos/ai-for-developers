"""
Compare Personalities
Sends the same question to all available personalities and prints their responses side by side.
"""

from pathlib import Path

from dotenv import load_dotenv

from chatbot import PersonalityChatbot, list_personalities

# Load .env from module_02_prompt_engineering/.env
_HERE = Path(__file__).resolve().parent
load_dotenv(_HERE / "../../.env")

SEPARATOR = "=" * 70


def compare(question: str, personalities: list[str] | None = None) -> dict[str, str]:
    """
    Ask the same question to multiple personalities.

    Args:
        question: The question to ask all personalities.
        personalities: List of personality names. If None, uses all available.

    Returns:
        Dict mapping personality name -> response text.
    """
    if personalities is None:
        personalities = list_personalities()

    results = {}
    for personality_name in personalities:
        print(f"Querying: {personality_name}...")
        bot = PersonalityChatbot(personality_name)
        response = bot.chat(question)
        results[bot.name] = response

    return results


def print_comparison(question: str, results: dict[str, str]) -> None:
    """Pretty-print comparison results."""
    print(f"\n{SEPARATOR}")
    print(f"QUESTION: {question}")
    print(SEPARATOR)

    for personality_name, response in results.items():
        print(f"\n[{personality_name.upper()}]")
        print("-" * 50)
        print(response)

    print(f"\n{SEPARATOR}\n")


def main():
    """Run a comparison demo with a set of example questions."""
    example_questions = [
        "What is the meaning of life?",
        "How do I deal with stress at work?",
        "Can you explain how photosynthesis works?",
    ]

    available = list_personalities()
    if not available:
        print("No personalities found.")
        return

    print(f"Found personalities: {', '.join(available)}")
    print("\nRunning personality comparison...\n")

    for question in example_questions:
        results = compare(question, available)
        print_comparison(question, results)

    # Interactive mode
    print("Enter your own question (or 'quit' to exit):")
    while True:
        user_q = input("\nQuestion: ").strip()
        if not user_q or user_q.lower() == "quit":
            break
        results = compare(user_q, available)
        print_comparison(user_q, results)


if __name__ == "__main__":
    main()
