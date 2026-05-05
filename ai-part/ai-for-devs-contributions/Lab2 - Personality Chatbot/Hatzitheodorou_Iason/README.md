# Personality Chatbot (Lab 2)

A multi-personality chatbot project with:

- terminal chat mode
- Gradio web UI
- personality presets loaded from JSON
- selectable LLM backend (OpenAI API or local Ollama)
- conversation export to text/JSON (with optional metadata)

This README documents the current implementation state of this sub-project.

## Project Structure

```
yes_lab2_HatzitheodorouIason/
├── README.md
├── chatbot.py
├── compare_personalities.py
├── conversation_manager.py
├── gradio_app.py
├── personalities/
│   ├── cynical_support.json
│   ├── drunk_maniac.json
│   ├── pirate_expert.json
│   └── zen_master.json
├── assets/
│   ├── cynical_support.png
│   ├── drunk_maniac.png
│   ├── pirate_expert.png
│   └── zen_master.png
└── exports/
        └── (example exported conversations)
```

## Implemented Features

## 1) Personality system

- Personalities are loaded from `personalities/*.json`.
- Each personality includes at least:
    - `name`
    - `description`
    - `system_prompt`
    - `temperature`
    - `greeting`
- UI also maps each personality JSON filename stem to `assets/<stem>.png` when available.

Currently available personalities:

- The Cynical Support Agent
- Barfly McCodeface
- First Mate PirateScript
- Master Zen Coder

## 2) Terminal chatbot (`chatbot.py`)

- Supports interactive chat in terminal.
- Supports commands:
    - `/switch <name>`
    - `/list`
    - `/clear`
    - `/history`
    - `/help`
    - `/quit`
- Uses OpenAI Chat Completions (`gpt-4o-mini` in current code).

Run examples:

```bash
python chatbot.py
python chatbot.py --personality cynical_support
python chatbot.py --list
```

## 3) Conversation manager (`conversation_manager.py`)

- Stores system prompt and user/assistant message history.
- Supports role validation (`user` or `assistant`).
- Supports history trimming with `max_history`.
- Provides summary counts.
- Supports JSON export via `export_conversation(...)`.

Run local checks:

```bash
python conversation_manager.py
```

## 4) Gradio app (`gradio_app.py`)

Implemented UI capabilities:

- Personality dropdown + personality info preview.
- Personality profile image rendering.
- Client selector:
    - `Ollama (local)`
    - `OpenAI API` (available only if `OPENAI_API_KEY` is set)
- Model selector per client.
- Runtime controls:
    - `Temperature` slider
    - `Max Tokens` slider
- Chat panel with history.
- Greeting injection on personality change (when conversation has not really started).
- Token tracking state:
    - last round tokens
    - per-round token list
    - total conversation tokens (or `unknown` when unavailable)
- Response timing capture (`time_lapsed`) in metadata state.
- Export buttons:
    - Export JSON
    - Export Text
    - Export JSON with metadata

Run:

```bash
python gradio_app.py
```

Then open `http://localhost:7860`.

## 5) Prompt experiments (`compare_personalities.py`)

- Experiment 1: sends the same technical question to all personalities.
- Experiment 2: compares outputs across temperatures (`0.0`, `0.5`, `1.0`).

Run:

```bash
python compare_personalities.py
```

## Environment and Dependencies

## Python

- Python 3.10+ recommended.

## Environment variables

Create a `.env` file in the lab root (as expected by the code), with:

```env
OPENAI_API_KEY=sk-...
```

If `OPENAI_API_KEY` is missing, the Gradio app still works with Ollama local mode.

## Install dependencies

From the workspace root (where `requirements.txt` exists):

```bash
pip install -r requirements.txt
```

Note: the current `requirements.txt` is shared at workspace level and includes more packages than this sub-project strictly needs.

## Ollama Setup (Optional, for local models)

To use local models from Gradio:

1. Install Ollama and ensure `ollama` is available on PATH.
2. Start Ollama service.
3. Pull at least one model (example):

```bash
ollama pull llama3.2
```

The app reads models via `ollama list`.

## Current Known Limitations

- `chatbot.py` currently initializes only the OpenAI client (no Ollama fallback in terminal mode).
- Token usage may be unavailable for some Ollama responses, so total tokens can become `unknown`.
- Export dialogs use Tkinter native save dialogs, which may behave differently across environments.

## TODOs

1. Add robust exception handling and user-facing error messages in `gradio_app.py` for backend failures (timeouts, missing model, connection refused).
2. Add automated tests for `gradio_app.py` helper functions (`_normalize_history_for_export`, metadata payload construction, token display formatting).
3. Refactor shared chat logic into a common module used by both `chatbot.py` and `gradio_app.py` to avoid duplicate behavior.
4. Add optional persistence layer (save/load active session automatically without manual export).
5. Enforce specific structured json schema for the metadata json export, as well as 
relevant validation.

