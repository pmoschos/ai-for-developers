"""
Example 4: Interactive Events (Buttons & State)
================================================
Using gr.Blocks for more control over layout and events.

Concepts:
    - gr.Blocks instead of gr.Interface (more flexibility)
    - gr.Button with .click() events
    - gr.State for keeping data between interactions
    - Live updates with .change()

Run:  python 04_interactive_events.py
"""

import gradio as gr


def add_item(item: str, current_list: list):
    """Add an item to the shopping list."""
    if not item.strip():
        return current_list, format_list(current_list), "⚠️ Type something first!"

    current_list = current_list + [item.strip()]  # don't mutate the original
    return current_list, format_list(current_list), f"✅ Added: {item}"


def clear_list():
    """Clear the entire list."""
    return [], "🛒 *Your list is empty*", "🗑️ List cleared!"


def format_list(items: list) -> str:
    """Format the list as markdown."""
    if not items:
        return "🛒 *Your list is empty*"

    lines = [f"{i+1}. {item}" for i, item in enumerate(items)]
    return "### 🛒 Shopping List\n" + "\n".join(lines) + f"\n\n**Total: {len(items)} items**"


# gr.Blocks gives you full control over layout
with gr.Blocks(title="🛒 Shopping List") as demo:
    gr.Markdown("# 🛒 Interactive Shopping List")
    gr.Markdown("Learn how **Buttons**, **State**, and **Events** work in Gradio.")

    # gr.State stores data between interactions (invisible to the user)
    shopping_list = gr.State([])

    with gr.Row():
        item_input = gr.Textbox(
            label="Add Item",
            placeholder="Type an item and click Add...",
            scale=3,
        )
        add_btn = gr.Button("➕ Add", variant="primary", scale=1)

    clear_btn = gr.Button("🗑️ Clear All", variant="secondary")

    list_display = gr.Markdown("🛒 *Your list is empty*")
    status = gr.Textbox(label="Status", interactive=False)

    # Wire up events:
    # Button click → calls add_item(input_text, current_state) → updates [state, display, status]
    add_btn.click(
        fn=add_item,
        inputs=[item_input, shopping_list],
        outputs=[shopping_list, list_display, status],
    )

    # Also add on Enter key press
    item_input.submit(
        fn=add_item,
        inputs=[item_input, shopping_list],
        outputs=[shopping_list, list_display, status],
    )

    clear_btn.click(
        fn=clear_list,
        inputs=[],
        outputs=[shopping_list, list_display, status],
    )


if __name__ == "__main__":
    # demo.launch(share=True)
    demo.launch()
