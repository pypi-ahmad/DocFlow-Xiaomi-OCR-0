@echo off
cd /d "%~dp0"
uv run --offline --no-sync streamlit run streamlit_app.py --server.address 127.0.0.1 --server.port 8472
