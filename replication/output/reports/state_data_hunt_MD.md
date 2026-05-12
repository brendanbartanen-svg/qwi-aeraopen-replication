# Maryland (MSDE) Staff Data Hunt

## Goal
Find downloadable Maryland district-level staff turnover and/or headcount data for SY 2021-22 and 2022-23 to validate QWI Figure 1.

## What I tried
1. **MSDE Report Card SPA** (`reportcard.msde.maryland.gov/Graphs/`). Reverse-engineered the JS bundle (`/Scripts/build/main-Bundle.js`). The data download endpoint is a POST to `DataDownloads/GetdatadownloadViewGet` (session-bound) and files served via `DataDownloads/FileDownload/{id}`. Probing live IDs 1-800 all returned HTTP 500 (server bug). Wayback CDX (`reportcard.msde.maryland.gov/DataDownloads/FileDownload/*` from 2022-2025) lists ~30 archived zip IDs - all are enrollment/attendance/grad/MCAP/special-services. **No "Staff" file ID is exposed via the Report Card data downloads** for any year - the only educator file is `Educator_Equity_Data_*.pdf` (state-aggregate Title I only, not LEA).
2. **MSDE Staff and Student Publications page** (`marylandpublicschools.org/about/Pages/DCAA/SSP/`) - the source for the underlying staff data. Files are PDFs only (no xlsx/csv).
3. **State Board briefing decks** at `marylandpublicschools.org/stateboard/Documents/...` - some contain LEA-level attrition charts (page 7 of TWS-2022, page 11 of TWS-2024).
4. **Maryland Open Data Portal** - searched via Socrata catalog API. No MSDE K-12 staff datasets.

## What I found (saved to `data/raw/state_validation/`)

### LEA-level headcounts (definitive source per LEA per year)
- `md_2021-22_StaffEmployed.pdf` - Oct 2021 staff per LEA (Tables 1-5; "Annual Staff Report from 24 LSSs"). Total staff, teachers, therapists, aides etc. per LEA.
- `md_2022-23_StaffEmployed.pdf` - Oct 2022 same structure.
- `md_2023-24_StaffEmployed.pdf` - Oct 2023.

These are PDFs but tables are well-structured for extraction (e.g. pdfplumber/tabula).

### LEA-level turnover (attrition rates from MSDE Staff Data Collection)
- `md_TWS-2022_TeacherPipelineDiversity.pdf` page 7: LEA attrition bar chart for **SY 2021-22** (24 LEA values, "% of teachers in LEA in 2020-21 who did not return to teach in same LEA in 2021-22").
- `md_TWS-2024_Supply-Demand-Diversity.pdf` page 11: LEA attrition bar chart for **SY 2023-24** (24 LEA values).
- `md_EducatorWorkforce_overview.pdf` (Feb 2025): state-only attrition trend; no LEA chart for 2022-23.

### Other (state-aggregate only, not useful for LEA validation)
- `md_2021-22_and_2022-23_EducatorEquity.pdf`, `md_2022-23_EducatorEquity.pdf`, `md_TWS-2025_*`.

## Critical gap
**No LEA-level attrition chart for SY 2022-23** was published in any MSDE board doc I could find. Possible workarounds:
- Compute LEA turnover for 2022-23 as `1 - (returning_teachers / prior_year_teachers)` from the StaffEmployed PDFs (Tables 1/2 give LEA teacher counts for Oct 2021, Oct 2022, Oct 2023). This gives net change, not true turnover.
- File a Maryland Public Information Act request to MSDE-DAAPR for the underlying Staff Data Collection.
- Email Bleiberg/Nguyen for their original extract.

## Left to try
- Wayback for `marylandpublicschools.org/stateboard/Documents/2023/*` - my probes returned 404 but CDX hit rate-limited; could retry.
- MLDS Center (`mldscenter.maryland.gov`) - has a Blueprint Teacher Diversity report that may include LEA tables.
- Direct PIA request to MSDE.
