# Repository Guidelines

## Project Structure & Module Organization
- Core Python services live at the repository root: `audiobook_maker.py` orchestrates PDF-to-audio conversion, while `pdf_extractor.py`, `text_processor.py`, and `audio_generator.py` each handle a dedicated stage in the pipeline.
- `app.py` exposes the workflow through a Gradio web UI; `example_usage.py` demonstrates the scripted path.
- Shell helpers (`start_web.sh`, `start_with_proxy.sh`, `start_p100.sh`) and the Windows batch file mirror the same launch flow; keep environment-specific changes inside these wrappers.
- Assets generated at runtime (chunk WAVs, merged audiobooks) should live in a `output/` or scenario-specific subfolder created by your feature—avoid adding binary artifacts to the repository.

## Build, Test, and Development Commands
- `python -m venv .venv && source .venv/bin/activate` boots an isolated environment; use `pip install -r requirements.txt` to sync dependencies.
- `python app.py` starts the Gradio server on `http://localhost:7860`; prefer `./start_web.sh` or `start_web.bat` when you need preset environment variables.
- `python audiobook_maker.py RivewTown.pdf --output demo.wav --voice v2/zh_speaker_1` triggers the full CLI pipeline; adjust `--small-model` when developing on limited GPUs.
- `python example_usage.py` is a quick integration smoke test that exercises the orchestrator with canned inputs.

## Coding Style & Naming Conventions
- Follow idiomatic Python with 4-space indentation, type hints for new functions, and docstrings on reusable helpers.
- Module- and file-level names are snake_case; classes use CapWords. Align new voice presets or pipeline stages with existing naming (e.g., `generate_*`, `*_processor`).
- Run `ruff check .` if you introduce linting (prefer adding it once we formalize tooling); keep imports sorted and limit functions to single responsibilities.

## Testing Guidelines
- There is no automated test suite yet; validate changes by running `python example_usage.py` and a targeted CLI invocation against a short PDF.
- For audio regressions, compare output durations and listen to the first and last minute of the merged WAV.
- Add pytest-style unit tests under a future `tests/` folder when you split logic from the I/O heavy scripts; isolate Bark calls behind mocks.

## Commit & Pull Request Guidelines
- Keep commit messages in the present tense (“Add CLI voice selector”), mirroring the initial history and keeping scope focused.
- Reference related issues in the body with `Refs #123` and note GPU/runtime assumptions.
- Pull requests should summarize user-visible changes, list manual test commands, and include before/after timings or sample output paths when touching synthesis speed.
