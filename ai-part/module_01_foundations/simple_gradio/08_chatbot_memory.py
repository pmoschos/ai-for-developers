"""
Example 8: Chatbot with OpenAI + Memory
========================================
A chatbot that REMEMBERS the entire conversation.

Concepts:
    - Using Gradio's `history` to build the full messages list
    - How LLMs "remember": we send ALL previous messages every time
    - System prompts for personality
    - Token cost awareness (more history = more tokens = more cost)

Run:  python 08_chatbot_memory.py
Requires: OPENAI_API_KEY in your .env file
"""

import os
from pathlib import Path

import gradio as gr
from dotenv import load_dotenv
from openai import OpenAI

# Load API key from project root .env
load_dotenv(Path(__file__).resolve().parents[2] / ".env", override=True)

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY", "").strip().strip('"').strip("'")
)

SYSTEM_PROMPT = """You are a friendly and helpful assistant.
You remember everything the user has said in this conversation.
Be concise but warm. Use emoji occasionally."""


def chat_with_memory(message: str, history: list):
    """
    Send the FULL conversation history to OpenAI so it remembers context.

    How memory works:
        1. Start with the system prompt
        2. Add ALL previous messages from history
        3. Add the new user message
        4. Send everything to OpenAI
        5. The model "remembers" because it sees the full conversation

    ┌──────────────────────────────────────────────┐
    │  messages = [                                │
    │    {"role": "system",    "content": "..."},  │  ← personality
    │    {"role": "user",      "content": "Hi"},   │  ← turn 1
    │    {"role": "assistant", "content": "Hey!"}, │  ← turn 1
    │    {"role": "user",      "content": "..."},  │  ← turn 2
    │    {"role": "assistant", "content": "..."},  │  ← turn 2
    │    {"role": "user",      "content": "..."},  │  ← NEW message
    │  ]                                           │
    └──────────────────────────────────────────────┘
    """
    # Step 1: Start with system prompt
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    # Step 2: Add all previous messages from Gradio history
    # Gradio gives us history as [[user_msg, bot_msg], ...]
    for entry in history:
        if isinstance(entry, dict):
            # Gradio 6 format: {"role": "user/assistant", "content": "..."}
            messages.append(entry)
            print(f"entry: {entry}")
        elif isinstance(entry, (list, tuple)):
            # Legacy format: [user_msg, bot_msg]
            messages.append({"role": "user", "content": entry[0]}) # what user said before
            print(f"entry[0]: {entry[0]}")
            if entry[1]:
                messages.append({"role": "assistant", "content": entry[1]}) # what the bot said before
                print(f"entry[1]: {entry[1]}")
    # print(*history)
    # Step 3: Add the new user message
    messages.append({"role": "user", "content": message})
    print(f"Message: {messages}")

    # Step 4: Send to OpenAI with streaming
    try:
        stream = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            stream=True,
            max_tokens=500,
        )

        partial = ""
        for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                partial += delta
                yield partial

    except Exception as e:
        yield f"❌ **Error:** {e}"


demo = gr.ChatInterface(
    fn=chat_with_memory,
    title="🧠 OpenAI Chatbot with Memory",
    description=(
        "This chatbot **remembers** the conversation!\n\n"
        "Try it: tell it your name, then ask *'What is my name?'*\n\n"
        "💡 **How it works:** We send the full conversation history "
        "to OpenAI every time. More history = more tokens = more cost."
    ),
    examples=[
        "My name is Alice. Remember it!",
        "What are 3 fun facts about Python?",
        "Let's play a word game — I say a word, you say a related one.",
    ],
)

if __name__ == "__main__":
    demo.launch()
