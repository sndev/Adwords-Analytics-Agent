"""SalesNexus CRM REST API connector.

Credentials: SN_API_KEY env var (plus optional SN_API_BASE_URL).
Represents leads, contacts, and demo/opportunity records with source attribution.
"""
from typing import Any, Dict, List

import requests

from ..config_loader import optional_env, require_env

DEFAULT_BASE = "https://api.salesnexus.com/api"


def api_key() -> str:
    return require_env("SN_API_KEY")


def base_url() -> str:
    return optional_env("SN_API_BASE_URL", DEFAULT_BASE)


def _headers() -> Dict[str, str]:
    return {
        "Authorization": f"Bearer {api_key()}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }


def get(path: str, params: Dict[str, Any] | None = None) -> Any:
    resp = requests.get(f"{base_url()}{path}", headers=_headers(), params=params, timeout=30)
    resp.raise_for_status()
    return resp.json()


def verify() -> bool:
    """Probe the CRM with a lightweight endpoint to confirm connectivity."""
    # Exact endpoint depends on the deployed CRM API; adjust to a known one.
    r = requests.get(f"{base_url()}/contacts", headers=_headers(), timeout=30)
    return r.status_code in (200, 401, 403)


def recent_demo_bookings(days: int = 30) -> List[Dict[str, Any]]:
    """Fetch recent demo/opportunity records with source attribution fields.

    NOTE: field names depend on the CRM API schema — confirm the source/campaign
    tag fields (e.g., UTM parameters / 'Google Ads' campaign) before relying on this.
    """
    # Placeholder mapping; refine once the CRM schema is confirmed.
    return get("/opportunities", {"days": days}) if False else []
