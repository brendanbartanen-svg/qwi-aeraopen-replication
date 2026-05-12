# Extract C: Maryland LEA Teacher Attrition (SY 2022-23 -> 2023-24)

## Source

- File: `replication/data/raw/state_validation/md_TWS-2024_Supply-Demand-Diversity.pdf`
- Page: 11 (PDF index 10), titled "Maryland Teacher Attrition by LEA, SY 2023-2024"

## Method

Used `pdfplumber` with `page.extract_text()` and `page.extract_words()` to harvest
the raw text and per-word positions. No `extract_tables`, no OCR, no vision.

The chart on page 11 is a vertical bar chart with 24 bars (one per Maryland LSS).
The value labels (percentages) are typeset above each bar in the chart band
(approx `280 < top < 345`), and the LEA names are rendered as vertical (rotated)
text below the bars. The vertical text appears in `extract_text()` output as the
reversed string of the LEA name (e.g. "ynagellA" -> "Allegany",
"lednurA ennA" -> "Anne Arundel"). The 24 LEAs are laid out in alphabetical order
left-to-right (verified by reading the reversed labels and matching their x
positions to the bars).

Extraction logic:
1. Open PDF, take page index 10.
2. Confirm year via regex on extracted text:
   `r'Maryland Teacher Attrition by LEA, SY\s*([\d\-]+)'` -> captured `2023-2024`.
3. Confirm direction-of-flow via footnote regex
   `r'Rates indicate.*?2023-24\.'` -> matches:
   "Rates indicate the percentage of teachers in an LEA in 2022-23 who did not
   return to teach in the same LEA in 2023-24."
4. Walk `extract_words()`, filter to tokens matching `r'\b(\d{1,2}\.\d)%'` whose
   `top` coordinate is inside the chart band (`280 < top < 345`).
5. Sort the resulting 24 percent tokens by `x0` (left-to-right).
6. Pair the sorted percentages 1:1 with the canonical alphabetical list of
   Maryland's 24 LSSs.

## Column header (exact quoted text from PDF)

The chart title is:
> "Maryland Teacher Attrition by LEA, SY 2023-2024"

The narrative line above the chart is:
> "In the SY2023-2024, 12% of teachers did not return to teach in the same LEA from the prior school year. Attrition by LEA varied from a low of 7% to a high of 18%."

The footnote (which defines the rate semantics) is:
> "Source: MSDE Staff Data, As of October 15 of each school year. Rates indicate the percentage of teachers in an LEA in 2022-23 who did not return to teach in the same LEA in 2023-24."

This footnote confirms the SY 2022-23 -> SY 2023-24 transition pairing requested.

## Regex used

- Year-label check: `r'Maryland Teacher Attrition by LEA, SY\s*([\d\-]+)'`
- Footnote check: `r'Rates indicate.*?2023-24\.'`
- Value-token match: `r'\b(\d{1,2}\.\d)%'` applied to each word from
  `extract_words()`, with positional filter `280 < top < 345` to exclude
  unrelated percentages elsewhere on the page.

## Verification

- `len(values) == 24` (asserted).
- Min/max in extracted data: 6.8 (Allegany) and 18.1 (Kent), bracketing the
  narrative-stated 7%-18% range.
- Bar labels match the order of vertical LEA labels by x-coordinate.
