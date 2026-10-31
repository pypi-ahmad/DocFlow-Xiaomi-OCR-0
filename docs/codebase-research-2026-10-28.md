# DocLayout source research and conversion walkthrough

> This is a dated investigation of the neighboring DocLayout repository. The current DocFlow implementation uses Xiaomi-OCR-0 and PP-DocLayoutV3; see the [developer guide](developer-guide.md).

Date: 2026-10-28. Scope: the current local working tree, including existing uncommitted changes. This report describes the conversion pipeline; it does not represent a release audit or measured extraction accuracy. Application code and runtime prompts were not changed.

## Architecture and dependencies

DocLayout is a Python package with CLI, Streamlit GUI, and FastAPI entry points. The package manifest defines Python >=3.11,<4, core conversion dependencies, and separate `gui`, `server`, and document-format extras. Console commands dispatch to `doclayout.scripts`. [Source: pyproject.toml](../../DocLayout/pyproject.toml#L1)

The conversion layers have distinct responsibilities:

| Layer | Responsibility | Primary source |
| --- | --- | --- |
| CLI/configuration | Parse options, validate settings, choose converter/processors/renderer | [ConfigParser](../../DocLayout/doclayout/config/parser.py#L76) |
| Provider | Detect source format, validate limits, render page images and bounds | [provider registry](../../DocLayout/doclayout/providers/registry.py#L60), [PdfProvider](../../DocLayout/doclayout/providers/pdf.py#L18) |
| Layout | Load pinned PP-DocLayoutV3 artifacts, run ONNX inference, reconcile geometry and reading order | [layout.py](../../DocLayout/doclayout/layout.py#L594) |
| Extraction | Send page images and instructions to the configured structured-response model | [OpenAIService](../../DocLayout/doclayout/services/openai.py#L86) |
| Document model | Hold typed pages, blocks, structure, usage, and source lineage | [Document](../../DocLayout/doclayout/schema/document.py#L27), [DocumentBuilder](../../DocLayout/doclayout/builders/document.py#L27) |
| Processing/rendering | Group and refine blocks, sanitize HTML, render Markdown or other formats | [PdfConverter](../../DocLayout/doclayout/converters/pdf.py#L220), [MarkdownRenderer](../../DocLayout/doclayout/renderers/markdown.py#L423) |
| Export | Write representations, metadata, and extracted image crops | [output.py](../../DocLayout/doclayout/output.py#L139) |

The main dependency direction is CLI → converter → provider/builder → layout and model service → structured document → processors → renderer → filesystem export. The layout engine is process-cached; model artifacts own an HTTP client that callers close separately. [Sources: models.py](../../DocLayout/doclayout/models.py#L7), [PdfConverter](../../DocLayout/doclayout/converters/pdf.py#L220)

## Walkthrough: single-document PDF to Markdown

### 1. Enter through the command

`doclayout_single` invokes `convert_single_cli`. It builds a validated configuration, creates model artifacts, selects the converter and renderer, converts the source, saves output, prints usage, and closes the owned client in `finally`. Conversion errors become Click errors. [Source: convert_single.py](../../DocLayout/doclayout/scripts/convert_single.py#L13)

The newer `doclayout FILE OUTPUT_DIR` route builds the document once and passes it to the selected export generators. This is a separate export path from the older single-renderer command. [Source: convert.py](../../DocLayout/doclayout/scripts/convert.py#L21)

### 2. Resolve configuration and services

`PdfConverter.__init__` validates configuration, resolves optional processor overrides, and defaults to `MarkdownRenderer`. It copies the artifact dictionary. For a real `OpenAIService`, it creates a configured page service and, only when refinement is enabled, a refinement service sharing usage with that page service. Omitted CLI/API model choices resolve to `gpt-6.1-sol`; supported choices are Luna and Sol. [Sources: pdf.py](../../DocLayout/doclayout/converters/pdf.py#L102), [validation.py](../../DocLayout/doclayout/config/validation.py#L3)

The service copies configuration without replacing another converter's model settings. Its request semaphore is class-level and limits this service's in-process requests to three; this is not a cross-process limit. [Source: openai.py](../../DocLayout/doclayout/services/openai.py#L29)

### 3. Prepare layout and select a provider

`build_document` clears that converter's usage, prepares the layout engine, and chooses a provider by validated file contents, with an extension fallback. A layout preparation exception produces a conversion-local fallback engine; it does not stop page extraction. [Sources: pdf.py](../../DocLayout/doclayout/converters/pdf.py#L236), [registry.py](../../DocLayout/doclayout/providers/registry.py#L60), [layout.py](../../DocLayout/doclayout/layout.py#L180)

`PdfProvider` validates selected pages, rejects empty/out-of-range selections, and records page bounds in PDF points. Rendering uses a process-wide PDFium lock, checks raster pixel limits, renders form fields by default, and returns RGB PIL images. It deliberately supplies no embedded-text references. [Source: pdf.py provider](../../DocLayout/doclayout/providers/pdf.py#L23)

### 4. Render and extract pages

`DocumentBuilder` renders pages on the calling thread, then submits batches of up to three extraction tasks. Default rasterization is 192 DPI. Each page keeps its original page ID, PDF-space bounds, raster image, and initial empty block structure. Futures are consumed in submission order. [Source: document.py](../../DocLayout/doclayout/builders/document.py#L27)

Each worker runs local layout analysis and then a whole-page model request. Available layout contributes a prompt prior; layout exceptions use the original page prompt and record fallback. Model request failures propagate instead of becoming blank pages. [Source: document.py](../../DocLayout/doclayout/builders/document.py#L52)

The model receives the system prompt, page prompt, encoded page image, `ExtractedPage` response schema, medium reasoning, and `store=False`. An incomplete or missing parsed response raises `ExtractionError`; usage is recorded even when a request fails. [Source: openai.py](../../DocLayout/doclayout/services/openai.py#L86)

### 5. Validate and reconcile geometry

`ExtractedPage` requires blank pages to have no blocks and nonblank pages to have blocks. Each `ExtractedBlock` has an allowed block type, HTML, and a nonempty normalized 0–1000 rectangle. HTML is sanitized and nonvisual blocks must contain visible text. [Source: extraction.py](../../DocLayout/doclayout/schema/extraction.py#L71)

`reconcile` converts model rectangles to pixel coordinates, computes compatible geometry overlaps, greedily assigns one-to-one matches, and returns PDF-space boxes plus provenance. It preserves model text and block types. Matched blocks receive layout order within matched slots; unmatched blocks retain their slots. Ambiguity, split/merge overlaps, and unmatched regions become diagnostic issues. [Source: layout.py](../../DocLayout/doclayout/layout.py#L945)

The builder creates typed blocks, attaches source footprints, and records per-page runtime diagnostics. On an extraction/build exception, it waits for executor shutdown before closing rendered images. Successful images remain attached to pages for downstream rendering/cropping. [Source: document.py](../../DocLayout/doclayout/builders/document.py#L106)

### 6. Process and render

The converter builds structural groups, executes the configured processor sequence, sanitizes resulting HTML/descriptions, snapshots usage, and finalizes layout lineage. Refinement is optional; whole-page extraction is not disabled by turning refinement off. [Source: pdf.py](../../DocLayout/doclayout/converters/pdf.py#L249)

`MarkdownRenderer` renders the document tree, resolves HTML content references and image crops, converts HTML with Markdownify, cleans the text, and returns `MarkdownOutput(markdown, images, metadata)`. [Sources: markdown.py](../../DocLayout/doclayout/renderers/markdown.py#L423), [html.py](../../DocLayout/doclayout/renderers/html.py#L99)

### 7. Persist output

The single-renderer export writes timestamped text, a `_metadata.json` sidecar, and renamed image crops. The caller creates the destination directory. These filesystem writes occur after conversion and make no model requests. [Sources: output.py](../../DocLayout/doclayout/output.py#L139), [parser.py](../../DocLayout/doclayout/config/parser.py#L149)

## Runtime branches and side effects

- Layout uses one serialized session. Automatic device selection can retry on CPU after CUDA startup or runtime failure; explicit CUDA disables that CPU fallback. Conversion can still continue with model-only layout fallback. [Sources: layout.py](../../DocLayout/doclayout/layout.py#L799), [prepare_for_conversion](../../DocLayout/doclayout/layout.py#L180)
- Layout initialization may download hash-verified pinned artifacts; model calls send page images to the configured API. Local rasterization, geometry reconciliation, and final exports run locally. [Sources: model_files](../../DocLayout/doclayout/layout.py#L367), [OpenAIService](../../DocLayout/doclayout/services/openai.py#L98)
- Folder conversion optionally uses multiple spawned processes. Each process has its own service semaphore and layout session. Consequently, the three-request bound applies per process. [Sources: convert.py](../../DocLayout/doclayout/scripts/convert.py#L247), [openai.py](../../DocLayout/doclayout/services/openai.py#L35)
- `--skip_existing` uses output basename and the pipeline fingerprint. It does not verify source file contents. Documentation describes skipping an existing output representation, so this is a cache limitation rather than a demonstrated contract violation. [Sources: convert.py](../../DocLayout/doclayout/scripts/convert.py#L88), [output.py](../../DocLayout/doclayout/output.py#L56), [usage.md](../../DocLayout/docs/usage.md#L254)

## Review observations and verification limits

No confirmed must-fix defect was established in this focused upstream trace. The boundaries explicitly distinguish optional layout failure from extraction failure, preserve source provenance, and isolate per-converter model settings. These observations come from the source, not a live model accuracy test. [Sources: document.py](../../DocLayout/doclayout/builders/document.py#L52), [openai.py](../../DocLayout/doclayout/services/openai.py#L57)

The source retains rendered page images for the document lifetime and serializes local layout inference. Memory therefore scales with selected pages, and worker concurrency does not imply parallel ONNX sessions. These are capacity considerations, not measured regressions. [Sources: document.py](../../DocLayout/doclayout/builders/document.py#L78), [layout.py](../../DocLayout/doclayout/layout.py#L815)

Both graph tools were consulted before source tracing. The code-review-graph reported an October 2 index matching HEAD, while the working tree contained existing modifications; current source was used for behavioral claims. Live API requests and model downloads were not performed by this research task. Offline check results are recorded in the task's final review response.

## Walkthrough: saved conversion to extracted fields

The review also traced the downstream path independently of page conversion:

1. `process_file` checks for reusable source artifacts and a run matching the document and definition version. A cache hit returns the saved field result. [Source: batch.py](../../DocLayout/doclayout/ui/batch.py#L222)
2. `retry_fields` reads saved Markdown and metadata, allowing extraction to run without reconverting the PDF. [Source: batch.py](../../DocLayout/doclayout/ui/batch.py#L195)
3. `extract_fields` applies input-budget and classification routing, then calls the field model through `_call` using the snapshotted definition. [Sources: fields.py](../../DocLayout/doclayout/fields.py#L383), [_call](../../DocLayout/doclayout/fields.py#L172)
4. `ground_records` checks returned records against source text and existing chunks; `save_result` writes the outcome and definition to SQLite and attempts JSON exports. [Sources: fields.py](../../DocLayout/doclayout/fields.py#L268), [field_store.py](../../DocLayout/doclayout/field_store.py#L140)
5. The review page lists saved runs and loads the selected result. [Source: review.py](../../DocLayout/doclayout/scripts/app_pages/review.py#L26)

Data flow: saved raw Markdown plus chunks → definition-controlled model output → grounded field records and review issues → SQLite run/result JSON → review page. This downstream path consumes conversion evidence rather than requiring new page reads. [Sources: retry_fields](../../DocLayout/doclayout/ui/batch.py#L195), [extract_fields](../../DocLayout/doclayout/fields.py#L383)

## Critical Issues (Must Fix Before Merge)

No confirmed critical issue was established in the inspected paths. This is a bounded review of the current working tree, not a claim that every dependency or deployment configuration is secure.

## Warnings (Should Address)

### Input-budget changes reuse an earlier rejected field run

Locations: [definition fingerprint](../../DocLayout/doclayout/fields.py#L135), [run-cache match](../../DocLayout/doclayout/ui/batch.py#L278), [definition persistence](../../DocLayout/doclayout/field_store.py#L170).

`load_definition` reads `max_input_bytes`, but excludes it from the snapshot used to compute `definition.version`. The cache compares document identity and this version, so raising the budget can reuse a previously saved `needs_review` result instead of retrying a now-eligible document. Definition persistence also retains the first snapshot for that shared version:

```python
hashlib.sha256(snapshot.encode()).hexdigest()
```

```sql
INSERT OR IGNORE INTO definitions VALUES (?, ?)
```

The root review reproduced this offline with budgets of 1 and 900000 bytes: versions were identical; after saving the small-budget rejection, the larger-budget request returned `reused=True` and `needs_review`, with zero calls to `retry_fields`. A manual extraction retry is needed to recover. Even then, the stored definition can retain the earlier budget because the version key collides.

Why it matters: the active configuration and persisted audit snapshot can disagree, and changing the setting that caused rejection does not automatically recover the result. Include the budget in definition identity, or explicitly invalidate cached budget-dependent outcomes and persist the actual per-run settings.

## Suggestions (Nice to Have)

### Query the matching field run without loading all history

Locations: [FieldStore.runs](../../DocLayout/doclayout/field_store.py#L206), [per-document cache lookup](../../DocLayout/doclayout/ui/batch.py#L278).

The cache lookup scans `store.runs()`, which loads every run, including its serialized result JSON, for the complete history:

```python
for r in store.runs()
```

Why it matters: repeated uploads can pay for unrelated historical JSON on every lookup. This is a source-based growth risk, not a measured slowdown. A filtered latest-run query for `(document_id, definition_version)` would bound the data loaded; consider a supporting index when history size warrants it.

## Verification results

- Root offline suite: `uv run --no-sync pytest -q -m 'not integration' --ignore=tests/test_ui_browser.py` — **464 passed, 1 deselected in 33.13s**.
- Focused conversion, builder, service, and layout runtime/readiness suite — **99 passed in 14.01s**.
- Budget-cache reproduction — `same_version=True`, `reused=True`, `status='needs_review'`, `retry_calls=0`.
- Source-replacement cache observation — the existing representation was reused without creating a model client, consistent with the documented skip behavior.
- Browser tests, live API accuracy checks, and actual GPU/model-download execution were not run as part of this review.
