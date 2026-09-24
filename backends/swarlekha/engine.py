from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

import torch

MODEL_REPO = os.getenv("SWARLEKHA_REPO", "indra17/swarlekha")

class SwarlekhaEngine:
    """Lazy adapter for the upstream Swarlekha implementation."""
    name = "Swarlekha"

    def __init__(self, device: Optional[str] = None):
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.model = None

    def load(self):
        if self.model is not None:
            return self.model
        try:
            from swarlekha_model.tts_nepali import SwarlekhaNepaliTTS
        except ImportError as exc:
            raise RuntimeError("Swarlekha runtime is not installed. Install the isolated backend dependencies and upstream implementation.") from exc
        self.model = SwarlekhaNepaliTTS.from_pretrained(device=self.device)
        return self.model

    @torch.inference_mode()
    def generate(self, text: str, reference_audio: Optional[str] = None):
        if not text or not text.strip():
            raise ValueError("Text is required.")
        if not reference_audio:
            raise ValueError("A 3–10 second consented reference voice clip is required.")
        if not Path(reference_audio).exists():
            raise FileNotFoundError(f"Reference audio not found: {reference_audio}")
        model = self.load()
        wav = model.generate(text.strip(), audio_prompt_path=reference_audio)
        return wav.detach().cpu(), model.sr
