"""Configuration loading + environment secret helpers."""
import os
from pathlib import Path
from typing import Any, Dict

import yaml

ROOT = Path(__file__).resolve().parent.parent
CONFIG_DIR = ROOT / "config"


def load_yaml(name: str) -> Dict[str, Any]:
    with open(CONFIG_DIR / name, "r") as f:
        return yaml.safe_load(f) or {}


def settings() -> Dict[str, Any]:
    return load_yaml("settings.yaml")


def campaign_plan() -> Dict[str, Any]:
    return load_yaml("campaign_plan.yaml")


def require_env(var: str) -> str:
    val = os.environ.get(var, "").strip()
    if not val:
        raise RuntimeError(f"Missing required environment variable: {var}")
    return val


def optional_env(var: str, default: str = "") -> str:
    return os.environ.get(var, default).strip()
