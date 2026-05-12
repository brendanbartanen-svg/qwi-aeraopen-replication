"""Pull state-level QWI data by race × ethnicity for NAICS 6111, 2000 Q1 to 2024 Q2.

Used for Figure 4 and Appendix Tables A5, A6, A7. Per the paper, Figure 4 is at the state level.

QWI race codes:
  A0=All, A1=White, A2=Black, A3=Am. Indian/Alaska Native, A4=Asian,
  A5=Native Hawaiian/Other Pac. Islander, A6=Two or more
QWI ethnicity codes:
  A0=All, A1=Not Hispanic or Latino, A2=Hispanic or Latino

The QWI API requires explicit filter values; comma-separated lists return empty.
Per (race, ethnicity) we make one API call per state, with all 98 quarters in one request.
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from _config import QWI_CURRENT_DIR
from _qwi_client import US_STATE_FIPS, pull_state_chunked_by_years


# Marginals only: race × ethnicity=A0 (all), and race=A0 × ethnicity for ethnicity panels
RACE_CODES = ["A0", "A1", "A2", "A3", "A4", "A5", "A6"]
ETH_CODES = ["A0", "A1", "A2"]


def main() -> None:
    QWI_CURRENT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = QWI_CURRENT_DIR / "state_race_ethnicity.parquet"

    all_rows: list[pd.DataFrame] = []
    t0 = time.time()
    # Race-marginal pulls (ethnicity = A0)
    combos = [("race", r) for r in RACE_CODES] + [("ethnicity", e) for e in ["A1", "A2"]]
    total = len(combos) * len(US_STATE_FIPS)
    n_done = 0
    for dim, code in combos:
        for st in US_STATE_FIPS:
            t_st = time.time()
            extra = {dim: code}
            if dim == "race":
                extra["ethnicity"] = "A0"
            else:
                extra["race"] = "A0"
            df = pull_state_chunked_by_years(
                endpoint="rh",
                state_fips=st,
                geography=f"state:{st}",
                extra_params=extra,
                start_year=2000,
                end_quarter="2024-Q2",
                chunk_years=12,  # state-level is small, fewer chunks
            )
            n_done += 1
            if not df.empty:
                df["pull_dim"] = dim
                df["pull_code"] = code
                all_rows.append(df)
            if n_done % 20 == 0 or n_done == total:
                dt = time.time() - t0
                print(f"  [{n_done:>4}/{total}] dim={dim:9s} code={code} st={st}  elapsed={dt:5.1f}s")

    combined = pd.concat(all_rows, ignore_index=True)
    if combined.empty:
        print("No data!")
        return
    for col in ("EmpTotal", "HirN"):
        combined[col] = pd.to_numeric(combined[col], errors="coerce").astype("Int64")
    combined["year"] = combined["time"].str.split("-Q").str[0].astype(int)
    combined["quarter"] = combined["time"].str.split("-Q").str[1].astype(int)

    keep = ["state", "year", "quarter", "time", "industry",
            "race", "ethnicity", "pull_dim", "pull_code", "EmpTotal", "HirN"]
    keep = [c for c in keep if c in combined.columns]
    combined = combined[keep]
    combined.to_parquet(out_path, index=False)

    print(f"\nWrote {len(combined):,} rows to {out_path}")
    print(f"  unique states: {combined['state'].nunique()}")
    print(f"  unique race codes: {sorted(combined['race'].unique())}")
    print(f"  unique ethnicity codes: {sorted(combined['ethnicity'].unique())}")


if __name__ == "__main__":
    main()
