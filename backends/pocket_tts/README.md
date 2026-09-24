# Pocket-TTS Nepali backend

Upstream model: https://huggingface.co/himalaya-ai/pocket-tts-nepali-6l

The model is a lightweight, CPU-oriented Nepali Pocket-TTS checkpoint. The upstream model card documents loading its config through hf://, a 3–5 second mono reference clip, voice cloning, and CPU inference.

## Access

The Hugging Face model is gated. Request access on the upstream model page and authenticate locally before the first model download.

## Safety and licensing

The model card explicitly says the model is not intended for impersonation, presenting generated audio as genuine, or cloning a voice without informed consent.

The model is CC-BY-4.0. Keep attribution for the model, Kyutai Pocket-TTS, and applicable CC-BY datasets as required by their terms.

No reference recordings or model weights are bundled in this repository.

## Runtime behavior

The adapter loads the model lazily, caches it in memory, caches each reference voice state, truncates prompts to 30 seconds, and writes no model assets into Git.
