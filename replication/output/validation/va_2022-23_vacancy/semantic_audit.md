# Semantic Audit: VA JLARC Report 576, Appendix C, Table C-1 (SY2022-23, LEFT column)

Source: `va_jlarc_rpt576_teacher_pipeline.pdf`, pp. 66-70 (PDF). Audit focuses on the LEFT (SY2022-23) panel.

## 1. Column meanings (verbatim headers)

Appendix C is titled: **"Teacher vacancies by school division"**. The introductory text states:

> "This appendix includes public K-12 teacher vacancy data, by school division, collected by the Virginia Department of Education for the past two school years (SY2022-23 and SY2023-24)."

Table C-1 title: **"Public K-12 teacher vacancies, SY2022-23 and SY2023-24"**.

Column headers under the SY2022-23 panel (verbatim, line-wrapped in the PDF):

- **"School division"**
- **"Total FTE teacher positions"**
- **"Total unfilled FTE teacher positions"**
- **"Vacancy rate (%)"**

So columns measure: (a) total full-time-equivalent teacher positions in the division, (b) total UNFILLED FTE teacher positions, and (c) the vacancy rate as a percent (unfilled / total).

For SY2022-23 the NOTE clarifies "unfilled" means **reported vacant as of an October 1 snapshot** (not first-day-of-school): see Note quote in section 5. The SY2023-24 column uses a different definition ("actual or assumed to be vacant ... on the first day of school"), but that does not apply to our 2022-23 file.

## 2. Time reference

Verbatim from the table NOTE:

> "SY2022-23 data represents vacant public K-12 full-time equivalent positions reported by divisions as of **October 1, 2022**."

So SY2022-23 = October 1, 2022 snapshot (reported vacancies), NOT first day of school and NOT a yearly average.

## 3. Population scope

The table covers **"Public K-12 teacher"** positions, expressed as FTE, reported by **school divisions** to VDOE. No further inclusion/exclusion footnote (e.g., classroom vs. non-classroom, special-education-specific) is provided adjacent to Table C-1. The scope is whatever VDOE collected as "teacher" FTE from divisions — there is no explicit narrowing to "classroom teachers only" and no explicit exclusion of special education. "Teacher positions" is taken at face value (all public K-12 teacher FTE).

The bottom-of-table totals are: **Total FTE teacher positions = 92,579; Total unfilled = 3,573** for SY2022-23.

## 4. Does our CSV label match?

CSV columns: `school_division, total_fte_teacher_positions, total_unfilled_fte, vacancy_rate_pct`.

| CSV column | PDF column | Match? |
|---|---|---|
| `school_division` | "School division" | Yes |
| `total_fte_teacher_positions` | "Total FTE teacher positions" | Yes (verbatim) |
| `total_unfilled_fte` | "Total unfilled FTE teacher positions" | Yes in meaning; CSV name truncates "teacher positions" but the underlying quantity is the same |
| `vacancy_rate_pct` | "Vacancy rate (%)" | Yes |

Caveat (not a label mismatch but a methodology nuance): the PDF's SY2022-23 "unfilled" is **reported-vacant as of Oct 1, 2022**, whereas SY2023-24 uses "actual or assumed to be vacant ... on the first day of school." A consumer who treats both years as the same construct would be wrong; the SY2022-23 figure is an Oct 1 reported-vacancy count, not a first-day-of-school count. The CSV column name `total_unfilled_fte` is consistent with the PDF; users should consult this audit for the time-reference distinction.

## 5. Verbatim source / notes block (bottom of Table C-1)

> "SOURCE: JLARC staff analysis of Virginia Department of Education data, school years 2022-23 and 2023-24.
>
> NOTE: SY2022-23 data represents vacant public K-12 full-time equivalent positions reported by divisions as of October 1, 2022. SY2023-24 vacancy data reflects actual or assumed to be vacant public K-12 full-time equivalent positions on the first day of school for 123 divisions."

(Cells showing "-" in the unfilled and rate columns indicate zero / no reported vacancies; the SY2022-23 panel uses "-" for both unfilled count and rate, while the SY2023-24 panel writes "0.0" for the rate.)
