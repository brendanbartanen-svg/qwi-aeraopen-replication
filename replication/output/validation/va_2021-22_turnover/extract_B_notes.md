# Extract B (Vision) — Notes

## Source
- PDF: `va_jlarc_rpt568_pandemic_impact.pdf`
- Table: Appendix J, TABLE J-2 "Teacher turnover by school division"
- Pages containing J-2: 157 (header + rows starting "Accomack County") through 161 (ending at "York County")

## Method
- Used PyMuPDF (`fitz`) to render each PDF page as a PNG at 180 dpi (and 300 dpi for confirmation passes), then read images with the vision-capable Read tool. No use of the PDF text layer.

## Columns
- `school_division` — division name verbatim (e.g., "Charles City County", "Williamsburg-James City County").
- `num_departing_sy21_to_sy22` — integer count, "# departing from SY21 and SY22" column.
- `pct_departing_sy21_to_sy22` — percentage with trailing `%` exactly as printed (e.g., `21%`).
- `pre_pandemic_avg_pct_departing` — percentage with trailing `%` (the "PPA*" column, defined in footnote as five-year average for 2015-16 through 2019-20).
- `pct_point_change` — percentage with trailing `%`; sign preserved (e.g., `-12%`, `0%`).

## Format choice
- Percentages preserved verbatim with `%` suffix because the source displays them that way and rounding rules are not specified in the PDF.
- Counts are integer (no thousands separator).

## Ambiguous / special cells
- "Charlotte" row (page 158): count = 120; the percent-departing, PPA, and percent-point-change cells are printed as `n.a.` Recorded as `n.a.` in those three columns.
- Charlotte is listed only as "Charlotte" (no "County" / "City" qualifier) — kept verbatim. Likely refers to Charlotte County, but the source is ambiguous so I did not edit.
- All other rows had clearly legible values at 300 dpi.

## Row count
- 132 divisions extracted (one row per division, plus header).
