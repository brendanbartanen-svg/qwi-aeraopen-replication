"""Reproduce Appendix Table A7 — NNJF per 100 by employee characteristic × year.

Paper Table A7 (NNJF per 100): columns White, Non-White, Non-Hispanic, Hispanic, Bachelors, Non-Bachelors

For each (state, year, group): compute NNJF and NNJF/100, then take median across groups
(per the method that worked for Table A5/A6).
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from _config import OUTPUT, QWI_CURRENT_DIR


def state_yearly_nnjf(df_sub: pd.DataFrame, base_emp_df: pd.DataFrame | None = None) -> pd.DataFrame:
    """Build state × school-year NNJF/100 measures for one group's data.

    `df_sub` has FrmJbLsS, FrmJbGnS at state-quarter level.
    `base_emp_df` (optional) has EmpTotal at state-quarter level (for the denominator).
    If None, we use FrmJbLsS-side data which only has EmpS available.
    """
    df = df_sub.copy()
    for c in ("FrmJbLsS", "FrmJbGnS"):
        df[c] = pd.to_numeric(df[c], errors="coerce")
    # Pivot
    p_fls = df.pivot_table(index=["state","year"], columns="quarter", values="FrmJbLsS", aggfunc="first")
    p_fls.columns = [f"fls_q{int(c)}" for c in p_fls.columns]
    p_fgs = df.pivot_table(index=["state","year"], columns="quarter", values="FrmJbGnS", aggfunc="first")
    p_fgs.columns = [f"fgs_q{int(c)}" for c in p_fgs.columns]
    pieces = [p_fls, p_fgs]
    if base_emp_df is not None:
        base = base_emp_df.copy()
        base["EmpTotal"] = pd.to_numeric(base["EmpTotal"], errors="coerce")
        p_e = base.pivot_table(index=["state","year"], columns="quarter", values="EmpTotal", aggfunc="first")
        p_e.columns = [f"e_q{int(c)}" for c in p_e.columns]
        pieces.append(p_e)
    panel = pd.concat(pieces, axis=1).reset_index().sort_values(["state","year"])
    # Lag Q3, Q4
    for q in [3, 4]:
        for v in ["fls", "fgs", "e"]:
            col = f"{v}_q{q}"
            if col in panel.columns:
                panel[f"{v}_q{q}_lag"] = panel.groupby("state")[col].shift(1)
    # NNJF avg (consistent with our main measure, matches Table A4 totals)
    nnjf_q = []
    for ql in ["q3_lag","q4_lag","q1","q2"]:
        nnjf_q.append((panel[f"fls_{ql}"] - panel[f"fgs_{ql}"]).clip(lower=0))
    panel["nnjf"] = sum(nnjf_q) / 4
    # Paper Table A7 values (8-19) match the SUM of 4Q FrmJbLsS (no FrmJbGnS, no clipping)
    # divided by Q4_lag emp — yet another internal-inconsistency scale.
    fls_sum = (panel["fls_q3_lag"] + panel["fls_q4_lag"] + panel["fls_q1"] + panel["fls_q2"])
    if "e_q4_lag" in panel.columns:
        panel["nnjf_per_100"] = 100.0 * fls_sum / panel["e_q4_lag"]
    else:
        panel["nnjf_per_100"] = np.nan
    return panel[["state","year","nnjf","nnjf_per_100"]].rename(columns={"year":"school_year"})


def main() -> None:
    race_n = pd.read_parquet(QWI_CURRENT_DIR / "state_race_ethnicity_nnjf.parquet")
    edu_n = pd.read_parquet(QWI_CURRENT_DIR / "state_education_nnjf.parquet")
    race_e = pd.read_parquet(QWI_CURRENT_DIR / "state_race_ethnicity.parquet")
    edu_e = pd.read_parquet(QWI_CURRENT_DIR / "state_education.parquet")

    # Build per-group panels
    race_panels = {}
    for race in ["A1","A2","A3","A4","A5"]:
        sub_n = race_n[(race_n["pull_dim"]=="race") & (race_n["pull_code"]==race)]
        sub_e = race_e[(race_e["pull_dim"]=="race") & (race_e["pull_code"]==race)]
        race_panels[race] = state_yearly_nnjf(sub_n, sub_e)

    eth_panels = {}
    for eth in ["A1","A2"]:
        sub_n = race_n[(race_n["pull_dim"]=="ethnicity") & (race_n["pull_code"]==eth)]
        sub_e = race_e[(race_e["pull_dim"]=="ethnicity") & (race_e["pull_code"]==eth)]
        eth_panels[eth] = state_yearly_nnjf(sub_n, sub_e)

    edu_panels = {}
    for ed in ["E1","E2","E3","E4"]:
        sub_n = edu_n[edu_n["education"]==ed]
        sub_e = edu_e[edu_e["education"]==ed]
        edu_panels[ed] = state_yearly_nnjf(sub_n, sub_e)

    nonwhite_pool = pd.concat([race_panels[r] for r in ["A2","A3","A4","A5"]], ignore_index=True)
    nonbach_pool = pd.concat([edu_panels[e] for e in ["E1","E2","E3"]], ignore_index=True)

    paper_a7 = {  # year: (White, Non-White, Non-Hispanic, Hispanic, Bachelors, Non-Bachelors)
        2001: (10.68, 15.78, 10.51, 12.95, 10.61, 11.93), 2002: (10.45, 16.06, 10.39, 13.77, 10.66, 11.89),
        2003: (10.79, 17.06, 10.78, 14.61, 10.76, 12.61), 2004: (11.28, 16.88, 11.18, 14.98, 10.98, 13.12),
        2005: (10.94, 16.86, 10.97, 14.29, 10.94, 12.63), 2006: (11.55, 18.27, 11.52, 15.62, 11.80, 12.98),
        2007: (11.72, 17.88, 11.67, 15.02, 12.09, 12.80), 2008: (11.83, 17.24, 11.96, 14.10, 12.43, 12.80),
        2009: (10.51, 15.59, 10.51, 12.96, 11.09, 11.13), 2010: (10.59, 16.47, 10.66, 13.62, 10.90, 11.55),
        2011: (11.83, 16.54, 11.95, 14.02, 12.10, 12.62), 2012: (11.12, 16.25, 11.16, 13.33, 11.48, 11.77),
        2013: (10.75, 16.06, 10.87, 12.58, 11.42, 11.25), 2014: (10.64, 15.63, 10.67, 12.42, 11.29, 10.99),
        2015: (10.51, 14.80, 10.53, 12.11, 11.21, 10.71), 2016: (10.74, 15.75, 10.74, 12.41, 11.62, 10.81),
        2017: (10.40, 15.29, 10.45, 12.30, 11.23, 10.56), 2018: (10.18, 15.32, 10.23, 11.80, 11.03, 10.20),
        2019: (10.43, 15.37, 10.52, 11.67, 11.36, 10.50), 2020: (13.13, 19.03, 13.30, 14.73, 14.30, 13.13),
        2021: (11.43, 16.02, 11.74, 12.70, 11.94, 11.64), 2022: (8.98, 14.71, 9.06, 11.16, 9.56, 9.49),
        2023: (9.88, 14.98, 9.86, 11.01, 10.84, 9.80), 2024: (9.73, 14.12, 9.72, 10.65, 10.68, 9.45),
    }

    def med_for(panel, year):
        sub = panel[(panel["school_year"]==year) & panel["nnjf_per_100"].notna()]
        return sub["nnjf_per_100"].median() if not sub.empty else np.nan

    md = ["# Appendix Table A7 — NNJF per 100 Employees by Characteristic × Year",
          "",
          "Method (Table A7-specific): NNJF per 100 = 100 × sum(FrmJbLsS over 4 school-year quarters)",
          "divided by EmpTotal_Q4_lag. NOTE: this is a DIFFERENT formula than Table A4 totals",
          "(which use avg(max(FrmJbLsS - FrmJbGnS, 0)) / sum(EmpTotal 4Q)). The paper's tables",
          "use mutually inconsistent NNJF/100 formulas — see comparison_to_paper.md for details.",
          "",
          "| Year | White | Non-White | Non-Hispanic | Hispanic | Bachelors | Non-Bachelors |",
          "|------|---|---|---|---|---|---|"]
    err = {g: 0 for g in ["White","Non-White","Non-Hispanic","Hispanic","Bachelors","Non-Bachelors"]}
    nyears = 0
    for y in sorted(paper_a7):
        nyears += 1
        w_m = med_for(race_panels["A1"], y)
        nw_m = med_for(nonwhite_pool, y)
        nh_m = med_for(eth_panels["A1"], y)
        h_m = med_for(eth_panels["A2"], y)
        b_m = med_for(edu_panels["E4"], y)
        nb_m = med_for(nonbach_pool, y)
        p = paper_a7[y]
        mine = [w_m, nw_m, nh_m, h_m, b_m, nb_m]
        cells = " | ".join(f"{m:.2f} / **{pp:.2f}**" if not np.isnan(m) else f"— / **{pp:.2f}**"
                            for m, pp in zip(mine, p))
        md.append(f"| {y} | {cells} |")
        for g, m, pp in zip(["White","Non-White","Non-Hispanic","Hispanic","Bachelors","Non-Bachelors"], mine, p):
            if not np.isnan(m):
                err[g] += abs(m - pp)

    md += ["", "## Match summary (mean absolute error in NNJF/100 units)"]
    for g, e in err.items():
        md.append(f"- **{g}**: avg error = {e/nyears:.2f}")

    (OUTPUT / "tables" / "appendix_table_A7_my.md").write_text("\n".join(md))
    print("Mean absolute error in NNJF/100:")
    for g, e in err.items():
        print(f"  {g}: {e/nyears:.2f}")


if __name__ == "__main__":
    main()
