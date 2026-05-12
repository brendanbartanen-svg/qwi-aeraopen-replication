"""Agent investigation: industry / ownership / firm-size filters for NNJF.

Goal: find a filter combo that brings per-100 NNJF rates closer to the paper's
reported values (paper pooled median 1.080; per-year medians 0.43/0.51/0.31/0.40)
while keeping NNJF totals reasonable (~176K / 225K / 150K / 162K).

Five hypotheses tested:
  H1: NAICS 6111, ownercode=A00 (default, baseline)
  H2: NAICS 6111, ownercode=A05 (small federal/government subset)
  H3: NAICS 611110 (6-digit, explicit; should equal H1 if hierarchy collapses)
  H4: NAICS 611 (3-digit, broader educational services)
  H5: NAICS 61  (2-digit, broadest educational services sector)
  H6: NAICS 6111 + firmage=0 + firmsize=0 (explicit "all" filters)
  H7: NAICS 6111 + ind_level=4 (explicit detailed-industry flag)

For each hypothesis we pull EmpTotal and FrmJbLsS for 3 representative states
(AL=01, CO=08, TX=48) over the 2018-Q3 → 2023-Q2 window (covers school years
2019, 2020, 2021, 2023), compute county-school-year NNJF (avg FrmJbLsS across
4 SY quarters) and per-100 rates, then report pooled totals and weighted
medians vs. the paper.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from _qwi_client import fetch_df


STATES = [("01", "AL"), ("08", "CO"), ("48", "TX")]
SCHOOL_YEARS = [2019, 2020, 2021, 2023]  # paper Table A4 reference years

# Paper targets pulled directly from Table A4 / A2
PAPER_TOTAL = {2019: 176.2, 2020: 224.9, 2021: 150.4, 2023: 162.1}
PAPER_MED = {2019: 0.43, 2020: 0.51, 2021: 0.31, 2023: 0.40}
PAPER_POOLED_MED = 1.080


def school_year_quarters(spring_year: int) -> list[tuple[int, int]]:
    """Four quarters making up a school year ending in spring spring_year.

    (year, quarter) order: q3_prev, q4_prev, q1_curr, q2_curr.
    """
    return [(spring_year - 1, 3), (spring_year - 1, 4),
            (spring_year, 1), (spring_year, 2)]


def pull_panel(industry: str, extra: dict, label: str) -> pd.DataFrame:
    """Pull (EmpTotal, FrmJbLsS) county-quarter rows for our 3 states, 2018-2023."""
    frames: list[pd.DataFrame] = []
    for fips, _abbr in STATES:
        for time_str in ("from+2018-Q3+to+2020-Q4", "from+2021-Q1+to+2023-Q4"):
            params = {
                "get": "EmpTotal,FrmJbLsS",
                "for": "county:*",
                "in": f"state:{fips}",
                "industry": industry,
                "time": time_str,
                **extra,
            }
            try:
                df = fetch_df("sa", params)
            except Exception as e:
                print(f"  [{label}] state={fips} time={time_str}: {str(e)[:120]}")
                df = pd.DataFrame()
            if not df.empty:
                frames.append(df)
    if not frames:
        return pd.DataFrame()
    out = pd.concat(frames, ignore_index=True)
    # Parse year/quarter from the time column (e.g., "2019-Q1")
    if "time" in out.columns:
        out["year"] = out["time"].str[:4].astype(int)
        out["quarter"] = out["time"].str[-1].astype(int)
    for c in ("EmpTotal", "FrmJbLsS"):
        if c in out.columns:
            out[c] = pd.to_numeric(out[c], errors="coerce")
    out["fips"] = out["state"].astype(str).str.zfill(2) + out["county"].astype(str).str.zfill(3)
    return out


def build_school_year(panel: pd.DataFrame) -> pd.DataFrame:
    """Reduce quarterly panel to (fips, school_year) with emp_lag, nnjf, nnjf_per_100."""
    if panel.empty:
        return pd.DataFrame()
    # Index by (fips, year, quarter)
    panel = panel.dropna(subset=["EmpTotal", "year", "quarter"]).copy()
    panel["year"] = panel["year"].astype(int)
    panel["quarter"] = panel["quarter"].astype(int)
    lookup_emp = panel.set_index(["fips", "year", "quarter"])["EmpTotal"].to_dict()
    lookup_loss = panel.set_index(["fips", "year", "quarter"])["FrmJbLsS"].to_dict()

    rows = []
    fipses = panel["fips"].unique()
    for fips in fipses:
        for sy in SCHOOL_YEARS:
            qs = school_year_quarters(sy)
            emps = [lookup_emp.get((fips, y, q)) for (y, q) in qs]
            losses = [lookup_loss.get((fips, y, q)) for (y, q) in qs]
            # Need all 4 quarters present
            if any(v is None or (isinstance(v, float) and np.isnan(v)) for v in emps + losses):
                continue
            emp_lag = emps[1]  # q4 of prev year
            if not emp_lag or emp_lag <= 0:
                continue
            nnjf = float(np.mean(losses))
            rows.append({
                "fips": fips, "school_year": sy,
                "emp_lag": float(emp_lag),
                "nnjf": nnjf,
                "nnjf_per_100": 100.0 * nnjf / float(emp_lag),
            })
    return pd.DataFrame(rows)


def weighted_quantile(values: np.ndarray, weights: np.ndarray, q: float) -> float:
    i = np.argsort(values)
    c = np.cumsum(weights[i]) / weights.sum()
    return float(values[i][np.searchsorted(c, q)])


def summarize(sy: pd.DataFrame, label: str) -> dict:
    """Compute totals/medians by year + pooled, formatted like Table A4."""
    if sy.empty:
        return {"label": label, "empty": True}
    rec = {"label": label, "n_obs": int(len(sy))}
    by_year = {}
    for y in SCHOOL_YEARS:
        sub = sy[sy["school_year"] == y]
        if sub.empty:
            by_year[y] = {"total_k": np.nan, "median": np.nan}
            continue
        sub = sub[sub["emp_lag"] > 0]
        total_k = float(sub["nnjf"].sum() / 1000.0)
        v = sub["nnjf_per_100"].to_numpy()
        w = 1.0 / sub["emp_lag"].to_numpy()
        med = weighted_quantile(v, w, 0.5)
        by_year[y] = {"total_k": total_k, "median": med}
    rec["by_year"] = by_year

    sub = sy[sy["emp_lag"] > 0]
    v = sub["nnjf_per_100"].to_numpy()
    w = 1.0 / sub["emp_lag"].to_numpy()
    rec["pooled_median"] = weighted_quantile(v, w, 0.5)
    rec["pooled_mean"] = float((v * w).sum() / w.sum())
    rec["total_3state_k"] = float(sub["nnjf"].sum() / 1000.0)
    return rec


def print_summary(rec: dict) -> None:
    print(f"\n===== {rec['label']} =====")
    if rec.get("empty"):
        print("  (no data returned)")
        return
    print(f"  n_obs = {rec['n_obs']}, pooled total (3 states, 4 SY) = {rec['total_3state_k']:.1f}k")
    print(f"  pooled weighted median NNJF/100 = {rec['pooled_median']:.3f}  (paper {PAPER_POOLED_MED})")
    print(f"  pooled weighted mean   NNJF/100 = {rec['pooled_mean']:.3f}")
    print(f"  {'Year':6s}{'Total(k)':>12s}{'Paper(k)':>12s}{'Ratio':>10s}"
          f"{'Median':>10s}{'Paper':>10s}{'Ratio':>10s}")
    for y, d in rec["by_year"].items():
        pt = PAPER_TOTAL[y]; pm = PAPER_MED[y]
        ratio_t = d["total_k"] / pt if pt else np.nan
        ratio_m = d["median"] / pm if pm else np.nan
        # NB: total here is 3-state subset, so paper-total ratio is informative only
        # of magnitude *direction* (we expect << 1.0 because we sampled 3 states).
        print(f"  {y:<6d}{d['total_k']:>12.1f}{pt:>12.1f}{ratio_t:>10.2f}"
              f"{d['median']:>10.3f}{pm:>10.3f}{ratio_m:>10.2f}")


def main() -> None:
    hypotheses = [
        ("H1: NAICS 6111, default (baseline)",   "6111",   {}),
        ("H2: NAICS 6111, ownercode=A05",        "6111",   {"ownercode": "A05"}),
        ("H3: NAICS 611110 (6-digit explicit)",  "611110", {}),
        ("H4: NAICS 611 (3-digit, all educ svc)", "611",   {}),
        ("H5: NAICS 61 (2-digit, educ services sector)", "61", {}),
        ("H6: NAICS 6111 + firmage=0 + firmsize=0", "6111",
            {"firmage": "0", "firmsize": "0"}),
        ("H7: NAICS 6111 + ind_level=4",         "6111",   {"ind_level": "4"}),
    ]

    results = []
    for label, ind, extra in hypotheses:
        print(f"\n>>> Fetching {label}")
        panel = pull_panel(ind, extra, label)
        if panel.empty:
            print("  no rows returned")
            results.append({"label": label, "empty": True})
            continue
        sy = build_school_year(panel)
        rec = summarize(sy, label)
        print_summary(rec)
        results.append(rec)

    # Also: report 3-state baseline expected total for context (rough proxy:
    # AL + CO + TX share of national emp = ~10-11%, so we expect ~22k for 2020)
    print("\n\nNote: 3-state subsample (AL+CO+TX) covers roughly 10-11% of national K-12 employment.")
    print("So total-k values should be ~10-11% of the paper's national totals.")

    # Write CSV summary
    out_path = Path(__file__).resolve().parents[1] / "output" / "reports" / "agent_filters_industry_results.csv"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    rows = []
    for r in results:
        if r.get("empty"):
            rows.append({"label": r["label"], "status": "empty"})
            continue
        row = {
            "label": r["label"], "n_obs": r["n_obs"],
            "pooled_median": r["pooled_median"],
            "pooled_mean": r["pooled_mean"],
            "total_3state_k": r["total_3state_k"],
        }
        for y, d in r["by_year"].items():
            row[f"total_{y}_k"] = d["total_k"]
            row[f"median_{y}"] = d["median"]
        rows.append(row)
    pd.DataFrame(rows).to_csv(out_path, index=False)
    print(f"\nWrote {out_path}")


if __name__ == "__main__":
    main()
