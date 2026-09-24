# Model License Matrix

This file records the intended separation of upstream model licensing. Always verify the current upstream license before redistributing weights or deploying commercially.

| Backend | Upstream model | License / terms | Weight policy |
|---|---|---|---|
| Chatterbox Nepali | Imbatmann/chatterbox-nepali-tts | MIT (verify upstream) | Runtime download/cache; do not commit weights |
| Swarlekha | indra17/swarlekha | MIT (verify upstream) | Runtime download/cache; do not commit weights |
| XTTS-v2 Nepali | Oshara/xtts-v2-nepali | Coqui Public Model License | Keep isolated; comply with CPML |
| Pocket-TTS Nepali | himalaya-ai/pocket-tts-nepali-6l | CC-BY-4.0 (verify upstream) | Runtime download/cache; attribution required |

The application license does not replace or supersede any upstream model license.

Before a production release, review each upstream model card and all dependency licenses again.
