from huggingface_hub import snapshot_download
from docflow.xiaomi import CACHE, OCR, OCR_REV, LAYOUT, LAYOUT_REV
for repo, revision in ((OCR, OCR_REV), (LAYOUT, LAYOUT_REV)):
    snapshot_download(repo, revision=revision, cache_dir=CACHE)
