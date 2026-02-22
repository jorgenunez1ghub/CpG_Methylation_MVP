"""Configuration values loaded from environment with safe defaults."""

from __future__ import annotations

import os

PAGE_TITLE = os.getenv("APP_PAGE_TITLE", "CpG Methylation MVP")
APP_TITLE = os.getenv("APP_TITLE", "CpG Upload → Parse → Normalize")
APP_LAYOUT = os.getenv("APP_LAYOUT", "wide")
APP_CAPTION = os.getenv(
    "APP_CAPTION",
    "Educational demo only. Not medical advice. No raw upload data is logged or displayed outside your session.",
)
APP_DESCRIPTION = os.getenv(
    "APP_DESCRIPTION",
    "Upload a **CSV or TSV** containing CpG methylation values. The app validates and normalizes your data into a canonical schema for downstream analysis.",
)
