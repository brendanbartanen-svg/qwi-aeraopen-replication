# Pennsylvania All-Staff Turnover Data Hunt — V2

## Outcome

**SUCCESS.** PA does not publish a pre-aggregated all-staff retention/attrition file (only the classroom-teacher one already found). However, PDE publishes the **Professional Personnel Individual Staff** files — per-person, per-assignment, per-school-year records with a stable cross-year identifier (`PublicID`) that makes it possible to compute district-level all-staff turnover directly.

District-level all-staff leaver/turnover counts for SY 2021-22 -> 2022-23 and SY 2022-23 -> 2023-24 have been computed and saved to:

- `pa_all_staff_turnover_computed.xlsx` (two sheets, one per transition)

Underlying raw files (per-person, ~32 MB each) also saved:

- `pa_2020-21_individual_staff.xlsx`
- `pa_2021-22_individual_staff.xlsx`
- `pa_2022-23_individual_staff.xlsx`
- `pa_2023-24_individual_staff.xlsx`
- `pa_2024-25_individual_staff.xlsx`
- `pa_individual_staff_notes_and_data_elements.xlsx` (codebook)

Bonus: the **CT attrition** (statewide-only) workbook was also downloaded:

- `pa_2022-23_to_2023-24_attrition_CT.xlsx` (classroom-teacher exits-from-teaching)

## Why this is the right data source

The paper (Bleiberg & Nguyen 2026) states the validation data is "available for staff, administrators, and teachers" for CO, MD, and PA. PDE achieved this by publishing the raw individual file rather than an aggregated all-staff table. The previous-agent hunt stopped at the aggregated `2022-23-2023-24-retention-classroom-teachers.xlsx`, which only covers CT.

## What's in the Individual Staff files

`pa_2022-23_individual_staff.xlsx` (Sheet `2022_23_Professional_Personnel`, 188,520 rows / 158,849 unique person-LEA pairs / 154,402 unique persons):

Columns: `SY, Staff Snapshot Date, PublicID, Last Name, First Name, ..., AnnualSalary, ..., Status, AUN, LEAName, LEATypeDescription, LEACountyCd, ..., FT/PT, JobClass, Primary Assignment, AssignCd, ..., EDF Category, Category Description 2017-, FTE%`.

Categories (Category Description) breakdown for 2021-22 person-LEA records:
- Classroom Teachers: 126,409
- Coordinate Services: 16,337
- Others: 7,128
- School Administrator: 5,146
- Other Supervisory Coordinator: 2,311
- Chief School Administrator: 770

LEA types: School District (133,974), Charter School (14,270), IU (7,227), CTC (2,551), SJCI (79).

Per the codebook, "All Professional Personnel are identified with a unique PublicID that is consistent from one year to the next." This is the exact identifier needed for matching.

## Computed turnover summary

| Transition | Districts | Headcount | Stayers (same LEA) | Movers (LEA change) | Leavers (exit PA edu) | Turnover (mov+leav) |
|---|---:|---:|---:|---:|---:|---:|
| 2021-22 -> 2022-23 | 782 | 158,101 | 140,143 (88.6%) | 7,509 (4.7%) | 10,449 (6.6%) | 17,958 (11.4%) |
| 2022-23 -> 2023-24 | 778 | 158,849 | 142,704 (89.8%) | 7,150 (4.5%) | 8,995 (5.7%) | 16,145 (10.2%) |

Each district row in the workbook contains all-staff totals plus break-outs for CT, admin, and other:

```
AUN, headcount_all, stayer_all, mover_all, leaver_all, turnover_all,
retention_rate_all, leaver_rate_all, turnover_rate_all,
headcount_ct, stayer_ct, mover_ct, leaver_ct,
headcount_other, stayer_other, mover_other, leaver_other,
headcount_admin, stayer_admin, mover_admin, leaver_admin
```

## Sanity check vs. PDE's published CT retention

PDE's `Statewide` sheet for SY 2022-23 -> 2023-24 reports `ALL CT` GROUP_SIZE = 127,441 with N RETAINED CT = 113,608 (89.1%). Our computation (matching on PublicID, treating any role in y1 as the unit) gives slightly different totals because PDE filters on `Primary Assignment = CT` (we use the broader EDF category). The all-staff totals shown above are not directly comparable to any PDE-published number — that's exactly why the file did not previously exist.

## URLs tried (full search space)

### Successful — files downloaded to `state_validation/`

| Status | URL |
|---|---|
| 200 | https://www.pa.gov/content/dam/copapwp-pagov/en/education/documents/data-and-reporting/professional-and-support-personnel/individual/2020-21%20professional%20personnel%20individual%20staff.xlsx |
| 200 | https://www.pa.gov/content/dam/copapwp-pagov/en/education/documents/data-and-reporting/professional-and-support-personnel/individual/2021-22%20professional%20personnel%20individual%20staff%20report.xlsx |
| 200 | https://www.pa.gov/content/dam/copapwp-pagov/en/education/documents/data-and-reporting/professional-and-support-personnel/individual/2022-23%20professional%20personnel%20individual%20staff%20report.xlsx |
| 200 | https://www.pa.gov/content/dam/copapwp-pagov/en/education/documents/data-and-reporting/professional-and-support-personnel/individual/2023-24%20professional%20personnel%20individual%20staff.xlsx |
| 200 | https://www.pa.gov/content/dam/copapwp-pagov/en/education/documents/data-and-reporting/professional-and-support-personnel/individual/2024-25%20professional%20personnel%20individual%20staff.xlsx |
| 200 | https://www.pa.gov/content/dam/copapwp-pagov/en/education/documents/data-and-reporting/professional-and-support-personnel/individual/professional%20personnel%20individual%20staff%20report%20notes%20and%20data%20elements.xlsx |
| 200 | https://www.pa.gov/content/dam/copapwp-pagov/en/education/documents/data-and-reporting/professional-and-support-personnel/2022-23-2023-24-attrition-classroom-teacher-exits-from-teaching.xlsx |
| 200 | https://www.pa.gov/content/dam/copapwp-pagov/en/education/documents/data-and-reporting/professional-and-support-personnel/2023-24-2024-25-attrition-classroom-teacher-exits-from-teaching.xlsx |

### 404 — patterns that did NOT exist

| URL |
|---|
| `.../individual/2020-21%20professional%20personnel%20individual%20staff%20report.xlsx` (only without `report`) |
| `.../2021-22-2022-23-retention-classroom-teachers.xlsx` (confirms missing; matches v1 finding) |
| `.../2020-21-2021-22-retention-classroom-teachers.xlsx` |
| `.../2021-22-2022-23-attrition-classroom-teacher-exits-from-teaching.xlsx` |
| `.../2022-23-2023-24-retention-professional-personnel.xlsx` |
| `.../2022-23-2023-24-retention-professional-staff.xlsx` |
| `.../2022-23-2023-24-retention-all-staff.xlsx` |
| `.../2022-23-2023-24-retention-professional-and-support-personnel.xlsx` |
| `.../2022-23-2023-24-retention.xlsx` |
| `.../2022-23-2023-24-attrition-professional-personnel.xlsx` |
| `.../2022-23-2023-24-retention-administrators.xlsx` |
| `.../2023-24-2024-25-retention.xlsx` |
| `.../retention.xlsx` |
| `.../professional-personnel-retention.xlsx` |
| `.../professional-staff-retention.xlsx` |
| `.../staff-mobility.xlsx` |
| `.../personnel-mobility.xlsx` |
| `.../professionalstaffterminationcodessy2015-2023.xlsx` |
| `.../professionalpersonnelterminationcodessy2015-2023.xlsx` |
| `.../professional%20personnel%20termination%20codes%20sy2015-2023.xlsx` |
| `.../staffterminationcodessy2015-2023.xlsx` |
| `.../administratorterminationcodessy2015-2023.xlsx` |
| `.../allstaffterminationcodessy2015-2023.xlsx` |
| `.../administrator-retention.xlsx` |

All 404s consistently returned a 76,061-byte HTML 404 page; that's how the v1 hunt confirmed each URL doesn't exist.

### Pages crawled

- `https://www.pa.gov/en/agencies/education/data-and-reporting/school-staff/professional-and-support-personnel.html` (full file inventory)
- `https://www.pa.gov/en/agencies/education/data-and-reporting/school-staff.html` (subpage map)
- `https://public.tableau.com/profile/padeptofed` (no usable file URLs returned; Tableau dashboards are interactive only)
- `https://www.pa.gov/agencies/education/data-and-reporting/school-staff/professional-and-support-personnel` (re-crawled to get Individual Staff URLs missed in v1)

### External leads checked

- `https://ceepa.psu.edu/news/pennsylvania-teacher-attrition-and-turnover-from-2014-to-2024` -> CEEPA brief uses PDE employment files, classroom-teacher only (Ed Fuller, July 2024)
- `https://ceepablog.wordpress.com/wp-content/uploads/2024/07/ceepa-and-pedc-research-brief-2024-5-_-teacher-attrition-and-turnover-in-pa-1.pdf` -> teachers-only methodology
- `https://www.pa.gov/.../educator-workforce-strategy/2024%20educator%20workforce%20annual%20report_pde_final.pdf` -> cites PDE retention/attrition tables which are CT-only; mentions admin certifications but not admin turnover/retention by district
- `https://www.pa.gov/.../educator-workforce-strategy/2025%20pde%20educator%20workforce%20annual%20report-final.pdf` -> same; explicitly uses Retention and Attrition CT-only reports
- `https://github.com/joshbleiberg` (6 repos: stackedev, education_attention, covid, common_core, EventStudyInteract, essa_sch_acct) -> none contain replication for this paper. `covid` repo is unrelated (RI infection estimator).
- `https://tuan-d-nguyen.github.io/research.html` -> no Bleiberg co-authored replication package linked.
- `https://www.education.pitt.edu/faculty/directory/josh-bleiberg/` -> no replication or data links.
- OSF search via API for "Bleiberg teacher" -> no hits for this paper.

### Tools tried that didn't help

- `web.archive.org/web/2024*/education.pa.gov/...` — Claude's WebFetch is blocked from web.archive.org.

## Recommended construction

For QWI validation, use `pa_all_staff_turnover_computed.xlsx`:

- **SY 2021-22 turnover**: `Turnover_2021-22_to_2022-23` sheet, `turnover_all` (= `leaver_all + mover_all`) or `leaver_all` alone.
- **SY 2022-23 turnover**: `Turnover_2022-23_to_2023-24` sheet, same fields.

The school year labeling convention matches the paper (state record year = SY that the cohort was last observed in, so the SY 2021-22 turnover is measured from SY 2021-22 -> SY 2022-23 transition).

`AUN` is the 9-digit Agency Unique Number that joins to the existing `pa_2021-22_prof_staff.xlsx` and `pa_2022-23_prof_staff.xlsx` files (Sheet `LEA_FT+PT`, `AUN` column).

If a definition closer to PDE's "Primary CT only" measure is needed, re-run with `Primary Assignment = Yes` filter — the raw individual files are saved so this is straightforward.

## Methodology notes

- Person counts deduplicate over multiple assignments within an LEA (e.g., a teacher who has two part-time assignments in the same district counts once).
- `PublicID` is consistent year over year per PDE codebook ("Notes" sheet of the data-elements workbook): "All Professional Personnel are identified with a unique PublicID that is consistent from one year to the next."
- "Leaver" definition used: PublicID present in y1, absent from y2 entirely. This is exits from PA public-LEA professional personnel rolls (does not distinguish retirement vs. private sector vs. another state).
- "Mover": PublicID in y2 at an AUN different from y1.
- "Stayer": PublicID at same AUN in y2.
- Includes Charter Schools, IUs, CTCs, and SJCI by default — filter on `LEATypeDescription = 'School District'` for school-district-only sample.
