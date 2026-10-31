# Xiaomi migration validation — 2026-10-31

> The observations below are dated migration checks. The Streamlit workbench was subsequently updated; see the [user guide](user-guide.md).

Implemented native Windows Streamlit and separate Gradio Space source using Xiaomi-OCR-0 with PP-DocLayoutV3_safetensors. Both models are revision-pinned in docflow/xiaomi.py. Native Python 3.12.15, torch 2.14.1+cu130, Transformers 5.17.0. Previous Python 3.15 environment preserved as .venv-py315-backup.

## Observed checks

- 14 pytest tests passed, including routing, duplicate detections, coordinate clamping, partial recognition, empty-layout fallback, table escaping, upload limits, exports and saved-result UI.
- `uv run ty check docflow` passed.
- Focused Ruff checks passed for the engine, Space entry point and new pipeline/postprocessing tests. Import/unused-symbol checks passed for changed app modules. Existing broad-exception lint findings remain at UI/conversion error boundaries.
- Gradio 6.31.0 UI construction passed; remote ZeroGPU execution was not tested.
- RTX 4060 Laptop GPU: synthetic invoice recognized correctly, 15.5 seconds including loading, peak allocated memory 2546 MiB.
- Two-page synthetic PDF with table, inline formula and footer: complete in 18.1 seconds including loading; both pages retained 42.00, formula and footer; annotations, Markdown, HTML, JSON and chunks generated.
- The PDF test patched socket.connect to reject network access during model initialization and conversion. It passed using cached snapshots.

These synthetic checks do not establish accuracy or throughput on representative dense/scanned documents.

## Deployment blocker

Attempted creation of pypi-ahmad/DocFlow-Xiaomi-OCR-0 with explicit ZeroGPU hardware. Hugging Face returned HTTP 402: free accounts are limited to two ZeroGPU Spaces. No new Space was created; existing Spaces were not modified. Free an eligible slot or upgrade the account before deploying. Do not silently switch to paid hardware or replace an existing Space.

## Sources

- https://huggingface.co/xiaomi-research/Xiaomi-OCR-0
- https://huggingface.co/PaddlePaddle/PP-DocLayoutV3_safetensors
- https://huggingface.co/docs/hub/spaces-zerogpu
- https://pytorch.org/get-started/previous-versions/

Postprocessing helpers retain the upstream Apache license and modification notice in docflow/xiaomi_postprocess.
