from __future__ import annotations

import tempfile
from pathlib import Path

import gradio as gr
import soundfile as sf

from .config import BACKENDS
from .diagnostics import backend_status, smoke_test

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


def _validate_reference(reference_audio):
    if not reference_audio:
        raise gr.Error("Please provide a consented reference voice recording.")

    path = Path(reference_audio)
    if not path.exists():
        raise gr.Error("Reference audio file could not be found.")

    try:
        info = sf.info(str(path))
    except Exception as exc:
        raise gr.Error(
            "Reference audio could not be read. Please upload a WAV, FLAC, "
            "or another supported audio file."
        ) from exc

    if info.frames == 0 or info.duration <= 0:
        raise gr.Error("Reference audio is empty.")
    if info.duration < 2:
        raise gr.Error("Please use a clear reference recording of at least 2 seconds.")
    if info.duration > 30:
        raise gr.Error("Please keep the reference recording under 30 seconds.")

    return str(path)


def generate(
    text,
    backend,
    reference_audio,
    exaggeration,
    temperature,
    cfg_weight,
    repetition_penalty,
):
    if not text or not text.strip():
        raise gr.Error("Please enter Nepali text.")

    reference_audio = _validate_reference(reference_audio)

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
                text,
                reference_audio,
                temperature=temperature,
                repetition_penalty=repetition_penalty,
            )
        elif backend == "pocket_tts":
            wav, sample_rate = engine.generate(text, reference_audio)
        else:
            raise ValueError(f"Unsupported backend: {backend}")

        return _write_wav(wav, sample_rate)
    except gr.Error:
        raise
    except Exception as exc:
        name = BACKENDS.get(backend).name if backend in BACKENDS else backend
        raise gr.Error(f"{name}: {exc}") from exc


def _diagnostic_rows():
    return [
        [row["name"], row["dependency"], row["installed"], row["access"]]
        for row in backend_status()
    ]


def _smoke_result(status):
    if status["status"] == "PASS":
        return f"✅ **PASS** — {status['message']}"
    if status["status"] == "BLOCKED":
        return f"🟡 **BLOCKED** — {status['message']}"
    return f"❌ **FAIL** — {status['message']}"


def build_ui():
    with gr.Blocks(title="🇳🇵 Nepali AI Voice Studio") as demo:
        gr.Markdown("# 🇳🇵 Nepali AI Voice Studio")
        gr.Markdown(
            "Generate Nepali speech with isolated voice models. "
            "Use only voices you own or have informed permission to clone."
        )

        with gr.Row():
            backend = gr.Dropdown(
                choices=[(v.name, k) for k, v in BACKENDS.items()],
                value="chatterbox_nepali",
                label="Model",
                scale=2,
            )
            gr.Markdown(
                "**Tip:** Chatterbox and XTTS use the advanced controls below. "
                "Swarlekha and Pocket-TTS use their documented defaults.",
                scale=3,
            )

        text = gr.Textbox(
            label="Nepali Text",
            placeholder="नमस्ते! मेरो नाम लक्ष्मण हो। नेपाल सुन्दर देश हो।",
            lines=7,
        )

        reference = gr.Audio(
            label="Reference Voice — 3–10 seconds recommended",
            type="filepath",
            sources=["upload", "microphone"],
        )

        consent = gr.Checkbox(
            label="I own this voice or have informed permission to clone it.",
            value=False,
        )

        with gr.Accordion("Advanced generation controls", open=False):
            with gr.Row():
                exaggeration = gr.Slider(0, 1, value=0.5, step=0.05, label="Chatterbox Exaggeration")
                temperature = gr.Slider(0.1, 1.5, value=0.65, step=0.05, label="Temperature")
            with gr.Row():
                cfg_weight = gr.Slider(0, 2, value=0.5, step=0.05, label="Chatterbox CFG Weight")
                repetition_penalty = gr.Slider(1, 8, value=5.0, step=0.1, label="XTTS Repetition Penalty")

        generate_button = gr.Button("🔊 Generate Nepali Speech", variant="primary")
        output = gr.Audio(label="Generated Audio", type="filepath")

        def guarded_generate(*args):
            text_value, backend_value, reference_value, consent_value, *controls = args
            if not consent_value:
                raise gr.Error(
                    "Please confirm that you own the voice or have informed permission to clone it."
                )
            return generate(text_value, backend_value, reference_value, *controls)

        generate_button.click(
            guarded_generate,
            [text, backend, reference, consent, exaggeration, temperature, cfg_weight, repetition_penalty],
            output,
        )

        with gr.Accordion("🩺 Backend diagnostics", open=False):
            diagnostics = gr.Dataframe(
                headers=["Backend", "Dependency", "Installed", "Access"],
                datatype=["str", "str", "str", "str"],
                value=_diagnostic_rows(),
                interactive=False,
                label="Local readiness check",
            )
            refresh = gr.Button("🔄 Refresh diagnostics")
            refresh.click(_diagnostic_rows, outputs=diagnostics)

            gr.Markdown(
                "Run a real smoke test below after uploading the same consented reference voice. "
                "The test downloads/loads the selected model and generates a short Nepali sentence."
            )
            smoke_backend = gr.Dropdown(
                choices=[(v.name, k) for k, v in BACKENDS.items()],
                value="chatterbox_nepali",
                label="Backend to test",
            )
            smoke_reference = gr.Audio(
                label="Consented reference voice for smoke test",
                type="filepath",
                sources=["upload", "microphone"],
            )
            smoke_button = gr.Button("🧪 Test selected model")
            smoke_output = gr.Markdown()
            smoke_button.click(
                lambda b, r: _smoke_result(smoke_test(b, r)),
                [smoke_backend, smoke_reference],
                smoke_output,
            )

        gr.Markdown(
            "⚠️ **Responsible use:** Do not use this tool for impersonation, "
            "fraud, deception, or to present synthetic speech as an authentic recording."
        )

    return demo


if __name__ == "__main__":
    build_ui().launch()
