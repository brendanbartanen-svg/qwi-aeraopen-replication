# Extract B (vision) notes

Source PDF: `replication/data/raw/state_validation/md_TWS-2024_Supply-Demand-Diversity.pdf`
Page: 11 (PDF page 11 of 33; slide number "9" shown in footer-right).

## Exact title (quoted verbatim from the image)
> "Maryland Teacher Attrition by LEA, SY 2023-2024"

## Exact subtitle / caption (quoted verbatim)
> "In the SY2023-2024, 12% of teachers did not return to teach in the same LEA from the prior school year. Attrition by LEA varied from a low of 7% to a high of 18%."

## Exact source/footnote line (quoted verbatim) — CRITICAL for transition verification
> "Source: MSDE Staff Data, As of October 15 of each school year. Rates indicate the percentage of teachers in an LEA in 2022-23 who did not return to teach in the same LEA in 2023-24."

Verification: the footnote explicitly states the rates are teachers in 2022-23 who did NOT return in 2023-24 — this IS the 2022-23 -> 2023-24 transition requested, even though the slide title is branded "SY 2023-2024". This matches what the task asked for.

## Y-axis label
No explicit y-axis label; gridlines at 0%, 10%, 20%, 30%, 40%, 50%. A dashed horizontal reference line sits near 12% (the statewide rate cited in the subtitle).

## X-axis
24 LEA names, alphabetical, vertical text labels.

## Data values (read from data labels above each bar)
Allegany 6.8%, Anne Arundel 12.6%, Baltimore City 17.0%, Baltimore County 13.8%, Calvert 10.7%, Caroline 13.6%, Carroll 11.5%, Cecil 8.9%, Charles 15.4%, Dorchester 14.8%, Frederick 10.2%, Garrett 10.8%, Harford 10.2%, Howard 10.1%, Kent 18.1%, Montgomery 9.1%, Prince George's 14.1%, Queen Anne's 9.4%, Saint Mary's 12.5%, Somerset 16.5%, Talbot 10.2%, Washington 10.7%, Wicomico 10.3%, Worcester 8.5%.

All 24 values were read directly from the printed data labels above each bar in the high-resolution rendering (350 dpi base; 4x cropped zoom for verification of each half of the chart). No values were interpolated from bar heights.

## Ambiguous cells
None. Every bar has a clearly printed data label with one decimal place. The "Saint Mary's" label uses "Saint" (not "St."); the apostrophes in "Prince George's", "Queen Anne's", and "Saint Mary's" are visible in the x-axis labels.

## Note on the 25th potential LEA
Maryland has 24 LSSs (one per county plus Baltimore City). The chart shows exactly 24 bars. There is no "Statewide" or aggregate bar in the chart itself; the 12% statewide figure appears only in the subtitle and as a dashed reference line.

## Rendering method
PyMuPDF (fitz) was used to rasterize the PDF page to PNG (poppler-utils was not installed, so `pdftoppm` could not be invoked). Only PNG renders of page 11 were inspected visually. The PDF text layer was NOT parsed. pdfplumber was NOT used.
