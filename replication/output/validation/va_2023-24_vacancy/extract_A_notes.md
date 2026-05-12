# Extract A — pdfplumber notes

## Source PDF
File: `replication/data/raw/state_validation/va_jlarc_rpt576_teacher_pipeline.pdf`
(The companion file `va_jlarc_rpt576_appendixes.pdf` only contains Appendixes E and F — no vacancy data — so it was not the source.)

## Pages used
Pages 66-70 (PDF page indices 65-69 zero-indexed) contain Appendix C, Table C-1.

## Appendix / table label (verbatim from PDF)
- Appendix title (page 66): "Appendix C: Teacher vacancies by school division"
- Appendix description (page 66): "This appendix includes public K-12 teacher vacancy data, by school division, collected by the Virginia Department of Education for the past two school years (SY2022-23 and SY2023-24)."
- Table title (page 66): "TABLE C-1 / Public K-12 teacher vacancies, SY2022-23 and SY2023-24"
- Right-column group header (page 66, verbatim): "SY2023-24"

## SY2023-24 confirmation
The right-hand column block is explicitly labeled "SY2023-24" at the top of page 66 (verified via word-position extraction at x=456.4, top=256.3). The footnote "Total 90,466 4,104" on page 70 corresponds to SY2023-24 totals shown in the right-side stack.

## Column headers (verbatim, right-side block, page 66)
Stacked across three text rows:
- Row 1: "Total FTE | Total unfilled |       "
- Row 2: "teacher  | FTE teacher  | Vacancy"
- Row 3: "School division | positions | positions | rate (%)"

## Mapping decisions
- The PDF lays Table C-1 out as two parallel sub-tables side-by-side: SY2022-23 on the left half of the page, SY2023-24 on the right half. Both sub-tables are sorted independently by vacancy rate (descending), so left-row N and right-row N are NOT the same division.
- I extracted ONLY the right half (x >= 315) of pages 66-70.
- Extraction method: `pdfplumber` `page.extract_words(use_text_flow=False)`, then grouped words into rows by y-coordinate (tolerance 3pt), then split each row into name tokens (x < 400) and numeric tokens (x >= 400). Names that wrap to a 2nd line (e.g. "Charles City / County") were stitched together by attaching a name-only line to the immediately previous data row. (`page.extract_tables()` was also used to scope the table, but the side-by-side layout collapsed pairs of cells, so word-position parsing was required for a clean right-side cut.)
- On page 70, the only SY2023-24 content is the "Total 90,466 4,104" row at y ~163. I cut off y > 170 to exclude SOURCE/NOTE footnotes that contained numbers (e.g., "October 1, 2022.").
- Dash ("-") in the unfilled-FTE column was mapped to integer 0; corresponding vacancy_rate_pct value in the PDF is "0.0" and is preserved as 0.0. These rows represent divisions with zero unfilled positions per the appendix prose ("some divisions experiencing zero vacancies").
- Vacancy rate values are kept as published floats (e.g., 21.5), not converted to fractions.
- Division name punctuation/spacing is preserved as it appears, e.g. "Williamsburg- James City County" (the hyphen and space come from the PDF line wrap).

## Row count and totals check
- Extracted 123 division rows for SY2023-24 (excludes the "Total" row).
- Sum of `total_fte_teacher_positions` = 90,465 (PDF "Total" = 90,466; off by 1, likely rounding of suppressed values).
- Sum of `total_unfilled_fte` = 4,104 (matches PDF "Total" = 4,104 exactly).
