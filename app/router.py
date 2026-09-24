from .config import BACKENDS

def list_backends():
    return BACKENDS

def choose_backend(text: str, preferred: str | None = None) -> str:
    if preferred in BACKENDS:
        return preferred

    # Conservative default: Swarlekha is the multilingual route.
    if any("\u0900" <= ch <= "\u097F" for ch in text):
        return "swarlekha"
    return "swarlekha"
