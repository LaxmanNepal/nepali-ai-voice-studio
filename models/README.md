# Model cache

Third-party model weights are intentionally excluded from Git.

Backends should download models into a local cache at runtime using the upstream model identifier and the user's Hugging Face authentication where required.

Never commit:
- .safetensors
- .pt
- .pth
- .ckpt
- voice recordings

See MODEL_LICENSES.md for the licensing separation.
