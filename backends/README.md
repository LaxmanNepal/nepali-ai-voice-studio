# Backend isolation

Each engine gets its own adapter and dependency set.

Do not import all four model stacks at application import time.

Recommended execution modes:

1. Separate Python virtual environments for local development.
2. Separate worker processes/services for production.
3. A shared Gradio router communicates with one selected backend.

This prevents PyTorch, Transformers, TTS, tokenizer and model-version conflicts.
