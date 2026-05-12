# Maryland (MSDE) LEA-level Teacher Attrition Data Hunt — v2

## Bottom line

**The user already had the right file but it was mislabeled in the v1 hunt.** The previous agent labeled `md_TWS-2024_Supply-Demand-Diversity.pdf` page 11 as "LEA-level attrition charts for SY 2023-24", which led the user to believe SY 2022-23 LEA data was missing. In fact, the source note on that exact page says:

> "Rates indicate the percentage of teachers in an LEA in **2022-23** who did not return to teach in the same LEA in **2023-24**."

This is *exactly* what the user asked for: "the number or rate of teachers/staff who left each Maryland school district **between 2022-23 and 2023-24**". MSDE labels the chart by the destination year (SY 2023-24), but the transition measured is from 2022-23 to 2023-24.

I extracted the bar values from page 11 of that PDF, mapped them to the correct LEA labels via x-coordinate matching, and wrote a verified CSV. The unweighted mean of the 24 LEA rates is **11.91%**, which matches MSDE's stated statewide weighted value of **12.1%** for that transition.

### Files produced

- `/Users/yvp3tf/Documents/CC Sandbox/replication/qwi_aeraopen/replication/data/raw/state_validation/md_2022-23_to_2023-24_LEA_attrition_TWS-2024_p11.csv` — **THE FILE THE USER NEEDS**. 24 LEAs × attrition rate for the SY 2022-23 → SY 2023-24 transition.
- `/Users/yvp3tf/Documents/CC Sandbox/replication/qwi_aeraopen/replication/data/raw/state_validation/md_2020-21_to_2021-22_LEA_attrition_TWS-2022_p7.csv` — also extracted for reference / cross-validation (matches the article quote "Allegany=7%, Cecil=7%, Dorchester=18%").

### Caveat about the user's prompt

The user's prompt has an internal contradiction:

1. They wrote: "teachers/staff who left each Maryland school district **between 2022-23 and 2023-24**" → this is the **2022-23 → 2023-24** transition (statewide 12.1%, in TWS-2024 page 11).
2. They also wrote: "The state-level value (**12.7%** statewide) is reported" → 12.7% is MSDE's value for the **2021-22 → 2022-23** transition (i.e., MSDE's "SY 2022-23 attrition rate" in their column-labeled-by-destination-year convention).

These are two *different* transitions. The data extracted matches interpretation (1). If the user actually wants interpretation (2) — the LEA breakdown of the 12.7% statewide rate (which would be teachers in 2021-22 who didn't return in 2022-23) — that breakdown was **apparently never publicly released by MSDE**. The 2023 State Board of Education meetings skipped the annual teacher-workforce report entirely (verified by enumerating every meeting agenda's PDFs; see "Dead ends" below). Only the May 2024 State Board deck resumed it, by which point the LEA bars shown are for the 2022-23 → 2023-24 transition.

## What I tried in detail

### 1. Verifying the existing local PDFs (success)

Carefully re-read `md_TWS-2024_Supply-Demand-Diversity.pdf` page 11 with `pdfplumber`. The chart title reads "Maryland Teacher Attrition by LEA, SY 2023-2024" but the source note at the bottom is unambiguous: "Rates indicate the percentage of teachers in an LEA in **2022-23** who did not return to teach in the same LEA in **2023-24**." Same convention applies in TWS-2022 page 7 (chart titled SY 2021-22, source note says "teachers in an LEA in 2020-21 who did not return … in 2021-22"). MSDE labels their attrition charts by the destination year. This is the convention used in essentially every state workforce dashboard.

Used `pdfplumber.extract_words` + x-coordinate matching to recover the bar values and pair each to its LEA label (the labels at the bottom of the chart are drawn rotated 90°, so they need character-level extraction). All 24 bar values matched to LEAs within tolerance; cross-checked TWS-2022 against the known facts (Allegany=7%, Cecil=7%, Dorchester=18%) and they aligned perfectly.

### 2. Looking for a TWS-2023 / a 2023 State Board doc with the 2021-22 → 2022-23 LEA breakdown (DEAD END)

Enumerated every 2023 State Board meeting (Jan, Feb, Mar, Apr, May-18, May-23, Jun, Jul-24, Jul-25, Aug, Sep-13, Sep-26, Oct-04, Oct-24, Nov-09, Dec-05). For each, listed every PDF on its agenda page:
- `https://marylandpublicschools.org/stateboard/Pages/meeting-agendas/2023/2023-MM-DD.aspx`

Only teacher-themed docs in 2023:
- `2023/0124/RegulationsDeepDiveEducatorPreparationLicensureJan2023.pdf` — licensure regs, no data
- `2023/0523/TeacherAppreciationWeekProclamation2023.pdf` — proclamation
- `2023/0725/TeacherCertificationAssessments.pdf` — certification assessments
- `2023/1024/PSSAM_SBOE_10_24_23_FINAL.pdf` — superintendents' assoc presentation, no LEA attrition

**Conclusion**: The State Board of Education skipped the annual workforce update in 2023. The next workforce report after the Aug 2022 AIB version (which had SY 2021-22 LEA data) was the May 2024 State Board deck (which had SY 2023-24 LEA data). No public document covers the 2021-22 → 2022-23 LEA breakdown.

### 3. AIB (Accountability and Implementation Board) — DEAD END for the missing year

- `https://aib.maryland.gov/Pages/presentations.aspx` — listed presentations. 2023 ones are about Blueprint essentials, MABE community engagement, MACo budget — none about teacher workforce data.
- `AIB 2024 Annual Report` (downloaded as `md_AIB_2024_Annual_Report.pdf`) — mentions teacher attrition trends qualitatively at state level only. No LEA breakdown.
- `dlslibrary.state.md.us/publications/Exec/AIB/ED5-409(b)(3)(2023)_2024.pdf` (AIB 2023 Annual Report) — same; high-level only.

### 4. MLDS Center — DEAD END

- `https://mldscenter.maryland.gov/centerreports.html` — lists the annual "Progress in Increasing the Preparation and Diversity of Teacher Candidates and New Teachers" reports.
- Downloaded `md_MLDS_2023_BlueprintTeacherDiversityReport.pdf` and `md_MLDS_2024_BlueprintTeacherDiversityReport.pdf`. These are pipeline/preparation/diversity reports, not LEA attrition.
- `LincoveBaltTeacherShortageSeptember2023.pdf` — Baltimore City only, not LEA-by-LEA.

### 5. Maryland Open Data Portal (Socrata) — DEAD END

Queried `https://opendata.maryland.gov/api/catalog/v1?q=...&search_context=opendata.maryland.gov` for: `teacher`, `educator`, `staff`, `attrition`. No MSDE K-12 staff/attrition dataset published on the portal. Only generic education-related items (school facility locations, "Choose Maryland" county comparisons, etc.). The unfiltered Socrata catalog returns OUSD/NYC/Massachusetts data which is not relevant.

### 6. Educator Workforce Dashboard (NEW LEAD, but inaccessible without a browser)

Found the **Maryland Educator Workforce Dashboard** at `https://marylandpublicschools.org/about/pages/dee/educator-dashboard.aspx`. The page embeds a Power BI report:

> `https://app.powerbigov.us/view?r=eyJrIjoiZDFhNWJjYTYtNTc0My00Y2Y1LThiYTctMTRhNjFkNzdlMGJjIiwidCI6IjYwYWZlOWUyLTQ5Y2QtNDliMS04ODUxLTY0ZGYwMjc2YTJlOCJ9`
>
> Resource key: `d1a5bca6-5743-4cf5-8ba7-14a61d77e0bc`
> Tenant: `60afe9e2-49cd-49b1-8851-64df0276a2e8`
> Backing cluster: `https://wabi-us-gov-virginia-redirect.analysis.usgovcloudapi.net/`

Attempted direct API access (`/public/reports/{id}/exploration`, `/public/reports/{id}/modelsAndExploration`, `/public/routing/cluster/{id}`) with browser-like headers — all returned `Connection reset by peer` or Power BI error pages. The Power BI Embedded "publishToWeb" flow requires a JS-rendered session to retrieve an access token, which curl/WebFetch cannot do.

**This dashboard almost certainly contains LEA-level historical attrition by year**, including the 2021-22 → 2022-23 transition. A follow-up using a real browser (Playwright/Selenium) or Power BI Pro/Embedded SDK would be the right next step. Alternatively, the user could screenshot the dashboard themselves and OCR the per-LEA bars.

### 7. Press / 3rd-party coverage — partial data only

- `marylandmatters.org/2023/03/26/...new-blueprint-reports-detail-difficulties/` (403 to WebFetch)
- `cnsmaryland.org/2024/03/18/marylands-teacher-shortage-...` — only Montgomery and Prince George's resignation counts.
- `washingtonpost.com/education/2023/08/09/dc-area-schools-teacher-resignations/` — only Montgomery (625) and Prince George's (1,126) resignations July 2022-July 2023. Not the full 24-LEA breakdown.
- PSSAM testimony: state-level "over 7,000 educators did not return to teaching in the 22/23 school year" (≈11.2% per their math) — no LEA breakdown.
- MABE 2025 conference deck (`md_MABE-2025_StaffSupplyDemand.pdf`, 32 pages, Kelly Meadows of MSDE-DEE) — only state-level attrition trends, no LEA-level chart for any year.

### 8. Wayback Machine — partial coverage

- `web.archive.org/cdx/search/cdx?url=marylandpublicschools.org/stateboard&matchType=prefix...` returned only ~30 unique 2023 PDFs.
- Confirmed no `TWS-2023`-named PDF or similar workforce-themed file from spring/summer 2023 was crawled.

### 9. Other dead ends checked

- `https://reportcard.msde.maryland.gov/` — confirmed Educator Equity Data is the only educator-related download; no staff attrition file exposed by file ID.
- `https://blueprint.marylandpublicschools.org/` — Blueprint program landing page, no data downloads.
- `https://aib.maryland.gov/ImplementationPlans/Pages/LEA%20Implementation%20Plans.aspx` — LEA Blueprint plans are submitted to AIB but linked via individual Google Drive folders (not enumerated on a single index page). Each LEA's plan is up to 98 pages of narrative — not a structured attrition dataset. Spot-check of one URL pattern (Anne Arundel 2024-2027) returned 404; the folder paths require navigation through the SharePoint UI.

### 10. Academic/researcher archives — DEAD END

- Searched OSF for "Bleiberg Kraft teacher turnover Maryland data" — no public replication archive found.
- TCF report ("Creating a More Diverse Teaching Workforce: Lessons for School Districts from Maryland") — about diversity/pipeline, no LEA attrition table.

## Recommended next steps if the user really needs the 2021-22 → 2022-23 LEA breakdown

The state-level figure (12.7%) is public, the LEA breakdown apparently was not published in any document I could find. Options:

1. **Scrape the Educator Workforce Dashboard with a real browser.** The Power BI report at the URL above likely has historical LEA-level attrition selectable by year. A Playwright script + `page.evaluate` to read tooltips, or a screenshot + manual transcription, would get the values in ~15-30 minutes of work.
2. **File a Maryland Public Information Act (PIA) request** to MSDE-DEE (Division of Educator Effectiveness, the unit that produces the dashboard) for "LEA-level teacher attrition rates for the SY 2021-22 → SY 2022-23 transition, by LEA."
3. **Email the dashboard contact.** MSDE-DEE is publishing this exact data interactively; they almost certainly have it in a CSV or PowerBI dataset and can share it.
4. **Email Bleiberg or Kraft** (Brown/Brookings) — they appear to have linked MSDE Staff Data extracts in their COVID labor market paper and may have the LEA-year panel.
5. **Compute from the StaffEmployed PDFs.** We have `md_2021-22_StaffEmployed.pdf`, `md_2022-23_StaffEmployed.pdf`, `md_2023-24_StaffEmployed.pdf`. These give teacher headcounts per LEA per Oct 15 of each year. The *net change* in teacher count per LEA between Oct 2021 and Oct 2022 is a *lower bound* on attrition (it nets out new hires). This isn't true attrition but may be useful for sanity-checking.

## Final advice for the v1 user-facing summary

The previous agent's report should be updated to say: "**TWS-2024 page 11 is the LEA-level attrition for the transition between SY 2022-23 and SY 2023-24** (i.e., teachers in 2022-23 who did not return in 2023-24). MSDE's chart-titling convention (`SY 2023-24 attrition`) labels by the destination year, not the source year." This was the cause of the confusion in v1.
