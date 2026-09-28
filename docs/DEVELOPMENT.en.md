# Development — 2.4

[Deutsch](ENTWICKLUNG.de.md) · [English](DEVELOPMENT.en.md) · [Русский](РАЗРАБОТКА.ru.md)

## Design

Teams UI Automation → LiveSource (new speech separate from old context) → local coordinator → OpenVINO text model → ten-answer history → native UI.
A manual slide request captures the current shared content using PrintWindow and sends it to local Ollama. The image cache includes image hash and language; capture timestamps stay fresh.

Loopback only: 8765 coordinator, 8766 text, 11435 vision. Write endpoints validate Origin and input sizes. Captions/screens are untrusted data, not instructions. No cloud fallback or credentials. The launcher owns and closes its own processes. Portable refuses occupied service ports rather than silently using another installation. Manual questions take priority after the current generation; they do not interrupt it.

## Portable build

Relative paths live in portable.json. Laufzeit/python is a standalone Python distribution with local import paths, not a copied venv. runtime_boot.py explicitly adds only the application directory. Modelle contains the OpenVINO model and only the required Ollama manifest/blobs. No user history/caches ship. Daten is created on the recipient's PC.

A working NPU is preferred; otherwise sequential bounded CPU/GPU probes select a device. Hardware/driver/model fingerprint invalidates the cache. CPU uses at most four threads. This small test is not a universal performance benchmark.

Developers (not end users) need Python 3.12 and Node.js:
1. `python -m pip install -r requirements-ui.txt`
2. `python verify.py --node PATH_TO_NODE --ui`
3. `python build-exe.py --output BUILD/dist`
4. Prepare standalone Python and requirements-npu.txt packages. Use `prepare-runtime.py --help` to provide explicit local runtime locations. It downloads nothing and checks isolated imports.
5. Prepare [OpenVINO Qwen3-8B](https://huggingface.co/OpenVINO/Qwen3-8B-int4-cw-ov) and [qwen3-vl:2b-instruct](https://ollama.com/library/qwen3-vl:2b-instruct).
6. `python build-portable.py --app APP_FOLDER --runtime RUNTIME_FOLDER --models MODEL_ROOT --output NEW_NAME.zip`. Model root must contain Qwen3-8B-int4-cw-ov plus ollama/manifests and ollama/blobs.
7. Fully extract elsewhere and test demo, real startup, languages, questions, slide errors and shutdown; then test a clean second Windows PC.
8. `python export-source.py --output NEW_SOURCE.zip` creates the separate allowlisted Git source package.

Pinned build components: Python 3.12.14, Node 24.19.0, OpenVINO 2026.3.1 / GenAI and Tokenizers 2026.3.1.0, NumPy 2.5.3, Ollama 0.33.3.

## Quality and release

verify.py covers syntax/version agreement, translations, allowlists, freshness, priority, real response limits, language-specific caching and simulated device choice. --ui adds native window/stack/Z-order/input tests, mocked audio and animation. Hardware integration is separate; CI must not load models or read real meetings.

Every fix needs a regression check; UI changes need synthetic visual review. Do not use real classroom data as fixtures. version.json is authoritative. Keep previous releases. The EXE is unsigned; second-PC testing, source-code license choice and public release review remain separate. Preserve third-party notices and artwork provenance. No repository was published.

