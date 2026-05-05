"""
Personality Chatbot
Core chatbot logic with personality loading and OpenAI API integration.
"""

import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

from conversation_manager import ConversationManager

# Load .env from module_02_prompt_engineering/.env
_HERE = Path(__file__).resolve().parent
load_dotenv(_HERE / "../../.env")

# Personalities directory is inside this lab folder
PERSONALITIES_DIR = _HERE / "personalities"

MODEL = "gpt-4o-mini"


def load_personality(personality_name: str) -> dict:
    """
    Load a personality configuration from a JSON file.

    Args:
        personality_name: Filename without extension (e.g. 'zen_master').

    Returns:
        Personality config dict with keys: name, description, system_prompt, greeting.
    """
    filepath = PERSONALITIES_DIR / f"{personality_name}.json"
    if not filepath.exists():
        raise FileNotFoundError(f"Personality file not found: {filepath}")
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def list_personalities() -> list[str]:
    """Return a list of available personality names (without .json extension)."""
    if not PERSONALITIES_DIR.exists():
        return []
    return [p.stem for p in PERSONALITIES_DIR.glob("*.json")]


class PersonalityChatbot:
    """A chatbot that adopts a specific personality loaded from a JSON config."""

    def __init__(self, personality_name: str):
        """
        Initialize the chatbot with a given personality.

        Args:
            personality_name: Name of the personality file (without .json).
        """
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.conversation = ConversationManager()
        self.load_personality(personality_name)

    def load_personality(self, name: str) -> None:
        """Load a personality by name and update the conversation system prompt."""
        self.personality = load_personality(name)
        self.conversation.set_system_prompt(self.personality["system_prompt"])

    @property
    def name(self) -> str:
        return self.personality["name"]

    @property
    def greeting(self) -> str:
        return self.personality["greeting"]

    def chat(self, user_message: str) -> str:
        """
        Send a message and get a response.

        Args:
            user_message: The user's input text.

        Returns:
            The assistant's response text.
        """
        self.conversation.add_message("user", user_message)

        response = self.client.chat.completions.create(
            model=MODEL,
            messages=self.conversation.get_messages(),
            max_tokens=500,
            temperature=self.personality.get("temperature", 0.8),
        )

        assistant_message = response.choices[0].message.content
        self.conversation.add_message("assistant", assistant_message)
        return assistant_message

    def switch_personality(self, name: str) -> None:
        """Switch to a different personality, keeping conversation history."""
        self.load_personality(name)
        print(f"  ✅ Personality switched to: {self.personality['name']}")

    def clear_history(self) -> None:
        """Clear the conversation history, keeping the current personality."""
        self.conversation.clear()
        print("  🗑️ Conversation history cleared")

    def reset(self) -> str:
        """Clear history and return the greeting."""
        self.conversation.clear()
        return self.greeting


def main():
    """Simple CLI demo of the personality chatbot."""
    personalities = list_personalities()
    if not personalities:
        print("No personalities found in:", PERSONALITIES_DIR)
        return

    if "--list" in sys.argv:
        print("Available personalities:")
        for i, p in enumerate(personalities, 1):
            print(f"  {i}. {p}")
        return

    print("Available personalities:")
    for i, p in enumerate(personalities, 1):
        print(f"  {i}. {p}")

    choice = input("\nChoose a personality (number or name): ").strip()
    if choice.isdigit():
        idx = int(choice) - 1
        personality_name = personalities[idx]
    else:
        personality_name = choice

    bot = PersonalityChatbot(personality_name)
    print(f"\n--- {bot.name} ---")
    print(bot.greeting)
    print("\n(Type 'quit' to exit, 'reset' to start over, 'clear' to clear history)\n")

    while True:
        user_input = input("You: ").strip()
        if not user_input:
            continue
        if user_input.lower() == "quit":
            break
        if user_input.lower() == "reset":
            print(bot.reset())
            continue
        if user_input.lower() == "clear":
            bot.clear_history()
            continue
        response = bot.chat(user_input)
        print(f"\n{bot.name}: {response}\n")


if __name__ == "__main__":
    main()
