"""Pull state-level FrmJbLsS and FrmJbGnS by education for NAICS 6111.

Used to build Appendix Table A7 (NNJF by group × year).
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
    out_path = QWI_CURRENT_DIR / "state_education_nnjf.parquet"

    all_rows: list[pd.DataFrame] = []
    t0 = time.time()
    EDU_CODES = ["E0", "E1", "E2", "E3", "E4"]
    total = len(EDU_CODES) * len(US_STATE_FIPS)
    n_done = 0
    for edu in EDU_CODES:
        for st in US_STATE_FIPS:
            df = pull_state_chunked_by_years(
                endpoint="se",
                state_fips=st,
                geography=f"state:{st}",
                get_vars=("FrmJbLsS", "FrmJbGnS", "EmpS"),
                extra_params={"sex": "0", "education": edu},
                start_year=2000, end_quarter="2024-Q2",
                chunk_years=12,
            )
            n_done += 1
            if not df.empty:
                all_rows.append(df)
            if n_done % 50 == 0:
                print(f"  [{n_done:>4}/{total}] elapsed={time.time()-t0:.1f}s")

    combined = pd.concat(all_rows, ignore_index=True)
    for col in ("FrmJbLsS", "FrmJbGnS", "EmpS"):
        if col in combined.columns:
            combined[col] = pd.to_numeric(combined[col], errors="coerce").astype("Int64")
    combined["year"] = combined["time"].str.split("-Q").str[0].astype(int)
    combined["quarter"] = combined["time"].str.split("-Q").str[1].astype(int)
    keep = ["state", "year", "quarter", "time", "industry",
            "sex", "education", "FrmJbLsS", "FrmJbGnS", "EmpS"]
    combined = combined[[c for c in keep if c in combined.columns]]
    combined.to_parquet(out_path, index=False)
    print(f"\nWrote {len(combined):,} rows to {out_path}")


if __name__ == "__main__":
    main()
