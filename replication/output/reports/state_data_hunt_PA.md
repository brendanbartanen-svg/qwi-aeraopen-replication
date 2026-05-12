# Pennsylvania Turnover Data Hunt - Summary

## Outcome

Found two new PDE datasets that, combined with the existing Professional Staff Summaries, allow direct computation of district-level classroom-teacher turnover for **2021-22 and 2022-23**.

## New files downloaded to `replication/data/raw/state_validation/`

1. **`pa_classroom_teacher_termination_2015-2023.xlsx`** (1.6 MB)
   - URL: `https://www.pa.gov/content/dam/copapwp-pagov/en/education/documents/data-and-reporting/professional-and-support-personnel/classroomteacherterminationcodessy2015-2023.xlsx`
   - One sheet per school year, 2015-16 through 2022-23. Sheets `2021-22` and `2022-23` both present.
   - Fields: `SY, COUNTY_CD, COUNTY, IU_AUN, DISTRICT_CODE, DISTRICT_NAME, ORG_TYPE, TERMINATION_CODE, TERMINATION_DESC, COUNT`. Long format: one row per LEA x termination reason.
   - 2021-22: 731 districts, 6,291 SD classroom-teacher leavers; 2022-23: 743 districts, 8,414 leavers (SD only; file also covers CS, CTC, IU, SJCI).
   - Headers are on row 2 (use `header=1`).

2. **`pa_2022-23_to_2023-24_retention.xlsx`** (1.3 MB)
   - URL: `https://www.pa.gov/content/dam/copapwp-pagov/en/education/documents/data-and-reporting/professional-and-support-personnel/2022-23-2023-24-retention-classroom-teachers.xlsx`
   - District-level retention/mobility with `GROUP_SIZE`, `N RETAINED CT`, `% RETAINED CT`, `N NEW LEA CT` (moved LEA), `N EXITED ED`, `% EXITED ED`. Sheets: `All, By Gender, By Race-Ethnicity, By Years in Education, By Years in the LEA, By Highest Degree, Statewide, Statewide Exits`.
   - This file gives turnover for SY 2022-23 directly. The analogous **2021-22 to 2022-23 file is no longer hosted by PDE** (confirmed 404 on all canonical pa.gov paths; legacy `education.pa.gov` URLs return an HTML redirect page despite HTTP 200).

## LEA matching

All three PA files share the same 9-digit AUN identifier (`AUN` in Prof Staff Summary, `DISTRICT_KEY` in retention, `DISTRICT_CODE` in termination). Verified joins: 499/499 SDs match Staff <-> Retention; 490/499 match Staff <-> Termination (9 districts had zero reported leavers).

In `pa_2021-22_prof_staff.xlsx` and `pa_2022-23_prof_staff.xlsx`, use sheet **`LEA_FT+PT`** with `header=6`; the `AUN` column is the join key and `CT` is the classroom-teacher headcount.

## Recommended turnover construction

- **SY 2022-23 turnover**: use `pa_2022-23_to_2023-24_retention.xlsx` directly (`% EXITED ED` + `% NEW LEA CT` = classroom-teacher turnover rate; `100 - % RETAINED CT` is the broader leaving-as-CT rate).
- **SY 2021-22 turnover**: compute as `COUNT / CT_headcount` from termination file (2021-22 sheet) divided by the CT count in `pa_2021-22_prof_staff.xlsx` LEA_FT+PT sheet. Sum termination COUNT across all reasons (or filter by reason). This is comparable in spirit to the retention file's exits.

Year-over-year staff-count matching is not needed; explicit leaver data is available.
