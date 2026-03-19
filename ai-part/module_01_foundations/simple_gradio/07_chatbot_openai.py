"""
Example 7: Chatbot with OpenAI
===============================
Connect Gradio to a real LLM — OpenAI's GPT model.

Concepts:
    - Loading API keys from .env
    - OpenAI chat completions inside Gradio
    - Streaming responses with yield
    - Error handling for API calls

Run:  python 07_chatbot_openai.py
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


def chat(message: str, history: list):
    """
    Send the user's message to OpenAI and stream the response.

    Note: This is a SINGLE-TURN chatbot — it does NOT remember
    previous messages. Each message is independent.
    See 08_chatbot_memory.py for the memory version!
    """
    try:
        stream = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant. Be concise."},
                {"role": "user", "content": message},
            ],
            stream=True,
            max_tokens=500,
        )

        # Yield partial responses for a streaming effect
        partial = ""
        for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                partial += delta
                yield partial

    except Exception as e:
        yield f"❌ **Error:** {e}\n\nMake sure your `OPENAI_API_KEY` is set in `.env`"


demo = gr.ChatInterface(
    fn=chat,
    # chatbot=gr.Chatbot(height=800),
    title="🤖 OpenAI Chatbot",
    description=(
        "Chat with GPT-4o-mini — responses stream in real-time!\n\n"
        "⚠️ **No memory** — each message is independent. "
        "See `08_chatbot_memory.py` for conversation memory."
    ),
    examples=[
        "What is Python in one sentence?",
        "Write a haiku about programming",
        "Explain APIs like I'm 10 years old",
    ],
)

if __name__ == "__main__":
    demo.launch()
