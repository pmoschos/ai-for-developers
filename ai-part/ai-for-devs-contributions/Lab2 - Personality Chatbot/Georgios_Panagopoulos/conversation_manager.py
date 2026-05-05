"""
Conversation Manager
Manages conversation history for the personality chatbot.
"""

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional


@dataclass
class Message:
    role: str
    content: str
    timestamp: datetime = field(default_factory=datetime.now)


class ConversationManager:
    """Manages conversation history for a chatbot session."""

    def __init__(self, system_prompt: str = "", max_history: int = 20):
        """
        Args:
            system_prompt: The system prompt defining the chatbot's personality.
            max_history: Maximum number of messages (user + assistant) to keep.
        """
        self.system_prompt = system_prompt
        self.max_history = max_history
        self.messages: list[Message] = []

    # ------------------------------------------------------------------
    # 1. set_system_prompt
    # ------------------------------------------------------------------

    def set_system_prompt(self, prompt: str) -> None:
        """Update the system prompt without touching the message history."""
        self.system_prompt = prompt

    # ------------------------------------------------------------------
    # 2. add_message
    # ------------------------------------------------------------------

    def add_message(self, role: str, content: str) -> None:
        """
        Append a message after validating the role.

        Raises:
            ValueError: if role is not 'user' or 'assistant'.
        """
        if role not in ("user", "assistant"):
            raise ValueError(
                f"Invalid role '{role}'. Must be 'user' or 'assistant'."
            )
        self.messages.append(Message(role=role, content=content))
        self._trim()

    # ------------------------------------------------------------------
    # 3. get_messages
    # ------------------------------------------------------------------

    def get_messages(self) -> list[dict]:
        """
        Return the full message list ready for an API call.

        Format: [{"role": "system", "content": ...}, {"role": "user", ...}, ...]
        The system dict is included only if system_prompt is non-empty.
        """
        result: list[dict] = []
        if self.system_prompt:
            result.append({"role": "system", "content": self.system_prompt})
        result.extend({"role": m.role, "content": m.content} for m in self.messages)
        return result

    # ------------------------------------------------------------------
    # 4. clear
    # ------------------------------------------------------------------

    def clear(self) -> None:
        """Clear the message history while keeping the system prompt."""
        self.messages = []

    # ------------------------------------------------------------------
    # 5. get_summary
    # ------------------------------------------------------------------

    def get_summary(self) -> dict:
        """Return a summary dict with counts of messages."""
        return {
            "message_count": len(self.messages),
            "has_system_prompt": bool(self.system_prompt),
            "user_messages": sum(1 for m in self.messages if m.role == "user"),
            "assistant_messages": sum(
                1 for m in self.messages if m.role == "assistant"
            ),
        }

    # ------------------------------------------------------------------
    # 6. export_conversation (bonus)
    # ------------------------------------------------------------------

    def export_conversation(self, filepath: Optional[str] = None) -> list[dict]:
        """
        Export the conversation as a list of dicts with timestamps.

        If filepath is given, writes the result to that JSON file.
        """
        exported = [
            {
                "role": m.role,
                "content": m.content,
                "timestamp": m.timestamp.isoformat(),
            }
            for m in self.messages
        ]
        if filepath:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(exported, f, indent=2, ensure_ascii=False)
        return exported

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _trim(self) -> None:
        """Trim messages to max_history."""
        if len(self.messages) > self.max_history:
            self.messages = self.messages[-self.max_history :]

    def get_system_prompt(self) -> str:
        """Return the current system prompt."""
        return self.system_prompt


# ======================================================================
# Tests
# ======================================================================

def _run_tests() -> None:
    import tempfile, os

    passed = 0
    failed = 0

    def ok(label: str) -> None:
        nonlocal passed
        passed += 1
        print(f"  PASS  {label}")

    def fail(label: str, reason: str) -> None:
        nonlocal failed
        failed += 1
        print(f"  FAIL  {label}: {reason}")

    print("\nRunning ConversationManager tests...\n")

    # Test 1 — set_system_prompt
    try:
        cm = ConversationManager()
        cm.set_system_prompt("You are a pirate.")
        assert cm.system_prompt == "You are a pirate."
        ok("1. set_system_prompt updates system_prompt")
    except Exception as e:
        fail("1. set_system_prompt updates system_prompt", str(e))

    # Test 2 — add_message with valid roles
    try:
        cm = ConversationManager()
        cm.add_message("user", "Hello")
        cm.add_message("assistant", "Arrr, ahoy!")
        assert len(cm.messages) == 2
        assert cm.messages[0].role == "user"
        assert cm.messages[1].role == "assistant"
        ok("2. add_message stores valid roles")
    except Exception as e:
        fail("2. add_message stores valid roles", str(e))

    # Test 3 — add_message raises ValueError for invalid role
    try:
        cm = ConversationManager()
        raised = False
        try:
            cm.add_message("system", "Oops")
        except ValueError:
            raised = True
        assert raised, "ValueError not raised"
        ok("3. add_message raises ValueError for invalid role")
    except Exception as e:
        fail("3. add_message raises ValueError for invalid role", str(e))

    # Test 4 — get_messages includes system prompt first
    try:
        cm = ConversationManager(system_prompt="Be helpful.")
        cm.add_message("user", "Hi")
        msgs = cm.get_messages()
        assert msgs[0] == {"role": "system", "content": "Be helpful."}
        assert msgs[1] == {"role": "user", "content": "Hi"}
        ok("4. get_messages includes system prompt first")
    except Exception as e:
        fail("4. get_messages includes system prompt first", str(e))

    # Test 5 — get_messages without system prompt skips system dict
    try:
        cm = ConversationManager()
        cm.add_message("user", "Hello")
        msgs = cm.get_messages()
        assert len(msgs) == 1
        assert msgs[0]["role"] == "user"
        ok("5. get_messages without system prompt has no system dict")
    except Exception as e:
        fail("5. get_messages without system prompt has no system dict", str(e))

    # Test 6 — clear keeps system_prompt
    try:
        cm = ConversationManager(system_prompt="Stay calm.")
        cm.add_message("user", "Hi")
        cm.add_message("assistant", "Hello")
        cm.clear()
        assert cm.messages == []
        assert cm.system_prompt == "Stay calm."
        ok("6. clear resets messages but keeps system_prompt")
    except Exception as e:
        fail("6. clear resets messages but keeps system_prompt", str(e))

    # Test 7 — get_summary counts correctly
    try:
        cm = ConversationManager(system_prompt="Be wise.")
        cm.add_message("user", "Q1")
        cm.add_message("assistant", "A1")
        cm.add_message("user", "Q2")
        summary = cm.get_summary()
        assert summary["message_count"] == 3
        assert summary["has_system_prompt"] is True
        assert summary["user_messages"] == 2
        assert summary["assistant_messages"] == 1
        ok("7. get_summary returns correct counts")
    except Exception as e:
        fail("7. get_summary returns correct counts", str(e))

    # Bonus — export_conversation with file write
    try:
        cm = ConversationManager()
        cm.add_message("user", "Export me")
        cm.add_message("assistant", "Exported!")
        with tempfile.NamedTemporaryFile(
            suffix=".json", delete=False, mode="w"
        ) as tmp:
            tmp_path = tmp.name
        exported = cm.export_conversation(filepath=tmp_path)
        assert len(exported) == 2
        assert "timestamp" in exported[0]
        with open(tmp_path, encoding="utf-8") as f:
            from_file = json.load(f)
        assert from_file == exported
        os.unlink(tmp_path)
        ok("BONUS. export_conversation returns list and writes JSON file")
    except Exception as e:
        fail("BONUS. export_conversation", str(e))

    print(f"\nResults: {passed} passed, {failed} failed\n")
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    _run_tests()
