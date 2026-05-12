"""Extract SY 2022-23 (left column) from JLARC Report 576 Appendix C, Table C-1.

Method:
  - pdfplumber.page.extract_text(layout=True) preserves column positions.
  - For each table page (1-indexed 66-70, 0-indexed 65-69), slice characters
    [0:44] to isolate the LEFT block (SY 2022-23). Column boundary 44 was
    determined by inspecting the header column positions and verifying many
    data rows: row content always ends by column 43, right-column content
    always begins at column 45.
  - Walk LEFT slices line-by-line. Three regex classes match data lines:
      * TRAILING_RE      -> name + three numeric fields on one line
      * NUMBERS_ONLY_RE  -> three numeric fields with no name (continuation)
      * TOTAL_RE         -> "Total <fte> <unfilled>" (rate column absent)
    A line that is pure text (no numbers) is either:
      * a continuation suffix of the just-emitted row (if it set
        _needs_suffix=True), or
      * a name prefix for the next numbers-bearing row.
"""
from __future__ import annotations

import csv
import re
from pathlib import Path

import pdfplumber

PDF_PATH = Path(
    "/Users/yvp3tf/Documents/CC Sandbox/replication/qwi_aeraopen/replication/data/raw/state_validation/va_jlarc_rpt576_teacher_pipeline.pdf"
)
OUT_CSV = Path(
    "/Users/yvp3tf/Documents/CC Sandbox/replication/qwi_aeraopen/replication/output/validation/va_2022-23_vacancy/extract_C_textregex.csv"
)

PAGE_INDICES = [65, 66, 67, 68, 69]  # PDF pages 66-70 (1-indexed)
LEFT_SLICE_END = 44

NUM = r"(\d{1,3}(?:,\d{3})*|-)"
RATE = r"(\d+\.\d+|-)"
TRAILING_RE = re.compile(rf"^(?P<name>.*?)\s+(?P<fte>{NUM})\s+(?P<unfilled>{NUM})\s+(?P<rate>{RATE})\s*$")
NUMBERS_ONLY_RE = re.compile(rf"^\s+(?P<fte>{NUM})\s+(?P<unfilled>{NUM})\s+(?P<rate>{RATE})\s*$")
TOTAL_RE = re.compile(rf"^\s*Total\s+(?P<fte>{NUM})\s+(?P<unfilled>{NUM})\s*$")


def parse_int(s: str) -> int:
    return 0 if s == "-" else int(s.replace(",", ""))


def parse_rate(s: str) -> float:
    # "-" in the rate column means 0.0 (no vacancies; the SY2023-24 column
    # explicitly renders these as 0.0 for the corresponding divisions).
    return 0.0 if s == "-" else float(s)


# Patterns recognising lines that are NOT data (headers, page numbers, notes, etc.).
SKIP_PREFIXES = (
    "Appen",  # "Appendixes" running header (truncated to "Appen" at col 44)
    "TABLE ",
    "Public K",
    "This appendix",
    "Data shows",
    "encing zero",
    "and least teacher",
    "Department of Education",
    "Total FTE",
    "teacher",  # subtitle "teacher FTE teacher Vacancy"
    "School division",
    "SOURCE:",
    "NOTE:",
    "SY2022",  # plain header strip
    "SY2023",  # plain header strip + NOTE continuation
    "123 divisions",
)


def is_skip(stripped: str) -> bool:
    if not stripped:
        return True
    if stripped.startswith(SKIP_PREFIXES):
        return True
    if re.fullmatch(r"\d+", stripped):  # bare page number e.g. "52"
        return True
    return False


def collect_left_lines() -> list[str]:
    out: list[str] = []
    with pdfplumber.open(PDF_PATH) as pdf:
        for pidx in PAGE_INDICES:
            text = pdf.pages[pidx].extract_text(layout=True)
            for raw in text.split("\n"):
                left = raw[:LEFT_SLICE_END].rstrip()
                stripped = left.strip()
                if is_skip(stripped):
                    continue
                out.append(left)
    return out


def stitch(a: str, b: str) -> str:
    """Join two name fragments. No space if first ends with hyphen."""
    a = a.rstrip()
    b = b.strip()
    if not a:
        return b
    if not b:
        return a
    if a.endswith("-"):
        return a + b
    return a + " " + b


def parse_rows(lines: list[str]) -> list[dict]:
    rows: list[dict] = []
    pending_prefix = ""  # accumulated name fragment(s) waiting for an upcoming numbers row

    for line in lines:
        stripped = line.strip()

        # Total row (no rate column)
        m = TOTAL_RE.match(line)
        if m:
            rows.append(
                {
                    "school_division": "Total",
                    "total_fte_teacher_positions": parse_int(m.group("fte")),
                    "total_unfilled_fte": parse_int(m.group("unfilled")),
                    "vacancy_rate_pct": None,
                    "_needs_suffix": False,
                }
            )
            pending_prefix = ""
            continue

        # Numbers-only continuation: belongs to pending_prefix (may be empty)
        m = NUMBERS_ONLY_RE.match(line)
        if m:
            name = pending_prefix
            pending_prefix = ""
            rows.append(
                {
                    "school_division": name,
                    "total_fte_teacher_positions": parse_int(m.group("fte")),
                    "total_unfilled_fte": parse_int(m.group("unfilled")),
                    "vacancy_rate_pct": parse_rate(m.group("rate")),
                    "_needs_suffix": True,  # next pure-text line may be the name suffix
                }
            )
            continue

        # Name + numbers row
        m = TRAILING_RE.match(line)
        if m:
            name_in_line = m.group("name").strip()
            had_pending = bool(pending_prefix)
            full_name = stitch(pending_prefix, name_in_line) if pending_prefix else name_in_line
            pending_prefix = ""
            rows.append(
                {
                    "school_division": full_name,
                    "total_fte_teacher_positions": parse_int(m.group("fte")),
                    "total_unfilled_fte": parse_int(m.group("unfilled")),
                    "vacancy_rate_pct": parse_rate(m.group("rate")),
                    # A suffix line follows only when the name in the table was
                    # wrapped across lines (i.e., pending_prefix was non-empty).
                    "_needs_suffix": had_pending,
                }
            )
            continue

        # Pure text line.  Either suffix of the just-emitted row OR prefix for the next.
        if rows and rows[-1]["_needs_suffix"]:
            rows[-1]["school_division"] = stitch(rows[-1]["school_division"], stripped)
            rows[-1]["_needs_suffix"] = False
            continue
        pending_prefix = stitch(pending_prefix, stripped)

    for r in rows:
        r.pop("_needs_suffix", None)
    return rows


def main():
    lines = collect_left_lines()
    rows = parse_rows(lines)

    sum_fte = sum(r["total_fte_teacher_positions"] for r in rows if r["school_division"] != "Total")
    sum_unfilled = sum(r["total_unfilled_fte"] for r in rows if r["school_division"] != "Total")
    total_row = next((r for r in rows if r["school_division"] == "Total"), None)

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUT_CSV.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["school_division", "total_fte_teacher_positions", "total_unfilled_fte", "vacancy_rate_pct"])
        for r in rows:
            rate = r["vacancy_rate_pct"]
            w.writerow(
                [
                    r["school_division"],
                    r["total_fte_teacher_positions"],
                    r["total_unfilled_fte"],
                    "" if rate is None else rate,  # rate is None only for the Total row
                ]
            )

    n_div = sum(1 for r in rows if r["school_division"] != "Total")
    print(f"division rows: {n_div}")
    print(f"sum FTE (divs): {sum_fte}  ; Total row FTE: {total_row['total_fte_teacher_positions']}  ; diff: {sum_fte - total_row['total_fte_teacher_positions']}")
    print(f"sum Unfilled (divs): {sum_unfilled}  ; Total row Unfilled: {total_row['total_unfilled_fte']}  ; diff: {sum_unfilled - total_row['total_unfilled_fte']}")


if __name__ == "__main__":
    main()
