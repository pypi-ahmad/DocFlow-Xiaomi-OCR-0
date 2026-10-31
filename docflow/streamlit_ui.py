"""Presentation helpers; opening documents never invokes inference."""

import io
import json
from contextlib import closing
from zipfile import ZIP_DEFLATED, ZipFile

import bleach
import markdown2

from docflow.conversion import page_images

TAGS = {
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
    "hr",
}
ATTRIBUTES = {"td": ["rowspan", "colspan"], "th": ["rowspan", "colspan"]}


def safe_html(value):
    return bleach.clean(value, tags=TAGS, attributes=ATTRIBUTES, strip=True)


def markdown_text(result):
    return "\n\n---\n\n".join(page.get("markdown", "") for page in result["pages"])


def artifacts(result, directory):
    """Rebuild missing legacy artifacts in memory without changing saved files."""
    markdown = markdown_text(result)
    html_path = directory / "document.html"
    html = safe_html(
        html_path.read_text(encoding="utf-8")
        if html_path.exists()
        else str(markdown2.markdown(markdown, extras=["tables", "fenced-code-blocks"]))
    )
    chunks = [
        {"page": page["number"], **block}
        for page in result["pages"]
        for block in page.get("blocks", [])
    ]
    return {
        "document.md": markdown,
        "document.html": html,
        "document.json": json.dumps(result, ensure_ascii=False, indent=2),
        "chunks.json": json.dumps(chunks, ensure_ascii=False, indent=2),
    }


def archive_bytes(result, directory):
    buffer = io.BytesIO()
    generated = artifacts(result, directory)
    with ZipFile(buffer, "w", ZIP_DEFLATED) as archive:
        for name, content in generated.items():
            archive.writestr(name, content)
        for path in directory.iterdir():
            if path.is_file() and path.name not in generated:
                archive.write(path, path.name)
    return buffer.getvalue()


def preview_bytes(data, filename, page):
    with closing(page_images(data, filename, page, page)) as pages:
        image = next(pages)
        try:
            buffer = io.BytesIO()
            image.save(buffer, format="PNG")
            return buffer.getvalue()
        finally:
            image.close()
