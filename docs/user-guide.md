# User guide

## Setup on Windows

Install uv and Python 3.12, and use an NVIDIA GPU with a compatible driver. Setup needs internet access and disk space for both model snapshots. From the project directory:

```powershell
uv sync --python 3.12
uv run python -m scripts.setup-models
.\launch.cmd
```

Open [http://127.0.0.1:8472](http://127.0.0.1:8472). After setup, the launcher uses the installed environment and cached models offline. The models load when you first parse a document. Docker and WSL are not required.

## Convert documents

1. Upload PDF, PNG, JPEG, GIF, TIFF or WebP files in the sidebar. A file can be up to 200 MiB; documents can have up to 500 pages and image frames up to 40 megapixels.
2. For a single file, choose inclusive start and end pages. Batches process all pages sequentially. Preview a single upload before parsing.
3. Select **Parse documents**. Choose a result in the sidebar and use Input preview, Markdown, HTML, Annotated, JSON and Chunks tabs to inspect it.
4. Download individual outputs or the ZIP. Review incomplete pages and their warnings in Annotated or JSON before retrying.

Results are stored in `conversion_results/`. Select a saved conversion and choose **Open saved conversion** to view it without loading models. Clearing the view leaves saved files on disk. Page images and JSON contain document content; protect the results directory.

## Troubleshooting

- If model files are missing, reconnect to the internet and repeat `uv run python -m scripts.setup-models`.
- Check CUDA with `uv run --no-sync python -c "import torch; print(torch.__version__, torch.version.cuda, torch.cuda.is_available())"`. The final value must be `True` for local GPU inference.
- If a page is incomplete, inspect its warnings and errors. Dense documents may exceed available GPU memory or the region token limit.
- If port 8472 is occupied, stop only the conflicting app you own or run Streamlit on an available port.

## Hugging Face Space

The separate Gradio Space is prepared but was not published. It allows up to five documents and five selected pages total, 50 MiB per file, and 40 megapixels per image frame. Its GPU event has a 120-second limit. Session files are temporary; download results before leaving. GPU queues and quotas apply. See the [developer guide](developer-guide.md) for deployment status.
