"""Hugging Face Spaces / simple launcher entrypoint."""
from app.main import build_ui

demo = build_ui()

if __name__ == "__main__":
    demo.launch()
