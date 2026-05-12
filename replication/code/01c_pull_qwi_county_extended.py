"""Extend the county-level pull through 2025-Q2 to overlap with the latest state validation data.

Outputs data/raw/qwi_current/county_sex0_full_2025q2.parquet
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
    out_path = QWI_CURRENT_DIR / "county_sex0_full_2025q2.parquet"

    all_rows: list[pd.DataFrame] = []
    t0 = time.time()
    for i, st in enumerate(US_STATE_FIPS, 1):
        df = pull_state_chunked_by_years(
            endpoint="sa",
            state_fips=st,
            get_vars=("EmpTotal", "Emp", "HirN", "FrmJbLs"),
            extra_params={"sex": "0"},
            start_year=2000,
            end_quarter="2025-Q2",
            chunk_years=4,
        )
        all_rows.append(df)
        if i % 10 == 0:
            print(f"  [{i:2d}/51] elapsed={time.time()-t0:.1f}s")

    combined = pd.concat(all_rows, ignore_index=True)
    for col in ("EmpTotal", "Emp", "HirN", "FrmJbLs"):
        if col in combined.columns:
            combined[col] = pd.to_numeric(combined[col], errors="coerce").astype("Int64")
    combined["year"] = combined["time"].str.split("-Q").str[0].astype(int)
    combined["quarter"] = combined["time"].str.split("-Q").str[1].astype(int)
    combined["fips"] = combined["state"].astype(str) + combined["county"].astype(str)

    keep_cols = ["fips", "state", "county", "year", "quarter", "time", "industry", "sex",
                 "EmpTotal", "Emp", "HirN", "FrmJbLs"]
    combined = combined[[c for c in keep_cols if c in combined.columns]]
    combined.to_parquet(out_path, index=False)

    print(f"\nWrote {len(combined):,} rows to {out_path}")
    print(f"  time range: {combined['time'].min()} to {combined['time'].max()}")


if __name__ == "__main__":
    main()
