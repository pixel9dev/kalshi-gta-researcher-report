"""
Kalshi GTA VI Daily Live Market, Equity & Telemetry Automation Engine
Runs daily at 09:00 AM EST (14:00 UTC) via GitHub Actions (.github/workflows/gta6_daily_check.yml)
or on-demand locally / via workflow_dispatch.

Live Unauthenticated Data Sources Polled:
  1. Kalshi Trade API v2 (live GTA VI series: KXGTA6ONTIME, KXGTASALESRECORD, KXGTA6UNITS,
     KXGTAONLINE, KXGTAPCRELEASE, KXGTA6STORY, KXGTA6SONGS, KXGTA6)
  2. Yahoo Finance Chart v8 API (TTWO Take-Two Interactive & DASH DoorDash live equity tape)
  3. Valve Steam Web API (GTA V AppID 271590 live concurrent player count)
  4. Speedrun.com REST API v1 (Grand Theft Auto VI leaderboard & verified run monitor)

Outputs Updated on Every Run:
  - GTA 6 PREDICTION/daily_reports/YYYY-MM-DD_Daily_Leonida_Pulse.md
  - GTA 6 PREDICTION/daily_reports/LATEST_DAILY_PULSE.md
  - GTA 6 PREDICTION/daily_reports/daily_telemetry_log.csv
  - GTA 6 PREDICTION/daily_reports/live_kalshi_gta6_orderbook.csv
  - GTA 6 PREDICTION/charts/05_live_kalshi_gta6_daily_pulse.png
  - docs/live_pulse.json
"""

from __future__ import annotations

from datetime import datetime, timezone
import json
import os
from pathlib import Path
import urllib.request
import urllib.parse

import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
G6_DIR = ROOT / "GTA 6 PREDICTION"
DAILY_DIR = G6_DIR / "daily_reports"
CHART_DIR = G6_DIR / "charts"
DOCS_DIR = ROOT / "docs"

for d in (DAILY_DIR, CHART_DIR, DOCS_DIR):
    d.mkdir(parents=True, exist_ok=True)

USER_AGENT = "Kalshi-GTA6-Research-Automation/1.0 (https://github.com/pixel9dev/kalshi-gta-researcher-report)"

KALSHI_GTA_SERIES = [
    ("KXGTA6ONTIME", "Launch On Time (Nov 19)"),
    ("KXGTASALESRECORD", "24h Gaming Revenue Record"),
    ("KXGTA6UNITS", "GTA VI Units Sold-In"),
    ("KXGTAONLINE", "GTA VI Online Release"),
    ("KXGTAPCRELEASE", "GTA VI PC Release Window"),
    ("KXGTA6STORY", "Story DLC / Content Window"),
    ("KXGTA6SONGS", "Launch Radio Tracklist"),
    ("KXGTA6", "Release Window Milestones"),
]

BG_DARK = "#0B0F14"
PANEL_BG = "#111821"
GRID_COL = "#1E293B"
TEXT_MAIN = "#F1F5F9"
TEXT_MUTED = "#94A3B8"
KALSHI_GREEN = "#00D287"
CYAN_ACCENT = "#38BDF8"
AMBER_WARN = "#F59E0B"
CORAL_RED = "#F43F5E"


def fetch_json(url: str, timeout: int = 10) -> dict | None:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as exc:
        print(f"[WARN] Non-fatal fetch fallback for {url}: {exc}")
        return None


def poll_kalshi_gta6_markets() -> pd.DataFrame:
    rows = []
    for series_ticker, category_label in KALSHI_GTA_SERIES:
        url = f"https://api.elections.kalshi.com/trade-api/v2/markets?series_ticker={series_ticker}&status=open&limit=20"
        payload = fetch_json(url)
        if not payload:
            continue
        for m in payload.get("markets", []):
            last_p = float(m.get("last_price_dollars") or 0.0)
            yes_bid = float(m.get("yes_bid_dollars") or 0.0)
            yes_ask = float(m.get("yes_ask_dollars") or 0.0)
            mid_p = round((yes_bid + yes_ask) / 2.0, 4) if (yes_bid > 0 and yes_ask > 0) else last_p
            vol_total = float(m.get("volume_fp") or 0.0)
            vol_24h = float(m.get("volume_24h_fp") or 0.0)
            open_int = float(m.get("open_interest_fp") or 0.0)
            subtitle = (m.get("yes_sub_title") or "").strip()
            title = (m.get("title") or "").strip()
            label = f"{title} [{subtitle}]" if subtitle and subtitle.lower() != "yes" else title

            rows.append({
                "Series": series_ticker,
                "Category": category_label,
                "Ticker": m.get("ticker", ""),
                "Contract_Label": label,
                "Subtitle": subtitle or "Yes",
                "Last_Price_Cents": round(last_p * 100, 1),
                "Yes_Bid_Cents": round(yes_bid * 100, 1),
                "Yes_Ask_Cents": round(yes_ask * 100, 1),
                "Implied_Prob_Pct": round((last_p if last_p > 0 else mid_p) * 100, 1),
                "Volume_24h_Contracts": round(vol_24h, 1),
                "Total_Volume_Contracts": round(vol_total, 1),
                "Open_Interest_Contracts": round(open_int, 1),
                "Status": m.get("status", "active"),
            })

    df = pd.DataFrame(rows)
    if not df.empty:
        df = df.sort_values(["Open_Interest_Contracts", "Total_Volume_Contracts"], ascending=False).reset_index(drop=True)
    return df


def poll_equity_quote(symbol: str) -> dict:
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1d&range=5d"
    payload = fetch_json(url)
    if not payload:
        return {"symbol": symbol, "price": None, "prev_close": None, "change_pct": None, "status": "UNAVAILABLE"}
    try:
        res = payload["chart"]["result"][0]
        meta = res["meta"]
        price = float(meta.get("regularMarketPrice") or 0.0)
        closes = [c for c in res["indicators"]["quote"][0].get("close", []) if c is not None]
        prev = float(closes[-2]) if len(closes) >= 2 else float(meta.get("chartPreviousClose") or price)
        chg_pct = round(((price - prev) / prev) * 100.0, 2) if prev else 0.0
        return {
            "symbol": symbol,
            "price": round(price, 2),
            "prev_close": round(prev, 2),
            "change_pct": chg_pct,
            "currency": meta.get("currency", "USD"),
            "status": "LIVE",
        }
    except Exception as exc:
        print(f"[WARN] Quote parse error for {symbol}: {exc}")
        return {"symbol": symbol, "price": None, "prev_close": None, "change_pct": None, "status": "PARSE_ERR"}


def poll_steam_gtav_players() -> int | None:
    url = "https://api.steampowered.com/ISteamUserStats/GetNumberOfCurrentPlayers/v1/?appid=271590"
    payload = fetch_json(url)
    if not payload:
        return None
    return payload.get("response", {}).get("player_count")


def poll_speedrun_gta6() -> dict:
    q = urllib.parse.quote("Grand Theft Auto VI")
    url = f"https://www.speedrun.com/api/v1/games?name={q}&max=5"
    payload = fetch_json(url)
    if not payload or not payload.get("data"):
        return {"game_found": False, "game_id": None, "verified_runs_status": "Pending Launch"}
    for g in payload["data"]:
        title = g.get("names", {}).get("international", "")
        if "VI" in title or "6" in title:
            gid = g.get("id")
            runs_payload = fetch_json(f"https://www.speedrun.com/api/v1/runs?game={gid}&status=verified&max=5")
            n_runs = len(runs_payload.get("data", [])) if runs_payload else 0
            return {
                "game_found": True,
                "game_id": gid,
                "title": title,
                "verified_runs_count": n_runs,
                "weblink": g.get("weblink", "https://www.speedrun.com"),
            }
    return {"game_found": False, "game_id": None, "verified_runs_status": "Awaiting Board Activation"}


def generate_live_pulse_chart(df_mkts: pd.DataFrame, ts_str: str) -> Path:
    plt.rcParams.update({
        "figure.facecolor": BG_DARK,
        "axes.facecolor": PANEL_BG,
        "axes.edgecolor": GRID_COL,
        "axes.labelcolor": TEXT_MAIN,
        "text.color": TEXT_MAIN,
        "xtick.color": TEXT_MUTED,
        "ytick.color": TEXT_MUTED,
        "grid.color": GRID_COL,
        "font.family": "sans-serif",
        "font.sans-serif": ["Segoe UI", "Inter", "DejaVu Sans", "Arial"],
    })

    out_chart = CHART_DIR / "05_live_kalshi_gta6_daily_pulse.png"
    if df_mkts.empty:
        fig, ax = plt.subplots(figsize=(10, 4), dpi=160)
        ax.text(0.5, 0.5, f"Kalshi Live API Snapshot ({ts_str}): Awaiting Active Orderbooks",
                ha="center", va="center", fontsize=12, color=TEXT_MAIN)
        fig.savefig(out_chart)
        plt.close(fig)
        return out_chart

    top = df_mkts[df_mkts["Open_Interest_Contracts"] > 0].head(10).iloc[::-1]
    if top.empty:
        top = df_mkts.head(10).iloc[::-1]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13.2, 6.2), dpi=180, gridspec_kw={"width_ratios": [1.25, 1.0]})
    y = np.arange(len(top))
    short_labels = [
        f"{r['Ticker']} ({r['Subtitle'][:20]})" for _, r in top.iterrows()
    ]

    probs = top["Implied_Prob_Pct"].values
    bar_colors = [KALSHI_GREEN if p >= 65 else (CYAN_ACCENT if p >= 30 else AMBER_WARN) for p in probs]
    b1 = ax1.barh(y, probs, color=bar_colors, height=0.6)
    ax1.set_yticks(y)
    ax1.set_yticklabels(short_labels, fontsize=8.4, color=TEXT_MAIN)
    ax1.xaxis.set_major_formatter(mtick.FuncFormatter(lambda v, _: f"{v:.0f}¢"))
    ax1.set_xlim(0, 114)
    ax1.set_xlabel("Live Implied Probability / Last Price (¢)", fontsize=10)
    ax1.set_title("Live Kalshi GTA VI Markets — Implied Odds", fontsize=11.5, fontweight="bold", pad=10)
    ax1.grid(True, axis="x", linestyle="--", alpha=0.38)
    for bar, val in zip(b1, probs):
        ax1.text(val + 1.8, bar.get_y() + bar.get_height() / 2, f"{val:.1f}¢",
                 va="center", fontsize=8.3, fontweight="bold", color=TEXT_MAIN)

    oi_k = top["Open_Interest_Contracts"].values / 1e3
    b2 = ax2.barh(y, oi_k, color=CORAL_RED, alpha=0.88, height=0.6)
    ax2.set_yticks(y)
    ax2.set_yticklabels(["" for _ in y])
    ax2.xaxis.set_major_formatter(mtick.FuncFormatter(lambda v, _: f"{v:,.0f}K"))
    max_oi = max(float(np.max(oi_k)) if len(oi_k) else 10.0, 1.0)
    ax2.set_xlim(0, max_oi * 1.24)
    ax2.set_xlabel("Live Open Interest (Thousands of Contracts)", fontsize=10)
    ax2.set_title("Open Interest Depth (Kalshi API v2)", fontsize=11.5, fontweight="bold", pad=10)
    ax2.grid(True, axis="x", linestyle="--", alpha=0.38)
    for bar, val in zip(b2, oi_k):
        ax2.text(val + max_oi * 0.02, bar.get_y() + bar.get_height() / 2, f"{val:,.1f}K",
                 va="center", fontsize=8.3, fontweight="bold", color=TEXT_MAIN)

    fig.suptitle(f"Automated Daily Kalshi × GTA VI Live Market Pulse  |  Snapshot: {ts_str}",
                 fontsize=13, fontweight="bold", y=0.98)
    fig.tight_layout(rect=[0, 0, 1, 0.94])
    fig.savefig(out_chart)
    plt.close(fig)
    return out_chart


def main() -> None:
    now_utc = datetime.now(timezone.utc)
    date_slug = now_utc.strftime("%Y-%m-%d")
    ts_utc = now_utc.strftime("%Y-%m-%d %H:%M:%S UTC")
    launch_utc = datetime(2026, 11, 19, 5, 0, 0, tzinfo=timezone.utc)  # 00:00 EST Nov 19 = 05:00 UTC
    delta_hours = round((launch_utc - now_utc).total_seconds() / 3600.0, 1)
    countdown_label = f"T-{abs(delta_hours):.1f}h to Midnight EST Launch" if delta_hours > 0 else f"T+{abs(delta_hours):.1f}h Post-Launch Live"

    desk_note = os.environ.get("DESK_NOTE", "").strip()

    df_kalshi = poll_kalshi_gta6_markets()
    ttwo = poll_equity_quote("TTWO")
    dash = poll_equity_quote("DASH")
    steam_gtav = poll_steam_gtav_players()
    sr_info = poll_speedrun_gta6()

    # Save latest live Kalshi orderbook snapshot CSV
    orderbook_csv = DAILY_DIR / "live_kalshi_gta6_orderbook.csv"
    if not df_kalshi.empty:
        df_kalshi.to_csv(orderbook_csv, index=False)

    total_kalshi_vol = float(df_kalshi["Total_Volume_Contracts"].sum()) if not df_kalshi.empty else 0.0
    total_kalshi_24h = float(df_kalshi["Volume_24h_Contracts"].sum()) if not df_kalshi.empty else 0.0
    total_kalshi_oi = float(df_kalshi["Open_Interest_Contracts"].sum()) if not df_kalshi.empty else 0.0
    active_mkt_count = int(len(df_kalshi))

    rec_prob = None
    ontime_prob = None
    if not df_kalshi.empty:
        rec_match = df_kalshi[df_kalshi["Series"] == "KXGTASALESRECORD"]
        if not rec_match.empty:
            rec_prob = float(rec_match.iloc[0]["Implied_Prob_Pct"])
        ont_match = df_kalshi[df_kalshi["Series"] == "KXGTA6ONTIME"]
        if not ont_match.empty:
            ontime_prob = float(ont_match.iloc[0]["Implied_Prob_Pct"])

    # Append daily historical row (deduplicating same UTC date by keeping latest snapshot)
    hist_csv = DAILY_DIR / "daily_telemetry_log.csv"
    new_row = {
        "Date_UTC": date_slug,
        "Timestamp_UTC": ts_utc,
        "Launch_Phase": countdown_label,
        "Active_Kalshi_GTA6_Markets": active_mkt_count,
        "Kalshi_GTA6_Total_Volume": round(total_kalshi_vol, 0),
        "Kalshi_GTA6_24h_Volume": round(total_kalshi_24h, 0),
        "Kalshi_GTA6_Open_Interest": round(total_kalshi_oi, 0),
        "KXGTASALESRECORD_Yes_Cents": rec_prob,
        "KXGTA6ONTIME_Yes_Cents": ontime_prob,
        "TTWO_Price_USD": ttwo.get("price"),
        "TTWO_Daily_Chg_Pct": ttwo.get("change_pct"),
        "DASH_Price_USD": dash.get("price"),
        "DASH_Daily_Chg_Pct": dash.get("change_pct"),
        "Steam_GTAV_Concurrent_Players": steam_gtav,
        "Speedrun_Verified_GTA6_Runs": sr_info.get("verified_runs_count", 0),
    }

    if hist_csv.exists():
        df_hist = pd.read_csv(hist_csv)
        df_hist = df_hist[df_hist["Date_UTC"] != date_slug]
        df_hist = pd.concat([df_hist, pd.DataFrame([new_row])], ignore_index=True)
    else:
        df_hist = pd.DataFrame([new_row])
    df_hist.to_csv(hist_csv, index=False)

    # Generate live chart
    generate_live_pulse_chart(df_kalshi, ts_utc)

    # Build Markdown table of top 12 live Kalshi GTA VI markets
    mkt_table_lines = [
        "| Kalshi Ticker | Series | Market / Outcome | Last (`¢`) | Bid / Ask (`¢`) | 24h Vol | Open Interest |",
        "| :--- | :--- | :--- | ---: | :---: | ---: | ---: |",
    ]
    if not df_kalshi.empty:
        for _, r in df_kalshi.head(12).iterrows():
            short_title = r["Contract_Label"]
            if len(short_title) > 58:
                short_title = short_title[:55] + "..."
            mkt_table_lines.append(
                f"| `{r['Ticker']}` | `{r['Series']}` | {short_title} | **{r['Implied_Prob_Pct']:.1f}¢** | "
                f"`{r['Yes_Bid_Cents']:.0f}¢ / {r['Yes_Ask_Cents']:.0f}¢` | {r['Volume_24h_Contracts']:,.0f} | **{r['Open_Interest_Contracts']:,.0f}** |"
            )
    else:
        mkt_table_lines.append("| *API Snapshot Offline* | — | — | — | — | — | — |")

    ttwo_str = f"\\${ttwo['price']:,.2f} ({ttwo['change_pct']:+.2f}%)" if ttwo.get("price") else "Market Closed / N/A"
    dash_str = f"\\${dash['price']:,.2f} ({dash['change_pct']:+.2f}%)" if dash.get("price") else "Market Closed / N/A"
    steam_str = f"{steam_gtav:,} concurrent PC players" if steam_gtav else "N/A"
    note_block = f"\n> **Analyst Desk Note:** {desk_note}\n" if desk_note else ""

    report_md = f"""# Automated Daily GTA VI & Leonida Market Pulse — {date_slug}
**Generated Automatically by Kalshi GTA Research Bot**  
**Timestamp:** `{ts_utc}` | **Launch Clock:** `{countdown_label}` | **Schedule:** Daily at `09:00 AM EST (14:00 UTC)`
{note_block}
---

## 1. Live Cross-Market Snapshot (Kalshi API v2 + Equities + Gaming Telemetry)

| Signal Pillar | Live Observed Metric | Latest Reading | Desk Interpretation |
| :--- | :--- | :--- | :--- |
| **Kalshi GTA VI Ecosystem** | Active Open Contracts (`{len(KALSHI_GTA_SERIES)}` Series) | **`{active_mkt_count}` markets** | `{total_kalshi_oi:,.0f}` open interest / `{total_kalshi_vol:,.0f}` cumulative contracts traded |
| **24h Revenue Record (`KXGTASALESRECORD`)** | *Highest-grossing game in 24h?* | **`{f"{rec_prob:.1f}¢" if rec_prob is not None else "N/A"}`** | Market heavily prices Day-1 pre-order + Deluxe ASP record smash |
| **Launch On-Time (`KXGTA6ONTIME`)** | *Releases by Nov 19, 2026?* | **`{f"{ontime_prob:.1f}¢" if ontime_prob is not None else "N/A"}`** | Locked into midnight regional console rollout |
| **Take-Two Interactive (`TTWO`)** | NASDAQ Live / Last Close | **{ttwo_str}** | Public equity proxy for Year-1 bookings & GTA VI Online expectations |
| **DoorDash (`DASH`)** | NASDAQ Live / Last Close | **{dash_str}** | Primary real-economy derivative for 96-hour launch delivery surge (`+\\$434M` GOV model) |
| **GTA V Pre-Launch Baseline** | Live Steam Concurrent (`AppID 271590`) | **{steam_str}** | Tracks franchise engagement & post-Nov-19 cannibalization velocity |
| **Speedrun.com Verification** | Verified *GTA VI* Any% Runs | **`{sr_info.get("verified_runs_count", 0)}` verified runs** | Monitors sub-18h Week-1 speedrun threshold (`KXSPEEDRUN-W1-18H`) |

---

## 2. Live Kalshi GTA VI Orderbook Leaders (Sorted by Open Interest)

{chr(10).join(mkt_table_lines)}

---

## 3. Live Visual Orderbook & Open-Interest Pulse

![Live Kalshi GTA VI Daily Pulse](../charts/05_live_kalshi_gta6_daily_pulse.png)

---

## 4. Historical Daily Automation Log (`daily_telemetry_log.csv`)

- **Cumulative Snapshots Logged:** `{len(df_hist)}`
- **Raw Time-Series CSV:** [`daily_telemetry_log.csv`](daily_telemetry_log.csv)
- **Full Live Kalshi Orderbook CSV:** [`live_kalshi_gta6_orderbook.csv`](live_kalshi_gta6_orderbook.csv)
"""

    dated_report = DAILY_DIR / f"{date_slug}_Daily_Leonida_Pulse.md"
    latest_report = DAILY_DIR / "LATEST_DAILY_PULSE.md"
    dated_report.write_text(report_md, encoding="utf-8")

    # Adjust relative image path for LATEST_DAILY_PULSE.md (same directory, so same ../charts/ works!)
    latest_report.write_text(report_md, encoding="utf-8")

    # Write docs/live_pulse.json for GitHub Pages Interactive Terminal!
    pulse_json = {
        "updated_utc": ts_utc,
        "countdown": countdown_label,
        "active_kalshi_markets": active_mkt_count,
        "total_open_interest": round(total_kalshi_oi, 0),
        "total_volume": round(total_kalshi_vol, 0),
        "volume_24h": round(total_kalshi_24h, 0),
        "sales_record_prob_cents": rec_prob,
        "ontime_prob_cents": ontime_prob,
        "ttwo": ttwo,
        "dash": dash,
        "steam_gtav_concurrent": steam_gtav,
        "speedrun_verified_runs": sr_info.get("verified_runs_count", 0),
        "top_markets": df_kalshi.head(8).to_dict(orient="records") if not df_kalshi.empty else [],
    }
    (DOCS_DIR / "live_pulse.json").write_text(json.dumps(pulse_json, indent=2), encoding="utf-8")
    print(f"[OK] Generated daily pulse for {date_slug} | {active_mkt_count} live Kalshi GTA VI markets | OI={total_kalshi_oi:,.0f}")


if __name__ == "__main__":
    main()
