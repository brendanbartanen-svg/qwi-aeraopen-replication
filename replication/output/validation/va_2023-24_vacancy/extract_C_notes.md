# Extract C: Text + Regex Extraction Notes

## Source
- **PDF**: `replication/data/raw/state_validation/va_jlarc_rpt576_teacher_pipeline.pdf`
- **Pages**: 66-70 (1-indexed); Appendix C, Table C-1 "Public K-12 teacher vacancies, SY2022-23 and SY2023-24"
- **Other candidate** `va_jlarc_rpt576_appendixes.pdf` is only 5 pages and does not contain this table.

## Year label found in source text
- Header reads: **"SY2022-23 and SY2023-24"** (en-dash); we extract only the right-hand column **SY2023-24**.
- Footnote: "SY2023-24 vacancy data reflects actual or assumed to be vacant public K-12 full-time equivalent positions on the first day of school for 123 divisions."

## Method
1. Open PDF with `pdfplumber` and call `page.extract_text(layout=True)` for each of pages 66-70 (indices 65-69). The `layout=True` mode preserves horizontal spacing so left and right columns of the side-by-side table can be sliced by character position.
2. The two-column table layout was identified empirically: the right column begins at character index **44**.
3. For each line on each page, take the substring from column 44 onward (`line[44:].rstrip()`).
4. Skip header lines (those containing "School division" and "rate") and footer/source/note lines (lines starting with "Total ", "SOURCE", or "NOTE").
5. Apply the regex:
   ```
   ^\s*(.+?)\s+(\d{1,3}(?:,\d{3})*)\s+(\d{1,3}(?:,\d{3})*|-)\s+(\d+\.\d+|-)\s*$
   ```
   to match `<name> <total_fte_pos> <unfilled_fte_or_dash> <rate_or_dash>` at the end of a right-slice line.
6. For each matched data line, scan up to 3 following right-slice lines for a **name continuation** (a non-empty line that does NOT itself match the data regex). If found, concatenate to the captured name. This handles names whose last word ("County", "Highlands", "City") wraps to a subsequent visual line.
7. Deduplicate by (name, pos, unfilled, rate) tuple while preserving order.

## Edge cases handled
- **Name wraps onto a later line** (e.g., "Charles City" + "County", "Williamsburg-" + "James City County", "Alleghany High-" + "lands City"): captured by the 3-line lookahead for non-data continuation text.
- **Dash placeholders** for unfilled and rate in zero-vacancy divisions (e.g., Botetourt County): regex allows `-` for the second and third numerics. Some divisions in SY2023-24 show e.g. "Botetourt County 340 - 0.0" (rate present but unfilled hidden); regex still parses these correctly.
- **Comma-separated thousands** in position counts (e.g., "12,681"): regex `\d{1,3}(?:,\d{3})*` matches.
- **Pages without a header**: header detection conditional - data starts at line 0 if no header on that page.
- **Footer detection**: parsing stops when encountering a "Total ..." or "SOURCE" / "NOTE" line.

## Validation
- Extracted **123 unique divisions** for SY2023-24 (matches footnote: "first day of school for 123 divisions").
- Sum of `total_fte_teacher_positions` = 90,465 vs. published total of 90,466 (off by 1 due to rounding in source totals; all individual rows match the printed values).
- Sum of `total_unfilled_fte` = 4,104, matches published total exactly.
- No duplicate division names.
