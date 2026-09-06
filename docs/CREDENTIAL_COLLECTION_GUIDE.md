# Credential Collection Guide — Step by Step

Collect these 4 groups of credentials. Each part tells you exactly where to click and what to copy. Work through them in order — **Part 2 (Google Ads) is the longest**.

## One-time prerequisites (do first, ~10 min)

1. Use the **same Google account** that owns/administers the Google Ads account and the GA4 property.
2. Have access to the **Google Cloud Console** with a billing-enabled project (you already have `salesnexus-ads-analytics`).
3. Have a Google Ads **Manager (MCC)** account. If you don't, create one at https://ads.google.com → "Switch to manager account" → create. This is where the Developer Token lives.

---

# PART 1 — Google Analytics (GA4)

Goal: get the **GA4 Property ID** and grant the **service account** Viewer access.

### 1.1 Give the service account access to the property
1. Go to https://analytics.google.com (use `cklein@salesnexus.com` or your admin).
2. This is your GA4 property. Left rail → bottom-left **Admin** (gear icon).
3. Under **Property** column → **Property Access Management**.
4. Click **+** (top) → *Add users*.
5. Enter the service account email:
   `ga4-reporting@salesnexus-ads-analytics.iam.gserviceaccount.com`
6. Role: **Viewer**.
7. Click **Add**. (Notifications email can be left blank.)

### 1.2 Find the GA4 Property ID
1. Still under **Admin** → **Property** column → **Property Settings**.
2. First page shows **Property ID** — a numeric string like `123456789`.
3. **Copy that number.** This is `GA4_PROPERTY_ID`.

### 1.3 Your service-account key file
You already downloaded `salesnexus-ads-analytics-1e91ea5a09c4.json`. Keep it safe — its full JSON contents will go into the `GA4_SERVICE_ACCOUNT_JSON` secret.

> If you lost the file: Google Cloud Console → IAM & Admin → Service Accounts → open `ga4-reporting` → **Keys** → **Add Key → Create new key → JSON** → a new `.json` downloads.

---

# PART 2 — Google Ads API

Goal: collect **6 values** — Developer Token, Client ID, Client Secret, Refresh Token, Customer ID, Login Customer ID.

### 2.1 Developer Token
1. Go to https://ads.google.com → in the **Manager (MCC) account**.
2. Top-right **Tools** icon (wrench) → **Setup** → **API Center** (or directly: https://ads.google.com/aw/apicenter).
3. Under *Your developer token* you'll see a long token string → **copy it**.
4. **Check the access level** next to it. It should be **Basic** or **Standard**.
   - If it shows **Test account** or **Explorer**, apply for increased access (API Center → *Apply for higher access*) **now** — this review takes days and blocks production writes.
   - Note: link your **production customer ID** to the application if asked.

### 2.2 Customer IDs (both of them)
- **Customer ID (target account):** In Google Ads, top-right shows your account ID — 10 digits with dashes, e.g. `123-456-7890`. Or read it from the URL `https://ads.google.com/aw/campaigns?ocid=????&customer_id=123-456-7890`. This is the **salesnexus.com Ads account**.
- **Login Customer ID (MCC):** Switch into your Manager account — the ID shown there is the MCC. If you manage the salesnexus account from that MCC, note this ID too.

Record BOTH as 10-digit strings (dashes optional; the app strips them).

### 2.3 Create an OAuth "Desktop App" client
The current local file is a **Web** client, which makes the refresh-token step finicky. Create a **Desktop** client instead — it's the reliable path.

1. Go to https://console.cloud.google.com/apis/credentials
2. Top bar: confirm project = **salesnexus-ads-analytics**.
3. Click **+ CREATE CREDENTIALS** → **OAuth client ID**.
4. **Application type:** **Desktop app**.
5. Name: `salesnexus-ads-agent`
6. Click **CREATE** → a popup shows **Client ID** + **Client Secret** → **copy both** (or download JSON).
   - If the popup closes: click the client row → "Download JSON" or copy from the detail panel.

You now have `GOOGLE_ADS_CLIENT_ID` and `GOOGLE_ADS_CLIENT_SECRET`.

### 2.4 Generate the Refresh Token (one-time human step)
Use Google's OAuth Playground:

1. Open https://developers.google.com/oauthplayground
2. Top-right **gear (⚙) icon** → check **"Use your own OAuth credentials"** → paste your **Client ID** and **Client Secret** from 2.3 → close the gear.
3. Left panel, in the *Select & authorize APIs* box, paste this scope exactly:
   `https://www.googleapis.com/auth/adwords`
   → click **Authorize APIs**.
4. **Sign in with the Google account that has access to the Google Ads account** (the one you're using now). Approve the consent screen.
5. Playground now shows an *Authorization code*. Click **Exchange authorization code for tokens**.
6. Result screen shows **Access token** and **Refresh token**.
   → **Copy the Refresh token.** It's a long string starting with `1//`. This is `GOOGLE_ADS_REFRESH_TOKEN`.
7. In the bottom-left dropdown (Step 2, *Set the max number of results*) you can find the **authorized packages** list — the request log here also confirms the call went through.

> 🔑 **Critical tip from the earlier failure:** Our earlier `401 invalid_client` means the old client ID/secret didn't validate. The **Desktop** client in step 2.3 + this refresh token should resolve it.

---

# PART 3 — SalesNexus CRM

Goal: confirm the **API key** and note the **source-attribution fields**.

1. The CRM already uses `SN_API_KEY` (referenced in your docs). Confirm the token value so it can be loaded as a secret.
   - If you don't know where to find it, check SalesNexus admin → **Settings / Integrations → API** (the API key is typically displayed there once; rotate/regenerate if needed).
2. **Source attribution:** log in to SalesNexus and open a demo/opportunity record. Note which fields record the lead source (e.g., UTM campaign/source, "Lead Source", "Google Ads"). The agent uses these to tie ad clicks → CRM demo bookings.
3. Note the API base URL for your pod (e.g., `https://api.salesnexus.com/api`) — needed for `SN_API_BASE_URL`.

---

# PART 4 — What to add as GitHub Secrets

Repo: `sndev/Adwords-Analytics-Agent` → **Settings → Secrets and variables → Actions → New repository secret**.

Add each (exact name, no extra spaces):

| Secret name | Value to paste |
|---|---|
| `GOOGLE_ADS_DEVELOPER_TOKEN` | from 2.1 |
| `GOOGLE_ADS_CLIENT_ID` | from 2.3 |
| `GOOGLE_ADS_CLIENT_SECRET` | from 2.3 |
| `GOOGLE_ADS_REFRESH_TOKEN` | from 2.4 |
| `GOOGLE_ADS_CUSTOMER_ID` | 10-digit salesnexus Ads account (2.2) |
| `GOOGLE_ADS_LOGIN_CUSTOMER_ID` | 10-digit MCC id (2.2, leave blank if none) |
| `GA4_PROPERTY_ID` | from 1.2 |
| `GA4_SERVICE_ACCOUNT_JSON` | FULL contents of the service-account `.json` file |
| `SN_API_KEY` | CRM API key (3.1) |
| `SN_API_BASE_URL` | CRM base URL (3.3, optional) |
| `SLACK_WEBHOOK_URL` | Slack app Incoming Webhook URL (create at https://api.slack.com/apps → **Incoming Webhooks**) |

## Verify everything works
1. Repo → **Actions** → **Verify Connections** workflow → **Run workflow** (top-right "Run workflow" → click).
2. It runs `python -m src.verify` and reports for each system: **OK / FAILED / SKIPPED**.
   - All three should show **OK**.
3. If any show FAILED, click into the failing run and the error message tells you which value is wrong.

## Troubleshooting table

| Symptom | Cause / Fix |
|---|---|
| Ads: `401 invalid_client` | Wrong client secret — regenerate the Desktop OAuth client (2.3) and redo refresh token (2.4) |
| Ads: "login customer ID is invalid" | `GOOGLE_ADS_LOGIN_CUSTOMER_ID` isn't a 10-digit ID or you're not using an MCC — remove it/blank it |
| Ads: permission denied on reads | Developer token at Test/Explorer level → apply for Basic/Standard (2.1) |
| GA4: `PERMISSION_DENIED` | Service account not added to Property Access Management (1.1) or not Viewer |
| GA4: `UNAUTHENTICATED / 401` | `GA4_SERVICE_ACCOUNT_JSON` not the full valid JSON key file |
| CRM call errors | Wrong base URL or expired API key (Part 3) |