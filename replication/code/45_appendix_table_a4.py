"""Reproduce Appendix Table A4 — Labor Market Measures by Year.

Paper columns:
  Year | Turnover Mean | Turnover Median | NNJF Per 100 Mean | NNJF Per 100 Median | NNJF Total

Methodology per authors' Stata code:
  - Turnover Mean/Median: weighted by `1/emp_lag` (proxy for paper's `1/fte`)
  - NNJF Per 100 Mean/Median: NNJF/100 weighted by 1/emp_lag
       (NB: "Per 100" here is misleading — it's just `(sum FrmJbLsS over 4Q)/100`,
        not a per-100-employees rate; see author_code/AUTHOR_CODE_FINDINGS.md)
  - NNJF Total: Stata-style `collapse (sum) job_destruct [aw=weight]`,
       i.e., sum(x_i * w_i * N / sum(w_j)) — see _config.stata_aweight_sum.

Replace `1/emp_lag` with `1/fte_elsi` once ELSI is integrated to match the paper exactly.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from _config import (
    DATA_DERIVED, OUTPUT,
    stata_aweight_sum, stata_aweight_mean, stata_aweight_quantile,
)


# Paper Table A4 (verbatim from supplementary appendix p8)
PAPER_A4 = {
    2001: (26.6, 26.4, 0.65, 0.40, 120.6),
    2002: (29.2, 28.1, 0.68, 0.39, 145.1),
    2003: (28.9, 26.8, 0.71, 0.42, 161.8),
    2004: (26.7, 26.0, 0.73, 0.43, 171.1),
    2005: (27.2, 26.1, 0.71, 0.39, 172.5),
    2006: (27.3, 26.2, 0.74, 0.43, 179.0),
    2007: (27.6, 26.4, 0.80, 0.48, 192.8),
    2008: (27.9, 26.4, 0.77, 0.46, 185.8),
    2009: (26.5, 25.3, 0.74, 0.47, 180.0),
    2010: (25.5, 23.6, 0.74, 0.43, 180.1),
    2011: (24.1, 23.0, 0.82, 0.50, 198.7),
    2012: (24.5, 23.2, 0.78, 0.47, 188.8),
    2013: (26.3, 24.8, 0.75, 0.45, 181.8),
    2014: (25.2, 24.0, 0.76, 0.45, 185.0),
    2015: (25.3, 24.1, 0.75, 0.44, 182.9),
    2016: (25.2, 24.1, 0.76, 0.45, 184.7),
    2017: (24.4, 23.3, 0.71, 0.42, 171.4),
    2018: (24.3, 23.4, 0.73, 0.43, 176.3),
    2019: (24.1, 23.3, 0.73, 0.43, 176.2),
    2020: (29.7, 28.3, 0.93, 0.51, 224.9),
    2021: (20.7, 20.3, 0.62, 0.31, 150.4),
    2022: (27.5, 27.1, 0.61, 0.34, 144.1),
    2023: (27.2, 26.6, 0.69, 0.40, 162.1),
    2024: (25.9, 25.8, 0.67, 0.40, 138.6),
}


def main() -> None:
    sy = pd.read_parquet(DATA_DERIVED / "county_school_year_measures.parquet")
    sy = sy[(sy["school_year"] >= 2001) & (sy["school_year"] <= 2024)].copy()
    # Stata uses 1/fte; we proxy with 1/emp_lag until ELSI is integrated.
    sy = sy.dropna(subset=["emp_lag"])
    sy = sy[sy["emp_lag"] > 0]
    sy["w"] = 1.0 / sy["emp_lag"].astype(float)
    # NNJF / 100 for the "Per 100" columns (just rescaling per authors' code)
    sy["nnjf_div100"] = sy["nnjf"].astype(float) / 100.0

    rows = []
    rows.append("# Appendix Table A4 — Labor Market Measures by Year (v2, authors' formulas)")
    rows.append("")
    rows.append("Format per cell: mine / **paper**")
    rows.append("")
    rows.append("Weighting: 1/emp_lag (proxy for 1/FTE_ELSI; switch when ELSI is integrated).")
    rows.append("NNJF formula: sum(FrmJbLsS) over 4 school-year quarters (Q3_lag+Q4_lag+Q1+Q2).")
    rows.append("NNJF Total: Stata-style aweight sum (see _config.stata_aweight_sum).")
    rows.append("")
    rows.append("| Year | Turnover Mean | Turnover Median | NNJF/100 Mean | NNJF/100 Median | NNJF Total (thousands) |")
    rows.append("|---|---|---|---|---|---|")

    err = {"t_mean": 0, "t_med": 0, "p_mean": 0, "p_med": 0, "tot": 0}
    nyr = 0
    for y in sorted(PAPER_A4):
        sub = sy[sy["school_year"] == y]
        sub_t = sub.dropna(subset=["turnover"])
        sub_n = sub.dropna(subset=["nnjf"])
        if len(sub_t) == 0 or len(sub_n) == 0:
            continue

        t = sub_t["turnover"].values
        w_t = sub_t["w"].values
        n100 = sub_n["nnjf_div100"].values
        w_n = sub_n["w"].values
        nnjf_count = sub_n["nnjf"].values

        my_t_mean = stata_aweight_mean(t, w_t) * 100
        my_t_med = stata_aweight_quantile(t, w_t, 0.5) * 100
        my_p_mean = stata_aweight_mean(n100, w_n)
        my_p_med = stata_aweight_quantile(n100, w_n, 0.5)
        my_total_k = stata_aweight_sum(nnjf_count, w_n) / 1000

        p_t_mean, p_t_med, p_p_mean, p_p_med, p_total_k = PAPER_A4[y]
        rows.append(
            f"| {y} | {my_t_mean:.1f}% / **{p_t_mean:.1f}%** "
            f"| {my_t_med:.1f}% / **{p_t_med:.1f}%** "
            f"| {my_p_mean:.2f} / **{p_p_mean:.2f}** "
            f"| {my_p_med:.2f} / **{p_p_med:.2f}** "
            f"| {my_total_k:.1f} / **{p_total_k:.1f}** |"
        )
        err["t_mean"] += abs(my_t_mean - p_t_mean)
        err["t_med"] += abs(my_t_med - p_t_med)
        err["p_mean"] += abs(my_p_mean - p_p_mean)
        err["p_med"] += abs(my_p_med - p_p_med)
        err["tot"] += abs(my_total_k - p_total_k)
        nyr += 1

    rows.append("")
    rows.append("## Mean absolute error vs paper")
    rows.append("")
    rows.append(f"- Turnover Mean:    {err['t_mean']/nyr:.2f} pp")
    rows.append(f"- Turnover Median:  {err['t_med']/nyr:.2f} pp")
    rows.append(f"- NNJF/100 Mean:    {err['p_mean']/nyr:.3f}")
    rows.append(f"- NNJF/100 Median:  {err['p_med']/nyr:.3f}")
    rows.append(f"- NNJF Total:       {err['tot']/nyr:.1f}K")

    out_path = OUTPUT / "tables" / "appendix_table_A4_my.md"
    out_path.write_text("\n".join(rows))
    print(f"Wrote {out_path}")
    print("\nMean absolute errors vs paper Table A4:")
    print(f"  Turnover Mean:    {err['t_mean']/nyr:.2f} pp (target <2.0)")
    print(f"  Turnover Median:  {err['t_med']/nyr:.2f} pp (target <2.0)")
    print(f"  NNJF/100 Mean:    {err['p_mean']/nyr:.3f} (target <0.1)")
    print(f"  NNJF/100 Median:  {err['p_med']/nyr:.3f} (target <0.1)")
    print(f"  NNJF Total:       {err['tot']/nyr:.1f}K (target <20K)")


if __name__ == "__main__":
    main()
