"""Shared configuration: paths, API key loading, target values, weighted aggregations."""

from pathlib import Path
import os
import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_RAW = REPO_ROOT / "data" / "raw"
DATA_DERIVED = REPO_ROOT / "data" / "derived"
OUTPUT = REPO_ROOT / "output"
FIGURES = OUTPUT / "figures"
TABLES = OUTPUT / "tables"

QWI_CURRENT_DIR = DATA_RAW / "qwi_current"
QWI_VINTAGE_DIR = DATA_RAW / "qwi_vintage_2025q1"
STATE_VAL_DIR = DATA_RAW / "state_validation"
CCD_DIR = DATA_RAW / "ccd"
POLICY_DIR = DATA_RAW / "policy"

NAICS_K12 = "6111"
QWI_API_BASE = "https://api.census.gov/data/timeseries/qwi"

AUTHORS_EXTRACTION_DATE = "2025-03-05"
AUTHORS_LATEST_QUARTER = "2024-Q2"


def census_api_key() -> str:
    key = os.environ.get("CENSUS_API_KEY")
    if not key or key == "your_key_here":
        env_path = REPO_ROOT / ".env"
        if env_path.exists():
            for line in env_path.read_text().splitlines():
                line = line.strip()
                if line.startswith("CENSUS_API_KEY="):
                    key = line.split("=", 1)[1].strip().strip('"').strip("'")
                    break
    if not key or key == "your_key_here":
        raise RuntimeError(
            "Census API key not found. Add it to "
            f"{REPO_ROOT}/.env as CENSUS_API_KEY=... "
            "(get one at https://api.census.gov/data/key_signup.html)."
        )
    return key


def stata_aweight_sum(x, w):
    """Reproduce Stata's `collapse (sum) x [aw=w]` exactly.

    Stata's analytic weights for (sum):
        sum(x_i * w_i * N / sum(w_j))
    where N = number of non-missing obs.

    This is what the authors use for Table A4 'NNJF Total' and Table A8 'NNJF Total'.
    Pass `w = 1/fte` (or `1/emp_lag` as a proxy) to match the paper.
    """
    x = np.asarray(x, dtype=float)
    w = np.asarray(w, dtype=float)
    mask = (~np.isnan(x)) & (~np.isnan(w)) & (w > 0)
    x = x[mask]; w = w[mask]
    if len(x) == 0:
        return float("nan")
    N = len(x)
    return float((x * w * N / w.sum()).sum())


def stata_aweight_mean(x, w):
    """Stata's `collapse (mean) x [aw=w]` — standard weighted mean."""
    x = np.asarray(x, dtype=float)
    w = np.asarray(w, dtype=float)
    mask = (~np.isnan(x)) & (~np.isnan(w)) & (w > 0)
    x = x[mask]; w = w[mask]
    if len(x) == 0:
        return float("nan")
    return float((x * w).sum() / w.sum())


def stata_aweight_quantile(x, w, q):
    """Stata's `summarize x [aw=w], detail` percentiles.

    Stata uses interpolated weighted percentile. Approximation: sort, cum-weight,
    find first index where cumsum/total >= q.
    """
    x = np.asarray(x, dtype=float)
    w = np.asarray(w, dtype=float)
    mask = (~np.isnan(x)) & (~np.isnan(w)) & (w > 0)
    x = x[mask]; w = w[mask]
    if len(x) == 0:
        return float("nan")
    idx = np.argsort(x)
    cw = np.cumsum(w[idx]) / w.sum()
    i = np.searchsorted(cw, q)
    i = min(i, len(x) - 1)
    return float(x[idx][i])
