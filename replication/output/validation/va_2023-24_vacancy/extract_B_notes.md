# Extract B (Vision) Notes

## Source
- PDF: `va_jlarc_rpt576_teacher_pipeline.pdf`
- Pages: 52-55 (printed) / pages 66-69 (PDF page index, 1-indexed)
- Table: "TABLE C-1: Public K-12 teacher vacancy data, SY2022-23 and SY2023-24"
- Appendix: "Appendix C: Teacher vacancies by school division"

## Year Label (Verbatim)
The exact label visible on the column header (page 66 / printed p. 52) reads:

> "SY2023-24"

The table title reads (verbatim):

> "Public K-12 teacher vacancy data, SY2022-23 and SY2023-24"

Note in the document body (page 66) reads (verbatim):

> "This appendix includes public K-12 teacher vacancy data, by school division, collected by the Virginia Department of Education for the past two school years (SY2022-23 and SY2023-24)."

Note on page 70 (printed p. 56) confirming SY2023-24 source (verbatim):

> "SY2023-24 vacancy data reflects actual or assumed to be vacant public K-12 full-time equivalent positions on the first day of school for 123 divisions."

## Columns Extracted (SY2023-24 right-hand panel)
- School division
- Total FTE teacher positions
- Total unfilled FTE teacher positions
- Vacancy rate (%)

## Method
- Used PyMuPDF (pymupdf) to render each PDF page to a PNG image at 200-300 DPI.
- Viewed each rendered image using the Read tool (vision).
- Did NOT use the PDF text layer, did NOT use pdfplumber.
- Transcribed each row from the SY2023-24 columns (right side of the two-panel table).

## Validation Checks
- Row count: 123 divisions extracted (matches the source NOTE: "for 123 divisions").
- Sum of unfilled FTE: 4,104 (matches printed total: 4,104).
- Sum of total FTE positions: 90,465 (printed total: 90,466 — off by 1).
  - The 1-unit discrepancy is likely either a typo in the printed total or a 1-unit rounding difference in the printed total row of the source PDF; all individual rows were transcribed verbatim from the printed values.

## Ambiguous Cells / Notes
- For "0.0" vacancy rate rows, the source displays the unfilled count as a dash ("-"). I encoded these as `0` integers in `total_unfilled_fte` to keep the column integer-typed. The dash unambiguously corresponds to zero vacancies given the 0.0% rate.
  - Affected rows: Botetourt County, Carroll County, Clarke County, Colonial Beach, Falls Church City, Fluvanna County, Grayson County, Lexington City, Russell County, Staunton City.
- "Colonial Beach" appears in the source without a "City" suffix (it is a town); transcribed verbatim.
- "Williamsburg-James City County" uses an en-dash in the source; transcribed with an ASCII hyphen.
- The table is sorted by SY2023-24 vacancy rate (descending), with ties broken by an unknown secondary key.
- The two-panel layout means the SY2022-23 (left) division names differ in order and membership from the SY2023-24 (right) names; only the right panel was extracted.

## Source / Methodology Note (from page 70)
> "SOURCE: JLARC staff analysis of Virginia Department of Education data, school years 2022-23 and 2023-24."
> "NOTE: SY2022-23 data represents vacant public K-12 full-time equivalent positions reported by divisions as of October 1, 2022. SY2023-24 vacancy data reflects actual or assumed to be vacant public K-12 full-time equivalent positions on the first day of school for 123 divisions."
