"""Smoke test: verifies the Census API key is loaded and the QWI endpoint responds.

Usage: python replication/code/00_test_api.py
"""

import json
import urllib.parse
import urllib.request

from _config import QWI_API_BASE, census_api_key


def fetch(endpoint: str, params: dict) -> list:
    url = f"{QWI_API_BASE}/{endpoint}?{urllib.parse.urlencode(params)}"
    print(f"GET {endpoint}  ({', '.join(f'{k}={v}' for k, v in params.items() if k != 'key')})")
    with urllib.request.urlopen(url, timeout=30) as resp:
        return json.loads(resp.read())


def main() -> None:
    key = census_api_key()
    common = dict(
        industry="6111",
        year="2023",
        quarter="1",
        key=key,
    )

    # State-level, sex × age endpoint — what the main pull will use
    data = fetch(
        "sa",
        {"get": "EmpTotal,HirN,Emp,EmpS,sex,industry", "for": "state:01", **common},
    )
    print("Alabama state-level rows:")
    for row in data:
        print("  ", row)

    # County-level test
    print()
    data = fetch(
        "sa",
        {"get": "EmpTotal,HirN,sex", "for": "county:*", "in": "state:01", **common},
    )
    print(f"Alabama county-level: {len(data) - 1} rows (header: {data[0]})")
    print("First 3 data rows:")
    for row in data[1:4]:
        print("  ", row)


if __name__ == "__main__":
    main()
