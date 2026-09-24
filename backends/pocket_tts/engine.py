from __future__ import annotations

import os
from pathlib import Path

import numpy as np
import torch

MODEL_REPO = os.getenv("POCKET_TTS_NEPALI_REPO", "himalaya-ai/pocket-tts-nepali-6l")
CONFIG_URI = os.getenv("POCKET_TTS_NEPALI_CONFIG", f"hf://{MODEL_REPO}/config.yaml")
DEVICE = "cpu"


class PocketTtsNepaliEngine:
    """CPU-oriented Pocket-TTS Nepali adapter."""

    def __init__(self):
        self._model = None
        self._voice_states: dict[str, dict] = {}

    def _load(self):
        if self._model is not None:
            return
        try:
            from pocket_tts import TTSModel
        except ImportError as exc:
            raise RuntimeError(
                "Pocket-TTS dependencies are missing. Install "
                "backends/pocket_tts/requirements.txt in an isolated environment."
            ) from exc
        try:
            self._model = TTSModel.load_model(config=CONFIG_URI)
            self._model.to(DEVICE)
        except Exception as exc:
            raise RuntimeError(
                "Could not load the gated Nepali Pocket-TTS model. "
                "Request access to himalaya-ai/pocket-tts-nepali-6l and authenticate "
                "Hugging Face with an account that has access."
            ) from exc

    def _voice_state(self, reference_audio: str):
        key = str(Path(reference_audio).resolve())
        if key not in self._voice_states:
            self._voice_states[key] = self._model.get_state_for_audio_prompt(
                reference_audio, truncate=True
            )
        return self._voice_states[key]

    def generate(self, text: str, reference_audio: str):
        if not text or not text.strip():
            raise ValueError("Text is required.")
        if not reference_audio:
            raise ValueError("A consented reference voice recording is required.")
        reference = Path(reference_audio)
        if not reference.exists():
            raise FileNotFoundError(f"Reference audio not found: {reference}")
        self._load()
        state = self._voice_state(str(reference))
        with torch.inference_mode():
            audio = self._model.generate_audio(state, text.strip())
        if audio.ndim > 1:
            audio = audio.squeeze(0)
        wav = np.asarray(audio.detach().cpu(), dtype=np.float32)
        return torch.from_numpy(wav), int(self._model.sample_rate)
