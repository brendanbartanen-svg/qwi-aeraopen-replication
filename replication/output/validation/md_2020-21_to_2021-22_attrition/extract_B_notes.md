# Extract B (Vision) - Notes

## Source
- File: `md_TWS-2022_TeacherPipelineDiversity.pdf` (Maryland Teacher Workforce Study 2022, MSDE)
- Page: 7 (rendered via PyMuPDF at 200/400 dpi, viewed as image; no PDF text layer used)

## Exact title/caption/header (transcribed verbatim from image)

- Slide title: **"Maryland Teacher Attrition by LEA"**
- Subheading (verbatim): "In the 2021-2022 school year, 10% of teachers did not return to teach from the prior school year. Attrition by LEA varied with a low of 7% in Allegany and Cecil to a high of 18% in Dorchester."
- Chart annotation: "Statewide LEA%: 10.0%"
- Footnote (verbatim, defines the column): **"Rates indicate the percentage of teachers in an LEA in 2020-21 who did not return to teach in the same LEA in 2021-22"**
- Source line: "Source: MSDE Staff Data, As of October 15 of each school year."

## Confirmation of transition year
The footnote explicitly states the percentages reflect teachers in an LEA in **2020-21** who did **not return** in **2021-22**. This is the SY 2020-21 -> 2021-22 transition, NOT 2021-22 -> 2022-23. Cross-referenced against page 6's "Maryland Teacher Attrition" line chart, where the "2021-22" data point on the x-axis is described as "The percentage of Maryland public school teachers in the prior year who did not return as a teacher in the same LEA in the following year" - confirming the same convention (the year label is the "following year").

## Bar values (read in chart left-to-right, alphabetical by LEA)
All values are presented as integer percentages with a "%" sign on each bar.

| LEA | % |
|---|---|
| Allegany | 7% |
| Anne Arundel | 11% |
| Baltimore City | 12% |
| Baltimore County | 11% |
| Calvert | 9% |
| Caroline | 12% |
| Carroll | 10% |
| Cecil | 7% |
| Charles | 15% |
| Dorchester | 18% |
| Frederick | 12% |
| Garrett | 13% |
| Harford | 9% |
| Howard | 8% |
| Kent | 17% |
| Montgomery | 8% |
| Prince George's | 11% |
| Queen Anne's | 10% |
| Saint Mary's | 10% |
| Somerset | 11% |
| Talbot | 13% |
| Washington | 11% |
| Wicomico | 9% |
| Worcester | 8% |

24 LEAs total (matches the 24 LSSs in Maryland).

## Ambiguous cells / notes
- No ambiguous cells. All 24 bar labels and 24 numeric values are clearly legible at 400 dpi.
- LEA name spelling on the x-axis is rotated 90 degrees; rendered exactly as displayed: "Saint Mary's" (not "St. Mary's"), "Queen Anne's", "Prince George's" (with apostrophes).
- The CSV stores percentages as integers (no "%" sign and no decimal) since the chart displays whole-number percents only. Statewide reference (10.0%) is not included in the CSV (it is a reference line, not an LEA row).
