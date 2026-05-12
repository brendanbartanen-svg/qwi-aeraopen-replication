# Extract A: pdfplumber `extract_tables()` — Notes

## Source
- PDF: `replication/data/raw/state_validation/va_jlarc_rpt568_pandemic_impact.pdf`
- Table: Appendix J-1 "Number of teacher vacancies by school division" (JLARC Report 568)
- Pages covered: PDF pages 153 through 157 (1-indexed). The body of J-1 begins on page 153 (with the header and first 16 division rows) and ends on page 157 (last row: York County). Page 157 also contains the SOURCE/NOTE footer and the start of Table J-2 (turnover) — those rows are excluded.

## Method
- Tool: `pdfplumber` only. `page.extract_tables(table_settings={"vertical_strategy": "text", "horizontal_strategy": "text"})`.
- No OCR, no manual transcription. All values are taken from cells returned by `extract_tables()`.
- The default `{"vertical_strategy": "lines", "horizontal_strategy": "lines"}` returned 0 tables on these pages because the PDF table has no ruled lines, so the text-based strategies were required.

## Column mapping
PDF columns -> CSV columns:
- "Division" -> `school_division`
- "PPA* # vacant" (pre-pandemic average # vacant, 5-year avg 2015-16 through 2019-20) -> `pre_pandemic_avg_vacancies` (float)
- "SY22 # vacant" (as of October 2021) -> `num_vacant_sy22` (float, preserving the one-decimal PDF formatting, e.g., 29.1)
- "SY22 % vacant" -> `pct_vacant_sy22` (string, preserved as e.g. "3%")
- "% change" (from pre-pandemic average) -> `pct_change_from_ppa` (string, preserved as e.g. "1,344%" or "-100%")

## Value-format decisions
- `pre_pandemic_avg_vacancies` and `num_vacant_sy22` are written as floats (e.g., `5.8`, `12.0`, `29.1`).
- Percentage columns are kept as exact strings from the PDF — including the trailing `%`, the thousands separators (`1,344%`), and the leading minus signs (`-100%`).
- For divisions whose PPA is `0.0` the PDF does not display a percent change (division-by-zero):
  - On the visible row for `Bristol City` and `Buckingham County` the PDF leaves the cell **blank** -> emitted as empty string `""`.
  - On the visible rows for `Nelson County`, `Salem City`, and `Sussex County` the PDF prints a literal en-dash/hyphen `-` -> emitted as `"-"`.
  These two patterns are preserved verbatim from the source.

## Post-processing fixes applied to `extract_tables()` output
The `{vertical_strategy: text, horizontal_strategy: text}` strategy returns clean rows but has three artifacts that needed deterministic, content-agnostic fixes (no manual transcription):

1. **"Alexandria City" PPA was `10.6`**: `extract_tables()` merged the leading `1` of `10.6` into the name cell, producing `"Alexandria City 1"` followed by `"0.6"`. The parser detects the pattern `<name> <single-digit>` followed by a numeric next-cell and reconstructs the leading digit into the PPA value.
2. **`-100%` cells split into `"-"` and `"100%"`**: e.g., on the row for `West Point`. The parser merges any standalone `"-"` cell with an immediately-following `<digits>%` cell into a single `-<digits>%` cell. This only fires for the percent-change column.
3. **Long division names split mid-word across cells** (e.g., `"Westmoreland Coun" + "ty"`, `"Williamsburg-James" + "City County"`): when joining the leading non-numeric cells into the division name, the parser concatenates with no separator if the next cell begins with a lowercase letter, otherwise with a single space. This recovers `"Westmoreland County"` and `"Williamsburg-James City County"` correctly.

## Stop sentinel for page 157
Page 157 contains both the tail of Table J-1 and the head of Table J-2 (turnover). The parser stops scanning rows once it encounters any of:
`SOURCE`/`OURCE`, `NOTE`/`OTE`, `TABLE J-2`/`ABLE J-2`, `Teacher turnov`/`eacher turnov` (the leading capital sometimes lands in a separate empty cell on this page, hence the truncated forms).

## Output
- Rows extracted: **132 school divisions** (Accomack County -> York County).
- This matches the JLARC report's stated count of 132 divisions.
- No duplicates.
- Header row written.
