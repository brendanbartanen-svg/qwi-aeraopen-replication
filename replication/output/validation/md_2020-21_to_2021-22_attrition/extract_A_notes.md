# Extract A — pdfplumber

## Source
- File: `replication/data/raw/state_validation/md_TWS-2022_TeacherPipelineDiversity.pdf`
- Page: 7 (PDF page index 6)
- Slide title: "Maryland Teacher Attrition by LEA"

## Method
- `pdfplumber.open(...)` then `page.extract_tables()` (per task constraint), supplemented
  by `page.extract_words()` to recover bar-chart label positions because the slide is a
  graphic, not a tabular layout.
- The LEA names are rendered as vertical (90-degree rotated) text; pdfplumber reads them
  with their characters in reverse order (e.g. `ynagellA` for Allegany,
  `retsehcroD` for Dorchester). The LEA name is identified by matching that reversed
  token, and each bar's data label is the integer percent whose x-center is closest to
  the corresponding LEA label (within 15 pt tolerance, well inside the ~34 pt bar pitch).
- Y-axis gridline labels (`0%, 10%, 20%, 30%, 40%, 50%` at x < 80) and the right-margin
  legend "LEA%: 10.0%" (x > 900) are excluded.

## Verbatim text from the PDF (column-header / caption verification)
The PDF does not present this as a column-headed table; the values are bar labels on a
chart. The chart's caption / footnote — quoted verbatim from `extract_tables()` output —
is the authoritative description of what each bar value represents:

> "Rates indicate the percentage of teachers in an LEA in 2020-21 who did not return to teach in the same LEA in 2021-22"

Additional verbatim text from the same slide (for context):

> "Maryland Teacher Attrition by LEA"
>
> "In the 2021-2022 school year, 10% of teachers did not return to teach from the prior school year."
>
> "Attrition by LEA varied with a low of 7% in Allegany and Cecil to a high of 18% in Dorchester."
>
> "Source: MSDE Staff Data, As of October 15 of each school year."

This caption confirms the year transition is **2020-21 -> 2021-22** as required by the
task.

## Value format choice
- Format: **integer**.
- Rationale: every data-label on the bar chart is rendered as a whole-number percent
  (e.g. `7%`, `11%`, `18%`). There are no decimal data values on this chart. The only
  decimal that appears (`LEA%: 10.0%`) is the statewide summary, which is not an LEA row
  and is excluded.
- Stored as the integer percentage (e.g. Allegany = `7`, meaning 7%). The column name
  `pct_teachers_2020-21_did_not_return_2021-22` makes the unit (percent) explicit.

## Row count
24 rows (all 24 Maryland LSSs: 23 counties + Baltimore City).
