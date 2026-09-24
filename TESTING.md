# Runtime Test Checklist

This repository has four isolated backend adapters. Adapter code can be reviewed in GitHub, but a backend is only considered runtime-verified after its own environment successfully generates a Nepali WAV.

## Common checks

- Python environment starts successfully.
- Hugging Face authentication works where the model is gated.
- A 3–10 second mono reference recording is supplied by the speaker or with explicit permission.
- Nepali text generates without an exception.
- Output is a valid WAV and is audible.
- No model weights, reference recordings, or generated audio are written to Git.
- Short, medium, and long Nepali text are tested.
- The same reference voice is tested twice for consistency.

## Backend checks

### Chatterbox Nepali
Install:
    pip install -r backends/chatterbox_nepali/requirements.txt

Verify the gated Imbatmann checkpoint loads and language_id=ne produces Nepali speech.

### Swarlekha
Install:
    pip install -r backends/swarlekha/requirements.txt

Verify the upstream Swarlekha implementation providing swarlekha_model.tts_nepali is installed and the documented generate API works.

### XTTS-v2 Nepali
Install:
    pip install -r backends/xtts_nepali/requirements.txt

Verify epoch-10 loads, the custom model config includes Nepali, and language=ne succeeds.

### Pocket-TTS Nepali
Install:
    pip install -r backends/pocket_tts/requirements.txt

Request access to the gated Nepali model, authenticate Hugging Face, load config.yaml, encode the reference voice, and generate Nepali audio on CPU.

## Important

Do not mark a backend runtime-tested merely because its adapter imports. The model checkpoint, tokenizer/config, language support, reference voice path, and actual generation call must all succeed.
