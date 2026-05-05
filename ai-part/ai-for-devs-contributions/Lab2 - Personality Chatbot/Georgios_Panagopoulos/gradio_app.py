"""
Gradio App for Personality Chatbot
Provides a web UI to interact with different chatbot personalities.
"""

import json
import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI
import gradio as gr

# Load .env from module_02_prompt_engineering/.env
_HERE = Path(__file__).resolve().parent
load_dotenv(_HERE / "../../.env")

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ---------------------------------------------------------------------------
# Load all personalities from JSON files into a single dict
# ---------------------------------------------------------------------------

PERSONALITIES_DIR = _HERE / "personalities"

def _load_all_personalities() -> dict:
    result = {
        "Default Assistant": {
            "name": "Default Assistant",
            "system_prompt": "You are a helpful assistant.",
            "greeting": "Hello! How can I help you today?",
            "temperature": 0.8,
        }
    }
    for filepath in sorted(PERSONALITIES_DIR.glob("*.json")):
        with open(filepath, encoding="utf-8") as f:
            data = json.load(f)
        result[data["name"]] = data
    return result

PERSONALITIES = _load_all_personalities()
PERSONALITY_NAMES = list(PERSONALITIES.keys())

# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def get_greeting(personality: str) -> str:
    """Return the greeting message for the given personality."""
    persona = PERSONALITIES.get(personality, PERSONALITIES["Default Assistant"])
    return persona.get("greeting", "Hello! How can I help you?")

# ---------------------------------------------------------------------------
# Core logic
# ---------------------------------------------------------------------------

def chat(message: str, history: list, personality: str) -> str:
    """
    Build the message list and call the OpenAI API.

    Args:
        message:     The current user input.
        history:     List of {"role": ..., "content": ...} dicts.
        personality: Selected personality name.

    Returns:
        The assistant's response string.
    """
    persona = PERSONALITIES.get(personality, PERSONALITIES["Default Assistant"])

    messages = [{"role": "system", "content": persona["system_prompt"]}]
    for msg in history:
        messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": message})

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=persona.get("temperature", 0.8),
        max_tokens=500,
    )
    return response.choices[0].message.content


def respond(message: str, history: list, personality: str) -> tuple[str, list]:
    """Handle a user message: call chat(), append to history, return updated state."""
    if not message.strip():
        return "", history

    response = chat(message, history, personality)
    history.append({"role": "user", "content": message})
    history.append({"role": "assistant", "content": response})
    return "", history


def show_greeting(personality: str, history: list) -> list:
    """Show the personality greeting when history is empty (e.g. on load or switch)."""
    if not history:
        return [{"role": "assistant", "content": get_greeting(personality)}]
    return history

# ---------------------------------------------------------------------------
# Gradio UI
# ---------------------------------------------------------------------------

with gr.Blocks(title="Personality Chatbot") as demo:
    gr.Markdown("# Personality Chatbot\nChoose a personality and start chatting!")

    personality_dropdown = gr.Dropdown(
        choices=PERSONALITY_NAMES,
        value=PERSONALITY_NAMES[0],
        label="Select Personality",
    )

    chatbot_ui = gr.Chatbot(
        label="Conversation",
        height=450,
        type="messages",
    )

    with gr.Row():
        msg = gr.Textbox(
            placeholder="Type your message here...",
            label="Your message",
            scale=4,
        )
        send_btn = gr.Button("Send", variant="primary", scale=1)

    clear_btn = gr.Button("Clear History")

    # Event bindings
    msg.submit(
        fn=respond,
        inputs=[msg, chatbot_ui, personality_dropdown],
        outputs=[msg, chatbot_ui],
    )
    send_btn.click(
        fn=respond,
        inputs=[msg, chatbot_ui, personality_dropdown],
        outputs=[msg, chatbot_ui],
    )
    clear_btn.click(
        fn=lambda: [],
        outputs=[chatbot_ui],
    )
    personality_dropdown.change(
        fn=show_greeting,
        inputs=[personality_dropdown, chatbot_ui],
        outputs=[chatbot_ui],
    )

    # Show greeting on startup
    demo.load(
        fn=show_greeting,
        inputs=[personality_dropdown, chatbot_ui],
        outputs=[chatbot_ui],
    )


if __name__ == "__main__":
    demo.launch(share=False)
