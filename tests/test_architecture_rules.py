from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_core_modules_do_not_import_streamlit() -> None:
    core_dir = REPO_ROOT / "core"
    violations: list[str] = []

    for path in core_dir.glob("*.py"):
        source = path.read_text(encoding="utf-8")
        if "import streamlit" in source or "from streamlit" in source:
            violations.append(str(path.relative_to(REPO_ROOT)))

    assert not violations, f"core modules importing streamlit: {violations}"


def test_streamlit_app_uses_public_core_api() -> None:
    app_source = (REPO_ROOT / "app" / "main.py").read_text(encoding="utf-8")

    assert "from core.config import" not in app_source
