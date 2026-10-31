import io
from zipfile import ZipFile

from PIL import Image
from streamlit.testing.v1 import AppTest

from docflow.streamlit_ui import archive_bytes, artifacts, preview_bytes


def test_legacy_exports_are_safe_and_unique(tmp_path):
    result = {
        "name": "old.pdf",
        "complete": True,
        "pages": [{"number": 8, "markdown": "Hello", "blocks": [{"text": "Hello"}]}],
    }
    (tmp_path / "document.html").write_text(
        '<script>alert(1)</script><p onclick="bad()">Hello</p>'
    )
    generated = artifacts(result, tmp_path)
    assert "<script>" not in generated["document.html"]
    assert "onclick" not in generated["document.html"]
    assert '"page": 8' in generated["chunks.json"]
    with ZipFile(io.BytesIO(archive_bytes(result, tmp_path))) as archive:
        assert len(archive.namelist()) == len(set(archive.namelist())) == 4
    assert not (tmp_path / "chunks.json").exists()


def test_preview_selected_frame_only():
    source = io.BytesIO()
    Image.new("RGB", (10, 10), "red").save(
        source,
        format="TIFF",
        save_all=True,
        append_images=[Image.new("RGB", (10, 10), "blue")],
    )
    with Image.open(
        io.BytesIO(preview_bytes(source.getvalue(), "test.tiff", 2))
    ) as page:
        assert page.getpixel((0, 0)) == (0, 0, 255)


def test_saved_result_tabs_and_selection_do_not_load_models(tmp_path, monkeypatch):
    import docflow.xiaomi

    def forbidden(*args, **kwargs):
        raise AssertionError("Navigation loaded models")

    monkeypatch.setattr(docflow.xiaomi, "Engine", forbidden)
    result = {
        "name": "one.pdf",
        "complete": False,
        "pages": [{"number": 8, "markdown": "Hello", "error": "Partial page"}],
    }
    second = {**result, "name": "two.pdf"}
    app = AppTest.from_file("../streamlit_app.py")
    app.session_state["results"] = [(result, tmp_path), (second, tmp_path)]
    app.run()
    assert not app.exception
    assert [tab.label for tab in app.tabs] == [
        "Input preview",
        "Markdown",
        "HTML",
        "Annotated",
        "JSON",
        "Chunks",
    ]
    app.selectbox(key="active_result").select(1).run()
    assert not app.exception
    assert any(text.value == "two.pdf" for text in app.text)
    for label in ("Markdown", "HTML", "Annotated", "JSON", "Chunks"):
        app.session_state["result_tabs"] = label
        app.run()
        assert not app.exception
