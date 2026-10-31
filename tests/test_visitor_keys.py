import ast
from pathlib import Path


def test_space_directly_binds_gpu_handler():
    tree = ast.parse(Path("app.py").read_text(encoding="utf-8"))
    calls = [n for n in ast.walk(tree) if isinstance(n, ast.Call)]
    build = next(n for n in calls if isinstance(n.func, ast.Name) and n.func.id == "build_demo")
    assert build.args[1].id == "run_gpu"
    assert "NVIDIA_API_KEY" not in Path("app.py").read_text()
