"""Agent investigation: NNJF per-100 denominator mystery.

The replication has NNJF/100 ~2.3-6x larger than the paper. The TOTAL count of NNJF
matches the paper (within 1.0-1.3x), so the issue is the per-100 normalization.

This script tests 10+ alternative denominator/normalization specifications.

Paper target values (Table A4 medians for NNJF/100):
    2019: 0.43
    2020: 0.51
    2021: 0.31
    2023: 0.40
Paper Table A2 pooled (2001-2021):
    median 1.080, mean 3.32
Current baseline (avg(FrmJbLsS) / EmpTotal_q4_lag):
    median ~2.96, mean ~5.55  (2.3x off pooled; 6.5x off 2019 median)
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from _config import DATA_DERIVED, QWI_CURRENT_DIR, OUTPUT


# -----------------------------------------------------------------------------
# Reference data
# -----------------------------------------------------------------------------
PAPER_MEDIANS = {
    2001: 0.40, 2002: 0.39, 2003: 0.42, 2004: 0.43, 2005: 0.39,
    2006: 0.43, 2007: 0.48, 2008: 0.46, 2009: 0.47, 2010: 0.43,
    2011: 0.50, 2012: 0.47, 2013: 0.45, 2014: 0.45, 2015: 0.44,
    2016: 0.45, 2017: 0.42, 2018: 0.43, 2019: 0.43, 2020: 0.51,
    2021: 0.31, 2022: 0.34, 2023: 0.40, 2024: 0.40,
}
PAPER_MEANS = {
    2001: 0.65, 2002: 0.68, 2003: 0.71, 2004: 0.73, 2005: 0.71,
    2006: 0.74, 2007: 0.80, 2008: 0.77, 2009: 0.74, 2010: 0.74,
    2011: 0.82, 2012: 0.78, 2013: 0.75, 2014: 0.76, 2015: 0.75,
    2016: 0.76, 2017: 0.71, 2018: 0.73, 2019: 0.73, 2020: 0.93,
    2021: 0.62, 2022: 0.61, 2023: 0.69, 2024: 0.67,
}
PAPER_POOLED_MEDIAN = 1.080
PAPER_POOLED_MEAN = 3.32

CHECK_YEARS = [2019, 2020, 2021, 2023]


def weighted_quantile(v: np.ndarray, w: np.ndarray, q: float = 0.5) -> float:
    v = np.asarray(v, dtype=float); w = np.asarray(w, dtype=float)
    mask = np.isfinite(v) & np.isfinite(w) & (w > 0)
    v, w = v[mask], w[mask]
    if len(v) == 0:
        return np.nan
    idx = np.argsort(v)
    cw = np.cumsum(w[idx]) / w.sum()
    return float(v[idx][np.searchsorted(cw, q)])


def weighted_mean(v: np.ndarray, w: np.ndarray) -> float:
    v = np.asarray(v, dtype=float); w = np.asarray(w, dtype=float)
    mask = np.isfinite(v) & np.isfinite(w) & (w > 0)
    v, w = v[mask], w[mask]
    if len(v) == 0:
        return np.nan
    return float((v * w).sum() / w.sum())


def summarize_panel(df: pd.DataFrame, rate_col: str, weight_col: str,
                    sample_years=(2001, 2021)) -> dict:
    d = df.dropna(subset=[rate_col, weight_col]).copy()
    d = d[d[weight_col] > 0]
    d[rate_col] = pd.to_numeric(d[rate_col], errors="coerce")
    d = d[np.isfinite(d[rate_col].astype(float))]
    d_pool = d[(d.school_year >= sample_years[0]) & (d.school_year <= sample_years[1])]
    v = d_pool[rate_col].astype(float).values
    w = 1.0 / d_pool[weight_col].astype(float).values
    out = {"pooled_median": weighted_quantile(v, w, 0.5),
           "pooled_mean": weighted_mean(v, w)}
    for yr in CHECK_YEARS:
        dy = d[d.school_year == yr]
        vy = dy[rate_col].astype(float).values
        wy = 1.0 / dy[weight_col].astype(float).values
        out[f"median_{yr}"] = weighted_quantile(vy, wy, 0.5)
        out[f"mean_{yr}"] = weighted_mean(vy, wy)
    return out


# -----------------------------------------------------------------------------
# Build wide-quarter panel with ALL the variables we need
# -----------------------------------------------------------------------------
def build_wide_panel() -> pd.DataFrame:
    main_path = QWI_CURRENT_DIR / "county_sex0_full_2025q2.parquet"
    sstable_path = QWI_CURRENT_DIR / "county_sex0_frmjblss.parquet"

    df = pd.read_parquet(main_path)
    for c in ("EmpTotal", "Emp", "HirN", "FrmJbLs"):
        df[c] = pd.to_numeric(df[c], errors="coerce")

    sst = pd.read_parquet(sstable_path)
    for c in ("FrmJbLsS", "FrmJbGnS", "EmpS", "EmpEnd"):
        sst[c] = pd.to_numeric(sst[c], errors="coerce")

    base = df.merge(
        sst[["fips", "year", "quarter", "FrmJbLsS", "FrmJbGnS", "EmpS", "EmpEnd"]],
        on=["fips", "year", "quarter"], how="left"
    )

    vars_to_pivot = ["EmpTotal", "Emp", "EmpS", "EmpEnd", "HirN",
                     "FrmJbLs", "FrmJbLsS", "FrmJbGnS"]
    short = {"EmpTotal": "empt", "Emp": "emp", "EmpS": "emps", "EmpEnd": "empend",
             "HirN": "hir", "FrmJbLs": "fjl", "FrmJbLsS": "fjls",
             "FrmJbGnS": "fjgs"}
    pivs = []
    for v in vars_to_pivot:
        p = base.pivot_table(index=["fips", "year"], columns="quarter",
                              values=v, aggfunc="first")
        p.columns = [f"{short[v]}_q{int(c)}" for c in p.columns]
        pivs.append(p)
    wide = pd.concat(pivs, axis=1).reset_index()

    # Build lagged-year cols (q3_lag, q4_lag) for each
    prev_cols = ["fips", "year"]
    rename = {"year": "prev_year"}
    for v in vars_to_pivot:
        s = short[v]
        prev_cols += [f"{s}_q3", f"{s}_q4"]
        rename[f"{s}_q3"] = f"{s}_q3_lag"
        rename[f"{s}_q4"] = f"{s}_q4_lag"
    prev = wide[prev_cols].rename(columns=rename)
    wide["prev_year"] = wide["year"] - 1
    wide = wide.merge(prev, on=["fips", "prev_year"], how="left")
    wide["school_year"] = wide["year"]

    for c in wide.columns:
        if c not in ("fips", "year", "school_year", "prev_year"):
            wide[c] = wide[c].astype("Float64")
    return wide


# -----------------------------------------------------------------------------
# Hypothesis testers
# -----------------------------------------------------------------------------
def build_hypothesis_panels(wide: pd.DataFrame) -> dict[str, pd.DataFrame]:
    panels = {}

    fjls_sum4 = (wide["fjls_q3_lag"] + wide["fjls_q4_lag"]
                 + wide["fjls_q1"] + wide["fjls_q2"])
    fjls_avg4 = fjls_sum4 / 4.0

    fjgs_sum4 = (wide["fjgs_q3_lag"] + wide["fjgs_q4_lag"]
                 + wide["fjgs_q1"] + wide["fjgs_q2"])
    fjl_sum4 = (wide["fjl_q3_lag"] + wide["fjl_q4_lag"]
                + wide["fjl_q1"] + wide["fjl_q2"])

    empt_sum4 = (wide["empt_q3_lag"] + wide["empt_q4_lag"]
                 + wide["empt_q1"] + wide["empt_q2"])

    # BASELINE
    panels["BASELINE: 100*avg(FrmJbLsS)/EmpTotal_q4_lag"] = pd.DataFrame({
        "fips": wide["fips"], "school_year": wide["school_year"],
        "rate": 100.0 * fjls_avg4 / wide["empt_q4_lag"],
        "emp_lag": wide["empt_q4_lag"],
    })

    # ----------------------------------------------------------------------
    # H1: SUM(FrmJbLsS) / SUM(EmpTotal) over 4 school-year quarters
    # (i.e. denominator is "annualized" sum, numerator is total job losses)
    # ----------------------------------------------------------------------
    panels["H1: 100*sum(FrmJbLsS)/sum(EmpTotal)"] = pd.DataFrame({
        "fips": wide["fips"], "school_year": wide["school_year"],
        "rate": 100.0 * fjls_sum4 / empt_sum4,
        "emp_lag": wide["empt_q4_lag"],
    })

    # ----------------------------------------------------------------------
    # H2: 100 * avg(FrmJbLsS) / sum(EmpTotal) over 4 q  (= baseline/4)
    # Same as H10: scales like an "annualized rate"
    # ----------------------------------------------------------------------
    panels["H2: 100*avg(FrmJbLsS)/sum(EmpTotal) = BASELINE/4"] = pd.DataFrame({
        "fips": wide["fips"], "school_year": wide["school_year"],
        "rate": 100.0 * fjls_avg4 / empt_sum4,
        "emp_lag": wide["empt_q4_lag"],
    })

    # ----------------------------------------------------------------------
    # H3: per-quarter rate then mean (using EmpTotal denom)
    # ----------------------------------------------------------------------
    rates_t = []
    for fq, eq in [("fjls_q3_lag", "empt_q3_lag"),
                   ("fjls_q4_lag", "empt_q4_lag"),
                   ("fjls_q1", "empt_q1"),
                   ("fjls_q2", "empt_q2")]:
        rates_t.append((100.0 * wide[fq] / wide[eq]).astype("Float64"))
    rate_mean_t = (rates_t[0] + rates_t[1] + rates_t[2] + rates_t[3]) / 4.0
    panels["H3: mean per-quarter rate (EmpTotal denom)"] = pd.DataFrame({
        "fips": wide["fips"], "school_year": wide["school_year"],
        "rate": rate_mean_t,
        "emp_lag": wide["empt_q4_lag"],
    })

    # ----------------------------------------------------------------------
    # H4: avg(FrmJbLsS) divided by avg(EmpTotal across q3_lag, q4_lag, q1, q2)
    # (same as H1 numerically but useful sanity check)
    # ----------------------------------------------------------------------
    panels["H4: 100*avg(FrmJbLsS)/avg(EmpTotal over 4q)"] = pd.DataFrame({
        "fips": wide["fips"], "school_year": wide["school_year"],
        "rate": 100.0 * fjls_avg4 / (empt_sum4 / 4.0),
        "emp_lag": wide["empt_q4_lag"],
    })

    # ----------------------------------------------------------------------
    # H5: NET job destruction: max(FrmJbLsS - FrmJbGnS, 0) per quarter, avg of 4.
    # This is the "net-negative" interpretation of Eq 2-3 from the paper. Test
    # demonstrated this NUMERATOR matches paper's NNJF totals (Table A4) almost
    # exactly: 2019=174K (paper 176K), 2020=253K (paper 225K), 2021=147K
    # (paper 150K), 2023=162K (paper 162K).  So the COUNT is correct; rate
    # is still 6x off paper, meaning denominator issue remains.
    # ----------------------------------------------------------------------
    net = ((wide["fjls_q3_lag"] - wide["fjgs_q3_lag"]).clip(lower=0)
           + (wide["fjls_q4_lag"] - wide["fjgs_q4_lag"]).clip(lower=0)
           + (wide["fjls_q1"] - wide["fjgs_q1"]).clip(lower=0)
           + (wide["fjls_q2"] - wide["fjgs_q2"]).clip(lower=0)) / 4.0
    panels["H5: 100*avg(max(FrmJbLsS-FrmJbGnS,0))/EmpTotal_q4_lag"] = pd.DataFrame({
        "fips": wide["fips"], "school_year": wide["school_year"],
        "rate": 100.0 * net / wide["empt_q4_lag"],
        "emp_lag": wide["empt_q4_lag"],
    })

    # H5b: net-negative NUMERATOR, sum-of-quarters DENOMINATOR (annualized)
    panels["H5b: 100*sum(max(FrmJbLsS-FrmJbGnS,0))/sum(EmpTotal)"] = pd.DataFrame({
        "fips": wide["fips"], "school_year": wide["school_year"],
        "rate": 100.0 * (4 * net) / empt_sum4,
        "emp_lag": wide["empt_q4_lag"],
    })
    # H5c: net-negative NUMERATOR /4, denominator EmpTotal_q4_lag (=H5/4)
    panels["H5c: 100*avg(max(FrmJbLsS-FrmJbGnS,0))/(4*EmpTotal_q4_lag)"] = pd.DataFrame({
        "fips": wide["fips"], "school_year": wide["school_year"],
        "rate": 100.0 * net / (4.0 * wide["empt_q4_lag"]),
        "emp_lag": wide["empt_q4_lag"],
    })

    # ----------------------------------------------------------------------
    # H6: STATE-AGGREGATED rate as the county-level value.
    # Compute total NNJF and total EmpTotal_q4_lag at state level, then ASSIGN
    # the state rate back to each county.  This tests whether the paper
    # "rolls up" to state level.
    # ----------------------------------------------------------------------
    h6 = wide[["fips", "school_year"]].copy()
    h6["nnjf"] = fjls_avg4
    h6["emp"] = wide["empt_q4_lag"]
    h6["state"] = h6["fips"].astype(str).str[:2]
    grp = h6.groupby(["state", "school_year"]).agg(
        nnjf_sum=("nnjf", "sum"), emp_sum=("emp", "sum")).reset_index()
    grp["state_rate"] = 100.0 * grp["nnjf_sum"] / grp["emp_sum"]
    h6 = h6.merge(grp[["state", "school_year", "state_rate"]],
                   on=["state", "school_year"], how="left")
    panels["H6: state-aggregated rate assigned to county"] = pd.DataFrame({
        "fips": h6["fips"], "school_year": h6["school_year"],
        "rate": h6["state_rate"], "emp_lag": h6["emp"],
    })

    # ----------------------------------------------------------------------
    # H7: NNJF expressed per FIRM not per WORKER.
    # If paper meant per-100 *firms* (schools/districts), the denom is much smaller.
    # But that would make rate LARGER, not smaller. Skip.
    # Instead, try: numerator is `FrmJbLsS_q3_lag + FrmJbLsS_q4_lag + FrmJbLsS_q1`
    # (3 quarters, dropping Q2 since that's the "end" not a stable period).
    # Divided by 3*EmpTotal_q4_lag.
    # ----------------------------------------------------------------------
    fjls_3q = (wide["fjls_q3_lag"] + wide["fjls_q4_lag"] + wide["fjls_q1"]) / 3.0
    panels["H7: 100*avg(FrmJbLsS over q3,q4,q1)/EmpTotal_q4_lag"] = pd.DataFrame({
        "fips": wide["fips"], "school_year": wide["school_year"],
        "rate": 100.0 * fjls_3q / wide["empt_q4_lag"],
        "emp_lag": wide["empt_q4_lag"],
    })

    # ----------------------------------------------------------------------
    # H8: Maybe paper uses (FrmJbLsS_q2_only) — the END of the school year
    # only — divided by EmpTotal_q4_lag. That's the "left employment" rate.
    # ----------------------------------------------------------------------
    panels["H8: 100*FrmJbLsS_q2/EmpTotal_q4_lag (Q2 only)"] = pd.DataFrame({
        "fips": wide["fips"], "school_year": wide["school_year"],
        "rate": 100.0 * wide["fjls_q2"] / wide["empt_q4_lag"],
        "emp_lag": wide["empt_q4_lag"],
    })

    # ----------------------------------------------------------------------
    # H9: Maybe NNJF is in PERCENTAGE POINTS already, not counts.
    # i.e., paper's NNJF column = avg(FrmJbLsS) / 100  (off by 100 division).
    # Equivalently NNJF/100 = avg(FrmJbLsS)/100/EmpTotal_q4_lag/100.
    # That would be baseline/100 — wrong scale. Try baseline/10 (decimal-point
    # error).
    # ----------------------------------------------------------------------
    # We can compute this by just dividing baseline by 10 — but it's not a
    # principled hypothesis. Skip.

    # ----------------------------------------------------------------------
    # H9: PER 100 STABLE workers averaged across 4 quarters using EmpS
    # ----------------------------------------------------------------------
    emps_avg4 = (wide["emps_q3_lag"] + wide["emps_q4_lag"]
                 + wide["emps_q1"] + wide["emps_q2"]) / 4.0
    panels["H9: 100*avg(FrmJbLsS)/avg(EmpS)"] = pd.DataFrame({
        "fips": wide["fips"], "school_year": wide["school_year"],
        "rate": 100.0 * fjls_avg4 / emps_avg4,
        "emp_lag": wide["empt_q4_lag"],
    })

    # ----------------------------------------------------------------------
    # H10: avg(FrmJbLs) / sum(EmpTotal) -- the un-stable variant of H1
    # ----------------------------------------------------------------------
    panels["H10: 100*sum(FrmJbLs)/sum(EmpTotal)"] = pd.DataFrame({
        "fips": wide["fips"], "school_year": wide["school_year"],
        "rate": 100.0 * fjl_sum4 / empt_sum4,
        "emp_lag": wide["empt_q4_lag"],
    })

    # ----------------------------------------------------------------------
    # H11: Per-quarter rate using FrmJbLsS / EmpS, then median across quarters,
    # then median across years -- a robust median-of-medians estimator
    # ----------------------------------------------------------------------
    rates_q = []
    for fq, eq in [("fjls_q3_lag", "emps_q3_lag"),
                   ("fjls_q4_lag", "emps_q4_lag"),
                   ("fjls_q1", "emps_q1"),
                   ("fjls_q2", "emps_q2")]:
        rates_q.append((100.0 * wide[fq] / wide[eq]).astype("Float64"))
    # take min as a "stability" lower-bound
    med_rate = pd.concat(rates_q, axis=1).median(axis=1)
    panels["H11: median across 4 per-quarter FrmJbLsS/EmpS rates"] = pd.DataFrame({
        "fips": wide["fips"], "school_year": wide["school_year"],
        "rate": med_rate,
        "emp_lag": wide["empt_q4_lag"],
    })

    return panels


def main() -> None:
    wide = build_wide_panel()
    print(f"Built wide panel: {len(wide):,} rows")

    panels = build_hypothesis_panels(wide)

    rows = []
    for name, pdat in panels.items():
        pdat = pdat[(pdat.school_year >= 2001) & (pdat.school_year <= 2024)]
        stats = summarize_panel(pdat, "rate", "emp_lag", sample_years=(2001, 2021))
        row = {"hypothesis": name, **stats}
        rows.append(row)
    summary = pd.DataFrame(rows)

    summary["pooled_median_target"] = PAPER_POOLED_MEDIAN
    summary["pooled_mean_target"] = PAPER_POOLED_MEAN
    summary["ratio_med"] = summary["pooled_median"] / PAPER_POOLED_MEDIAN
    summary["ratio_mean"] = summary["pooled_mean"] / PAPER_POOLED_MEAN

    def closeness(row):
        targets = {"pooled_median": PAPER_POOLED_MEDIAN}
        for yr in CHECK_YEARS:
            targets[f"median_{yr}"] = PAPER_MEDIANS[yr]
        diffs = []
        for k, t in targets.items():
            if pd.notna(row[k]) and row[k] > 0:
                diffs.append(abs(np.log(row[k] / t)))
        return float(np.mean(diffs)) if diffs else np.inf
    summary["closeness"] = summary.apply(closeness, axis=1)
    summary = summary.sort_values("closeness")

    print("\n" + "=" * 120)
    print("Hypothesis test results (pooled = 2001-2021 sample, weighted by 1/emp_lag)")
    print("=" * 120)
    print(f"{'Hypothesis':<58} {'pool_med':>8} {'pool_mn':>8} "
          f"{'m2019':>7} {'m2020':>7} {'m2021':>7} {'m2023':>7} {'rat_med':>7} {'close':>7}")
    print(f"{'PAPER TARGET':<58} {PAPER_POOLED_MEDIAN:>8.3f} "
          f"{PAPER_POOLED_MEAN:>8.3f} "
          f"{PAPER_MEDIANS[2019]:>7.2f} {PAPER_MEDIANS[2020]:>7.2f} "
          f"{PAPER_MEDIANS[2021]:>7.2f} {PAPER_MEDIANS[2023]:>7.2f} "
          f"{'1.00':>7} {'-':>7}")
    print("-" * 120)
    for _, r in summary.iterrows():
        print(f"{r['hypothesis']:<58} {r['pooled_median']:>8.3f} "
              f"{r['pooled_mean']:>8.3f} "
              f"{r['median_2019']:>7.3f} {r['median_2020']:>7.3f} "
              f"{r['median_2021']:>7.3f} {r['median_2023']:>7.3f} "
              f"{r['ratio_med']:>7.2f} "
              f"{r['closeness']:>7.3f}")

    out_path = OUTPUT / "tables" / "agent_denominator_results.csv"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    summary.to_csv(out_path, index=False)
    print(f"\nSaved to {out_path}")

    # Top 3 year-by-year
    print("\n\nYear-by-year medians for top 3 hypotheses:\n")
    top3 = summary.head(3)
    yr_rows = []
    for _, row in top3.iterrows():
        name = row["hypothesis"]
        pdat = panels[name]
        pdat = pdat[(pdat.school_year >= 2001) & (pdat.school_year <= 2024)]
        pdat = pdat.dropna(subset=["rate", "emp_lag"]).copy()
        pdat = pdat[pdat.emp_lag > 0]
        meds = {}
        for yr in range(2001, 2025):
            sub = pdat[pdat.school_year == yr]
            v = sub["rate"].astype(float).values
            w = 1.0 / sub["emp_lag"].astype(float).values
            meds[yr] = weighted_quantile(v, w, 0.5)
        yr_rows.append({"name": name, **meds})
    yr_df = pd.DataFrame(yr_rows).set_index("name").T
    yr_df["PAPER"] = pd.Series(PAPER_MEDIANS)
    print(yr_df.to_string(float_format=lambda x: f"{x:.3f}"))


if __name__ == "__main__":
    main()
