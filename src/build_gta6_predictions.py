"""
Kalshi GTA VI (Leonida) Pre-Launch Prediction Engine
Generates inside `GTA 6 PREDICTION/`:
  1. 4 CSV datasets in `GTA 6 PREDICTION/data/`
  2. Multi-tab live-formula Excel model in `GTA 6 PREDICTION/spreadsheets/Kalshi_GTA6_Leonida_Prediction_Model.xlsx`
  3. 4 High-DPI Kalshi dark-mode prediction charts in `GTA 6 PREDICTION/charts/`
"""

from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

ROOT = Path(__file__).resolve().parent.parent
G6_DIR = ROOT / "GTA 6 PREDICTION"
DATA_DIR = G6_DIR / "data"
SHEET_DIR = G6_DIR / "spreadsheets"
CHART_DIR = G6_DIR / "charts"

for d in (DATA_DIR, SHEET_DIR, CHART_DIR):
    d.mkdir(parents=True, exist_ok=True)

BG_DARK = "#0B0F14"
PANEL_BG = "#111821"
GRID_COL = "#1E293B"
TEXT_MAIN = "#F1F5F9"
TEXT_MUTED = "#94A3B8"
KALSHI_GREEN = "#00D287"
CYAN_ACCENT = "#38BDF8"
AMBER_WARN = "#F59E0B"
CORAL_RED = "#F43F5E"
PURPLE_ACCENT = "#A855F7"

plt.rcParams.update({
    "figure.facecolor": BG_DARK,
    "axes.facecolor": PANEL_BG,
    "axes.edgecolor": GRID_COL,
    "axes.labelcolor": TEXT_MAIN,
    "text.color": TEXT_MAIN,
    "xtick.color": TEXT_MUTED,
    "ytick.color": TEXT_MUTED,
    "grid.color": GRID_COL,
    "grid.alpha": 0.55,
    "font.family": "sans-serif",
    "font.sans-serif": ["Segoe UI", "Inter", "DejaVu Sans", "Arial"],
})


def build_gta6_datasets() -> dict[str, pd.DataFrame]:
    # 1. Leonida 6 Confirmed Regions Economic Matrix
    regions = [
        ("Leonida Keys", "Florida Keys", "Brian Heder Boatyard & Smuggling", 185_000, 18.0, 35, 82, "Act I Seed Smuggling Drops"),
        ("Port Gellhorn", "Gulf Coast", "Pawn Shops, Motels & Chop-Shops", 145_000, 12.0, 48, 76, "Cross-Region Fence Spreads"),
        ("Grassrivers", "Everglades", "Off-Grid Airboats & Cartel Caches", 230_000, 10.0, 22, 79, "Zero-Radar Contraband Transit"),
        ("Ambrosia", "Central Sugar Belt", "Sugar Refinery Monopoly & Bikers", 410_000, 15.0, 64, 91, "'Redwood 2.0' Corporate Stock Sabotage"),
        ("Mount Kalaga", "Northern Highlands", "Wilderness Pelts & Prepper Bunkers", 310_000, 8.0, 18, 86, "Hour-2 Static Gold/Bullion Caches"),
        ("Vice City", "Modern Miami", "Boobie Ike Fronts & Raul Bautista Scores", 1_650_000, 14.0, 88, 97, "Clean Laundering + Endgame Vaults + Crypto"),
    ]
    df_regions = pd.DataFrame(regions, columns=[
        "Region", "Real_World_Analog", "Confirmed_Economic_Anchor",
        "Predicted_Peak_Dirty_Cash_Per_Hr", "Predicted_Laundering_Haircut_Pct",
        "Police_ANPR_Heat_Index_0_100", "Exploit_Alpha_Score_0_100", "Primary_MinMax_Hypothesis"
    ])
    df_regions["Net_Clean_Banked_Per_Hr"] = (
        df_regions["Predicted_Peak_Dirty_Cash_Per_Hr"] * (1.0 - df_regions["Predicted_Laundering_Haircut_Pct"] / 100.0)
    ).round(0).astype(int)

    # 2. Cumulative Revenue Trajectory: GTA VI Forecast vs DFC Consensus vs GTA V 2013
    rev_rows = [
        ("T+0h (Pre-Orders)", 0, 1.26, 1.05, 0.28, 0.39),
        ("T+24h (Day 1)", 1, 1.79, 1.52, 0.82, 1.13),
        ("T+72h (Launch Wknd)", 3, 2.38, 2.05, 1.00, 1.38),
        ("T+7d (Week 1)", 7, 2.64, 2.30, 1.15, 1.59),
        ("T+30d (Month 1)", 30, 2.95, 2.65, 1.35, 1.86),
        ("T+90d (Quarter 1)", 90, 3.18, 2.90, 1.52, 2.10),
        ("T+365d (Year 1 + Online)", 365, 3.48, 3.20, 1.98, 2.73),
    ]
    df_rev = pd.DataFrame(rev_rows, columns=[
        "Milestone", "Days_Elapsed",
        "Kalshi_Desk_GTAVI_Rev_Billions", "DFC_Consensus_GTAVI_Rev_Billions",
        "GTA5_2013_Nominal_Billions", "GTA5_2013_InflationAdj_2026_Billions"
    ])

    # 3. 96-Hour Launch Window: DoorDash Surge & US Workplace Absence Curve
    timeline = [
        ("Thu 00:00-04:00", 6.80, 44.0, 0.35, 78.5, "Midnight Preload Unlock + Late-Night DashMart Surge"),
        ("Thu 04:00-08:00", 3.90, 26.0, 0.60, 41.2, "All-Nighter Streamers + Early East Coast Wake-Up"),
        ("Thu 08:00-12:00", 4.85, 18.5, 1.92, 52.0, "Wave 1 'GTA Flu' Sick Calls Hit Slack/HR"),
        ("Thu 12:00-17:00", 5.35, 21.0, 1.98, 68.4, "WFH Stealth Sessions + Lunch Delivery Spike"),
        ("Thu 17:00-23:59", 10.90, 31.0, 0.40, 118.6, "Post-Work Convergence; 6.5M Global Stream Viewers"),
        ("Fri 00:00-08:00", 5.60, 36.5, 0.55, 59.0, "Night-2 Binge; Act II Grassrivers/Ambrosia Push"),
        ("Fri 08:00-17:00", 6.40, 24.0, 2.38, 84.5, "Peak 2.38M US Absences (4-Day Weekend PTO Bridge)"),
        ("Fri 17:00-Sat 03:00", 12.20, 38.5, 0.20, 142.0, "Peak US Concurrency (12.2M) & Peak DoorDash GOV"),
        ("Sat 03:00-23:59", 11.60, 23.5, 0.15, 112.4, "Weekend Act III Vice City Heist Grind"),
        ("Sun 00:00-23:59", 11.10, 20.5, 0.15, 91.4, "First Unrouted Story Credits Roll; Sunday Prep"),
    ]
    df_hourly = pd.DataFrame(timeline, columns=[
        "Window_EST", "US_Active_Players_Millions", "DoorDash_Order_Surge_Pct",
        "US_Absent_Workers_Millions", "Incremental_Delivery_GOV_USD_M", "Phase_Notes"
    ])

    # 4. 15 Kalshi GTA VI Event Contracts
    contracts_15 = [
        ("KXGTAVI-ASP-79", "US PS5 Standard Base MSRP > $70 (79.99+ SKU)", "PlayStation Store US", 0.58, 0.42, "BUY NO"),
        ("KXGTAVI-PRE-12B", "Pre-Launch Pre-Order Revenue > $1.20B", "TTWO IR / DFC", 0.54, 0.71, "BUY YES"),
        ("KXGTAVI-REV24H-16B", "24-Hour Global Gross Revenue > $1.60B", "TTWO Form 8-K", 0.59, 0.76, "STRONG BUY YES"),
        ("KXGTAVI-REV72H-22B", "72-Hour Global Gross Revenue > $2.20B", "TTWO Form 8-K", 0.52, 0.67, "BUY YES"),
        ("KXGTAVI-Y1-32B", "First-12-Month Gross Bookings > $3.20B", "TTWO 10-K/10-Q", 0.60, 0.73, "BUY YES"),
        ("KXGTAVI-META-96", "Metacritic PS5 Critic Score >= 96", "Metacritic (T+14d)", 0.64, 0.72, "BUY YES"),
        ("KXDASH-LAUNCH-15P", "US Late-Night Food Delivery +15% YoY Launch Wknd", "DoorDash / Second Measure", 0.64, 0.83, "MAX CONVICTION YES"),
        ("KXLABOR-PTO-22M", ">= 2.20M US Full-Time Workers Absent Nov 19-20", "UKG / BLS CPS", 0.61, 0.78, "STRONG BUY YES"),
        ("KXTWITCH-CONC-40M", "Twitch-Only GTA VI Category > 4.00M Concurrent", "TwitchTracker", 0.73, 0.61, "BUY NO"),
        ("KXYOUTUBE-VIEWS-250M", "YouTube GTA VI Views > 250M in First 24h", "YouTube Trends", 0.66, 0.82, "BUY YES"),
        ("KXROCKSTAR-DOWN-60M", "Rockstar Services >= 60m Down/Limited in Day 1", "Rockstar Status", 0.70, 0.85, "BUY YES"),
        ("KXSPEEDRUN-W1-18H", "Verified Glitchless Any% Beat < 18h 00m in Wk 1", "Speedrun.com", 0.49, 0.27, "STRONG BUY NO"),
        ("KXLEONIDA-1B-72H", "Unmodded Console Player Hits $1B in Story in 72h", "Verified Uncut VoD", 0.45, 0.34, "OBSERVE / LEAN NO"),
        ("KXLEONIDA-HOTFIX-W1", "Rockstar Patches Story Money Glitch in Week 1", "Rockstar Patch Notes", 0.62, 0.44, "BUY NO"),
        ("KXTTWO-CLOSE-UP5", "TTWO Stock Closes >= +5.0% in 5 Trading Days Post-Launch", "NASDAQ Close", 0.58, 0.41, "BUY NO"),
    ]
    df_k15 = pd.DataFrame(contracts_15, columns=[
        "Ticker", "Contract_Question", "Oracle", "Retail_Consensus_Yes", "Kalshi_Desk_Fair_Yes", "Action_Signal"
    ])
    df_k15["Edge_Bps"] = ((df_k15["Kalshi_Desk_Fair_Yes"] - df_k15["Retail_Consensus_Yes"]).abs() * 10_000).round(0).astype(int)

    datasets = {
        "01_leonida_regional_economy_forecast": df_regions,
        "02_gta6_revenue_trajectory_72h_to_y1": df_rev,
        "03_nov19_hourly_doordash_and_labor_curve": df_hourly,
        "04_kalshi_gta6_15_contracts_pricing": df_k15,
    }
    for name, df in datasets.items():
        df.to_csv(DATA_DIR / f"{name}.csv", index=False)
    return datasets


def build_gta6_excel(datasets: dict[str, pd.DataFrame]) -> Path:
    out_path = SHEET_DIR / "Kalshi_GTA6_Leonida_Prediction_Model.xlsx"
    wb = openpyxl.Workbook()
    wb.remove(wb.active)

    header_fill = PatternFill("solid", fgColor="0A2E23")
    zebra_fill = PatternFill("solid", fgColor="F8FAFC")
    accent_fill = PatternFill("solid", fgColor="D1FAE5")
    header_font = Font(name="Calibri", size=11, bold=True, color="00FF9D")
    title_font = Font(name="Calibri", size=14, bold=True, color="064E3B")
    bold_font = Font(name="Calibri", size=10, bold=True, color="0F172A")
    reg_font = Font(name="Calibri", size=10, color="0F172A")
    thin_border = Border(
        bottom=Side(style="thin", color="CBD5E1"),
        top=Side(style="thin", color="E2E8F0"),
    )

    ws_exec = wb.create_sheet("00_GTA6_Prediction_Summary")
    ws_exec["A1"] = "KALSHI GTA VI (LEONIDA) PRE-LAUNCH PREDICTION MODEL"
    ws_exec["A1"].font = title_font
    ws_exec["A2"] = "Live Formula-Driven Forecast | Launching Midnight November 19, 2026"
    ws_exec["A2"].font = Font(name="Calibri", size=10, italic=True, color="475569")

    summary_rows = [
        ("Forecast Metric / Kalshi Alpha KPI", "Live Formula / Projection", "Methodology / Benchmark"),
        ("Projected Day-1 Global Revenue ($ Billions)", "='02_Revenue_Curve'!C4", "Includes recognized digital pre-orders (~22.4M units)"),
        ("Projected 72-Hour Global Revenue ($ Billions)", "='02_Revenue_Curve'!C5", "2.38x GTA V's $1.00B 72h record"),
        ("Projected Year-1 Total Bookings ($ Billions)", "='02_Revenue_Curve'!C9", "Kalshi Desk ($3.48B) vs DFC Consensus ($3.20B)"),
        ("Peak Vice City Net Clean Laundering Rate ($/hr)", "=MAX('01_Leonida_Regions'!I3:I8)", "After predicted Boobie Ike front laundering haircut"),
        ("Peak US Simultaneous Active Players (Millions)", "=MAX('03_Hourly_Fallout'!B3:B12)", "Friday night marathon peak"),
        ("Peak US Absent Full-Time Workers (Millions)", "=MAX('03_Hourly_Fallout'!D3:D12)", "Friday Nov 20 4-day-weekend bridge"),
        ("Total 96h US Incremental Delivery GOV ($ Millions)", "=SUM('03_Hourly_Fallout'!E3:E12)*0.764", "Net national food/convenience delivery surge ($648M)"),
        ("Highest-Edge Kalshi Contract (bps)", "=MAX('04_Kalshi_15_Markets'!G3:G17)", "KXSPEEDRUN-W1-18H (+2,200 bps) & KXDASH (+1,900 bps)"),
        ("Average Absolute Pricing Edge Across 15 Markets (bps)", "=AVERAGE('04_Kalshi_15_Markets'!G3:G17)", "Mean institutional edge vs retail consensus"),
    ]
    for r_idx, row in enumerate(summary_rows, start=4):
        for c_idx, val in enumerate(row, start=1):
            cell = ws_exec.cell(row=r_idx, column=c_idx, value=val)
            if r_idx == 4:
                cell.fill = header_fill
                cell.font = header_font
            else:
                cell.font = bold_font if c_idx == 2 else reg_font
                cell.border = thin_border
                if c_idx == 2:
                    cell.fill = accent_fill
                    cell.number_format = "0.00" if r_idx in (5, 6, 7, 9, 10) else "$#,##0" if r_idx in (8, 11) else "#,##0"

    for col, width in zip("ABC", [54, 24, 54]):
        ws_exec.column_dimensions[col].width = width

    tabs = [
        ("01_Leonida_Regions", datasets["01_leonida_regional_economy_forecast"]),
        ("02_Revenue_Curve", datasets["02_gta6_revenue_trajectory_72h_to_y1"]),
        ("03_Hourly_Fallout", datasets["03_nov19_hourly_doordash_and_labor_curve"]),
        ("04_Kalshi_15_Markets", datasets["04_kalshi_gta6_15_contracts_pricing"]),
    ]
    for sname, df in tabs:
        ws = wb.create_sheet(sname)
        ws["A1"] = f"KALSHI GTA VI PREDICTION TABLE — {sname.upper()}"
        ws["A1"].font = title_font
        for c_idx, col_name in enumerate(df.columns, start=1):
            cell = ws.cell(row=2, column=c_idx, value=col_name)
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

        for r_idx, (_, row) in enumerate(df.iterrows(), start=3):
            for c_idx, col_name in enumerate(df.columns, start=1):
                val = row[col_name]
                if isinstance(val, (np.integer,)):
                    val = int(val)
                elif isinstance(val, (np.floating,)):
                    val = float(val)
                cell = ws.cell(row=r_idx, column=c_idx, value=val)
                cell.font = reg_font
                cell.border = thin_border
                if r_idx % 2 == 1:
                    cell.fill = zebra_fill

        if sname == "01_Leonida_Regions":
            for r in range(3, 9):
                ws[f"I{r}"] = f"=ROUND(D{r}*(1-E{r}/100),0)"
        elif sname == "04_Kalshi_15_Markets":
            for r in range(3, 18):
                ws[f"G{r}"] = f"=ROUND(ABS(E{r}-D{r})*10000,0)"

        ws.freeze_panes = "A3"
        for col_idx, col_name in enumerate(df.columns, start=1):
            col_letter = get_column_letter(col_idx)
            max_len = max(len(str(col_name)), *(len(str(v)) for v in df[col_name]))
            ws.column_dimensions[col_letter].width = min(max(max_len + 4, 14), 44)

    wb.save(out_path)
    return out_path


def generate_gta6_charts(datasets: dict[str, pd.DataFrame]) -> list[Path]:
    paths: list[Path] = []

    # Chart 1: GTA VI Revenue Curve vs DFC Consensus vs GTA V 2013
    df_r = datasets["02_gta6_revenue_trajectory_72h_to_y1"]
    fig, ax = plt.subplots(figsize=(11.2, 5.8), dpi=180)
    x = np.arange(len(df_r))

    ax.plot(x, df_r["Kalshi_Desk_GTAVI_Rev_Billions"], marker="o", linewidth=3.0, color=KALSHI_GREEN,
            label="Kalshi Desk GTA VI Forecast (USD 1.79B in 24h -> 3.48B Y1)")
    ax.plot(x, df_r["DFC_Consensus_GTAVI_Rev_Billions"], marker="s", linestyle="--", linewidth=2.3, color=CYAN_ACCENT,
            label="DFC Intelligence / Industry Consensus ($3.20B Y1)")
    ax.plot(x, df_r["GTA5_2013_InflationAdj_2026_Billions"], marker="^", linestyle="-.", linewidth=2.1, color=AMBER_WARN,
            label="GTA V (2013) Real Revenue in 2026 USD ($1.38B 72h)")
    ax.plot(x, df_r["GTA5_2013_Nominal_Billions"], marker="x", linestyle=":", linewidth=1.8, color=CORAL_RED,
            label="GTA V (2013) Nominal Revenue ($1.00B 72h)")

    ax.set_xticks(x)
    ax.set_xticklabels(df_r["Milestone"], rotation=18, ha="right", fontsize=9.2)
    ax.yaxis.set_major_formatter(mtick.FuncFormatter(lambda v, _: f"${v:.2f}B"))
    ax.set_ylim(0, 3.95)
    ax.set_ylabel("Cumulative Global Gross Bookings (USD Billions)", fontsize=10.5)
    ax.set_title("GTA VI Launch & Year-1 Revenue Trajectory: Kalshi Quant Model vs. GTA V Record",
                 fontsize=13, fontweight="bold", pad=14)
    for idx_pt, val in enumerate(df_r["Kalshi_Desk_GTAVI_Rev_Billions"]):
        ax.text(idx_pt, val + 0.11, f"${val:.2f}B", ha="center", fontsize=8.6, fontweight="bold", color=KALSHI_GREEN)
    ax.legend(loc="lower right", frameon=True, facecolor=BG_DARK, edgecolor=GRID_COL, fontsize=9)
    ax.grid(True, linestyle="--", alpha=0.38)
    fig.tight_layout()
    p1 = CHART_DIR / "01_gta6_vs_gta5_revenue_curve.png"
    fig.savefig(p1)
    plt.close(fig)
    paths.append(p1)

    # Chart 2: Leonida's 6 Confirmed Regions — Net Clean Hourly Yield & Exploit Alpha Score
    df_reg = datasets["01_leonida_regional_economy_forecast"].sort_values("Net_Clean_Banked_Per_Hr", ascending=True)
    fig, ax1 = plt.subplots(figsize=(11.4, 5.8), dpi=180)
    y_pos = np.arange(len(df_reg))
    bar_cols = [CYAN_ACCENT, CYAN_ACCENT, AMBER_WARN, PURPLE_ACCENT, AMBER_WARN, KALSHI_GREEN]
    bars = ax1.barh(y_pos, df_reg["Net_Clean_Banked_Per_Hr"] / 1e3, color=bar_cols, height=0.58)
    ax1.set_yticks(y_pos)
    ax1.set_yticklabels([f"{r} ({a})" for r, a in zip(df_reg["Region"], df_reg["Real_World_Analog"])], fontsize=9.5, color=TEXT_MAIN)
    ax1.xaxis.set_major_formatter(mtick.FuncFormatter(lambda v, _: f"${v:,.0f}K/hr"))
    ax1.set_xlim(0, 1950)
    ax1.set_xlabel("Predicted Peak Net Laundered Income (Leonida$ Thousands / Hour)", fontsize=10.5)
    ax1.set_title("State of Leonida Regional Economy Forecast: Yield After Laundering Haircut & Alpha Score",
                  fontsize=12.8, fontweight="bold", pad=14)
    for bar, (_, r) in zip(bars, df_reg.iterrows()):
        net_k = r["Net_Clean_Banked_Per_Hr"] / 1e3
        alpha = r["Exploit_Alpha_Score_0_100"]
        ax1.text(net_k + 22, bar.get_y() + bar.get_height() / 2,
                 f"${net_k:,.0f}K/hr  |  Alpha Score: {alpha}/100", va="center", fontsize=8.8, fontweight="bold", color=TEXT_MAIN)
    ax1.grid(True, axis="x", linestyle="--", alpha=0.38)
    fig.tight_layout()
    p2 = CHART_DIR / "02_leonida_6_regions_economic_matrix.png"
    fig.savefig(p2)
    plt.close(fig)
    paths.append(p2)

    # Chart 3: 96-Hour Launch Weekend Shock — DoorDash Surge (%) & US Absent Workers (Millions)
    df_h = datasets["03_nov19_hourly_doordash_and_labor_curve"]
    fig, ax1 = plt.subplots(figsize=(11.5, 5.9), dpi=180)
    ax2 = ax1.twinx()
    xh = np.arange(len(df_h))

    ax1.bar(xh - 0.17, df_h["DoorDash_Order_Surge_Pct"], width=0.34, color=KALSHI_GREEN, alpha=0.88,
            label="DoorDash (DASH) Order Volume Surge vs. Normal Baseline (%)")
    ax2.plot(xh + 0.17, df_h["US_Absent_Workers_Millions"], color=CORAL_RED, marker="o", linewidth=2.8,
             label="U.S. Full-Time Workers Out on 'GTA Flu' / PTO (Millions)")

    ax1.set_xticks(xh)
    ax1.set_xticklabels(df_h["Window_EST"], rotation=24, ha="right", fontsize=8.8)
    ax1.yaxis.set_major_formatter(mtick.FuncFormatter(lambda v, _: f"+{v:.0f}%"))
    ax2.yaxis.set_major_formatter(mtick.FuncFormatter(lambda v, _: f"{v:.1f}M"))
    ax1.set_ylim(0, 54)
    ax2.set_ylim(0, 3.0)
    ax1.set_ylabel("DoorDash Late-Night / Daytime Surge (%)", color=KALSHI_GREEN, fontsize=10.5)
    ax2.set_ylabel("Absent U.S. Full-Time Workers (Millions)", color=CORAL_RED, fontsize=10.5)
    ax1.set_title("96-Hour Launch Shock (Nov 19–22, 2026): DoorDash Volume Surge & The Friday PTO Bridge",
                  fontsize=12.8, fontweight="bold", pad=14)
    ax1.grid(True, axis="y", linestyle="--", alpha=0.35)

    l1, lb1 = ax1.get_legend_handles_labels()
    l2, lb2 = ax2.get_legend_handles_labels()
    ax1.legend(l1 + l2, lb1 + lb2, loc="upper right", frameon=True, facecolor=BG_DARK, edgecolor=GRID_COL, fontsize=9)
    fig.tight_layout()
    p3 = CHART_DIR / "03_nov19_hourly_doordash_and_absenteeism_shock.png"
    fig.savefig(p3)
    plt.close(fig)
    paths.append(p3)

    # Chart 4: 15 Kalshi GTA VI Event Contracts Alpha Map
    df_k = datasets["04_kalshi_gta6_15_contracts_pricing"].iloc[::-1]
    fig, ax = plt.subplots(figsize=(11.8, 7.4), dpi=180)
    yk = np.arange(len(df_k))

    for i, (_, r) in enumerate(df_k.iterrows()):
        m_p = r["Retail_Consensus_Yes"] * 100
        f_p = r["Kalshi_Desk_Fair_Yes"] * 100
        col = KALSHI_GREEN if f_p > m_p else CORAL_RED
        ax.plot([m_p, f_p], [i, i], color=col, linewidth=2.8, alpha=0.88)

    ax.scatter(df_k["Retail_Consensus_Yes"] * 100, yk, color=AMBER_WARN, s=72, zorder=4,
               label="Retail Consensus Price (¢)")
    ax.scatter(df_k["Kalshi_Desk_Fair_Yes"] * 100, yk, color=KALSHI_GREEN, s=88, zorder=5,
               label="Kalshi Desk Quant Fair Value (¢)")

    ax.set_yticks(yk)
    ax.set_yticklabels([f"{t}  |  {q[:38]}..." for t, q in zip(df_k["Ticker"], df_k["Contract_Question"])], fontsize=8.4)
    ax.xaxis.set_major_formatter(mtick.FuncFormatter(lambda v, _: f"{v:.0f}¢"))
    ax.set_xlim(14, 95)
    ax.set_xlabel("Implied Probability / Contract Price (1¢ – 99¢)", fontsize=10.5)
    ax.set_title("Kalshi GTA VI Master Market Book: 15 Resolvable Contracts & Pricing Alpha",
                 fontsize=13, fontweight="bold", pad=14)
    ax.legend(loc="upper left", frameon=True, facecolor=BG_DARK, edgecolor=GRID_COL, fontsize=8.8)
    ax.grid(True, axis="x", linestyle="--", alpha=0.4)
    fig.tight_layout()
    p4 = CHART_DIR / "04_kalshi_gta6_15_contracts_alpha_map.png"
    fig.savefig(p4)
    plt.close(fig)
    paths.append(p4)

    return paths


if __name__ == "__main__":
    ds = build_gta6_datasets()
    xlsx = build_gta6_excel(ds)
    charts = generate_gta6_charts(ds)
    print(f"Generated {len(ds)} GTA 6 CSV files in {DATA_DIR}")
    print(f"Generated GTA 6 Excel model: {xlsx}")
    print(f"Generated {len(charts)} GTA 6 charts in {CHART_DIR}")
