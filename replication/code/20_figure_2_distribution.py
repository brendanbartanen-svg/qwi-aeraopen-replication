"""Figure 2: Distribution of turnover and net-negative job flow.

Panel A: Histogram + boxplot of turnover.
Panel B: Histogram + boxplot of log(NNJF).

The paper says distributions are weighted by the inverse of educator count.
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from _config import DATA_DERIVED, FIGURES, QWI_CURRENT_DIR


def weighted_quantile(values, weights, q):
    """Approximate weighted quantile."""
    sorted_idx = np.argsort(values)
    v = values[sorted_idx]
    w = weights[sorted_idx]
    cw = np.cumsum(w) / w.sum()
    return v[np.searchsorted(cw, q)]


def main() -> None:
    FIGURES.mkdir(parents=True, exist_ok=True)
    sy = pd.read_parquet(DATA_DERIVED / "county_school_year_measures.parquet")

    # Weight by inverse of count of educators (paper's wording)
    valid = sy.dropna(subset=["turnover", "emp_lag"])
    valid = valid[valid["emp_lag"] > 0]
    t = valid["turnover"].astype(float).values
    w_inv = (1.0 / valid["emp_lag"].astype(float)).values

    # NNJF panel — Paper Figure 2 Panel B labels median = 108 (note: Table A2 says 43,
    # an internal paper inconsistency). The figure label matches the SUM of FrmJbLsS
    # over the 4 school-year quarters (NOT averaged, NOT subtracting FrmJbGnS, NOT clipped).
    # We use this measure for the figure to match the paper's plot annotation.
    df_raw = pd.read_parquet(QWI_CURRENT_DIR / "county_sex0_full_2025q2.parquet")
    ss = pd.read_parquet(QWI_CURRENT_DIR / "county_sex0_frmjblss.parquet")
    ss["FrmJbLsS"] = pd.to_numeric(ss["FrmJbLsS"], errors="coerce")
    df_raw = df_raw.merge(ss[["fips","year","quarter","FrmJbLsS"]],
                           on=["fips","year","quarter"], how="left")
    p_fls = df_raw.pivot_table(index=["fips","year"], columns="quarter",
                                values="FrmJbLsS", aggfunc="first")
    p_fls.columns = [f"fls_q{int(c)}" for c in p_fls.columns]
    p_fls = p_fls.reset_index().sort_values(["fips","year"])
    for q in [3, 4]:
        p_fls[f"fls_q{q}_lag"] = p_fls.groupby("fips")[f"fls_q{q}"].shift(1)
    p_fls["nnjf_fig"] = p_fls["fls_q3_lag"] + p_fls["fls_q4_lag"] + p_fls["fls_q1"] + p_fls["fls_q2"]
    p_fls = p_fls.merge(sy[["fips","school_year","emp_lag"]],
                         left_on=["fips","year"], right_on=["fips","school_year"], how="inner")
    p_fls = p_fls[(p_fls["year"] >= 2001) & (p_fls["year"] <= 2024)]

    valid_n = p_fls.dropna(subset=["nnjf_fig", "emp_lag"])
    valid_n = valid_n[(valid_n["emp_lag"] > 0) & (valid_n["nnjf_fig"] > 0)]
    n = valid_n["nnjf_fig"].astype(float).values
    w_inv_n = (1.0 / valid_n["emp_lag"].astype(float)).values

    fig, axes = plt.subplots(2, 2, figsize=(11, 9))

    # Panel A1: Turnover histogram
    ax = axes[0, 0]
    ax.hist(t, bins=80, range=(0, 1), weights=w_inv, density=True, color="lightgray", edgecolor="black")
    med = weighted_quantile(t, w_inv, 0.5)
    p99 = weighted_quantile(t, w_inv, 0.99)
    ax.axvline(med, ls="--", color="black", lw=1)
    ax.axvline(p99, ls="--", color="black", lw=1)
    ax.text(med, ax.get_ylim()[1] * 0.95, f"Median={med:.2%}", ha="left", va="top", fontsize=8,
            bbox=dict(facecolor="white", edgecolor="black", boxstyle="round,pad=0.2"))
    ax.text(p99, ax.get_ylim()[1] * 0.80, f"99th Pct={p99:.2%}", ha="right", va="top", fontsize=8,
            bbox=dict(facecolor="white", edgecolor="black", boxstyle="round,pad=0.2"))
    ax.set_xlabel("Educator Turnover")
    ax.set_ylabel("Density")
    ax.set_xlim(0, 1)
    ax.set_title("Panel A. Turnover (histogram)")

    # Panel A2: Turnover boxplot
    ax = axes[0, 1]
    ax.boxplot(t, vert=True, widths=0.4, showfliers=True)
    ax.set_ylabel("Educator Turnover")
    ax.set_ylim(0, 1)
    ax.set_xticks([])
    ax.set_title("Panel A. Turnover (boxplot)")

    # Panel B1: log(NNJF) histogram — paper uses UNWEIGHTED for the figure
    # (Table A2's median=43 is weighted by 1/emp; Figure 2's annotation median=108
    # is unweighted). We reproduce the figure faithfully (unweighted).
    ax = axes[1, 0]
    ax.hist(np.log(n), bins=80, density=True, color="lightgray", edgecolor="black")
    med_n = np.median(n)
    p99_n = np.percentile(n, 99)
    ax.axvline(np.log(med_n), ls="--", color="black", lw=1)
    ax.axvline(np.log(p99_n), ls="--", color="black", lw=1)
    ax.text(np.log(med_n), ax.get_ylim()[1] * 0.95, f"Median={med_n:.0f}", ha="left", va="top", fontsize=8,
            bbox=dict(facecolor="white", edgecolor="black", boxstyle="round,pad=0.2"))
    ax.text(np.log(p99_n), ax.get_ylim()[1] * 0.80, f"99th Pct={p99_n:.0f}", ha="right", va="top", fontsize=8,
            bbox=dict(facecolor="white", edgecolor="black", boxstyle="round,pad=0.2"))
    ax.set_xlabel("Educator Net-Negative Job Flow (log)")
    ax.set_ylabel("Density")
    ax.set_title("Panel B. Net-negative job flow (histogram)")

    # Panel B2: NNJF boxplot
    ax = axes[1, 1]
    ax.boxplot(np.log(n), vert=True, widths=0.4, showfliers=True)
    ax.set_ylabel("Educator NNJF (log)")
    ax.set_xticks([])
    ax.set_title("Panel B. Net-negative job flow (boxplot)")

    fig.suptitle("Figure 2. Distribution of education labor market measures", fontsize=13)
    fig.tight_layout()
    out_path = FIGURES / "figure_2_distribution.png"
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    print(f"Wrote {out_path}")

    # Print stats for comparison to paper Appendix Table A2
    print(f"\n  Weighted (1/emp) turnover:")
    print(f"    median = {weighted_quantile(t, w_inv, 0.5):.4f}  (paper: 0.251)")
    print(f"    mean   = {(t * w_inv).sum() / w_inv.sum():.4f}  (paper: 0.261)")
    print(f"    p25    = {weighted_quantile(t, w_inv, 0.25):.4f}  (paper: 0.204)")
    print(f"    p75    = {weighted_quantile(t, w_inv, 0.75):.4f}  (paper: 0.305)")
    print(f"    p99    = {weighted_quantile(t, w_inv, 0.99):.4f}  (paper: 0.5249)")

    print(f"\n  Weighted (1/emp) NNJF (count, not per-100):")
    print(f"    median = {weighted_quantile(n, w_inv_n, 0.5):.1f}  (paper text: 43; paper figure: 108)")
    print(f"    mean   = {(n * w_inv_n).sum() / w_inv_n.sum():.1f}  (paper: 73.3)")
    print(f"    p25    = {weighted_quantile(n, w_inv_n, 0.25):.1f}  (paper: 24)")
    print(f"    p75    = {weighted_quantile(n, w_inv_n, 0.75):.1f}  (paper: 77)")

    # Also try positive emp weighting
    w_pos = valid["emp_lag"].astype(float).values
    print(f"\n  Weighted (positive emp) turnover:")
    print(f"    median = {weighted_quantile(t, w_pos, 0.5):.4f}")
    print(f"    mean   = {(t * w_pos).sum() / w_pos.sum():.4f}")

    print(f"\n  Unweighted turnover:")
    print(f"    median = {np.median(t):.4f}")
    print(f"    mean   = {t.mean():.4f}")


if __name__ == "__main__":
    main()
