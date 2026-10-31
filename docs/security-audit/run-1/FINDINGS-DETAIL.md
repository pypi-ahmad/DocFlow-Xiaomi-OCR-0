> Historical audit of the Nemotron implementation. This is not a security audit of the current Xiaomi pipeline. See the [developer guide](../../developer-guide.md).

# Finding details

No confirmed medium, high or critical findings were established. The two source-grounded resource leads were corrected locally and independently rechecked; their final schema verdict is rejected with a mitigation explanation. See REPORT.md and findings.json for the exact distinction between fixed source paths and unproved historical shared-service impact.

The PDF correction is in docflow/conversion.py:31,52,97 and docflow/space_ui.py:33. The image guard is in docflow/image_limits.py:6, docflow/conversion.py:40,68 and runtime/server.py:41. Bounded regression cases are in tests/test_document_limits.py. No exploit or availability proof is claimed.
