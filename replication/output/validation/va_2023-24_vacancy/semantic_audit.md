# Semantic Audit: va_2023-24_vacancy_jlarc_appx_c.csv

**Source:** JLARC Report 576, Appendix C, Table C-1 (pages 66-70).
**Title (verbatim):** "Public K–12 teacher vacancies, SY2022–23 and SY2023–24"

## 1. Column measurements (verbatim PDF headers)

The PDF table has two side-by-side blocks. For SY2023-24 (RIGHT block), the columns are:

- **"School division"**
- **"Total FTE teacher positions"**
- **"Total unfilled FTE teacher positions"**
- **"Vacancy rate (%)"**

The footnote defines "unfilled FTE" as **"actual or assumed to be vacant"** (not strictly confirmed vacant):

> "SY2023–24 vacancy data reflects actual or assumed to be vacant public K–12 full-time equivalent positions on the first day of school for 123 divisions."

This is a critical distinction from the SY2022-23 column, whose note says only "reported by divisions" (no "assumed" language).

## 2. Time reference (verbatim)

> "SY2023–24 vacancy data reflects actual or assumed to be vacant public K–12 full-time equivalent positions **on the first day of school** for 123 divisions."

(SY2022-23, by contrast, is "as of October 1, 2022.")

## 3. Population scope (verbatim)

> "This appendix includes **public K–12 teacher vacancy data**, by school division, collected by the Virginia Department of Education for the past two school years (SY2022–23 and SY2023–24)."

Footnote reiterates: "public K–12 full-time equivalent positions." No restriction to classroom-only nor exclusion of special education is stated. Scope = all public K–12 teacher FTE positions.

## 4. CSV column labeling vs. PDF

| CSV column | PDF header | Match? |
|---|---|---|
| `school_division` | "School division" | Yes |
| `total_fte_teacher_positions` | "Total FTE teacher positions" | Yes |
| `total_unfilled_fte` | "Total unfilled FTE teacher positions" | Substantively yes; CSV name drops "teacher positions" but the meaning is identical |
| `vacancy_rate_pct` | "Vacancy rate (%)" | Yes |

Labels match the PDF's substantive meaning. Minor: `total_unfilled_fte` is an abbreviation of "Total unfilled FTE teacher positions" — acceptable.

## 5. Row count / 123 divisions

The methodology says vacancy data is reported "for 123 divisions." Virginia has 132 school divisions total. The gap of 9 divisions is consistent with the PDF table itself: the SY2023-24 column shows 8 divisions reporting "-" for the unfilled FTE count (Grayson, Lexington, Russell, Staunton — all with explicit "0.0" rates — plus rows where data appears suppressed). Some divisions did not report vacancy data for SY2023-24. The "123 divisions" likely refers to those reporting non-missing data; the total row sums to 90,466 FTE / 4,104 unfilled.

## 6. Methodology / Notes section (verbatim)

> **SOURCE:** JLARC staff analysis of Virginia Department of Education data, school years 2022–23 and 2023–24.
>
> **NOTE:** SY2022–23 data represents vacant public K–12 full-time equivalent positions reported by divisions as of October 1, 2022. SY2023–24 vacancy data reflects actual or assumed to be vacant public K–12 full-time equivalent positions on the first day of school for 123 divisions.

**Total row (SY2023-24):** Total FTE = 90,466; Total unfilled FTE = 4,104; no overall rate printed.

## Verdict

Column labels in the CSV faithfully represent the PDF semantics for SY2023-24. The "unfilled FTE" measure is **not strictly vacant**; per JLARC's own note it includes positions "assumed to be vacant" on the first day of school. Any downstream interpretation should treat the SY2023-24 figure as a vacancy-plus-assumed-vacancy count, not a clean vacancy count, and should NOT be directly compared to the SY2022-23 October-1 reported-vacancy figure without caveat.
