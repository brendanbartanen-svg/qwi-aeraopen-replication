"""Pull FrmJbLsS (Firm Job Losses to Stable Employment) at county level for NAICS 6111.

This is the stable-employment-subset variant. May be the actual variable used in the paper.
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
    out_path = QWI_CURRENT_DIR / "county_sex0_frmjblss.parquet"

    all_rows: list[pd.DataFrame] = []
    t0 = time.time()
    for i, st in enumerate(US_STATE_FIPS, 1):
        df = pull_state_chunked_by_years(
            endpoint="sa",
            state_fips=st,
            get_vars=("FrmJbLsS", "FrmJbGnS", "EmpS", "EmpEnd"),
            extra_params={"sex": "0"},
            start_year=2000,
            end_quarter="2025-Q2",
            chunk_years=4,
        )
        all_rows.append(df)
        if i % 10 == 0:
            print(f"  [{i:2d}/51] elapsed={time.time()-t0:.1f}s")

    combined = pd.concat(all_rows, ignore_index=True)
    for col in ("FrmJbLsS", "FrmJbGnS", "EmpS", "EmpEnd"):
        if col in combined.columns:
            combined[col] = pd.to_numeric(combined[col], errors="coerce").astype("Int64")
    combined["year"] = combined["time"].str.split("-Q").str[0].astype(int)
    combined["quarter"] = combined["time"].str.split("-Q").str[1].astype(int)
    combined["fips"] = combined["state"].astype(str) + combined["county"].astype(str)

    keep = ["fips", "state", "county", "year", "quarter", "time", "industry", "sex",
            "FrmJbLsS", "FrmJbGnS", "EmpS", "EmpEnd"]
    combined = combined[[c for c in keep if c in combined.columns]]
    combined.to_parquet(out_path, index=False)
    print(f"Wrote {len(combined):,} rows to {out_path}")


if __name__ == "__main__":
    main()
