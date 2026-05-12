"""Pull state-level QWI data by education for NAICS 6111, 2000 Q1 to 2024 Q2.

Used for Figure 5 and Appendix Tables A5, A6, A7. State-level.

QWI education codes:
  E0=All, E1=Less than HS, E2=HS or equivalent, E3=Some college or AA,
  E4=Bachelor's degree or above, E5=Education attainment not available (worker < 24)

We use sex=0 (all sex) and pull per education code.
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from _config import QWI_CURRENT_DIR
from _qwi_client import US_STATE_FIPS, pull_state_chunked_by_years


EDU_CODES = ["E0", "E1", "E2", "E3", "E4", "E5"]


def main() -> None:
    QWI_CURRENT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = QWI_CURRENT_DIR / "state_education.parquet"

    all_rows: list[pd.DataFrame] = []
    t0 = time.time()
    total = len(EDU_CODES) * len(US_STATE_FIPS)
    n_done = 0
    for edu in EDU_CODES:
        for st in US_STATE_FIPS:
            df = pull_state_chunked_by_years(
                endpoint="se",
                state_fips=st,
                geography=f"state:{st}",
                extra_params={"sex": "0", "education": edu},
                start_year=2000,
                end_quarter="2024-Q2",
                chunk_years=12,
            )
            n_done += 1
            if not df.empty:
                all_rows.append(df)
            if n_done % 20 == 0 or n_done == total:
                dt = time.time() - t0
                print(f"  [{n_done:>4}/{total}] edu={edu} st={st}  elapsed={dt:5.1f}s")

    combined = pd.concat(all_rows, ignore_index=True)
    if combined.empty:
        print("No data!")
        return
    for col in ("EmpTotal", "HirN"):
        combined[col] = pd.to_numeric(combined[col], errors="coerce").astype("Int64")
    combined["year"] = combined["time"].str.split("-Q").str[0].astype(int)
    combined["quarter"] = combined["time"].str.split("-Q").str[1].astype(int)

    keep = ["state", "year", "quarter", "time", "industry",
            "sex", "education", "EmpTotal", "HirN"]
    keep = [c for c in keep if c in combined.columns]
    combined = combined[keep]
    combined.to_parquet(out_path, index=False)

    print(f"\nWrote {len(combined):,} rows to {out_path}")
    print(f"  unique states: {combined['state'].nunique()}")
    print(f"  unique education codes: {sorted(combined['education'].unique())}")


if __name__ == "__main__":
    main()
