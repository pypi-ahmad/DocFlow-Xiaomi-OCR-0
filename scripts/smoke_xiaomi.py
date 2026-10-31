"""Run a synthetic page through both models without network access."""
import time

import torch
from PIL import Image, ImageDraw, ImageFont

from docflow.xiaomi import Engine


def main():
    image = Image.new("RGB", (800, 400), "white")
    ImageDraw.Draw(image).text(
        (40, 60), "DocFlow test invoice\nTotal 42.00",
        font=ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 32), fill="black",
    )
    start = time.monotonic()
    result = Engine(offline=True)(image)
    print({"complete": result.complete, "markdown": result.markdown,
           "seconds": round(time.monotonic() - start, 1),
           "peak_mib": round(torch.cuda.max_memory_allocated() / 1024**2)})
    assert result.complete and "42" in result.markdown
    assert result.blocks


if __name__ == "__main__":
    main()
