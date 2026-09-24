# Swarlekha backend

Swarlekha is a Nepali/English TTS and voice-cloning model based on the Chatterbox architecture. Its model card documents the public Python API through SwarlekhaNepaliTTS and the generate(text, audio_prompt_path=...) interface.

Upstream model artifacts include t3_nepali_checkpoint.pt, tokenizer_np.json, ve.safetensors, s3gen.safetensors, and conds.pt. They remain runtime assets and are not stored in this repository.

Use only a reference voice you have permission to clone. The upstream model recommends clean 3–10 second reference speech.

The upstream model is listed as MIT; Chatterbox-derived components retain their applicable upstream notices.
