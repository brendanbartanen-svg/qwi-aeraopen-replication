"""Pull county-level QWI data for NAICS 6111, sex=0, all states, 2000-Q1 to 2024-Q2.

Output: data/raw/qwi_current/county_sex0.parquet  (long format, one row per county-quarter)

This matches the paper's analytic sample: 2000-Q1 to 2024-Q2 (the same window the authors
extracted on 2025-03-05). Values may differ from the paper's because QWI is revised quarterly.
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from _config import QWI_CURRENT_DIR
from _qwi_client import US_STATE_FIPS, pull_state_chunked_by_years


def main() -> None:
    QWI_CURRENT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = QWI_CURRENT_DIR / "county_sex0.parquet"

    all_rows: list[pd.DataFrame] = []
    t0 = time.time()
    for i, st in enumerate(US_STATE_FIPS, 1):
        t_st = time.time()
        df = pull_state_chunked_by_years(
            endpoint="sa",
            state_fips=st,
            extra_params={"sex": "0"},
            start_year=2000,
            end_quarter="2024-Q2",
        )
        n = len(df)
        all_rows.append(df)
        dt = time.time() - t_st
        elapsed = time.time() - t0
        print(f"  [{i:2d}/51] state={st}: {n:>6} rows  ({dt:4.1f}s) elapsed={elapsed:5.1f}s")

    combined = pd.concat(all_rows, ignore_index=True)
    for col in ("EmpTotal", "HirN"):
        combined[col] = pd.to_numeric(combined[col], errors="coerce").astype("Int64")
    combined["year"] = combined["time"].str.split("-Q").str[0].astype(int)
    combined["quarter"] = combined["time"].str.split("-Q").str[1].astype(int)
    combined["fips"] = combined["state"].astype(str) + combined["county"].astype(str)

    combined = combined[["fips", "state", "county", "year", "quarter", "time",
                         "industry", "sex", "EmpTotal", "HirN"]]
    combined.to_parquet(out_path, index=False)

    print(f"\nWrote {len(combined):,} rows to {out_path}")
    print(f"  unique counties: {combined['fips'].nunique()}")
    print(f"  time range: {combined['time'].min()} to {combined['time'].max()}")
    print(f"  EmpTotal non-null: {combined['EmpTotal'].notna().sum():,}")
    print(f"  HirN non-null: {combined['HirN'].notna().sum():,}")


if __name__ == "__main__":
    main()
