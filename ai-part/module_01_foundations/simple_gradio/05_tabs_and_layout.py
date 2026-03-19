"""
Example 5: Tabs & Layout
=========================
Organize your app with Tabs, Rows, and Columns.

Concepts:
    - gr.Tabs / gr.TabItem for multi-page apps
    - gr.Row / gr.Column for layout control
    - gr.Accordion for collapsible sections
    - Combining everything into a polished app

Run:  python 05_tabs_and_layout.py
"""

import gradio as gr


# ── Tab 1 functions ──
def celsius_to_fahrenheit(c: float) -> str:
    f = (c * 9 / 5) + 32
    return f"🌡️ {c}°C = **{f:.1f}°F**"


def fahrenheit_to_celsius(f: float) -> str:
    c = (f - 32) * 5 / 9
    return f"🌡️ {f}°F = **{c:.1f}°C**"


# ── Tab 2 functions ──
def calculate_bmi(weight: float, height: float) -> str:
    if height <= 0:
        return "⚠️ Enter a valid height"
    bmi = weight / (height / 100) ** 2

    if bmi < 18.5:
        category = "Underweight"
    elif bmi < 25:
        category = "Normal ✅"
    elif bmi < 30:
        category = "Overweight"
    else:
        category = "Obese"

    return f"### BMI: {bmi:.1f}\n**Category:** {category}"


# ── Tab 3 function ──
def count_words(text: str) -> str:
    if not text.strip():
        return "Type some text above!"
    words = len(text.split())
    chars = len(text)
    lines = len(text.splitlines())
    return f"📊 **{words}** words | **{chars}** characters | **{lines}** lines"


# ── Build the app ──
with gr.Blocks(title="🧰 Multi-Tool App") as demo:
    gr.Markdown("# 🧰 Multi-Tool App")
    gr.Markdown("An app with **tabs** and **layout** — a common pattern in Gradio.")

    with gr.Tabs():
        # ── Tab 1: Temperature Converter ──
        with gr.TabItem("🌡️ Temperature"):
            gr.Markdown("### Convert temperatures")

            with gr.Row():
                with gr.Column():
                    c_input = gr.Number(label="Celsius", value=0)
                    c_btn = gr.Button("Convert to °F", variant="primary")
                    c_result = gr.Markdown()

                with gr.Column():
                    f_input = gr.Number(label="Fahrenheit", value=32)
                    f_btn = gr.Button("Convert to °C", variant="primary")
                    f_result = gr.Markdown()

            c_btn.click(celsius_to_fahrenheit, c_input, c_result)
            f_btn.click(fahrenheit_to_celsius, f_input, f_result)

        # ── Tab 2: BMI Calculator ──
        with gr.TabItem("⚖️ BMI Calculator"):
            gr.Markdown("### Calculate your Body Mass Index")

            with gr.Row():
                weight = gr.Number(label="Weight (kg)", value=70)
                height = gr.Number(label="Height (cm)", value=175)

            bmi_btn = gr.Button("Calculate BMI", variant="primary")
            bmi_result = gr.Markdown()

            bmi_btn.click(calculate_bmi, [weight, height], bmi_result)

        # ── Tab 3: Word Counter ──
        with gr.TabItem("📝 Word Counter"):
            gr.Markdown("### Count words, characters, and lines")

            text_input = gr.Textbox(
                label="Your Text",
                placeholder="Paste or type text here...",
                lines=5,
            )
            word_result = gr.Markdown()

            # live=True equivalent: update on every keystroke
            text_input.change(count_words, text_input, word_result)

    # Collapsible section at the bottom
    with gr.Accordion("💡 What did we learn?", open=False):
        gr.Markdown("""
- **`gr.Tabs`** + **`gr.TabItem`** create tabbed navigation
- **`gr.Row`** places components side by side
- **`gr.Column`** stacks components vertically (inside a Row)
- **`gr.Accordion`** creates collapsible sections
- **`.change()`** triggers on every keystroke (live updates)
        """)


if __name__ == "__main__":
    demo.launch()
