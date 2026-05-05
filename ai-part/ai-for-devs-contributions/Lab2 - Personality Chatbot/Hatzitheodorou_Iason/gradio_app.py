"""
Personality Chatbot — Gradio UI (Βήμα 3)
==========================================
Web interface for a chatbot with personality selection.

Προαπαιτούμενα:
    ✅ Βήμα 1: conversation_manager.py (ολοκληρωμένο)
    ✅ Βήμα 2: chatbot.py (ολοκληρωμένο)

Εκτέλεση:
    python gradio_app.py
    → Ανοίγει http://localhost:7860

Τεκμηρίωση Gradio:
    https://www.gradio.app/docs
"""

import os
import json
from datetime import datetime
from pathlib import Path
import re
from time import perf_counter
import tkinter as tk
from tkinter import filedialog
from dotenv import load_dotenv
from numpy import ma
import openai
import gradio as gr
from openai import OpenAI
import subprocess

# Load .env
env_path = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(env_path, override=True)

# Helper function to fetch available Ollama models using the CLI
def get_ollama_models() -> list[str]:
    """Returns available Ollama model names using the Ollama CLI.
    Args:
        None
    Returns:
        list[str]: A list of available Ollama model names.
    """
    result = subprocess.run(
        ["ollama", "list"],
        capture_output=True,
        text=True,
        check=True,
        encoding="utf-8",
    )
    lines = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    if len(lines) <= 1:
        return []
    models = []
    for line in lines[1:]:
        parts = line.split()
        if parts:
            models.append(parts[0])
    return models

# Define OpenAI clients for both Ollama and OpenAI API (can be used interchangeably)
ollama_client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama",  # required by the client, but Ollama ignores it
)

# Get the Ollama available models
try:
    ollama_models = get_ollama_models()
except Exception as e:
    print(f"Failed to fetch Ollama models: {e}")
    ollama_models = []

openai_api_key = os.getenv("OPENAI_API_KEY")
openai_client = OpenAI() if openai_api_key else None
client = openai_client
openai_models = ["gpt-4o-mini"] if openai_client else []
model_name = "gpt-4o-mini"
clients_list = ["Ollama (local)", "OpenAI API"] if openai_client else ["Ollama (local)"]

CLIENT_OBJECTS = {
    "Ollama (local)": ollama_client,
    "OpenAI API": openai_client,
}

MODELS_BY_CLIENT = {
    "Ollama (local)": ollama_models,
    "OpenAI API": openai_models,
}

default_client_label = clients_list[0] if clients_list else "Ollama (local)"
default_models = MODELS_BY_CLIENT.get(default_client_label, [])
default_model_name = default_models[0] if default_models else ""


# ─────────────────────────────────────────────────────────────
# ΔΟΣΜΕΝΟ: Φόρτωση personalities
# ─────────────────────────────────────────────────────────────
def load_personalities() -> dict:
    """Loads all personality JSON files from the 'personalities' directory
    and returns a dict of personalities. Handles missing personas by providing
    a default personality.
    Args:
        None
    Returns:
        dict: {personality_name: personality_config_dict} 
    Raises:
        None (errors are caught and printed, but do not stop execution)
    """
    personalities = {}
    try:
        personalities_dir = Path(__file__).parent / "personalities"
    except Exception as e:
        print(f"Error determining personalities directory: {e}")
        return personalities

  
    for file in personalities_dir.glob("*.json"):
            try:    
                with open(file, encoding="utf-8") as f:
                    data = json.load(f)
                    data["image_id"] = file.stem
                    personalities[data["name"]] = data
            except Exception as e:
                print(f"Error loading personality from {file}: {e}")
                continue

    # Default personality (χωρίς αρχείο)
    if len(personalities) == 0:
        personalities["Default Assistant"] = {
            "name": "Default Assistant",
            "system_prompt": "You are a helpful assistant.",
            "greeting": "Hello! How can I help you today?",
        }
    return personalities

PERSONALITIES = load_personalities()
# Select the first personality as default (or use "Default Assistant")
if PERSONALITIES:
    default_personality = next(iter(PERSONALITIES.keys()))
else:
    default_personality = "Default Assistant"

# ─────────────────────────────────────────────────────────────
# ΑΣΚΗΣΗ: Υλοποιήστε τη συνάρτηση chat
# ─────────────────────────────────────────────────────────────
def chat(message: str, 
        history: list,
        personality: str,
        client=openai_client,
        model="gpt-4o-mini",
        temperature=0.8,
        max_tokens=500) -> tuple[str, int | str]:
    """
    Sends a message to the OpenAI API and returns a response.
    Args:
        message: The user's message (string)
        history: Chat history (list of dicts)
                 Each dict: {"role": "user"|"assistant", "content": "..."}
        personality: Personality name (key in the PERSONALITIES dict)
        client: OpenAI client instance (default: openai_client)
        model: The model to use for the response (default: "gpt-4o-mini")
        temperature: Sampling temperature for response generation (default: 0.8)
        max_tokens: Maximum number of tokens for the response (default: 500)
    Returns:
        str: The AI's response
        int or str: The total tokens used or "unknown" if not available
    Raises:
        RuntimeError: If there is an error during API call or personality retrieval
    """
    # Get the first persona in the PERSONALITIES dict as default if the specified one is not found
    try: 
        persona = PERSONALITIES.get(personality)
        if persona is None:
            raise ValueError(f"Personality '{personality}' not found")
    except Exception as e:
        print(f"Error retrieving personality '{personality}': {e}")
        print(f"Falling back to default personality: '{default_personality}'")
        try:
            persona = PERSONALITIES.get(default_personality)
        except Exception as e:
            print(f"Error retrieving default personality '{default_personality}': {e}")
            raise RuntimeError("No valid personalities available")
        
    messages = [{"role": "system", "content": persona["system_prompt"]}]
    for msg in history:
        messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": message})
    # Get the API response
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=persona.get("temperature", 0.8) if temperature is None else temperature,
            max_tokens=persona.get("max_tokens", 500) if max_tokens is None else max_tokens
        )
        # Get the total tokens usage if possible (Ollama might not serve this)
        if response:
            try:
                total_tokens = response.usage.total_tokens
            except Exception as e:
                total_tokens = "unknown" #Fallback if usage info is not available
    except Exception as e:
        raise RuntimeError(f"Error during API call: {e}")
    return response.choices[0].message.content, total_tokens

def get_greeting(personality: str) -> str:
    """Returns the greeting message for a given personality.
    Args:
        personality: Personality name (key in the PERSONALITIES dict)
    Returns:
        str: Greeting message
    """
    persona = PERSONALITIES.get(personality, {}) 
    return persona.get("greeting", "Hello!")


def get_profile_image(personality: str) -> None | str:
    """Returns the image path for a given personality, if available.
    Args:
        personality: Personality name (key in the PERSONALITIES dict)
    Returns:
        str or None: Path to the profile image or None if not available
    """
    persona = PERSONALITIES.get(personality, {})
    image_id = persona.get("image_id")
    if not image_id:
        return None

    image_path = Path(__file__).parent / "assets" / f"{image_id}.png"
    if image_path.exists():
        return str(image_path)
    return None


# ─────────────────────────────────────────────────────────────
# ΑΣΚΗΣΗ: Κατασκευή Gradio Interface
# ─────────────────────────────────────────────────────────────
#
# Βασικά Gradio components που θα χρησιμοποιήσετε:
#
#   gr.Blocks()       → Container για όλο το app
#   gr.Markdown()     → Τίτλος/κείμενο
#   gr.Row() / gr.Column() → Layout
#   gr.Dropdown()     → Επιλογή personality
#   gr.Chatbot()      → Εμφάνιση συνομιλίας
#   gr.Textbox()      → Input κειμένου
#   gr.Button()       → Κουμπί
#
# Events:
#   button.click(fn, inputs=[...], outputs=[...])
#   textbox.submit(fn, inputs=[...], outputs=[...])
#
# ─────────────────────────────────────────────────────────────

# Define CSS for profile images to maintain aspect ratio

PROFILE_IMAGE_CSS = """
.profile-image {
    width: 100%;
}
.profile-image img {
    width: 100% !important;
    height: auto !important;
    object-fit: contain;
}
.chat-actions-right {
    display: flex;
    justify-content: flex-end;
    gap: 8px;
    width: 100%;
}
.chat-panel {
    position: relative;
}
:root {
    --chat-scrollbar-width: 16px;
}
#conversation-token-counter-wrap {
    position: absolute !important;
    left: 0 !important;
    right: 0 !important;
    bottom: 10px;
    z-index: 20;
    margin: 0 !important;
    padding-right: calc(10px + var(--chat-scrollbar-width)) !important;
    border: none !important;
    background: transparent !important;
    box-shadow: none !important;
    pointer-events: none;
}
#conversation-token-counter-wrap * {
    margin: 0 !important;
    padding: 0 !important;
    border: none !important;
    background: transparent !important;
    box-shadow: none !important;
}
.conversation-token-text {
    display: block;
    text-align: right;
    white-space: nowrap;
    font-size: 12px;
    line-height: 1.2;
    color: #6b7280;
}
"""

def export_conversation_history_to_json(history, filename="conversation_history.json") -> None:
    """Exports the conversation history to a JSON file.
    Args: 
        history: List of dicts representing the conversation history. Each dict should have the format:
                 {"role": "user"|"assistant", "content": "..."}
        filename: Name of the JSON file to save the history (default: conversation_history.json)
        Returns:
            None (saves the history to a file)
    """
    history_data = []
    for msg in history:
        history_data.append({
            "role": msg["role"],
            "content": msg["content"]
        })
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(history_data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Error exporting conversation history: {e}")
        # TODO: Enforce JSON schema validation for history data structure
        # TODO: Add error handling
    return None

def export_chat_history_raw_text(history, filename="conversation_history.txt") -> None:
    """Exports the conversation history to a plain text file in a readable format.
    Args: 
        history: List of dicts representing the conversation history. Each dict should have the format:
                 {"role": "user"|"assistant", "content": "..."}
        filename: Name of the text file to save the history (default: conversation_history.txt)
        Returns:
            None (saves the history to a file)
    """
    try:
        with open(filename, "w", encoding="utf-8") as f:
            for msg in history:
                role = msg["role"].capitalize()
                content = msg["content"]
                f.write(f"{role}: {content}\n\n")
    except Exception as e:
        print(f"Error exporting conversation history: {e}")

    return None


def export_conversation_history_to_json_with_metadata(history_meta: list[dict], filename="conversation_history_with_metadata.json") -> None:
    """Exports metadata history entries directly to a JSON file."""
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(history_meta or [], f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Error exporting conversation history with metadata: {e}")
    return None


def _normalize_history_for_export(history) -> list[dict]:
    """Normalizes Gradio Chatbot history into role/content message dicts.
    Args:
        history: The chat history from the Gradio Chatbot component, which can be in different formats
             (list of dicts or list of [user, assistant] pairs)
    Returns:
        list: A normalized list of dicts with "role" and "content" keys,
            suitable for export functions.
    """

    normalized = []
    for msg in history or []:
        if isinstance(msg, dict):
            role = msg.get("role")
            content = msg.get("content")
            if role in {"user", "assistant"} and content is not None:
                normalized.append({
                    "role": role,
                    "content": str(content),
                })
        elif isinstance(msg, (list, tuple)) and len(msg) == 2:
            user_text, assistant_text = msg
            if user_text:
                normalized.append({
                    "role": "user",
                    "content": str(user_text),
                })
            if assistant_text:
                normalized.append({
                    "role": "assistant",
                    "content": str(assistant_text),
                })
    return normalized


def build_metadata_export_payload(
    history,
    personality,
    client_label,
    model_name,
    conversation_round_tokens_all,
    conversation_total_tokens,
    conversation_tokens_unknown,
    temperature,
    max_tokens,
) -> list[dict]:
    """Builds a top-level array of per-message metadata export entries."""
    normalized_history = _normalize_history_for_export(history)
    conversation_total = None if conversation_tokens_unknown else conversation_total_tokens

    round_tokens_all = conversation_round_tokens_all or []
    payload = []
    current_round_index = -1
    for msg in normalized_history:
        round_tokens_value = None
        if msg["role"] == "user":
            current_round_index += 1
        if current_round_index >= 0 and current_round_index < len(round_tokens_all):
            round_tokens_value = round_tokens_all[current_round_index]

        payload.append({
            "personality_used": personality,
            "client_used": client_label,
            "model_used": model_name,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "role": msg["role"],
            "content": msg["content"],
            "time_lapsed": None,
            "total_tokens_last_round": round_tokens_value,
            "conversation_total_tokens": conversation_total,
            "tokens_unknown": conversation_tokens_unknown,
        })
    return payload


def resolve_client_by_label(client_label: str):
    """Maps a client label from the UI to a concrete OpenAI-compatible client object."""
    return CLIENT_OBJECTS.get(client_label)


def update_model_dropdown_for_client(client_label: str) -> tuple[dict, str, str]:
    """Updates the model choices when the user changes client selection."""
    models = MODELS_BY_CLIENT.get(client_label, [])
    selected_model = models[0] if models else ""
    return gr.update(choices=models, value=selected_model), client_label, selected_model


def format_total_tokens_display(conversation_total_tokens: int, is_unknown: bool) -> str:
    """Returns the formatted text for the total conversation token counter."""
    if is_unknown:
        return '<div class="conversation-token-text">Total Conversation Tokens: unknown</div>'
    return f'<div class="conversation-token-text">Total Conversation Tokens: {conversation_total_tokens}</div>'


def clear_conversation_and_tokens() -> tuple[list, int, bool, None, list, list, str]:
    """Clears chat history and resets token aggregation state."""
    return [], 0, False, None, [], [], format_total_tokens_display(0, False)


with gr.Blocks(title="🎭 Personality Chatbot") as app:

    # ── Header ──
    gr.Markdown("""
    # 🎭 Personality Chatbot
    ### Chat with AI personalities! Each personality has its own unique style.
    **Module 2: Prompt Engineering Lab**
    """)

    with gr.Row():

        # ── Left column: Personality selection ──
        with gr.Column(scale=1):
            personality_dropdown = gr.Dropdown(
                choices=list(PERSONALITIES.keys()),
                value=default_personality, #The first personality in the dict or "Default Assistant"
                label="Select Personality",
                info="Each personality has a unique system prompt"
            )
            # Personality profile image (if available)
            profile_image = gr.Image(
                value=get_profile_image(default_personality),
                label="Profile Picture",
                interactive=False,
                elem_classes=["profile-image"]
            )

            def update_info(personality):
                persona = PERSONALITIES.get(personality, {})
                prompt_preview = persona.get("system_prompt", "")[:200] + "..."
                return f"""
**{persona.get('name', 'Unknown')}**

*Greeting:* {persona.get('greeting', 'Hello!')}

*System Prompt Preview:*
> {prompt_preview}
"""

            gr.Markdown("### Personality Info")
            personality_info = gr.Markdown(update_info(default_personality))

            personality_dropdown.change(
                update_info,
                inputs=[personality_dropdown],
                outputs=[personality_info]
            )

            personality_dropdown.change(
                get_profile_image,
                inputs=[personality_dropdown],
                outputs=[profile_image]
            )

        # ── Δεξιά στήλη: Chat ──
        with gr.Column(scale=3):
            with gr.Row():
                client_dropdown = gr.Dropdown(
                    choices=clients_list,
                    value=default_client_label,
                    label="Client Select"
                )
                model_dropdown = gr.Dropdown(
                    choices=default_models,
                    value=default_model_name,
                    label="Model Select"
                )
                max_tokens_slider = gr.Slider(
                    minimum=100,
                    maximum=5000,
                    value=PERSONALITIES.get(default_personality, {}).get("max_tokens", 500),
                    step=100,
                    label="Max Tokens"
                )
                temperature_slider = gr.Slider(
                    minimum=0.0,
                    maximum=1.0,
                    value=PERSONALITIES.get(default_personality, {}).get("temperature", 0.8),
                    step=0.05,
                    label="Temperature"
                )

            selected_client_state = gr.State(default_client_label)
            selected_model_state = gr.State(default_model_name)
            selected_temperature_state = gr.State(temperature_slider.value)
            max_tokens_state = gr.State(max_tokens_slider.value)
            conversation_total_tokens_state = gr.State(0)
            conversation_tokens_unknown_state = gr.State(False)
            conversation_round_tokens_last_state = gr.State(None)
            conversation_round_tokens_all_state = gr.State([])
            history_meta_state = gr.State([])

            with gr.Column(elem_classes=["chat-panel"]):
                chatbot = gr.Chatbot(
                    height=450,
                    placeholder="Select a personality and start chatting!",
                    label="Conversation"
                )
                conversation_tokens_display = gr.HTML(
                    value=format_total_tokens_display(0, False),
                    elem_id="conversation-token-counter-wrap"
                )

            with gr.Row():
                msg = gr.Textbox(
                    placeholder="Type your message here...",
                    label="Message",
                    scale=4
                )
                send_btn = gr.Button("Send", variant="primary", scale=1)

            with gr.Row(elem_classes=["chat-actions-right"]):
                clear_btn = gr.Button("Clear Chat")
                export_json_btn = gr.Button("Export JSON")
                export_json_with_metadata_btn = gr.Button("Export JSON with metadata")
                export_txt_btn = gr.Button("Export Text")

            export_status = gr.Markdown(visible=False)

    # ─────────────────────────────────────────────────────
    # ΑΣΚΗΣΗ: Συνδέστε τα events
    # ─────────────────────────────────────────────────────
        def respond(message,
                    history,
                    personality,
                    client_label,
                    model_name,
                    max_tokens,
                    temperature,
                    conversation_total_tokens,
                    conversation_tokens_unknown,
                    conversation_round_tokens_last,
                    conversation_round_tokens_all,
                    history_meta=None) -> tuple[str, list[dict], int, bool, int | None, list[int | None], list[dict], str]:
            """
            Handler for sending a message and storing history, history with metadata, and token counts for display.
            Args:
                message: The user's message
                history: The chat history
                personality: The selected personality
                client_label: The selected client label from the dropdown
                model_name: The selected model name from the dropdown
                max_tokens: The maximum number of tokens for the response
                temperature: The temperature for the response
                conversation_total_tokens: Running token total for the current conversation
                conversation_tokens_unknown: Whether token total became unknown
                conversation_round_tokens_last: Token count for the last round
                conversation_round_tokens_all: Token counts for all rounds
                history_meta: Metadata for the chat history (list of dicts)
            Returns:
                tuple: Updated message, history, token states, history metadata, and formatted token display
            """
            history_meta = list(history_meta or [])

            def append_message_with_meta(
                role: str,
                content: str,
                round_tokens_value: int | None,
                time_lapsed_value: float | str,
                conversation_total_snapshot: int | None,
                tokens_unknown_snapshot: bool,
                round_tokens_all_snapshot: list[int | None],
            ) -> None:
                history.append({"role": role, "content": content})
                history_meta.append({
                    "personality_used": personality,
                    "client_used": client_label,
                    "model_used": model_name,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                    "role": role,
                    "content": content,
                    "time_lapsed": time_lapsed_value,
                    "total_tokens_last_round": round_tokens_value,
                    "conversation_total_tokens": conversation_total_snapshot,
                    "tokens_unknown": tokens_unknown_snapshot,
                    "conversation_round_tokens_last": round_tokens_value,
                    "conversation_round_tokens_all": list(round_tokens_all_snapshot),
                })

            if not message or message.isspace():
                return "", history, conversation_total_tokens, conversation_tokens_unknown, conversation_round_tokens_last, conversation_round_tokens_all, history_meta, format_total_tokens_display(conversation_total_tokens, conversation_tokens_unknown)
            selected_client = resolve_client_by_label(client_label)
            if selected_client is None:
                append_message_with_meta(
                    "assistant",
                    f"Selected client '{client_label}' is not configured.",
                    None,
                    "no_message_response_no_time_rec",
                    None if conversation_tokens_unknown else conversation_total_tokens,
                    conversation_tokens_unknown,
                    conversation_round_tokens_all or [],
                )
                return "", history, conversation_total_tokens, conversation_tokens_unknown, conversation_round_tokens_last, conversation_round_tokens_all, history_meta, format_total_tokens_display(conversation_total_tokens, conversation_tokens_unknown)
            if not model_name:
                append_message_with_meta(
                    "assistant",
                    "No model is available for the selected client.",
                    None,
                    "no_message_response_no_time_rec",
                    None if conversation_tokens_unknown else conversation_total_tokens,
                    conversation_tokens_unknown,
                    conversation_round_tokens_all or [],
                )
                return "", history, conversation_total_tokens, conversation_tokens_unknown, conversation_round_tokens_last, conversation_round_tokens_all, history_meta, format_total_tokens_display(conversation_total_tokens, conversation_tokens_unknown)
            request_started_at = perf_counter()
            response, total_tokens = chat(message, history, personality, client=selected_client, model=model_name, max_tokens=max_tokens, temperature=temperature)
            time_lapsed = round(perf_counter() - request_started_at, 3)
            round_tokens_value = total_tokens if isinstance(total_tokens, int) else None
            conversation_round_tokens_last = round_tokens_value
            conversation_round_tokens_all = (conversation_round_tokens_all or []) + [round_tokens_value]
            if not conversation_tokens_unknown:
                if isinstance(total_tokens, int):
                    conversation_total_tokens += total_tokens
                else:
                    conversation_tokens_unknown = True
            conversation_total_snapshot = None if conversation_tokens_unknown else conversation_total_tokens
            tokens_unknown_snapshot = conversation_tokens_unknown
            round_tokens_all_snapshot = conversation_round_tokens_all
            append_message_with_meta(
                "user",
                message,
                round_tokens_value,
                "user_input_no_time_rec",
                conversation_total_snapshot,
                tokens_unknown_snapshot,
                round_tokens_all_snapshot,
            )
            append_message_with_meta(
                "assistant",
                response,
                round_tokens_value,
                time_lapsed,
                conversation_total_snapshot,
                tokens_unknown_snapshot,
                round_tokens_all_snapshot,
            )
            return "", history, conversation_total_tokens, conversation_tokens_unknown, conversation_round_tokens_last, conversation_round_tokens_all, history_meta, format_total_tokens_display(conversation_total_tokens, conversation_tokens_unknown)

    def export_json(history) ->  dict[str, object]:
        """
        Handler for exporting conversation history as JSON
        Args:
            history: The chat history to export
        Returns:
            dict[str, object]: gr.update status message object to show export result
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_name = f"conversation_history_{timestamp}.json"
        root = tk.Tk() # Create a hidden root window for the file dialog
        root.withdraw()
        root.attributes("-topmost", True) # Ensure the dialog appears on top of other windows
        file_path = filedialog.asksaveasfilename(
            title="Save conversation history (JSON)",
            initialfile=default_name,
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
        )
        root.destroy()
        if not file_path:
            return gr.update(value="Export canceled.", visible=True)
        normalized_history = _normalize_history_for_export(history)
        export_conversation_history_to_json(normalized_history, filename=str(file_path))
        return gr.update(value=f"Saved JSON to: {file_path}", visible=True)

    def export_text(history) ->  dict[str, object]:
        """
        Handler for exporting conversation history as plain text
        Args:
            history: The chat history to export
        Returns:
            dict[str, object]: gr.update status message object to show export result
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_name = f"conversation_history_{timestamp}.txt"
        root = tk.Tk() # Create a hidden root window for the file dialog
        root.withdraw() 
        root.attributes("-topmost", True) # Ensure the dialog appears on top of other windows
        file_path = filedialog.asksaveasfilename(
            title="Save conversation history (Text)",
            initialfile=default_name,
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
        )
        root.destroy()
        if not file_path:
            return gr.update(value="Export canceled.", visible=True)
        normalized_history = _normalize_history_for_export(history)
        export_chat_history_raw_text(normalized_history, filename=str(file_path))
        return gr.update(value=f"Saved text to: {file_path}", visible=True)

    def export_json_with_metadata(history_meta) -> dict[str, object]:
        """
        Handler for exporting conversation history as JSON with metadata
        Args:
            history_meta: The metadata-rich chat history to export
        Returns:
            dict[str, object]: gr.update status message object to show export result
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_name = f"conversation_history_with_metadata_{timestamp}.json"
        root = tk.Tk() # Create a hidden root window for the file dialog
        root.withdraw()
        root.attributes("-topmost", True) # Ensure the dialog appears on top of other windows
        file_path = filedialog.asksaveasfilename(
            title="Save conversation history (JSON with metadata)",
            initialfile=default_name,
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
        )
        root.destroy()
        if not file_path:
            return gr.update(value="Export canceled.", visible=True)

        export_conversation_history_to_json_with_metadata(history_meta, filename=str(file_path))
        return gr.update(value=f"Saved JSON with metadata to: {file_path}", visible=True)

    client_dropdown.change(
        update_model_dropdown_for_client,
        inputs=[client_dropdown],
        outputs=[model_dropdown, selected_client_state, selected_model_state]
    )

    model_dropdown.change(
        lambda model: model,
        inputs=[model_dropdown],
        outputs=[selected_model_state]
    )

    temperature_slider.change(
        lambda temp: temp,
        inputs=[temperature_slider],
        outputs=[selected_temperature_state]
    )

    max_tokens_slider.change(
        lambda max_tok: max_tok,
        inputs=[max_tokens_slider],
        outputs=[max_tokens_state]
    )

    msg.submit(
        respond,
        [msg, chatbot, personality_dropdown, selected_client_state, selected_model_state, max_tokens_state, selected_temperature_state, conversation_total_tokens_state, conversation_tokens_unknown_state, conversation_round_tokens_last_state, conversation_round_tokens_all_state, history_meta_state],
        [msg, chatbot, conversation_total_tokens_state, conversation_tokens_unknown_state, conversation_round_tokens_last_state, conversation_round_tokens_all_state, history_meta_state, conversation_tokens_display]
    )
    send_btn.click(
        respond,
        [msg, chatbot, personality_dropdown, selected_client_state, selected_model_state, max_tokens_state, selected_temperature_state, conversation_total_tokens_state, conversation_tokens_unknown_state, conversation_round_tokens_last_state, conversation_round_tokens_all_state, history_meta_state],
        [msg, chatbot, conversation_total_tokens_state, conversation_tokens_unknown_state, conversation_round_tokens_last_state, conversation_round_tokens_all_state, history_meta_state, conversation_tokens_display]
    )
    clear_btn.click(
        clear_conversation_and_tokens,
        outputs=[chatbot, conversation_total_tokens_state, conversation_tokens_unknown_state, conversation_round_tokens_last_state, conversation_round_tokens_all_state, history_meta_state, conversation_tokens_display]
    )
    export_json_btn.click(export_json, inputs=[chatbot], outputs=[export_status])
    export_json_with_metadata_btn.click(
        export_json_with_metadata,
        inputs=[history_meta_state],
        outputs=[export_status]
    )
    export_txt_btn.click(export_text, inputs=[chatbot], outputs=[export_status])

    # ─── Greeting κατά την αλλαγή personality ───
    def show_greeting(personality, history, history_meta, client_label, model_name, temperature, max_tokens) -> tuple[list[dict[str, str]], list[dict]]:
        """
        Shows the personality's greeting when the personality is changed
        (only if chat is empty).
        Args:
            personality: The selected personality
            history: The current chat history
        Returns:
            tuple[list[dict[str, str]], list[dict]]: Updated chat history and metadata with greeting if applicable
        """
        greeting = get_greeting(personality)
        greeting_history = [{"role": "assistant", "content": greeting}]
        greeting_history_meta = [{
            "personality_used": personality,
            "client_used": client_label,
            "model_used": model_name,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "role": "assistant",
            "content": greeting,
            "time_lapsed": "greet_msg_no_time_rec",
            "total_tokens_last_round": None,
            "conversation_total_tokens": 0,
            "tokens_unknown": False,
            "conversation_round_tokens_last": None,
            "conversation_round_tokens_all": [],
        }]
        # No history yet -> show greeting
        if not history:
            return greeting_history, greeting_history_meta

        # If conversation hasn't started (only assistant/system-like messages), refresh greeting
        has_user_message = any(
            isinstance(msg, dict) and msg.get("role") == "user"
            for msg in history
        )
        if not has_user_message:
            return greeting_history, greeting_history_meta

        # Real conversation exists -> do not overwrite
        return history, history_meta

    personality_dropdown.change(
        show_greeting,
        inputs=[personality_dropdown, chatbot, history_meta_state, selected_client_state, selected_model_state, selected_temperature_state, max_tokens_state],
        outputs=[chatbot, history_meta_state]
    )

    # ── Footer ──
    gr.Markdown("""
    ---
    ### 💡 Learning Points

    1. **System prompts** define the AI's personality
    2. **Temperature** affects creativity (higher = more creative)
    3. **Context** is maintained through message history
    4. Try creating your own personality in the `personalities/` folder!
    """)

if __name__ == "__main__":
    app.launch(share=False, css=PROFILE_IMAGE_CSS)
