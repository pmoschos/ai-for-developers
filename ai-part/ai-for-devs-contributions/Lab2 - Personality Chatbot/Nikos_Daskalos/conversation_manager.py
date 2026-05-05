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
import json


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
        Αρχικοποίηση.

        Args:
            max_history: Μέγιστος αριθμός μηνυμάτων στο ιστορικό
                        (αποφεύγουμε να ξεπεράσουμε το context window)
        """
        self.max_history = max_history
        self.system_prompt: Optional[str] = None
        self.messages: List[Message] = []



    def set_system_prompt(self, prompt: str):
        """
        Ορίζει το system prompt (personality).

        Args:
            prompt: Το system prompt string
        """
        if prompt:
            self.system_prompt = prompt

    def add_message(self, role: str, content: str):
        """
        Προσθέτει μήνυμα στο ιστορικό.

        Args:
            role: "user" ή "assistant" (ΜΟΝΟ αυτές οι τιμές!)
            content: Το κείμενο του μηνύματος
        """
        if not (role == "user" or role == "assistant"):
            raise ValueError(f"Invalid role: {role}")
        
        self.messages.append(Message(role, content))

        if len(self.messages) > self.max_history:
            self.messages = self.messages[-self.max_history:]
            

    def get_messages(self) -> List[Dict[str, str]]:
        """
        Επιστρέφει το ιστορικό σε format κατάλληλο για το OpenAI API.

        Returns:
            List of dicts: [{"role": "system", "content": "..."}, ...]
        """
        result = []

        if self.system_prompt:
            result.append({"role": "system", "content": self.system_prompt})
        
        result.extend({"role": msg.role, "content": msg.content} for msg in self.messages) 

        return result
    

    def clear(self):
        """
        Καθαρίζει το ιστορικό (ΚΡΑΤΑΕΙ το system prompt).
        """
        self.messages.clear()

    def get_summary(self) -> Dict:
        """
        Επιστρέφει στατιστικά της συνομιλίας.

        Returns:
            Dict με: message_count, has_system_prompt,
                    user_messages, assistant_messages
         """
        return {
            "message_count": len(self.messages),
            "has_system_prompt": any(msg.role == "system" for msg in self.messages),
            "user_messages": sum(1 for msg in self.messages if msg.role == "user"),
            "assistant_messages": sum(1 for msg in self.messages if msg.role == "assistant")
        }

    # ─────────────────────────────────────────────────────────
    # BONUS ΑΣΚΗΣΗ: Export Conversation
    # ─────────────────────────────────────────────────────────
    def export_conversation(self, filepath: str = None) -> List[Dict]:
        """
        Εξάγει τη συνομιλία σε μορφή λίστας dicts (κατάλληλη για JSON).
        Αν δοθεί filepath, αποθηκεύει σε αρχείο.

        Returns:
            List of dicts: [{"role": "user", "content": "...", "timestamp": "..."}, ...]
        """
        conversation = [{"role": msg.role, "content": msg.content, "timestamp": msg.timestamp.isoformat()} for msg in self.messages]

        if filepath:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(conversation,f, ensure_ascii=False, indent=2)
                print(f"💾 Conversation exported to {filepath}")

        return conversation


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
