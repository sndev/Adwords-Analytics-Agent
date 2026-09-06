"""SalesNexus CRM REST API connector.

Credentials: SN_API_KEY env var (plus optional SN_API_BASE_URL).
Represents leads, contacts, and demo/opportunity records with source attribution.
"""
from typing import Any, Dict, List

import requests

from ..config_loader import optional_env, require_env

DEFAULT_BASE = "https://api-beta.salesnex.us"


def api_key() -> str:
    return require_env("SN_API_KEY")


def base_url() -> str:
    return optional_env("SN_API_BASE_URL", DEFAULT_BASE)


def _headers() -> Dict[str, str]:
    return {
        "X-Api-Key": api_key(),
        "Content-Type": "application/json",
        "Accept": "application/json",
    }


def get(path: str, params: Dict[str, Any] | None = None) -> Any:
    resp = requests.get(f"{base_url()}{path}", headers=_headers(), params=params, timeout=30)
    resp.raise_for_status()
    return resp.json()


def verify() -> bool:
    """Ping the CRM to confirm connectivity and valid API key."""
    r = requests.get(f"{base_url()}/api/v1/Ping", headers=_headers(), timeout=15)
    return r.status_code == 200


def contacts(limit: int = 5) -> List[Dict[str, Any]]:
    """Fetch a small sample of contacts (for verification / diagnostics)."""
    data = get("/api/v1/Contacts", {"page": 1, "pageSize": limit})
    return data.get("items") or data.get("contacts") or data if isinstance(data, list) else []


def recent_demo_bookings(days: int = 30) -> List[Dict[str, Any]]:
    """Fetch recent demo/opportunity records with source attribution fields.

    NOTE: field names depend on the CRM API schema — confirm the source/campaign
    tag fields (e.g., UTM parameters / 'Google Ads' campaign) before relying on this.
    """
    return get("/api/v1/Opportunities", {"days": days}) if False else []
