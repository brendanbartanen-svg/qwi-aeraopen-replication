# Extract B (vision) notes

## Source PDF
`/Users/yvp3tf/Documents/CC Sandbox/replication/qwi_aeraopen/replication/data/raw/state_validation/va_jlarc_rpt576_teacher_pipeline.pdf`
Pages 66-70 (1-indexed), Appendix C, Table C-1 "Public K-12 teacher vacancies, SY2022-23 and SY2023-24".

## Method
PDF pages 66-70 were rasterized to PNG at 220 dpi via PyMuPDF (`fitz`), then visually inspected with the Read tool. The page images were cropped to the LEFT half (SY 2022-23) and zoomed for legibility. No PDF text layer or pdfplumber was used. Right-half SY 2023-24 column was not transcribed.

## Exact column headers (LEFT block, SY 2022-23)
Top-level year header: `SY2022-23` (spanning the three numeric columns).
Column headers:
- `School division`
- `Total FTE teacher positions`
- `Total unfilled FTE teacher positions`
- `Vacancy rate (%)`

## Total row (bottom of page 70, bold)
- Total FTE teacher positions: **92,579**
- Total unfilled FTE teacher positions: **3,573**
- (no Vacancy rate cell in Total row for SY 2022-23)

Source footer also notes "SY2023-24 vacancy data reflects ... 123 divisions" — but the SY 2022-23 column contains 131 rows (120 with vacancy data, 11 with FTE only and dashes in unfilled/rate). All 131 division-name rows for SY 2022-23 were transcribed.

## Sum reconciliation against published Total
- Sum of transcribed `total_fte_teacher_positions` = 92,583 (published Total: 92,579; diff +4)
- Sum of transcribed `total_unfilled_fte` = 3,580 (published Total: 3,573; diff +7)
Differences are consistent with the report rounding underlying non-integer FTEs to integer displays per row (the per-row stated vacancy rate often does not equal `unfilled/FTE * 100` to the displayed precision, confirming the integers are rounded).

## Ambiguous / noteworthy cells
- Division names hyphenated across lines were joined: e.g. "Alleghany High-lands" -> `Alleghany Highlands`; "Williamsburg-James City County" preserved.
- "Roanoke City" (1,066 / 34 / 3.2 on p. 68) and "Roanoke County" (999 / 1 / 0.1 on p. 69) are distinct rows; likewise "Richmond City" (1,914 / 80 / 4.2 on p. 67) vs "Richmond County" (93 / 3 / 3.2 on p. 68) and "Franklin City" (85 / 11 / 13.0 on p. 66) vs "Franklin County" (524 / 11 / 2.0 on p. 68).
- 11 divisions on pages 69-70 show FTE only with dash ("-") in both the unfilled and rate cells: Buena Vista City, Charlotte County, Falls Church City, Goochland County, Highland County, Lexington City, Norton City, Radford City, Salem City, Scott County, West Point. These are encoded as empty strings (NA) in the CSV's unfilled and rate columns.
- Per-row vacancy-rate consistency check: a handful of rows have rates that differ slightly from `unfilled/FTE*100` when computed from displayed integers (e.g. Bath County 55 / 3 stated 4.6%; Grayson County 148 / 3 stated 1.7%). The displayed values were transcribed verbatim; the apparent mismatch is from the source's underlying non-integer values being rounded for display.
- Hyphen character in column header and source: en-dash (U+2013) in "SY2022-23"; rendered as ASCII hyphen in this note for portability.

## CSV
Written 131 data rows + 1 header row to `extract_B_vision.csv`.
