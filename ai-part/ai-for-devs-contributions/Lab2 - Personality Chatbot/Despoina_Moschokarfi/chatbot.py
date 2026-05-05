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
load_dotenv(Path(__file__).parent.parent.parent / ".env")

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
    Φόρτωση personality configuration από JSON αρχείο.

    Args:
        name: Όνομα αρχείου χωρίς .json (π.χ. "cynical_support")

    Returns:
        dict με: name, description, system_prompt, temperature, greeting
    """
    filepath = PERSONALITIES_DIR / f"{name}.json"

    if not filepath.exists():
        raise FileNotFoundError(f"Personality '{name}' not found at {filepath}")

    with open(filepath) as f:
        return json.load(f)


def list_personalities() -> list[dict]:
    """Επιστρέφει λίστα με όλα τα διαθέσιμα personalities"""
    personalities = []
    for filepath in PERSONALITIES_DIR.glob("*.json"):
        with open(filepath) as f:
            data = json.load(f)
            data["filename"] = filepath.stem
            personalities.append(data)
    return personalities


def display_personalities():
    """Εμφανίζει τα διαθέσιμα personalities"""
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
        Αρχικοποίηση chatbot.

        ΔΟΣΜΕΝΟ — Δεν χρειάζεται αλλαγή.
        """
        self.conversation = ConversationManager()
        self.load_personality(personality_name)

    def load_personality(self, name: str):
        """
        Φόρτωση personality.

        ΔΟΣΜΕΝΟ — Δεν χρειάζεται αλλαγή.
        """
        personality = load_personality(name)
        self.personality = personality
        self.conversation.set_system_prompt(personality["system_prompt"])
        print(f"  [Loaded personality: {personality['name']}]")

    def chat(self, user_message: str) -> str:
        """
        Στέλνει μήνυμα και λαμβάνει απάντηση.

        Αυτή είναι η ΚΥΡΙΑ μέθοδος — εδώ γίνεται η κλήση στο OpenAI API!

        Args:
            user_message: Το μήνυμα του χρήστη

        Returns:
            str: Η απάντηση του AI
        """

        # Add user message to conversation history
        self.conversation.add_message("user", user_message)

        # API call
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=self.conversation.get_messages(),
            max_tokens=500,
            temperature=self.personality.get("temperature", 0.8)
        )
        
        # Get result
        assistant_message = response.choices[0].message.content

        # Add assistant message to conversation history
        self.conversation.add_message("assistant", assistant_message)

        return assistant_message

    def switch_personality(self, name: str):
        """
        Αλλαγή personality (κρατάει το ιστορικό).
        """
        # Load personality
        self.load_personality(name)
        print(f"✅ Personality switched to: {self.personality['name']}")

    def clear_history(self):
        """
        Καθαρισμός ιστορικού.
        """
        self.conversation.clear()
        print("  🗑️ Conversation history cleared")

    def show_help(self):
        """
        Εμφάνιση βοήθειας.

        ΔΟΣΜΕΝΟ — Δεν χρειάζεται αλλαγή.
        """
        print("""
╔══════════════════════════════════════════════╗
║                   Help                       ║
╠══════════════════════════════════════════════╣
║  /switch <name>  — Switch personality        ║
║  /list           — Show personalities        ║
║  /clear          — Clear chat history        ║
║  /history        — Show chat history         ║
║  /help           — Show this help            ║
║  /quit           — Exit chatbot              ║
╚══════════════════════════════════════════════╝
        """)


# ─────────────────────────────────────────────────────────────
# ΔΟΣΜΕΝΟ: Κύριος βρόχος (main loop)
# Μελετήστε τον για να καταλάβετε πώς δουλεύει η εφαρμογή.
# ─────────────────────────────────────────────────────────────
def run_chatbot(personality_name: str):
    """Κύριος βρόχος chatbot"""
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

    # Εμφάνιση πληροφοριών personality
    print()
    print(f"  🎭 Current Personality: {chatbot.personality['name']}")
    print(f"  📝 {chatbot.personality.get('description', '')}")
    print(f"  💡 Type /help for commands")
    print()

    # Βρόχος συνομιλίας
    while True:
        try:
            user_input = input("You: ")

            if not user_input.strip():
                continue

            # Χειρισμός εντολών
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

            # ── Κανονικό μήνυμα chat ──
            response = chatbot.chat(user_input)

            # Εμφάνιση απάντησης
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
