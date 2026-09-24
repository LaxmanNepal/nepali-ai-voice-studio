from __future__ import annotations

import tempfile
import gradio as gr
import soundfile as sf
from .config import BACKENDS


def _generate_chatterbox(text, reference_audio, exaggeration, temperature, cfg_weight):
    from backends.chatterbox_nepali import ChatterboxNepaliEngine
    engine = ChatterboxNepaliEngine()
    wav, sample_rate = engine.generate(text=text, reference_audio=reference_audio, exaggeration=exaggeration, temperature=temperature, cfg_weight=cfg_weight)
    output = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    output.close()
    sf.write(output.name, wav.squeeze().numpy(), sample_rate)
    return output.name


def generate(text, backend, reference_audio, exaggeration, temperature, cfg_weight):
    if not text or not text.strip():
        raise gr.Error("Please enter text.")
    if backend == "chatterbox_nepali":
        try:
            return _generate_chatterbox(text, reference_audio, exaggeration, temperature, cfg_weight)
        except Exception as exc:
            raise gr.Error(str(exc)) from exc
    raise gr.Error(f"{BACKENDS[backend].name} is listed but its isolated backend is not enabled yet.")


def build_ui():
    with gr.Blocks(title="🇳🇵 Nepali AI Voice Studio") as demo:
        gr.Markdown("# 🇳🇵 Nepali AI Voice Studio")
        gr.Markdown("Unified Nepali TTS and voice-cloning interface.")
        backend = gr.Dropdown(choices=[(v.name, k) for k, v in BACKENDS.items()], value="chatterbox_nepali", label="Model")
        text = gr.Textbox(label="Nepali Text", placeholder="नमस्ते! मेरो नाम लक्ष्मण हो। नेपाल सुन्दर देश हो।", lines=6)
        reference = gr.Audio(label="Reference Voice (5–10 seconds)", type="filepath", sources=["upload", "microphone"])
        with gr.Row():
            exaggeration = gr.Slider(0, 1, value=0.5, step=0.05, label="Exaggeration")
            temperature = gr.Slider(0.1, 1.5, value=0.8, step=0.05, label="Temperature")
            cfg_weight = gr.Slider(0, 2, value=0.5, step=0.05, label="CFG Weight")
        generate_button = gr.Button("🔊 Generate Nepali Speech", variant="primary")
        output = gr.Audio(label="Generated Audio", type="filepath")
        generate_button.click(generate, [text, backend, reference, exaggeration, temperature, cfg_weight], output)
    return demo


if __name__ == "__main__":
    build_ui().launch()
