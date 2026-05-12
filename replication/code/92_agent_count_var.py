"""Test alternative QWI count variables for the NNJF numerator.

Existing tested variants (NOT retested here):
  - EmpTotal abs(diff) summed                  -> 5-8x too big
  - FrmJbLsS avg over 4 SY quarters (current)  -> 1.0-1.3x (rate still 2.3x off)
  - FrmJbLs avg over 4 SY quarters             -> 1.0-1.5x
  - FrmJbC abs(net change)                     -> 2-4x

This script pulls additional QWI variables (Sep, SepBeg, SepS, HirA, HirAEnd,
HirAEndRepl, FrmJbGn, FrmJbC) and constructs 5 NEW hypotheses for the NNJF
numerator, plus a bonus 6th:

  H1  Sep          avg over 4 SY quarters
  H2  SepBeg       avg over 4 SY quarters (beginning-of-quarter separations)
  H3  SepS         avg over 4 SY quarters (stable separations only)
  H4  max(Sep - HirA, 0)   AVG over 4 SY quarters  (net job-loss flow)
  H5  max(FrmJbLsS - FrmJbGnS, 0)  AVG over 4 SY quarters  (net STABLE flow)
  H6  HirAEndRepl  avg over 4 SY quarters (bonus: replacement hires)

For each, report school-year-total NNJF (in thousands) for SYs 2019, 2020, 2021,
2023, and the pooled weighted (1/emp_lag) median NNJF count.
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from _config import QWI_CURRENT_DIR
from _qwi_client import US_STATE_FIPS, pull_state_chunked_by_years


# ------------------- 1. Data: pull or load the additional QWI vars -----------

EXTRA_VARS = ("Sep", "SepBeg", "SepS", "HirA", "HirAEnd", "HirAEndRepl",
              "FrmJbGn", "FrmJbC")
EXTRA_PATH = QWI_CURRENT_DIR / "county_sex0_alt_count_vars.parquet"


def pull_extra() -> pd.DataFrame:
    if EXTRA_PATH.exists():
        df = pd.read_parquet(EXTRA_PATH)
        print(f"Loaded cached extra-vars file: {EXTRA_PATH.name}  shape={df.shape}")
        return df
    print(f"Pulling extra QWI vars for {len(US_STATE_FIPS)} states ...")
    chunks: list[pd.DataFrame] = []
    t0 = time.time()
    for i, st in enumerate(US_STATE_FIPS, 1):
        df = pull_state_chunked_by_years(
            endpoint="sa",
            state_fips=st,
            get_vars=EXTRA_VARS,
            extra_params={"sex": "0"},
            start_year=2000,
            end_quarter="2025-Q2",
            chunk_years=4,
        )
        chunks.append(df)
        if i % 5 == 0:
            print(f"  [{i:2d}/51] elapsed={time.time()-t0:.1f}s")
    combined = pd.concat(chunks, ignore_index=True)
    for col in EXTRA_VARS:
        if col in combined.columns:
            combined[col] = pd.to_numeric(combined[col], errors="coerce")
    combined["year"] = combined["time"].str.split("-Q").str[0].astype(int)
    combined["quarter"] = combined["time"].str.split("-Q").str[1].astype(int)
    combined["fips"] = combined["state"].astype(str) + combined["county"].astype(str)
    keep = ["fips", "state", "county", "year", "quarter", "time"] + list(EXTRA_VARS)
    combined = combined[[c for c in keep if c in combined.columns]]
    combined.to_parquet(EXTRA_PATH, index=False)
    print(f"Wrote {len(combined):,} rows to {EXTRA_PATH}")
    return combined


# ------------------- 2. Build wide quarterly panel ---------------------------

PIVOT_COLS = ("EmpTotal", "FrmJbLs",
              "Sep", "SepBeg", "SepS", "HirA", "HirAEnd", "HirAEndRepl",
              "FrmJbGn", "FrmJbC",
              "FrmJbLsS", "FrmJbGnS", "EmpS", "EmpEnd")


def build_wide(df_main: pd.DataFrame, df_extra: pd.DataFrame,
               df_stab: pd.DataFrame) -> pd.DataFrame:
    """One row per (fips, year); columns like sep_q1..q4, hira_q1..q4, frmjblss_q1..q4 etc."""
    m = df_main[["fips", "year", "quarter", "EmpTotal", "FrmJbLs"]].merge(
        df_extra[["fips", "year", "quarter", *EXTRA_VARS]],
        on=["fips", "year", "quarter"], how="outer").merge(
        df_stab[["fips", "year", "quarter", "FrmJbLsS", "FrmJbGnS", "EmpS", "EmpEnd"]],
        on=["fips", "year", "quarter"], how="outer")
    pivots = []
    for c in PIVOT_COLS:
        if c not in m.columns:
            continue
        p = m.pivot_table(index=["fips", "year"], columns="quarter",
                          values=c, aggfunc="first")
        p.columns = [f"{c.lower()}_q{int(q)}" for q in p.columns]
        pivots.append(p)
    out = pd.concat(pivots, axis=1).reset_index()
    return out


def add_lags(wide: pd.DataFrame) -> pd.DataFrame:
    wide = wide.sort_values(["fips", "year"]).reset_index(drop=True)
    lag_targets = []
    for c in PIVOT_COLS:
        for q in (3, 4):
            col = f"{c.lower()}_q{q}"
            if col in wide.columns:
                lag_targets.append(col)
    prev = wide[["fips", "year"] + lag_targets].copy()
    rename = {"year": "prev_year"}
    for c in lag_targets:
        rename[c] = f"{c}_lag"
    prev = prev.rename(columns=rename)
    wide["prev_year"] = wide["year"] - 1
    merged = wide.merge(prev, on=["fips", "prev_year"], how="left")
    merged["school_year"] = merged["year"]
    for c in merged.columns:
        if any(c.startswith(p.lower() + "_q") for p in PIVOT_COLS):
            merged[c] = pd.to_numeric(merged[c], errors="coerce").astype("float")
    merged["emp_lag"] = pd.to_numeric(merged["emptotal_q4_lag"], errors="coerce").astype(float)
    return merged


# ------------------- 3. Hypotheses -------------------------------------------

QUARTERS = ["q3_lag", "q4_lag", "q1", "q2"]


def sy_avg(d: pd.DataFrame, prefix: str) -> pd.Series:
    return sum(d[f"{prefix}_{q}"] for q in QUARTERS) / 4.0


def sy_sum(d: pd.DataFrame, prefix: str) -> pd.Series:
    return sum(d[f"{prefix}_{q}"] for q in QUARTERS)


def sy_clip_avg(d: pd.DataFrame, minuend: str, subtrahend: str) -> pd.Series:
    return sum((d[f"{minuend}_{q}"] - d[f"{subtrahend}_{q}"]).clip(lower=0)
               for q in QUARTERS) / 4.0


HYPOTHESES = {
    "H1_sep_avg":        lambda d: sy_avg(d, "sep"),
    "H2_sepbeg_avg":     lambda d: sy_avg(d, "sepbeg"),
    "H3_seps_avg":       lambda d: sy_avg(d, "seps"),
    "H4_sep_minus_hira_clip_avg":     lambda d: sy_clip_avg(d, "sep", "hira"),
    "H5_frmjblss_minus_frmjbgns_clip_avg": lambda d: sy_clip_avg(d, "frmjblss", "frmjbgns"),
    "H6_hiraendrepl_avg":             lambda d: sy_avg(d, "hiraendrepl"),
}

HYPOTHESIS_DESC = {
    "H1_sep_avg": "Sep (separations) avg over 4 SY quarters",
    "H2_sepbeg_avg": "SepBeg (BoQ separations) avg over 4 SY quarters",
    "H3_seps_avg": "SepS (stable separations) avg over 4 SY quarters",
    "H4_sep_minus_hira_clip_avg": "max(Sep - HirA, 0) avg over 4 SY quarters",
    "H5_frmjblss_minus_frmjbgns_clip_avg":
        "max(FrmJbLsS - FrmJbGnS, 0) avg over 4 SY quarters (net STABLE firm job-loss flow)",
    "H6_hiraendrepl_avg": "HirAEndRepl (replacement hires) avg over 4 SY quarters",
}


# ------------------- 4. Reporting --------------------------------------------

PAPER_TOTAL = {  # Table A4, in thousands
    2001: 120.6, 2002: 145.1, 2003: 161.8, 2004: 171.1, 2005: 172.5,
    2006: 179.0, 2007: 192.8, 2008: 185.8, 2009: 180.0, 2010: 180.1,
    2011: 198.7, 2012: 188.8, 2013: 181.8, 2014: 185.0, 2015: 182.9,
    2016: 184.7, 2017: 171.4, 2018: 176.3, 2019: 176.2, 2020: 224.9,
    2021: 150.4, 2022: 144.1, 2023: 162.1, 2024: 138.6,
}
PAPER_MEDIAN_COUNT = 43      # Table A2 pooled
PAPER_MEAN_COUNT = 73.3
PAPER_P25_COUNT = 24
PAPER_P75_COUNT = 77
PAPER_MEDIAN_RATE = 1.08
PAPER_MEAN_RATE = 3.32

TARGET_SY = [2019, 2020, 2021, 2023]


def weighted_q(values: np.ndarray, weights: np.ndarray, q: float) -> float:
    mask = ~np.isnan(values) & ~np.isnan(weights) & (weights > 0)
    v = values[mask]; w = weights[mask]
    if len(v) == 0:
        return np.nan
    i = np.argsort(v); cw = np.cumsum(w[i]) / w.sum()
    return float(v[i][np.searchsorted(cw, q)])


def summarize_one(hname: str, hfn, merged: pd.DataFrame) -> dict:
    s = hfn(merged).astype(float)
    sub = merged[(s.notna()) & (merged["emp_lag"] > 0)].copy()
    sub["_val"] = hfn(sub).astype(float)
    # Per-year totals (in thousands)
    yearly = {}
    ratios = []
    for sy in sorted(PAPER_TOTAL):
        t = sub.loc[sub["school_year"] == sy, "_val"].sum() / 1000.0
        yearly[sy] = t
        if PAPER_TOTAL[sy] > 0:
            ratios.append(t / PAPER_TOTAL[sy])
    # Pooled weighted distribution (counts and per-100 rates)
    sub["_rate"] = 100.0 * sub["_val"].values / sub["emp_lag"].values
    wts = 1.0 / sub["emp_lag"].values
    med_count = weighted_q(sub["_val"].values, wts, 0.5)
    p25_count = weighted_q(sub["_val"].values, wts, 0.25)
    p75_count = weighted_q(sub["_val"].values, wts, 0.75)
    med_rate = weighted_q(sub["_rate"].values, wts, 0.5)
    # Pooled weighted mean
    mask = ~np.isnan(sub["_val"].values) & (wts > 0)
    wmean_count = float(np.average(sub["_val"].values[mask], weights=wts[mask]))
    wmean_rate  = float(np.average(sub["_rate"].values[mask], weights=wts[mask]))
    return {
        "hypothesis": hname,
        "desc": HYPOTHESIS_DESC[hname],
        "yearly_totals_thousands": yearly,
        "sy2019": round(yearly[2019], 1),
        "sy2020": round(yearly[2020], 1),
        "sy2021": round(yearly[2021], 1),
        "sy2023": round(yearly[2023], 1),
        "mean_ratio_yrs": round(float(np.mean(ratios)), 3),
        "median_ratio_yrs": round(float(np.median(ratios)), 3),
        "pooled_wmedian_count": round(med_count, 2),
        "pooled_wp25_count": round(p25_count, 2),
        "pooled_wp75_count": round(p75_count, 2),
        "pooled_wmean_count": round(wmean_count, 2),
        "pooled_wmedian_rate": round(med_rate, 3),
        "pooled_wmean_rate": round(wmean_rate, 3),
    }


def main() -> None:
    df_main = pd.read_parquet(QWI_CURRENT_DIR / "county_sex0_full_2025q2.parquet")
    for c in ("EmpTotal", "HirN", "FrmJbLs", "Emp"):
        if c in df_main.columns:
            df_main[c] = pd.to_numeric(df_main[c], errors="coerce")
    print(f"Main panel: {df_main.shape}")

    df_stab = pd.read_parquet(QWI_CURRENT_DIR / "county_sex0_frmjblss.parquet")
    for c in ("FrmJbLsS", "FrmJbGnS", "EmpS", "EmpEnd"):
        if c in df_stab.columns:
            df_stab[c] = pd.to_numeric(df_stab[c], errors="coerce")
    print(f"Stable panel: {df_stab.shape}")

    df_extra = pull_extra()

    wide = build_wide(df_main, df_extra, df_stab)
    print(f"Wide panel: {wide.shape}")

    merged = add_lags(wide)
    merged = merged[(merged["school_year"] >= 2001) & (merged["school_year"] <= 2024)]
    print(f"With lags: {merged.shape}\n")

    results = []
    for hname, hfn in HYPOTHESES.items():
        r = summarize_one(hname, hfn, merged)
        results.append(r)

    summary_df = pd.DataFrame([
        {k: v for k, v in r.items() if k != "yearly_totals_thousands"}
        for r in results
    ])
    # Add paper reference row
    paper_row = {
        "hypothesis": "PAPER", "desc": "Paper-reported targets",
        "sy2019": PAPER_TOTAL[2019], "sy2020": PAPER_TOTAL[2020],
        "sy2021": PAPER_TOTAL[2021], "sy2023": PAPER_TOTAL[2023],
        "mean_ratio_yrs": 1.0, "median_ratio_yrs": 1.0,
        "pooled_wmedian_count": PAPER_MEDIAN_COUNT,
        "pooled_wp25_count": PAPER_P25_COUNT,
        "pooled_wp75_count": PAPER_P75_COUNT,
        "pooled_wmean_count": PAPER_MEAN_COUNT,
        "pooled_wmedian_rate": PAPER_MEDIAN_RATE,
        "pooled_wmean_rate": PAPER_MEAN_RATE,
    }
    summary_df = pd.concat([summary_df, pd.DataFrame([paper_row])], ignore_index=True)
    out_csv = (Path(__file__).resolve().parents[1] / "output" / "reports"
               / "agent_count_var_summary.csv")
    summary_df.to_csv(out_csv, index=False)

    # Per-year totals table for each hypothesis
    year_rows = []
    for r in results:
        row = {"hypothesis": r["hypothesis"]}
        for sy in sorted(PAPER_TOTAL):
            row[f"sy{sy}"] = round(r["yearly_totals_thousands"][sy], 1)
        year_rows.append(row)
    # paper line
    paper_yr = {"hypothesis": "PAPER"}
    for sy in sorted(PAPER_TOTAL):
        paper_yr[f"sy{sy}"] = PAPER_TOTAL[sy]
    year_rows.append(paper_yr)
    yearly_df = pd.DataFrame(year_rows)
    yearly_df.to_csv(out_csv.with_name("agent_count_var_yearly.csv"), index=False)

    # Print tidy report
    print("="*100)
    print("HYPOTHESIS TOTALS (thousands) FOR TARGET SCHOOL YEARS")
    print("="*100)
    cols = ["hypothesis", "sy2019", "sy2020", "sy2021", "sy2023",
            "mean_ratio_yrs", "median_ratio_yrs"]
    print(summary_df[cols].to_string(index=False))
    print()
    print("="*100)
    print("HYPOTHESIS POOLED DISTRIBUTION (weighted by 1/emp_lag)")
    print("="*100)
    dist_cols = ["hypothesis", "pooled_wp25_count", "pooled_wmedian_count",
                 "pooled_wp75_count", "pooled_wmean_count",
                 "pooled_wmedian_rate", "pooled_wmean_rate"]
    print(summary_df[dist_cols].to_string(index=False))
    print()
    print("="*100)
    print("FULL YEARLY TOTALS (thousands) FOR ALL 2001-2024")
    print("="*100)
    print(yearly_df.to_string(index=False))

    # Closeness ranking: smaller |mean_ratio - 1| is better for totals
    print("\n" + "="*100)
    print("RANKING")
    print("="*100)
    scored = summary_df[summary_df["hypothesis"] != "PAPER"].copy()
    scored["score_total"] = (scored["mean_ratio_yrs"] - 1).abs()
    scored["score_median"] = (scored["pooled_wmedian_count"] -
                              PAPER_MEDIAN_COUNT).abs() / PAPER_MEDIAN_COUNT
    print("\nBy closeness to paper TOTAL (lower |mean_ratio - 1| is better):")
    print(scored.sort_values("score_total")[["hypothesis", "mean_ratio_yrs",
                                              "score_total"]].to_string(index=False))
    print("\nBy closeness to paper MEDIAN count (lower is better):")
    print(scored.sort_values("score_median")[["hypothesis", "pooled_wmedian_count",
                                               "score_median"]].to_string(index=False))


if __name__ == "__main__":
    main()
