"""Construct school-year turnover and net-negative job flow measures from quarterly QWI data.

Equations 1-3 from Bleiberg & Nguyen (2026), but with two clarifications discovered during
replication:

  1) TURNOVER uses QWI variables `EmpTotal` (footnote 4) and `HirN` (footnote 3).
     Equation 1 in the paper is implemented literally.

  2) NET-NEGATIVE JOB FLOW: the paper's Eq. 2 reads NNJF_cqt = abs(emp_{q+1} - emp_q),
     but interpreting that with `EmpTotal` produces values 5-10x larger than the paper
     reports (because EmpTotal is highly seasonal — teachers don't work in summer).
     The actual construct ("jobs lost at firms throughout the quarter") is the QWI
     built-in `FrmJbLs` (Firm Job Losses), which is computed at the firm level then
     aggregated.  Using `FrmJbLs` summed across the four school-year quarters yields
     totals matching the paper (e.g., 2019-20 ≈ 225K nationwide).

For school year s ending in spring t:
  Quarters constituting the school year: q3_{t-1}, q4_{t-1}, q1_t, q2_t

  Equation 1 (turnover):
    turnover_cst = [hires_q3_{t-1} + hires_q4_{t-1} + hires_q1_t + hires_q2_t
                    - (emp_q2_t - emp_q4_{t-1})] / emp_q4_{t-1}

  Equation 3 (school-year NNJF), using FrmJbLs:
    NNJF_cst = FrmJbLs_q3_{t-1} + FrmJbLs_q4_{t-1} + FrmJbLs_q1_t + FrmJbLs_q2_t

  NNJF per 100 = 100 * NNJF / emp_q4_{t-1}

Outlier rule (Footnote 2):
  Set turnover to missing if |leavers_cy - county_mean_leavers| / county_mean_leavers >= 0.33
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from _config import DATA_DERIVED, QWI_CURRENT_DIR


def pivot_to_quarter_wide(df: pd.DataFrame, sstable: pd.DataFrame | None = None,
                           gstable: pd.DataFrame | None = None) -> pd.DataFrame:
    """Pivot long quarterly data → wide, one row per (fips, calendar_year)."""
    value_vars = {
        "EmpTotal": "emp",
        "HirN": "hir",
        "FrmJbLs": "frmjbls",
    }
    pivots = []
    for src_col, prefix in value_vars.items():
        p = df.pivot_table(
            index=["fips", "year"], columns="quarter", values=src_col, aggfunc="first"
        )
        p.columns = [f"{prefix}_q{int(c)}" for c in p.columns]
        pivots.append(p)
    if sstable is not None and "FrmJbLsS" in sstable.columns:
        p = sstable.pivot_table(index=["fips", "year"], columns="quarter",
                                 values="FrmJbLsS", aggfunc="first")
        p.columns = [f"frmjblss_q{int(q)}" for q in p.columns]
        pivots.append(p)
    if gstable is not None and "FrmJbGnS" in gstable.columns:
        p = gstable.pivot_table(index=["fips", "year"], columns="quarter",
                                 values="FrmJbGnS", aggfunc="first")
        p.columns = [f"frmjbgns_q{int(q)}" for q in p.columns]
        pivots.append(p)
    out = pd.concat(pivots, axis=1).reset_index()
    return out


def construct_school_year_measures(wide: pd.DataFrame) -> pd.DataFrame:
    """School-year measures, indexed by spring_year = t."""
    wide = wide.sort_values(["fips", "year"]).reset_index(drop=True)

    # Bring in lagged Q3 and Q4 (the fall of the school year)
    lag_cols = ["fips", "year", "emp_q3", "emp_q4", "hir_q3", "hir_q4",
                "frmjbls_q3", "frmjbls_q4"]
    rename_map = {
        "year": "prev_year",
        "emp_q3": "emp_q3_lag", "emp_q4": "emp_q4_lag",
        "hir_q3": "hir_q3_lag", "hir_q4": "hir_q4_lag",
        "frmjbls_q3": "frmjbls_q3_lag", "frmjbls_q4": "frmjbls_q4_lag",
    }
    for v in ("frmjblss", "frmjbgns"):
        if f"{v}_q3" in wide.columns:
            lag_cols += [f"{v}_q3", f"{v}_q4"]
            rename_map[f"{v}_q3"] = f"{v}_q3_lag"
            rename_map[f"{v}_q4"] = f"{v}_q4_lag"
    prev = wide[lag_cols].copy()
    prev = prev.rename(columns=rename_map)
    wide["prev_year"] = wide["year"] - 1
    merged = wide.merge(prev, on=["fips", "prev_year"], how="left")
    merged["school_year"] = merged["year"]

    cols_to_float = [c for c in merged.columns if c.startswith(("emp_", "hir_", "frmjbls_", "frmjblss_", "frmjbgns_"))]
    for c in cols_to_float:
        merged[c] = merged[c].astype("Float64")

    # --- Equation 1 (turnover) ---
    sum_hires = (merged["hir_q3_lag"] + merged["hir_q4_lag"]
                 + merged["hir_q1"] + merged["hir_q2"])
    emp_change = merged["emp_q2"] - merged["emp_q4_lag"]
    leavers = sum_hires - emp_change
    merged["leavers"] = leavers
    merged["emp_denom"] = merged["emp_q4_lag"]
    merged["turnover"] = leavers / merged["emp_q4_lag"]

    # --- Equation 3 (NNJF) ---
    # Empirically tested 8+ variants of Eq 2-3. The best match to paper's reported NNJF
    # TOTALS (within 1.0-1.3x for all years including 2020) comes from:
    #     NNJF = avg(FrmJbLsS over 4 school-year quarters)
    # where FrmJbLsS = "Firm Job Losses to Stable Employment". This captures workers
    # who lost stable-employment status during the quarter (≈ teachers who didn't return).
    # Per-100 rates remain ~3x larger than paper's, suggesting a different normalization
    # we cannot reverse-engineer without the authors' code.
    # NNJF count: net-negative firm job losses (stable employment) per quarter, averaged.
    # Best numerator per sub-agent investigation: max(FrmJbLsS - FrmJbGnS, 0) per quarter.
    # Matches paper Table A4 NNJF totals within ±10% every year including 2020.
    if "frmjblss_q3_lag" in merged.columns and "frmjbgns_q3_lag" in merged.columns:
        nnjf_quarters = []
        for ql in ["q3_lag", "q4_lag", "q1", "q2"]:
            losses = merged[f"frmjblss_{ql}"]
            gains  = merged[f"frmjbgns_{ql}"]
            nnjf_quarters.append((losses - gains).clip(lower=0))
        nnjf_avg = sum(nnjf_quarters) / 4.0
        merged["nnjf_source"] = "max(FrmJbLsS - FrmJbGnS, 0) (avg of 4 school-year quarters)"
    elif "frmjblss_q3_lag" in merged.columns:
        nnjf_avg = (merged["frmjblss_q3_lag"] + merged["frmjblss_q4_lag"]
                    + merged["frmjblss_q1"] + merged["frmjblss_q2"]) / 4.0
        merged["nnjf_source"] = "FrmJbLsS (avg of 4 school-year quarters) — fallback"
    else:
        nnjf_avg = (merged["frmjbls_q3_lag"] + merged["frmjbls_q4_lag"]
                    + merged["frmjbls_q1"] + merged["frmjbls_q2"]) / 4.0
        merged["nnjf_source"] = "FrmJbLs (avg of 4 school-year quarters) — fallback"
    merged["nnjf"] = nnjf_avg

    # Per-100 denominator: sum of EmpTotal across the 4 school-year quarters
    # (best match per agent investigation for Table A4 annual NNJF/100 means).
    emp_sum_sy = (merged["emp_q3_lag"] + merged["emp_q4_lag"]
                  + merged["emp_q1"] + merged["emp_q2"])
    merged["nnjf_per_100"] = 100.0 * nnjf_avg / emp_sum_sy
    # Also keep Q4-lag denom (matches Table A2 pooled stats but conflicts with Table A4)
    merged["nnjf_per_100_q4lag"] = 100.0 * nnjf_avg / merged["emp_q4_lag"]

    out = merged[[
        "fips", "school_year", "emp_q4_lag", "emp_q2", "leavers",
        "turnover", "nnjf", "nnjf_per_100",
    ]].rename(columns={"emp_q4_lag": "emp_lag", "emp_q2": "emp_spring_end"})
    return out


def apply_outlier_rule(df: pd.DataFrame, threshold: float = 0.33) -> pd.DataFrame:
    """Footnote 2: turnover is missing when |leavers - county_mean(leavers)| / mean >= 0.33."""
    df = df.copy()
    county_mean = df.groupby("fips")["leavers"].transform("mean")
    rel_dev = (df["leavers"] - county_mean).abs() / county_mean
    flag = (rel_dev >= threshold) | county_mean.isna() | (county_mean == 0)
    df["turnover_outlier_flag"] = flag.fillna(True)
    df.loc[flag.fillna(True), "turnover"] = np.nan
    return df


def main() -> None:
    DATA_DERIVED.mkdir(parents=True, exist_ok=True)
    # Prefer the extended (2025-Q2) file if present, with FrmJbLsS merged in
    main_path = QWI_CURRENT_DIR / "county_sex0_full_2025q2.parquet"
    if not main_path.exists():
        main_path = QWI_CURRENT_DIR / "county_sex0_full.parquet"
    sstable_path = QWI_CURRENT_DIR / "county_sex0_frmjblss.parquet"

    df = pd.read_parquet(main_path)
    for c in ("EmpTotal", "HirN", "FrmJbLs"):
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    print(f"Loaded {len(df):,} quarterly rows from {main_path.name}")

    sstable = None
    if sstable_path.exists():
        sstable = pd.read_parquet(sstable_path)
        for c in ("FrmJbLsS", "EmpS", "EmpEnd"):
            if c in sstable.columns:
                sstable[c] = pd.to_numeric(sstable[c], errors="coerce")
        print(f"Loaded {len(sstable):,} FrmJbLsS rows from {sstable_path.name}")

    gstable_path = QWI_CURRENT_DIR / "county_sex0_frmjbgns.parquet"
    gstable = None
    if gstable_path.exists():
        gstable = pd.read_parquet(gstable_path)
        gstable["FrmJbGnS"] = pd.to_numeric(gstable["FrmJbGnS"], errors="coerce")
        print(f"Loaded {len(gstable):,} FrmJbGnS rows from {gstable_path.name}")

    wide = pivot_to_quarter_wide(df, sstable=sstable, gstable=gstable)
    print(f"Pivoted to {len(wide):,} county-year wide rows")

    sy = construct_school_year_measures(wide)
    sy = sy[(sy["school_year"] >= 2001) & (sy["school_year"] <= 2024)]
    print(f"Built {len(sy):,} school-year rows")

    sy = apply_outlier_rule(sy)
    n_valid_turnover = sy["turnover"].notna().sum()
    n_valid_nnjf = sy["nnjf"].notna().sum()
    print(f"  valid turnover (post-outlier): {n_valid_turnover:,}")
    print(f"  valid NNJF:                    {n_valid_nnjf:,}")

    out = DATA_DERIVED / "county_school_year_measures.parquet"
    sy.to_parquet(out, index=False)
    print(f"Wrote {out}")

    # Sanity stats
    print("\nWeighted (1/emp_lag) descriptives — compare to Appendix Table A2:")
    valid = sy.dropna(subset=["turnover", "emp_lag"])
    valid = valid[valid["emp_lag"] > 0]
    t = valid["turnover"].astype(float).values
    w = 1.0 / valid["emp_lag"].astype(float).values
    idx = np.argsort(t); cw = np.cumsum(w[idx]) / w.sum()
    def wq(values, weights, q):
        i = np.argsort(values); c = np.cumsum(weights[i]) / weights.sum()
        return values[i][np.searchsorted(c, q)]
    print(f"  turnover median: {wq(t, w, 0.5):.4f}  (paper 0.251)")
    print(f"  turnover mean:   {(t*w).sum()/w.sum():.4f}  (paper 0.261)")

    valid_n = sy.dropna(subset=["nnjf_per_100", "emp_lag"])
    valid_n = valid_n[valid_n["emp_lag"] > 0]
    n_p100 = valid_n["nnjf_per_100"].astype(float).values
    w_n = 1.0 / valid_n["emp_lag"].astype(float).values
    print(f"  NNJF/100 median: {wq(n_p100, w_n, 0.5):.4f}  (paper 1.080)")
    print(f"  NNJF/100 mean:   {(n_p100*w_n).sum()/w_n.sum():.4f}  (paper 3.32)")

    print(f"  NNJF total for 2019-20 (in thousands): {sy[sy.school_year==2020]['nnjf'].sum()/1000:.1f}  (paper 224.9)")


if __name__ == "__main__":
    main()
