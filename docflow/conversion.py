"""Document rendering and common Xiaomi output processing."""

import hashlib
import io
import json
from pathlib import Path
from typing import Any

import bleach
import markdown2
import pypdfium2 as pdfium
from PIL import Image, ImageDraw

from docflow.image_limits import check_image_size
from docflow.xiaomi import LAYOUT, LAYOUT_REV, OCR
from docflow.xiaomi import OCR_REV as MODEL_REVISION

ROOT = Path(__file__).resolve().parents[1]


def _page_indexes(count, first, last):
    if count > 500:
        raise ValueError("Maximum document length is 500 pages.")
    if first < 1 or (last is not None and last < first):
        raise ValueError("Invalid page selection.")
    return range(first - 1, min(count, last if last is not None else count))


def page_count(data, filename):
    """Inspect page metadata without rasterizing pages or creating RGB copies."""
    if len(data) > 200 * 1024**2:
        raise ValueError("Maximum file size is 200 MiB.")
    if Path(filename).suffix.lower() == ".pdf":
        with pdfium.PdfDocument(data) as pdf:
            count = len(pdf)
    else:
        with Image.open(io.BytesIO(data)) as image:
            check_image_size(image.size)
            count = getattr(image, "n_frames", 1)
    _page_indexes(count, 1, None)
    return count


def page_images(data, filename, first=1, last=None):
    """Render selected pages only, preserving their order in the document."""
    if len(data) > 200 * 1024**2:
        raise ValueError("Maximum file size is 200 MiB.")
    if Path(filename).suffix.lower() == ".pdf":
        with pdfium.PdfDocument(data) as pdf:
            for index in _page_indexes(len(pdf), first, last):
                page = pdf[index]
                try:
                    scale = min(2048 / page.get_width(), 2048 / page.get_height())
                    bitmap = page.render(scale=scale)
                    try:
                        yield bitmap.to_pil().convert("RGB")
                    finally:
                        bitmap.close()
                finally:
                    page.close()
    else:
        with Image.open(io.BytesIO(data)) as image:
            count = getattr(image, "n_frames", 1)
            for index in _page_indexes(count, first, last):
                image.seek(index)
                check_image_size(image.size)
                page = image.convert("RGB")
                page.thumbnail((2048, 2048))
                yield page


def convert(data, filename, mode, first=1, last=None, progress=None, *,
            page_parser=None, output_root=None):
    if first < 1 or (last is not None and last < first):
        raise ValueError("Invalid page selection.")
    if page_parser is None:
        raise ValueError("Load the Xiaomi pipeline first.")
    identity = hashlib.sha256(
        data + json.dumps([mode, MODEL_REVISION, LAYOUT_REV, first, last, 2, 2048, 4096, 0.25, Path(filename).name]).encode()
    ).hexdigest()
    directory = (Path(output_root) if output_root is not None else ROOT / "conversion_results") / identity
    saved = directory / "document.json"
    if saved.exists():
        result = json.loads(saved.read_text(encoding="utf-8"))
        if result["complete"]:
            return result, directory
    directory.mkdir(parents=True, exist_ok=True)
    pages: list[dict[str, Any]] = []
    for number, image in enumerate(page_images(data, filename, first, last), first):
        (directory / f"annotated-{number}.png").unlink(missing_ok=True)
        image.save(directory / f"page-{number}.png")
        try:
            raw = page_parser(image)
            parsed = {"markdown": raw.markdown, "blocks": raw.blocks, "warnings": raw.warnings}
            item = {
                "number": number,
                "coordinate_frame": {"width": image.width, "height": image.height, "units": "pixels", "format": "xyxy"},
                "raw": raw.content,
                "finish_reason": raw.finish_reason,
                "usage": raw.usage,
                "complete": raw.complete,
                **parsed,
            }
            annotated = image.copy()
            draw = ImageDraw.Draw(annotated)
            for block in parsed["blocks"]:
                box = block.get("bbox_pixels")
                if box and len(box) == 4:
                    draw.rectangle(box, outline="red", width=2)
            annotated.save(directory / f"annotated-{number}.png")
        except Exception as exc:
            item = {
                "number": number,
                "complete": False,
                "error": str(exc),
                "markdown": "",
                "blocks": [],
            }
        pages.append(item)
        if progress:
            progress(number)
    if not pages:
        raise ValueError("No pages matched the selection.")
    result = {
        "schema_version": 2,
        "models": {"ocr": {"id": OCR, "revision": MODEL_REVISION}, "layout": {"id": LAYOUT, "revision": LAYOUT_REV}},
        "layout_model_revision": LAYOUT_REV,
        "name": Path(filename).name,
        "backend": mode,
        "local_model_revision": MODEL_REVISION if mode in ("offline", "space-gpu") else None,
        "complete": all(p["complete"] for p in pages),
        "pages": pages,
    }
    saved.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    markdown = "\n\n---\n\n".join(page["markdown"] for page in pages)
    (directory / "document.md").write_text(markdown, encoding="utf-8")
    html = bleach.clean(
        str(markdown2.markdown(markdown, extras=["tables", "fenced-code-blocks"])),
        tags={
            "p",
            "br",
            "strong",
            "em",
            "h1",
            "h2",
            "h3",
            "h4",
            "table",
            "thead",
            "tbody",
            "tr",
            "td",
            "th",
            "pre",
            "code",
            "ul",
            "ol",
            "li",
            "blockquote",
        },
        attributes={"td": ["rowspan", "colspan"], "th": ["rowspan", "colspan"]},
        strip=True,
    )
    (directory / "document.html").write_text(
        '<!doctype html><html><head><meta charset="utf-8"><title>Document</title></head><body>'
        + html
        + "</body></html>",
        encoding="utf-8",
    )
    chunks = [
        {"page": page["number"], **block} for page in pages for block in page["blocks"]
    ]
    (directory / "chunks.json").write_text(
        json.dumps(chunks, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return result, directory
