# GTA 6 Daily Checks & Automated Report Pipeline (`09:00 AM EST`)

This directory powers the **Daily 9:00 AM EST (`14:00 UTC` / `7:30 PM IST`) GTA VI & Leonida Market Pulse**, polling real live data across:
1. **Kalshi Trade API v2 (`api.elections.kalshi.com`)** — All 8 GTA VI series (`KXGTA6ONTIME`, `KXGTASALESRECORD`, `KXGTA6UNITS`, `KXGTAONLINE`, `KXGTAPCRELEASE`, `KXGTA6STORY`, `KXGTA6SONGS`, `KXGTA6` — currently tracking **62 active contracts** and **2.65M+ open interest**).
2. **Public Equities (`TTWO` & `DASH`)** — Live NASDAQ quotes & daily momentum for Take-Two Interactive and DoorDash.
3. **Gaming & Speedrun Telemetry** — Live Valve Steam concurrent player count (`AppID 271590`) and `Speedrun.com` verified *GTA VI* leaderboard runs.

---

## Option A: Run Automatically 24/7 on GitHub Actions (Cloud Cron)

A ready-to-run GitHub Actions workflow is located at [`gta6_daily_check.yml`](gta6_daily_check.yml) (`cron: "0 14 * * *"` = **9:00 AM EST daily** + manual `workflow_dispatch`).

To activate it in `.github/workflows/` from your terminal (requires the GitHub CLI `workflow` OAuth scope):

```powershell
gh auth refresh -h github.com -s workflow
New-Item -ItemType Directory -Force .github/workflows | Out-Null
Copy-Item "GTA 6 PREDICTION/automation/gta6_daily_check.yml" ".github/workflows/gta6_daily_check.yml"
git add .github/workflows/gta6_daily_check.yml
git commit -m "ci: activate 09:00 EST GitHub Actions workflow"
git push origin main
gh workflow run gta6_daily_check.yml
```

*(Alternatively, on GitHub.com click **Actions -> New workflow -> set up a workflow yourself** and paste [`gta6_daily_check.yml`](gta6_daily_check.yml)).*

---

## Option B: Run On-Demand or via Local Scheduler (Uses Existing `repo` Scope)

```powershell
powershell -ExecutionPolicy Bypass -File "GTA 6 PREDICTION/automation/run_daily_and_push.ps1"
```
