"""Reproduce Appendix Table A3 — quantile (median) regressions on year dummies.

Paper Table A3:
  (1) Turnover ~ 1[Year=2020] + 1[Year=2021], sample 2000-2021
        Year 2020:  0.0331*** (0.0023)
        Year 2021: -0.0430*** (0.0017)
        Constant:   0.2311*** (0.0004)
        N = 43,189
  (2) Turnover ~ 1[Years 2022-2024], sample 2013-2024
        Year ≥ 2022: 0.0268*** (0.0011)
        Constant:    0.2232*** (0.0006)
        N = 21,231
  (3) NNJF/100 ~ 1[Year=2020], sample 2000-2021
        Year 2020: 0.2400*** (0.0333)
        Constant:  1.0900*** (0.0075)
        N = 47,884
  (4) NNJF/100 ~ 1[Years 2021-2024], sample 2020-2024
        Coef:      -0.3600*** (0.0341)
        Constant:   1.3300*** (0.0304)
        N = 11,722
  (5) NNJF/100 ~ 1[Years 2021-2024], sample 2013-2024
        Coef:      -0.1500*** (0.0206)
        Constant:   1.1100*** (0.0110)
        N = 24,001
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

sys.path.insert(0, str(Path(__file__).parent))
from _config import DATA_DERIVED, OUTPUT


def main() -> None:
    sy = pd.read_parquet(DATA_DERIVED / "county_school_year_measures.parquet")
    sy["turnover"] = pd.to_numeric(sy["turnover"], errors="coerce")
    sy["nnjf_per_100"] = pd.to_numeric(sy["nnjf_per_100"], errors="coerce")
    sy["emp_lag"] = pd.to_numeric(sy["emp_lag"], errors="coerce")

    paper = {
        "(1) turnover 2020, 2000-2021": dict(N=43189, c_2020=0.0331, c_2021=-0.0430, const=0.2311),
        "(2) turnover yrs 2022-24, 2013-2024": dict(N=21231, c=0.0268, const=0.2232),
        "(3) NNJF/100 yr 2020, 2000-2021": dict(N=47884, c=0.2400, const=1.0900),
        "(4) NNJF/100 yrs 2021-24, 2020-2024": dict(N=11722, c=-0.3600, const=1.3300),
        "(5) NNJF/100 yrs 2021-24, 2013-2024": dict(N=24001, c=-0.1500, const=1.1100),
    }

    print("="*70)
    print("Appendix Table A3 replication")
    print("="*70)

    # (1) Turnover quantile regression 2000-2021, year 2020 and year 2021 dummies
    samp = sy[(sy["school_year"] >= 2001) & (sy["school_year"] <= 2021)].dropna(subset=["turnover"])
    samp["yr_2020"] = (samp["school_year"] == 2020).astype(int)
    samp["yr_2021"] = (samp["school_year"] == 2021).astype(int)
    print(f"\n(1) Turnover ~ yr2020 + yr2021, sample 2001-2021")
    print(f"    My N = {len(samp):,}   Paper N = 43,189")
    try:
        m = smf.quantreg("turnover ~ yr_2020 + yr_2021", data=samp).fit(q=0.5, max_iter=2000)
        print(f"    yr_2020  coef = {m.params['yr_2020']:.4f}   (paper 0.0331)")
        print(f"    yr_2021  coef = {m.params['yr_2021']:.4f}   (paper -0.0430)")
        print(f"    constant     = {m.params['Intercept']:.4f}  (paper 0.2311)")
    except Exception as e:
        print(f"    failed: {e}")

    # (2) Turnover 2013-2024, years 2022-2024 dummy
    samp = sy[(sy["school_year"] >= 2013) & (sy["school_year"] <= 2024)].dropna(subset=["turnover"])
    samp = samp[(samp["school_year"] != 2020) & (samp["school_year"] != 2021)]  # paper says estimates exclude 2020/2021
    samp["yr_2022p"] = (samp["school_year"] >= 2022).astype(int)
    print(f"\n(2) Turnover ~ yr_2022_to_2024, sample 2013-2024 excl. 2020 & 2021")
    print(f"    My N = {len(samp):,}   Paper N = 21,231")
    try:
        m = smf.quantreg("turnover ~ yr_2022p", data=samp).fit(q=0.5, max_iter=2000)
        print(f"    yr_2022p coef = {m.params['yr_2022p']:.4f}  (paper 0.0268)")
        print(f"    constant     = {m.params['Intercept']:.4f}  (paper 0.2232)")
    except Exception as e:
        print(f"    failed: {e}")

    # (3) NNJF/100 ~ yr 2020 dummy, sample 2000-2021
    samp = sy[(sy["school_year"] >= 2001) & (sy["school_year"] <= 2021)].dropna(subset=["nnjf_per_100"])
    samp["yr_2020"] = (samp["school_year"] == 2020).astype(int)
    print(f"\n(3) NNJF/100 ~ yr_2020, sample 2001-2021")
    print(f"    My N = {len(samp):,}   Paper N = 47,884")
    try:
        m = smf.quantreg("nnjf_per_100 ~ yr_2020", data=samp).fit(q=0.5, max_iter=2000)
        print(f"    yr_2020  coef = {m.params['yr_2020']:.4f}  (paper 0.2400)")
        print(f"    constant     = {m.params['Intercept']:.4f}   (paper 1.0900)")
    except Exception as e:
        print(f"    failed: {e}")

    # (4) NNJF/100 ~ yrs 2021-2024, sample 2020-2024
    samp = sy[(sy["school_year"] >= 2020) & (sy["school_year"] <= 2024)].dropna(subset=["nnjf_per_100"])
    samp["yr_2021p"] = (samp["school_year"] >= 2021).astype(int)
    print(f"\n(4) NNJF/100 ~ yr_2021_to_2024, sample 2020-2024")
    print(f"    My N = {len(samp):,}   Paper N = 11,722")
    try:
        m = smf.quantreg("nnjf_per_100 ~ yr_2021p", data=samp).fit(q=0.5, max_iter=2000)
        print(f"    yr_2021p coef = {m.params['yr_2021p']:.4f}  (paper -0.3600)")
        print(f"    constant     = {m.params['Intercept']:.4f}  (paper 1.3300)")
    except Exception as e:
        print(f"    failed: {e}")

    # (5) NNJF/100 ~ yrs 2021-2024, sample 2013-2024
    samp = sy[(sy["school_year"] >= 2013) & (sy["school_year"] <= 2024)].dropna(subset=["nnjf_per_100"])
    samp["yr_2021p"] = (samp["school_year"] >= 2021).astype(int)
    print(f"\n(5) NNJF/100 ~ yr_2021_to_2024, sample 2013-2024")
    print(f"    My N = {len(samp):,}   Paper N = 24,001")
    try:
        m = smf.quantreg("nnjf_per_100 ~ yr_2021p", data=samp).fit(q=0.5, max_iter=2000)
        print(f"    yr_2021p coef = {m.params['yr_2021p']:.4f}  (paper -0.1500)")
        print(f"    constant     = {m.params['Intercept']:.4f}  (paper 1.1100)")
    except Exception as e:
        print(f"    failed: {e}")


if __name__ == "__main__":
    main()
