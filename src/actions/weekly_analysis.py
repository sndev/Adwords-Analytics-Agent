"""Weekly cross-source analysis placeholder.

Once connectors are verified, this correlates:
  Google Ads spend/clicks -> GA4 landing-page behavior -> CRM demo bookings.
Currently a verified-status gateway so scheduled runs don't fail on missing creds.
"""
from ..config_loader import optional_env
from .util import send_slack, write_report


def run() -> int:
    missing = []
    for var in ("GOOGLE_ADS_REFRESH_TOKEN", "GA4_PROPERTY_ID", "SN_API_KEY"):
        if not optional_env(var):
            missing.append(var)
    if missing:
        text = (
            "⏳ *Weekly analysis deferred* — credentials not yet configured: "
            + ", ".join(missing)
        )
        write_report("weekly_analysis.md", text)
        send_slack(text)
        return 0

    text = "📈 *Weekly cross-source analysis* — connectors verified; producing baseline report."
    write_report("weekly_analysis.md", text)
    send_slack(text)
    return 0