"""Pull county-level Emp (beginning-of-quarter) and EmpEnd alongside EmpTotal and HirN.

The paper's Eq 2 uses 'emp' generically. EmpTotal is flow employment (seasonal-sensitive);
Emp is BoQ (more stable across quarters). Testing both.
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
    out_path = QWI_CURRENT_DIR / "county_sex0_full.parquet"

    all_rows: list[pd.DataFrame] = []
    t0 = time.time()
    for i, st in enumerate(US_STATE_FIPS, 1):
        t_st = time.time()
        df = pull_state_chunked_by_years(
            endpoint="sa",
            state_fips=st,
            get_vars=("EmpTotal", "Emp", "EmpEnd", "HirN", "HirA", "Sep", "FrmJbLs", "FrmJbGn"),
            extra_params={"sex": "0"},
            start_year=2000,
            end_quarter="2024-Q2",
            chunk_years=4,  # more vars = chunk more aggressively
        )
        n = len(df)
        all_rows.append(df)
        dt = time.time() - t_st
        elapsed = time.time() - t0
        print(f"  [{i:2d}/51] state={st}: {n:>6} rows  ({dt:4.1f}s) elapsed={elapsed:5.1f}s")

    combined = pd.concat(all_rows, ignore_index=True)
    for col in ("EmpTotal", "Emp", "EmpEnd", "HirN", "HirA", "Sep", "FrmJbLs", "FrmJbGn"):
        if col in combined.columns:
            combined[col] = pd.to_numeric(combined[col], errors="coerce").astype("Int64")
    combined["year"] = combined["time"].str.split("-Q").str[0].astype(int)
    combined["quarter"] = combined["time"].str.split("-Q").str[1].astype(int)
    combined["fips"] = combined["state"].astype(str) + combined["county"].astype(str)

    keep_cols = ["fips", "state", "county", "year", "quarter", "time", "industry", "sex",
                 "EmpTotal", "Emp", "EmpEnd", "HirN", "HirA", "Sep", "FrmJbLs", "FrmJbGn"]
    combined = combined[[c for c in keep_cols if c in combined.columns]]
    combined.to_parquet(out_path, index=False)

    print(f"\nWrote {len(combined):,} rows to {out_path}")


if __name__ == "__main__":
    main()
