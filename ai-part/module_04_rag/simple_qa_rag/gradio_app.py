"""
Module 4: Document Q&A Bot — Enhanced Gradio UI
================================================
Features:
  1. Conversation memory
  2. Relevance threshold guard
  3. Streaming responses
  4. Token / cost counter
  5. Custom system prompt via Settings tab

Usage:
    python gradio_app.py
"""

import os
from pathlib import Path
from dotenv import load_dotenv
import gradio as gr

load_dotenv(Path(__file__).parent / ".env", override=True)

from document_qa_bot.config import get_config
from document_qa_bot.ingestion.loader import DocumentLoader
from document_qa_bot.ingestion.chunker import TextChunker
from document_qa_bot.ingestion.embedder import Embedder
from document_qa_bot.retrieval.vector_store import VectorStore
from document_qa_bot.retrieval.retriever import Retriever
from document_qa_bot.generation.qa_chain import QAChain
from document_qa_bot.generation.prompts import QA_SYSTEM_PROMPT


class QABotManager:
    """Manages the QA bot instance (lazy init singleton)."""

    def __init__(self):
        self._qa_bot = None

    def get_qa_bot(self) -> QAChain:
        if self._qa_bot is None:
            config = get_config()
            embedder = Embedder()
            vector_store = VectorStore(persist_directory=str(config.chroma_db_path))
            retriever = Retriever(vector_store=vector_store, embedder=embedder)
            self._qa_bot = QAChain(retriever=retriever)
        return self._qa_bot

    def set_system_prompt(self, prompt: str):
        """Pass updated system prompt to QAChain (Feature #5)."""
        bot = self.get_qa_bot()
        bot.set_system_prompt(prompt)


qa_manager = QABotManager()


# ── Callbacks ──────────────────────────────────────────────────────────────────

def ingest_file(file):
    """Ingest an uploaded file into ChromaDB."""
    if file is None:
        return "Please upload a file first."

    config = get_config()
    loader = DocumentLoader()
    chunker = TextChunker(chunk_size=config.chunk_size, chunk_overlap=config.chunk_overlap)
    embedder = Embedder()
    vector_store = VectorStore(persist_directory=str(config.chroma_db_path))

    try:
        documents = loader.load(Path(file.name))
        if not documents:
            return f"❌ Could not extract content from **{Path(file.name).name}**"

        chunks = []
        for doc in documents:
            chunks.extend(chunker.chunk(doc["content"], doc["metadata"]))

        vector_store.add_documents(chunks, embedder)
        return f"✅ Ingested **{Path(file.name).name}** → {len(chunks)} chunks added"

    except Exception as e:
        return f"❌ Error: {e}"


def answer_question(question: str, history: list, use_hyde: bool = False):
    """
    Stream the RAG answer token-by-token.
    Passes conversation history to the LLM (Feature #1).
    Supports HyDE retrieval when use_hyde=True.
    """
    if not question.strip():
        yield history, "", ""
        return

    history = list(history or [])
    history.append({"role": "user", "content": question})
    history.append({"role": "assistant", "content": ""})

    try:
        qa_bot = qa_manager.get_qa_bot()
        conv_history = history[:-2]

        accumulated = ""
        current_sources = []
        hyde_doc_text = ""

        for event in qa_bot.answer_stream(question, history=conv_history, use_hyde=use_hyde):
            if event["type"] == "token":
                accumulated += event["content"]
                history[-1]["content"] = accumulated
                label = "🔬 HyDE ⏳ Generating…" if use_hyde else "⏳ Generating…"
                yield history, label, ""

            elif event["type"] == "done":
                current_sources = event.get("sources", [])
                token_info = event.get("token_info", "")
                hyp = event.get("hypothetical_doc")
                if hyp:
                    hyde_doc_text = f"**🔬 HyDE — Hypothetical Document used for search:**\n\n> {hyp}"

                if current_sources:
                    sources_md = "\n\n---\n📚 **Sources:**\n"
                    for s in current_sources[:3]:
                        sources_md += f"- `{s['source']}` (relevance: {s['score']:.2f})\n"
                    history[-1]["content"] = accumulated + sources_md

                mode = "🔬 HyDE" if use_hyde else "🔍 Standard"
                yield history, f"{mode} | 🔢 {token_info}", hyde_doc_text

    except Exception as e:
        history[-1]["content"] = f"❌ Error: {e}"
        yield history, "", ""


def apply_system_prompt(prompt: str):
    """Apply a custom system prompt (Feature #5)."""
    qa_manager.set_system_prompt(prompt)
    return "✅ System prompt applied!"


def reset_system_prompt():
    return QA_SYSTEM_PROMPT, "↩️ Reset to default."


def get_stats():
    try:
        config = get_config()
        vector_store = VectorStore(persist_directory=str(config.chroma_db_path))
        stats = vector_store.get_stats()
        sources_list = "\n".join(f"- {s}" for s in stats["sources"][:15]) or "_No documents yet._"
        return f"""### 📊 Knowledge Base Stats
- **Total Chunks:** {stats['total_chunks']}
- **Unique Sources:** {stats['unique_sources']}

**Documents:**
{sources_list}"""
    except Exception as e:
        return f"Error: {e}"


def clear_database():
    try:
        config = get_config()
        VectorStore(persist_directory=str(config.chroma_db_path)).clear()
        return "✅ Database cleared."
    except Exception as e:
        return f"❌ Error: {e}"


# ── Gradio UI ──────────────────────────────────────────────────────────────────

with gr.Blocks(title="📚 Document Q&A Bot") as app:

    gr.Markdown("""
    # 📚 Document Q&A Bot
    Upload documents and ask questions using **RAG** (Retrieval-Augmented Generation).
    *Module 4 · Enhanced Edition — streaming · memory · relevance guard · cost tracking*
    """)

    with gr.Tabs():

        # ── Tab 1: Chat ────────────────────────────────────
        with gr.TabItem("💬 Chat"):
            chatbot = gr.Chatbot(
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

            hyde_checkbox = gr.Checkbox(
                label="🔬 Use HyDE (Hypothetical Document Embedding)",
                value=False,
                info="GPT first generates a hypothetical answer, then searches using its embedding. More powerful but costs extra tokens.",
            )

            with gr.Row():
                clear_chat = gr.Button("🗑️ Clear Chat", scale=1)
                with gr.Column(scale=4):
                    token_display = gr.Markdown("")

            with gr.Accordion("🔬 HyDE — Hypothetical Document", open=False):
                hyde_display = gr.Markdown(
                    "_Enable HyDE and ask a question to see the hypothetical document used for retrieval._"
                )

            msg.submit(answer_question, [msg, chatbot, hyde_checkbox], [chatbot, token_display, hyde_display]).then(
                lambda: "", outputs=msg
            )
            send_btn.click(answer_question, [msg, chatbot, hyde_checkbox], [chatbot, token_display, hyde_display]).then(
                lambda: "", outputs=msg
            )
            clear_chat.click(lambda: ([], "", ""), outputs=[chatbot, token_display, hyde_display])


        # ── Tab 2: Upload ──────────────────────────────────
        with gr.TabItem("📁 Upload Documents"):
            gr.Markdown("### Add documents to the knowledge base")

            file_upload = gr.File(
                label="Upload Document",
                file_types=[".pdf", ".txt", ".md", ".docx"],
                file_count="single",
            )
            ingest_btn = gr.Button("⬆️ Ingest Document", variant="primary")
            ingest_status = gr.Markdown()

            ingest_btn.click(ingest_file, file_upload, ingest_status)

            gr.Markdown("""
            **Supported:** PDF, TXT, Markdown, DOCX

            Each document is:
            1. Split into chunks (~1000 chars with 200-char overlap)
            2. Embedded with OpenAI `text-embedding-3-small`
            3. Stored in ChromaDB for fast semantic search
            """)

        # ── Tab 3: Stats ───────────────────────────────────
        with gr.TabItem("📊 Stats"):
            stats_output = gr.Markdown()
            with gr.Row():
                refresh_btn = gr.Button("🔄 Refresh")
                clear_db_btn = gr.Button("🗑️ Clear Database", variant="stop")
            clear_status = gr.Markdown()

            refresh_btn.click(get_stats, outputs=stats_output)
            clear_db_btn.click(clear_database, outputs=clear_status)
            app.load(get_stats, outputs=stats_output)

        # ── Tab 4: Settings ────────────────────────────────
        with gr.TabItem("⚙️ Settings"):
            gr.Markdown("### Customize the bot's behaviour")

            system_prompt_box = gr.Textbox(
                value=QA_SYSTEM_PROMPT,
                label="System Prompt",
                lines=8,
                info="Controls how the assistant responds. Changes apply immediately.",
            )

            with gr.Row():
                apply_btn = gr.Button("✅ Apply", variant="primary")
                reset_btn = gr.Button("↩️ Reset to Default")

            prompt_status = gr.Markdown()

            apply_btn.click(apply_system_prompt, system_prompt_box, prompt_status)
            reset_btn.click(reset_system_prompt, outputs=[system_prompt_box, prompt_status])

            gr.Markdown("""
            ---
            ### 💡 Example Personas

            **Formal / Academic**
            > You are a scholarly assistant. Provide detailed, well-cited answers based strictly on the provided context. Always mention which source contains the information.

            **Brief & Direct**
            > You are a concise assistant. Answer in 1-2 sentences using only the context provided. Cite the source as [Source N].

            **Socratic Tutor**
            > You are a Socratic tutor. Instead of giving direct answers, ask guiding questions that lead the student to discover the answer themselves, using only the context.

            **Custom Domain (e.g. Legal)**
            > You are a legal document assistant. Answer questions about the provided legal texts accurately. Always caveat that your answers are not legal advice.
            """)

    gr.Markdown("""
    ---
    **💡 How it works:** Chunking → Embedding → Vector Search → LLM Generation
    """)


if __name__ == "__main__":
    app.launch(share=False, theme=gr.themes.Soft())
