import json,hashlib
from pathlib import Path
out=Path('docs/security-audit/run-1')
m=json.loads((out/'run-metadata.json').read_text(encoding='utf-8')); m.update(run_status='incomplete',incomplete_reason='mandatory_validators_unavailable_on_windows_node_no_follow_nonblocking',completed_phase='reconnaissance; coverage seeded but validation blocked before hunting',agent_invocations=4,prior_run_note='No prior compatible ledger found in workspace audit root.',validator_errors={'coverage':'OS no-follow and nonblocking input protection is unavailable','findings':'OS no-follow and nonblocking input protection is unavailable'},sandbox_status='Not established; target-controlled execution was prohibited and not performed.',promotion_status='Race-safe Windows directory-handle-relative artifact promotion not established; no scratch evidence promoted.',application_source_unchanged=all(Path(p).is_file() and hashlib.sha256(Path(p).read_bytes()).hexdigest()==v for p,v in m['source_hashes'].items()))
(out/'run-metadata.json').write_text(json.dumps(m,indent=2),encoding='utf-8')
us=json.loads((out/'coverage-ledger.json').read_text(encoding='utf-8'))
for u in us: u.update(status='deferred',unresolved=['Mandatory coverage validator cannot run: OS no-follow and nonblocking input protection unavailable in Windows Node. No hunter assignment permitted before successful seed validation.'])
(out/'coverage-ledger.json').write_text(json.dumps(us,indent=2),encoding='utf-8')
(out/'findings.json').write_text('[]\n',encoding='utf-8')
(out/'REPORT.md').write_text('''# DocFlow NIM security audit — incomplete

## Status and scope

**This is an incomplete full-repository audit, not a security clearance.** The mandatory coverage validator failed before the hunting phase, so no vulnerability candidates received the required independent validation. An empty findings file means no findings were adjudicated; it does not establish that the app is secure.

Profile: standard. Target: current dirty worktree based on commit `1993506958b162b97d76bda16939b5c1079109f4`, including uncommitted Gradio additions. Four baseline reconnaissance agents ran; hunting, coverage critics, candidate verification and final verification did not run. No strict agent budget was set; the initial estimate was 20 calls. No prior compatible ledger was found under the workspace audit root. No same-source confirmations were carried.

Scope covers the maintained first-party Gradio and Streamlit applications, shared parser/output code, local FastAPI worker, Windows launcher, dependency manifests, tests and documentation. Ignored user documents/results, credentials, weights, model caches and graph databases were not audited. Native decoder and framework implementations are not assessed as whole dependency codebases. Current external advisory coverage and deployed platform controls were not assessed.

## Exact blocker

Both supplied validators return:

```text
OS no-follow and nonblocking input protection is unavailable
```

The installed Windows Node runtime cannot supply the protections required by the validators. The only available WSL distribution is Docker Desktop; a read-only command lookup found no Linux Node executable there. The audit did not install dependencies, modify the validators, or weaken their file-opening safeguards.

Separately, no complete OS-enforced sandbox was established with all required controls: no external network, an empty allowlisted environment, read-only target/toolchain, scratch-only writes, and CPU/memory/process/file-size/disk/wall-clock limits. A compliant Windows artifact-promotion implementation was also unestablished. Consequently no target code, tests, builds, browser fixtures or model inference ran during this audit. Trusted report generation and the supplied validators were the only audit-specific code executed. No deployed endpoint, provider API, real credential, user document or service control plane was tested. Prior functional deployment checks are not security evidence for this run.

## Reconnaissance results

- `app.py:14-19` downloads an immutable model revision and loads its executable model code. This establishes a model-publisher trust boundary, not evidence of a vulnerability.
- `app.py:62` and `docflow/space_ui.py:46-51` use server state, session temporary roots and fresh job directories. Framework state isolation and file routing still need the planned review.
- `docflow/space_ui.py:22-40` applies upload count/size and selected-page limits. `docflow/conversion.py:22-47` performs document decoding/rendering, including work outside the GPU reservation. Resource containment has not been validated.
- `app.py:76` enables Markdown sanitization; shared conversion applies a separate HTML export sanitizer. Rendering and derived-copy boundaries have not received hunter verification.
- `launch.cmd:9` binds Streamlit to loopback. `scripts/start-offline.ps1:17` publishes a newly created worker on loopback with a read-only model mount. Existing named-container reuse takes a different path; actual runtime settings were not inspected.
- `streamlit_app.py:70-77` lists the local global saved-results store. Its intended single-user local deployment must be distinguished from the public Gradio session model.
- `docflow/backends.py` uses a constant NVIDIA HTTPS destination and server-read credentials. No credential values were read or captured by the audit.
- The existing Streamlit export test can perform a worker health request; the ordinary test suite is not automatically an audit-isolated fixture.

These are architecture observations only. None is a confirmed finding or a validated vulnerability lead.

## Confirmed findings

None adjudicated. Hunting and independent verification were blocked.

## Needs validation

No schema-shaped vulnerability lead was independently adjudicated. See `NEEDS-VALIDATION.md` for the run-level blockers and safe resumption requirements.

## Coverage

29 planned deterministic coverage units were seeded: public state/files/lifecycle, input/resource limits, output rendering/secrets, local worker/container boundaries, and dependency/model build inputs. All 29 are explicitly **deferred**; covered=0, candidate=0, blocked=0, deferred=29. The coverage file itself did not pass the mandatory validator, so these counts describe the proposed plan, not completed coverage. No post-wave or final-clean coverage critic ran. There are no unvalidated candidate fingerprints to list.

## Resume safely

Resume in a compatible Linux audit environment with an already-installed Node runtime and the required sandbox controls. Run the unmodified coverage validator against `coverage-ledger.json` before any hunter assignment. Recheck current source hashes, mark changed source explicitly, and reseed deferred units as current planned work. Complete hunting, coverage critics, independent candidate validation, both validators, independent record verification, and report derivation. Execute any target fixtures only inside the required bounded sandbox with dummy data; do not probe the live Space.

Application source and the deployed Space were left unchanged by this audit. Reports are locally ignored via `.git/info/exclude` and were not published.
''',encoding='utf-8')
(out/'FINDINGS-DETAIL.md').write_text('# Finding details\n\nNo confirmed medium, high or critical records were adjudicated. This run stopped before hunting because mandatory validators were unavailable. See REPORT.md; this is not evidence of a clean security posture.\n',encoding='utf-8')
(out/'NEEDS-VALIDATION.md').write_text('''# Validation gaps

This file records run-level blockers, not vulnerability findings. No candidate received independent source verification, and no severity is assigned.

1. **Mandatory validators:** Windows Node refused protected file opening. Provide an already-installed compatible Linux Node runtime, retain the validators unchanged, and validate the seeded ledger before assigning hunters. The findings validator must also pass before final reporting.
2. **Execution sandbox:** Establish OS-enforced network isolation, empty safe environment, read-only target and toolchain, scratch-only writes, and explicit low resource/time limits before any target fixture or test runs. Use dummy uploads and principals only.
3. **Artifact promotion:** Establish trusted no-follow directory-handle-relative traversal, regular-file/single-link checks, bounded reads and exclusive destination creation, or retain source-only evidence with artifact:null.
4. **Unreviewed coverage:** All29 units remain deferred. Read the architecture and ledger; verify current source hashes, then resume the complete hunter/critic/verifier workflow. Do not treat prior functional Space smoke checks as audit validation.

No live-probe instructions are supplied. Platform configuration questions should be resolved by owner-observed configuration evidence, not traffic against the deployed Space.
''',encoding='utf-8')
print('Wrote all seven shared report/metadata files. Source hashes unchanged:',m['application_source_unchanged'])
