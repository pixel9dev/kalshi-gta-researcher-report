$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
Set-Location $RepoRoot

Write-Host "[Kalshi GTA6 Bot] Running live Kalshi API v2, TTWO/DASH & Steam checks..."
python src/gta6_daily_check.py

git add "GTA 6 PREDICTION/daily_reports/" "GTA 6 PREDICTION/charts/" "docs/live_pulse.json"
$diff = git status --porcelain
if ($diff) {
    $dateStr = (Get-Date).ToUniversalTime().ToString("yyyy-MM-dd")
    git commit -m "chore(gta6-daily): automated 09:00 EST Leonida & Kalshi market pulse [$dateStr]"
    git pull --rebase origin main
    git push origin main
    Write-Host "[Kalshi GTA6 Bot] Pushed daily report for $dateStr to GitHub."
} else {
    Write-Host "[Kalshi GTA6 Bot] No changes since last snapshot."
}
