"""Reproduce Appendix Table A6 — turnover by employee characteristic × year.

Paper Table A6 (Turnover %): columns White, Non-White, Non-Hispanic, Hispanic, Bachelors, Non-Bachelors

Approach: each race/edu group treated as a separate panel observation (state × year × group),
then median across non-white panel obs gives the Non-White value (and similarly for others).
This matches the paper's method confirmed in Table A5 replication.

Table A7 (NNJF/100): requires FrmJbLsS at state × race × edu level — not pulled here.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from _config import OUTPUT, QWI_CURRENT_DIR


def state_yearly(df_sub: pd.DataFrame) -> pd.DataFrame:
    df_sub = df_sub.copy()
    for c in ("EmpTotal","HirN"):
        df_sub[c] = pd.to_numeric(df_sub[c], errors="coerce")
    p_emp = df_sub.pivot_table(index=["state","year"], columns="quarter", values="EmpTotal", aggfunc="first")
    p_emp.columns = [f"emp_q{int(c)}" for c in p_emp.columns]
    p_hir = df_sub.pivot_table(index=["state","year"], columns="quarter", values="HirN", aggfunc="first")
    p_hir.columns = [f"hir_q{int(c)}" for c in p_hir.columns]
    panel = pd.concat([p_emp, p_hir], axis=1).reset_index().sort_values(["state","year"])
    for q in [3,4]:
        panel[f"emp_q{q}_lag"] = panel.groupby("state")[f"emp_q{q}"].shift(1)
        panel[f"hir_q{q}_lag"] = panel.groupby("state")[f"hir_q{q}"].shift(1)
    sum_h = panel["hir_q3_lag"] + panel["hir_q4_lag"] + panel["hir_q1"] + panel["hir_q2"]
    emp_chg = panel["emp_q2"] - panel["emp_q4_lag"]
    panel["leavers"] = sum_h - emp_chg
    panel["turnover"] = panel["leavers"] / panel["emp_q4_lag"]
    return panel[["state","year","turnover"]].rename(columns={"year":"school_year"})


def main() -> None:
    race_df = pd.read_parquet(QWI_CURRENT_DIR / "state_race_ethnicity.parquet")
    edu_df = pd.read_parquet(QWI_CURRENT_DIR / "state_education.parquet")

    # Build per-group panels
    race_panels = {}
    for race in ["A1","A2","A3","A4","A5"]:
        race_panels[race] = state_yearly(
            race_df[(race_df["pull_dim"]=="race") & (race_df["pull_code"]==race)])

    eth_panels = {}
    for eth in ["A1","A2"]:
        eth_panels[eth] = state_yearly(
            race_df[(race_df["pull_dim"]=="ethnicity") & (race_df["pull_code"]==eth)])

    edu_panels = {}
    for ed in ["E1","E2","E3","E4"]:
        edu_panels[ed] = state_yearly(edu_df[edu_df["education"]==ed])

    # Combine non-white races into one pooled panel
    nonwhite_pool = pd.concat([race_panels["A2"], race_panels["A3"], race_panels["A4"], race_panels["A5"]],
                              ignore_index=True)
    nonbach_pool = pd.concat([edu_panels["E1"], edu_panels["E2"], edu_panels["E3"]], ignore_index=True)

    paper_a6 = {  # year: (White, Non-White, Non-Hispanic, Hispanic, Bachelors, Non-Bachelors)
        2001: (26.9, 43.7, 27.1, 43.5, 18.5, 28.2), 2002: (26.6, 43.7, 27.1, 43.6, 18.2, 28.2),
        2003: (25.2, 41.5, 25.7, 40.4, 17.5, 26.4), 2004: (24.0, 39.4, 24.5, 37.2, 16.4, 25.4),
        2005: (23.9, 38.2, 24.5, 38.4, 16.4, 25.6), 2006: (24.5, 38.3, 24.9, 38.3, 17.1, 26.1),
        2007: (24.2, 37.7, 24.7, 36.2, 17.1, 25.8), 2008: (23.5, 36.6, 23.6, 35.4, 16.3, 24.5),
        2009: (22.6, 33.6, 23.0, 32.7, 16.0, 23.5), 2010: (20.9, 30.6, 21.3, 29.4, 14.5, 21.6),
        2011: (20.1, 29.3, 20.6, 28.2, 14.2, 20.8), 2012: (20.1, 29.5, 20.6, 28.2, 14.1, 20.8),
        2013: (21.5, 32.0, 22.0, 29.5, 15.6, 22.2), 2014: (21.3, 31.4, 21.8, 30.2, 15.3, 21.9),
        2015: (21.9, 32.4, 22.4, 31.3, 15.9, 22.5), 2016: (22.1, 33.0, 22.8, 31.2, 16.3, 22.9),
        2017: (22.0, 33.1, 22.6, 31.0, 16.1, 22.6), 2018: (21.5, 32.2, 22.2, 30.5, 15.9, 22.2),
        2019: (21.5, 32.9, 22.3, 30.3, 16.0, 22.1), 2020: (28.7, 40.5, 29.7, 37.1, 22.9, 28.3),
        2021: (17.2, 24.8, 17.4, 23.6, 12.0, 16.2), 2022: (25.4, 37.8, 26.2, 35.5, 19.1, 25.5),
        2023: (24.5, 35.9, 25.3, 33.3, 18.5, 24.4), 2024: (23.4, 34.0, 24.2, 31.7, 17.7, 23.1),
    }

    def med_for(panel, year):
        sub = panel[(panel["school_year"]==year) & panel["turnover"].notna()]
        return sub["turnover"].median() * 100 if not sub.empty else np.nan

    md = ["# Appendix Table A6 — Turnover by Employee Characteristic × Year",
          "",
          "Method: each race/edu group treated as separate state×year panel obs; report median across obs.",
          "",
          "| Year | White | Non-White | Non-Hispanic | Hispanic | Bachelors | Non-Bachelors |",
          "|------|---|---|---|---|---|---|"]
    total_err = {g: 0 for g in ["White","Non-White","Non-Hispanic","Hispanic","Bachelors","Non-Bachelors"]}
    for y in sorted(paper_a6):
        w_m = med_for(race_panels["A1"], y)
        nw_m = med_for(nonwhite_pool, y)
        nh_m = med_for(eth_panels["A1"], y)
        h_m  = med_for(eth_panels["A2"], y)
        b_m  = med_for(edu_panels["E4"], y)
        nb_m = med_for(nonbach_pool, y)
        p = paper_a6[y]
        mine = [w_m, nw_m, nh_m, h_m, b_m, nb_m]
        cells = " | ".join(f"{m:.1f} / **{pp:.1f}**" for m, pp in zip(mine, p))
        md.append(f"| {y} | {cells} |")
        for g, m, pp in zip(["White","Non-White","Non-Hispanic","Hispanic","Bachelors","Non-Bachelors"], mine, p):
            if not np.isnan(m):
                total_err[g] += abs(m - pp)

    md += ["", "## Match summary (mean absolute error in pp across years)"]
    for g, err in total_err.items():
        md.append(f"- **{g}**: {err/24:.2f} pp average error")

    (OUTPUT / "tables" / "appendix_table_A6_my.md").write_text("\n".join(md))
    print("Mean absolute error (pp):")
    for g, err in total_err.items():
        print(f"  {g}: {err/24:.2f}")


if __name__ == "__main__":
    main()
