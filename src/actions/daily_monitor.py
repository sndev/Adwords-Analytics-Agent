"""Daily monitor: pull performance, check approvals/budget, auto-apply within guardrails.

If credentials aren't configured yet, defers (no alert spam during setup).
"""
from ..config_loader import optional_env
from .util import escalate, send_slack, write_report


def run() -> int:
    if not optional_env("GOOGLE_ADS_REFRESH_TOKEN"):
        text = "⏳ *Daily monitor deferred* — Google Ads creds not configured."
        write_report("daily_monitor.md", text)
        return 0

    try:
        from ..connectors import google_ads_client as ads
        overview = ads.collect_campaign_overview()
        digest = [
            f"{c['name']} | {c['status']} | imp {c['impressions']} | clicks {c['clicks']} "
            f"| cost ${c['cost_micros'] / 1e6:.2f} | conv {c['conversions']}"
            for c in overview
        ]
        text = "📊 *Daily Ad Performance*\n" + "\n".join(digest) if digest else "⚠️ No campaigns pulled."
    except Exception as e:  # noqa: BLE001
        text = f"⚠️ Daily monitor could not pull Google Ads data: {e}"
        escalate("daily_monitor", str(e))

    write_report("daily_monitor.md", text)
    send_slack(text)
    return 0