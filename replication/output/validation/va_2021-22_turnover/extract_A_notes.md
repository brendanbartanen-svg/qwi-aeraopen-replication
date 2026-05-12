# Extraction A notes (pdfplumber)

## Source
- PDF: `replication/data/raw/state_validation/va_jlarc_rpt568_pandemic_impact.pdf`
- Table: JLARC Report 568, Appendix J, TABLE J-2 "Teacher turnover by school division"
- Pages: 157-161 (1-indexed)

## Method
- `pdfplumber` 0.11.8, `page.extract_text()` on pages 157-161.
- `page.extract_tables()` returned 0 tables with default settings (no ruling lines in the
  PDF). Text-strategy table extraction also worked but produced fragmented cells. Parsing
  `extract_text()` line-by-line was simpler and lossless because each data row sits on a
  single visual line with whitespace-separated columns.
- Row detection: started capturing after the header line containing
  `"Division SY21 and SY22"`; stopped at `SOURCE:`/`NOTE:`/`Teacher quality`/`TABLE J-3`.
- For each row, split on whitespace, took the last 4 tokens as the numeric columns and
  joined the remainder as the school division name.

## Column mapping
PDF columns (header spans two lines):

| PDF column                                  | CSV column                         |
|---------------------------------------------|------------------------------------|
| Division                                    | school_division                    |
| # departing from SY21 and SY22              | num_departing_sy21_to_sy22         |
| % departing from SY21 and SY22              | pct_departing_sy21_to_sy22         |
| PPA* departing per year                     | pre_pandemic_avg_pct_departing     |
| % point change                              | pct_point_change                   |

`*PPA: Pre-pandemic average` (five-year average from 2015-16 through 2019-20).

The schema asked for "SY 2020-21 -> 2021-22"; the PDF labels these as
"SY21 and SY22", which the source defines as departures measured between SY 2020-21
and SY 2021-22. Same quantity, different shorthand.

## Value formatting choices
- Counts (`num_departing_sy21_to_sy22`): integers, exactly as printed in the PDF.
- Percentages: preserved the PDF's `"NN%"` format, including negative values such as
  `"-10%"`. The "% point change" column is also reported as `"N%"` in the source.
- Special value: `Charlotte` row contains `120 n.a. n.a. n.a.` (three non-available
  values per the source footnote `n.a. = not available`). These were preserved as
  `"n.a."` strings.

## Row count
- 132 divisions extracted (matches the count in the source table, which lists all
  Virginia school divisions in alphabetical order from Accomack County to York County).
