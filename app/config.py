from dataclasses import dataclass


@dataclass(frozen=True)
class BackendInfo:
    name: str
    description: str
    languages: tuple[str, ...]
    license: str
    hardware: str
    access: str


BACKENDS = {
    "chatterbox_nepali": BackendInfo(
        "Chatterbox Nepali",
        "Nepali voice cloning backend",
        ("ne",),
        "MIT (model card)",
        "GPU recommended",
        "Gated Hugging Face model",
    ),
    "swarlekha": BackendInfo(
        "Swarlekha",
        "Nepali / English voice cloning backend",
        ("ne", "en"),
        "MIT (model card)",
        "Model-dependent",
        "Runtime model download",
    ),
    "xtts_nepali": BackendInfo(
        "XTTS-v2 Nepali",
        "Custom XTTS-v2 Nepali voice cloning backend",
        ("ne",),
        "CPML",
        "CPU/GPU",
        "Runtime model download",
    ),
    "pocket_tts": BackendInfo(
        "Pocket-TTS Nepali",
        "Lightweight Nepali CPU-oriented voice cloning backend",
        ("ne",),
        "CC-BY-4.0",
        "CPU-oriented",
        "Gated Hugging Face model",
    ),
}
