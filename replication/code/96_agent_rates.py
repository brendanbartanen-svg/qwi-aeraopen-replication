"""Test 10+ hypotheses about whether the paper used QWI built-in rate variables
to construct NNJF/100, rather than counts/Emp.

Paper target values (Appendix Table A2, weighted by 1/Emp):
  NNJF/100 pooled: median=1.080, mean=3.32, p25=0.53, p75=2.6, SD=9.30
Paper Table A4 (year-by-year medians):
  2019: 0.43, 2020: 0.51, 2021: 0.31, 2023: 0.40
Paper Table A4 (year-by-year means):
  2019: 0.73, 2020: 0.93, 2021: 0.62, 2023: 0.69

Naive baseline (current pipeline): avg(FrmJbLsS over 4 sy-q) / emp_q4_lag * 100
yields weighted median 2.96, mean 5.30 — uniformly ~2.7× too big.

Hypotheses tested here (all weighted by 1/Emp):

H1: avg of per-quarter FrmJbLsS/EmpS rate (×100) across 4 sy-quarters
    -- "firm job losses to stable employment per 100 stably employed"
H2: SUM of per-quarter FrmJbLsS/EmpS rates (×100) across 4 sy-quarters
H3: sum(FrmJbLsS)/sum(EmpS)*100 (ratio-of-sums) per county-school-year
H4: SepBegR (built-in QWI Beginning-of-Quarter Separation Rate), averaged over 4 sy-q
H5: HirAEndReplr (built-in Replacement Hiring Rate), averaged over 4 sy-q
H6: TurnOvrS (built-in Stable Turnover Rate), averaged over 4 sy-q
H7: Sep/Emp*100 averaged over 4 sy-q
H8: NNJF/100 using EmpEnd of prior Q4 (vs Emp) as denominator
H9: per-quarter FrmJbLsS/EmpEnd rate (×100) averaged over 4 sy-q
H10: POOLED across all county-quarters (NOT aggregated to school-year):
     per-quarter FrmJbLsS/Emp rate (×100). The paper's "pooled" Table A2
     statistic may operate on the quarter, not on the school-year.
H11: Same as H10 but with FrmJbLs/EmpTotal
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from _config import DATA_DERIVED, OUTPUT, QWI_CURRENT_DIR
from _qwi_client import US_STATE_FIPS, pull_state_chunked_by_years


# ---------------------------------------------------------------------------
# Weighted descriptive stats (1/emp weighting like the paper)
# ---------------------------------------------------------------------------

def weighted_quantile(values: np.ndarray, weights: np.ndarray, q: float) -> float:
    v = np.asarray(values, dtype=float); w = np.asarray(weights, dtype=float)
    keep = np.isfinite(v) & np.isfinite(w) & (w > 0)
    v = v[keep]; w = w[keep]
    if len(v) == 0:
        return np.nan
    i = np.argsort(v)
    c = np.cumsum(w[i]) / w.sum()
    return float(v[i][np.searchsorted(c, q)])


def weighted_mean(values: np.ndarray, weights: np.ndarray) -> float:
    v = np.asarray(values, dtype=float); w = np.asarray(weights, dtype=float)
    keep = np.isfinite(v) & np.isfinite(w) & (w > 0)
    v = v[keep]; w = w[keep]
    return float((v * w).sum() / w.sum()) if len(v) else np.nan


def weighted_sd(values: np.ndarray, weights: np.ndarray) -> float:
    v = np.asarray(values, dtype=float); w = np.asarray(weights, dtype=float)
    keep = np.isfinite(v) & np.isfinite(w) & (w > 0)
    v = v[keep]; w = w[keep]
    if len(v) == 0:
        return np.nan
    m = (v * w).sum() / w.sum()
    return float(np.sqrt((w * (v - m) ** 2).sum() / w.sum()))


def describe_weighted(values, weights):
    return {
        "n": int(np.sum(np.isfinite(np.asarray(values, dtype=float)) & (np.asarray(weights, dtype=float) > 0))),
        "p25": weighted_quantile(values, weights, 0.25),
        "p50": weighted_quantile(values, weights, 0.50),
        "p75": weighted_quantile(values, weights, 0.75),
        "mean": weighted_mean(values, weights),
        "sd": weighted_sd(values, weights),
    }


# ---------------------------------------------------------------------------
# Load data & pull rate panel (cached)
# ---------------------------------------------------------------------------

def load_base_panel() -> pd.DataFrame:
    main_path = QWI_CURRENT_DIR / "county_sex0_full_2025q2.parquet"
    df = pd.read_parquet(main_path)
    for c in ("EmpTotal", "Emp", "HirN", "FrmJbLs"):
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    ss = pd.read_parquet(QWI_CURRENT_DIR / "county_sex0_frmjblss.parquet")
    for c in ("FrmJbLsS", "FrmJbGnS", "EmpS", "EmpEnd"):
        if c in ss.columns:
            ss[c] = pd.to_numeric(ss[c], errors="coerce")
    return df.merge(
        ss[["fips", "year", "quarter", "FrmJbLsS", "FrmJbGnS", "EmpS", "EmpEnd"]],
        on=["fips", "year", "quarter"], how="left",
    )


def pull_rate_panel() -> pd.DataFrame:
    out_path = QWI_CURRENT_DIR / "county_sex0_rates.parquet"
    if out_path.exists():
        return pd.read_parquet(out_path)

    rate_vars_a = ("SepBegR", "HirAEndR", "HirAEndReplr")
    rate_vars_b = ("TurnOvrS", "Sep", "EmpS")
    all_rows: list[pd.DataFrame] = []
    t0 = time.time()
    for i, st in enumerate(US_STATE_FIPS, 1):
        for vars_ in (rate_vars_a, rate_vars_b):
            d = pull_state_chunked_by_years(
                endpoint="sa", state_fips=st, get_vars=vars_,
                extra_params={"sex": "0"},
                start_year=2017, end_quarter="2024-Q2", chunk_years=4,
            )
            all_rows.append(d)
        if i % 10 == 0:
            print(f"  [{i:2d}/51] elapsed={time.time()-t0:.1f}s")

    raw = pd.concat(all_rows, ignore_index=True)
    raw["year"] = raw["time"].str.split("-Q").str[0].astype(int)
    raw["quarter"] = raw["time"].str.split("-Q").str[1].astype(int)
    raw["fips"] = raw["state"].astype(str) + raw["county"].astype(str)
    cols_a = [c for c in raw.columns if c in ("SepBegR", "HirAEndR", "HirAEndReplr")]
    cols_b = [c for c in raw.columns if c in ("TurnOvrS", "Sep", "EmpS")]
    for c in cols_a + cols_b:
        raw[c] = pd.to_numeric(raw[c], errors="coerce")
    rates = raw.groupby(["fips", "year", "quarter"], as_index=False).agg(
        {c: "first" for c in cols_a + cols_b}
    )
    rates.to_parquet(out_path, index=False)
    return rates


# ---------------------------------------------------------------------------
# Build school-year wide structure
# ---------------------------------------------------------------------------

def build_school_year_measures(panel: pd.DataFrame) -> pd.DataFrame:
    p = panel.copy()
    p["r_frmjblss_emps_pct"] = 100.0 * p["FrmJbLsS"] / p["EmpS"]
    p["r_frmjblss_empend_pct"] = 100.0 * p["FrmJbLsS"] / p["EmpEnd"]
    p["r_frmjbls_emptotal_pct"] = 100.0 * p["FrmJbLs"] / p["EmpTotal"]
    if "Sep" in p.columns:
        p["r_sep_emp_pct"] = 100.0 * p["Sep"] / p["Emp"]
    p = p.sort_values(["fips", "year", "quarter"]).reset_index(drop=True)
    p["sy"] = np.where(p["quarter"].isin([3, 4]), p["year"] + 1, p["year"])

    def pivot_one(col: str, prefix: str) -> pd.DataFrame:
        sub = p[["fips", "sy", "quarter", col]].copy()
        return sub.pivot_table(index=["fips", "sy"], columns="quarter",
                                values=col, aggfunc="first").rename(
            columns=lambda q: f"{prefix}_q{int(q)}"
        )

    pieces = []
    cols = [
        ("EmpTotal", "emp"), ("Emp", "empbeg"), ("EmpS", "emps"),
        ("EmpEnd", "empend"), ("FrmJbLsS", "fjs"), ("FrmJbLs", "fj"),
        ("r_frmjblss_emps_pct", "rss"), ("r_frmjblss_empend_pct", "rse"),
        ("r_frmjbls_emptotal_pct", "rfe"), ("r_sep_emp_pct", "rsep"),
        ("SepBegR", "sepbegR"), ("HirAEndR", "hirR"),
        ("HirAEndReplr", "replR"), ("TurnOvrS", "turnS"),
    ]
    for col, prefix in cols:
        if col in p.columns:
            pieces.append(pivot_one(col, prefix))
    wide = pd.concat(pieces, axis=1).reset_index()
    required = ["emp_q1", "emp_q2", "emp_q3", "emp_q4"]
    return wide.dropna(subset=required)


def compute_hypotheses(sy: pd.DataFrame) -> pd.DataFrame:
    h = pd.DataFrame({"fips": sy["fips"], "sy": sy["sy"], "emp_lag": sy["empbeg_q4"]})

    def have(*cs): return all(c in sy.columns for c in cs)

    if have("rss_q1","rss_q2","rss_q3","rss_q4"):
        h["H1_FJSEmpS_rate_avg"] = sy[["rss_q3","rss_q4","rss_q1","rss_q2"]].mean(axis=1)
        h["H2_FJSEmpS_rate_sum"] = sy[["rss_q3","rss_q4","rss_q1","rss_q2"]].sum(axis=1)
    if have("fjs_q1","fjs_q2","fjs_q3","fjs_q4","emps_q1","emps_q2","emps_q3","emps_q4"):
        num = sy[["fjs_q3","fjs_q4","fjs_q1","fjs_q2"]].sum(axis=1)
        den = sy[["emps_q3","emps_q4","emps_q1","emps_q2"]].sum(axis=1)
        h["H3_FJSEmpS_ratio_of_sums"] = 100.0 * num / den
    if have("sepbegR_q1","sepbegR_q2","sepbegR_q3","sepbegR_q4"):
        h["H4_SepBegR_avg"] = sy[["sepbegR_q3","sepbegR_q4","sepbegR_q1","sepbegR_q2"]].mean(axis=1)
    if have("replR_q1","replR_q2","replR_q3","replR_q4"):
        h["H5_HirAEndReplr_avg"] = sy[["replR_q3","replR_q4","replR_q1","replR_q2"]].mean(axis=1)
    if have("turnS_q1","turnS_q2","turnS_q3","turnS_q4"):
        h["H6_TurnOvrS_avg"] = sy[["turnS_q3","turnS_q4","turnS_q1","turnS_q2"]].mean(axis=1)
    if have("rsep_q1","rsep_q2","rsep_q3","rsep_q4"):
        h["H7_SepEmp_rate_avg"] = sy[["rsep_q3","rsep_q4","rsep_q1","rsep_q2"]].mean(axis=1)
    if have("fjs_q1","fjs_q2","fjs_q3","fjs_q4","empend_q4"):
        h["H8_avgFJS_over_EmpEnd_q4"] = 100.0 * sy[["fjs_q3","fjs_q4","fjs_q1","fjs_q2"]].mean(axis=1) / sy["empend_q4"]
    if have("rse_q1","rse_q2","rse_q3","rse_q4"):
        h["H9_FJSEmpEnd_rate_avg"] = sy[["rse_q3","rse_q4","rse_q1","rse_q2"]].mean(axis=1)
    # H14: 100 * avg(FJS over 4 sy-q) / sum(EmpTotal over 4 sy-q). Best match to paper Table A4 means.
    if have("fjs_q1","fjs_q2","fjs_q3","fjs_q4","emp_q1","emp_q2","emp_q3","emp_q4"):
        num = sy[["fjs_q3","fjs_q4","fjs_q1","fjs_q2"]].mean(axis=1)
        den = sy[["emp_q3","emp_q4","emp_q1","emp_q2"]].sum(axis=1)
        h["H14_avgFJS_over_sumEmpTotal4q"] = 100.0 * num / den
    return h


def pooled_quarter_hypotheses(panel: pd.DataFrame) -> dict:
    """H10–H11: pool across all county-quarters (not aggregated by school-year).
    Returned dict has keys keyed to hypothesis names; each value is the descriptive dict."""
    p = panel.copy()
    p["sy"] = np.where(p["quarter"].isin([3, 4]), p["year"] + 1, p["year"])
    sub = p[(p["sy"] >= 2002) & (p["sy"] <= 2024)].copy()
    out = {}

    specs = [
        ("H10_FJSEmp_pooled_quarter",
         100.0 * sub["FrmJbLsS"] / sub["Emp"], sub["Emp"], sub["sy"]),
        ("H11_FJEmpTotal_pooled_quarter",
         100.0 * sub["FrmJbLs"] / sub["EmpTotal"], sub["EmpTotal"], sub["sy"]),
        ("H12_FJSEmpEnd_pooled_quarter",
         100.0 * sub["FrmJbLsS"] / sub["EmpEnd"], sub["EmpEnd"], sub["sy"]),
        ("H13_FJSEmpS_pooled_quarter",
         100.0 * sub["FrmJbLsS"] / sub["EmpS"], sub["EmpS"], sub["sy"]),
    ]
    for name, rate, denom, sy_col in specs:
        v = rate.values
        w = 1.0 / np.asarray(denom.values, dtype=float)
        pooled = describe_weighted(v, w)
        by_year = {}
        for yr in (2019, 2020, 2021, 2023):
            mask = (sy_col == yr).values
            if mask.sum() == 0:
                continue
            by_year[yr] = {"p50": weighted_quantile(v[mask], w[mask], 0.5),
                           "mean": weighted_mean(v[mask], w[mask])}
        out[name] = {"pooled": pooled, "by_year": by_year}
    return out


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------

PAPER_TARGETS = {
    "pooled":  {"p25": 0.53, "p50": 1.080, "p75": 2.6, "mean": 3.32, "sd": 9.30},
    "by_year": {2019: {"p50": 0.43, "mean": 0.73},
                2020: {"p50": 0.51, "mean": 0.93},
                2021: {"p50": 0.31, "mean": 0.62},
                2023: {"p50": 0.40, "mean": 0.69}},
}


def evaluate(h: pd.DataFrame, var: str) -> dict:
    valid = h.dropna(subset=[var, "emp_lag"])
    valid = valid[valid["emp_lag"] > 0]
    v = valid[var].astype(float).values
    w = 1.0 / valid["emp_lag"].astype(float).values
    out = {"pooled": describe_weighted(v, w), "by_year": {}}
    for yr in (2019, 2020, 2021, 2023):
        sub = valid[valid["sy"] == yr]
        if len(sub) == 0:
            continue
        vy = sub[var].astype(float).values
        wy = 1.0 / sub["emp_lag"].astype(float).values
        out["by_year"][yr] = {"p50": weighted_quantile(vy, wy, 0.5),
                              "mean": weighted_mean(vy, wy)}
    return out


def main() -> None:
    print("=" * 70)
    print("Hypothesis testing: QWI built-in rate variables for NNJF/100")
    print("=" * 70)
    base = load_base_panel()
    print(f"Base panel: {len(base):,} county-quarter rows")

    rates = pull_rate_panel()
    rates_keep = [c for c in rates.columns if c in
                  ("fips","year","quarter","SepBegR","HirAEndR","HirAEndReplr","TurnOvrS","Sep","EmpS")]
    rates2 = rates[rates_keep].rename(columns={"EmpS": "EmpS_rate"})
    full = base.merge(rates2, on=["fips","year","quarter"], how="left")

    # School-year (H1-H9)
    sy = build_school_year_measures(full)
    h = compute_hypotheses(sy)
    h = h[(h["sy"] >= 2002) & (h["sy"] <= 2024)]
    print(f"School-year hypothesis matrix: {len(h):,} rows")

    sy_results = {col: evaluate(h, col) for col in h.columns if col.startswith("H")}

    # Pooled-quarter (H10-H13) — does NOT use school-year aggregation
    pooled_results = pooled_quarter_hypotheses(base)

    all_results = {**sy_results, **pooled_results}

    # ---------- Report ----------
    target = PAPER_TARGETS
    lines = []
    lines.append("# Agent rates: hypothesis tests for NNJF/100 specification")
    lines.append("")
    lines.append("## Paper target (Table A2, 1/Emp weighted, pooled)")
    lines.append("- p25=0.53, p50=1.080, p75=2.6, mean=3.32, sd=9.30")
    lines.append("- 2019: p50=0.43, mean=0.73 / 2020: 0.51, 0.93 / 2021: 0.31, 0.62 / 2023: 0.40, 0.69")
    lines.append("")
    lines.append("## Naive baseline (current pipeline)")
    lines.append("`100 * avg(FrmJbLsS over 4 sy-quarters) / emp_q4_lag` → median 2.96, mean 5.30 (~2.7× too big).")
    lines.append("")
    lines.append("## Hypothesis results (school-year and pooled-quarter)")
    lines.append("")
    lines.append("| Hypothesis | p25 | p50 | p75 | mean | sd | 2019 med | 2020 med | 2021 med | 2023 med |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
    lines.append(
        f"| **PAPER** | {target['pooled']['p25']:.2f} | **{target['pooled']['p50']:.3f}** | "
        f"{target['pooled']['p75']:.2f} | {target['pooled']['mean']:.2f} | "
        f"{target['pooled']['sd']:.2f} | "
        f"{target['by_year'][2019]['p50']:.2f} | {target['by_year'][2020]['p50']:.2f} | "
        f"{target['by_year'][2021]['p50']:.2f} | {target['by_year'][2023]['p50']:.2f} |"
    )

    def fmt_row(name, r):
        p = r["pooled"]; by = r["by_year"]
        def g(yr):
            return f"{by.get(yr, {}).get('p50', np.nan):.2f}" if yr in by else "—"
        return (f"| {name} | {p['p25']:.2f} | {p['p50']:.3f} | {p['p75']:.2f} | "
                f"{p['mean']:.2f} | {p['sd']:.2f} | "
                f"{g(2019)} | {g(2020)} | {g(2021)} | {g(2023)} |")

    for name, r in all_results.items():
        lines.append(fmt_row(name, r))
        p = r["pooled"]
        print(f"\n{name}: p50={p['p50']:.3f} mean={p['mean']:.2f} sd={p['sd']:.2f} "
              f"(target 1.08 / 3.32 / 9.30)")

    # Score
    def score(r):
        p = r["pooled"]
        if not np.isfinite(p["p50"]) or p["p50"] <= 0: return np.inf
        if not np.isfinite(p["mean"]) or p["mean"] <= 0: return np.inf
        return float(np.sqrt(np.log(p["p50"]/target["pooled"]["p50"])**2
                             + np.log(p["mean"]/target["pooled"]["mean"])**2))

    ranked = sorted(all_results.items(), key=lambda kv: score(kv[1]))
    lines.append("")
    lines.append("## Ranked by closeness to paper (log-distance in pooled p50 & mean)")
    lines.append("")
    lines.append("| Rank | Hypothesis | log-distance |")
    lines.append("|---:|---|---:|")
    for i, (name, r) in enumerate(ranked, 1):
        lines.append(f"| {i} | {name} | {score(r):.3f} |")

    lines.append("")
    lines.append("## Conclusion")
    lines.append("")
    lines.append("**The QWI built-in rate variables `SepBegR`, `HirAEndR`, `HirAEndReplr`, "
                 "`TurnOvrS` do NOT close the 2.3× gap.** They are too small (decimal "
                 "fractions, median 0.04-0.08) — over 10× *smaller* than paper's 1.08.")
    lines.append("")
    lines.append("**However, H10 (pooled per-county-quarter FrmJbLsS/Emp rate) IS within "
                 "~25% of paper's pooled NNJF/100 distribution.** This suggests the paper's "
                 "Appendix Table A2 \"pooled\" statistic may be computed across "
                 "**county-quarters**, not the school-year-aggregated `NNJF/100` that Eq 3 "
                 "would imply. Per-quarter rate × 100 already produces magnitudes "
                 "matching p50≈1.08.")
    lines.append("")
    lines.append("**A consistent reading**: Paper computes school-year NNJF *count* as "
                 "Eq 3 (sum of 4 quarters of FrmJbLsS — matches Table A2's median count of 43 "
                 "and total 224.9K in 2019-20 ✓). But for NNJF/100, paper might use the "
                 "per-quarter rate, not (school-year sum)/(Q4 lag emp) ×100.")
    lines.append("")
    lines.append("**Caveat**: Even H10 still has p50=0.795 (vs paper 1.08) — close but off by "
                 "~25%. Paper's Table A4 year-by-year medians (0.31-0.51) are still smaller than "
                 "anything I produce. Table A8 (state-level pandemic) shows NNJF/100 medians of "
                 "6-37, suggesting heterogeneity in the per-state aggregation that does not "
                 "match Table A2's reported 1.08 median. The internal inconsistency between "
                 "Table A2 (p50=1.08) and Table A8 (per-state p50≈7-15) is notable.")

    out_md = OUTPUT / "reports" / "agent_rates.md"
    out_md.write_text("\n".join(lines) + "\n")
    print(f"\nWrote {out_md}")

    # CSV
    rows = []
    for name, r in all_results.items():
        rows.append({
            "hypothesis": name,
            **{f"pool_{k}": v for k, v in r["pooled"].items()},
            **{f"y{yr}_p50": r["by_year"].get(yr, {}).get("p50", np.nan)
               for yr in (2019,2020,2021,2023)},
            **{f"y{yr}_mean": r["by_year"].get(yr, {}).get("mean", np.nan)
               for yr in (2019,2020,2021,2023)},
        })
    out_csv = OUTPUT / "tables" / "agent_rates_results.csv"
    pd.DataFrame(rows).to_csv(out_csv, index=False)
    print(f"Wrote {out_csv}")


if __name__ == "__main__":
    main()
