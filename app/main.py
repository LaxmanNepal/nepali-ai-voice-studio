import gradio as gr
from .config import BACKENDS

def placeholder_generate(text, backend, reference_audio):
    if not text or not text.strip():
        raise gr.Error("Please enter text.")
    raise gr.Error(
        f"{BACKENDS[backend].name} backend is not enabled yet. "
        "The adapter will be added in the next implementation stage."
    )

def build_ui():
    with gr.Blocks(title="🇳🇵 Nepali AI Voice Studio") as demo:
        gr.Markdown("# 🇳🇵 Nepali AI Voice Studio")
        gr.Markdown("Unified Nepali TTS and voice-cloning interface.")

        backend = gr.Dropdown(
            choices=[(v.name, k) for k, v in BACKENDS.items()],
            value="swarlekha",
            label="Model"
        )
        text = gr.Textbox(
            label="Text",
            placeholder="नमस्ते! मेरो नाम लक्ष्मण हो।",
            lines=6
        )
        reference = gr.Audio(
            label="Reference Voice",
            type="filepath",
            sources=["upload", "microphone"]
        )
        generate = gr.Button("🔊 Generate Speech", variant="primary")
        output = gr.Audio(label="Generated Audio")

        generate.click(
            placeholder_generate,
            [text, backend, reference],
            output
        )

    return demo

if __name__ == "__main__":
    build_ui().launch()
