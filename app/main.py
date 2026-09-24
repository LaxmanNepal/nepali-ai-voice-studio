from __future__ import annotations

import time
from pathlib import Path

import gradio as gr
import soundfile as sf

from .config import BACKENDS
from .diagnostics import backend_status, smoke_test
from .runtime import engine_lock, log_generation_done, log_generation_error, log_generation_start, output_path, runtime_summary

_ENGINES = {}
MAX_TEXT_CHARS = 2500


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
    path = output_path(".wav")
    sf.write(path, wav.squeeze().numpy(), sample_rate)
    return path


def _validate_reference(reference_audio):
    if not reference_audio:
        raise gr.Error("Please provide a consented reference voice recording.")
    path = Path(reference_audio)
    if not path.exists():
        raise gr.Error("Reference audio file could not be found.")
    try:
        info = sf.info(str(path))
    except Exception as exc:
        raise gr.Error("Reference audio could not be read. Upload WAV, FLAC, or another supported file.") from exc
    if info.frames == 0 or info.duration <= 0:
        raise gr.Error("Reference audio is empty.")
    if info.duration < 2:
        raise gr.Error("Please use a clear reference recording of at least 2 seconds.")
    if info.duration > 30:
        raise gr.Error("Please keep the reference recording under 30 seconds.")
    return str(path)


def _validate_text(text):
    value = (text or "").replace("\ufeff", "").replace("\u200b", "").strip()
    if not value:
        raise gr.Error("Please enter Nepali text.")
    if len(value) > MAX_TEXT_CHARS:
        raise gr.Error(f"Text is too long. Keep each generation under {MAX_TEXT_CHARS} characters.")
    return value


def _generate_with_engine(backend, text, reference_audio, exaggeration, temperature, cfg_weight, repetition_penalty):
    engine = _get_engine(backend)
    if backend == "chatterbox_nepali":
        return engine.generate(text=text, reference_audio=reference_audio, exaggeration=exaggeration,
                               temperature=temperature, cfg_weight=cfg_weight)
    if backend == "swarlekha":
        return engine.generate(text, reference_audio)
    if backend == "xtts_nepali":
        return engine.generate(text, reference_audio, temperature=temperature,
                               repetition_penalty=repetition_penalty)
    if backend == "pocket_tts":
        return engine.generate(text, reference_audio)
    raise ValueError(f"Unsupported backend: {backend}")


def generate(text, backend, reference_audio, exaggeration, temperature, cfg_weight, repetition_penalty):
    text = _validate_text(text)
    reference_audio = _validate_reference(reference_audio)
    started = time.perf_counter()
    log_generation_start(backend, len(text))
    try:
        with engine_lock(backend):
            wav, sample_rate = _generate_with_engine(
                backend, text, reference_audio, exaggeration, temperature, cfg_weight, repetition_penalty
            )
        result = _write_wav(wav, sample_rate)
        log_generation_done(backend, time.perf_counter() - started)
        return result
    except gr.Error:
        raise
    except Exception as exc:
        log_generation_error(backend, exc)
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


def _model_rows():
    return [
        [v.name, v.description, ", ".join(v.languages).upper(), v.license, v.hardware, v.access]
        for v in BACKENDS.values()
    ]


def build_ui():
    css = """
    .studio-hero { padding: 1rem 0 .5rem; }
    .studio-note { border-radius: 12px; }
    .model-card { min-height: 90px; padding: .75rem; border-radius: 12px; }
    """
    with gr.Blocks(title="🇳🇵 Nepali AI Voice Studio", css=css) as demo:
        gr.Markdown(
            "# 🇳🇵 Nepali AI Voice Studio\n"
            "One interface for four isolated Nepali voice backends. "
            "Use only a voice you own or have informed permission to clone."
        )

        with gr.Tabs():
            with gr.Tab("🎙️ Generate"):
                with gr.Row():
                    backend = gr.Dropdown(
                        choices=[(v.name, k) for k, v in BACKENDS.items()],
                        value="chatterbox_nepali", label="Model", scale=2
                    )
                    gr.Markdown(
                        "**Workflow:** choose a model → enter Nepali text → add reference voice → confirm consent → generate.",
                        scale=3
                    )
                backend_info = gr.Markdown("**Selected model:** Chatterbox Nepali · MIT · GPU recommended · gated Hugging Face model")
                backend.change(lambda b: "**Selected model:** {} · {} · {} · {}".format(BACKENDS[b].name, BACKENDS[b].license, BACKENDS[b].hardware, BACKENDS[b].access), backend, backend_info)
                text = gr.Textbox(
                    label="Nepali text",
                    placeholder="नमस्ते! मेरो नाम लक्ष्मण हो। नेपाल सुन्दर देश हो।",
                    lines=7,
                    max_lines=12,
                )
                char_count = gr.Markdown("0 / 2500 characters")
                text.input(lambda x: f"{len(x or '')} / {MAX_TEXT_CHARS} characters", text, char_count)

                reference = gr.Audio(
                    label="Reference Voice — 3–10 seconds recommended",
                    type="filepath", sources=["upload", "microphone"]
                )
                consent = gr.Checkbox(
                    label="I own this voice or have informed permission to clone it.", value=False
                )

                with gr.Accordion("Advanced generation controls", open=False):
                    with gr.Row():
                        exaggeration = gr.Slider(0, 1, value=0.5, step=0.05, label="Chatterbox Exaggeration")
                        temperature = gr.Slider(0.1, 1.5, value=0.65, step=0.05, label="Temperature")
                    with gr.Row():
                        cfg_weight = gr.Slider(0, 2, value=0.5, step=0.05, label="Chatterbox CFG Weight")
                        repetition_penalty = gr.Slider(1, 8, value=5.0, step=0.1, label="XTTS Repetition Penalty")

                generate_button = gr.Button("🔊 Generate Nepali Speech", variant="primary")
                generation_status = gr.Markdown()
                output = gr.Audio(label="Generated Audio", type="filepath")
                download_output = gr.File(label="Download WAV")
                output_metadata = gr.Markdown()

                def guarded_generate(*args):
                    text_value, backend_value, reference_value, consent_value, *controls = args
                    if not consent_value:
                        raise gr.Error("Please confirm that you own the voice or have informed permission to clone it.")
                    result = generate(text_value, backend_value, reference_value, *controls)
                    return result, result, "**{}** generated successfully.".format(BACKENDS[backend_value].name), "✅ **Generation complete.**"

                generate_button.click(
                    guarded_generate,
                    [text, backend, reference, consent, exaggeration, temperature, cfg_weight, repetition_penalty],
                    [output, download_output, output_metadata, generation_status],
                )

            with gr.Tab("⚖️ Compare"):
                gr.Markdown("Generate identical text with all four backends. Each model is isolated: one failure does not cancel the others.")
                compare_text = gr.Textbox(label="Comparison text", value="नमस्ते! यो नेपाली AI आवाज परीक्षण हो।", lines=3)
                compare_reference = gr.Audio(label="Consented reference voice", type="filepath", sources=["upload", "microphone"])
                compare_consent = gr.Checkbox(label="I own this voice or have informed permission to clone it.", value=False)
                compare_button = gr.Button("⚖️ Generate with all 4 models", variant="primary")
                compare_status = gr.Markdown()
                compare_outputs = []
                for backend_id, info in BACKENDS.items():
                    with gr.Group():
                        gr.Markdown(f"### {info.name}")
                        gr.Markdown(f"{info.description} · {info.license} · {info.hardware}")
                        compare_outputs.append(gr.Audio(label="Audio", type="filepath"))
                def compare_all(text_value, reference_value, consent_value, exag, temp, cfg, rep):
                    if not consent_value:
                        raise gr.Error("Please confirm that you own the voice or have informed permission to clone it.")
                    text_value = _validate_text(text_value)
                    reference_path = _validate_reference(reference_value)
                    audios = []
                    messages = []
                    for backend_id, info in BACKENDS.items():
                        started = time.perf_counter()
                        try:
                            with engine_lock(backend_id):
                                wav, sr = _generate_with_engine(
                                    backend_id, text_value, reference_path, exag, temp, cfg, rep
                                )
                            path = _write_wav(wav, sr)
                            elapsed = time.perf_counter() - started
                            try:
                                audio_info = sf.info(path)
                                detail = "{:.2f}s audio · {:,} Hz · {:.1f}s generation".format(audio_info.duration, audio_info.samplerate, elapsed)
                            except Exception:
                                detail = "{:.1f}s generation".format(elapsed)
                            audios.append(path)
                            messages.append("✅ **{}: PASS** — {}".format(info.name, detail))
                        except Exception as exc:
                            audios.append(None)
                            log_generation_error(backend_id, exc)
                            messages.append("❌ **{}: FAIL** — Check Diagnostics and backend requirements.".format(info.name))
                    return audios + ["\n".join(messages)]
                compare_button.click(
                    compare_all,
                    [compare_text, compare_reference, compare_consent, exaggeration, temperature, cfg_weight, repetition_penalty],
                    compare_outputs + [compare_status],
                )

            with gr.Tab("📚 Models"):
                gr.Markdown("### Backend matrix")
                gr.Dataframe(
                    headers=["Backend", "Purpose", "Languages", "License", "Hardware", "Access"],
                    datatype=["str"] * 6, value=_model_rows(), interactive=False
                )
                gr.Markdown(
                    "Model licenses apply to upstream checkpoints and are separate from this application's source code. "
                    "Review MODEL_LICENSES.md and THIRD_PARTY_NOTICES.md before redistribution."
                )

            with gr.Tab("🩺 Diagnostics"):
                diagnostics = gr.Dataframe(
                    headers=["Backend", "Dependency", "Installed", "Access"],
                    datatype=["str"] * 4, value=_diagnostic_rows(), interactive=False
                )
                refresh = gr.Button("🔄 Refresh diagnostics")
                refresh.click(_diagnostic_rows, outputs=diagnostics)
                gr.Markdown("A smoke test performs real model loading and a short Nepali generation.")
                smoke_backend = gr.Dropdown(
                    choices=[(v.name, k) for k, v in BACKENDS.items()],
                    value="chatterbox_nepali", label="Backend to test"
                )
                smoke_reference = gr.Audio(label="Consented reference voice", type="filepath", sources=["upload", "microphone"])
                smoke_button = gr.Button("🧪 Test selected model")
                smoke_output = gr.Markdown()
                smoke_button.click(
                    lambda b, r: _smoke_result(smoke_test(b, r)),
                    [smoke_backend, smoke_reference], smoke_output
                )

        gr.Markdown(
            "⚠️ **Responsible use:** Use voice cloning only with ownership or informed permission. "
            "Do not use generated speech for impersonation, fraud, deception, or to present synthetic speech as authentic."
        )
    return demo


if __name__ == "__main__":
    build_ui().queue(max_size=8, default_concurrency_limit=1).launch()
