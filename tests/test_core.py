from app.config import BACKENDS
from app.router import choose_backend
from app.runtime import device_summary, runtime_summary


def test_all_four_backends_are_registered():
    assert set(BACKENDS) == {
        "chatterbox_nepali",
        "swarlekha",
        "xtts_nepali",
        "pocket_tts",
    }


def test_router_prefers_explicit_backend():
    assert choose_backend("नमस्ते", "pocket_tts") == "pocket_tts"


def test_router_detects_devanagari():
    assert choose_backend("नमस्ते नेपाल") == "chatterbox_nepali"


def test_router_falls_back_to_english_backend():
    assert choose_backend("Hello Nepal") == "swarlekha"


def test_runtime_summary_is_safe():
    summary = runtime_summary()
    assert summary["python"]
    assert summary["device"]
    assert summary["hf_token"] in {"configured", "not configured"}
    assert device_summary()
