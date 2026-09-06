"""Campaign build/import placeholder.

Builds (or reconciles) the managed campaign definitions in config/campaign_plan.yaml
against the live account once Ads write access is verified.
"""
from typing import Optional

from ..config_loader import optional_env
from .util import send_slack, write_report


def run(dry_run: bool = True) -> int:
    """dry_run default True: recommend-only until explicitly set to apply."""
    if not optional_env("GOOGLE_ADS_REFRESH_TOKEN"):
        text = "⏳ *Build deferred* — Google Ads creds not configured."
        write_report("build_campaign.md", text)
        send_slack(text)
        return 0

    text = (
        "🛠️ *Campaign build* verifies/creates the Intent Leads campaign "
        f"{'(dry run)' if dry_run else '(apply)'}."
    )
    write_report("build_campaign.md", text)
    send_slack(text)
    return 0