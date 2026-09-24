from __future__ import annotations

import importlib.util
import os
import time

from .config import BACKENDS


def _module_available(name: str) -> bool:
    return importlib.util.find_spec(name) is not None


def backend_status() -> list[dict[str, str]]:
    return [
        {
            "id": "chatterbox_nepali",
            "name": BACKENDS["chatterbox_nepali"].name,
            "dependency": "chatterbox",
            "installed": "ready" if _module_available("chatterbox") else "missing",
            "access": "HF_TOKEN configured" if os.getenv("HF_TOKEN") else "HF_TOKEN not configured",
        },
        {
            "id": "swarlekha",
            "name": BACKENDS["swarlekha"].name,
            "dependency": "swarlekha_model",
            "installed": "ready" if _module_available("swarlekha_model") else "missing",
            "access": "runtime model download",
        },
        {
            "id": "xtts_nepali",
            "name": BACKENDS["xtts_nepali"].name,
            "dependency": "TTS",
            "installed": "ready" if _module_available("TTS") else "missing",
            "access": "runtime model download",
        },
        {
            "id": "pocket_tts",
            "name": BACKENDS["pocket_tts"].name,
            "dependency": "pocket_tts",
            "installed": "ready" if _module_available("pocket_tts") else "missing",
            "access": "HF_TOKEN configured" if os.getenv("HF_TOKEN") else "HF_TOKEN not configured",
        },
    ]


def smoke_test(backend: str, reference_audio: str | None = None) -> dict[str, str]:
    """Run a tiny real generation test for one backend.

    This deliberately uses a caller-supplied reference recording so the app
    never bundles or invents a voice. The generated file is not persisted by
    this diagnostic.
    """
    if backend not in BACKENDS:
        return {"status": "FAIL", "message": f"Unknown backend: {backend}"}
    if not reference_audio:
        return {
            "status": "BLOCKED",
            "message": "Upload a consented reference voice to run a real generation test.",
        }

    started = time.perf_counter()
    try:
        from .main import _get_engine, _validate_reference
        reference = _validate_reference(reference_audio)
        engine = _get_engine(backend)
        if backend == "chatterbox_nepali":
            wav, sample_rate = engine.generate(
                text="नमस्ते, यो परीक्षण आवाज हो।",
                reference_audio=reference,
                exaggeration=0.5,
                temperature=0.65,
                cfg_weight=0.5,
            )
        elif backend == "swarlekha":
            wav, sample_rate = engine.generate(
                "नमस्ते, यो परीक्षण आवाज हो।", reference
            )
        elif backend == "xtts_nepali":
            wav, sample_rate = engine.generate(
                "नमस्ते, यो परीक्षण आवाज हो।",
                reference,
                temperature=0.65,
                repetition_penalty=5.0,
            )
        elif backend == "pocket_tts":
            wav, sample_rate = engine.generate(
                "नमस्ते, यो परीक्षण आवाज हो।", reference
            )
        else:
            raise RuntimeError("Unsupported backend")

        duration = float(wav.numel()) / float(sample_rate)
        elapsed = time.perf_counter() - started
        if wav.numel() == 0 or duration <= 0:
            raise RuntimeError("Backend returned empty audio.")
        return {
            "status": "PASS",
            "message": f"Generated {duration:.1f}s audio at {sample_rate} Hz in {elapsed:.1f}s.",
        }
    except Exception as exc:
        elapsed = time.perf_counter() - started
        return {
            "status": "FAIL",
            "message": f"{type(exc).__name__}: {exc} (after {elapsed:.1f}s)",
        }
