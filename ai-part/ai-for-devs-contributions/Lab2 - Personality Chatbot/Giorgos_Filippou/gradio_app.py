"""
Personality Chatbot — Gradio UI (Βήμα 3)
==========================================
Web interface για το chatbot με dropdown επιλογής personality.

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
from pathlib import Path
from dotenv import load_dotenv
import gradio as gr
from openai import OpenAI

load_dotenv(Path(__file__).parent.parent.parent / ".env")

client = OpenAI()


# ─────────────────────────────────────────────────────────────
# ΔΟΣΜΕΝΟ: Φόρτωση personalities
# ─────────────────────────────────────────────────────────────
def load_personalities():
    """Φορτώνει όλα τα personality JSON αρχεία"""
    personalities = {}
    personalities_dir = Path(__file__).parent / "personalities"

    for file in personalities_dir.glob("*.json"):
        with open(file) as f:
            data = json.load(f)
            personalities[data["name"]] = data

    # Default personality (χωρίς αρχείο)
    personalities["Default Assistant"] = {
        "name": "Default Assistant",
        "system_prompt": "You are a helpful assistant.",
        "greeting": "Hello! How can I help you today?",
    }

    return personalities


PERSONALITIES = load_personalities()


# ─────────────────────────────────────────────────────────────
# ΑΣΚΗΣΗ: Υλοποιήστε τη συνάρτηση chat
# ─────────────────────────────────────────────────────────────
def chat(message: str, history: list, personality: str):
    """
    Στέλνει μήνυμα στο OpenAI API και επιστρέφει απάντηση.

    Args:
        message: Το μήνυμα του χρήστη (string)
        history: Ιστορικό μηνυμάτων (list of dicts)
                 Κάθε dict: {"role": "user"|"assistant", "content": "..."}
        personality: Όνομα personality (key στο PERSONALITIES dict)

    Returns:
        str: Η απάντηση του AI

    TODO:
    1. Πάρτε το personality config:
       persona = PERSONALITIES.get(personality, PERSONALITIES["Default Assistant"])

    2. Χτίστε τη λίστα messages:
       messages = [{"role": "system", "content": persona["system_prompt"]}]

    3. Προσθέστε το ιστορικό (ΣΗΜΑΝΤΙΚΟ για τη μνήμη!):
       for msg in history:
           messages.append({"role": msg["role"], "content": msg["content"]})

    4. Προσθέστε το νέο μήνυμα:
       messages.append({"role": "user", "content": message})

    5. Κάντε API call:
       response = client.chat.completions.create(
           model="gpt-4o-mini",
           messages=messages,
           temperature=0.8,
           max_tokens=500
       )

    6. Επιστρέψτε: response.choices[0].message.content
    """
    #Παίρνουμε το persona
    persona = PERSONALITIES.get(personality, PERSONALITIES["Default Assistant"])
    messages = [{'role':'system', 'content':persona["system_prompt"]}]

    #Προσθέτουμε το ιστορικό
    messages.extend(history)
    messages.append({'role':'user','content':message})

    #API Call
    response = client.chat.completions.create(
        model = 'gpt-4o-mini',
        messages = messages,
        temperature=persona.get("temperature", 0.8),
        max_tokens=500
    )

    return response.choices[0].message.content


def get_greeting(personality: str):
    """Επιστρέφει τον χαιρετισμό μιας personality"""
    persona = PERSONALITIES.get(personality, PERSONALITIES["Default Assistant"])
    return persona.get("greeting", "Hello!")



with gr.Blocks(title="🎭 Personality Chatbot") as app:

    # ── Header ──
    gr.Markdown("""
    # 🎭 Personality Chatbot

    Chat with AI personalities! Each personality has its own unique style.

    **Module 2: Prompt Engineering Lab**
    """)

    with gr.Row():

        # ── Αριστερή στήλη: Επιλογή personality ──
        with gr.Column(scale=1):
            personality_dropdown = gr.Dropdown(
                choices=list(PERSONALITIES.keys()),
                value="Default Assistant",
                label="Select Personality",
                info="Each personality has a unique system prompt"
            )

            gr.Markdown("### Personality Info")
            personality_info = gr.Markdown("Select a personality to see details")

            # ΔΟΣΜΕΝΟ: Ενημέρωση info panel
            def update_info(personality):
                persona = PERSONALITIES.get(personality, {})
                prompt_preview = persona.get("system_prompt", "")[:200] + "..."
                return f"""
**{persona.get('name', 'Unknown')}**

*Greeting:* {persona.get('greeting', 'Hello!')}

*System Prompt Preview:*
> {prompt_preview}
"""

            personality_dropdown.change(
                update_info,
                inputs=[personality_dropdown],
                outputs=[personality_info]
            )

        # ── Δεξιά στήλη: Chat ──
        with gr.Column(scale=3):
            chatbot = gr.Chatbot(
                height=400,
                placeholder="Select a personality and start chatting!",
                label="Conversation"
            )

            with gr.Row():
                msg = gr.Textbox(
                    placeholder="Type your message here...",
                    label="Message",
                    scale=4
                )
                send_btn = gr.Button("Send", variant="primary", scale=1)

            clear_btn = gr.Button("Clear Chat")

    # ─────────────────────────────────────────────────────
    # ΑΣΚΗΣΗ: Συνδέστε τα events
    # ─────────────────────────────────────────────────────
    def respond(message, history, personality) :
        """
        Handler για αποστολή μηνύματος.

        TODO:
        1. Αν το message είναι κενό → return "", history (χωρίς αλλαγή)
        2. Καλέστε: response = chat(message, history, personality)
        3. Προσθέστε στο history:
           history.append({"role": "user", "content": message})
           history.append({"role": "assistant", "content": response})
        4. Επιστρέψτε: "", history  (κενό textbox + νέο history)
        """
        # Αν δεν υπαρχει message, επιστρέφουμε (κενό μήνυμα, same history) 
        if not message: return "", history

        #Response from LLM
        response = chat(message, history, personality)

        #Προσθέτουμε το message και το response στο ιστορικό
        history.append({'role':'user', 'content':message})
        history.append({'role':'assistant', 'content':response})

        return "", history



    msg.submit(respond, [msg, chatbot, personality_dropdown], [msg, chatbot]) # Triggers by pressing enter
    send_btn.click(respond, [msg, chatbot, personality_dropdown], [msg, chatbot]) # Triggers by pressing Send button
    clear_btn.click(lambda: [], outputs=[chatbot])

    # ─── Greeting κατά την αλλαγή personality ───
    def show_greeting(personality, history):
        """
        Εμφανίζει greeting όταν αλλάζει personality (μόνο αν το chat είναι κενό).
        """

        if not history:
            greeting = get_greeting(personality)
            return [{"role": "assistant", "content": greeting}]
        return history

    personality_dropdown.change(
        show_greeting,
        inputs=[personality_dropdown, chatbot],
        outputs=[chatbot]
    )



    # --------------------
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
    app.launch(share=False)
