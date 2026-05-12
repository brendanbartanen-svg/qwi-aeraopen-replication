# Validation summary — VA and MD extraction files

**Method:** for each of 6 hand-transcribed CSV files, three independent extraction agents (pdfplumber tables, vision-only transcription, pdfplumber text+regex) re-derived the data from the source PDF. A cell-level reconciliation compared the three new extractions against the existing CSV. A consistency-check script verified row counts and stated-totals. A semantic-audit agent (with no access to extractions) confirmed what each column actually measures.

## Headline verdict

| File | Rows | A vs B vs C vs CUR | Stated totals | Semantic | Overall |
|---|---|---|---|---|---|
| VA 2022-23 vacancy | 131 | 366 AGREE, 36 MAJORITY, 0 SPLIT | FTE 92,583 vs 92,579; unfilled 3,580 vs 3,573 (Δ +4 / +7 — PDF internal inconsistency, present in all 3 extractions) | LABEL_OK | **VERIFIED** |
| VA 2021-22 turnover | 132 | 528 AGREE, 0 MAJORITY, 0 SPLIT | n/a | LABEL_OK (column name ambiguous; see caveat) | **VERIFIED — caveat** |
| VA 2023-24 vacancy | 123 | 356 AGREE, 6 MAJORITY, 13 SPLIT (all encoding artifacts) | FTE 90,465 vs 90,466; unfilled 4,104 exact | LABEL_OK | **VERIFIED** |
| VA 2021-22 vacancy | 132 | 528 AGREE, 0 MAJORITY, 0 SPLIT | n/a | LABEL_OK | **VERIFIED** |
| MD 2020-21→2021-22 attrition | 24 | 24 AGREE | matches PDF intro values (Allegany=7, Cecil=7, Dorchester=18) | LABEL_OK | **VERIFIED** |
| MD 2022-23→2023-24 attrition | 24 | 24 AGREE | n/a | LABEL_OK | **VERIFIED** |

## What the validation caught

### 1. Source-PDF mislabeling (VA 2022-23 and 2023-24 vacancy)

The filename convention `va_*_vacancy_jlarc_appx_c.csv` implies the data comes from JLARC Report 576's Appendix C. We had two PDFs in the repo named `va_jlarc_rpt576_appendixes.pdf` (5 pages, contains only Appendix E and F) and `va_jlarc_rpt576_teacher_pipeline.pdf` (large; contains the full report). The first three extraction agents pointed at `appendixes.pdf` independently confirmed Appendix C is NOT in that file. The actual location of Appendix C Table C-1 is `va_jlarc_rpt576_teacher_pipeline.pdf` pages 66-70, with side-by-side SY 2022-23 (left) and SY 2023-24 (right) blocks. Re-running the three extractors against the correct PDF produced 131 and 123 rows respectively, matching our CSVs.

This was a substantive finding the original extraction pipeline did not surface. The data is correct; the documentation of where it came from was wrong.

### 2. JLARC PDF internal inconsistency (VA 2022-23 vacancy totals)

All three independent extractors got identical sums: FTE 92,583 and unfilled 3,580. The PDF's printed "Total" row says 92,579 and 3,573. The +4 / +7 deltas reproduce across all three methods using independent code paths (table detection, vision, text+regex), proving the inconsistency exists in the PDF itself, not in our extraction. Spot-checks against individual division values confirm row-level extractions are correct.

### 3. Snapshot-date discrepancy between SY 2022-23 and SY 2023-24 (VA vacancy)

The semantic audit surfaced a methodology change inside JLARC's own report:
- **SY 2022-23 unfilled** = "reported vacant as of October 1, 2022"
- **SY 2023-24 unfilled** = "actual or assumed to be vacant on the first day of school"

These are different definitions. Year-over-year comparisons of the two columns are subtly biased — Oct 1 captures vacancies that may have been filled by then, while first-day-of-school captures vacancies including assumed-vacant slots. Not an extraction error, but an analytical caveat.

### 4. Column-name ambiguity (VA 2021-22 turnover)

Our column is named `pct_departing_sy21_to_sy22`. The audit confirms the data is correctly the percentage of SY 2020-21 teachers who did not return for SY 2021-22 — but the column name reads naturally as "departing FROM SY 2021-22 TO SY 2022-23", which would be the wrong transition. The numbers are right; the label could be misread. Recommendation: rename to `pct_did_not_return_sy20_to_sy21` for clarity (or, equivalently, `pct_left_after_sy20_21`).

### 5. Pre-pandemic average is 5 years, not 3 (VA both)

Both VA vacancy and turnover audits confirm the "pre-pandemic average" column is a 5-year mean across SY 2015-16 through SY 2019-20. Earlier notes in the replication assumed a 3-year window; this is corrected.

### 6. Chart title vs data direction (MD 2022-23→2023-24 attrition)

The MD TWS-2024 page-11 chart is titled "Maryland Teacher Attrition by LEA, SY 2023-2024" but the footnote definitively states it measures "teachers in an LEA in 2022-23 who did not return to teach in the same LEA in 2023-24". The title's year is the year of NON-return, not the cohort/base year. Our filename `md_2022-23_to_2023-24_LEA_attrition` is correct.

## "Splits" that turned out to be encoding artifacts

The reconciliation flagged 13 SPLITs in VA 2023-24 and 36 MAJORITY-disagreements in VA 2022-23. Investigation showed:

- **All Williamsburg-James City County splits** are name-spelling variants. Pdfplumber gets `"Williamsburg- James City County"` (space after hyphen), vision gets `"Williamsburg-James City County"`, the existing CSV has `"WilliamsburgJames City County"`. The numeric values (828, 11, 1.3) are identical across all four. Recommendation: normalize LEA names to a canonical form during data load.

- **All dash/zero splits** are encoding choices. The PDF prints "—" (or "-") for empty cells; pdfplumber and vision agents encoded these as `0`, while text+regex preserved the literal `-`. Existing CSV has `-`. Semantically equivalent (zero vacancies for that division). Recommendation: standardize on either `0` or `NA`/empty.

## What was NOT caught (limits of the framework)

- Cannot detect if JLARC's own data has data-collection errors at the source (e.g., a division reported their numbers wrong to JLARC).
- Cannot detect if MSDE's definitions changed across the 2020-21 and 2022-23 charts in subtle ways the footnotes don't disambiguate.
- For MD, both charts are bar-chart visualizations (not tables); the agents reconstructed values from bar coordinates / labels. The reconciliation confirms they got the same numbers, but if the original chart itself rounds or clips, all three methods would inherit the same rounding.

## File-level verdict

All 6 files are VERIFIED for use in the replication. The two methodology caveats (Oct-1 vs first-day-of-school for VA vacancy, and the VA 2021-22 turnover column name ambiguity) should be carried forward as footnotes in any final analysis.

## Output files per source

```
output/validation/<source>/
  extract_A_pdfplumber.csv     # method 1: pdfplumber table detection
  extract_B_vision.csv         # method 2: vision-only transcription
  extract_C_textregex.csv      # method 3: pdfplumber text + regex
  extract_A_notes.md / _B_ / _C_  # per-method notes on edge cases
  reconciliation.md            # cell-level A/B/C/CUR comparison
  semantic_audit.md            # what does each column actually measure
output/validation/
  consistency_all.md           # combined consistency-check report
  reconcile.py                 # reconciliation script
  consistency.py               # consistency-check script
  VALIDATION_SUMMARY.md        # this file
```
