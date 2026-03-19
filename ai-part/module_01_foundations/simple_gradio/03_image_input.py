"""
Example 3: Image & File Inputs
===============================
Working with non-text inputs: images and files.

Concepts:
    - gr.Image input/output
    - PIL image processing
    - Real-time preview with live=True

Run:  python 03_image_input.py
"""

import gradio as gr
from PIL import Image, ImageFilter


def process_image(image, effect: str):
    """Apply a visual effect to an uploaded image."""
    if image is None:
        return None, "Please upload an image first!"

    # Convert to PIL Image (Gradio gives us a numpy array by default)
    img = Image.fromarray(image)

    if effect == "Blur":
        result = img.filter(ImageFilter.GaussianBlur(radius=5))
    elif effect == "Sharpen":
        result = img.filter(ImageFilter.SHARPEN)
    elif effect == "Edges":
        result = img.filter(ImageFilter.FIND_EDGES)
    elif effect == "Grayscale":
        result = img.convert("L")
    else:
        result = img

    info = f"**Original:** {img.size[0]}×{img.size[1]}px | **Effect:** {effect}"
    return result, info


demo = gr.Interface(
    fn=process_image,
    inputs=[
        gr.Image(label="Upload an Image"),
        gr.Radio(
            choices=["Blur", "Sharpen", "Edges", "Grayscale"],
            value="Blur",
            label="Effect",
        ),
    ],
    outputs=[
        gr.Image(label="Result"),
        gr.Markdown(label="Info"),
    ],
    title="🖼️ Image Effects",
    description="Upload an image and apply a filter!",
    flagging_mode="never",
)

if __name__ == "__main__":
    demo.launch()
