# Xiaomi-OCR-0 research

Researched on 2026-10-31 from the requested [GitHub repository](https://github.com/xiaomi-research/Xiaomi-OCR-0) and [Hugging Face model card](https://huggingface.co/xiaomi-research/Xiaomi-OCR-0), plus their linked primary sources. This is a research report; no model download, installation, inference, or application change was performed.

## Assessment for this project

The application now uses Xiaomi-OCR-0 with PP-DocLayoutV3_safetensors. V3 detects regions and reading order; Xiaomi recognizes crops. The implementation and pinned revisions are described in the [developer guide](developer-guide.md). Published benchmark results use a two-stage pipeline and do not establish this application's accuracy. [Evaluation pipeline](https://github.com/xiaomi-research/Xiaomi-OCR-0/blob/main/evaluation_pipeline/README.md)

Whole-page OCR is used when no usable regions are detected, with page-level geometry. The initial research preceded implementation; later synthetic GPU and offline checks are recorded in [migration validation](xiaomi-migration-validation.md).

## Model and outputs

The authors describe Xiaomi-OCR-0 as a 0.8B vision-language model based on Qwen3.5-0.8B-Base, trained on approximately 170 million OCR-centric samples. Its training combines text-location anchoring, continued pretraining, and mixed-task reinforcement learning. The authors released the weights and report in September 2026. [Model card](https://huggingface.co/xiaomi-research/Xiaomi-OCR-0), [technical report](https://arxiv.org/abs/2609.36136)

Document parsing produces ordered Markdown, tables in OTSL, and formulas in LaTeX. The repository's postprocessing converts OTSL tables to HTML in the final Markdown. The published whole-page prompt asks the model to ignore headers and footers, which may conflict with a requirement to preserve every page element; changing the prompt would need evaluation. [Model prompts](https://huggingface.co/xiaomi-research/Xiaomi-OCR-0#task-prompts), [evaluation pipeline](https://github.com/xiaomi-research/Xiaomi-OCR-0/blob/main/evaluation_pipeline/README.md)

The model also supports schema-directed key information extraction and document question answering. Those capabilities are outside this project's agreed scope. The source repository includes a browser demo and an MCP service for preparing PDFs and images, optional region detection, inference, and assembly. [Repository](https://github.com/xiaomi-research/Xiaomi-OCR-0), [model prompts](https://huggingface.co/xiaomi-research/Xiaomi-OCR-0#task-prompts)

## Execution and resources

The model card demonstrates whole-page inference through Transformers, using Python 3.13, `transformers==5.17.0`, `torch==2.14.0`, `torchvision==0.29.0`, and Pillow in its stated verified combination. The example selects CUDA, Apple MPS, or CPU, and accepts a local model directory. The repository also documents local SGLang and vLLM servers; they need versions supporting `Qwen3_5ForConditionalGeneration`. Its manual demo requires Python 3.10 or newer. These examples do not establish compatibility with this project's exact environment or GPU. [Transformers example](https://huggingface.co/xiaomi-research/Xiaomi-OCR-0#transformers), [repository installation](https://github.com/xiaomi-research/Xiaomi-OCR-0#manual-installation)

The requested Hugging Face repository lists a 1.75 GB `model.safetensors` file and approximately 1.77 GB for the repository as displayed. Those are download/storage figures, not measured inference memory requirements. The card also points to community GGUF conversions; the authors say their original benchmark results do not establish accuracy for those conversions. [File listing](https://huggingface.co/xiaomi-research/Xiaomi-OCR-0/tree/main), [conversion notes](https://huggingface.co/xiaomi-research/Xiaomi-OCR-0#community-model-conversions)

Local offline operation would require the model and all runtime assets to be present beforehand and the application to enforce network isolation; the local-directory example alone does not prove that the full runtime is offline-ready. The repository notes that its default server downloads the checkpoint on first launch if absent. [Model example](https://huggingface.co/xiaomi-research/Xiaomi-OCR-0#transformers), [repository setup](https://github.com/xiaomi-research/Xiaomi-OCR-0#manual-installation)

## Benchmarks and limitations

The authors report overall scores of 96.83 on OmniDocBench v1.6, 95.24 on Real5-OmniDocBench, and 87.94 on Wild-OmniDocBench. They state that these three document-parsing results use their two-stage method. The public evaluation procedure detects regions with PaddleX PP-DocLayoutV3 at threshold 0.25, recognizes crops, and assembles the page. These numbers cannot be treated as the expected score of whole-page-only inference. [Benchmark and scope](https://github.com/xiaomi-research/Xiaomi-OCR-0#key-performance), [evaluation procedure](https://github.com/xiaomi-research/Xiaomi-OCR-0/blob/main/evaluation_pipeline/README.md)

The authors recommend whole-page parsing for handwriting, historical books, scene text, and irregular layouts because incorrect region boundaries may lose context. Their experimental Ollama check reports seven input-token comparisons and five exact raw-output matches against an HF BF16 reference on Apple Silicon; they explicitly say this does not establish general accuracy parity. Neither finding establishes performance on this project's target documents or Windows GPU. [Repository usage and validation](https://github.com/xiaomi-research/Xiaomi-OCR-0)

The Hugging Face model card labels the model Apache-2.0, and the GitHub repository provides an Apache-2.0 license. Check the exact revision and third-party dependencies' terms before redistribution. [Model card](https://huggingface.co/xiaomi-research/Xiaomi-OCR-0), [repository license](https://github.com/xiaomi-research/Xiaomi-OCR-0/blob/main/LICENSE)

## Verification still needed

Evaluate the current pipeline on representative pages. Measure omissions, headers and footers, reading order, tables and formulas, GPU memory and latency, and the availability of usable geometry. Test the exact pinned model and runtime offline after setup. The original research did not perform this comparison; synthetic hardware checks are documented separately.
