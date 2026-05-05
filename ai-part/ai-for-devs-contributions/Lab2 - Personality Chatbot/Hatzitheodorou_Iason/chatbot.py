"""
Personality Chatbot (Βήμα 2)
============================
Interactive chatbot με εναλλασσόμενες προσωπικότητες στο terminal.

Χρησιμοποιεί:
- ConversationManager (Βήμα 1) για το ιστορικό
- personality JSON αρχεία για system prompts
- OpenAI API για τις απαντήσεις

Εκτέλεση:
    python chatbot.py                           # Default personality
    python chatbot.py --personality zen_master   # Συγκεκριμένη
    python chatbot.py --list                    # Εμφάνιση διαθέσιμων

Εντολές μέσα στο chat:
    /switch <name>  — Αλλαγή personality
    /list           — Εμφάνιση personalities
    /clear          — Καθαρισμός ιστορικού
    /history        — Εμφάνιση ιστορικού
    /help           — Βοήθεια
    /quit           — Έξοδος
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Φόρτωση .env από τον γονικό φάκελο
try: 
    load_dotenv(Path(__file__).parent.parent.parent / ".env")
except Exception as e:
    print(f"❌ Failed to load .env file: {e}")

from openai import OpenAI
from conversation_manager import ConversationManager

client = OpenAI()

# Φάκελος με τα personality JSON αρχεία
PERSONALITIES_DIR = Path(__file__).parent / "personalities"


# ─────────────────────────────────────────────────────────────
# ΔΟΣΜΕΝΟ: Φόρτωση personality από αρχείο
# ─────────────────────────────────────────────────────────────
def load_personality(name: str) -> dict:
    """
    Loads personality configuration from a JSON file.
    Args:
        name: Filename without .json (e.g., "cynical_support")
    Returns:
        dict with: name, description, system_prompt, temperature, greeting
    """
    filepath = PERSONALITIES_DIR / f"{name}.json"

    if not filepath.exists():
        raise FileNotFoundError(f"Personality '{name}' not found at {filepath}")

    with open(filepath, encoding="utf-8") as f:
        return json.load(f)


def list_personalities() -> list[dict]:
    """
    Returns a list of all available personalities
    Args:
        None
    Returns:
        list of dicts with: name, description, filename (without .json)
    """
    personalities = []
    for filepath in PERSONALITIES_DIR.glob("*.json"):
        with open(filepath, encoding="utf-8") as f:
            data = json.load(f)
            data["filename"] = filepath.stem
            personalities.append(data)
    return personalities


def display_personalities():
    """Displays the available personalities"""
    personalities = list_personalities()

    print("\n╔══════════════════════════════════════════════╗")
    print("║          Available Personalities             ║")
    print("╠══════════════════════════════════════════════╣")
    for p in personalities:
        print(f"║  📌 {p['name']}")
        print(f"║     {p.get('description', '')}")
        print(f"║     File: {p['filename']}.json")
        print("║──────────────────────────────────────────────║")
    print("╚══════════════════════════════════════════════╝\n")


# ─────────────────────────────────────────────────────────────
# ΑΣΚΗΣΗ: Υλοποιήστε τις μεθόδους του PersonalityChatbot
# ─────────────────────────────────────────────────────────────
class PersonalityChatbot:
    """
    Chatbot με configurable personality.

    Αρχιτεκτονική:
    ─────────────
    PersonalityChatbot
      ├── self.personality (dict)     ← Από JSON αρχείο
      ├── self.conversation           ← ConversationManager instance
      └── chat() ───────────────────→ OpenAI API ──→ response
    """

    def __init__(self, personality_name: str = "cynical_support"):
        """
        Chatbot constructor.
        Args:
            personality_name: personality name (filename without .json)
        Returns:
            None
        """
        self.conversation = ConversationManager()
        self.load_personality(personality_name)

    def load_personality(self, name: str):
        """
        Loads personality.
        Args:
            name: personality name (filename without .json)
        Returns:
            None
        """
        personality = load_personality(name)
        self.personality = personality
        self.conversation.set_system_prompt(personality["system_prompt"])
        print(f"  [Loaded personality: {personality['name']}]")

    def chat(self, user_message: str) -> str:
        """
        Sends a message and receives a response.
        This is the MAIN method — this is where the OpenAI API call happens!
        Args:
            user_message: The user's message
        Returns:
            str: The AI's response
        """
        #Validate user_message
        if not isinstance(user_message, str) or not user_message.strip():
            raise ValueError("User message must be a non-empty string")

        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=self.conversation.get_messages(),
                max_tokens=500,
                temperature=self.personality.get("temperature", 0.8)
            )
        except Exception as e:
            raise RuntimeError(f"Error during API call: {e}")

        # Add user message and assistant response to conversation history after
        # successful API call
        self.conversation.add_message("user", user_message)

        assistant_message = response.choices[0].message.content
        self.conversation.add_message("assistant", assistant_message)
        return assistant_message


    def switch_personality(self, name: str):
        """
        Changes personality (keeps conversation history).
        Args:
            name: personality name (filename without .json)
        Returns:
            None  
        """
        self.load_personality(name)
        print(f"  ✅ Personality switched to: {self.personality['name']}")

    def clear_history(self):
        """
        Clears conversation history.
        Args:
            None
        Returns:
            None
        """
        self.conversation.clear()
        print("  🗑️ Conversation history cleared")

    def show_help(self):
        """
        Show help message with available commands.
        Args:    
            None
        Returns:
            None
        """
        print("""
╔════════════════════════════════════════════════════════════════════════════╗
║                   Help                                                     ║
╠════════════════════════════════════════════════════════════════════════════╣
║  /switch <name>  — Switch personality (use json filename without .json)    ║
║  /list           — Show personalities                                      ║
║  /clear          — Clear chat history                                      ║
║  /history        — Show chat history                                       ║
║  /help           — Show this help                                          ║
║  /quit           — Exit chatbot                                            ║
╚════════════════════════════════════════════════════════════════════════════╝
        """)

def run_chatbot(personality_name: str):
    """Main chatbot loop"""
    print()
    print("╔═══════════════════════════════════════════════╗")
    print("║              Personality Chatbot              ║")
    print("║     Chat with an AI that has personality!     ║")
    print("╚═══════════════════════════════════════════════╝")

    try:
        chatbot = PersonalityChatbot(personality_name)
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        print("Use --list to see available personalities")
        return 1

    # Display personality information
    print()
    print(f"  🎭 Current Personality: {chatbot.personality['name']}")
    print(f"  📝 {chatbot.personality.get('description', '')}")
    print(f"  💡 Type /help for commands")
    print()

    # Chat loop
    while True:
        try:
            user_input = input("You: ")

            if not user_input.strip():
                continue

            # Command handling
            if user_input.startswith("/"):
                command = user_input.lower().split()
                cmd = command[0]

                if cmd in ["/quit", "/exit", "/q"]:
                    print("\nGoodbye! 👋")
                    break
                elif cmd == "/help":
                    chatbot.show_help()
                elif cmd == "/list":
                    display_personalities()
                elif cmd == "/clear":
                    chatbot.clear_history()
                elif cmd == "/history":
                    messages = chatbot.conversation.get_messages()
                    print("\n── Chat History ──")
                    for msg in messages:
                        role = msg["role"].capitalize()
                        print(f"  {role}: {msg['content'][:100]}...")
                    print()
                elif cmd == "/switch":
                    if len(command) < 2:
                        print("❌ Usage: /switch <personality_name>")
                    else:
                        try:
                            chatbot.switch_personality(command[1])
                        except FileNotFoundError as e:
                            print(f"❌ {e}")
                else:
                    print(f"⚠️ Unknown command: {cmd}")
                continue

            # ── Regular chat message ──
            response = chatbot.chat(user_input)

            # Display response
            print(f"\n{chatbot.personality['name']}:")
            print(f"  {response}")
            print()

        except KeyboardInterrupt:
            print("\n\nGoodbye! 👋")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")

    return 0

def main():
    parser = argparse.ArgumentParser(
        description="Interactive chatbot with configurable personalities"
    )
    parser.add_argument(
        "--personality", "-p",
        default="cynical_support",
        help="Name of the personality to use"
    )
    parser.add_argument(
        "--list", "-l",
        action="store_true",
        help="List available personalities"
    )

    args = parser.parse_args()

    if args.list:
        display_personalities()
        return 0

    return run_chatbot(args.personality)

if __name__ == "__main__":
    exit(main())
