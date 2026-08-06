# SalesNexus B2B Campaign Optimization — Integration Setup Documentation

**Document owner:** Digital Advertising Campaign Management Agent
**Last updated:** August 6, 2026
**Purpose:** Record of credentials/access configured to enable end-to-end analysis of Google Ads, Google Analytics (GA4), and SalesNexus CRM data for optimizing B2B sales-leader ad campaigns driving demo bookings and free trials on salesnexus.com.

---

## 1. Status Summary

| System | Status | Notes |
|---|---|---|
| SalesNexus CRM | ✅ **Connected & Verified** | API key present and active in this session |
| Google Ads API | ⏳ **Setup reported complete by user — credentials not yet received** | Awaiting handoff of secret values to run live verification |
| Google Analytics 4 (GA4) API | ⏳ **Setup reported complete by user — credentials not yet received** | Awaiting handoff of secret values to run live verification |

> **Action needed:** The steps below were completed per our setup walkthrough, but the actual secret values (tokens, keys, IDs) have not yet been shared into this working session. See [Section 5](#5-outstanding-items-to-complete-verification) for exactly what to send and how.

---

## 2. SalesNexus CRM

| Item | Value / Detail |
|---|---|
| Access method | REST API (JSON) |
| Credential | API Key (`SN_API_KEY`) |
| Status | Present in session environment, treated as a live secret |
| Scope of access | Full CRM read access assumed (contacts, leads, opportunities, campaign/source tracking fields) — **to confirm:** does this key have access to the fields that tag lead source (e.g., "Google Ads," "GA4 campaign," UTM parameters)? |
| Used for | Matching ad clicks/sessions to actual demo bookings and free trial signups; measuring lead quality and pipeline, not just clicks |

---

## 3. Google Ads API — Setup Checklist

| # | Item | Purpose | Status |
|---|---|---|---|
| 1 | Google Ads Manager (MCC) account | Home for the developer token; recommended at the root of the account hierarchy | Reported done |
| 2 | Developer Token (API Center → API Access form) | Required for every Google Ads API call; access level (Test Account / Explorer / Basic) controls which accounts and daily call volume are available | Reported done — **need token value + access level** |
| 3 | Google Cloud project | Home for OAuth client and enabled APIs | Reported done |
| 4 | Google Ads API enabled in that project | Required to call the API | Reported done |
| 5 | OAuth consent screen configured with scope `https://www.googleapis.com/auth/adwords` | Authorizes the app to act on the Ads account | Reported done |
| 6 | OAuth Client ID + Client Secret | Used to mint access tokens from the refresh token | Reported done — **need values** |
| 7 | Refresh Token (generated via OAuth Playground or first-run consent) | Lets me obtain new access tokens without repeated logins | Reported done — **need value** |
| 8 | Google Ads Customer ID (10-digit, target account) | Identifies which Ads account to query/manage | Reported done — **need value** |
| 9 | Login Customer ID (MCC ID, if applicable) | Required header when accessing a client account through a manager account | Reported done — **need value (or confirm not using an MCC)** |
| 10 | Account access level of the authorizing Google user | Must have at least Standard access on the Ads account | Reported done |

**Credential fields needed from you:**
```
GOOGLE_ADS_DEVELOPER_TOKEN=
GOOGLE_ADS_CLIENT_ID=
GOOGLE_ADS_CLIENT_SECRET=
GOOGLE_ADS_REFRESH_TOKEN=
GOOGLE_ADS_CUSTOMER_ID=
GOOGLE_ADS_LOGIN_CUSTOMER_ID=      (leave blank if not using an MCC)
```

**Known limitation to flag:** if the developer token is still at "Test Account" or "Explorer" access level (pending Basic/Standard approval from Google), production campaign data and write actions (e.g., bid/budget changes) may be restricted until that review completes. Please confirm the access level shown in the API Center.

---

## 4. Google Analytics 4 (GA4) — Setup Checklist

| # | Item | Purpose | Status |
|---|---|---|---|
| 1 | Google Cloud project (same or separate from Ads) | Home for the service account and enabled APIs | Reported done |
| 2 | Google Analytics Data API enabled | Fetches report data (sessions, conversions, engagement, landing pages, etc.) | Reported done |
| 3 | Google Analytics Admin API enabled | Discovers accounts/properties and manages access programmatically | Reported done |
| 4 | Service Account created in the Cloud project | Authenticates server-to-server without interactive login | Reported done — **need service account email** |
| 5 | Service Account JSON key downloaded | Private key file used to authenticate API calls | Reported done — **need file contents** |
| 6 | Service Account added to GA4 Property Access Management | Grants the service account permission to read the property | Reported done |
| 7 | Role granted to service account | Viewer is sufficient for reporting/analysis | Reported done — **please confirm role granted (Viewer/Analyst/Editor)** |
| 8 | GA4 Property ID (numeric) | Identifies which property to query | Reported done — **need value** |

**Credential fields needed from you:**
```
GA4_PROPERTY_ID=
GA4_SERVICE_ACCOUNT_EMAIL=
GA4_SERVICE_ACCOUNT_JSON=        (full contents of the downloaded key file)
```

---

## 5. Outstanding Items to Complete Verification

To move each system from "Reported done" to "Connected & Verified," please do one of the following:

1. **Preferred:** Add the credential values above as environment variables/secrets to this working session (the same way `SN_API_KEY` is already configured), OR
2. Upload the GA4 service account JSON key file to the session's uploads folder, and share the remaining Google Ads values as text (client secret and refresh token should be treated as sensitive — avoid posting them anywhere outside this secured session).

Once received, I will:
- Run a test call to `customers:listAccessibleCustomers` (Google Ads) to confirm the developer token, OAuth credentials, and customer ID all resolve correctly.
- Run a test GA4 Data API report request (e.g., last 7 days of sessions/conversions) to confirm the service account has property access.
- Update the **Status Summary** table in this document to "Connected & Verified" for each system.
- Begin the first cross-platform analysis: matching Google Ads spend/clicks → GA4 landing page behavior → SalesNexus demo bookings/free trial conversions.

---

## 6. Security Notes

- Client secrets, refresh tokens, developer tokens, and service account JSON keys should be treated as sensitive as a password — do not commit them to shared documents, code repositories, or plaintext chat outside this secured session.
- Store credentials as environment variables/session secrets rather than embedding them directly in scripts or files.
- Recommend periodically rotating the GA4 service account key and reviewing Google Ads account access under **Admin → Access and Security** to remove any unused users/tokens.
- Recommend maintaining at least two administrators on both the Google Ads Manager account and the GA4 property, so access isn't dependent on a single person.
