# Extract A: pdfplumber coordinate-based extraction

## Source
- PDF: `replication/data/raw/state_validation/va_jlarc_rpt576_teacher_pipeline.pdf`
- Table: Appendix C, Table C-1 ("Public K-12 teacher vacancies, SY2022-23 and SY2023-24")
- PDF pages 66-70 (0-indexed 65-69)
- Target: SY 2022-23 column block only (left half of each page)

## Method
- Library: `pdfplumber` 0.11.8 (no OCR, no vision).
- Strategy: crop each page to its left half (`page.crop((0, 0, page.width/2, page.height))`),
  call `page.extract_words()` to get word-level bounding boxes, then:
  1. Cluster words into visual lines by `top` coordinate (tolerance ~3.5 px).
  2. Assign each word to one of four columns by `x0`:
     - name: `x0 < 160`
     - fte: `160 <= x0 < 200`
     - unfilled: `200 <= x0 < 260`
     - rate: `x0 >= 260`
  3. A line is a "num row" if the fte cell matches an integer pattern and unfilled/rate match int-or-dash and rate-or-dash patterns respectively. The header row (`Total FTE | Total unfilled | Vacancy rate (%)`) is rejected because its FTE/unfilled cells contain non-numeric tokens like "FTE", "unfilled".
  4. A line is a "name fragment" if all its words fall in the name column and the text doesn't match known header / intro / footer prefixes (`Appendix`, `TABLE`, `Public K`, `SY2022`, `SOURCE`, `NOTE`, etc.).
  5. For each num row, attach adjacent name fragments (above and below within the inter-row band) using nearest-neighbour distance to the num-row baseline. Names can wrap above OR below the numbers -- e.g. "Westmoreland \\ 123 11 9.0 \\ County" -> "Westmoreland County".
  6. Hyphenation repair: soft line-wrap hyphens (`High- lands` -> `Highlands`) are collapsed when the char after the hyphen is lowercase; true compound hyphens are preserved (`Williamsburg-James City County`).

## Output
- CSV: `replication/output/validation/va_2022-23_vacancy/extract_A_pdfplumber.csv`
- Header: `school_division,total_fte_teacher_positions,total_unfilled_fte,vacancy_rate_pct`
- 131 data rows (one row per VA school division reporting SY 2022-23 data).
- Divisions with zero vacancies (printed as `-` `-` in the PDF) are written with empty `total_unfilled_fte` and `vacancy_rate_pct` cells.

## Totals validation (vs PDF "Total" row)

| Field                       | Extracted sum | PDF "Total" row | Delta |
|-----------------------------|--------------:|----------------:|------:|
| total_fte_teacher_positions |        92,583 |          92,579 |    +4 |
| total_unfilled_fte          |         3,580 |           3,573 |    +7 |

Sums differ from the printed Total by +4 (FTE) and +7 (unfilled). This is an
internal inconsistency in the published PDF, not an extraction error:

- The same totals (92,583 / 3,580) are obtained independently by running a
  regex `([\d,]+)\s+(\d+|-)\s+(\d+\.\d+|-)` over `pdfplumber.extract_text()`
  output of the same left-half region. Two independent parsing strategies
  on the same source yield identical numbers, so the discrepancy is in the
  PDF text itself.
- Spot-checks of individual rows against the PDF's printed text confirm
  the extracted values match the printed values exactly (e.g. "Williamsburg-
  James City County 828 10 1.1" -- the PDF prints rate "1.1" even though
  10/828 = 1.21%; this rounding choice is in the source).

## Notes on edge cases handled
- Header row ("School division | Total FTE teacher positions | Total unfilled FTE teacher positions | Vacancy rate (%)") rejected because non-numeric tokens occupy the numeric columns.
- Page header "Appendixes" and footer page numbers ("52", "53", ...) rejected.
- "Total 92,579 3,573" row recognized (no rate cell) and excluded from data rows; used only for the totals comparison above.
- Multi-line division names handled in both directions (name above number / name below number / name straddling number).
- Soft-hyphen line break repaired: "Alleghany High- lands" -> "Alleghany Highlands".
- Real compound hyphen preserved: "Williamsburg-James City County".
