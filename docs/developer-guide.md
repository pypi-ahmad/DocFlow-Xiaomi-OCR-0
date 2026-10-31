# Developer guide

## Runtime and layout

`streamlit_app.py` provides the local workbench; `docflow/streamlit_ui.py` handles previews and exports. `app.py`, `gradio_ui.py` and `docflow/space_ui.py` provide the separate Gradio interface. Both call `docflow/conversion.py` and `docflow/xiaomi.py`. `docflow/image_limits.py` checks image dimensions, and `docflow/xiaomi_postprocess/` contains adapted postprocessing with its license and notice.

`pyproject.toml` and `uv.lock` manage the Python 3.12 local environment. Local PyTorch 2.14.1 and torchvision 0.29.1 use the configured CUDA 13.0 index. The Space requirements use PyTorch 2.13.0 and torchvision 0.28.0; both use Transformers 5.17.0. `scripts/setup-models.py` downloads pinned snapshots to `.models/`; `launch.cmd` runs Streamlit offline on port 8472.

For the model roles, official guides and implementation details, see [How the models work in DocFlow](models.md).

## Conversion flow

PDFium renders selected PDF pages; Pillow loads image frames. Pages are bounded to 2048 pixels per dimension. The engine loads PP-DocLayoutV3 and Xiaomi-OCR-0 on CUDA, runs layout detection at threshold 0.25, deduplicates reading-order values and recognizes each crop sequentially. Tables use the OTSL prompt, formulas use the LaTeX prompt, and other regions use the text prompt. If no usable regions remain, whole-page OCR uses page-level geometry. Each crop has a 4096-token limit. A lock serializes calls to the engine.

The model IDs and revisions are defined in `docflow/xiaomi.py`. The document schema includes page Markdown, blocks, coordinates, warnings, status and model metadata. Conversion writes `document.json`, `document.md`, `document.html`, `chunks.json`, source PNGs and annotated PNGs. Cache identity includes input bytes and filename, backend, both revisions, page selection and fixed conversion settings. Complete results are reused; incomplete results are retried.

The Streamlit preview and saved-result navigation do not load models. Local results persist under `conversion_results/`; Space results use temporary session directories. Space model loading happens at startup and GPU work runs inside a 120-second `spaces.GPU` event.

## Checks

```powershell
uv run --no-sync python -m pytest -q
uv run --no-sync ty check docflow
uv run --no-sync ruff check streamlit_app.py docflow/streamlit_ui.py tests/test_streamlit_workbench.py
uv run --offline --no-sync python -m scripts.smoke_xiaomi
```

The smoke check requires downloaded models and a working NVIDIA GPU. See [migration validation](xiaomi-migration-validation.md) for dated observed results and their limits.

## Space deployment

The target is `pypi-ahmad/DocFlow-Xiaomi-OCR-0`. Creation was rejected with HTTP 402 because the account had reached its two-ZeroGPU-Space limit; no new deployment was verified. To deploy after resolving account eligibility, create a Gradio Space with ZeroGPU and upload `app.py`, `gradio_ui.py`, `requirements.txt`, `README.md`, `docflow/*.py`, `docflow/xiaomi_postprocess/` including its license and notice, `docs/user-guide.md`, `docs/developer-guide.md`, `docs/models.md`, `docs/xiaomi-migration-validation.md`, `docs/diagrams/architecture.html` and `docs/images/architecture.png` so the README links resolve. Exclude credentials, model caches, local results and environments. Verify the build and a real conversion before describing it as live.

The neighboring DocLayout repository is reference material. The previous security audit covered the Nemotron implementation, not the Xiaomi migration.
