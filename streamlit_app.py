"""Local document workbench inspired by DocLayout's conversion workflow."""

import hashlib
import json
from pathlib import Path

import bleach
import streamlit as st

from docflow.conversion import ROOT, convert, page_count
from docflow.streamlit_ui import (
    ATTRIBUTES,
    TAGS,
    archive_bytes,
    artifacts,
    preview_bytes,
)

st.set_page_config(
    page_title="DocFlow Xiaomi OCR", page_icon=":material/description:", layout="wide"
)
st.title("DocFlow Xiaomi OCR")
st.caption("From scans and images to structured Markdown.")
st.caption(
    "Xiaomi-OCR-0 + PP-DocLayoutV3 · Local GPU · Models load when parsing starts"
)
st.session_state.setdefault("results", [])


@st.cache_resource
def local_engine():
    from docflow.xiaomi import Engine

    return Engine(offline=True)


files = st.sidebar.file_uploader(
    "PDF or image files",
    type=["pdf", "png", "jpg", "jpeg", "gif", "tif", "tiff", "webp"],
    accept_multiple_files=True,
    key="uploads",
    max_upload_size=200,
)
signature = hashlib.sha256(
    b"".join(hashlib.sha256(f.getvalue() + f.name.encode()).digest() for f in files)
).hexdigest()
if st.session_state.get("upload_signature", signature) != signature:
    st.session_state.results = []
    st.session_state.receipts = []
    for key in (
        "start",
        "end",
        "input_page",
        "active_result",
        "result_tabs",
        "preview_cache",
    ):
        st.session_state.pop(key, None)
st.session_state.upload_signature = signature
first, last, count = 1, None, 0
valid = bool(files)
if len(files) == 1:
    try:
        count = page_count(files[0].getvalue(), files[0].name)
        st.sidebar.caption(f"{count} page(s) · Pages are numbered from 1")
        first = int(
            st.sidebar.number_input(
                "Start page", min_value=1, max_value=max(count, 1), value=1, key="start"
            )
        )
        last = int(
            st.sidebar.number_input(
                "End page",
                min_value=1,
                max_value=max(count, 1),
                value=max(count, 1),
                key="end",
            )
        )
        valid = 1 <= first <= last <= count
        if not valid:
            st.sidebar.error("End page must be at least Start page.")
    except Exception:  # noqa: BLE001 -- document failures remain local to the upload
        valid = False
        st.sidebar.error(
            "Could not inspect this document. Check its format and limits."
        )
elif files:
    st.sidebar.caption(f"{len(files)} files · All pages · Processed sequentially")
st.sidebar.caption("Processed locally · 200 MiB per file · Images up to 40 megapixels")
if st.sidebar.button(
    "Parse documents", type="primary", width="stretch", disabled=not valid
):
    st.session_state.results = []
    st.session_state.receipts = []
    for upload in files:
        with st.status(f"Parsing {upload.name}") as status:
            try:
                result, directory = convert(
                    upload.getvalue(),
                    upload.name,
                    "offline",
                    first if len(files) == 1 else 1,
                    last if len(files) == 1 else None,
                    page_parser=local_engine(),
                    progress=lambda page: status.update(label=f"Processed page {page}"),
                )
                st.session_state.results.append((result, directory))
                label = "Complete" if result["complete"] else "Partial"
                st.session_state.receipts.append({"File": upload.name, "Status": label})
                status.update(
                    label=f"{upload.name} · {label}",
                    state="complete" if result["complete"] else "error",
                )
            except Exception:  # noqa: BLE001 -- preserve the rest of the batch
                st.session_state.receipts.append(
                    {"File": upload.name, "Status": "Failed"}
                )
                status.update(label=f"{upload.name} · Failed", state="error")
                st.error("Conversion failed. Check the document and local model setup.")
    st.session_state.pop("active_result", None)

saved = sorted((ROOT / "conversion_results").glob("*/document.json"))
if saved:

    def saved_label(path):
        try:
            return f"{json.loads(path.read_text(encoding='utf-8'))['name']} · {path.parent.name[:8]}"
        except (ValueError, OSError, KeyError):
            return f"Unavailable · {path.parent.name[:8]}"

    selected = st.sidebar.selectbox("Saved conversion", saved, format_func=saved_label)
    if st.sidebar.button("Open saved conversion"):
        try:
            result = json.loads(selected.read_text(encoding="utf-8"))
            if not isinstance(result.get("pages"), list) or not result["pages"]:
                raise ValueError("No pages")
            st.session_state.results = [(result, selected.parent)]
            st.session_state.pop("active_result", None)
            st.session_state.receipts = []
        except (ValueError, OSError, KeyError):
            st.sidebar.error("This saved conversion could not be opened.")

if st.session_state.get("receipts"):
    st.dataframe(st.session_state.receipts, hide_index=True, width="stretch")
results = st.session_state.results
result, directory = None, None
if results:
    index = st.sidebar.selectbox(
        "Result document",
        range(len(results)),
        format_func=lambda i: f"{i + 1}. {results[i][0]['name']}",
        key="active_result",
    )
    result, directory = results[index]
    directory = Path(directory)
    st.text(result["name"])
    if result["complete"]:
        st.sidebar.success(f"OCR complete · {len(result['pages'])} page(s)")
    else:
        st.warning(
            "Some pages are incomplete. Review page errors and warnings in Annotated."
        )
    st.sidebar.download_button(
        "Download ZIP",
        archive_bytes(result, directory),
        "document.zip",
        "application/zip",
        on_click="ignore",
    )
    with st.sidebar.popover("Clear results"):
        st.caption("Clear this view? Saved files stay on disk.")
        if st.button("Clear this view"):
            st.session_state.results = []
            st.session_state.receipts = []
            st.rerun()

if not files and not result:
    st.info("Upload PDFs or images in the sidebar, or open a saved conversion.")

tabs = st.tabs(
    ["Input preview", "Markdown", "HTML", "Annotated", "JSON", "Chunks"],
    key="result_tabs",
    on_change="rerun",
)
context = directory.name if directory else signature
with tabs[0]:
    if tabs[0].open:
        if result:
            number = st.selectbox(
                "Preview page",
                [p["number"] for p in result["pages"]],
                key=f"source-{context}",
            )
            path = directory / f"page-{number}.png"
            if path.exists():
                st.image(str(path), width="stretch", alt=f"Original page {number}")
            else:
                st.info("Source preview unavailable for this saved result.")
        elif len(files) == 1 and count:
            page = int(
                st.number_input(
                    "Preview page",
                    min_value=1,
                    max_value=count,
                    value=1,
                    key="input_page",
                )
            )
            try:
                cache_key = (signature, page)
                if st.session_state.get("preview_cache", (None,))[0] != cache_key:
                    st.session_state.preview_cache = (
                        cache_key,
                        preview_bytes(files[0].getvalue(), files[0].name, page),
                    )
                st.image(
                    st.session_state.preview_cache[1],
                    width="stretch",
                    alt=f"Input page {page}",
                )
            except Exception:  # noqa: BLE001 -- preview must not discard results
                st.warning("Preview unavailable for this page.")
        elif files:
            st.caption(
                "Parse the batch, then select a result document to preview its pages."
            )

if result:
    for tab, name, label, mime in (
        (tabs[1], "document.md", "Markdown", "text/markdown"),
        (tabs[2], "document.html", "HTML", "text/html"),
        (tabs[4], "document.json", "JSON", "application/json"),
        (tabs[5], "chunks.json", "Chunks", "application/json"),
    ):
        with tab:
            if tab.open:
                value = artifacts(result, directory)[name]
                st.download_button(
                    f"Download {label}", value, name, mime, on_click="ignore"
                )
                if label == "Markdown":
                    view = st.segmented_control(
                        "Markdown view",
                        ["Rendered", "Raw"],
                        default="Rendered",
                        key=f"markdown-{context}",
                    )
                    if view == "Raw":
                        st.code(value, language="markdown", wrap_lines=True)
                    else:
                        st.markdown(
                            bleach.clean(
                                value, tags=TAGS, attributes=ATTRIBUTES, strip=True
                            ),
                            unsafe_allow_html=True,
                        )
                elif label == "HTML":
                    view = st.segmented_control(
                        "HTML view",
                        ["Rendered", "Raw"],
                        default="Rendered",
                        key=f"html-{context}",
                    )
                    if view == "Raw":
                        st.code(value, language="html", wrap_lines=True)
                    else:
                        st.html(value)
                else:
                    st.json(value)
    with tabs[3]:
        if tabs[3].open:
            number = st.selectbox(
                "Annotated page",
                [p["number"] for p in result["pages"]],
                key=f"annotation-{context}",
            )
            page = next(p for p in result["pages"] if p["number"] == number)
            for warning in page.get("warnings", []):
                st.warning(warning)
            if page.get("error"):
                st.error(page["error"])
            path = directory / f"annotated-{number}.png"
            if path.exists():
                st.image(
                    str(path), width="stretch", alt=f"Detected layout on page {number}"
                )
                st.download_button(
                    "Download page PNG",
                    path.read_bytes(),
                    path.name,
                    "image/png",
                    on_click="ignore",
                )
            else:
                st.info("Annotations unavailable for this page.")
else:
    for tab in tabs[1:]:
        with tab:
            if tab.open:
                st.caption(
                    "Parse documents or open a saved conversion to view this output."
                )
