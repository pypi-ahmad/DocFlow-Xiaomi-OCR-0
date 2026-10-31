# How the models work in DocFlow

DocFlow uses two models for each page. PP-DocLayoutV3 finds document regions and their reading order. Xiaomi-OCR-0 reads the detected regions. Together they provide text alongside the boxes shown in the Annotated tab.

## Xiaomi-OCR-0

[Xiaomi-OCR-0](https://huggingface.co/xiaomi-research/Xiaomi-OCR-0) is Xiaomi Research's 0.8B vision-language model for document parsing and OCR-related understanding. Its [official guide](https://github.com/xiaomi-research/Xiaomi-OCR-0) describes whole-page parsing and region parsing. The model card gives separate prompts for text, tables and formulas. The documented outputs include plain text, OTSL table markup and LaTeX; upstream postprocessing can convert OTSL into HTML tables. The model also supports other tasks, such as question answering and key information extraction, which this app does not expose. [Official task prompts](https://huggingface.co/xiaomi-research/Xiaomi-OCR-0#task-prompts)

Whole-page parsing can produce a document without a separate layout model. DocFlow uses detected regions because it also needs page annotations and structured blocks with coordinates. Xiaomi's published document-parsing benchmarks use a two-stage method; those scores do not establish accuracy for this implementation. Xiaomi recommends whole-page parsing for handwriting, historical books, scene text and irregular layouts because crop boundaries can lose context. DocFlow currently uses whole-page parsing only if detection returns no usable regions. [Official repository](https://github.com/xiaomi-research/Xiaomi-OCR-0#what-it-does)

## PP-DocLayoutV3

[PP-DocLayoutV3](https://huggingface.co/PaddlePaddle/PP-DocLayoutV3) is PaddlePaddle's document layout model. Its [Transformers-compatible Safetensors checkpoint](https://huggingface.co/PaddlePaddle/PP-DocLayoutV3_safetensors) predicts region classes, bounding geometry and reading order. The official examples use `AutoImageProcessor` and `AutoModelForObjectDetection`, then postprocess results with the page dimensions. The detector identifies where content is located; Xiaomi supplies the recognized content. [Transformers guide](https://huggingface.co/docs/transformers/en/model_doc/pp_doclayout_v3)

DocFlow uses the Safetensors distribution with Transformers, so its local Windows pipeline does not need the Paddle runtime.

## What happens to a page

1. PDFium renders a selected PDF page, or Pillow reads an image frame. The page is bounded to 2048 pixels per dimension.
2. V3 detects regions at confidence threshold 0.25. DocFlow keeps the highest-scoring detection for each reading-order value, sorts the remaining regions by that value, clamps rectangles to the page and discards empty rectangles. It retains the class, confidence, reading order, rectangle and polygon.
3. Xiaomi processes rectangular crops sequentially. Category 21 uses the table prompt, categories 5 and 15 use the formula prompt, and all other detected categories use the text prompt, including image regions. Decoding is deterministic with thinking disabled and at most 4096 new tokens per crop.
4. Adapted Xiaomi postprocessing normalizes output and converts OTSL tables to HTML. DocFlow joins block content in detector order and saves Markdown, HTML, JSON, chunks, page previews and annotated images. The annotation images show rectangles; polygon points remain in JSON.
5. With no usable detections, Xiaomi receives the whole page and the result carries a warning and page-level box. Failed or truncated recognition is marked incomplete.

The current deduplication uses reading-order values rather than geometric overlap. Distinct detections sharing a value can therefore be dropped. This integration differs from Xiaomi's full benchmark pipeline and needs evaluation on representative documents, especially dense or irregular pages.

## Versions and execution

The pinned model IDs and revisions are defined in [`docflow/xiaomi.py`](../docflow/xiaomi.py):

| Purpose | Repository | Revision |
| --- | --- | --- |
| Recognition | `xiaomi-research/Xiaomi-OCR-0` | `bbd8cf8d21f256b3644b44cb860f3a7cecb93c30` |
| Layout | `PaddlePaddle/PP-DocLayoutV3_safetensors` | `e4f489dc536556fc1be02b973ba06756e0d4a2ac` |

The Windows Streamlit app loads cached models on the local GPU when parsing starts. The separate Gradio Space uses the same engine on its allocated GPU; its deployment has not been verified. See the [developer guide](developer-guide.md) for setup, dependencies and output storage, and [migration validation](xiaomi-migration-validation.md) for the synthetic checks performed so far.
