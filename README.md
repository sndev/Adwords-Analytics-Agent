# Adwords-Analytics-Agent

Autonomous agent that builds, manages, and optimizes Google Ads campaigns by correlating
**Google Ads** spend/performance with **Google Analytics (GA4)** behavior and **SalesNexus CRM**
demo-bookings/conversions — for B2B lead-generation campaigns.

Runs on **GitHub Actions** (no local machine needed) and uses **fit-for-purpose LLM tiering**
so inference cost stays under ~$1/month.

## Status

| System | Status |
|---|---|
| SalesNexus CRM | ⏳ Awaiting verified credentials |
| Google Ads API | ⏳ Awaiting verified credentials |
| Google Analytics 4 (GA4) | ⏳ Awaiting verified credentials (service-account JSON present locally; needs Viewer grant + property ID) |

See [`integration-setup-documentation.md`](integration-setup-documentation.md) for the credential
checklist and [`docs/`](docs) for the operating plan.

## Quick start

```bash
pip install -r requirements.txt
# Provide credentials via environment variables (never commit them)
# GOOGLE_ADS_DEVELOPER_TOKEN, GOOGLE_ADS_CLIENT_ID, GOOGLE_ADS_CLIENT_SECRET,
# GOOGLE_ADS_REFRESH_TOKEN, GOOGLE_ADS_CUSTOMER_ID, GOOGLE_ADS_LOGIN_CUSTOMER_ID,
# GA4_PROPERTY_ID, GOOGLE_APPLICATION_CREDENTIALS, SN_API_KEY, SLACK_WEBHOOK_URL
python -m src.verify            # verify all connections
python -m src.main --mode daily  # run a scheduled analysis
```

Scheduled runs are defined in `.github/workflows/` (daily monitor + weekly analysis).

## Configuration

- `config/settings.yaml` — guardrails (hard caps): max bid, max daily budget, conversion
  thresholds before auto-apply, LLM cost caps, Slack reporting.
- `config/campaign_plan.yaml` — the managed campaign definitions (Intent Leads first;
  architecture supports multiple campaigns / future paid media).

## Security

Credentials are injected via environment variables / GitHub Actions secrets only. Secrets are
never committed. `.gitignore` excludes all credential and data files.
