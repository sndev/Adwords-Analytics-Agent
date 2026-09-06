"""Verify all system connections. Run with: python -m src.verify"""
import sys

from .config_loader import optional_env


def _has(var: str) -> bool:
    return bool(optional_env(var))


def check_google_ads() -> str:
    from .connectors import google_ads_client as ads

    if not all(
        _has(v)
        for v in ("GOOGLE_ADS_DEVELOPER_TOKEN", "GOOGLE_ADS_CLIENT_ID",
                  "GOOGLE_ADS_CLIENT_SECRET", "GOOGLE_ADS_REFRESH_TOKEN",
                  "GOOGLE_ADS_CUSTOMER_ID")
    ):
        return "SKIPPED (Google Ads creds not set)"
    try:
        customers = ads.list_accessible_customers()
        rows = ads.collect_campaign_overview()
        return f"OK ({len(customers)} accessible customers; {len(rows)} campaigns found)"
    except Exception as e:  # noqa: BLE001
        return f"FAILED ({e})"


def check_ga4() -> str:
    from .connectors import ga4_client as ga4

    if not _has("GA4_PROPERTY_ID"):
        return "SKIPPED (GA4_PROPERTY_ID not set)"
    try:
        result = ga4.sessions_last_7_days()
        return (
            f"OK (last-7-days: {result['total_sessions']} sessions, "
            f"{result['total_key_events']} key events)"
        )
    except Exception as e:  # noqa: BLE001
        return f"FAILED ({e})"


def check_crm() -> str:
    from .connectors import crm_client as crm

    if not _has("SN_API_KEY"):
        return "SKIPPED (SN_API_KEY not set)"
    try:
        ok = crm.verify()
        if not ok:
            return "FAILED (Ping returned non-200)"
        sample = crm.contacts(limit=1)
        return f"OK (connected; sample contact count: {len(sample)})"
    except Exception as e:  # noqa: BLE001
        return f"FAILED ({e})"


def main() -> int:
    checks = {
        "Google Ads": check_google_ads,
        "GA4": check_ga4,
        "SalesNexus CRM": check_crm,
    }
    print("=" * 50, flush=True)
    print("SalesNexus Ads + Analytics Agent — connection verification", flush=True)
    print("=" * 50, flush=True)
    exit_code = 0
    for name, fn in checks.items():
        status = fn()
        exit_code |= 1 if status.startswith("FAILED") else 0
        print(f"  {name:<22} {status}", flush=True)
    print("=" * 50, flush=True)
    return exit_code


if __name__ == "__main__":
    sys.exit(main())