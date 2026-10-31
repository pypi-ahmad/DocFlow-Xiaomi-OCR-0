# PP-DocLayoutV4 checkpoint access

> This records the earlier V4 access investigation. The application now uses PP-DocLayoutV3_safetensors; see the [developer guide](developer-guide.md).

Checked 2026-10-31.

The [Transformers documentation](https://huggingface.co/docs/transformers/en/model_doc/pp_doclayout_v4) provides the inference API and names `PaddlePaddle/PP-DocLayoutV4_safetensors` as its checkpoint. It does not itself provide trained weights.

The [Transformers integration pull request](https://github.com/huggingface/transformers/pull/48387) states that the checkpoint repository is private until the official release. The [upstream integration test](https://github.com/huggingface/transformers/blob/main/tests/models/pp_doclayout_v4/test_modeling_pp_doclayout_v4.py) remains skipped pending publication of the weights. The configured Hugging Face token authenticated successfully during this investigation, but requests for `PaddlePaddle/PP-DocLayoutV4_safetensors` and `PaddlePaddle/PP-DocLayoutV4` returned HTTP 404. This establishes that the current account cannot access those repository IDs; it does not prove whether access is offered to other accounts.

No public access request form or release date was found in these primary sources. A new token does not by itself grant access to a private repository.

## Practical next steps

1. Watch the [Transformers pull request](https://github.com/huggingface/transformers/pull/48387) for the promised publication update, or ask its authors in a comment whether early access or a release date is available. This is a suggested inquiry, not a documented access process.
2. Alternatively, ask the maintainers through [PaddleOCR Discussions](https://github.com/PaddlePaddle/PaddleOCR/discussions); their [documentation](https://www.paddleocr.ai/main/en/index/) directs non-bug questions to Discussions. Ask for the official checkpoint URL, availability, and license.
3. Once the maintainers provide a public checkpoint or explicitly grant the Hugging Face account access, retry the repository with that account's token. Do not post a token in a public discussion.

No message was sent to maintainers, and no checkpoint was downloaded or tested.
