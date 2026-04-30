"""
Module 3: AI API Playground - Gradio UI (API-Backed)
=====================================================
Same interactive playground as gradio_app.py, but all calls
go through the FastAPI backend at http://localhost:8000
instead of calling OpenAI directly.

Prerequisites:
    1. Start the API server:  python run.py
    2. Then launch this UI:   python gradio_api_app.py

Usage:
    python gradio_api_app.py
"""

import json
import httpx
import gradio as gr

API_BASE = "http://localhost:8000"
TIMEOUT = 60.0  # seconds — LLM calls can be slow


# ==================== API FUNCTIONS ====================

def summarize(text: str, style: str, max_length: int):
    """Call POST /summarize on the FastAPI backend"""
    if not text.strip():
        return "Please enter some text to summarize."

    try:
        r = httpx.post(
            f"{API_BASE}/summarize",
            json={
                "text": text,
                "max_length": int(max_length),
                "style": style,
            },
            timeout=TIMEOUT,
        )
        r.raise_for_status()
        data = r.json()

        summary = data["summary"]
        original = data["original_length"]
        summary_len = data["summary_length"]
        ratio = data["compression_ratio"]
        tokens = data["tokens_used"]
        cost = data["estimated_cost"]

        return (
            f"{summary}\n\n---\n"
            f"📊 *Original: {original} words → Summary: {summary_len} words "
            f"({ratio*100:.1f}% compression)*\n"
            f"🔢 *Tokens: {tokens} | Cost: ${cost:.6f}*"
        )
    except httpx.HTTPStatusError as e:
        return f"❌ API Error ({e.response.status_code}): {e.response.text}"
    except httpx.ConnectError:
        return "❌ Cannot connect to API. Is the server running? (`python run.py`)"
    except Exception as e:
        return f"❌ Error: {e}"


def analyze_sentiment(text: str, include_reasoning: bool):
    """Call POST /sentiment on the FastAPI backend"""
    if not text.strip():
        return "Please enter some text to analyze."

    try:
        r = httpx.post(
            f"{API_BASE}/sentiment",
            json={
                "text": text,
                "include_reasoning": include_reasoning,
            },
            timeout=TIMEOUT,
        )
        r.raise_for_status()
        data = r.json()

        sentiment = data["sentiment"].upper()
        confidence = data["confidence"]
        tokens = data["tokens_used"]
        cost = data["estimated_cost"]

        result = f"SENTIMENT: {sentiment}\nCONFIDENCE: {confidence*100:.0f}%"
        if data.get("reasoning"):
            result += f"\nREASONING: {data['reasoning']}"
        result += f"\n\n🔢 Tokens: {tokens} | Cost: ${cost:.6f}"
        return result

    except httpx.HTTPStatusError as e:
        return f"❌ API Error ({e.response.status_code}): {e.response.text}"
    except httpx.ConnectError:
        return "❌ Cannot connect to API. Is the server running? (`python run.py`)"
    except Exception as e:
        return f"❌ Error: {e}"


def generate_copy(product: str, description: str, tone: str, audience: str, variants: int):
    """Call POST /copywriter on the FastAPI backend"""
    if not product.strip():
        return "Please enter a product name."

    # Map Gradio dropdown values to API enum values
    tone_map = {"luxury": "luxurious"}
    api_tone = tone_map.get(tone, tone)

    try:
        r = httpx.post(
            f"{API_BASE}/copywriter",
            json={
                "product_name": product,
                "description": description or "A great product",
                "tone": api_tone,
                "target_audience": audience or "general consumers",
                "num_variants": int(variants),
            },
            timeout=TIMEOUT,
        )
        r.raise_for_status()
        data = r.json()

        tokens = data["tokens_used"]
        cost = data["estimated_cost"]

        output = ""
        for i, v in enumerate(data["variants"], 1):
            output += f"### Variant {i}\n"
            output += f"**{v['headline']}**\n\n"
            output += f"{v['body']}\n\n"
            output += f"🔘 *CTA: {v['cta']}*\n\n---\n\n"

        output += f"🔢 *Tokens: {tokens} | Cost: ${cost:.6f}*"
        return output

    except httpx.HTTPStatusError as e:
        return f"❌ API Error ({e.response.status_code}): {e.response.text}"
    except httpx.ConnectError:
        return "❌ Cannot connect to API. Is the server running? (`python run.py`)"
    except Exception as e:
        return f"❌ Error: {e}"


def stream_response(prompt: str, system_prompt: str):
    """Call POST /stream (SSE) on the FastAPI backend, yielding tokens progressively"""
    if not prompt.strip():
        yield "Please enter a prompt."
        return

    payload = {"prompt": prompt, "max_tokens": 500}
    if system_prompt.strip():
        payload["system_prompt"] = system_prompt

    try:
        with httpx.stream(
            "POST",
            f"{API_BASE}/stream",
            json=payload,
            timeout=TIMEOUT,
        ) as r:
            r.raise_for_status()
            full_response = ""
            for line in r.iter_lines():
                if line.startswith("data: "):
                    try:
                        data = json.loads(line[6:])
                        if data.get("content"):
                            full_response += data["content"]
                            yield full_response
                        if data.get("error"):
                            yield f"{full_response}\n\n❌ Stream error: {data['error']}"
                            return
                    except json.JSONDecodeError:
                        continue

    except httpx.ConnectError:
        yield "❌ Cannot connect to API. Is the server running? (`python run.py`)"
    except Exception as e:
        yield f"❌ Error: {e}"


# ==================== GRADIO APP ====================

with gr.Blocks(title="🚀 AI API Playground", theme=gr.themes.Soft()) as app:
    gr.Markdown("""
    # 🚀 AI API Playground
    
    Test the AI-powered API endpoints interactively!
    
    **Module 3: AI Architecture Stack** — *API-backed version (calls FastAPI at localhost:8000)*
    """)

    with gr.Tabs():
        # Summarization Tab
        with gr.TabItem("📝 Summarization"):
            gr.Markdown("### Condense text into key points")

            with gr.Row():
                with gr.Column():
                    sum_text = gr.Textbox(
                        label="Text to Summarize",
                        placeholder="Paste a long article or document here...",
                        lines=8
                    )
                    with gr.Row():
                        sum_style = gr.Dropdown(
                            choices=["concise", "detailed", "bullet_points"],
                            value="concise",
                            label="Style"
                        )
                        sum_length = gr.Slider(
                            minimum=50, maximum=500, value=150,
                            label="Max Words"
                        )
                    sum_btn = gr.Button("Summarize", variant="primary")

                with gr.Column():
                    sum_output = gr.Markdown(label="Summary")

            sum_btn.click(summarize, [sum_text, sum_style, sum_length], sum_output)

        # Sentiment Tab
        with gr.TabItem("😊 Sentiment Analysis"):
            gr.Markdown("### Analyze the emotional tone of text")

            with gr.Row():
                with gr.Column():
                    sent_text = gr.Textbox(
                        label="Text to Analyze",
                        placeholder="Enter text to analyze sentiment...",
                        lines=4
                    )
                    sent_reasoning = gr.Checkbox(
                        label="Include reasoning",
                        value=True
                    )
                    sent_btn = gr.Button("Analyze", variant="primary")

                    gr.Examples(
                        examples=[
                            ["I absolutely love this product! Best purchase ever!"],
                            ["This is the worst experience I've ever had."],
                            ["The meeting was okay, nothing special."],
                            ["I'm excited but also a bit nervous about the change."]
                        ],
                        inputs=[sent_text]
                    )

                with gr.Column():
                    sent_output = gr.Textbox(label="Analysis", lines=6)

            sent_btn.click(analyze_sentiment, [sent_text, sent_reasoning], sent_output)

        # Copywriting Tab
        with gr.TabItem("✍️ Copywriting"):
            gr.Markdown("### Generate marketing copy variants")

            with gr.Row():
                with gr.Column():
                    copy_product = gr.Textbox(label="Product Name")
                    copy_desc = gr.Textbox(
                        label="Product Description",
                        placeholder="Describe the product and its benefits...",
                        lines=3
                    )
                    with gr.Row():
                        copy_tone = gr.Dropdown(
                            choices=["professional", "casual", "luxurious", "playful", "urgent"],
                            value="professional",
                            label="Tone"
                        )
                        copy_audience = gr.Textbox(
                            label="Target Audience",
                            value="general consumers"
                        )
                    copy_variants = gr.Slider(
                        minimum=1, maximum=5, value=3, step=1,
                        label="Number of Variants"
                    )
                    copy_btn = gr.Button("Generate Copy", variant="primary")

                with gr.Column():
                    copy_output = gr.Markdown(label="Generated Copy")

            copy_btn.click(
                generate_copy,
                [copy_product, copy_desc, copy_tone, copy_audience, copy_variants],
                copy_output
            )

        # Streaming Tab
        with gr.TabItem("⚡ Streaming"):
            gr.Markdown("### Watch responses generate in real-time")

            stream_system = gr.Textbox(
                label="System Prompt (optional)",
                placeholder="e.g., You are a helpful pirate assistant",
                lines=2
            )
            stream_prompt = gr.Textbox(
                label="Your Prompt",
                placeholder="Ask anything...",
                lines=2
            )
            stream_btn = gr.Button("Generate (Streaming)", variant="primary")
            stream_output = gr.Textbox(label="Response", lines=10)

            stream_btn.click(
                stream_response,
                [stream_prompt, stream_system],
                stream_output
            )

    gr.Markdown("""
    ---
    ### 💡 Learning Points
    
    1. **This UI calls the FastAPI backend** — not OpenAI directly
    2. **Summarize, Sentiment, Copywriter** use standard POST requests
    3. **Streaming** uses Server-Sent Events (SSE) for real-time output
    4. **Cost & token tracking** is handled by the backend middleware
    
    API Swagger docs: [http://localhost:8000/docs](http://localhost:8000/docs)
    """)


if __name__ == "__main__":
    app.launch(share=False)
