"""
Conversation Manager (Βήμα 1)
=============================
Διαχειρίζεται το ιστορικό μηνυμάτων μιας συνομιλίας.

Αυτό το module δεν χρειάζεται OpenAI API — μπορείτε να το τεστάρετε μόνο του!

Δοκιμή:
    python conversation_manager.py
"""

from typing import List, Dict, Optional
from dataclasses import dataclass, field
from datetime import datetime


# ─────────────────────────────────────────────────────────────
# ΔΟΣΜΕΝΟ: Η κλάση Message (dataclass)
# ─────────────────────────────────────────────────────────────
@dataclass
class Message:
    """
    Αναπαριστά ένα μήνυμα στη συνομιλία.

    Attributes:
        role: Ο ρόλος του αποστολέα — "user" ή "assistant"
        content: Το περιεχόμενο του μηνύματος
        timestamp: Πότε στάλθηκε (αυτόματη τιμή)
    """
    role: str
    content: str
    timestamp: datetime = field(default_factory=datetime.now)


# ─────────────────────────────────────────────────────────────
# ΑΣΚΗΣΗ: Υλοποιήστε τις μεθόδους της ConversationManager
# ─────────────────────────────────────────────────────────────
class ConversationManager:
    """
    Διαχειριστής ιστορικού συνομιλίας.

    Πώς λειτουργεί η μνήμη ενός chatbot:
    ──────────────────────────────────────
    Τα LLMs ΔΕΝ θυμούνται προηγούμενα μηνύματα αυτόματα.
    Σε κάθε API call, πρέπει να στείλουμε ΟΛΟΚΛΗΡΟ το ιστορικό:

    messages = [
        {"role": "system",    "content": "You are a pirate..."},   ← personality
        {"role": "user",      "content": "Hello!"},                ← 1ο μήνυμα
        {"role": "assistant", "content": "Ahoy!"},                 ← 1η απάντηση
        {"role": "user",      "content": "Tell me about Python"},  ← 2ο μήνυμα
    ]

    Αυτή η κλάση φροντίζει να κρατάει αυτό το ιστορικό.
    """

    def __init__(self, max_history: int = 50):
        """
        Initialization.

        Args:
            max_history: Max number of messages to keep in history
            (be wary of model's context window)
        """
        self.max_history = max_history
        self.system_prompt: Optional[str] = None
        self.messages: List[Message] = []

    def set_system_prompt(self, prompt: str):
        """
        Sets the system prompt (personality).

        Args:
            prompt: The system prompt string

        
        """
        self.system_prompt = prompt

    def add_message(self, role: str, content: str):
        """
        Adds a message to the conversation history.

        Args:
            role: "user" or "assistant" (ONLY these values!)
            content: The message text
        """
        
        # If role is invalid, raise an error
        if role not in ("user", "assistant"):
            raise ValueError(f"Invalid role: {role} - must be 'user' or 'assistant'")
        
        # Create a new Message object and add it to the messages list
        new_message = Message(role=role, content=content)

        # Check the length of messages and trim if necessary
        self.messages.append(new_message)
        if len(self.messages) > self.max_history:
            self.messages = self.messages[-self.max_history:]

    def get_messages(self) -> List[Dict[str, str]]:
        """
        Returns the conversation history in the format expected by OpenAI API.
        List of dicts: [{"role": "system", "content": "..."}, {"role": "user", "content": "..."}, ...]

        Returns:
            List of dicts: [{"role": "system", "content": "..."}, ...]

        TODO:
        1. Ξεκινήστε με κενή λίστα result = []
        2. Αν υπάρχει self.system_prompt → προσθέστε:
           {"role": "system", "content": self.system_prompt}
        3. Για κάθε msg στο self.messages → προσθέστε:
           {"role": msg.role, "content": msg.content}
        4. Επιστρέψτε τη result
        """

        result = []
        if self.system_prompt:
            result.append({"role": "system", "content": self.system_prompt})
            for msg in self.messages:
                result.append({"role": msg.role, "content": msg.content})
        return result

    def clear(self):
        """
        Clears the conversation history but keeps the system prompt.

        TODO: Αδειάστε τη λίστα self.messages
        """
        self.messages = []

    def get_summary(self) -> Dict:
        """
        Returns conversation statistics: total message count, count of user 
        and assistant messages, and whether a system prompt is set.

        Returns:
            Dict: message_count, has_system_prompt,
                    user_messages, assistant_messages
        """
        summary = {
            "message_count": len(self.messages),
            "has_system_prompt": self.system_prompt is not None,
            "user_messages": sum(1 for m in self.messages if m.role == "user"),
            "assistant_messages": sum(1 for m in self.messages if m.role == "assistant"),
        }
        return summary

    # ─────────────────────────────────────────────────────────
    # BONUS ΑΣΚΗΣΗ: Export Conversation
    # ─────────────────────────────────────────────────────────
    def export_conversation(self, filepath: str = None) -> List[Dict]:
        """
        Exports the conversation history to a list of dicts. Optionally
        saves to a JSON file.

        Returns:
            List of dicts: [{"role": "user", "content": "...", "timestamp": "..."}, ...]

        TODO:
        1. Δημιουργήστε λίστα με list comprehension:
           Για κάθε msg στο self.messages, φτιάξτε dict:
           {
               "role": msg.role,
               "content": msg.content,
               "timestamp": msg.timestamp.isoformat()
           }

        2. Αν δόθηκε filepath (if filepath):
           - import json (στην αρχή του αρχείου ή μέσα στη μέθοδο)
           - Ανοίξτε το αρχείο: with open(filepath, "w", encoding="utf-8") as f:
           - Γράψτε: json.dump(data, f, ensure_ascii=False, indent=2)
           - print(f"💾 Conversation exported to {filepath}")

        3. Επιστρέψτε τη λίστα
        """
        for msg in self.messages:
            data = [
                {
                    "role": msg.role,
                    "content": msg.content,
                    "timestamp": msg.timestamp.isoformat()
                }
                for msg in self.messages
            ]
        if filepath:
            import json
            try:
                with open(filepath, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                    print(f"💾 Conversation exported to {filepath}")
            except Exception as e:
                print(f"❌ Failed to export conversation: {e}")
        return data



# ─────────────────────────────────────────────────────────────
# TESTS: Τρέξτε αυτό το αρχείο μόνο του για να ελέγξετε
# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 50)
    print("Testing ConversationManager")
    print("=" * 50)

    cm = ConversationManager()

    # Test 1: System prompt
    cm.set_system_prompt("You are a helpful pirate.")
    assert cm.system_prompt == "You are a helpful pirate.", "❌ set_system_prompt failed"
    print("✅ Test 1: set_system_prompt — OK")

    # Test 2: Add messages
    cm.add_message("user", "Hello!")
    cm.add_message("assistant", "Ahoy, matey!")
    assert len(cm.messages) == 2, "❌ add_message failed"
    print("✅ Test 2: add_message — OK")

    # Test 3: Invalid role
    try:
        cm.add_message("invalid_role", "test")
        print("❌ Test 3: Should have raised ValueError!")
    except ValueError:
        print("✅ Test 3: Invalid role raises ValueError — OK")

    # Test 4: get_messages format
    messages = cm.get_messages()
    assert messages[0]["role"] == "system", "❌ First message should be system"
    assert messages[1]["role"] == "user", "❌ Second message should be user"
    assert messages[2]["role"] == "assistant", "❌ Third message should be assistant"
    assert len(messages) == 3, f"❌ Expected 3 messages, got {len(messages)}"
    print("✅ Test 4: get_messages format — OK")

    # Test 5: Clear
    cm.clear()
    assert len(cm.messages) == 0, "❌ clear failed"
    assert cm.system_prompt is not None, "❌ clear should keep system prompt!"
    print("✅ Test 5: clear (keeps system prompt) — OK")

    # Test 6: Summary
    cm.add_message("user", "test 1")
    cm.add_message("assistant", "response 1")
    cm.add_message("user", "test 2")
    summary = cm.get_summary()
    assert summary["message_count"] == 3, "❌ Wrong message count"
    assert summary["user_messages"] == 2, "❌ Wrong user count"
    assert summary["assistant_messages"] == 1, "❌ Wrong assistant count"
    print("✅ Test 6: get_summary — OK")

    # Test 7: Export conversation (Bonus)
    exported = cm.export_conversation()
    if exported is not None:
        assert isinstance(exported, list), "❌ export should return a list"
        assert len(exported) == 3, f"❌ Expected 3 entries, got {len(exported)}"
        assert "role" in exported[0], "❌ Each entry needs 'role'"
        assert "content" in exported[0], "❌ Each entry needs 'content'"
        assert "timestamp" in exported[0], "❌ Each entry needs 'timestamp'"
        print("✅ Test 7: export_conversation — OK (Bonus!)")
    else:
        print("⏭️  Test 7: export_conversation — Skipped (not implemented yet)")

    print()
    print("🎉 Τα βασικά tests πέρασαν! Προχωρήστε στο Βήμα 2 (chatbot.py)")
