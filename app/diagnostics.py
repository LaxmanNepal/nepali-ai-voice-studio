from __future__ import annotations

import importlib.util
import os

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
