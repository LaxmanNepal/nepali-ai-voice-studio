from __future__ import annotations

import tempfile

import gradio as gr
import soundfile as sf

from .config import BACKENDS


def _write_wav(wav, sample_rate):
    output = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    output.close()
    sf.write(output.name, wav.squeeze().numpy(), sample_rate)
    return output.name


def _generate_chatterbox(text, reference_audio, exaggeration, temperature, cfg_weight):
    from backends.chatterbox_nepali import ChatterboxNepaliEngine

    engine = ChatterboxNepaliEngine()
    wav, sample_rate = engine.generate(
        text=text,
        reference_audio=reference_audio,
        exaggeration=exaggeration,
        temperature=temperature,
        cfg_weight=cfg_weight,
    )
    return _write_wav(wav, sample_rate)


def _generate_swarlekha(text, reference_audio):
    from backends.swarlekha import SwarlekhaEngine

    engine = SwarlekhaEngine()
    wav, sample_rate = engine.generate(text, reference_audio)
    return _write_wav(wav, sample_rate)


def _generate_xtts(text, reference_audio, temperature, repetition_penalty):
    from backends.xtts_nepali import XttsNepaliEngine

    engine = XttsNepaliEngine()
    wav, sample_rate = engine.generate(
        text,
        reference_audio,
        temperature=temperature,
        repetition_penalty=repetition_penalty,
    )
    return _write_wav(wav, sample_rate)


def generate(text, backend, reference_audio, exaggeration, temperature, cfg_weight, repetition_penalty):
    if not text or not text.strip():
        raise gr.Error("Please enter text.")

    try:
        if backend == "chatterbox_nepali":
            return _generate_chatterbox(
                text, reference_audio, exaggeration, temperature, cfg_weight
            )
        if backend == "swarlekha":
            return _generate_swarlekha(text, reference_audio)
        if backend == "xtts_nepali":
            return _generate_xtts(
                text, reference_audio, temperature, repetition_penalty
            )
    except Exception as exc:
        raise gr.Error(str(exc)) from exc

    raise gr.Error(
        f"{BACKENDS[backend].name} is listed but its isolated backend is not enabled yet."
    )


def build_ui():
    with gr.Blocks(title="🇳🇵 Nepali AI Voice Studio") as demo:
        gr.Markdown("# 🇳🇵 Nepali AI Voice Studio")
        gr.Markdown("Unified Nepali TTS and voice-cloning interface.")

        backend = gr.Dropdown(
            choices=[(v.name, k) for k, v in BACKENDS.items()],
            value="chatterbox_nepali",
            label="Model",
        )
        text = gr.Textbox(
            label="Nepali Text",
            placeholder="नमस्ते! मेरो नाम लक्ष्मण हो। नेपाल सुन्दर देश हो।",
            lines=6,
        )
        reference = gr.Audio(
            label="Reference Voice (5–10 seconds)",
            type="filepath",
            sources=["upload", "microphone"],
        )

        with gr.Row():
            exaggeration = gr.Slider(
                0, 1, value=0.5, step=0.05, label="Chatterbox Exaggeration"
            )
            temperature = gr.Slider(
                0.1, 1.5, value=0.65, step=0.05, label="Temperature"
            )
            cfg_weight = gr.Slider(
                0, 2, value=0.5, step=0.05, label="Chatterbox CFG Weight"
            )
            repetition_penalty = gr.Slider(
                1, 8, value=5.0, step=0.1, label="XTTS Repetition Penalty"
            )

        generate_button = gr.Button("🔊 Generate Nepali Speech", variant="primary")
        output = gr.Audio(label="Generated Audio", type="filepath")
        generate_button.click(
            generate,
            [
                text,
                backend,
                reference,
                exaggeration,
                temperature,
                cfg_weight,
                repetition_penalty,
            ],
            output,
        )
    return demo


if __name__ == "__main__":
    build_ui().launch()
