# Extract A — pdfplumber

## Source
- PDF: `replication/data/raw/state_validation/md_TWS-2024_Supply-Demand-Diversity.pdf`
- Page 11 (PDF page index 10), titled "Teacher Workforce Demand"

## Exact column/title text from the PDF (verbatim)

Chart title:
> "Maryland Teacher Attrition by LEA, SY 2023-2024"

Chart subtitle / description:
> "In the SY2023-2024, 12% of teachers did not return to teach in the same LEA from the prior school year. Attrition by LEA varied from a low of 7% to a high of 18%."

Source/footnote (this is the key verification text — it explicitly states the transition):
> "Source: MSDE Staff Data, As of October 15 of each school year. Rates indicate the percentage of teachers in an LEA in 2022-23 who did not return to teach in the same LEA in 2023-24."

So the transition labeled "SY 2023-2024" in the chart title corresponds to teachers in 2022-23 who did not return in 2023-24 — confirmed match for the 2022-23 to 2023-24 transition.

## Method
- Used `pdfplumber` only.
- `page.extract_tables()` on page 11 returns the chart as a single text blob (chart, not a real table), so values and labels could not be cleanly recovered that way.
- Fell back to `page.extract_words()` (still pdfplumber, no OCR) to get x/y coordinates of each glyph cluster.
- County labels on the x-axis are rendered with rotated text (each word's characters appear reversed, and multi-word names are stacked vertically). Reconstruction:
  - Grouped word fragments by x0 bucket (each column ~34 pt wide).
  - Reversed each fragment's characters to recover the English word.
  - Reversed the top-to-bottom stacking order to recover natural reading order (e.g. "Arundel" stacked above "Anne" -> "Anne Arundel").
- Percentages: filtered words ending in `%` in the y-range 280–335 with x0 > 80 (excludes axis labels 0%/10%/20%/30%/40%/50%).
- Paired counties to percentages in order along x0 (both sequences have exactly 24 entries, monotonically increasing in x0, with each percentage's x0 sitting ~8–9 pt left of its column's leftmost label x0 — a consistent offset across all 24 columns).

## Result
- 24 rows, one per Maryland LSS, matching MD's 24 LSSs.
- Range: 6.8% (Allegany) to 18.1% (Kent). Consistent with the chart subtitle's stated low of 7% and high of 18%.
