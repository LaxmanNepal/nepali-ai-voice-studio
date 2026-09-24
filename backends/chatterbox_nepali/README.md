# Chatterbox Nepali backend

Integrates the Imbatmann/chatterbox-nepali-tts checkpoint with the upstream Chatterbox multilingual runtime.

The checkpoint is not committed to Git. It is downloaded through Hugging Face Hub at runtime.

Runtime requirements:
- Dedicated Python environment
- Chatterbox-compatible PyTorch runtime
- Hugging Face access to the model
- A user-provided, consented 5–10 second reference voice clip
- CUDA GPU recommended

Environment variables:
- HF_TOKEN: use when Hugging Face authentication is required
- CHATTERBOX_NEPALI_REPO: override the upstream model repo
- CHATTERBOX_NEPALI_CHECKPOINT: override the checkpoint filename

The model card identifies the Nepali fine-tune as MIT. Underlying Chatterbox components retain their own upstream licensing.
