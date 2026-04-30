"""
Module 3: AI API Playground - Gradio UI
========================================
Interactive playground to test all API endpoints.

Usage:
    python gradio_app.py
"""

import os
from pathlib import Path
from dotenv import load_dotenv
import gradio as gr
from openai import OpenAI

load_dotenv(Path(__file__).parent.parent / ".env", override=True)

client = OpenAI()


# ==================== API FUNCTIONS ====================

def summarize(text: str, style: str, max_length: int):
    """Summarize text with specified style"""
    if not text.strip():
        return "Please enter some text to summarize."
    
    style_instructions = {
        "concise": "Be extremely brief, focusing only on key points.",
        "detailed": "Provide a thorough summary with important details.",
        "bullet_points": "Format the summary as bullet points.",
        "executive": "Write an executive summary suitable for leadership."
    }
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": f"You are an expert summarizer. {style_instructions.get(style, '')} "
                          f"Keep the summary under {max_length} words."
            },
            {"role": "user", "content": f"Summarize this text:\n\n{text}"}
        ],
        max_tokens=500
    )
    
    summary = response.choices[0].message.content
    original_words = len(text.split())
    summary_words = len(summary.split())
    compression = f"{(1 - summary_words/original_words)*100:.1f}%"
    
    return f"{summary}\n\n---\n📊 *Original: {original_words} words → Summary: {summary_words} words ({compression} compression)*"


def analyze_sentiment(text: str, include_reasoning: bool):
    """Analyze sentiment of text"""
    if not text.strip():
        return "Please enter some text to analyze."
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": """Analyze the sentiment of the text. 
                Return your analysis in this format:
                SENTIMENT: [positive/negative/neutral/mixed]
                CONFIDENCE: [0-100]%
                """ + ("REASONING: [brief explanation]" if include_reasoning else "")
            },
            {"role": "user", "content": text}
        ],
        max_tokens=200
    )
    
    return response.choices[0].message.content


def generate_copy(product: str, description: str, tone: str, audience: str, variants: int):
    """Generate marketing copy variants"""
    if not product.strip():
        return "Please enter a product name."
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": f"""You are an expert copywriter. Generate {variants} different marketing copy variants.
                
Tone: {tone}
Target Audience: {audience}

Format each variant clearly numbered."""
            },
            {
                "role": "user",
                "content": f"Product: {product}\n\nDescription: {description}"
            }
        ],
        max_tokens=800
    )
    
    return response.choices[0].message.content


def stream_response(prompt: str, system_prompt: str):
    """Stream a response token by token"""
    if not prompt.strip():
        yield "Please enter a prompt."
        return
    
    messages = []
    if system_prompt.strip():
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})
    
    stream = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        stream=True,
        max_tokens=500
    )
    
    full_response = ""
    for chunk in stream:
        if chunk.choices[0].delta.content:
            full_response += chunk.choices[0].delta.content
            yield full_response


# ==================== GRADIO APP ====================

with gr.Blocks(title="🚀 AI API Playground", theme=gr.themes.Soft()) as app:
    gr.Markdown("""
    # 🚀 AI API Playground
    
    Test the AI-powered API endpoints interactively!
    
    **Module 3: AI Architecture Stack**
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
                            choices=["concise", "detailed", "bullet_points", "executive"],
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
                            choices=["professional", "casual", "luxury", "playful", "urgent"],
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
    
    1. **Different endpoints** serve different use cases
    2. **Parameters** like style, tone, and audience affect output
    3. **Streaming** improves perceived latency
    4. This UI could be the frontend for your FastAPI backend!
    
    Try running the actual FastAPI server: `python run.py`
    """)


if __name__ == "__main__":
    app.launch(share=False)
