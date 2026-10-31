from docflow.xiaomi_postprocess.document import finalize_document


def test_table_cells_escape_html():
    result = finalize_document('<fcel><script>alert(1)</script><fcel>Total<nl><fcel>A<fcel>42<nl>')
    assert "<table>" in result
    assert "<script>" not in result
    assert "&lt;script&gt;" in result


def test_math_and_plain_text_survive():
    assert "Header" in finalize_document("Header\n\nFooter")
    assert "x" in finalize_document(r"\[x\]")
