"""
Example 2: Multiple Inputs & Outputs
=====================================
A Gradio app with several input types and multiple outputs.

Concepts:
    - Different input types: Textbox, Slider, Dropdown
    - Multiple return values → multiple outputs
    - gr.Interface with lists of inputs/outputs

Run:  python 02_multiple_inputs.py
"""

import gradio as gr


def build_profile(name: str, age: int, language: str):
    """Build a profile card from user inputs."""
    # Output 1: a formatted profile card
    profile = f"""### 📇 Profile Card
- **Name:** {name}
- **Age:** {age}
- **Language:** {language}
- **Status:** {"Student 🎓" if age < 25 else "Professional 💼"}
"""

    # Output 2: a fun fact based on age
    fun_fact = f"{name} has been alive for approximately {age * 365:,} days!"

    return profile, fun_fact


demo = gr.Interface(
    fn=build_profile,
    inputs=[
        gr.Textbox(label="Name", placeholder="Enter your name"),
        gr.Slider(minimum=10, maximum=100, value=20, step=1, label="Age"),
        gr.Dropdown(
            choices=["Python", "JavaScript", "Java", "C++", "Go"],
            value="Python",
            label="Favorite Language",
        ),
    ],
    outputs=[
        gr.Markdown(label="Profile Card"),
        gr.Textbox(label="Fun Fact"),
    ],
    title="📇 Profile Builder",
    description="Enter your details and get a profile card!",
    flagging_mode="never",
)

if __name__ == "__main__":
    demo.launch()
