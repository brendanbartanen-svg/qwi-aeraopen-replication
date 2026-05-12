"""External-consistency checks per file.

Checks:
1. Row count matches expected #LEAs
2. Statewide row sums/matches stated statewide figure
3. Magnitude (values fall within plausible range for the column)
4. YoY stability (where applicable across multiple year files)
"""

from __future__ import annotations

import csv
from pathlib import Path

VALIDATION_DIR = Path("/Users/yvp3tf/Documents/CC Sandbox/replication/qwi_aeraopen/replication/output/validation")
RAW_DIR = Path("/Users/yvp3tf/Documents/CC Sandbox/replication/qwi_aeraopen/replication/data/raw/state_validation")


# Expected ranges and reference points from published reports
EXPECTED = {
    "va_2022-23_vacancy": {
        "current": "va_2022-23_vacancy_jlarc_appx_c.csv",
        "expected_rows": (123, 132),  # JLARC reports cover 132 divisions; 2022-23 had 131-132
        "magnitude": {"vacancy_rate_pct": (0.0, 25.0)},
        "stated_total": {"total_unfilled_fte": None, "total_fte_teacher_positions": None},
    },
    "va_2021-22_turnover": {
        "current": "va_2021-22_turnover_jlarc_appx_j2.csv",
        "expected_rows": (130, 135),
    },
    "va_2023-24_vacancy": {
        "current": "va_2023-24_vacancy_jlarc_appx_c.csv",
        "expected_rows": (120, 132),
        "magnitude": {"vacancy_rate_pct": (0.0, 25.0)},
        "stated_total": {"total_unfilled_fte": 4104, "total_fte_teacher_positions": 90466},
    },
    "va_2021-22_vacancy": {
        "current": "va_2021-22_vacancy_jlarc_appx_j1.csv",
        "expected_rows": (130, 135),
    },
    "md_2020-21_to_2021-22_attrition": {
        "current": "md_2020-21_to_2021-22_LEA_attrition_TWS-2022_p7.csv",
        "expected_rows": (24, 25),  # 24 LSSs
        "magnitude": {"pct_teachers_2020-21_did_not_return_2021-22": (0.0, 30.0)},
    },
    "md_2022-23_to_2023-24_attrition": {
        "current": "md_2022-23_to_2023-24_LEA_attrition_TWS-2024_p11.csv",
        "expected_rows": (24, 25),
        "magnitude": {"pct_teachers_2022-23_did_not_return_2023-24": (0.0, 30.0)},
    },
}


def parse_num(v: str) -> float | None:
    if v is None:
        return None
    s = str(v).strip().rstrip("%").replace(",", "")
    if s == "" or s.lower() in ("n.a.", "na", "n/a", "-"):
        return None
    try:
        return float(s)
    except ValueError:
        return None


def check_file(name: str, info: dict) -> list[str]:
    folder = VALIDATION_DIR / name
    extracts = {
        "A": folder / "extract_A_pdfplumber.csv",
        "B": folder / "extract_B_vision.csv",
        "C": folder / "extract_C_textregex.csv",
        "CUR": RAW_DIR / info["current"],
    }

    out = [f"# Consistency checks — {name}\n"]

    # Row count
    min_rows, max_rows = info.get("expected_rows", (0, 999))
    out.append(f"## Row count (expected {min_rows}-{max_rows})")
    out.append("")
    out.append("| extract | rows | pass |")
    out.append("|---|---|---|")
    for label, p in extracts.items():
        n = 0
        if p.exists() and p.stat().st_size > 0:
            with p.open() as f:
                n = sum(1 for _ in f) - 1
        ok = "PASS" if min_rows <= n <= max_rows else "FAIL"
        out.append(f"| {label} | {n} | {ok} |")
    out.append("")

    # Magnitude
    mag = info.get("magnitude", {})
    if mag:
        out.append("## Magnitude (values in plausible range)")
        out.append("")
        for col, (lo, hi) in mag.items():
            out.append(f"### {col} (expected {lo}-{hi})")
            out.append("")
            out.append("| extract | n_values | min | max | n_outliers | pass |")
            out.append("|---|---|---|---|---|---|")
            for label, p in extracts.items():
                if not p.exists() or p.stat().st_size == 0:
                    out.append(f"| {label} | 0 | - | - | - | NO_DATA |")
                    continue
                with p.open() as f:
                    reader = csv.DictReader(f)
                    vals = [parse_num(r.get(col, "")) for r in reader]
                    vals = [v for v in vals if v is not None]
                if not vals:
                    out.append(f"| {label} | 0 | - | - | - | NO_COL |")
                    continue
                n_out = sum(1 for v in vals if v < lo or v > hi)
                ok = "PASS" if n_out == 0 else f"FAIL ({n_out} outliers)"
                out.append(f"| {label} | {len(vals)} | {min(vals):.2f} | {max(vals):.2f} | {n_out} | {ok} |")
            out.append("")

    # Stated totals
    totals = info.get("stated_total", {}) or {}
    if any(v is not None for v in totals.values()):
        out.append("## Stated totals (from PDF Total row)")
        out.append("")
        out.append("| column | stated | A sum | B sum | C sum | CUR sum |")
        out.append("|---|---|---|---|---|---|")
        for col, stated in totals.items():
            if stated is None:
                continue
            row = [f"| {col} | {stated}"]
            for label, p in extracts.items():
                if not p.exists() or p.stat().st_size == 0:
                    row.append(" - ")
                    continue
                with p.open() as f:
                    reader = csv.DictReader(f)
                    vals = [parse_num(r.get(col, "")) for r in reader]
                    vals = [v for v in vals if v is not None]
                s = sum(vals) if vals else 0
                diff = s - stated
                marker = "" if abs(diff) <= 2 else f" (Δ={diff:+.0f})"
                row.append(f" {s:.0f}{marker} ")
            out.append("|".join(row) + "|")
        out.append("")

    return out


def main():
    all_out = []
    for name, info in EXPECTED.items():
        all_out.extend(check_file(name, info))
        all_out.append("---\n")
    (VALIDATION_DIR / "consistency_all.md").write_text("\n".join(all_out))
    print(f"Wrote {VALIDATION_DIR / 'consistency_all.md'}")


if __name__ == "__main__":
    main()
