# 🇳🇵 Nepali AI Voice Studio

A unified Gradio-based voice studio architecture for Nepali text-to-speech and voice cloning.

## Planned engines

- Chatterbox Nepali
- Swarlekha
- XTTS-v2 Nepali
- Pocket-TTS Nepali

## Architecture

Each model is implemented as an isolated backend so that model-specific dependencies, checkpoints, tokenizers, and licenses are not mixed.

Model weights are **not committed to Git**. They are downloaded/cached at runtime from their upstream Hugging Face repositories where access and licensing permit.

## Repository structure

```
app/                  # Shared UI, routing and utilities
backends/             # One isolated adapter per TTS engine
models/               # Runtime model cache documentation; no weights
scripts/              # Model download/setup helpers
licenses/             # Third-party license notices
examples/             # Safe text examples
```

## License

The application code will have its own license. Third-party model code, weights, datasets, tokenizers and dependencies remain subject to their respective upstream licenses. See `MODEL_LICENSES.md` and `THIRD_PARTY_NOTICES.md`.

> This project does not redistribute third-party voice recordings or model checkpoints unless their applicable license and access terms explicitly permit redistribution.
