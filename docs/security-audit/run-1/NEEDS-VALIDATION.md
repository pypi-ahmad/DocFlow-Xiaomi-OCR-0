> Historical audit of the Nemotron implementation. This is not a security audit of the current Xiaomi pipeline. See the [developer guide](../../developer-guide.md).

# Remaining validation gaps

There are no active independently adjudicated needs_validation vulnerability records. The two initial resource hypotheses were mitigated in local source and checked by fresh final source reviewers. The following coverage gaps remain; no severity is assigned.

1. **Gradio session and file binding:** inspect the pinned Gradio6.31 implementation or use a bounded isolated dummy-session fixture to verify State cannot be replaced across sessions, uploaded paths are scoped, and File/Gallery download references have the intended capability scope. No cross-session read was demonstrated.
2. **Cleanup and queued work:** inspect framework cache/State expiry and, in an isolated dummy fixture with a stub parser, examine Clear versus queued work and cached downloads. Current documentation distinguishes session-directory cleanup from framework caches. Do not assume Clear revokes an already shared or copied download.
3. **Existing worker configuration:** owner-observed configuration should establish image identity, loopback publication, read-only model mount and absence of unexpected privileged mounts for the reused named container. The maintained new-container path is explicit; manipulation by an equally privileged Docker operator is not treated as a lower-trust exploit.
4. **Dependencies:** obtain authoritative advisory evidence for resolved Windows, Space and worker dependencies; exact deployed dependency versions and framework routes/headers were not established by manifests alone. Do not infer CVE-free status from this source review.
5. **Runtime containment:** the source fixes remove skipped-page rasterization and add explicit pixel checks, but do not establish a bound for every native decoder allocation, framework header scan, queue or aggregate session resource. Any additional investigation must use small dummy fixtures under strict resource limits. Production configuration questions should use existing owner-observed evidence, not adversarial uploads or load tests.
6. **Rollout:** local code changes are not deployment evidence. A rebuilt worker and updated Space release are separate rollout steps; no live control plane was contacted for this security task.

No live-probe instructions are supplied. See REPORT.md for the mocked-PDF and cached-Pillow limits of the eight focused implementation checks.
