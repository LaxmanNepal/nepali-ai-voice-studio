# XTTS-v2 Nepali backend

Upstream model: https://huggingface.co/Oshara/xtts-v2-nepali

This adapter loads the recommended `epoch-10` checkpoint at runtime from Hugging Face and performs zero-shot voice cloning from a user-supplied reference recording.

## Important license

The upstream checkpoint inherits the **Coqui Public Model License (CPML)**. CPML is separate from this repository's application code and from the other TTS backends. Review the current CPML terms before any commercial or revenue-generating use.

## Runtime

The adapter follows the upstream model-card API:

1. Download only `epoch-10/config.json`, `model.pth`, `vocab.json`, and `speakers_xtts.pth` into the Hugging Face cache.
2. Load `XttsConfig` and `Xtts`.
3. Synthesize with language code `ne` and a consented reference voice.
4. Return 24 kHz audio.

Set `XTTS_NEPALI_SUBFOLDER=epoch-20` only if you intentionally want the alternate checkpoint.

Model weights are never committed to this repository.
