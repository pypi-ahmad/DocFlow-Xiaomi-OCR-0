> Historical audit of the Nemotron implementation. This is not a security audit of the current Xiaomi pipeline. See the [developer guide](../../developer-guide.md).

# DocFlow NIM security review and fixes

## Result and limits

The resumed standard audit reviewed the maintained first-party repository and corrected two resource-handling paths locally. **This is not a production security clearance.** No shared-service outage, cross-user disclosure or code-execution exploit was demonstrated. Both original resource hypotheses received independent candidate review as `needs_validation`; after correction, fresh independent source verifiers checked the fixes. The schema has no resolved verdict, so the two mitigated leads are retained as `rejected` with an explicit reason explaining the corrected worktree. They are not active confirmed vulnerabilities or evidence that the old implementation was safe.

The reviewed source is the dirty worktree based on commit `1993506958b162b97d76bda16939b5c1079109f4`, including the earlier Gradio additions and this task's fixes. The metadata records before/after source hashes. Profile: standard; no strict agent budget; 15 agent assignments completed against an initial estimate of20. No prior compatible ledger was available in the workspace audit root. No prior same-source confirmations were excluded or carried.

## Corrective changes

| Source lead | Previous behavior | Corrected behavior |
| --- | --- | --- |
| Selected PDF pages | Preflight and conversion rendered preceding pages before checking the selected range. | Preflight reads page metadata. Rendering indexes only selected PDF pages; original page numbers remain in exports. |
| Decoded image allocation | RGB expansion preceded output thumbnailing without an application pixel budget. | A shared40-megapixel guard rejects oversized or nonpositive dimensions before RGB expansion in document loading and the local worker. Each selected frame is checked. |

The worker now imports the shared guard. Its Docker build uses the repository root as context; a new `.dockerignore` allowlist sends only the worker sources and guard. The user guide contains the matching build command. README cleanup wording distinguishes session directories from framework-cached downloads instead of promising exact one-hour revocation of every copy.

## Checks observed

Eight focused checks passed inside an offline, read-only container: six new unittest cases plus two existing small fixture functions. They cover metadata-only preflight, rejecting more than five selected pages without rasterization, rendering only the selected PDF page, preserving original page numbering, rejecting oversized dimensions before RGB conversion, the exact pixel boundary, selecting the correct real small TIFF frame, session-root separation and batch archive naming.

PDFium was mocked to count calls without expensive documents. The cached image supplied Pillow for the small TIFF fixture. Missing unrelated bleach/markdown2 dependencies were stubbed; these checks do not establish sanitizer behavior. The existing fixture functions ran through a minimal raises adapter rather than a complete pytest installation. The full test suite, a real PDFium decode, GPU model inference, rebuilt worker image and browser/Gradio integration were not run during this task. Source type checks passed. Changed-file Ruff checks passed with the pre-existing broad-exception rule BLE001 excluded; the diff whitespace check passed.

Sandbox settings: cached image only (`--pull never`), no network, no IPC sharing, unprivileged uid1000, read-only root/toolchain/source, dropped capabilities, no-new-privileges, read-only shared-memory/message directories, and one writable32MiB scratch tmpfs. Limits: one CPU,256MiB memory,32 processes,20CPU seconds,45seconds wall time,5MiB per output file and64 file descriptors. Execution began from an empty environment with only safe PATH, HOME/TMPDIR/cache paths under scratch and bytecode writes disabled. Only allowlisted source and tests were exposed; no host credentials, model files, original user documents, other agent directories or retained artifacts were mounted. No scratch execution output was promoted as audit evidence. Ledger evidence remains source-only (`artifact:null`).

The mandatory unmodified findings and coverage validators now run successfully using the Linux Node executable in an already-cached image. The original Windows Node failure was a tooling limitation, not an application vulnerability. No dependency installation or live audit probe was used.

## Confirmed findings

None. The two reviewed resource leads were mitigated locally without escalating unproved shared availability impact into a confirmed severity.

## Remaining validation gaps

Some framework/session/file-serving/cache guarantees, the effective settings of a pre-existing worker container, current dependency advisories and the deployed framework dependency set remain unverified. These are blocked coverage areas, not confirmed vulnerabilities and not open schema-shaped vulnerability leads. `NEEDS-VALIDATION.md` lists safe owner-observed follow-up work. Do not infer missing infrastructure controls from their absence in first-party source.

## Coverage

The ledger contains29 units: covered=18, candidate=4, blocked=7, deferred=0. The four historical candidate units link to two final mitigated/rejected records; there are zero unadjudicated candidate fingerprints. Both post-wave and distinct final-clean critics returned no additional units or reassignments. Blocked units are not counted as covered, and no exhaustive coverage claim is made.

Scope includes Gradio, Streamlit, the shared converter, worker, launcher, manifests, tests and maintained documentation. Ignored user data, credentials, model weights, indexes and caches were excluded. Third-party native implementations, cloud control planes and advisory databases were not audited as first-party source. Positive source patterns include session/job namespaces, fixed output filenames, a fixed provider URL, server-only credential use, immutable model revision and narrow HTML export sanitization. Optional future hardening includes resolved deployment locks, bounded per-session retention and explicit Clear/job ordering; none became a demonstrated vulnerability in this pass.

## Deployment

This task did not publish or deploy the security changes. Rebuild the local worker with the documented root-context command and deploy the updated Space sources before assuming the new guards are active there. The audit sent no traffic to the live app. Existing user edits and Git history were preserved; reports remain locally ignored and were not published.
