# 🇳🇵 Nepali AI Voice Studio

A unified Gradio voice studio for Nepali text-to-speech and voice cloning, with model-specific dependencies and licenses kept isolated.

## Backends

| Backend | Nepali | Voice cloning | Runtime |
|---|---|---|---|
| Chatterbox Nepali | Yes | Yes | GPU-oriented |
| Swarlekha | Yes + English | Yes | Model-dependent |
| XTTS-v2 Nepali | Yes | Yes | CPU/GPU |
| Pocket-TTS Nepali | Yes | Yes | CPU-oriented |

## Architecture

Each backend owns its inference adapter and dependency file. Model weights are never committed to Git. Gated or licensed checkpoints are downloaded at runtime into the Hugging Face cache.

The shared Gradio app lazy-loads and caches each backend in memory, so model initialization is not repeated for every generation request. The UI also provides a four-model comparison workspace, model/license metadata, live text-length validation, and real smoke-test diagnostics.

## Current status

- [x] Shared Gradio UI
- [x] Chatterbox Nepali adapter
- [x] Swarlekha adapter
- [x] XTTS-v2 Nepali adapter
- [x] Pocket-TTS Nepali adapter
- [x] Runtime-only model weights
- [x] In-memory backend caching
- [x] Consent warning/reference-audio requirement
- [x] Separate dependency files
- [x] License matrix and third-party notices
- [ ] Full runtime test matrix on each backend environment
- [x] Four-model comparison workspace
- [x] Backend metadata/license matrix in UI
- [x] Text length validation and live character counter
- [x] Per-model failure isolation during comparison
- [x] Lazy backend loading remains enabled
- [x] Per-backend inference serialization
- [x] Production logging and runtime/device diagnostics
- [x] Docker and Hugging Face Spaces entrypoints
- [x] Deployment and production test documentation

## Access and licensing

### Chatterbox Nepali
Imbatmann/chatterbox-nepali-tts is gated. Accept the upstream access conditions and authenticate if required.

### Swarlekha
indra17/swarlekha is documented as MIT and supports Nepali/English voice cloning. Keep its upstream notices with deployments.

### XTTS-v2 Nepali
Oshara/xtts-v2-nepali defaults to epoch-10. Its checkpoint is subject to the Coqui Public Model License. Do not assume the application's license applies to the model or its outputs.

### Pocket-TTS Nepali
himalaya-ai/pocket-tts-nepali-6l is gated and CC-BY-4.0. The model card requires attribution and says to use a speaker recording only with informed consent. It is intended for Nepali CPU-oriented speech synthesis.

## Running

Install the shared shell first:

    pip install -r requirements.txt

Then install one backend environment at a time:

    pip install -r backends/chatterbox_nepali/requirements.txt

or:

    pip install -r backends/swarlekha/requirements.txt

or:

    pip install -r backends/xtts_nepali/requirements.txt

or:

    pip install -r backends/pocket_tts/requirements.txt

Authenticate Hugging Face when a gated model requires it, then:

    python -m app.main

Because backend dependency stacks can conflict, the recommended production layout is one virtual environment/container per backend with the same shared UI layer.

## Reference audio

Use only a voice recording you own or have explicit permission to clone. Do not present generated speech as an authentic recording of a real person.

## Repository policy

No third-party model checkpoints, voice recordings, or generated audio are committed. See MODEL_LICENSES.md, THIRD_PARTY_NOTICES.md, and each backend README.

## Test matrix

The repository records all four adapters as implemented, but a final production release still requires runtime generation tests for all four environments, including gated-model authentication, Nepali pronunciation, reference-voice cloning, output WAV integrity, CPU/GPU behavior, and long-text handling.

Pocket-TTS documents TTSModel.load_model, get_state_for_audio_prompt, and generate_audio, and its Nepali model card specifies a user-provided 3–5 second mono reference clip. The upstream Pocket-TTS project describes CPU-oriented operation and voice cloning.
## Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for Hugging Face Spaces and selected-backend Docker deployment. The repository deliberately avoids a single untested environment containing all four model stacks.
