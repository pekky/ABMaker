# Repository Guidelines

## Project Structure & Module Organization
- Core Python services live at the repository root: `audiobook_maker.py` orchestrates PDF-to-audio conversion, while `pdf_extractor.py`, `text_processor.py`, and `audio_generator.py` each handle a dedicated stage in the pipeline.
- `app.py` exposes the workflow through a Gradio web UI; `example_usage.py` demonstrates the scripted path.
- Shell helpers (`start_web.sh`, `start_with_proxy.sh`, `start_p100.sh`) and the Windows batch file mirror the same launch flow; keep environment-specific changes inside these wrappers.
- Assets generated at runtime (chunk WAVs, merged audiobooks) should live in a `output/` or scenario-specific subfolder created by your feature—avoid adding binary artifacts to the repository.
- **All temporary files must be stored in the `tmp/` directory**: This includes audio chunks, intermediate processing files, and test outputs. Use subdirectories like `tmp/batch/`, `tmp/fast_batch/`, etc. for different processing modes.
- **Batch processing rule**: When processing large documents, split them into batches of 15,000 tokens each. Each batch should generate a separate audio file. This rule is configurable via `--batch-mode` and `--batch-size` parameters in `optimized_audiobook_maker.py`.
- **Logging rule**: Each run of `optimized_audiobook_maker.py` creates a log file in the `tmp/` directory with the format `pdf名_yymmdd.log` (where yymmdd is year-month-day). All logs for the day are written to this single file. The batch processor outputs the total number of batches created to this log file.
- **Interactive selection rule**: When running `optimized_audiobook_maker.py`, if language (`-l`) and voice (`-v`) parameters are not specified, the system provides interactive menus for selection. Supported languages: English (en), Chinese (zh), Japanese (ja). Default configuration: English + English male voice (v2/en_speaker_0). Users can press Enter to accept defaults or choose from 8-9 voice options per language.

## Build, Test, and Development Commands
- **Environment Setup**: Use `./setup_environment.sh` (Linux/Mac) or `setup_environment.bat` (Windows) to automatically install miniconda, create abmaker310 environment, and install dependencies.
- **Quick Environment Activation**: Use `./activate_env.sh` (Linux/Mac) for quick environment activation.
- **Main Launch Script**: Use `./run_audiobook_maker.sh` for complete workflow including environment check, quality mode selection, background execution, and progress monitoring.
- **Progress Monitoring**: Use `./monitor.sh` to monitor conversion progress in real-time.
- **Stop Conversion**: Use `./stop_conversion.sh` to stop running conversion and monitoring processes.
- **Always activate conda environment before running Python scripts**: Use `source ~/.bashrc && conda activate abmaker310 && python3 script.py` for all Python executions.
- **All dependencies must be installed in the virtual environment**: Always use `conda install` or `pip install` within the activated `abmaker310` environment. Never install packages globally or with `sudo pip`. Use `conda install -c conda-forge` for packages that require system libraries (e.g., ffmpeg, pandas).
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
- **Bark API Compatibility**: The Bark library API changes frequently. Only use basic parameters: `text`, `history_prompt`, `text_temp`, `waveform_temp`. Avoid deprecated parameters like `coarse_temp`, `top_p`, `top_k`, `cfg_scale`.

## Commit & Pull Request Guidelines
- Keep commit messages in the present tense (“Add CLI voice selector”), mirroring the initial history and keeping scope focused.
- Reference related issues in the body with `Refs #123` and note GPU/runtime assumptions.
- Pull requests should summarize user-visible changes, list manual test commands, and include before/after timings or sample output paths when touching synthesis speed.
