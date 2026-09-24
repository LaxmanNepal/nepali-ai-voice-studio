# Deployment

## Architecture

The four backends intentionally keep their dependency stacks isolated. Do not install every backend into one production image unless the combined dependency set has been tested. The preferred production pattern is one container/worker per backend.

## Hugging Face Spaces

`app.py` is the Space-friendly entrypoint:

    python app.py

Set `HF_TOKEN` as a Space secret only when the selected gated model requires it. Never commit a token.

For a dedicated Pocket-TTS Space:

    pip install -r requirements.txt
    pip install -r backends/pocket_tts/requirements.txt

Replace the backend requirements path for other backends.

## Docker

Build a selected-backend image:

    docker build --build-arg BACKEND_REQ=backends/pocket_tts/requirements.txt -t nepali-ai-voice-studio .

Run it:

    docker run --rm -p 7860:7860 --env-file .env nepali-ai-voice-studio

The build argument supports all four backend requirements files.

Do not bake model weights into Git or the Docker image. Hugging Face downloads remain runtime-managed and can use a persistent cache volume.

## Secrets

- `HF_TOKEN`: Hugging Face token for gated models.
- Never put tokens in source files, README examples, Dockerfiles, logs, or screenshots.

## Reliability

Inference is serialized per backend. This prevents overlapping calls against the same loaded model while allowing independent backend workers to operate separately.

Use `LOG_LEVEL=INFO` normally. Set `VOICE_OUTPUT_DIR` to a writable ephemeral or persistent directory.

## Health checks

The Diagnostics tab reports dependency readiness and token configuration. Its smoke test performs real model loading/generation but requires a user-supplied consented reference recording.

A dependency marked ready does not prove that the model can generate successfully.

## Production test matrix

Before public launch, test each selected backend in its own environment:

- app startup
- gated authentication where applicable
- reference validation
- Nepali pronunciation
- consented voice cloning
- valid/audible WAV output
- supported CPU/GPU behavior
- short and long text
- repeat generation
- concurrent requests and per-backend serialization
- persistent cache behavior, if used

The repository does not claim that this full runtime matrix has been completed.
