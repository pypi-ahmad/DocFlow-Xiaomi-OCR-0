from types import SimpleNamespace
from unittest.mock import Mock

import numpy as np
from PIL import Image

from docflow.xiaomi import Engine


def test_layout_order_category_routing_and_partial_result():
    engine = Engine.__new__(Engine)
    engine.detector = Mock()
    engine.detector.config = SimpleNamespace(id2label={21: "table", 5: "formula"})
    engine.detector_processor = Mock(return_value=SimpleNamespace(to=lambda _: {}))
    engine.detector_processor.post_process_object_detection.return_value = [{
        "scores": np.array([.8, .9, .7]), "order_seq": np.array([2, 1, 2]),
        "labels": np.array([21, 5, 21]),
        "boxes": np.array([[0, 40, 100, 100], [-2, 0, 100, 30], [0, 40, 100, 100]]),
        "polygon_points": [[], [], []],
    }]
    engine.recognize = Mock(side_effect=[("x=1", True, 3), ("partial", False, 4)])
    result = engine.parse(Image.new("RGB", (100, 100)))
    assert [b["category_id"] for b in result.blocks] == [5, 21]
    assert result.blocks[0]["bbox_pixels"][0] == 0
    assert "LATEX" in engine.recognize.call_args_list[0].args[1]
    assert "OTSL" in engine.recognize.call_args_list[1].args[1]
    assert result.usage["output_tokens"] == 7
    assert not result.complete


def test_empty_layout_uses_explicit_page_fallback():
    engine = Engine.__new__(Engine)
    engine.detector = Mock()
    engine.detector_processor = Mock(return_value=SimpleNamespace(to=lambda _: {}))
    engine.detector_processor.post_process_object_detection.return_value = [{"scores": []}]
    engine.recognize = Mock(return_value=("Hello", True, 1))
    result = engine.parse(Image.new("RGB", (80, 60)))
    assert result.warnings
    assert result.blocks[0]["bbox_pixels"] == [0, 0, 80, 60]
    assert result.markdown == "Hello"
