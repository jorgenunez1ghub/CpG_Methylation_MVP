"""Configuration values loaded from environment with safe defaults."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class AppConfig:
    """UI-facing app configuration values."""

    page_title: str
    app_title: str
    app_layout: str
    app_caption: str
    app_description: str


def get_app_config() -> AppConfig:
    """Build app configuration from environment variables with defaults."""
    return AppConfig(
        page_title=os.getenv("APP_PAGE_TITLE", "CpG Methylation MVP"),
        app_title=os.getenv("APP_TITLE", "CpG Upload → Parse → Normalize"),
        app_layout=os.getenv("APP_LAYOUT", "wide"),
        app_caption=os.getenv(
            "APP_CAPTION",
            "Educational demo only. Not medical advice. No raw upload data is logged or displayed outside your session.",
        ),
        app_description=os.getenv(
            "APP_DESCRIPTION",
            "Upload a **CSV or TSV** containing CpG methylation values. The app validates and normalizes your data into a canonical schema for downstream analysis.",
        ),
    )


APP_CONFIG = get_app_config()
PAGE_TITLE = APP_CONFIG.page_title
APP_TITLE = APP_CONFIG.app_title
APP_LAYOUT = APP_CONFIG.app_layout
APP_CAPTION = APP_CONFIG.app_caption
APP_DESCRIPTION = APP_CONFIG.app_description
