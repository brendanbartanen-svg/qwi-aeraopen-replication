"""Construct school-year turnover and net-negative job flow measures from quarterly QWI data.

v2 (incorporates authors' Stata code; see author_code/AUTHOR_CODE_FINDINGS.md):

  1) TURNOVER (paper Eq 1): leavers = ΣHirN_4Q − ΔEmp; turnover = leavers / EmpTotal_Q4_lag.
     Quarter window: Q3(t-1), Q4(t-1), Q1(t), Q2(t) — school year ending in t.

  2) NNJF: authors' code uses
        NNJF = FrmJbLsS_q1 + FrmJbLsS_q2_lag + FrmJbLsS_q3_lag + FrmJbLsS_q4_lag
     This is the SUM over 4 quarters of just FrmJbLsS (Firm Job Losses to Stable
     Employment) — NOT averaged, NOT subtracting FrmJbGnS. The quarter window uses
     q2_LAG (not q2 like turnover does), which is either an intentional asymmetric
     window or a typo. We compute BOTH windows and write both to the panel:
       nnjf_sy:     sum(FrmJbLsS) over Q3_lag + Q4_lag + Q1 + Q2 (school year)
       nnjf_authors: sum(FrmJbLsS) over Q1 + Q2_lag + Q3_lag + Q4_lag (their literal code)

  3) PER-100 NORMALIZATIONS: authors use different normalizations in different places.
     We compute all three and let each appendix-table script pick the right one:
       nnjf_per_100_simple:  NNJF / 100              (Figure 2 / Table A2 distribution)
       nnjf_per_100_q3lag:   NNJF / (EmpTotal_Q3_lag / 100)  (demographic tables A6/A7)
       nnjf_per_100_q3:      NNJF / (EmpTotal_Q3 / 100)      (state pandemic table A8)

  4) OUTLIER RULES (authors' code lines 278-308):
       - Drop county-year if leavers > 1.33 × county-mean leavers
       - Drop county-year if EmpTotal > 1.33 × county-mean EmpTotal
       - Drop county-year if turnover > 1.33 × county-mean turnover
       - Drop COUNTY (all years) if mean turnover >= 0.7
     Applied successively. We keep the variable name `33% rule` (paper Footnote 2);
     the authors' multiplier of 1.33 implements the same threshold.
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

    # --- NNJF (authors' formula) ---
    # Authors' Stata: gen job_destruct = frmjblss_q1 + frmjblss_q2_lag + frmjblss_q3_lag + frmjblss_q4_lag
    # That's SUM (not avg) of FrmJbLsS only (not subtracting FrmJbGnS).
    # Quarter window asymmetry (q2_lag instead of q2) is either intentional or a typo;
    # we compute BOTH windows and write both to the panel.
    if "frmjblss_q3_lag" in merged.columns:
        # School-year window (same window as turnover): Q3_lag + Q4_lag + Q1 + Q2
        merged["nnjf_sy"] = (merged["frmjblss_q3_lag"] + merged["frmjblss_q4_lag"]
                              + merged["frmjblss_q1"] + merged["frmjblss_q2"])
        # Authors' literal window: Q1 + Q2_lag + Q3_lag + Q4_lag
        # Need to construct Q2_lag — it's "Q2 of previous calendar year"
        if "frmjblss_q2" in merged.columns:
            # Build a Q2_lag by shifting within county
            merged = merged.sort_values(["fips", "year"]).reset_index(drop=True)
            merged["frmjblss_q2_lag"] = merged.groupby("fips")["frmjblss_q2"].shift(1)
            merged["nnjf_authors"] = (merged["frmjblss_q1"] + merged["frmjblss_q2_lag"]
                                       + merged["frmjblss_q3_lag"] + merged["frmjblss_q4_lag"])
        else:
            merged["nnjf_authors"] = pd.NA
        merged["nnjf_source"] = "sum(FrmJbLsS over 4 quarters) per authors' Stata code"
    else:
        # Fallback to FrmJbLs (non-stable) if FrmJbLsS unavailable
        merged["nnjf_sy"] = (merged["frmjbls_q3_lag"] + merged["frmjbls_q4_lag"]
                              + merged["frmjbls_q1"] + merged["frmjbls_q2"])
        merged["nnjf_authors"] = pd.NA
        merged["nnjf_source"] = "sum(FrmJbLs) — fallback (FrmJbLsS unavailable)"

    # Primary NNJF column = school-year window (matches turnover's window).
    # Downstream scripts can switch to nnjf_authors if needed.
    merged["nnjf"] = merged["nnjf_sy"]

    # --- Per-100 normalizations (authors use three different formulas) ---
    # Formula 1: NNJF / 100  (Figure 2 / Table A2; "per 100" is just a rescale, not a rate)
    merged["nnjf_per_100_simple"] = merged["nnjf"] / 100.0
    # Formula 2: NNJF / (EmpTotal_Q3_lag / 100)  (demographic tables A6/A7)
    merged["nnjf_per_100_q3lag"] = merged["nnjf"] / (merged["emp_q3_lag"] / 100.0)
    # Formula 3: NNJF / (EmpTotal_Q3 / 100)  (state pandemic Table A8)
    merged["nnjf_per_100_q3"] = merged["nnjf"] / (merged["emp_q3"] / 100.0)
    # Back-compat alias: keep `nnjf_per_100` as the simple form (matches Table A2)
    merged["nnjf_per_100"] = merged["nnjf_per_100_simple"]

    out_cols = [
        "fips", "school_year", "emp_q4_lag", "emp_q3_lag", "emp_q3", "emp_q2", "leavers",
        "turnover", "nnjf", "nnjf_sy", "nnjf_authors",
        "nnjf_per_100", "nnjf_per_100_simple", "nnjf_per_100_q3lag", "nnjf_per_100_q3",
    ]
    out = merged[out_cols].rename(columns={"emp_q4_lag": "emp_lag", "emp_q2": "emp_spring_end"})
    return out


def merge_fte(sy: pd.DataFrame, fte_path: Path) -> pd.DataFrame:
    """Merge NCES CCD LEA-staff FTE counts (aggregated to county-year) into the
    school-year measures panel. Adds a `fte` column. Authors' Stata weight is
    1/FTE (with FTE from NCES ELSI). For counties/years without FTE coverage,
    fte is NaN — downstream code falls back to 1/emp_lag.
    """
    if not fte_path.exists():
        print(f"  (no FTE file at {fte_path} — skipping)")
        sy["fte"] = np.nan
        return sy
    fte = pd.read_parquet(fte_path)
    fte["fips"] = fte["fips"].astype(str).str.zfill(5)
    fte["school_year"] = fte["school_year"].astype(int)
    sy["fips"] = sy["fips"].astype(str).str.zfill(5)
    sy["school_year"] = sy["school_year"].astype(int)
    sy = sy.merge(fte[["fips","school_year","fte"]], on=["fips","school_year"], how="left")
    n_matched = sy["fte"].notna().sum()
    n_total = len(sy)
    print(f"  FTE merge: {n_matched:,} / {n_total:,} county-years have FTE coverage ({100*n_matched/n_total:.1f}%)")
    return sy


def apply_outlier_rule(df: pd.DataFrame, multiplier: float = 1.33,
                        county_mean_max_turnover: float = 0.7) -> pd.DataFrame:
    """Authors' Stata outlier rule (lines 278-308 of Teacher Labor Market Data QWI V13 Color.do):

    Applied successively to (1) leavers, (2) emp_lag, (3) turnover:
        - Drop if value > multiplier * county_mean(value)
        - Drop if value falls below a low-bound (catches negatives/zeros):
            leavers, emp_lag: drop if value <= 1
            turnover:         drop if value <= 0.001

    Then drop any county whose mean turnover is >= 0.7 entirely.

    The multiplier of 1.33 corresponds to paper Footnote 2's "33% deviation" rule.
    """
    df = df.copy()
    low_bound = {"leavers": 1.0, "emp_lag": 1.0, "turnover": 0.001}
    for col in ["leavers", "emp_lag", "turnover"]:
        if col not in df.columns:
            continue
        county_mean = df.groupby("fips")[col].transform("mean")
        threshold = county_mean * multiplier
        high_outlier = (df[col] > threshold) & df[col].notna()
        low_outlier = df[col] <= low_bound[col]
        df.loc[high_outlier | low_outlier, col] = np.nan
        # If we just NaN'd leavers or emp_lag, recompute turnover
        if col == "leavers" or col == "emp_lag":
            df["turnover"] = df["leavers"] / df["emp_lag"]

    # Drop counties with mean turnover >= 0.7 entirely
    mean_turnover = df.groupby("fips")["turnover"].transform("mean")
    df = df[~(mean_turnover >= county_mean_max_turnover)].copy()

    df["turnover_outlier_flag"] = df["turnover"].isna()
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

    # v2.1: merge in NCES CCD FTE for 1/FTE weighting (authors' weight)
    sy = merge_fte(sy, DATA_DERIVED / "county_year_fte.parquet")

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
    print(f"  NNJF/100 median (simple): {wq(n_p100, w_n, 0.5):.4f}  (paper Table A2: 1.080)")
    print(f"  NNJF/100 mean (simple):   {(n_p100*w_n).sum()/w_n.sum():.4f}  (paper Table A2: 3.32)")

    # Unweighted (Figure 2 Panel B annotation says median = 108, P99 = 3,660)
    print("\nUnweighted NNJF count distribution — compare to Figure 2 Panel B annotation:")
    n_all = sy.dropna(subset=["nnjf"])["nnjf"].astype(float).values
    print(f"  NNJF count unweighted median: {np.median(n_all):.1f}  (paper Figure 2: 108)")
    print(f"  NNJF count unweighted P99:    {np.percentile(n_all, 99):.0f}  (paper Figure 2: 3,660)")

    # Test the authors' alternate window (q1 + q2_lag + q3_lag + q4_lag)
    if sy["nnjf_authors"].notna().any():
        print("\nAuthors' literal quarter window (q1 + q2_lag + q3_lag + q4_lag):")
        n_alt = sy.dropna(subset=["nnjf_authors"])["nnjf_authors"].astype(float).values
        print(f"  unweighted median: {np.median(n_alt):.1f}  (paper 108)")
        print(f"  unweighted P99:    {np.percentile(n_alt, 99):.0f}  (paper 3,660)")
        print(f"  2019-20 total:     {sy[sy.school_year==2020]['nnjf_authors'].sum()/1000:.1f}K  (paper 224.9K)")

    print(f"\n  NNJF total for 2019-20 (school-year window, K): {sy[sy.school_year==2020]['nnjf'].sum()/1000:.1f}  (paper 224.9)")


if __name__ == "__main__":
    main()
