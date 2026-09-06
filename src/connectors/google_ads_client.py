"""Google Ads API connector.

All credentials come from environment variables (never committed).
"""
from typing import Any, Dict, List, Optional

from ..config_loader import optional_env, require_env

API_VERSION = "v18"


def _deps_ok() -> bool:
    try:
        import google.ads.googleads  # noqa: F401
        return True
    except ImportError:
        return False


def build_config() -> Dict[str, Any]:
    """Build the google-ads client config dict from environment."""
    cfg = {
        "developer_token": require_env("GOOGLE_ADS_DEVELOPER_TOKEN"),
        "client_id": require_env("GOOGLE_ADS_CLIENT_ID"),
        "client_secret": require_env("GOOGLE_ADS_CLIENT_SECRET"),
        "refresh_token": require_env("GOOGLE_ADS_REFRESH_TOKEN"),
        "use_proto_plus": True,
    }
    login = optional_env("GOOGLE_ADS_LOGIN_CUSTOMER_ID").replace("-", "")
    if login:
        cfg["login_customer_id"] = login
    return cfg


def customer_id() -> str:
    return require_env("GOOGLE_ADS_CUSTOMER_ID").replace("-", "")


def client() -> Any:
    if not _deps_ok():
        raise ImportError("google-ads package not installed. Run: pip install -r requirements.txt")
    from google.ads.googleads.client import GoogleAdsClient
    return GoogleAdsClient.load_from_dict(build_config())


def list_accessible_customers() -> List[str]:
    """Verify token + auth by listing accessible accounts."""
    c = client()
    customer_service = c.get_service("CustomerService")
    try:
        response = customer_service.list_accessible_customers()
        return [r for r in response.resource_names]
    except Exception as e:  # noqa: BLE001
        raise RuntimeError(f"listAccessibleCustomers failed: {e}") from e


def run_gaql(query: str, cid: Optional[str] = None) -> List[Dict[str, Any]]:
    """Run a GAQL query against the target customer id."""
    c = client()
    cid = cid or customer_id()
    ga_service = c.get_service("GoogleAdsService")
    try:
        response = ga_service.search(customer_id=cid, query=query)
        rows = []
        for row in response:
            rows.append(row)
        return rows
    except Exception as e:  # noqa: BLE001
        raise RuntimeError(f"GAQL search failed: {e}") from e


def collect_campaign_overview(cid: Optional[str] = None) -> List[Dict[str, Any]]:
    """Baseline inventory of campaigns for reconciliation against the plan."""
    query = """
        SELECT
          campaign.id,
          campaign.name,
          campaign.status,
          campaign.daily_budget_micros,
          campaign.network_settings.target_google_search,
          campaign.network_settings.target_search_network,
          campaign.network_settings.target_content_network,
          metrics.impressions,
          metrics.clicks,
          metrics.cost_micros,
          metrics.conversions
        FROM campaign
        ORDER BY campaign.id
    """
    rows = run_gaql(query, cid)
    out = []
    for r in rows:
        out.append(
            {
                "id": r.campaign.id,
                "name": r.campaign.name,
                "status": r.campaign.status.name,
                "daily_budget_micros": r.campaign.daily_budget_micros,
                "target_google_search": r.campaign.network_settings.target_google_search,
                "target_search_network": r.campaign.network_settings.target_search_network,
                "target_content_network": r.campaign.network_settings.target_content_network,
                "impressions": r.metrics.impressions,
                "clicks": r.metrics.clicks,
                "cost_micros": r.metrics.cost_micros,
                "conversions": r.metrics.conversions,
            }
        )
    return out
