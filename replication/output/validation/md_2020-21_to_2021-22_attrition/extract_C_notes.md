# extract_C — text + regex method (pdfplumber.extract_text / extract_words)

## Source
- PDF: `replication/data/raw/state_validation/md_TWS-2022_TeacherPipelineDiversity.pdf`
- Page index 6 (page 7 in document): "Maryland Teacher Attrition by LEA"

## Exact column header (quoted from PDF text)
The bar chart itself has no traditional column header; the table values are bar labels. The chart's caption/legend (quoted verbatim from `page.extract_text()` output) reads:

> "Rates indicate the percentage of teachers in an LEA in 2020-21 who did not return to teach in the same LEA in 2021-22"

The title above the chart (quoted verbatim) is:

> "Maryland Teacher Attrition by LEA"

The CSV column header used: `pct_teachers_2020-21_did_not_return_2021-22` (per the task spec), corresponding to the rate described above.

## Method
1. Open PDF with `pdfplumber.open(...)` and select `pdf.pages[6]`.
2. Call `page.extract_text()` to verify content (NOT `extract_tables`).
3. Call `page.extract_words(use_text_flow=False, extra_attrs=['upright'])` to obtain positional words; rotated bar-axis LEA names have `upright=False`.
4. Build LEA names: group rotated words by `round(x0, 1)`; reverse each rotated word's string (rotated text appears character-reversed in extraction); join words within a column ordered by descending `top` (bottom-first reading) to produce e.g. "Anne Arundel", "Prince George's".
5. Identify bar value labels with regex `^\d+%$` on upright words whose `top` is in (250, 340) and whose `x0 > 60` (excluding the y-axis labels at `x0 == 49.4`).
6. Sort both LEA list and pct-label list by x-coordinate and pair index-wise (24 LEAs <-> 24 bar labels).
7. Write CSV with header `LEA,pct_teachers_2020-21_did_not_return_2021-22` and value stripped of trailing `%`.

## Regex / parser snippets
- LEA-name word collection: `if not w['upright']` then `text[::-1]` and group by x0 column.
- Bar value selector:
  ```python
  pct_words = [w for w in words
               if w['upright']
               and re.match(r'^\d+%$', w['text'])
               and 250 < w['top'] < 340
               and w['x0'] > 60]
  ```

## Sanity checks
- 24 LEAs found (matches Maryland's 24 LSSs).
- 24 bar value labels found.
- Intro text in PDF states "low of 7% in Allegany and Cecil to a high of 18% in Dorchester" — extracted values: Allegany=7, Cecil=7, Dorchester=18 — match.
- Statewide LEA% shown in PDF as "10.0%" (not included as a row; only the 24 LEA bars are output).
