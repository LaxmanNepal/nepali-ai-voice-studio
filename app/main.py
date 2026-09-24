from __future__ import annotations

import tempfile

import gradio as gr
import soundfile as sf

from .config import BACKENDS

_ENGINES = {}


def _get_engine(backend):
    if backend not in _ENGINES:
        if backend == "chatterbox_nepali":
            from backends.chatterbox_nepali import ChatterboxNepaliEngine
            _ENGINES[backend] = ChatterboxNepaliEngine()
        elif backend == "swarlekha":
            from backends.swarlekha import SwarlekhaEngine
            _ENGINES[backend] = SwarlekhaEngine()
        elif backend == "xtts_nepali":
            from backends.xtts_nepali import XttsNepaliEngine
            _ENGINES[backend] = XttsNepaliEngine()
        elif backend == "pocket_tts":
            from backends.pocket_tts import PocketTtsNepaliEngine
            _ENGINES[backend] = PocketTtsNepaliEngine()
        else:
            raise ValueError(f"Unknown backend: {backend}")
    return _ENGINES[backend]


def _write_wav(wav, sample_rate):
    output = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    output.close()
    sf.write(output.name, wav.squeeze().numpy(), sample_rate)
    return output.name


def generate(text, backend, reference_audio, exaggeration, temperature, cfg_weight, repetition_penalty):
    if not text or not text.strip():
        raise gr.Error("Please enter text.")
    if not reference_audio:
        raise gr.Error("Please provide a consented reference voice recording.")

    try:
        engine = _get_engine(backend)

        if backend == "chatterbox_nepali":
            wav, sample_rate = engine.generate(
                text=text,
                reference_audio=reference_audio,
                exaggeration=exaggeration,
                temperature=temperature,
                cfg_weight=cfg_weight,
            )
        elif backend == "swarlekha":
            wav, sample_rate = engine.generate(text, reference_audio)
        elif backend == "xtts_nepali":
            wav, sample_rate = engine.generate(
                text, reference_audio,
                temperature=temperature,
                repetition_penalty=repetition_penalty,
            )
        elif backend == "pocket_tts":
            wav, sample_rate = engine.generate(text, reference_audio)
        else:
            raise ValueError(f"Unsupported backend: {backend}")

        return _write_wav(wav, sample_rate)
    except Exception as exc:
        raise gr.Error(str(exc)) from exc


def build_ui():
    with gr.Blocks(title="🇳🇵 Nepali AI Voice Studio") as demo:
        gr.Markdown("# 🇳🇵 Nepali AI Voice Studio")
        gr.Markdown(
            "One interface for isolated Nepali TTS and voice-cloning backends. "
            "Use only voices you own or have permission to clone."
        )

        backend = gr.Dropdown(
            choices=[(v.name, k) for k, v in BACKENDS.items()],
            value="chatterbox_nepali",
            label="Model",
        )
        text = gr.Textbox(
            label="Text",
            placeholder="नमस्ते! मेरो नाम लक्ष्मण हो। नेपाल सुन्दर देश हो।",
            lines=6,
        )
        reference = gr.Audio(
            label="Reference Voice (3–10 seconds recommended)",
            type="filepath",
            sources=["upload", "microphone"],
        )

        with gr.Row():
            exaggeration = gr.Slider(0, 1, value=0.5, step=0.05, label="Chatterbox Exaggeration")
            temperature = gr.Slider(0.1, 1.5, value=0.65, step=0.05, label="Temperature")
            cfg_weight = gr.Slider(0, 2, value=0.5, step=0.05, label="Chatterbox CFG Weight")
            repetition_penalty = gr.Slider(1, 8, value=5.0, step=0.1, label="XTTS Repetition Penalty")

        generate_button = gr.Button("🔊 Generate Nepali Speech", variant="primary")
        output = gr.Audio(label="Generated Audio", type="filepath")
        generate_button.click(
            generate,
            [text, backend, reference, exaggeration, temperature, cfg_weight, repetition_penalty],
            output,
        )
    return demo


if __name__ == "__main__":
    build_ui().launch()
