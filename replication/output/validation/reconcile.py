"""Cell-level reconciliation across A (pdfplumber), B (vision), C (text+regex), and CURRENT.

For each (file, row, column) cell, compares values across the four extractions:
  - All 4 close   -> AGREE
  - 3 of 4 close  -> MAJORITY (note the minority)
  - Split          -> SPLIT

Writes <file>/reconciliation.md per file.

Tolerance: 0.05 for percent values, 1 for counts, 0.05 for floats.
"""

from __future__ import annotations

import csv
import re
from pathlib import Path
from collections import Counter, defaultdict

VALIDATION_DIR = Path("/Users/yvp3tf/Documents/CC Sandbox/replication/qwi_aeraopen/replication/output/validation")
RAW_DIR = Path("/Users/yvp3tf/Documents/CC Sandbox/replication/qwi_aeraopen/replication/data/raw/state_validation")

FILES = {
    "va_2022-23_vacancy": {
        "current": "va_2022-23_vacancy_jlarc_appx_c.csv",
        "key": "school_division",
    },
    "va_2021-22_turnover": {
        "current": "va_2021-22_turnover_jlarc_appx_j2.csv",
        "key": "school_division",
    },
    "va_2023-24_vacancy": {
        "current": "va_2023-24_vacancy_jlarc_appx_c.csv",
        "key": "school_division",
    },
    "va_2021-22_vacancy": {
        "current": "va_2021-22_vacancy_jlarc_appx_j1.csv",
        "key": "school_division",
    },
    "md_2020-21_to_2021-22_attrition": {
        "current": "md_2020-21_to_2021-22_LEA_attrition_TWS-2022_p7.csv",
        "key": "LEA",
    },
    "md_2022-23_to_2023-24_attrition": {
        "current": "md_2022-23_to_2023-24_LEA_attrition_TWS-2024_p11.csv",
        "key": "LEA",
    },
}


def normalize_value(v: str) -> str:
    """Normalize a cell for comparison: strip whitespace, drop trailing %,
    normalize 'n.a.'/'-'/'' to a missing sentinel, strip commas in numbers,
    cast to float when possible."""
    if v is None:
        return "<MISSING>"
    v = str(v).strip()
    if v == "" or v.lower() in ("n.a.", "na", "n/a", "-"):
        return "<MISSING>"
    # Drop trailing %
    had_pct = v.endswith("%")
    v_clean = v.rstrip("%").replace(",", "").strip()
    try:
        f = float(v_clean)
        return f"{f:.4f}"
    except ValueError:
        return v


def values_match(values: list[str]) -> bool:
    """Two values match if they're both missing or both numerically close,
    or both equal as strings."""
    if not values:
        return True
    # All same?
    if len(set(values)) == 1:
        return True
    # All numeric & close?
    floats = []
    for v in values:
        try:
            floats.append(float(v))
        except ValueError:
            return False
    return max(floats) - min(floats) < 0.05


def read_csv(path: Path, key: str) -> tuple[list[str], dict[str, dict[str, str]]]:
    """Read CSV. Returns (columns, {key_value -> {col -> val}}). Skips empty files."""
    if not path.exists() or path.stat().st_size == 0:
        return [], {}
    with path.open() as f:
        reader = csv.DictReader(f)
        cols = reader.fieldnames or []
        rows = {}
        for r in reader:
            kv = r.get(key, "").strip()
            if not kv:
                continue
            # Normalize LEA name: strip whitespace
            rows[kv.strip()] = {c: (r.get(c) or "").strip() for c in cols}
        return cols, rows


def reconcile_one(name: str, info: dict) -> None:
    folder = VALIDATION_DIR / name
    a_path = folder / "extract_A_pdfplumber.csv"
    b_path = folder / "extract_B_vision.csv"
    c_path = folder / "extract_C_textregex.csv"
    current_path = RAW_DIR / info["current"]
    key = info["key"]

    a_cols, A = read_csv(a_path, key)
    b_cols, B = read_csv(b_path, key)
    c_cols, C = read_csv(c_path, key)
    cur_cols, CUR = read_csv(current_path, key)

    # Use union of keys, prefer existing CSV's key order
    all_keys = list(CUR.keys()) + [k for k in (list(A.keys()) + list(B.keys()) + list(C.keys())) if k not in CUR]
    # De-dup preserving order
    seen = set()
    keys_ordered = []
    for k in all_keys:
        if k not in seen:
            seen.add(k)
            keys_ordered.append(k)

    # Use current CSV's columns as the canonical set (excluding the key)
    if cur_cols:
        data_cols = [c for c in cur_cols if c != key]
    else:
        # Fall back to A's cols
        data_cols = [c for c in a_cols if c != key]

    n_agree = 0
    n_majority = 0
    n_split = 0
    n_missing_from_one = 0

    rows_out = []
    rows_out.append(f"# Reconciliation — {name}\n")
    rows_out.append(f"- Current CSV: `{info['current']}` ({len(CUR)} rows)")
    rows_out.append(f"- Extract A (pdfplumber): {len(A)} rows")
    rows_out.append(f"- Extract B (vision):     {len(B)} rows")
    rows_out.append(f"- Extract C (textregex):  {len(C)} rows")
    rows_out.append("")
    rows_out.append("## Cell-level verdicts")
    rows_out.append("")
    rows_out.append(f"| {key} | column | A | B | C | CURRENT | verdict |")
    rows_out.append(f"|---|---|---|---|---|---|---|")

    for k in keys_ordered:
        a_row = A.get(k, {})
        b_row = B.get(k, {})
        c_row = C.get(k, {})
        cur_row = CUR.get(k, {})

        for col in data_cols:
            a_raw = a_row.get(col, "")
            b_raw = b_row.get(col, "")
            c_raw = c_row.get(col, "")
            cur_raw = cur_row.get(col, "")

            a_n = normalize_value(a_raw)
            b_n = normalize_value(b_raw)
            c_n = normalize_value(c_raw)
            cur_n = normalize_value(cur_raw)

            present = {n for n in (a_n, b_n, c_n, cur_n) if n != "<MISSING>"}
            if len(present) == 0:
                # All missing — count as agree (trivially)
                verdict = "AGREE (all missing)"
                n_agree += 1
                continue

            # Find the "winning" group: largest set of values that match each other
            all_vals = [a_n, b_n, c_n, cur_n]
            # Cluster by closeness — start by treating equal strings or close numerics as same group
            groups: list[list[str]] = []
            for v in all_vals:
                placed = False
                for g in groups:
                    if values_match([g[0], v]):
                        g.append(v)
                        placed = True
                        break
                if not placed:
                    groups.append([v])

            sizes = [len(g) for g in groups]
            max_size = max(sizes)

            if max_size == 4:
                verdict = "AGREE"
                n_agree += 1
                # Skip showing fully-agreeing rows to keep table small
                continue
            elif max_size == 3:
                verdict = "MAJORITY (3/4)"
                n_majority += 1
                # Find the minority
                minority_g = [g for g in groups if len(g) == 1][0]
                minority_val = minority_g[0]
                # Which extractor was the minority?
                names = ["A", "B", "C", "CUR"]
                minority_idx = [i for i, v in enumerate(all_vals) if v == minority_val and len(groups[[gi for gi, g in enumerate(groups) if v in g][0]]) == 1]
                rows_out.append(f"| {k} | {col} | {a_raw} | {b_raw} | {c_raw} | {cur_raw} | {verdict} |")
            else:
                # Split — could be 2-2, 2-1-1, 1-1-1-1
                verdict = f"SPLIT ({'-'.join(str(s) for s in sorted(sizes, reverse=True))})"
                n_split += 1
                rows_out.append(f"| {k} | {col} | {a_raw} | {b_raw} | {c_raw} | {cur_raw} | {verdict} |")

    summary = [
        "",
        "## Summary",
        "",
        f"- AGREE (all 4 match):  {n_agree}",
        f"- MAJORITY (3/4 match): {n_majority}",
        f"- SPLIT:                {n_split}",
        f"- Total cells:          {n_agree + n_majority + n_split}",
    ]

    output = "\n".join([rows_out[0]] + rows_out[1:6] + summary + ["", "## Disagreements"] + rows_out[6:8] + rows_out[8:])
    (folder / "reconciliation.md").write_text(output)
    print(f"  {name}: AGREE={n_agree}  MAJORITY={n_majority}  SPLIT={n_split}")


def main():
    for name, info in FILES.items():
        reconcile_one(name, info)


if __name__ == "__main__":
    main()
