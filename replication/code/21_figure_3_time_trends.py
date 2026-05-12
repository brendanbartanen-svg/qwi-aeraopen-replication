"""Figure 3: Education labor market conditions over time.

Panel A: Turnover percent (median, mean, IQR) by year.
Panel B: Leaver count (total) by year.
Panel C: NNJF per 100 employees (median, mean, IQR) by year.
Panel D: NNJF total count by year.

All weighted by inverse FTE (paper's wording).
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from _config import DATA_DERIVED, FIGURES, TABLES


def wq(x, w, q):
    idx = np.argsort(x)
    cw = np.cumsum(w[idx]) / w.sum()
    return x[idx][np.searchsorted(cw, q)]


def main() -> None:
    FIGURES.mkdir(parents=True, exist_ok=True)
    TABLES.mkdir(parents=True, exist_ok=True)
    sy = pd.read_parquet(DATA_DERIVED / "county_school_year_measures.parquet")

    # Yearly stats
    rows = []
    for y, sub in sy.groupby("school_year"):
        valid_t = sub.dropna(subset=["turnover", "emp_lag"])
        valid_t = valid_t[valid_t["emp_lag"] > 0]
        valid_n = sub.dropna(subset=["nnjf_per_100", "emp_lag"])
        valid_n = valid_n[valid_n["emp_lag"] > 0]

        if len(valid_t) > 0:
            t = valid_t["turnover"].astype(float).values
            w_t = (1.0 / valid_t["emp_lag"].astype(float)).values
            t_med = wq(t, w_t, 0.5); t_mean = (t * w_t).sum() / w_t.sum()
            t_p25 = wq(t, w_t, 0.25); t_p75 = wq(t, w_t, 0.75)
            leavers_total = sub["leavers"].astype(float).sum() / 1000  # in thousands
        else:
            t_med = t_mean = t_p25 = t_p75 = leavers_total = np.nan

        if len(valid_n) > 0:
            n_per100 = valid_n["nnjf_per_100"].astype(float).values
            w_n = (1.0 / valid_n["emp_lag"].astype(float)).values
            n_med = wq(n_per100, w_n, 0.5); n_mean = (n_per100 * w_n).sum() / w_n.sum()
            n_p25 = wq(n_per100, w_n, 0.25); n_p75 = wq(n_per100, w_n, 0.75)
            nnjf_total = sub["nnjf"].astype(float).sum() / 1000
        else:
            n_med = n_mean = n_p25 = n_p75 = nnjf_total = np.nan

        rows.append({"year": int(y), "t_med": t_med, "t_mean": t_mean,
                     "t_p25": t_p25, "t_p75": t_p75, "leavers_K": leavers_total,
                     "n_med": n_med, "n_mean": n_mean, "n_p25": n_p25,
                     "n_p75": n_p75, "nnjf_K": nnjf_total})
    yr = pd.DataFrame(rows).set_index("year").sort_index()
    yr.to_csv(TABLES / "appendix_table_A4_my.csv")
    print("Yearly stats:")
    print(yr.round(4).to_string())

    # Plot
    fig, axes = plt.subplots(2, 2, figsize=(13, 9))
    recessions = [(2001.1, 2001.9), (2007.9, 2009.5), (2020.1, 2020.4)]

    # Panel A: Turnover
    ax = axes[0, 0]
    ax.fill_between(yr.index, yr["t_p25"]*100, yr["t_p75"]*100, alpha=0.2, color="gray", label="IQR")
    ax.plot(yr.index, yr["t_med"]*100, "-o", color="black", label="Median")
    ax.plot(yr.index, yr["t_mean"]*100, "--", color="black", label="Mean")
    for r0, r1 in recessions:
        ax.axvspan(r0, r1, alpha=0.15, color="gray")
    ax.set_xlabel("Year (Spring)"); ax.set_ylabel("Educator Turnover %")
    ax.set_title("Panel A. Turnover percent"); ax.legend()
    ax.set_ylim(0, 35)

    # Panel B: Leavers
    ax = axes[0, 1]
    ax.plot(yr.index, yr["leavers_K"]*10, "-o", color="black", label="Leavers")  # scale to match paper's "100Ks"
    for r0, r1 in recessions:
        ax.axvspan(r0, r1, alpha=0.15, color="gray")
    ax.set_xlabel("Year (Spring)"); ax.set_ylabel("Educator Leaver Count (100 Ks)")
    ax.set_title("Panel B. Leaver count")

    # Panel C: NNJF per 100
    ax = axes[1, 0]
    ax.fill_between(yr.index, yr["n_p25"], yr["n_p75"], alpha=0.2, color="gray", label="IQR")
    ax.plot(yr.index, yr["n_med"], "-o", color="black", label="Median")
    ax.plot(yr.index, yr["n_mean"], "--", color="black", label="Mean")
    for r0, r1 in recessions:
        ax.axvspan(r0, r1, alpha=0.15, color="gray")
    ax.set_xlabel("Year (Spring)"); ax.set_ylabel("NNJF per 100 Emps")
    ax.set_title("Panel C. NNJF per 100 employees"); ax.legend()

    # Panel D: NNJF total
    ax = axes[1, 1]
    ax.plot(yr.index, yr["nnjf_K"]*1000, "-o", color="black", label="NNJF")
    for r0, r1 in recessions:
        ax.axvspan(r0, r1, alpha=0.15, color="gray")
    ax.set_xlabel("Year (Spring)"); ax.set_ylabel("NNJF Count")
    ax.set_title("Panel D. NNJF count")

    fig.suptitle("Figure 3. Education labor market conditions over time", fontsize=13)
    fig.tight_layout()
    out_path = FIGURES / "figure_3_time_trends.png"
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    print(f"\nWrote {out_path}")


if __name__ == "__main__":
    main()
