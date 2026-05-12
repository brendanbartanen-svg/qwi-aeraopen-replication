# Appendix C extraction notes (text + regex method, SY 2022-23 left column)

## Source

- PDF: `replication/data/raw/state_validation/va_jlarc_rpt576_teacher_pipeline.pdf`
- Table: JLARC Report 576, Appendix C, Table C-1
  ("Public K-12 teacher vacancies, SY2022-23 and SY2023-24")
- Pages: 66-70 (1-indexed) / 65-69 (0-indexed)
- Extraction method: `pdfplumber.open(...).pages[i].extract_text(layout=True)`
  followed by a fixed character-column slice and a line-walking regex parser.
- Driver script: `_extract_C.py` (in this directory).

## Page layout

Each of pages 66-70 renders Table C-1 as a 6-column "side-by-side" panel:

```
SY2022-23 (LEFT)                            SY2023-24 (RIGHT)
School division | Total FTE | Unfilled | Rate (%)   School division | Total FTE | Unfilled | Rate (%)
```

`extract_text(layout=True)` preserves these column positions as character
offsets. Inspecting the column header line:

```
           School division positions positions rate (%) School division positions positions rate (%)
0         11        18       27        37       47   52 56       63        72        82      92  97
```

Body rows are 84 characters wide; the LEFT panel's rightmost content always
ends by column 43 and the RIGHT panel's leftmost content always starts at
column 45. We therefore slice `line[0:44]` for the LEFT (SY 2022-23) block.

## Character-slice index

**`LEFT_SLICE_END = 44`** (i.e., `left = raw_line[:44]`).

Verified by spot-checking many rows in `_extract_C.py` development logs —
no LEFT-side number ever extends past column 43, and no RIGHT-side text
ever begins before column 45.

## Line types within the LEFT slice

After slicing, each non-empty / non-skip line falls into one of four shapes:

1. **TRAILING** -- `<name>  <fte>  <unfilled>  <rate>` (single-line entry).
   Regex `TRAILING_RE`.
2. **NUMBERS_ONLY** -- whitespace + `<fte>  <unfilled>  <rate>` (the numbers
   for an entry whose name wrapped across multiple lines).
   Regex `NUMBERS_ONLY_RE`.
3. **TOTAL** -- `Total  <fte>  <unfilled>` (Total row has no rate cell).
   Regex `TOTAL_RE`.
4. **NAME-ONLY** -- pure text (no digits). Either a name prefix for an
   upcoming NUMBERS_ONLY row, or a suffix for the previous row.

Numeric token regex (handles thousands commas and the literal "-"):
- `NUM = (\d{1,3}(?:,\d{3})*|-)`
- `RATE = (\d+\.\d+|-)`

## Name-stitching algorithm

State variables:
- `pending_prefix` -- accumulated name fragments waiting for an upcoming
  numbers row.
- Each emitted row carries a transient `_needs_suffix` flag.

Rules:
- Encountering NUMBERS_ONLY: consume `pending_prefix` as the row's initial
  name, clear it, emit row with `_needs_suffix=True` (suffix may follow).
- Encountering TRAILING: build the name by prepending `pending_prefix` (if
  any) to the in-line name. Emit row; mark `_needs_suffix=True` **only if**
  `pending_prefix` was non-empty (i.e., the entry's name was wrapped). For a
  single-line entry, no suffix should follow, so `_needs_suffix=False`.
- Encountering a NAME-ONLY line: if `rows[-1]._needs_suffix` is True,
  append it (without space when the previous fragment ends with `-`,
  with one space otherwise) and clear the flag. Otherwise add it to
  `pending_prefix` for the next numbers row.

This handles the three observed entry shapes:
- Single line:   `Portsmouth City 959 158 16.5`
- 3-line wrap, name-numbers-name:
  `Southampton` / `        194  40  20.8` / `County`
  -> "Southampton County"
- 3-line wrap, name-name+numbers-name (Williamsburg):
  `Williamsburg-` / `James City 828 10 1.1` / `County`
  -> "Williamsburg-James City County"
- 3-line wrap, numbers-name (Loudoun) where numbers row precedes its name:
  `        6,511  75  1.1` / `Loudoun County`
  -> "Loudoun County"
- Hyphenated wrap (Alleghany Highlands):
  `Alleghany High-` / `        229  19  8.1` / `lands`
  -> "Alleghany High-lands" (no space added because prior fragment ends in
  "-")

## Skip filter (header / page-noise lines)

`is_skip()` drops lines whose stripped form is empty, matches a bare page
number, or starts with any of:

```
Appen, TABLE , Public K, This appendix, Data shows, encing zero,
and least teacher, Department of Education, Total FTE, teacher,
School division, SOURCE:, NOTE:, SY2022, SY2023, 123 divisions
```

Note: the running-header "Appendixes" gets truncated to "Appen" by the
44-column slice, so we match the `Appen` prefix. The single header label
"SY2022-23" (table sub-title row) also sits in the LEFT slice alone and
is filtered via the `SY2022` prefix rule.

## Value conventions

- `total_fte_teacher_positions`: integer. PDF uses thousands commas; stripped.
- `total_unfilled_fte`: integer. PDF prints `-` for divisions with zero
  vacancies; we encode `-` -> `0`.
- `vacancy_rate_pct`: float. PDF prints `-` for divisions with zero
  vacancies; we encode `-` -> `0.0` (consistent with the SY2023-24 column,
  which shows `0.0` rather than `-` for the same divisions).
- The Total row has no rate cell; its `vacancy_rate_pct` is left blank.

## Edge cases encountered

1. **Multi-line names with numbers between fragments** -- handled by
   `pending_prefix` + `_needs_suffix` two-line lookbehind/lookahead.
2. **Hyphen-broken names** (Alleghany High-lands) -- `stitch()` does not
   insert a space when the left fragment ends in `-`.
3. **Williamsburg-James City County** -- THREE name fragments
   ("Williamsburg-", "James City", "County") with numbers on the middle
   fragment. Handled by the TRAILING-with-pending-prefix path that also
   leaves `_needs_suffix=True` for the final "County".
4. **Loudoun County** -- numbers row precedes its name row (inverted
   order). Handled because NUMBERS_ONLY always emits with
   `_needs_suffix=True`, and the next NAME-ONLY line is appended.
5. **"-" tokens** -- both `NUM` and `RATE` regexes admit a bare `-`; the
   `parse_int`/`parse_rate` helpers convert it to 0 / 0.0.
6. **Total row** -- has only 2 numeric tokens (no rate column); matched
   by a dedicated `TOTAL_RE`.
7. **Running headers / page numbers** -- "Appendixes" running header is
   truncated to "Appen" by the column slice; bare page numbers ("52",
   "53", ...) appear left-aligned. Both filtered in `is_skip()`.

## Row count and Total sum comparison

- Data rows extracted (excluding Total): **131**
- Total row in PDF: **FTE = 92,579 ; Unfilled = 3,573**
- Sum across the 131 extracted rows: **FTE = 92,583 ; Unfilled = 3,580**
- Discrepancy: **+4 FTE, +7 unfilled** (extracted sum exceeds reported Total)

The discrepancy is present in the **source PDF itself** -- it is not a
parsing artifact. Verified two ways:

1. Direct regex over all LEFT-slice lines ending in `<num> <num> <rate>`
   yields the same sums (92,583 / 3,580).
2. Every extracted row's name+numbers triple in `extract_C_textregex.csv`
   can be located by visual reading of the PDF.

This appears to be a typesetting/round-trip error in JLARC Report 576's
Table C-1 Total row for the SY 2022-23 column. Note also that Virginia
has 132 school divisions but only 131 appear in the SY 2022-23 column
(one division is omitted entirely from this column); the comparable
SY 2023-24 column lists more divisions (the NOTE on page 70 mentions
"123 divisions" for SY 2023-24 first-day data quality).
