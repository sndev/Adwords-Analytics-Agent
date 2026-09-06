"""Shared run utilities: run-state, Slack reporting, guardrail escalation."""
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests

from ..config_loader import settings

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"
REPORT_DIR = Path(__file__).resolve().parent.parent.parent / "reports"


def state_path() -> Path:
    return DATA_DIR / "agent_state.json"


def load_state() -> Dict[str, Any]:
    if state_path().exists():
        return json.loads(state_path().read_text())
    return {}


def save_state(state: Dict[str, Any]) -> None:
    DATA_DIR.mkdir(exist_ok=True)
    state_path().write_text(json.dumps(state, indent=2, default=str))


def slack_enabled() -> bool:
    return bool(os.environ.get(settings().get("reporting", {}).get("slack_webhook_url_env", "")))


def send_slack(text: str) -> bool:
    webhook = os.environ.get(
        settings().get("reporting", {}).get("slack_webhook_url_env", "SLACK_WEBHOOK_URL")
    )
    if not webhook:
        return False
    try:
        requests.post(webhook, json={"text": text}, timeout=10)
        return True
    except requests.RequestException:
        return False


def write_report(filename: str, text: str) -> Path:
    REPORT_DIR.mkdir(exist_ok=True)
    p = REPORT_DIR / filename
    p.write_text(text)
    return p


def escalate(item: str, detail: str) -> None:
    """Escalate anything that exceeds guardrails / cannot be auto-applied."""
    msg = f"⚠️ *{item}* escalated for review:\n{detail}"
    send_slack(msg)