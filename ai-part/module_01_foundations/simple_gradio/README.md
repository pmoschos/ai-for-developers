# 🎓 Simple Gradio — Step-by-Step Tutorial

Learn Gradio from zero! Each example builds on the previous one.

## Examples

| #  | File | Concepts | API Key? |
|----|------|----------|----------|
| 01 | `01_hello_world.py`       | `gr.Interface`, text input/output              | ❌ No |
| 02 | `02_multiple_inputs.py`   | Slider, Dropdown, multiple outputs, Markdown   | ❌ No |
| 03 | `03_image_input.py`       | Image upload, Radio buttons, PIL processing    | ❌ No |
| 04 | `04_interactive_events.py`| `gr.Blocks`, Buttons, `gr.State`, `.submit()`  | ❌ No |
| 05 | `05_tabs_and_layout.py`   | Tabs, Rows, Columns, Accordion, `.change()`    | ❌ No |
| 06 | `06_chatbot.py`           | `gr.ChatInterface`, history, streaming (yield) | ❌ No |
| 07 | `07_chatbot_openai.py`    | OpenAI + Gradio, streaming, single-turn        | ✅ Yes |
| 08 | `08_chatbot_memory.py`    | Conversation memory, full message history      | ✅ Yes |

> **Examples 01–06 do not require an API key!**  
> Examples 07–08 require `OPENAI_API_KEY` in your `.env` file.

## How to Run

```bash
# Run any example:
python 01_hello_world.py

# Then open http://127.0.0.1:7860 in your browser
```

## Learning Path

```
01 → Basic Interface (fn + inputs + outputs)
02 → Multiple input types and outputs
03 → Working with images (non-text data)
04 → Buttons, State, and Events (gr.Blocks)
05 → Tabs, Rows, Columns (layout)
06 → Chatbot UI — fake bot (no API key needed)
07 → Chatbot with OpenAI (single-turn, no memory)
08 → Chatbot with OpenAI + Memory (full conversation)
```

After completing these, you're ready for `gradio_app.py` — the full LLM Playground!
