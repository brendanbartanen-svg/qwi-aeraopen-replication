# Extraction C: Text + Regex (pdfplumber `extract_text`)

## Source
JLARC Report 568, Appendix J, Table J-2 ("Teacher turnover by school division").
Located on PDF pages 157-161 (1-indexed).

## Method
1. Open PDF with `pdfplumber`.
2. Call `page.extract_text()` on pages 157-161 only (slice `pdf.pages[156:161]`).
   This is a deliberately different approach from `extract_tables()` and does
   not rely on any vision/OCR.
3. Split the page text into lines, strip whitespace.
4. Use header sentinel `"departing per year change"` to flip an `in_table`
   flag on, and `"SOURCE:"` / `"NOTE:"` / `"Teacher quality"` to flip it off.
   (In practice the page slice already isolates J-2, but the sentinels are
   defensive.)
5. Match each line against one of two regexes.

## Regexes

Normal data row (used for 131 of 132 rows):
```
^(?P<name>[A-Za-z][A-Za-z .\-]+?)\s+
 (?P<count>\d+)\s+
 (?P<pct1>-?\d+%)\s+
 (?P<pct2>-?\d+%)\s+
 (?P<pct3>-?\d+%)\s*$
```

Notes on the name group:
- Allows letters, spaces, periods (none observed in J-2 but harmless), and
  hyphens (needed for `Williamsburg-James City County`).
- Non-greedy (`+?`) so the trailing `\s+` boundary anchors against the
  numeric count rather than gobbling the count into the name.

Charlotte special-case row (`Charlotte 120 n.a. n.a. n.a.`):
```
^(?P<name>[A-Za-z][A-Za-z .\-]+?)\s+
 (?P<count>\d+)\s+
 n\.a\.\s+n\.a\.\s+n\.a\.\s*$
```

## Value format choice
- `num_departing_sy21_to_sy22`: integer string (as printed, no formatting in
  the PDF — values like `1737` appear without commas).
- The three percent columns: kept verbatim with the trailing `%` sign,
  including the leading `-` for negative percentage-point changes. This
  preserves the PDF's exact textual format (integer percent, no decimals)
  and avoids any ambiguity about whether values are fractions or percent.
- `n.a.` propagated literally for Charlotte's three percent columns.

## Edge cases encountered
1. **Charlotte row** lacks all three percent values (`n.a. n.a. n.a.`). The
   primary regex does not match it; a second NA-specific regex captures it.
   The division name "Charlotte" is distinct from "Charlottesville City",
   which appears as the next row with normal data.
2. **Hyphenated name**: `Williamsburg-James City County` — handled by
   including `-` in the name character class.
3. **Negative percentage-point changes** (e.g., `-5%`, `-12%`) — handled by
   `-?` in each percent group.
4. **Multi-word division names** with no internal digits — non-greedy match
   plus `\s+` boundary correctly assigns the first integer token to `count`.
5. The page-range slice (157-161) avoids cross-contamination with Table J-1
   (vacancies, pages 153-157) and J-3 (quality, pages 161+). Table J-1's
   rows have a leading float column (e.g., `5.8`) that wouldn't match `\d+`
   anyway, but page-slicing is an additional safeguard.
6. Header row on page 157 is filtered out: it does not match either regex
   because it contains the word tokens "SY21", "SY22", etc.

## Output
132 rows written to `extract_C_textregex.csv`, matching the count of
Virginia school divisions in J-2.
