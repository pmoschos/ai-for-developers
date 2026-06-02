"""
Gradio Chat UI for the Search Agent.

Authenticates via the FastAPI backend's /login/access-token endpoint,
then lets users create search sessions and chat with the AI agent.

Run:
    python gradio_app.py
"""

import httpx
import gradio as gr

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
API_BASE = "http://localhost:8000/api/v1"
LOGIN_URL = f"{API_BASE}/login/access-token"
SEARCHES_URL = f"{API_BASE}/searches"

# ---------------------------------------------------------------------------
# API helpers
# ---------------------------------------------------------------------------


def api_login(email: str, password: str) -> tuple[str | None, str]:
    """Authenticate and return (access_token, status_message)."""
    try:
        resp = httpx.post(
            LOGIN_URL,
            data={"username": email, "password": password},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=15,
        )
        if resp.status_code == 200:
            token = resp.json().get("access_token")
            return token, "✅ Logged in successfully!"
        else:
            detail = resp.json().get("detail", resp.text)
            return None, f"❌ Login failed: {detail}"
    except httpx.ConnectError:
        return None, "❌ Cannot reach the backend. Is it running on localhost:8000?"
    except Exception as exc:
        return None, f"❌ Unexpected error: {exc}"


def api_create_session(token: str, title: str = "Gradio Session") -> str | None:
    """Create a new SearchSession and return its UUID."""
    resp = httpx.post(
        f"{SEARCHES_URL}/",
        json={"title": title},
        headers={"Authorization": f"Bearer {token}"},
        timeout=15,
    )
    if resp.status_code == 200:
        return resp.json().get("id")
    return None


def api_chat(token: str, session_id: str, message: str) -> str:
    """Send a message to the agent and return the reply."""
    resp = httpx.post(
        f"{SEARCHES_URL}/{session_id}/chat",
        json={"message": message},
        headers={"Authorization": f"Bearer {token}"},
        timeout=120,  # agent may take a while
    )
    if resp.status_code == 200:
        return resp.json().get("reply", "")
    return f"⚠️ Error {resp.status_code}: {resp.text}"


def api_list_sessions(token: str) -> list[dict]:
    """Fetch all search sessions for the current user."""
    resp = httpx.get(
        f"{SEARCHES_URL}/",
        headers={"Authorization": f"Bearer {token}"},
        timeout=15,
    )
    if resp.status_code == 200:
        return resp.json().get("data", [])
    return []


# ---------------------------------------------------------------------------
# Theme & CSS
# ---------------------------------------------------------------------------

CUSTOM_CSS = """
/* ─── Login card ─── */
#login-card {
    max-width: 420px;
    margin: 60px auto;
    padding: 32px 36px;
    border-radius: 18px;
    background: linear-gradient(145deg, #1e1e2e 0%, #2a2a3c 100%);
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.45);
    border: 1px solid rgba(255, 255, 255, 0.06);
}
#login-card .gr-form { gap: 14px; }

#login-title {
    text-align: center;
    font-size: 1.6rem;
    font-weight: 700;
    background: linear-gradient(135deg, #a78bfa, #818cf8, #6366f1);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 4px;
}
#login-subtitle {
    text-align: center;
    font-size: 0.88rem;
    color: #9ca3af;
    margin-bottom: 12px;
}

#login-btn {
    background: linear-gradient(135deg, #7c3aed 0%, #6366f1 100%) !important;
    border: none !important;
    color: #fff !important;
    font-weight: 600 !important;
    border-radius: 10px !important;
    padding: 10px 0 !important;
    font-size: 0.95rem !important;
    transition: transform 0.15s ease, box-shadow 0.15s ease !important;
}
#login-btn:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(99, 102, 241, 0.4) !important;
}

#login-status {
    text-align: center;
    font-size: 0.85rem;
    min-height: 24px;
}

/* ─── Chat area ─── */
#chat-header {
    text-align: center;
    font-size: 1.25rem;
    font-weight: 700;
    background: linear-gradient(135deg, #a78bfa, #818cf8, #6366f1);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    padding: 8px 0;
}

#session-bar {
    display: flex;
    gap: 8px;
    align-items: center;
}

#new-session-btn {
    background: linear-gradient(135deg, #7c3aed, #6366f1) !important;
    border: none !important;
    color: #fff !important;
    font-weight: 600 !important;
    border-radius: 10px !important;
    min-width: 150px !important;
    transition: transform 0.15s ease, box-shadow 0.15s ease !important;
}
#new-session-btn:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 14px rgba(99, 102, 241, 0.35) !important;
}

#logout-btn {
    background: transparent !important;
    border: 1px solid rgba(239, 68, 68, 0.5) !important;
    color: #ef4444 !important;
    border-radius: 10px !important;
    font-weight: 500 !important;
    min-width: 90px !important;
    transition: background 0.2s ease !important;
}
#logout-btn:hover {
    background: rgba(239, 68, 68, 0.12) !important;
}

/* ─── Overall spacing ─── */
.gradio-container { max-width: 860px !important; }

/* chatbot bubble tweaks */
.chatbot .message.bot .content {
    background: linear-gradient(135deg, #312e81 0%, #1e1b4b 100%) !important;
    border: 1px solid rgba(129, 140, 248, 0.15) !important;
    border-radius: 14px !important;
}
"""

# ---------------------------------------------------------------------------
# Gradio App
# ---------------------------------------------------------------------------


def build_app() -> gr.Blocks:
    with gr.Blocks(
        title="🔍 Search Agent Chat",
    ) as app:
        # ── Shared state ──
        token_state = gr.State(value=None)  # JWT access token
        session_state = gr.State(value=None)  # current search session UUID

        # ══════════════════════════════════════════════════════════════════
        #  LOGIN VIEW
        # ══════════════════════════════════════════════════════════════════
        with gr.Column(visible=True, elem_id="login-card") as login_view:
            gr.Markdown("🔍 Search Agent", elem_id="login-title")
            gr.Markdown("Sign in to start chatting", elem_id="login-subtitle")

            email_box = gr.Textbox(
                label="Email",
                placeholder="you@example.com",
                type="email",
            )
            password_box = gr.Textbox(
                label="Password",
                placeholder="••••••••",
                type="password",
            )
            login_btn = gr.Button("Sign In", variant="primary", elem_id="login-btn")
            login_status = gr.Markdown("", elem_id="login-status")

        # ══════════════════════════════════════════════════════════════════
        #  CHAT VIEW
        # ══════════════════════════════════════════════════════════════════
        with gr.Column(visible=False) as chat_view:
            gr.Markdown("🔍 Search Agent Chat", elem_id="chat-header")

            with gr.Row(elem_id="session-bar"):
                session_dropdown = gr.Dropdown(
                    label="Session",
                    choices=[],
                    interactive=True,
                    scale=4,
                )
                new_session_btn = gr.Button(
                    "＋ New Session",
                    elem_id="new-session-btn",
                    scale=1,
                )
                logout_btn = gr.Button(
                    "Logout",
                    elem_id="logout-btn",
                    scale=1,
                )

            chatbot = gr.Chatbot(
                label="Conversation",
                height=460,
                avatar_images=(
                    None,
                    "https://api.dicebear.com/9.x/bottts-neutral/svg?seed=agent",
                ),
            )

            with gr.Row():
                msg_box = gr.Textbox(
                    placeholder="Ask anything… e.g. 'Latest news about AI'",
                    show_label=False,
                    scale=6,
                    lines=1,
                )
                send_btn = gr.Button("Send ➤", variant="primary", scale=1)

        # ──────────────────────────────────────────────────────────────
        #  CALLBACKS
        # ──────────────────────────────────────────────────────────────

        def handle_login(email: str, password: str):
            """Attempt login → on success, switch to chat view."""
            if not email or not password:
                return (
                    gr.update(visible=True),  # login_view
                    gr.update(visible=False),  # chat_view
                    "⚠️ Please enter email and password.",  # login_status
                    None,  # token_state
                    None,  # session_state
                    gr.update(choices=[], value=None),  # session_dropdown
                    [],  # chatbot
                )

            token, msg = api_login(email, password)
            if token is None:
                return (
                    gr.update(visible=True),
                    gr.update(visible=False),
                    msg,
                    None,
                    None,
                    gr.update(choices=[], value=None),
                    [],
                )

            # Fetch existing sessions
            sessions = api_list_sessions(token)
            choices = [(f"{s['title']}  ({s['id'][:8]}…)", s["id"]) for s in sessions]

            # Auto-create a session if none exist
            current_session = None
            if choices:
                current_session = choices[0][1]
            else:
                new_id = api_create_session(token, "Gradio Session")
                if new_id:
                    choices = [("Gradio Session", new_id)]
                    current_session = new_id

            return (
                gr.update(visible=False),  # hide login
                gr.update(visible=True),  # show chat
                "",  # clear login_status
                token,  # token_state
                current_session,  # session_state
                gr.update(choices=choices, value=current_session),
                [],  # fresh chatbot
            )

        login_btn.click(
            fn=handle_login,
            inputs=[email_box, password_box],
            outputs=[
                login_view,
                chat_view,
                login_status,
                token_state,
                session_state,
                session_dropdown,
                chatbot,
            ],
        )

        # Also trigger login on Enter key in password field
        password_box.submit(
            fn=handle_login,
            inputs=[email_box, password_box],
            outputs=[
                login_view,
                chat_view,
                login_status,
                token_state,
                session_state,
                session_dropdown,
                chatbot,
            ],
        )

        # ── New session ──
        def handle_new_session(token: str, current_choices):
            if not token:
                return None, gr.update(), []

            new_id = api_create_session(token, "Gradio Session")
            if not new_id:
                return None, gr.update(), []

            # Refresh full list
            sessions = api_list_sessions(token)
            choices = [(f"{s['title']}  ({s['id'][:8]}…)", s["id"]) for s in sessions]

            return (
                new_id,
                gr.update(choices=choices, value=new_id),
                [],
            )

        new_session_btn.click(
            fn=handle_new_session,
            inputs=[token_state, session_dropdown],
            outputs=[session_state, session_dropdown, chatbot],
        )

        # ── Switch session ──
        def handle_switch_session(selected_id):
            # Clear chat when switching – the backend keeps memory per session
            return selected_id, []

        session_dropdown.change(
            fn=handle_switch_session,
            inputs=[session_dropdown],
            outputs=[session_state, chatbot],
        )

        # ── Send message ──
        def handle_send(
            user_msg: str,
            history: list,
            token: str,
            session_id: str,
        ):
            if not user_msg or not user_msg.strip():
                yield history, gr.update()
                return

            if not token or not session_id:
                history = history + [
                    {"role": "user", "content": user_msg},
                    {
                        "role": "assistant",
                        "content": "⚠️ No active session. Please log in and select a session.",
                    },
                ]
                yield history, gr.update(value="")
                return

            # Show user message + typing indicator immediately
            history = history + [
                {"role": "user", "content": user_msg},
                {"role": "assistant", "content": "⏳ Thinking…"},
            ]
            yield history, gr.update(value="")

            # Call the agent
            reply = api_chat(token, session_id, user_msg)

            # Replace the typing indicator with the real reply
            history[-1] = {"role": "assistant", "content": reply}
            yield history, gr.update(value="")

        send_btn.click(
            fn=handle_send,
            inputs=[msg_box, chatbot, token_state, session_state],
            outputs=[chatbot, msg_box],
        )

        msg_box.submit(
            fn=handle_send,
            inputs=[msg_box, chatbot, token_state, session_state],
            outputs=[chatbot, msg_box],
        )

        # ── Logout ──
        def handle_logout():
            return (
                gr.update(visible=True),  # show login
                gr.update(visible=False),  # hide chat
                None,  # clear token
                None,  # clear session
                gr.update(choices=[], value=None),
                [],  # clear chatbot
                "",  # clear login_status
            )

        logout_btn.click(
            fn=handle_logout,
            inputs=[],
            outputs=[
                login_view,
                chat_view,
                token_state,
                session_state,
                session_dropdown,
                chatbot,
                login_status,
            ],
        )

    return app


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    _theme = gr.themes.Soft(
        primary_hue="indigo",
        secondary_hue="violet",
        neutral_hue="slate",
        font=gr.themes.GoogleFont("Inter"),
    ).set(
        body_background_fill="#0f0f1a",
        body_background_fill_dark="#0f0f1a",
        block_background_fill="#1a1a2e",
        block_background_fill_dark="#1a1a2e",
        input_background_fill="#262640",
        input_background_fill_dark="#262640",
        button_primary_background_fill="linear-gradient(135deg, #7c3aed, #6366f1)",
        button_primary_background_fill_dark="linear-gradient(135deg, #7c3aed, #6366f1)",
        button_primary_text_color="#ffffff",
    )

    demo = build_app()
    demo.launch(
        server_name="0.0.0.0",
        server_port=9987,
        share=False,
        show_error=True,
        theme=_theme,
        css=CUSTOM_CSS,
    )
