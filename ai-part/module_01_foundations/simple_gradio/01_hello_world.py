"""
Example 1: Hello World
======================
The simplest Gradio app — one input, one output.

Run:  python 01_hello_world.py
Then open http://127.0.0.1:7860 in your browser.


https://www.gradio.app/

"""

import gradio as gr


def greet(name):
    return f"Hello, {name}! 👋 Welcome to Gradio!"


# gr.Interface is the easiest way to create a UI:
#   fn      = the Python function to call
#   inputs  = what the user provides  (here: a text box)
#   outputs = what we show back       (here: a text box)
demo = gr.Interface(
    fn=greet,
    inputs=gr.Textbox(label="Your Name", placeholder="Type your name..."),
    outputs=gr.Textbox(label="Greeting"),
    title="👋 Hello World",
    description="Type your name and get a greeting!",
    flagging_mode="never",
)

if __name__ == "__main__":
    demo.launch()
