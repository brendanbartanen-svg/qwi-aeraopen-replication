"""Agent investigation: alternative time-aggregation methods for NNJF.

We have a remaining replication discrepancy:
  - With NNJF = avg(FrmJbLsS over 4 school-year quarters) and per-100 = 100*NNJF/emp_q4_lag,
    TOTALS land within 1.0-1.3x of the paper, but per-100 rates are ~2.3x too big at all
    quantiles.  The 2.3x is suspiciously *uniform* across years, pointing to a single
    missing scaling/aggregation step.

This script defines 5 distinct hypotheses about how the paper might collapse the four
school-year quarters into one annualized number, then computes the same summary stats
(year totals, pooled weighted median, year medians) for each.

Paper targets we compare against:
  - Table A4 NNJF Total (thousands) 2019/2020/2021/2023:  176.2 / 224.9 / 150.4 / 162.1
  - Table A4 NNJF/100 median (years):                     0.43 / 0.51 / 0.31 / 0.40
  - Table A2 pooled NNJF/100 median:                      1.080
  - Table A2 pooled NNJF/100 mean:                        3.32

Hypotheses tested (all use FrmJbLsS as the quarterly raw input, since the previous
investigation showed it's the construct closest to "jobs lost") :

  H1  Quarter-level rate first, then average rate across 4 quarters
        rate_cq   = 100 * FrmJbLsS_cq / EmpS_cq         (per-quarter rate)
        rate_cy   = mean(rate_cq) over the 4 SY quarters
        nnjf_count_cy = mean(FrmJbLsS_cq) over the 4 SY quarters
        -> tests "average the per-quarter rates, not the per-year totals"

  H2  Median across the 4 quarters (instead of mean)
        nnjf_count_cy = median(FrmJbLsS_cq) over 4 SY quarters
        rate_cy       = 100 * nnjf_count_cy / emp_q4_lag
        -> robust to a single big-quarter pandemic shock (Q2-2020)

  H3  Trimmed mean -- drop the single largest of the 4 quarters
        nnjf_count_cy = mean of the 3 smallest FrmJbLsS_cq among the 4 SY quarters
        rate_cy       = 100 * nnjf_count_cy / emp_q4_lag

  H4  Spring-only quarters: average over Q1 + Q2 of spring year (drop fall lag)
        nnjf_count_cy = mean(FrmJbLsS_q1, FrmJbLsS_q2)
        rate_cy       = 100 * nnjf_count_cy / emp_q4_lag
        -> tests whether the paper effectively only counts the "end-of-school-year leaving"

  H5  Annual-pre-aggregation: build an annual employment denominator that matches the
      quarterly numerator (sum, not point-in-time), and use SUM of FrmJbLsS:
        nnjf_count_cy = sum(FrmJbLsS over 4 SY quarters)           (literal Eq 3)
        annual_emp    = sum(EmpS over 4 SY quarters)               (worker-quarters)
        rate_cy       = 100 * nnjf_count_cy / annual_emp
        -> the "person-quarter" denominator -- divides the literal sum by 4x emp,
           which scales rates by 1/4 vs the original method.

Bonus H6: Like H1 (quarterly rate first, average across quarters), but use mean across
      ONLY 3 quarters because the QWI flag tag pre-aggregation includes a separation
      indicator for each quarter ending.  This is essentially H1 with the Q4-lag
      excluded (so that Q3 is the implicit "starting" and Q4 is interior).

We compare each hypothesis on:
  - Pooled weighted (1/emp_lag) median  -- target 1.080
  - Pooled weighted (1/emp_lag) mean    -- target 3.32
  - Year totals (thousands) for 2019/2020/2021/2023
  - Year medians (weighted) for 2019/2020/2021/2023

And we check whether ratios to the paper are *consistent* across years -- a
constant ratio across years is the signature of a single missing scaling factor.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from _config import DATA_DERIVED, QWI_CURRENT_DIR, TABLES, OUTPUT


PAPER_TOTAL_THOUSANDS = {2019: 176.2, 2020: 224.9, 2021: 150.4, 2023: 162.1}
PAPER_MEDIAN_PER100 = {2019: 0.43, 2020: 0.51, 2021: 0.31, 2023: 0.40}
PAPER_POOLED_MEDIAN = 1.080
PAPER_POOLED_MEAN = 3.32


# -------- I/O & pivoting --------

def load_quarterly() -> pd.DataFrame:
    """Return a single long frame with EmpTotal, HirN, FrmJbLs, FrmJbLsS, EmpS per
    (fips, year, quarter)."""
    main = pd.read_parquet(QWI_CURRENT_DIR / "county_sex0_full_2025q2.parquet")
    sst = pd.read_parquet(QWI_CURRENT_DIR / "county_sex0_frmjblss.parquet")
    for c in ("EmpTotal", "HirN", "FrmJbLs"):
        main[c] = pd.to_numeric(main[c], errors="coerce")
    for c in ("FrmJbLsS", "EmpS", "EmpEnd"):
        sst[c] = pd.to_numeric(sst[c], errors="coerce")

    keep = ["fips", "year", "quarter", "EmpTotal", "HirN", "FrmJbLs"]
    keep_s = ["fips", "year", "quarter", "FrmJbLsS", "EmpS", "EmpEnd"]
    merged = main[keep].merge(sst[keep_s], on=["fips", "year", "quarter"], how="outer")
    merged = merged.sort_values(["fips", "year", "quarter"]).reset_index(drop=True)
    return merged


def to_school_year_long(qdf: pd.DataFrame) -> pd.DataFrame:
    """Tag each county-quarter with the spring_year of the school year it belongs to.

    School year ending in spring t consists of:
        Q3 of calendar year t-1
        Q4 of calendar year t-1
        Q1 of calendar year t
        Q2 of calendar year t
    """
    df = qdf.copy()
    df["sy_position"] = pd.NA
    df["spring_year"] = pd.NA
    # Q3 and Q4: school year = year + 1
    mask_fall = df["quarter"].isin([3, 4])
    df.loc[mask_fall, "spring_year"] = df.loc[mask_fall, "year"] + 1
    df.loc[df["quarter"] == 3, "sy_position"] = "Q3_lag"
    df.loc[df["quarter"] == 4, "sy_position"] = "Q4_lag"
    # Q1, Q2: school year = year
    mask_spring = df["quarter"].isin([1, 2])
    df.loc[mask_spring, "spring_year"] = df.loc[mask_spring, "year"]
    df.loc[df["quarter"] == 1, "sy_position"] = "Q1"
    df.loc[df["quarter"] == 2, "sy_position"] = "Q2"
    df["spring_year"] = pd.to_numeric(df["spring_year"])
    # Also keep emp_q4_lag: emp at end of fall (q4 of t-1) per (fips, spring_year)
    return df


def emp_q4_lag_table(sy_long: pd.DataFrame) -> pd.DataFrame:
    """For each (fips, spring_year), the EmpTotal at Q4 of the previous calendar year."""
    sub = sy_long[sy_long["sy_position"] == "Q4_lag"][["fips", "spring_year", "EmpTotal"]].copy()
    sub = sub.rename(columns={"EmpTotal": "emp_q4_lag"})
    return sub


# -------- weighted-stats helpers --------

def wq(values: np.ndarray, weights: np.ndarray, q: float) -> float:
    """Weighted quantile."""
    m = np.isfinite(values) & np.isfinite(weights) & (weights > 0)
    v = values[m]; w = weights[m]
    if len(v) == 0:
        return np.nan
    idx = np.argsort(v); v = v[idx]; w = w[idx]
    cw = np.cumsum(w) / w.sum()
    j = np.searchsorted(cw, q, side="left")
    j = min(j, len(v) - 1)
    return float(v[j])


def wmean(values: np.ndarray, weights: np.ndarray) -> float:
    m = np.isfinite(values) & np.isfinite(weights) & (weights > 0)
    if m.sum() == 0:
        return np.nan
    return float((values[m] * weights[m]).sum() / weights[m].sum())


def summarize(name: str, sy: pd.DataFrame) -> dict:
    """Compute paper-comparable summary stats for one hypothesis output.

    Expects columns: fips, spring_year, nnjf, emp_lag, nnjf_per_100.
    """
    valid = sy.dropna(subset=["nnjf_per_100", "emp_lag"]).copy()
    valid = valid[valid["emp_lag"] > 0]
    v = valid["nnjf_per_100"].astype(float).values
    w = 1.0 / valid["emp_lag"].astype(float).values

    out = {
        "name": name,
        "pooled_med": wq(v, w, 0.5),
        "pooled_mean": wmean(v, w),
        "n_obs": len(valid),
    }
    for y in (2019, 2020, 2021, 2023):
        sub = sy[sy["spring_year"] == y]
        out[f"total_{y}_k"] = sub["nnjf"].astype(float).sum() / 1000.0
        sub_v = sub.dropna(subset=["nnjf_per_100", "emp_lag"])
        sub_v = sub_v[sub_v["emp_lag"] > 0]
        vy = sub_v["nnjf_per_100"].astype(float).values
        wy = 1.0 / sub_v["emp_lag"].astype(float).values
        out[f"med_{y}"] = wq(vy, wy, 0.5)
    return out


# -------- hypothesis builders --------

def build_h1_qrate_first(sy_long: pd.DataFrame, denom: pd.DataFrame) -> pd.DataFrame:
    """Per-quarter rate, then mean across the 4 SY quarters."""
    d = sy_long.dropna(subset=["spring_year"]).copy()
    # Need EmpS at the quarter level to form a per-quarter rate.
    d["q_rate"] = 100.0 * d["FrmJbLsS"].astype(float) / d["EmpS"].astype(float)
    # Replace inf / non-pos-denominator
    d.loc[~np.isfinite(d["q_rate"]), "q_rate"] = np.nan

    g = d.groupby(["fips", "spring_year"], as_index=False).agg(
        nnjf=("FrmJbLsS", "mean"),
        nnjf_per_100=("q_rate", "mean"),
        n_quarters=("FrmJbLsS", "count"),
    )
    g = g[g["n_quarters"] == 4]
    g = g.merge(denom, on=["fips", "spring_year"], how="left")
    g = g.rename(columns={"emp_q4_lag": "emp_lag"})
    return g


def build_h2_median(sy_long: pd.DataFrame, denom: pd.DataFrame) -> pd.DataFrame:
    """Median FrmJbLsS across 4 SY quarters; per-100 uses emp_q4_lag."""
    d = sy_long.dropna(subset=["spring_year"]).copy()
    g = d.groupby(["fips", "spring_year"], as_index=False).agg(
        nnjf=("FrmJbLsS", "median"),
        n_quarters=("FrmJbLsS", "count"),
    )
    g = g[g["n_quarters"] == 4]
    g = g.merge(denom, on=["fips", "spring_year"], how="left")
    g = g.rename(columns={"emp_q4_lag": "emp_lag"})
    g["nnjf_per_100"] = 100.0 * g["nnjf"].astype(float) / g["emp_lag"].astype(float)
    return g


def build_h3_trimmed_mean(sy_long: pd.DataFrame, denom: pd.DataFrame) -> pd.DataFrame:
    """Drop the single largest of the 4 quarters; mean of remaining 3."""
    d = sy_long.dropna(subset=["spring_year"]).copy()

    def trimmed(group: pd.DataFrame) -> float:
        vals = group["FrmJbLsS"].dropna().astype(float).values
        if len(vals) != 4:
            return np.nan
        return float(np.sort(vals)[:3].mean())

    rows = (
        d.groupby(["fips", "spring_year"])
        .apply(trimmed, include_groups=False)
        .reset_index(name="nnjf")
    )
    rows = rows.merge(denom, on=["fips", "spring_year"], how="left")
    rows = rows.rename(columns={"emp_q4_lag": "emp_lag"})
    rows["nnjf_per_100"] = 100.0 * rows["nnjf"].astype(float) / rows["emp_lag"].astype(float)
    return rows


def build_h4_spring_only(sy_long: pd.DataFrame, denom: pd.DataFrame) -> pd.DataFrame:
    """Use only Q1+Q2 of spring year; nnjf = mean of those 2 quarters."""
    d = sy_long[sy_long["sy_position"].isin(["Q1", "Q2"])].copy()
    g = d.groupby(["fips", "spring_year"], as_index=False).agg(
        nnjf=("FrmJbLsS", "mean"),
        n_quarters=("FrmJbLsS", "count"),
    )
    g = g[g["n_quarters"] == 2]
    g = g.merge(denom, on=["fips", "spring_year"], how="left")
    g = g.rename(columns={"emp_q4_lag": "emp_lag"})
    g["nnjf_per_100"] = 100.0 * g["nnjf"].astype(float) / g["emp_lag"].astype(float)
    return g


def build_h5_person_quarter_denom(sy_long: pd.DataFrame, denom: pd.DataFrame) -> pd.DataFrame:
    """Literal Eq 3 numerator (SUM of 4 quarters), denominator = SUM of EmpS over 4 quarters
    (i.e. person-quarters).  This effectively divides the standard count-based rate by 4."""
    d = sy_long.dropna(subset=["spring_year"]).copy()
    g = d.groupby(["fips", "spring_year"], as_index=False).agg(
        nnjf=("FrmJbLsS", "sum"),
        annual_emp=("EmpS", "sum"),
        n_quarters=("FrmJbLsS", "count"),
    )
    g = g[g["n_quarters"] == 4]
    g = g.merge(denom, on=["fips", "spring_year"], how="left")
    g = g.rename(columns={"emp_q4_lag": "emp_lag"})
    g["nnjf_per_100"] = 100.0 * g["nnjf"].astype(float) / g["annual_emp"].astype(float)
    # report nnjf as the **mean** of the 4 quarters, so year totals are comparable to A4
    g["nnjf_total_for_table"] = g["nnjf"] / 4.0
    g["nnjf_for_total"] = g["nnjf_total_for_table"]
    return g


def build_h6_qrate_first_3q(sy_long: pd.DataFrame, denom: pd.DataFrame) -> pd.DataFrame:
    """Per-quarter rate, mean across only Q4_lag + Q1 + Q2 (drop Q3_lag).

    Rationale: separations are recorded at the END of each quarter; Q3 (summer)
    captures pre-school-year turnover that may have been excluded.  This is a 3-quarter
    average.
    """
    d = sy_long[sy_long["sy_position"].isin(["Q4_lag", "Q1", "Q2"])].copy()
    d["q_rate"] = 100.0 * d["FrmJbLsS"].astype(float) / d["EmpS"].astype(float)
    d.loc[~np.isfinite(d["q_rate"]), "q_rate"] = np.nan
    g = d.groupby(["fips", "spring_year"], as_index=False).agg(
        nnjf=("FrmJbLsS", "mean"),
        nnjf_per_100=("q_rate", "mean"),
        n_quarters=("FrmJbLsS", "count"),
    )
    g = g[g["n_quarters"] == 3]
    g = g.merge(denom, on=["fips", "spring_year"], how="left")
    g = g.rename(columns={"emp_q4_lag": "emp_lag"})
    return g


def build_h7_mean_count_avg_emp_denom(sy_long: pd.DataFrame, denom: pd.DataFrame) -> pd.DataFrame:
    """Numerator = mean(FrmJbLsS over 4q); denominator = mean(EmpS over 4q), NOT Q4-lag.

    Effectively this is total_FrmJbLsS / total_EmpS (= H5 in disguise) but expressed
    with mean/mean, and we *also* report nnjf as mean(FrmJbLsS).  This isolates whether
    the denominator (Q4-lag pt-in-time vs SY-avg) matters.
    """
    d = sy_long.dropna(subset=["spring_year"]).copy()
    g = d.groupby(["fips", "spring_year"], as_index=False).agg(
        nnjf=("FrmJbLsS", "mean"),
        emp_lag=("EmpS", "mean"),
        n_quarters=("FrmJbLsS", "count"),
    )
    g = g[g["n_quarters"] == 4]
    g["nnjf_per_100"] = 100.0 * g["nnjf"].astype(float) / g["emp_lag"].astype(float)
    return g


def build_h8_mean_count_empend_denom(sy_long: pd.DataFrame, denom: pd.DataFrame) -> pd.DataFrame:
    """Numerator = mean(FrmJbLsS over 4q); denominator = EmpEnd_q4_lag (end-of-quarter emp
    at end of fall semester).

    EmpEnd is a different point-in-time concept than EmpTotal (which is mid-quarter)
    and is used in other QWI rate formulas.
    """
    d = sy_long.dropna(subset=["spring_year"]).copy()
    g = d.groupby(["fips", "spring_year"], as_index=False).agg(
        nnjf=("FrmJbLsS", "mean"),
        n_quarters=("FrmJbLsS", "count"),
    )
    g = g[g["n_quarters"] == 4]
    # Get EmpEnd at Q4_lag = quarter 4 of (spring_year-1)
    end = sy_long[sy_long["sy_position"] == "Q4_lag"][["fips", "spring_year", "EmpEnd"]].copy()
    end = end.rename(columns={"EmpEnd": "emp_lag"})
    g = g.merge(end, on=["fips", "spring_year"], how="left")
    g["nnjf_per_100"] = 100.0 * g["nnjf"].astype(float) / g["emp_lag"].astype(float)
    return g


def build_h9_sum_div_4emp(sy_long: pd.DataFrame, denom: pd.DataFrame) -> pd.DataFrame:
    """Literal sum numerator, denominator = 4 * Q4_lag emp (this is mathematically
    identical to mean(FrmJbLsS)/Q4_lag, but we keep it explicit because the *paper*
    text says nnjf = sum and might be using a per-quarter denominator)."""
    d = sy_long.dropna(subset=["spring_year"]).copy()
    g = d.groupby(["fips", "spring_year"], as_index=False).agg(
        nnjf_sum=("FrmJbLsS", "sum"),
        n_quarters=("FrmJbLsS", "count"),
    )
    g = g[g["n_quarters"] == 4]
    g = g.merge(denom, on=["fips", "spring_year"], how="left")
    g = g.rename(columns={"emp_q4_lag": "emp_lag"})
    g["nnjf"] = g["nnjf_sum"] / 4.0
    g["nnjf_per_100"] = 100.0 * g["nnjf_sum"].astype(float) / (4.0 * g["emp_lag"].astype(float))
    return g


def build_h10_quarterly_rate_then_weighted_med_across_quarters(
    sy_long: pd.DataFrame, denom: pd.DataFrame,
) -> pd.DataFrame:
    """For each county-year, take the weighted MEDIAN per-quarter rate
    (weighting each quarter by 1/EmpS_cq, same scheme as the cross-county median).

    If the paper computed quarterly rates and then took an emp-weighted median across
    *both* counties and quarters in one pool, that's a meaningfully different design.
    Here we still aggregate to county-year first (with within-county weighted median)
    so the cross-county weighting still works the same as the other hypotheses.
    """
    d = sy_long.dropna(subset=["spring_year"]).copy()
    d["q_rate"] = 100.0 * d["FrmJbLsS"].astype(float) / d["EmpS"].astype(float)
    d.loc[~np.isfinite(d["q_rate"]), "q_rate"] = np.nan
    d["q_w"] = 1.0 / d["EmpS"].astype(float)
    d.loc[~np.isfinite(d["q_w"]), "q_w"] = np.nan

    def _wmed(g: pd.DataFrame) -> pd.Series:
        v = g["q_rate"].values
        w = g["q_w"].values
        n_ok = np.isfinite(v) & np.isfinite(w) & (w > 0)
        rate = wq(v, w, 0.5) if n_ok.sum() else np.nan
        cnt = g["FrmJbLsS"].astype(float).mean()
        return pd.Series({"nnjf": cnt, "nnjf_per_100": rate, "n_quarters": int(n_ok.sum())})

    rows = d.groupby(["fips", "spring_year"]).apply(_wmed, include_groups=False).reset_index()
    rows = rows[rows["n_quarters"] >= 3]
    rows = rows.merge(denom, on=["fips", "spring_year"], how="left")
    rows = rows.rename(columns={"emp_q4_lag": "emp_lag"})
    return rows


# -------- main --------

def fmt(stats: dict) -> str:
    lines = []
    name = stats["name"]
    lines.append(f"### {name}")
    lines.append(f"    n_obs = {stats['n_obs']:,}")
    lines.append(f"    pooled weighted median NNJF/100 = {stats['pooled_med']:.3f}   (paper {PAPER_POOLED_MEDIAN})   ratio={stats['pooled_med']/PAPER_POOLED_MEDIAN:.2f}x")
    lines.append(f"    pooled weighted mean   NNJF/100 = {stats['pooled_mean']:.3f}   (paper {PAPER_POOLED_MEAN})   ratio={stats['pooled_mean']/PAPER_POOLED_MEAN:.2f}x")
    for y in (2019, 2020, 2021, 2023):
        tot = stats[f"total_{y}_k"]
        med = stats[f"med_{y}"]
        rt = tot / PAPER_TOTAL_THOUSANDS[y]
        rm = med / PAPER_MEDIAN_PER100[y] if PAPER_MEDIAN_PER100[y] else float("nan")
        lines.append(f"    {y}: total={tot:7.1f}k (paper {PAPER_TOTAL_THOUSANDS[y]}, ratio={rt:.2f}x)   median={med:.3f} (paper {PAPER_MEDIAN_PER100[y]}, ratio={rm:.2f}x)")
    return "\n".join(lines)


def main() -> None:
    print("Loading quarterly data...")
    q = load_quarterly()
    sy_long = to_school_year_long(q)
    denom = emp_q4_lag_table(sy_long)
    print(f"  {len(sy_long):,} county-quarter rows")
    print(f"  {len(denom):,} county-spring_year rows with Q4_lag emp")

    builders = [
        ("H1 q-rate first, mean across 4q", build_h1_qrate_first),
        ("H2 median across 4q", build_h2_median),
        ("H3 trimmed mean (drop max of 4)", build_h3_trimmed_mean),
        ("H4 spring-only (Q1+Q2)", build_h4_spring_only),
        ("H5 sum/person-quarter denom", build_h5_person_quarter_denom),
        ("H6 q-rate first, mean across 3q (Q4lag+Q1+Q2)", build_h6_qrate_first_3q),
        ("H7 mean count / mean(EmpS) denom", build_h7_mean_count_avg_emp_denom),
        ("H8 mean count / EmpEnd(Q4_lag) denom", build_h8_mean_count_empend_denom),
        ("H9 sum / (4 * Q4_lag emp)", build_h9_sum_div_4emp),
        ("H10 within-county weighted median qrate", build_h10_quarterly_rate_then_weighted_med_across_quarters),
    ]

    # Restrict to school years 2002-2024 like the paper
    results = []
    for name, fn in builders:
        out = fn(sy_long, denom)
        out = out[(out["spring_year"] >= 2002) & (out["spring_year"] <= 2024)].copy()
        out["nnjf"] = pd.to_numeric(out["nnjf"], errors="coerce")
        out["emp_lag"] = pd.to_numeric(out["emp_lag"], errors="coerce")
        out["nnjf_per_100"] = pd.to_numeric(out["nnjf_per_100"], errors="coerce")
        # For H5 we want the table-total to use the /4 version so it's comparable
        if "nnjf_for_total" in out.columns:
            out_for_summary = out.copy()
            out_for_summary["nnjf"] = out_for_summary["nnjf_for_total"]
            stats = summarize(name, out_for_summary)
        else:
            stats = summarize(name, out)
        results.append(stats)
        print()
        print(fmt(stats))

    # Save markdown summary
    md_lines = [
        "# Agent investigation: alternative time-aggregation methods for NNJF",
        "",
        "Hypotheses tested in `code/93_agent_aggregation.py`. Paper targets:",
        "",
        "- Table A4 NNJF Total (thousands) 2019 / 2020 / 2021 / 2023: 176.2 / 224.9 / 150.4 / 162.1",
        "- Table A4 NNJF/100 medians:                                  0.43 / 0.51 / 0.31 / 0.40",
        f"- Table A2 pooled NNJF/100 median: {PAPER_POOLED_MEDIAN}",
        f"- Table A2 pooled NNJF/100 mean:   {PAPER_POOLED_MEAN}",
        "",
    ]
    for s in results:
        md_lines.append("## " + s["name"])
        md_lines.append("")
        md_lines.append(f"- n_obs: {s['n_obs']:,}")
        md_lines.append(f"- pooled weighted median NNJF/100: **{s['pooled_med']:.3f}** (paper {PAPER_POOLED_MEDIAN}, ratio {s['pooled_med']/PAPER_POOLED_MEDIAN:.2f}x)")
        md_lines.append(f"- pooled weighted mean NNJF/100:   **{s['pooled_mean']:.3f}** (paper {PAPER_POOLED_MEAN}, ratio {s['pooled_mean']/PAPER_POOLED_MEAN:.2f}x)")
        md_lines.append("")
        md_lines.append("| Year | Total (k) | Paper | Ratio | Median | Paper | Ratio |")
        md_lines.append("|------|-----------|-------|-------|--------|-------|-------|")
        for y in (2019, 2020, 2021, 2023):
            tot = s[f"total_{y}_k"]
            med = s[f"med_{y}"]
            md_lines.append(
                f"| {y} | {tot:.1f} | {PAPER_TOTAL_THOUSANDS[y]} | {tot/PAPER_TOTAL_THOUSANDS[y]:.2f}x "
                f"| {med:.3f} | {PAPER_MEDIAN_PER100[y]} | {med/PAPER_MEDIAN_PER100[y]:.2f}x |"
            )
        md_lines.append("")

    # Cross-year ratio table -- the key consistency check
    md_lines.append("## Cross-year ratio consistency check (median ratio to paper)")
    md_lines.append("")
    md_lines.append("If a single missing scaling factor explains the gap, the per-year ratios")
    md_lines.append("should be ~constant across 2019/2020/2021/2023.")
    md_lines.append("")
    md_lines.append("| Hypothesis | r2019 | r2020 | r2021 | r2023 | sd/mean |")
    md_lines.append("|------------|-------|-------|-------|-------|---------|")
    for s in results:
        ratios = [s[f"med_{y}"] / PAPER_MEDIAN_PER100[y] for y in (2019, 2020, 2021, 2023)]
        cv = float(np.std(ratios) / np.mean(ratios)) if np.mean(ratios) else float("nan")
        md_lines.append(
            f"| {s['name']} | {ratios[0]:.2f}x | {ratios[1]:.2f}x | {ratios[2]:.2f}x | {ratios[3]:.2f}x | {cv:.3f} |"
        )
    md_lines.append("")

    # Conclusion (pick min |log(pooled_ratio)| as best, weighted equally with per-year mean ratio)
    def score(s: dict) -> float:
        pm = s["pooled_med"] / PAPER_POOLED_MEDIAN if s["pooled_med"] else float("inf")
        # geometric distance from 1
        per_year = np.mean([abs(np.log(max(s[f"med_{y}"] / PAPER_MEDIAN_PER100[y], 1e-6))) for y in (2019, 2020, 2021, 2023)])
        pooled_d = abs(np.log(max(pm, 1e-6)))
        return per_year + pooled_d

    best = min(results, key=score)
    md_lines.append("## Best hypothesis")
    md_lines.append("")
    md_lines.append(f"**{best['name']}** has the smallest combined log-distance from paper")
    md_lines.append(f"(pooled median ratio {best['pooled_med']/PAPER_POOLED_MEDIAN:.2f}x).")
    md_lines.append("")

    out_dir = OUTPUT / "reports"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_md = out_dir / "agent_aggregation.md"
    out_md.write_text("\n".join(md_lines))
    print(f"\nWrote {out_md}")


if __name__ == "__main__":
    main()
