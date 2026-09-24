from __future__ import annotations

import os
from pathlib import Path

import numpy as np
import torch
from huggingface_hub import snapshot_download


MODEL_REPO = os.getenv("XTTS_NEPALI_REPO", "Oshara/xtts-v2-nepali")
SUBFOLDER = os.getenv("XTTS_NEPALI_SUBFOLDER", "epoch-10")
DEVICE = os.getenv("XTTS_NEPALI_DEVICE", "cuda" if torch.cuda.is_available() else "cpu")


class XttsNepaliEngine:
    """Lazy XTTS-v2 Nepali loader.

    Checkpoints remain in the Hugging Face cache and are never written to Git.
    The upstream model is licensed under the Coqui Public Model License (CPML).
    """

    sample_rate = 24000

    def __init__(self, device: str | None = None):
        self.device = device or DEVICE
        self._model = None
        self._config = None
        self._model_dir: Path | None = None

    def _load(self):
        if self._model is not None:
            return

        try:
            from TTS.tts.configs.xtts_config import XttsConfig
            from TTS.tts.models.xtts import Xtts
        except ImportError as exc:
            raise RuntimeError(
                "XTTS backend dependencies are missing. Install "
                "backends/xtts_nepali/requirements.txt in an isolated environment."
            ) from exc

        model_dir = Path(
            snapshot_download(
                repo_id=MODEL_REPO,
                allow_patterns=[f"{SUBFOLDER}/config.json", f"{SUBFOLDER}/model.pth",
                                f"{SUBFOLDER}/vocab.json", f"{SUBFOLDER}/speakers_xtts.pth"],
            )
        ) / SUBFOLDER

        required = ["config.json", "model.pth", "vocab.json", "speakers_xtts.pth"]
        missing = [name for name in required if not (model_dir / name).exists()]
        if missing:
            raise RuntimeError(f"XTTS checkpoint is incomplete; missing: {', '.join(missing)}")

        config = XttsConfig()
        config.load_json(str(model_dir / "config.json"))
        model = Xtts.init_from_config(config)
        model.load_checkpoint(
            config,
            checkpoint_path=str(model_dir / "model.pth"),
            vocab_path=str(model_dir / "vocab.json"),
            speaker_file_path=str(model_dir / "speakers_xtts.pth"),
            eval=True,
        )
        if self.device == "cuda":
            model.cuda()
        else:
            model.cpu()

        self._config = config
        self._model = model
        self._model_dir = model_dir

    @staticmethod
    def _normalise_text(text: str) -> str:
        text = text.replace("\u200b", "").replace("\ufeff", "").strip()
        return text

    def generate(
        self,
        text: str,
        reference_audio: str,
        temperature: float = 0.65,
        repetition_penalty: float = 5.0,
    ):
        if not text or not text.strip():
            raise ValueError("Text is required.")
        if not reference_audio:
            raise ValueError("A consented reference voice recording is required.")

        reference = Path(reference_audio)
        if not reference.exists():
            raise FileNotFoundError(f"Reference audio not found: {reference}")

        self._load()
        with torch.inference_mode():
            out = self._model.synthesize(
                self._normalise_text(text),
                self._config,
                speaker_wav=str(reference),
                language="ne",
                temperature=temperature,
                repetition_penalty=repetition_penalty,
            )

        wav = np.asarray(out["wav"], dtype=np.float32)
        return torch.from_numpy(wav).cpu(), self.sample_rate
