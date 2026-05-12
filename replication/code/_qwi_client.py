"""Thin client around the Census QWI API."""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.parse
import urllib.request

import pandas as pd

from _config import QWI_API_BASE, census_api_key

US_STATE_FIPS = [
    "01", "02", "04", "05", "06", "08", "09", "10", "11", "12",
    "13", "15", "16", "17", "18", "19", "20", "21", "22", "23",
    "24", "25", "26", "27", "28", "29", "30", "31", "32", "33",
    "34", "35", "36", "37", "38", "39", "40", "41", "42", "44",
    "45", "46", "47", "48", "49", "50", "51", "53", "54", "55",
    "56",
]


def _fetch_json(endpoint: str, params: dict, retries: int = 3, timeout: int = 90) -> list:
    """One QWI API request, returns parsed JSON (list of lists)."""
    p = dict(params)
    p["key"] = census_api_key()
    url = f"{QWI_API_BASE}/{endpoint}?{urllib.parse.urlencode(p, safe='+:')}"
    last_err: Exception | None = None
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(url, timeout=timeout) as resp:
                body = resp.read()
            if not body.strip():
                return []
            try:
                return json.loads(body)
            except json.JSONDecodeError:
                return []
        except urllib.error.HTTPError as e:
            body = e.read().decode(errors="replace")[:300]
            # 204 = no content; treat as empty result
            if e.code == 204:
                return []
            last_err = RuntimeError(f"HTTP {e.code} on {endpoint}: {body}")
            if e.code in (500, 502, 503, 504):
                time.sleep(2 ** attempt)
                continue
            raise last_err
        except urllib.error.URLError as e:
            last_err = e
            time.sleep(2 ** attempt)
    raise last_err  # type: ignore[misc]


def fetch_df(endpoint: str, params: dict) -> pd.DataFrame:
    """Convenience wrapper returning a DataFrame (empty if 204)."""
    data = _fetch_json(endpoint, params)
    if not data:
        return pd.DataFrame()
    header = data[0]
    rows = data[1:]
    return pd.DataFrame(rows, columns=header)


def pull_state_chunked_by_years(
    endpoint: str,
    state_fips: str,
    *,
    industry: str = "6111",
    geography: str = "county:*",
    get_vars: tuple[str, ...] = ("EmpTotal", "HirN"),
    extra_params: dict | None = None,
    start_year: int = 2000,
    end_quarter: str = "2024-Q2",
    chunk_years: int = 6,
) -> pd.DataFrame:
    """Pull all quarters for a state, chunked over year ranges to stay under cell limits."""
    extra = extra_params or {}
    end_year = int(end_quarter.split("-")[0])
    end_q_n = int(end_quarter.split("-Q")[1])
    chunks: list[pd.DataFrame] = []
    yr = start_year
    while yr <= end_year:
        yr_to = min(yr + chunk_years - 1, end_year)
        time_from = f"{yr}-Q1"
        time_to = f"{yr_to}-Q4" if yr_to < end_year else end_quarter
        params = {
            "get": ",".join(get_vars),
            "for": geography,
            "industry": industry,
            "time": f"from+{time_from}+to+{time_to}",
            **extra,
        }
        # Only include the `in` parameter when pulling a sub-geography (e.g. county under state)
        if not geography.startswith("state:"):
            params["in"] = f"state:{state_fips}"
        df = fetch_df(endpoint, params)
        if not df.empty:
            chunks.append(df)
        yr = yr_to + 1
    if not chunks:
        return pd.DataFrame()
    return pd.concat(chunks, ignore_index=True)
