from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

import torch
from huggingface_hub import hf_hub_download
from safetensors.torch import load_file

MODEL_REPO = os.getenv("CHATTERBOX_NEPALI_REPO", "Imbatmann/chatterbox-nepali-tts")
CHECKPOINT = os.getenv("CHATTERBOX_NEPALI_CHECKPOINT", "t3_mtl_nepali_final.safetensors")

class ChatterboxNepaliEngine:
    """Lazy-loaded Nepali Chatterbox inference adapter."""
    name = "Chatterbox Nepali"
    sample_rate = 24000

    def __init__(self, device: Optional[str] = None):
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.model = None

    def load(self):
        if self.model is not None:
            return self.model
        try:
            from chatterbox.mtl_tts import ChatterboxMultilingualTTS
        except ImportError as exc:
            raise RuntimeError("Chatterbox is not installed. Install backends/chatterbox_nepali/requirements.txt.") from exc
        model = ChatterboxMultilingualTTS.from_pretrained(self.device)
        checkpoint = hf_hub_download(repo_id=MODEL_REPO, filename=CHECKPOINT)
        state_dict = load_file(checkpoint)
        cleaned = {key.replace("patched_model.", "").replace("model.", ""): value for key, value in state_dict.items()}
        model.t3.load_state_dict(cleaned, strict=False)
        model.t3.to(self.device).eval()
        self.model = model
        self.sample_rate = model.sr
        return model

    @torch.inference_mode()
    def generate(self, text: str, reference_audio: Optional[str] = None, exaggeration: float = 0.5, temperature: float = 0.8, cfg_weight: float = 0.5):
        if not text or not text.strip():
            raise ValueError("Text is required.")
        if not reference_audio:
            raise ValueError("A 5–10 second reference voice clip is required for voice cloning.")
        if not Path(reference_audio).exists():
            raise FileNotFoundError(f"Reference audio not found: {reference_audio}")
        model = self.load()
        wav = model.generate(text=text.strip(), language_id="ne", audio_prompt_path=reference_audio, exaggeration=float(exaggeration), temperature=float(temperature), cfg_weight=float(cfg_weight))
        return wav.detach().cpu(), model.sr
