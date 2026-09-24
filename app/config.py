from dataclasses import dataclass

@dataclass(frozen=True)
class BackendInfo:
    name: str
    description: str
    languages: tuple[str, ...]

BACKENDS = {
    "chatterbox_nepali": BackendInfo(
        "Chatterbox Nepali", "Nepali voice cloning backend", ("ne",)
    ),
    "swarlekha": BackendInfo(
        "Swarlekha", "Nepali / English voice backend", ("ne", "en")
    ),
    "xtts_nepali": BackendInfo(
        "XTTS-v2 Nepali", "XTTS Nepali voice cloning backend", ("ne",)
    ),
    "pocket_tts": BackendInfo(
        "Pocket-TTS Nepali", "Lightweight Nepali CPU-oriented backend", ("ne",)
    ),
}
