"""Figure 4: Education labor market over time and race/ethnicity.

Panel A: Turnover by race (state-level medians by year).
Panel B: NNJF per 100 by race.
Panel C: Turnover by ethnicity.
Panel D: NNJF per 100 by ethnicity.

The paper's Figure 4 is at the state level.
We build state × race-or-ethnicity × school-year measures, then plot the median across states.

Race codes mapping:
  A1=White, A2=Black, A3=Am Indian/AK Native, A4=Asian, A5=NHPI, A6=Two or more
Ethnicity codes:
  A1=Not Hispanic or Latino, A2=Hispanic or Latino
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from _config import FIGURES, QWI_CURRENT_DIR

RACE_LABELS = {"A1": "White", "A2": "Black", "A3": "Am Ind/AK Native",
               "A4": "Asian", "A5": "NHPI", "A6": "Two or more"}
ETH_LABELS = {"A1": "Not Hispanic or Latino", "A2": "Hispanic or Latino"}


def pull_qwi_county_pull(df: pd.DataFrame, dim: str, code: str) -> pd.DataFrame:
    return df[(df["pull_dim"] == dim) & (df["pull_code"] == code)].copy()


def state_school_year_measure(df_sub: pd.DataFrame) -> pd.DataFrame:
    """For a slice of state-quarter data, build state × school-year turnover and NNJF.
    NNJF here uses EmpTotal-based abs differences as a fallback since FrmJbLs isn't
    pulled in the state-level race/ethnicity data. (We accept this as a known limitation
    for Figure 4 — the paper's qualitative finding is what matters.)"""
    df_sub = df_sub.copy()
    for c in ("EmpTotal", "HirN"):
        df_sub[c] = pd.to_numeric(df_sub[c], errors="coerce")

    # Pivot by state, year
    p_emp = df_sub.pivot_table(index=["state", "year"], columns="quarter",
                                values="EmpTotal", aggfunc="first")
    p_emp.columns = [f"emp_q{int(c)}" for c in p_emp.columns]
    p_hir = df_sub.pivot_table(index=["state", "year"], columns="quarter",
                                values="HirN", aggfunc="first")
    p_hir.columns = [f"hir_q{int(c)}" for c in p_hir.columns]
    panel = pd.concat([p_emp, p_hir], axis=1).reset_index().sort_values(["state", "year"])

    for q in [3, 4]:
        panel[f"emp_q{q}_lag"] = panel.groupby("state")[f"emp_q{q}"].shift(1)
        panel[f"hir_q{q}_lag"] = panel.groupby("state")[f"hir_q{q}"].shift(1)

    sum_hires = (panel["hir_q3_lag"] + panel["hir_q4_lag"]
                 + panel["hir_q1"] + panel["hir_q2"])
    emp_change = panel["emp_q2"] - panel["emp_q4_lag"]
    leavers = sum_hires - emp_change
    panel["turnover"] = leavers / panel["emp_q4_lag"]

    # NNJF using abs differences as fallback (no FrmJbLs in this pull); divide by 4
    nnjf = ((panel["emp_q3_lag"] - panel["emp_q4_lag"]).abs()
            + (panel["emp_q4_lag"] - panel["emp_q1"]).abs()
            + (panel["emp_q1"] - panel["emp_q2"]).abs()
            + (panel["emp_q2"] - panel["emp_q3"]).abs()) / 4.0
    panel["nnjf_per_100"] = 100.0 * nnjf / panel["emp_q4_lag"]

    return panel[["state", "year", "turnover", "nnjf_per_100"]].rename(columns={"year": "school_year"})


def main() -> None:
    FIGURES.mkdir(parents=True, exist_ok=True)
    df = pd.read_parquet(QWI_CURRENT_DIR / "state_race_ethnicity.parquet")
    print(f"Loaded {len(df):,} rows from state_race_ethnicity.parquet")

    # Compute measures per race code, then by ethnicity
    race_data = {}
    for race in ["A1", "A2", "A3", "A4", "A5", "A6"]:
        sub = pull_qwi_county_pull(df, "race", race)
        if sub.empty:
            continue
        m = state_school_year_measure(sub)
        race_data[race] = m

    eth_data = {}
    for eth in ["A1", "A2"]:
        sub = pull_qwi_county_pull(df, "ethnicity", eth)
        if sub.empty:
            continue
        m = state_school_year_measure(sub)
        eth_data[eth] = m

    # Plot
    fig, axes = plt.subplots(2, 2, figsize=(13, 9))
    recessions = [(2001.1, 2001.9), (2007.9, 2009.5), (2020.1, 2020.4)]

    # Panel A: Turnover by race
    ax = axes[0, 0]
    for race, m in race_data.items():
        annual = m.groupby("school_year")["turnover"].median() * 100
        ax.plot(annual.index, annual.values, "-o", label=RACE_LABELS.get(race, race),
                markersize=4)
    for r0, r1 in recessions: ax.axvspan(r0, r1, alpha=0.15, color="gray")
    ax.set_xlabel("Year (Spring)"); ax.set_ylabel("Educator Turnover (Med)")
    ax.set_title("Panel A. Turnover by race")
    ax.legend(fontsize=8); ax.set_ylim(0, 50)

    # Panel B: NNJF/100 by race
    ax = axes[0, 1]
    for race, m in race_data.items():
        annual = m.groupby("school_year")["nnjf_per_100"].median()
        ax.plot(annual.index, annual.values, "-o", label=RACE_LABELS.get(race, race),
                markersize=4)
    for r0, r1 in recessions: ax.axvspan(r0, r1, alpha=0.15, color="gray")
    ax.set_xlabel("Year (Spring)"); ax.set_ylabel("NNJF per 100 (Med)")
    ax.set_title("Panel B. NNJF by race"); ax.legend(fontsize=8)

    # Panel C: Turnover by ethnicity
    ax = axes[1, 0]
    for eth, m in eth_data.items():
        annual = m.groupby("school_year")["turnover"].median() * 100
        ax.plot(annual.index, annual.values, "-o", label=ETH_LABELS.get(eth, eth),
                markersize=4)
    for r0, r1 in recessions: ax.axvspan(r0, r1, alpha=0.15, color="gray")
    ax.set_xlabel("Year (Spring)"); ax.set_ylabel("Educator Turnover (Med)")
    ax.set_title("Panel C. Turnover by ethnicity"); ax.legend(fontsize=8); ax.set_ylim(0, 45)

    # Panel D: NNJF/100 by ethnicity
    ax = axes[1, 1]
    for eth, m in eth_data.items():
        annual = m.groupby("school_year")["nnjf_per_100"].median()
        ax.plot(annual.index, annual.values, "-o", label=ETH_LABELS.get(eth, eth),
                markersize=4)
    for r0, r1 in recessions: ax.axvspan(r0, r1, alpha=0.15, color="gray")
    ax.set_xlabel("Year (Spring)"); ax.set_ylabel("NNJF per 100 (Med)")
    ax.set_title("Panel D. NNJF by ethnicity"); ax.legend(fontsize=8)

    fig.suptitle("Figure 4. Education labor market over time and race/ethnicity", fontsize=13)
    fig.tight_layout()
    out_path = FIGURES / "figure_4_race_ethnicity.png"
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
