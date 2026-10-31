"""Pinned native Transformers layout and recognition pipeline."""

import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast

OCR = "xiaomi-research/Xiaomi-OCR-0"
OCR_REV = "bbd8cf8d21f256b3644b44cb860f3a7cecb93c30"
LAYOUT = "PaddlePaddle/PP-DocLayoutV3_safetensors"
LAYOUT_REV = "e4f489dc536556fc1be02b973ba06756e0d4a2ac"
CACHE = Path(__file__).resolve().parents[1] / ".models"


@dataclass
class PageResult:
    content: str
    finish_reason: str
    usage: dict
    markdown: str
    blocks: list
    warnings: list

    @property
    def complete(self):
        return self.finish_reason == "stop"


class Engine:
    def __init__(self, *, offline=True):
        import torch
        from huggingface_hub import snapshot_download
        from transformers import (
            AutoImageProcessor,
            AutoModelForImageTextToText,
            AutoModelForObjectDetection,
            AutoProcessor,
        )

        self.torch = torch
        self.lock = threading.Lock()
        paths = [snapshot_download(repo, revision=revision, cache_dir=CACHE,
                                   local_files_only=offline)
                 for repo, revision in ((OCR, OCR_REV), (LAYOUT, LAYOUT_REV))]
        self.processor = AutoProcessor.from_pretrained(paths[0], local_files_only=True)
        self.model = cast(Any, AutoModelForImageTextToText.from_pretrained(
            paths[0], dtype=torch.float16, local_files_only=True,
            attn_implementation="sdpa")).to("cuda").eval()
        self.detector_processor = AutoImageProcessor.from_pretrained(paths[1], local_files_only=True)
        self.detector = AutoModelForObjectDetection.from_pretrained(
            paths[1], local_files_only=True).to("cuda").eval()

    def recognize(self, image, prompt):
        messages = [{"role": "user", "content": [
            {"type": "image", "image": image}, {"type": "text", "text": prompt}]}]
        inputs = self.processor.apply_chat_template(
            messages, tokenize=True, add_generation_prompt=True, enable_thinking=False,
            return_dict=True, return_tensors="pt").to("cuda")
        output = self.model.generate(**inputs, max_new_tokens=4096, do_sample=False)
        generated = output[0, inputs["input_ids"].shape[-1]:]
        eos = self.model.generation_config.eos_token_id
        eos = eos if isinstance(eos, list) else [eos]
        complete = len(generated) > 0 and generated[-1].item() in eos
        return self.processor.decode(generated, skip_special_tokens=True), complete, len(generated)

    def __call__(self, image):
        with self.lock, self.torch.inference_mode():
            return self.parse(image)

    def parse(self, image):
        from docflow.xiaomi_postprocess.document import finalize_document

        inputs = self.detector_processor(images=image, return_tensors="pt").to("cuda")
        detected = self.detector_processor.post_process_object_detection(
            self.detector(**inputs), threshold=0.25, target_sizes=[image.size[::-1]])[0]
        blocks: list[dict[str, Any]] = []
        warnings, seen = [], set()
        width, height = image.size
        candidates = sorted(range(len(detected["scores"])),
                            key=lambda i: float(detected["scores"][i]), reverse=True)
        selected = []
        for i in candidates:
            order = int(detected["order_seq"][i])
            if order not in seen:
                selected.append(i)
                seen.add(order)
        selected.sort(key=lambda i: int(detected["order_seq"][i]))
        for i in selected:
            box = detected["boxes"][i].tolist()
            box = [max(0, min(limit, value)) for value, limit in zip(box, [width, height, width, height])]
            if box[2] <= box[0] or box[3] <= box[1]:
                continue
            category = int(detected["labels"][i])
            blocks.append({"class": self.detector.config.id2label[category],
                           "category_id": category, "confidence": float(detected["scores"][i]),
                           "reading_order": int(detected["order_seq"][i]),
                           "bbox_pixels": box, "bbox": [v / d for v, d in zip(box, [width, height, width, height])],
                           "polygon": [list(map(float, point)) for point in detected["polygon_points"][i]]})
        if len(selected) >= 300:
            warnings.append("Layout detection reached its query capacity; review this page for missing regions.")
        if not blocks:
            warnings.append("No usable layout detections; using page-level OCR geometry.")
            blocks = [{"class": "Page", "category_id": -1, "bbox_pixels": [0, 0, width, height],
                       "bbox": [0, 0, 1, 1], "reading_order": 0}]
        total = 0
        for block in blocks:
            category = block["category_id"]
            prompt = ("Parse the table in the image into OTSL." if category == 21 else
                      "Identify the formula in the image and represent it using LATEX format." if category in (5, 15) else
                      "Extract the text in the image.")
            if category == -1:
                prompt = "Parse this document into Markdown. Preserve all visible text, headers and footers. Represent tables using OTSL and formulas using LaTeX."
            try:
                raw, complete, tokens = self.recognize(image.crop(block["bbox_pixels"]), prompt)
                total += tokens
                content = finalize_document(raw)
                if category in (5, 15) and content.strip() and not content.strip().startswith("$"):
                    delimiter = "$$" if category == 5 else "$"
                    content = delimiter + content.strip() + delimiter
                block.update(raw=raw, text=content, content=content, complete=complete)
            except (RuntimeError, ValueError, OSError) as exc:
                block.update(raw="", text="", content="", complete=False, error=type(exc).__name__)
                warnings.append("A region could not be recognized.")
        markdown = "\n\n".join(b["content"] for b in blocks)
        return PageResult("\n\n".join(b["raw"] for b in blocks),
                          "stop" if all(b["complete"] for b in blocks) else "incomplete",
                          {"output_tokens": total}, markdown, blocks, warnings)
