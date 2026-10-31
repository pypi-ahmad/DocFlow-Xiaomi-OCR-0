# Repository Guidelines

## Workspace scope

Keep project work in this repository. Store research reports in `docs/`. The separate DocLayout repository is reference material; do not write deliverables there unless explicitly requested.

## Project structure and current state

The repository contains application code in `docflow/`, the Streamlit entry point `streamlit_app.py`, backend tests in `tests/`, a native GPU smoke-check entry point in `runtime/`, and research in `docs/`. Dependencies are managed by `pyproject.toml` and `uv.lock`. Local code-index metadata lives in `.code-review-graph/` and `.codegraph/`. See `README.md` for implemented features and remaining work.

Treat index databases and process files as tooling metadata; do not edit them as application code. The shared engine is in `docflow/xiaomi.py`; `docflow/conversion.py` writes results, and `docflow/streamlit_ui.py` provides Streamlit presentation helpers. The Gradio entry points are `app.py` and `gradio_ui.py`.

## Agreed application scope

Use Xiaomi-OCR-0 with PP-DocLayoutV3_safetensors for layout. Local Streamlit runs natively on Windows, offline after model setup. The separate Gradio ZeroGPU app targets pypi-ahmad/DocFlow-Xiaomi-OCR-0. Do not update the old Nemotron Space.

Keep uploads, page selection, batches, previews, annotations, exports and saved results. Exclude chat, classification and business-field extraction. Never automatically fall back to online inference. Preserve historical saved results and research.

## Build, test, and development commands

Use `uv sync` for setup, `launch.cmd` for the UI, `uv run python -m pytest -q` for tests, and `uv run ty check docflow` for type checks. Inspect the workspace with:

- `Get-ChildItem -Force`: list root files, including hidden directories.
- `rg --files --hidden`: find files beneath the workspace.

The project uses Python 3.12 and CUDA wheels configured in `pyproject.toml`. Run `uv run python -m scripts.setup-models` once before offline use.

## Coding style and naming conventions

No language-specific style, indentation rules, formatter, or linter is established yet. Follow existing source conventions when code is added. Keep changes focused and avoid unrelated reformatting. Use descriptive names and document any adopted formatting rules alongside their configuration.

## Testing guidelines

Tests use pytest in `tests/test_*.py`; no coverage threshold is configured. Add focused checks that demonstrate intended behavior and relevant failures. Report checks actually run and explain verification limits.

## Commit and pull request guidelines

Use short, imperative commit subjects describing one change. Pull requests should explain the purpose, scope, and validation results; link relevant issues and include screenshots for visible interface changes.

## Security and configuration

Keep credentials out of source files, examples, and logs. Use configured environment variables for secrets. Preserve unrelated local files and request explicit authorization before destructive filesystem or Git operations.
