# SalesNexus Ads + Analytics Agent — Connection & Execution Plan

**Goal:** Stand up an autonomous agent (no dependency on a local computer) that builds/manages the "Intent Leads" Google Ads campaign, monitors Google Ads + GA4 + SalesNexus CRM, optimizes results, using fit-for-purpose LLMs to keep cost low without sacrificing results.

This document is the working plan. It separates **what we can start today** from **what is blocked on credentials**.

---

## 1. Current-State Audit (what I found)

Repo `sndev/Adwords-Analytics-Agent` exists (public, `sndev`) but contains **only 2 documentation files, no code**:
- `README.md` (one-liner)
- `integration-setup-documentation.md` (credential checklist; SalesNexus CRM marked connected, Ads + GA4 marked "reported done, creds not received")

Campaign build artifacts exist locally in `~/pCloudDrive/downloads/`:
- `Campaign_Build_and_Launch_Plan.md` (full strategy — 1 campaign, 3 ad groups, exact match, $20/day, book-a-demo conversion)
- `keywords_{core,apollo,zoominfo}_phase1.txt` (the 8 launch Exact keywords)
- `campaign_settings.csv`, `extensions_assets.csv`, web-UI walkthrough
- **Missing/non-saved locally:** `ads_rsa.csv`, `negative_keywords.csv`, `GTM_Setup_Instructions.md`, `keywords_*_phase2.txt`, and the `editor_paste_blocks/` folder referenced by the plan. These need to be regenerated or sourced before a full build.

### Credential status — THIS IS THE BLOCKER
From a prior session, tried to authenticate to **Google Ads** and **GA4** and the credentials in that environment did **not** work:
- Google Ads OAuth token refresh returned **`401 invalid_client`**
- Google Ads login customer ID was rejected (not a valid 10-digit account ID)
- GA4 service-account JSON env value was not parseable JSON, and a direct GA4 API call returned **`401 UNAUTHENTICATED`**
- In the current environment the `GOOGLE_ADS_*` / GA4 variables are **not set at all**

What *is* available locally as files:
- **GA4 service account JSON** (`salesnexus-ads-analytics-1e91ea5a09c4.json`) — appears structurally valid (private key + `client_email: ga4-reporting@salesnexus-ads-analytics.iam.gserviceaccount.com`), but the service account must be added as a **Viewer** on the GA4 property for it to work.
- **OAuth client secret JSON** — note it is a **`"web"`** type client. The Google Ads refresh-token flow typically uses a Desktop/Installed client; a web client can work for the OAuth Playground flow but must be configured with the right redirect URI.

**Bottom line:** No verified, authenticated integration exists yet for Google Ads or GA4. Nothing can be built/monitored against live accounts until secure credentials are provided and verified. SalesNexus CRM API may be usable (key referenced), but was not verified in this session either.

---

## 2. The Credential Gate (must be done first — do not skip)

Credentials must be provided **securely**, not pasted into this chat. Recommended path:

1. **GA4 (reporting — easiest, can start today)**
   - Use the existing service account file, or regenerate a key in GCP.
   - In **GA4 Admin → Property Access Management**, add `ga4-reporting@salesnexus-ads-analytics.iam.gserviceaccount.com` with **Viewer**.
   - Provide the numeric **GA4 Property ID**.
2. **Google Ads (build/monitor/optimize)**
   - Confirm a Manager (MCC) account exists and the 10-digit **Customer ID** (no dashes) + **Login Customer ID**.
   - **Developer Token** from **Admin → API Center**, ideally at **Basic/Standard** access (Test/Explorer limits production writes).
   - **OAuth**: best made reliable by using a **Desktop/Installed** OAuth client. Generate a **refresh token** via the OAuth Playground or Google's `generate_user_credentials.py`. If the only client is the current `web` client, either add a desktop client or run the flow with a valid redirect URI.
3. **SalesNexus CRM** — provide/confirm the API key (`SN_API_KEY`) and which fields tag lead source (UTM/campaign) so clicks can be matched to real demo-bookings/pipeline.

### Secure delivery options
- Add them as **secrets in this environment** (env vars), or
- Store in **GitHub repo → Settings → Secrets → Actions** (used by scheduled GitHub Actions runs), or
- Provider-managed secret store the host reads.

The plan (below) expects credentials to be injected via environment variables so no secret is committed to the repo.

---

## 3. Target Architecture (autonomous, off the local machine)

Recommended: **containerized Python agent + scheduler, deployed to a low-cost host**, driven by GitHub Actions for the pipeline.

```
                    ┌──────────────────────────────────────┐
                    │       HOST (Cloud Run / VM / GH)     │
                    │                                      │
  Scheduler ───────▶│  Agent Runner (Python, docker)       │
  (cron / GH        │   ├─ Connectors: Google Ads API      │
   Actions)         │   │               GA4 Data API       │
                    │   │               SalesNexus CRM API  │
                    │   └─ Analysis (LLM tiering)          │
                    │                                      │
                    │  State/Logs: SQLite + repo commits    │
                    └──────────────────────────────────────┘
                                            │
                          GitHub repo (config, prompts, rules)
```

### 3.1 Run cadence (match campaign phase)
| Cadence | Action |
|---|---|
| **Daily 07:00 ET** | Pull performance (clicks, spend, CTR, convs by ad group/keyword); detect approval issues, budget exhaustion, search-term negatives |
| **Daily 12:00 ET** | Search Terms report → suggest new negative keywords |
| **Weekly** | Cross-source analysis (Ads spend → GA4 landing behavior → CRM demo bookings); optimization recommendations |
| **Event-driven** | Campaign build/import, RSA refresh, structural changes |
| **After ~15–30 demo conversions** | Recommend switch to automated (Smart/Target CPA) bidding — per plan, not before |

### 3.2 Hosting options (pick one)
| Option | Cost | Pros | Cons |
|---|---|---|---|
| **GitHub Actions scheduled** | Free tier | Zero infra, repo-native, secure secrets | Max ~2h/run, less frequent |
| **Google Cloud Run** + Cloud Scheduler | ~$0–10/mo idle | Always-on, cheap, Google-native | Needs GCP billing |
| **Small VM (e.g., GCP e2-small / AWS t3.micro)** | ~$10–15/mo | Full control, any scheduler | More ops |
| **Local now → migrate later** | $0 | Start immediately | Doesn't meet "no local dependency" |

**Recommendation:** Start with **GitHub Actions** (free, immediate, secrets already integrated) while the campaign is read-mostly; add **Cloud Run + scheduler** when you need always-on/continuous reach. This satisfies "run automatically without my local computer."

---

## 4. LLM Cost-Optimization Strategy (fit-for-purpose tiering)

The agent's LLM workload is small (a few thousand tokens/day). Route by task type:

| Task | Recommended model/cost | Why |
|---|---|---|
| ETL / formatting / rule checks | **No LLM** (pure code) | Deterministic API pulls + calculations = free |
| Keyword/negative-keyword extraction | Cheap model (e.g., Gemini Flash, Groq Llama, Haiku) | Structured, low-risk |
| Summary/report prose | Cheap model | Near-zero reasoning |
| **Optimization decisions & bid/recommendation logic** | **Stronger model only** (e.g., Gemini Pro / GPT-4 / Claude) | High-stakes: correctness > cost |
| RSA headline/description generation | Mid model | Creative but recoverable |

Key cost controls:
- Use **no-LLM determinism** for all number crunching (costs $0).
- Keep a **rule-based guardrail layer** so the LLM *recommends* but a rule layer validates thresholds **before any auto-apply write** (protects budget and results). Hard caps live in `config/settings.yaml` (e.g., max bid, max daily budget, minimum conversion threshold before bid changes). Any proposed change exceeding a cap is escalated to Slack, not applied.
- **Cache/avoid re-pulling** unchanged data; only send deltas to the model.
- Track per-run token spend; alert if a run exceeds a budget cap (e.g., \$0.05).

This keeps total inference cost in the **sub-$1/month** range while reserving the expensive model for the few decisions that actually move money.

---

## 5. Phased Implementation

### Phase 0 — Secure access (blocked on you, ~1 day effort)
- [ ] Provide GA4 service account (Viewer) + Property ID
- [ ] Provide Google Ads Customer ID, Login Customer ID, Developer Token, Desktop OAuth client + refresh token
- [ ] Load all into environment/secrets (work on this in parallel with Phase 1)

### Phase 1 — Scaffold + connectors + verify (unblocked once creds land)
- [ ] Clone repo; set up repo structure (see §6)
- [ ] Add `google-ads` + `google-analytics-data` Python clients; `.env`/secrets handling via env vars; `.gitignore` for secrets
- [ ] **Verify Google Ads**: `listAccessibleCustomers` + a GAQL query for the "Intent Leads" campaign (confirm what was partially built manually)
- [ ] **Verify GA4**: last-7-days sessions/conversions report
- [ ] **Verify CRM**: pull recent demo/lead records with source fields
- [ ] Build a **status doc** that flips each system to "Connected & Verified" — the integration-setup-documentation.md already has this table
- [ ] Add GitHub Actions scheduled run that performs the verification + baseline report

### Phase 2 — Baseline data + build preparation
- [ ] **Inventory the live Ads account**: query existing campaigns/ad groups/keywords/ads/negatives/settings. Compare to the plan (the campaign is *partially* setup manually — we must reconcile, not assume it matches `Campaign_Build_and_Launch_Plan.md`)
- [ ] **Regenerate missing artifacts** (ads_rsa / negatives / GTM instructions / phase-2 keywords) so the build is fully defined
- [ ] Pull Keyword Planner volume/CPC to "true up" the $4–$6 bid caps
- [ ] Baseline GA4 funnel (landing page → demo-success) and CRM demo-bookings historical counts
- [ ] Produce a **Gap Report** (what's built vs. plan) + **Build Spec**

### Phase 3 — Build/manage the campaign (API-based)
- [ ] Implement create/update for campaign, ad groups, keywords, negatives, RSAs, assets, settings per plan
- [ ] Create the **"Demo Request Submitted"** conversion action (or import from GA4 key event)
- [ ] Human-in-the-loop approval for writes (config-controlled; default "recommend only" until you flip to "apply")
- [ ] Idempotent builds so re-runs don't duplicate entities

### Phase 4 — Monitoring + optimization loop
- [ ] Daily monitor job (per §3.1)
- [ ] Weekly cross-source analysis: Ads spend/cost-per-demo → GA4 CVR/session → CRM pipeline value
- [ ] Optimization rules + guardrails (budget caps, negative-keyword suggestions, approval flags)
- [ ] Reporting: commit summary to the repo + Slack digest/alert (per confirmed decisions)

### Phase 5 — Scale
- [ ] After 15–30 conversions: recommend Smart bidding switch
- [ ] Add Phase-2 phrasematch keywords once budget increases
- [ ] Optional: "SalesNexus vs. Apollo" landing page (flagged gap in the plan)
- [ ] Consider cross-domain tracking of Free Trial signups (app-beta.salesnex.us) if it becomes a tracked goal

---

## 6. Proposed Repo Structure

```
Adwords-Analytics-Agent/
├── README.md
├── .github/workflows/
│   ├── daily-monitor.yml
│   └── weekly-analysis.yml
├── config/
│   ├── settings.yaml            # budget, lock CPAs, guardrails
│   └── campaign_plan.yaml       # mirrors Campaign_Build_and_Launch_Plan.md
├── src/
│   ├── connectors/
│   │   ├── google_ads_client.py
│   │   ├── ga4_client.py
│   │   └── crm_client.py
│   ├── analysis/                # deterministic ETL + rules (no LLM)
│   ├── llm/                     # tiered model routing
│   ├── actions/                 # build/manage/monitor/optimize
│   └── main.py                  # entrypoint per scheduled run
├── data/                        # sqlite state, CSV snapshots (gitignored mostly)
├── reports/                     # generated summaries, committed
└── docs/                        # plan, walkthroughs, status
```

Secrets live **only** in environment variables / Actions secrets — never in the repo.

---

## 7. Immediate Next Actions (what I recommend doing now)

1. **You obtain + securely provide the credentials** in §2 — this is the one hard blocker. Nothing else can proceed against live accounts until this is done.
2. **In parallel (needs no credentials):** scaffold the repo structure + connectors so that the moment creds land we run the Phase-1 verification within minutes. I can do this now.
3. **Recover/recreate the missing campaign artifacts** (ads_rsa, negatives, GTM instructions) so the build spec is complete.
4. **Reconcile the live account vs. plan** once read access works — the campaign is "partially setup manually," so assume a gap to close.

---

## 8. Decision Points for You

## Confirmed Decisions (locked 2026-09-06)
1. **Hosting:** GitHub Actions (scheduled), migrate to Cloud Run + Scheduler later if always-on needed.
2. **Write policy:** **Auto-apply within guardrails** — agent applies changes (bids, budget shifts, negatives) automatically, but only inside hard caps you set in `config/settings.yaml`. Any change outside caps escalates for review.
3. **Reporting:** Slack (webhook) for alerts/digests; commit report summaries to the repo as an audit log.
4. **Scope:** **Broader** — architecture supports multiple campaigns and other paid media (Search, Display, Performance Max, future) with per-campaign config; the "Intent Leads" campaign is the first managed entity.
