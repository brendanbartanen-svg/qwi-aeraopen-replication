# Extract C — Text + Regex (pdfplumber `extract_text`)

## Source
`replication/data/raw/state_validation/va_jlarc_rpt568_pandemic_impact.pdf`
JLARC Report 568, Appendix J, **Table J-1: Number of teacher vacancies by school division** (PDF pages 153–157).

## Method
For each target page, call `page.extract_text()` and split on newlines. Each table row is one line in the extracted text, with the division name followed by four whitespace-separated numeric columns. Non-row lines (headers, page chrome, SOURCE/NOTE footers, appendix prose) are filtered out by (a) prefix blacklist and (b) the row regex itself not matching.

## Row regex
```
^(?P<name>[A-Za-z][A-Za-z .'\-]+?)\s+
 (?P<ppa>\d+\.\d+)\s+
 (?P<sy22>\d+\.\d+)\s+
 (?P<pct_vac>\d+)%
 (?:\s+(?P<pct_chg>-?[\d,]+%|-))?\s*$
```
- `name` is a lazy run of letters / spaces / `.` / `'` / `-` (covers e.g. `Williamsburg-James City County`, `Manassas Park City`, `King and Queen County`, `Isle of Wight County`).
- `ppa` and `sy22` are decimals (always one decimal place in the source, e.g. `0.0`, `97.0`, `229.5`).
- `pct_vac` is an integer percent.
- `pct_chg` is **optional** and may be `-` (literal en-dash glyph rendered as ASCII `-` by pdfplumber).

## Edge cases observed
| Case | Example line | Handling |
|---|---|---|
| Comma thousands separators in % change | `Lynchburg City 0.6 29.3 5% 4,783%` | regex `[\d,]+%` keeps comma; value stored verbatim (`"4,783%"`). |
| Negative % change | `Appomattox County 3.8 0.0 0% -100%` | regex `-?` prefix. |
| Literal dash for % change (undefined ratio, PPA = 0) | `Nelson County 0.0 1.7 1% -`, `Salem City 0.0 0.0 0% -`, `Sussex County 0.0 2.0 2% -` | regex alternation `\|-`; stored as `-`. |
| Missing % change cell (no trailing token at all) | `Bristol City 0.0 0.0 0%`, `Buckingham County 0.0 5.0 5%` | optional group `(?:...)?`; stored as empty string. |
| Single-word division names | `West Point 0.2 0.0 0% -100%` | name regex requires only one leading letter, no `County`/`City` suffix required. |
| Hyphenated name | `Williamsburg-James City County 3.4 1.0 0% -71%` | hyphen included in name char class. |
| Page header `Appendixes` repeated each page | filtered via prefix blacklist. |

## Output
`extract_C_textregex.csv` — 132 rows (all Virginia school divisions), header:
`school_division,pre_pandemic_avg_vacancies,num_vacant_sy22,pct_vacant_sy22,pct_change_from_ppa`

Percent values retained with `%` sign and commas as printed in the report; pct_change blank when the report cell was blank, `-` when the report printed an en-dash.
