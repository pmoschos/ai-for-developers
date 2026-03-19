"""
Example 6: Chatbot Interface
==============================
Build a chatbot UI — the #1 use case for Gradio in AI apps.

Concepts:
    - gr.ChatInterface (the easiest way to build a chatbot)
    - Conversation history management
    - Streaming responses with yield

Run:  python 06_chatbot.py

Note: This example uses a FAKE chatbot (no API key needed).
      It shows the Gradio pattern — swap in OpenAI later!
"""

import gradio as gr
import time


# ── Version 1: Simple chatbot (no streaming) ──

def echo_bot(message: str, history: list):
    """
    A simple echo bot.

    Parameters:
        message:  the user's latest message (str)
        history:  list of {"role": ..., "content": ...} dicts (Gradio 6 format)
    """
    return f"You said: **{message}**\n\n*I'm an echo bot — I repeat what you say!*"


# ── Version 2: Streaming chatbot (type-writer effect) ──

def streaming_bot(message: str, history: list):
    """
    A fake chatbot that streams its response word by word.
    Use `yield` instead of `return` to stream.
    """
    response = f"You asked: '{message}'. Here is my thoughtful response word by word."

    partial = ""
    for word in response.split():
        partial += word + " "
        time.sleep(0.1)  # simulate thinking
        yield partial.strip()


# ── Version 3: Chatbot with personality ──

def personality_bot(message: str, history: list):
    """
    A bot that changes behavior based on conversation length.
    Shows how `history` works.

    With type="messages", history is a list of dicts:
        [{"role": "user", "content": "hi"}, {"role": "assistant", "content": "hello!"}]
    """
    # Count only user messages to determine the turn number
    user_turns = sum(1 for msg in history if msg.get("role") == "user")
    turn = user_turns + 1

    if turn == 1:
        response = f"👋 Hello! This is our **first** exchange. You said: *{message}*"
    elif turn <= 3:
        response = f"Nice, turn **#{turn}**! I remember we've been chatting. You just said: *{message}*"
    else:
        response = f"Wow, turn **#{turn}** already! We're getting to know each other. 😊 You said: *{message}*"

    response += f"\n---\n*💡 History has **{len(history)}** messages so far.*"
    return response


# ── Choose which version to run ──
# Change this to try different bots:
#   echo_bot       → simple, no streaming
#   streaming_bot  → word-by-word streaming
#   personality_bot → uses conversation history

demo = gr.ChatInterface(
    # fn=personality_bot,
    # fn=echo_bot,
    fn=streaming_bot,
    title="💬 My First Chatbot",
    description="A simple chatbot built with `gr.ChatInterface` — no API key needed!",
    examples=[
        "Hello!",
        "What is Python?",
        "Tell me a joke",
    ],
)

if __name__ == "__main__":
    demo.launch()
