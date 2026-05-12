"""Figure 5: Education labor market over time and educational attainment.

Panel A: Turnover by education (state-level medians by year).
Panel B: NNJF per 100 by education.

Education codes:
  E1=Less than HS, E2=HS or equivalent, E3=Some college or AA, E4=Bachelor's+
  E5=Education attainment not available (worker < 24) - excluded from main analysis
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from _config import FIGURES, QWI_CURRENT_DIR

EDU_LABELS = {"E1": "Less than high school", "E2": "High school or equivalent",
              "E3": "Some college or AA", "E4": "Bachelor's degree or above"}


def state_school_year_measure(df_sub: pd.DataFrame) -> pd.DataFrame:
    df_sub = df_sub.copy()
    for c in ("EmpTotal", "HirN"):
        df_sub[c] = pd.to_numeric(df_sub[c], errors="coerce")
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

    nnjf = ((panel["emp_q3_lag"] - panel["emp_q4_lag"]).abs()
            + (panel["emp_q4_lag"] - panel["emp_q1"]).abs()
            + (panel["emp_q1"] - panel["emp_q2"]).abs()
            + (panel["emp_q2"] - panel["emp_q3"]).abs()) / 4.0
    panel["nnjf_per_100"] = 100.0 * nnjf / panel["emp_q4_lag"]
    return panel[["state", "year", "turnover", "nnjf_per_100"]].rename(columns={"year": "school_year"})


def main() -> None:
    FIGURES.mkdir(parents=True, exist_ok=True)
    df = pd.read_parquet(QWI_CURRENT_DIR / "state_education.parquet")
    print(f"Loaded {len(df):,} rows from state_education.parquet")

    edu_data = {}
    for edu in ["E1", "E2", "E3", "E4"]:  # exclude E0 (all) and E5 (<24 unknown)
        sub = df[df["education"] == edu]
        if sub.empty:
            continue
        m = state_school_year_measure(sub)
        edu_data[edu] = m

    fig, axes = plt.subplots(2, 1, figsize=(10, 9))
    recessions = [(2001.1, 2001.9), (2007.9, 2009.5), (2020.1, 2020.4)]

    # Panel A: Turnover by edu
    ax = axes[0]
    for edu, m in edu_data.items():
        annual = m.groupby("school_year")["turnover"].median() * 100
        ax.plot(annual.index, annual.values, "-o", label=EDU_LABELS.get(edu, edu),
                markersize=5)
    for r0, r1 in recessions: ax.axvspan(r0, r1, alpha=0.15, color="gray")
    ax.set_xlabel("Year (Spring)"); ax.set_ylabel("Educator Turnover % (Med)")
    ax.set_title("Panel A. Turnover"); ax.legend(fontsize=9); ax.set_ylim(0, 40)

    # Panel B: NNJF/100 by edu
    ax = axes[1]
    for edu, m in edu_data.items():
        annual = m.groupby("school_year")["nnjf_per_100"].median()
        ax.plot(annual.index, annual.values, "-o", label=EDU_LABELS.get(edu, edu),
                markersize=5)
    for r0, r1 in recessions: ax.axvspan(r0, r1, alpha=0.15, color="gray")
    ax.set_xlabel("Year (Spring)"); ax.set_ylabel("NNJF per 100 (Med)")
    ax.set_title("Panel B. Net-Negative Job-Flow"); ax.legend(fontsize=9)

    fig.suptitle("Figure 5. Education labor market over time and educational attainment", fontsize=13)
    fig.tight_layout()
    out_path = FIGURES / "figure_5_education.png"
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
