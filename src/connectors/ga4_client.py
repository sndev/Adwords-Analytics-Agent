"""Google Analytics 4 (Data API) connector using a service account.

Auth uses the standard GOOGLE_APPLICATION_CREDENTIALS env var pointing at the
service-account JSON key file, plus GA4_PROPERTY_ID for the target property.
"""
import datetime as dt
from typing import Any, Dict, List, Optional

from ..config_loader import require_env


def property_id() -> str:
    return require_env("GA4_PROPERTY_ID")


def _deps_ok() -> bool:
    try:
        import google.analytics.data_v1beta  # noqa: F401
        return True
    except ImportError:
        return False


def _imports():
    if not _deps_ok():
        raise ImportError(
            "google-analytics-data package not installed. Run: pip install -r requirements.txt"
        )
    from google.analytics.data_v1beta import BetaAnalyticsDataClient
    from google.analytics.data_v1beta.types import (
        DateRange,
        Dimension,
        Metric,
        RunReportRequest,
    )
    return BetaAnalyticsDataClient, DateRange, Dimension, Metric, RunReportRequest


def run_report(
    dimensions: Optional[List[str]] = None,
    metrics: Optional[List[str]] = None,
    start_date: str = "30daysAgo",
    end_date: str = "today",
    limit: int = 1000,
) -> List[Dict[str, Any]]:
    """Run a GA4 report and return rows as dicts keyed by dimension/metric name."""
    BetaAnalyticsDataClient, DateRange, Dimension, Metric, RunReportRequest = _imports()
    client = BetaAnalyticsDataClient()
    dims = [Dimension(name=d) for d in (dimensions or [])]
    mets = [Metric(name=m) for m in (metrics or ["sessions"])]
    request = RunReportRequest(
        property=f"properties/{property_id()}",
        dimensions=dims,
        metrics=mets,
        date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
        limit=limit,
    )
    response = client.run_report(request)
    rows = []
    for row in response.rows:
        dim_values = {
            d.name: dv.value
            for d, dv in zip(dims, row.dimension_values)
        }
        met_values = {
            m.name: mv.value
            for m, mv in zip(mets, row.metric_values)
        }
        rows.append({**dim_values, **met_values})
    return rows


def sessions_last_7_days() -> Dict[str, Any]:
    """Simple verification query: sessions + key events for last 7 days."""
    rows = run_report(
        dimensions=["date"],
        metrics=["sessions", "keyEvents", "totalUsers"],
        start_date="7daysAgo",
        end_date="yesterday",
    )
    total_sessions = sum(int(r.get("sessions", 0)) for r in rows)
    total_events = sum(int(r.get("keyEvents", 0)) for r in rows)
    return {"rows": rows, "total_sessions": total_sessions, "total_key_events": total_events}
