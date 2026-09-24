from .config import BACKENDS


def list_backends():
    return BACKENDS


def choose_backend(text: str, preferred: str | None = None) -> str:
    if preferred in BACKENDS:
        return preferred

    has_devanagari = any("\u0900" <= ch <= "\u097F" for ch in (text or ""))
    if has_devanagari:
        return "chatterbox_nepali"

    return "swarlekha"
