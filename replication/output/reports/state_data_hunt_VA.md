# Virginia Staffing & Vacancy Data Hunt — Findings

## Status: SUCCESS — data for SY2021-22, SY2022-23, and SY2023-24 obtained

The paper-cited VDOE landing page is rendered by Oracle APEX behind a Google reCAPTCHA at `https://p1pe.doe.virginia.gov/apex_captcha/home.do?apexTypeId=320` ("Positions and Exits Build-A-Table"). No XLSX/CSV link is exposed without solving the captcha. WebFetch returned 403 on `doe.virginia.gov`; curl with browser headers also got 403 on most VDOE pages. Wayback Machine had snapshots of the landing page but not of the captcha-gated data.

## What worked: JLARC reports

JLARC (Joint Legislative Audit and Review Commission of Virginia) republished VDOE Positions and Exits Collection data at division level in two reports. Both PDFs downloaded cleanly:

- **JLARC Rpt568** (Dec 2022, "Pandemic Impact on K-12 Public Education") — Appendix J:
  - Table J-1: Teacher vacancies by division, **SY2021-22** (as of Oct 2021), n=132 divisions
  - Table J-2: Teacher turnover by division, SY20-21 to SY21-22, n=132 divisions
  - Source URL: https://jlarc.virginia.gov/pdfs/reports/Rpt568-1.pdf
- **JLARC Rpt576** (Nov 2023, "Virginia's K-12 Teacher Pipeline") — Appendix C:
  - Table C-1: Teacher vacancies by division, **SY2022-23** (Oct 2022, n=131) and **SY2023-24** (first day of school, n=123)
  - Source URL: https://jlarc.virginia.gov/pdfs/reports/Rpt576-3.pdf

Both explicitly cite VDOE Positions and Exits Collection as the data source, with vacancy counts and rates per division.

## Files saved to `data/raw/state_validation/`

| File | Year | Source | Notes |
|------|------|--------|-------|
| `va_2021-22_vacancy.xlsx` / `.csv` | SY2021-22 | JLARC Rpt568 Appx J-1 | 132 divisions, pre-pandemic-avg + Oct 2021 count + % + % change |
| `va_2021-22_turnover.xlsx` / `.csv` | SY2020-21→SY2021-22 | JLARC Rpt568 Appx J-2 | 132 divisions, # and % departing |
| `va_2022-23_vacancy.xlsx` / `.csv` | SY2022-23 | JLARC Rpt576 Appx C | 131 divisions, FTE positions, unfilled FTE, vacancy rate |
| `va_2023-24_vacancy.xlsx` / `.csv` | SY2023-24 | JLARC Rpt576 Appx C | 123 divisions, same fields |
| `va_jlarc_rpt568_pandemic_impact.pdf` | full report | jlarc.virginia.gov | source PDF |
| `va_jlarc_rpt576_teacher_pipeline.pdf` | full report | jlarc.virginia.gov | source PDF |

## Validation

Reconstructed SY2022-23 totals from extracted CSV: 92,583 positions / 3,580 unfilled vs JLARC stated total of 92,579 / 3,573 (off by 4/7 — sub-0.2% rounding error in PDF column extraction). SY2023-24 unfilled total: 4,104 (exact match).

## What's left to try

- Direct API access to Build-A-Table (would require reCAPTCHA solver + form submission via Selenium/Playwright) — not pursued, JLARC data is the same underlying VDOE PEC source.
- The dashboard at doe.virginia.gov has an underlying Tableau/Power BI feed — could be inspected via browser dev tools, but JLARC data should suffice for the paper's correlation analysis (R=0.84 of NNJF vs vacancies).
