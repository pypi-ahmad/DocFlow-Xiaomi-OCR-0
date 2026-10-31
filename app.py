"""Gradio entry point for Hugging Face ZeroGPU Spaces."""

import spaces  # Must precede torch and other CUDA imports.

# ruff: noqa: I001
import gradio as gr
from pathlib import Path
from docflow.xiaomi import Engine
from docflow.conversion import convert
from docflow.space_ui import bundle, prepare, view
from gradio_ui import CSS, THEME, build_demo
engine = Engine(offline=False)

def preflight(files, first, last, state):
    """Reject invalid workloads before the GPU event."""
    try:
        return prepare(files, first, last, state)
    except (ValueError, OSError) as exc:
        raise gr.Error(str(exc)) from None


def convert_batch(state, mode, parser, progress):
    """Convert up to five pages; all returned state is CPU data."""
    results = []
    for index, job in enumerate(state["jobs"]):
        path = Path(job["path"])
        progress(index / len(state["jobs"]), desc=f"Parsing {path.name}")
        results.append(
            convert(
                path.read_bytes(),
                path.name,
                mode,
                job["first"],
                job["last"],
                page_parser=parser,
                output_root=Path(state["job_root"]) / str(index),
            )
        )
    state["results"] = [(result, str(directory)) for result, directory in results]
    archive = bundle(results, Path(state["job_root"]) / "documents.zip")
    choices = [
        (f"{i + 1}. {result['name']}", str(i)) for i, (result, _) in enumerate(results)
    ]
    return state, gr.Dropdown(choices=choices, value="0"), archive, *view(state, "0")


@spaces.GPU(duration=120)
def run_gpu(state, progress=gr.Progress()):  # noqa: B008 -- Gradio injects progress
    return convert_batch(state, "space-gpu", engine, progress)

demo = build_demo(preflight, run_gpu)

if __name__ == "__main__":
    demo.queue().launch(max_file_size="50mb", theme=THEME, css=CSS)
