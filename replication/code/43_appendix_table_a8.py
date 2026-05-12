"""Reproduce Appendix Table A8 — Labor Market Conditions during the Pandemic by State.

For school years 2019-20 to 2023-24, compute state-level:
  - Turnover mean, median (across counties)
  - Leaver total
  - NNJF mean (per 100), median (per 100), total

Comparison table to paper Table A8.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from _config import DATA_DERIVED, OUTPUT, stata_aweight_sum, stata_aweight_mean, stata_aweight_quantile


# Paper Table A8 values: state -> (t_mean, t_median, leaver_total, nnjf_mean, nnjf_med, nnjf_total)
# Using values from the paper's Table A8 (some states missing entries; using paper's exact values)
PAPER_A8 = {
    "01": (20.1, 20.4, 34549, 12.1, 8.6, 55383),    # Alabama
    "02": (np.nan, np.nan, np.nan, np.nan, np.nan, np.nan),  # Alaska
    "04": (28.2, 28.1, 35542, 12.0, 10.9, 94244),   # Arizona
    "05": (19.4, 19.3, 35252, 11.7, 10.8, 38844),   # Arkansas
    "06": (26.3, 27.3, 105060, 10.6, 10.1, 359376), # California
    "08": (31.5, 31.7, 22907, 18.1, 11.5, 115510),  # Colorado
    "09": (np.nan, np.nan, np.nan, 14.6, 11.3, 76469),  # Connecticut
    "10": (19.8, 14.8, 15391, 7.3, 6.9, 7353),      # Delaware
    "11": (32.3, 28.9, 32676, 7.3, 7.0, 9468),      # DC
    "12": (22.6, 22.7, 76793, 10.8, 7.4, 175688),   # Florida
    "13": (19.2, 18.8, 60035, 20.5, 8.0, 142147),   # Georgia
    "15": (17.0, 18.1, 26700, 8.5, 6.6, 15055),     # Hawaii
    "16": (31.3, 31.1, 10611, 11.9, 11.7, 28445),   # Idaho
    "17": (26.2, 26.4, 73084, 10.4, 9.4, 198485),   # Illinois
    "18": (28.5, 28.5, 94581, 9.1, 8.5, 74340),     # Indiana
    "19": (24.3, 24.3, 53847, 12.4, 12.3, 56426),   # Iowa
    "20": (29.6, 30.0, 35803, 13.9, 13.4, 45289),   # Kansas
    "21": (23.6, 23.3, 27295, 9.8, 9.4, 26376),     # Kentucky
    "22": (24.6, 23.0, 39841, 16.5, 8.6, 37911),    # Louisiana
    "23": (27.4, 28.3, 34227, 11.3, 9.7, 24784),    # Maine
    "24": (18.0, 19.0, 33188, 15.8, 7.3, 87874),    # Maryland
    "25": (24.8, 26.0, 100703, 8.1, 7.6, 90453),    # Massachusetts
    "26": (18.3, 16.8, 20592, 12.4, 9.7, 47009),    # Michigan
    "27": (28.6, 29.2, 63185, 14.9, 14.0, 129886),  # Minnesota
    "28": (21.5, 21.3, 32693, 12.2, 10.1, 42981),   # Mississippi
    "29": (25.0, 24.7, 63334, 15.3, 13.8, 93798),   # Missouri
    "30": (32.0, 33.0, 18647, 16.8, 16.6, 21135),   # Montana
    "31": (23.8, 24.5, 17036, 12.2, 11.2, 29055),   # Nebraska
    "32": (19.5, 19.5, 1478, 8.4, 7.6, 16162),      # Nevada
    "33": (27.2, 26.4, 34428, 12.7, 10.5, 26310),   # New Hampshire
    "34": (20.5, 21.0, 160130, 8.6, 7.7, 120344),   # New Jersey
    "35": (24.8, 26.7, 23539, 13.2, 9.7, 28501),    # New Mexico
    "36": (23.7, 23.6, 123725, 9.1, 7.5, 204545),   # New York
    "37": (20.4, 20.6, 50673, 10.7, 9.9, 98322),    # North Carolina
    "38": (27.3, 27.4, 12167, 13.9, 12.7, 14735),   # North Dakota
    "39": (23.2, 23.6, 129832, 9.0, 7.9, 127232),   # Ohio
    "40": (25.2, 25.9, 43021, 13.3, 12.6, 64197),   # Oklahoma
    "41": (28.5, 29.4, 20498, 15.0, 13.1, 54998),   # Oregon
    "42": (18.4, 18.9, 144225, 7.5, 6.7, 113762),   # Pennsylvania
    "44": (25.4, 23.7, 17756, 10.1, 8.2, 14022),    # Rhode Island
    "45": (22.0, 21.8, 28214, 10.9, 8.7, 61815),    # South Carolina
    "46": (28.5, 28.1, 13139, 12.2, 11.9, 12495),   # South Dakota
    "47": (23.4, 21.4, 45296, 8.6, 7.9, 63857),     # Tennessee
    "48": (27.4, 27.4, 145061, 11.4, 11.1, 469169), # Texas
    "49": (27.4, 27.4, 11135, 11.4, 10.1, 45972),   # Utah
    "50": (33.6, 37.0, 13040, 16.7, 13.9, 20669),   # Vermont
    "51": (24.9, 24.4, 72011, 15.0, 8.3, 121773),   # Virginia
    "53": (27.8, 29.5, 30815, 10.7, 9.9, 84324),    # Washington
    "54": (15.6, 15.2, 14661, 9.8, 7.5, 19485),     # West Virginia
    "55": (24.1, 24.1, 49799, 11.8, 10.5, 80384),   # Wisconsin
    "56": (21.0, 21.4, 8376, 11.7, 10.5, 7427),     # Wyoming
}

STATE_NAMES = {
    "01": "Alabama", "02": "Alaska", "04": "Arizona", "05": "Arkansas", "06": "California",
    "08": "Colorado", "09": "Connecticut", "10": "Delaware", "11": "DC", "12": "Florida",
    "13": "Georgia", "15": "Hawaii", "16": "Idaho", "17": "Illinois", "18": "Indiana",
    "19": "Iowa", "20": "Kansas", "21": "Kentucky", "22": "Louisiana", "23": "Maine",
    "24": "Maryland", "25": "Massachusetts", "26": "Michigan", "27": "Minnesota", "28": "Mississippi",
    "29": "Missouri", "30": "Montana", "31": "Nebraska", "32": "Nevada", "33": "New Hampshire",
    "34": "New Jersey", "35": "New Mexico", "36": "New York", "37": "North Carolina", "38": "North Dakota",
    "39": "Ohio", "40": "Oklahoma", "41": "Oregon", "42": "Pennsylvania", "44": "Rhode Island",
    "45": "South Carolina", "46": "South Dakota", "47": "Tennessee", "48": "Texas", "49": "Utah",
    "50": "Vermont", "51": "Virginia", "53": "Washington", "54": "West Virginia", "55": "Wisconsin",
    "56": "Wyoming",
}


def main() -> None:
    sy = pd.read_parquet(DATA_DERIVED / "county_school_year_measures.parquet")
    sy["state"] = sy["fips"].str[:2]
    sy = sy[(sy["school_year"] >= 2020) & (sy["school_year"] <= 2024)].copy()
    sy["turnover"] = pd.to_numeric(sy["turnover"], errors="coerce")
    sy["nnjf"] = pd.to_numeric(sy["nnjf"], errors="coerce")
    # v2: Table A8 uses NNJF / (Emp_Q3 / 100) per authors' Stata code (line 1394).
    # The 'nnjf_per_100_q3' column was added in 10_construct_measures.py for this purpose.
    if "nnjf_per_100_q3" in sy.columns:
        sy["nnjf_per_100"] = pd.to_numeric(sy["nnjf_per_100_q3"], errors="coerce")
    else:
        sy["nnjf_per_100"] = pd.to_numeric(sy["nnjf_per_100"], errors="coerce")
    sy["leavers"] = pd.to_numeric(sy["leavers"], errors="coerce")

    # State-level summaries (across counties × pandemic years 2020-2024)
    # All weighted statistics use 1/emp_lag as proxy for paper's 1/FTE_ELSI.
    sy["w"] = 1.0 / sy["emp_lag"].astype(float).replace(0, np.nan)
    rows = []
    for st, name in STATE_NAMES.items():
        sub = sy[sy["state"] == st]
        if sub.empty:
            rows.append((st, name, *([np.nan]*6)))
            continue
        # Turnover stats: weighted mean and median
        t_vals = sub["turnover"].values
        t_w = sub["w"].values
        t_mean = stata_aweight_mean(t_vals, t_w) * 100
        t_med = stata_aweight_quantile(t_vals, t_w, 0.5) * 100
        # Leaver Total: Stata-style aweight sum (authors' Stata line 1384)
        leaver_total = stata_aweight_sum(sub["leavers"].values, sub["w"].values)
        # NNJF stats: weighted mean/median of per-100, SIMPLE sum of count
        # (Authors' Stata line 1398 uses `collapse (sum) job_destruct_sum` WITHOUT aweight,
        #  even though Leaver Total in the same table uses aweight. Asymmetric within Table A8.)
        nnjf_p100 = sub["nnjf_per_100"].values
        nnjf_w = sub["w"].values
        nnjf_mean = stata_aweight_mean(nnjf_p100, nnjf_w)
        nnjf_med = stata_aweight_quantile(nnjf_p100, nnjf_w, 0.5)
        nnjf_total = float(np.nansum(sub["nnjf"].values))
        rows.append((st, name, t_mean, t_med, leaver_total, nnjf_mean, nnjf_med, nnjf_total))

    # Build markdown table
    md = ["# Appendix Table A8 — Pandemic-era Labor Market by State (2019-20 to 2023-24)",
          "",
          "Each cell: my value | paper value.",
          "",
          "| State | Turnover Mean (%) | Turnover Median (%) | Leaver Total | NNJF Mean (per 100) | NNJF Median (per 100) | NNJF Total |",
          "|-------|---|---|---|---|---|---|"]
    n_match = {"t_mean": 0, "t_med": 0, "leaver": 0, "nnjf_total": 0}
    n_states = 0
    for r in rows:
        st, name, t_mean, t_med, leaver, nm, nmd, nt = r
        p = PAPER_A8.get(st, (np.nan,)*6)
        n_states += 1
        # Check match (within 2pp for percentages, within 25% for totals)
        if not np.isnan(t_mean) and not np.isnan(p[0]) and abs(t_mean - p[0]) < 2:
            n_match["t_mean"] += 1
        if not np.isnan(t_med) and not np.isnan(p[1]) and abs(t_med - p[1]) < 2:
            n_match["t_med"] += 1
        if not np.isnan(leaver) and not np.isnan(p[2]) and abs(leaver / p[2] - 1) < 0.25:
            n_match["leaver"] += 1
        if not np.isnan(nt) and not np.isnan(p[5]) and abs(nt / p[5] - 1) < 0.50:
            n_match["nnjf_total"] += 1
        md.append(f"| {name} | "
                  f"{f'{t_mean:.1f}' if not np.isnan(t_mean) else '—'} / **{f'{p[0]:.1f}' if not np.isnan(p[0]) else '—'}** | "
                  f"{f'{t_med:.1f}' if not np.isnan(t_med) else '—'} / **{f'{p[1]:.1f}' if not np.isnan(p[1]) else '—'}** | "
                  f"{f'{leaver:,.0f}' if not np.isnan(leaver) else '—'} / **{f'{p[2]:,.0f}' if not np.isnan(p[2]) else '—'}** | "
                  f"{f'{nm:.1f}' if not np.isnan(nm) else '—'} / **{f'{p[3]:.1f}' if not np.isnan(p[3]) else '—'}** | "
                  f"{f'{nmd:.1f}' if not np.isnan(nmd) else '—'} / **{f'{p[4]:.1f}' if not np.isnan(p[4]) else '—'}** | "
                  f"{f'{nt:,.0f}' if not np.isnan(nt) else '—'} / **{f'{p[5]:,.0f}' if not np.isnan(p[5]) else '—'}** |")

    md += ["",
           "## Match summary",
           f"- States with turnover MEAN within 2 pp of paper: {n_match['t_mean']}/{n_states}",
           f"- States with turnover MEDIAN within 2 pp of paper: {n_match['t_med']}/{n_states}",
           f"- States with leaver TOTAL within 25% of paper: {n_match['leaver']}/{n_states}",
           f"- States with NNJF TOTAL within 50% of paper: {n_match['nnjf_total']}/{n_states}",
           ""]

    (OUTPUT / "tables" / "appendix_table_A8_my.md").write_text("\n".join(md))
    print(f"Wrote A8.")
    print(f"Match rate (within 2pp): turnover mean {n_match['t_mean']}/{n_states}, median {n_match['t_med']}/{n_states}")
    print(f"Match rate: leaver total within 25% = {n_match['leaver']}/{n_states}, NNJF total within 50% = {n_match['nnjf_total']}/{n_states}")


if __name__ == "__main__":
    main()
