"""
Module 4: Document Q&A Bot — LangChain + LangSmith Edition
============================================================
Usage:
    python gradio_app.py
    → http://127.0.0.1:7860

LangSmith traces: https://smith.langchain.com
"""

from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env", override=True)

import gradio as gr
from document_qa_bot.rag_pipeline import RAGPipeline
from document_qa_bot.generation.prompts import (
    QA_SYSTEM_PROMPT, QA_DETAILED_PROMPT, QA_CONCISE_PROMPT, QA_KIDS_PROMPT,
)

# ── Singleton Pipeline ─────────────────────────────────────────────────────────
pipeline: RAGPipeline | None = None


def get_pipeline() -> RAGPipeline:
    global pipeline
    if pipeline is None:
        pipeline = RAGPipeline()
    return pipeline


def capture_and_clear(question: str):
    """
    Step 1 (queue=False → instant): save question to State, clear the textbox.
    This runs BEFORE the LLM starts, so the input clears immediately.
    """
    return question, ""

# ── Callbacks ──────────────────────────────────────────────────────────────────

def ingest_file(files):
    """Generator: shows spinner instantly, then ingests each file and reports."""
    if not files:
        yield "Please upload at least one file first."
        return

    if not isinstance(files, list):
        files = [files]

    yield f"⏳ Processing {len(files)} file(s)…"

    results = []
    for f in files:
        name = Path(f.name).name
        try:
            n = get_pipeline().ingest(f.name)
            results.append(f"✅ **{name}** → {n} chunks added")
        except Exception as e:
            results.append(f"⚠️ **{name}**: {e}")

    yield "\n\n".join(results)


def answer_question(question: str, history: list, use_hyde: bool):
    """Stream RAG answer. Routes to HyDE or standard retrieval based on checkbox."""
    if not question.strip():
        yield history, "", ""
        return

    history = list(history or [])
    history.append({"role": "user", "content": question})
    history.append({"role": "assistant", "content": ""})

    accumulated = ""
    hyde_md     = ""

    try:
        for event in get_pipeline().answer_stream(question, history=history[:-2], use_hyde=use_hyde):
            if event["type"] == "status":
                yield history, event["message"], hyde_md

            elif event["type"] == "token":
                accumulated += event["content"]
                history[-1]["content"] = accumulated
                yield history, "⏳ Generating…", hyde_md

            elif event["type"] == "done":
                sources    = event.get("sources", [])
                token_info = event.get("token_info", "")
                hypo_doc   = event.get("hypothetical_doc")

                if sources:
                    sources_md = "\n\n---\n📚 **Sources:**\n"
                    for i, s in enumerate(sources[:4], 1):
                        filename = Path(s["source"]).name
                        page     = f" · page {int(s['page']) + 1}" if s.get("page") != "" else ""
                        score    = f" `[{s['score']:.2f}]`" if s.get("score") is not None else ""
                        chunk    = s.get("chunk", "")[:300].replace("\n", " ")
                        sources_md += f"\n**[{i}] `{filename}`{page}{score}**\n> {chunk}…\n"
                    history[-1]["content"] = accumulated + sources_md

                mode_label = "🧪 HyDE" if use_hyde else "🔍 Standard"
                if hypo_doc:
                    hyde_md = f"**💡 Hypothetical Document (HyDE):**\n\n> {hypo_doc}"

                yield history, f"{mode_label} | 🔢 {token_info}", hyde_md

    except Exception as e:
        history[-1]["content"] = f"❌ Error: {e}"
        yield history, "", ""


def apply_system_prompt(prompt: str):
    get_pipeline().set_system_prompt(prompt)
    return "✅ System prompt applied!"


def reset_system_prompt():
    return QA_SYSTEM_PROMPT, "↩️ Reset to default."


def get_stats():
    try:
        stats = get_pipeline().get_stats()
        sources = "\n".join(f"- {s}" for s in stats["sources"][:15]) or "_No documents yet._"
        return f"""### 📊 Knowledge Base Stats
- **Total Chunks:** {stats['total_chunks']}
- **Unique Sources:** {stats['unique_sources']}

**Documents:**
{sources}"""
    except Exception as e:
        return f"Error: {e}"


def clear_database():
    try:
        get_pipeline().clear()
        return "✅ Database cleared."
    except Exception as e:
        return f"❌ Error: {e}"


# ── Gradio UI ──────────────────────────────────────────────────────────────────

with gr.Blocks(title="📚 Document Q&A Bot — LangChain Edition") as app:

    gr.Markdown("""
    # 📚 Document Q&A Bot — LangChain Edition
    Powered by **LangChain** · **ChromaDB** · **GPT-4o-mini** · **LangSmith** observability
    """)

    with gr.Tabs():

        # ── Tab 1: Chat ────────────────────────────────────────
        with gr.TabItem("💬 Chat"):
            chatbot = gr.Chatbot(
                value=[{"role": "assistant",
                        "content": "👋 Γεια! Ανέβασε ένα έγγραφο στο tab **📁 Upload Documents** και ρώτα με ό,τι θέλεις!"}],
                height=400,
                placeholder="Upload documents first, then ask questions!",
                label="Conversation",
            )

            with gr.Row():
                msg = gr.Textbox(
                    placeholder="Ask a question about your documents…",
                    label="Question",
                    scale=4,
                )
                send_btn = gr.Button("Ask ➤", variant="primary", scale=1)

            with gr.Row():
                clear_chat  = gr.Button("🗑️ Clear Chat", scale=1)
                hyde_toggle = gr.Checkbox(label="🧪 Use HyDE", value=False, scale=1,
                                          info="Generates a hypothetical answer doc for better retrieval")
                token_display = gr.Markdown("", label="")

            with gr.Accordion("💡 HyDE — Hypothetical Document", open=False):
                hyde_display = gr.Markdown(
                    "_Enable HyDE and ask a question to see the generated document._"
                )

            # ── State: holds the question after the textbox is cleared ─────────
            question_state = gr.State("")

            msg.submit(
                capture_and_clear, [msg], [question_state, msg], queue=False
            ).then(
                answer_question, [question_state, chatbot, hyde_toggle],
                [chatbot, token_display, hyde_display]
            )
            send_btn.click(
                capture_and_clear, [msg], [question_state, msg], queue=False
            ).then(
                answer_question, [question_state, chatbot, hyde_toggle],
                [chatbot, token_display, hyde_display]
            )
            clear_chat.click(lambda: ([], "", ""), outputs=[chatbot, token_display, hyde_display])

        # ── Tab 2: Upload ──────────────────────────────────────
        with gr.TabItem("📁 Upload Documents"):
            gr.Markdown("### Add documents to the knowledge base")

            file_upload = gr.File(
                label="Upload Document(s)",
                file_types=[".pdf", ".txt", ".md", ".docx"],
                file_count="multiple",
            )
            ingest_btn = gr.Button("⬆️ Ingest Document", variant="primary")
            ingest_status = gr.Markdown()

            ingest_btn.click(ingest_file, file_upload, ingest_status)

            gr.Markdown("""
            **Supported:** PDF, TXT, Markdown, DOCX

            Each document is:
            1. Loaded via **LangChain** Document Loaders
            2. Split with `RecursiveCharacterTextSplitter` (1000 chars, 200 overlap)
            3. Embedded with `OpenAIEmbeddings` (`text-embedding-3-small`)
            4. Stored in **ChromaDB** (local persistence)
            """)

        # ── Tab 3: Stats ───────────────────────────────────────
        with gr.TabItem("📊 Stats"):
            stats_output = gr.Markdown()
            with gr.Row():
                refresh_btn = gr.Button("🔄 Refresh")
                clear_db_btn = gr.Button("🗑️ Clear Database", variant="stop")
            clear_status = gr.Markdown()

            refresh_btn.click(get_stats, outputs=stats_output)
            clear_db_btn.click(clear_database, outputs=clear_status)
            app.load(get_stats, outputs=stats_output)

        # ── Tab 4: Settings ────────────────────────────────────
        with gr.TabItem("⚙️ Settings"):
            gr.Markdown("### Customize the bot's persona")

            with gr.Row():
                preset_btns = [
                    gr.Button("🎓 Academic", scale=1),
                    gr.Button("✂️ Concise", scale=1),
                    gr.Button("👧 Kids Friendly", scale=1),
                    gr.Button("↩️ Default", scale=1),
                ]

            system_prompt_box = gr.Textbox(
                value=QA_SYSTEM_PROMPT,
                label="System Prompt",
                lines=8,
                info="Changes apply immediately to the next question.",
            )

            apply_btn = gr.Button("✅ Apply", variant="primary")
            prompt_status = gr.Markdown()

            apply_btn.click(apply_system_prompt, system_prompt_box, prompt_status)
            preset_btns[0].click(lambda: QA_DETAILED_PROMPT, outputs=system_prompt_box)
            preset_btns[1].click(lambda: QA_CONCISE_PROMPT,  outputs=system_prompt_box)
            preset_btns[2].click(lambda: QA_KIDS_PROMPT,    outputs=system_prompt_box)
            preset_btns[3].click(reset_system_prompt, outputs=[system_prompt_box, prompt_status])

    gr.Markdown("""
    ---
    **LangChain pipeline:** Loader → Splitter → Embeddings → ChromaDB → History-Aware Retriever → GPT-4o-mini
    | **LangSmith:** Enable tracing via `LANGCHAIN_TRACING_V2=true` in `.env`
    """)


if __name__ == "__main__":
    app.launch(share=False, theme=gr.themes.Soft())
