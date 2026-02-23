"""Dependency guardrails for core package imports."""

from __future__ import annotations

import importlib
from pathlib import Path


CORE_MODULES = [
    "core",
    "core.analyze",
    "core.config",
    "core.ingest",
    "core.io",
    "core.transform",
    "core.validate",
]


def test_core_modules_import() -> None:
    for module_name in CORE_MODULES:
        importlib.import_module(module_name)


def test_core_has_no_streamlit_imports() -> None:
    core_dir = Path(__file__).resolve().parents[1] / "core"
    for py_file in core_dir.glob("*.py"):
        contents = py_file.read_text(encoding="utf-8")
        assert "import streamlit" not in contents
        assert "from streamlit" not in contents
