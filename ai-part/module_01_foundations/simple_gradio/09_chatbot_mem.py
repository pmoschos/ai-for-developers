"""
Example 9: Chatbot with OpenAI + Memory (Gradio 6)
===================================================
A chatbot that REMEMBERS the entire conversation.

Concepts:
    - Gradio 6 history format: list of {"role": ..., "content": ...} dicts
    - How LLMs "remember": we send ALL previous messages every time
    - System prompts for personality
    - Token cost awareness (more history = more tokens = more cost)

Run:  python 09_chatbot_mem.py
Requires: OPENAI_API_KEY in your .env file
"""

import os
from pathlib import Path

import gradio as gr
from dotenv import load_dotenv
from openai import OpenAI

# Load API key from project root .env
load_dotenv(Path(__file__).resolve().parents[2] / ".env", override=True)

API_KEY=os.getenv("OPENAI_API_KEY", "").strip().strip('"').strip("'")

client = OpenAI(
    api_key=API_KEY
)

SYSTEM_PROMPT = """You are a friendly and helpful assistant.
You remember everything the user has said in this conversation.
Be concise but warm. Use emoji occasionally."""


def chat_with_memory(message: str, history: list):
    """
    Send the FULL conversation history to OpenAI so it remembers context.

    In Gradio 6, history is already a list of dicts:
        [
            {"role": "user",      "content": "Hi"},
            {"role": "assistant", "content": "Hey!"},
            {"role": "user",      "content": "..."},
            {"role": "assistant", "content": "..."},
        ]

    So we just: system prompt + history + new message → OpenAI
    """
    # Build the messages list: system + history + new message
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        *history,
        {"role": "user", "content": message},
    ]

    # Send to OpenAI with streaming
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
