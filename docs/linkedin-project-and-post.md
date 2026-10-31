# LinkedIn project and post

## Project entry

Name: DocFlow Xiaomi OCR

A document parsing app that uses Xiaomi-OCR-0 for recognition and PP-DocLayoutV3 for layout. The native Windows Streamlit interface converts PDFs and images into Markdown, HTML and JSON, with page selection, batch processing, annotations and exports.

A separate Gradio Space is prepared for ZeroGPU; deployment is pending.

## Post draft

I built a local document parsing workbench using Xiaomi-OCR-0 and PP-DocLayoutV3. It takes PDFs or images, lets me select pages and inspect layout annotations, and exports Markdown, HTML and structured JSON.

The Windows app runs on a local NVIDIA GPU after setup. A separate Hugging Face Space is planned; the current deployment is blocked by the account's ZeroGPU Space limit.
