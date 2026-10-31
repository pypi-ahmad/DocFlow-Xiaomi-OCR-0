import json,hashlib
from collections import Counter
from pathlib import Path
out=Path('docs/security-audit/run-1'); ledger=json.loads((out/'coverage-ledger.json').read_text()); records=json.loads((out/'findings.json').read_text()); counts=Counter(u['status'] for u in ledger)
for rec in records:
 rec['description']=rec['description'].replace('independent final review pending.','fresh independent final source verification passed.')
(out/'findings.json').write_text(json.dumps(records,indent=2))
v=json.loads((out/'verification-results.json').read_text());v['implementation_checks']['existing_fixture_functions']=2;v['implementation_checks']['total_checks_passed']=8;v['final_clean_critic']={'agent':'critic_final_clean','missing_units':[],'reassign_ids':[],'stop':True};(out/'verification-results.json').write_text(json.dumps(v,indent=2))
report='''# DocFlow NIM security review and fixes

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

'''
report+=f"The ledger contains29 units: covered={counts['covered']}, candidate={counts['candidate']}, blocked={counts['blocked']}, deferred={counts['deferred']}. The four historical candidate units link to two final mitigated/rejected records; there are zero unadjudicated candidate fingerprints. Both post-wave and distinct final-clean critics returned no additional units or reassignments. Blocked units are not counted as covered, and no exhaustive coverage claim is made.\n\n"
report+='''Scope includes Gradio, Streamlit, the shared converter, worker, launcher, manifests, tests and maintained documentation. Ignored user data, credentials, model weights, indexes and caches were excluded. Third-party native implementations, cloud control planes and advisory databases were not audited as first-party source. Positive source patterns include session/job namespaces, fixed output filenames, a fixed provider URL, server-only credential use, immutable model revision and narrow HTML export sanitization. Optional future hardening includes resolved deployment locks, bounded per-session retention and explicit Clear/job ordering; none became a demonstrated vulnerability in this pass.

## Deployment

This task did not publish or deploy the security changes. Rebuild the local worker with the documented root-context command and deploy the updated Space sources before assuming the new guards are active there. The audit sent no traffic to the live app. Existing user edits and Git history were preserved; reports remain locally ignored and were not published.
'''
(out/'REPORT.md').write_text(report,encoding='utf-8')
(out/'FINDINGS-DETAIL.md').write_text('''# Finding details

No confirmed medium, high or critical findings were established. The two source-grounded resource leads were corrected locally and independently rechecked; their final schema verdict is rejected with a mitigation explanation. See REPORT.md and findings.json for the exact distinction between fixed source paths and unproved historical shared-service impact.

The PDF correction is in docflow/conversion.py:31,52,97 and docflow/space_ui.py:33. The image guard is in docflow/image_limits.py:6, docflow/conversion.py:40,68 and runtime/server.py:41. Bounded regression cases are in tests/test_document_limits.py. No exploit or availability proof is claimed.
''',encoding='utf-8')
(out/'NEEDS-VALIDATION.md').write_text('''# Remaining validation gaps

There are no active independently adjudicated needs_validation vulnerability records. The two initial resource hypotheses were mitigated in local source and checked by fresh final source reviewers. The following coverage gaps remain; no severity is assigned.

1. **Gradio session and file binding:** inspect the pinned Gradio6.31 implementation or use a bounded isolated dummy-session fixture to verify State cannot be replaced across sessions, uploaded paths are scoped, and File/Gallery download references have the intended capability scope. No cross-session read was demonstrated.
2. **Cleanup and queued work:** inspect framework cache/State expiry and, in an isolated dummy fixture with a stub parser, examine Clear versus queued work and cached downloads. Current documentation distinguishes session-directory cleanup from framework caches. Do not assume Clear revokes an already shared or copied download.
3. **Existing worker configuration:** owner-observed configuration should establish image identity, loopback publication, read-only model mount and absence of unexpected privileged mounts for the reused named container. The maintained new-container path is explicit; manipulation by an equally privileged Docker operator is not treated as a lower-trust exploit.
4. **Dependencies:** obtain authoritative advisory evidence for resolved Windows, Space and worker dependencies; exact deployed dependency versions and framework routes/headers were not established by manifests alone. Do not infer CVE-free status from this source review.
5. **Runtime containment:** the source fixes remove skipped-page rasterization and add explicit pixel checks, but do not establish a bound for every native decoder allocation, framework header scan, queue or aggregate session resource. Any additional investigation must use small dummy fixtures under strict resource limits. Production configuration questions should use existing owner-observed evidence, not adversarial uploads or load tests.
6. **Rollout:** local code changes are not deployment evidence. A rebuilt worker and updated Space release are separate rollout steps; no live control plane was contacted for this security task.

No live-probe instructions are supplied. See REPORT.md for the mocked-PDF and cached-Pillow limits of the eight focused implementation checks.
''',encoding='utf-8')
arch=(out/'architecture.md').read_text(); arch+='\n## Resumed corrective pass\nThe original Windows validator blocker was resolved using an existing Linux Node runtime in an isolated cached container. All29 units were assigned to source hunters. The two resource leads received separate candidate and final source verification. Current preflight is metadata-only for PDFs, rendering receives the selected range, and a shared40MP image guard precedes RGB conversion. Eight focused implementation checks ran under the resource-limited network-none/read-only sandbox described in REPORT.md; no execution artifact was promoted. Framework/advisory/deployed-configuration coverage remains explicitly blocked.\n';(out/'architecture.md').write_text(arch)
m=json.loads((out/'run-metadata.json').read_text());m['pre_remediation_source_hashes']=m['source_hashes'];paths=sorted(set(m['source_hashes'])|{'.dockerignore','docflow/image_limits.py','tests/test_document_limits.py'});m['source_hashes']={p:hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in paths};m.update(run_status='in_progress',completed_phase='All six phases executed; final report validators pending.',agent_invocations=15,validator_errors={},sandbox_status='Eight bounded implementation checks passed in isolated cached Linux container; detailed limits in REPORT.md.',promotion_status='No execution artifacts promoted or used as local ledger evidence.',application_source_unchanged=False,source_changes_authorized_by='User: fix all security audits',remote_changes_performed=False,coverage_counts=dict(counts),final_unadjudicated_candidates=[],retained_record_verdicts={'rejected':2},execution_limit='Source-only security findings; isolated bounded implementation checks with dummy data and no retained execution evidence.');(out/'run-metadata.json').write_text(json.dumps(m,indent=2))
print('Reports updated. Coverage:',dict(counts))
