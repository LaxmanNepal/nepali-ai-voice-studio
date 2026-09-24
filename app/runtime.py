from __future__ import annotations

import logging
import os
import platform
import tempfile
import threading
from pathlib import Path

import torch

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(level=getattr(logging, LOG_LEVEL, logging.INFO),
                    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s")
logger = logging.getLogger("nepali-ai-voice-studio")

_OUTPUT_DIR = Path(os.getenv("VOICE_OUTPUT_DIR", "outputs")).resolve()
_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
_ENGINE_LOCKS: dict[str, threading.Lock] = {}
_ENGINE_LOCKS_GUARD = threading.Lock()

def engine_lock(backend: str) -> threading.Lock:
    with _ENGINE_LOCKS_GUARD:
        return _ENGINE_LOCKS.setdefault(backend, threading.Lock())

def device_summary() -> str:
    forced = os.getenv("XTTS_NEPALI_DEVICE", "").strip().lower()
    return forced or ("cuda" if torch.cuda.is_available() else "cpu")

def runtime_summary() -> dict[str, str]:
    gpu = "available" if torch.cuda.is_available() else "not available"
    if torch.cuda.is_available():
        gpu = f"available ({torch.cuda.get_device_name(0)})"
    return {"python": platform.python_version(), "torch": getattr(torch, "__version__", "unknown"),
            "device": device_summary(), "cuda": gpu,
            "hf_token": "configured" if os.getenv("HF_TOKEN") else "not configured",
            "output_dir": str(_OUTPUT_DIR)}

def output_path(suffix: str = ".wav") -> str:
    handle = tempfile.NamedTemporaryFile(suffix=suffix, prefix="nepali-ai-voice-", dir=_OUTPUT_DIR, delete=False)
    path = handle.name
    handle.close()
    return path

def log_generation_start(backend: str, text_length: int) -> None:
    logger.info("generation start backend=%s text_chars=%d", backend, text_length)

def log_generation_done(backend: str, elapsed: float) -> None:
    logger.info("generation done backend=%s elapsed=%.2fs", backend, elapsed)

def log_generation_error(backend: str, exc: Exception) -> None:
    logger.exception("generation failed backend=%s error=%s", backend, exc)
