# Semantic Audit: va_2021-22_turnover_jlarc_appx_j2.csv

Source: JLARC Report 568, Appendix J, Table J-2 ("Teacher turnover by school division"), PDF pp. 157-161; methodology from Appendix B ("Teacher turnover (Chapter 5)"), PDF pp. 107-108.

## 1. Column meanings (verbatim PDF headers)

Table J-2 headers (verbatim): `Division`, `# departing from SY21 and SY22`, `% departing from SY21 and SY22`, `PPA* departing per year`, `% point change`. The asterisk note reads: `*PPA: Pre-pandemic average`.

The "departing" definition is stated in the prose immediately above the table:

> "JLARC staff used teacher licensure data from VDOE's Master Schedule Collection database to calculate the number of teachers who departed employment from each school division from one school year to the next (Appendix B). The number of teachers departing each division includes teachers who left employment in Virginia's public school system altogether, teachers who became administrators in their current school division or another school division, and teachers who accepted a teaching position in another division; it does not include teachers who took another teaching job in their current division."

So "departing" = left the school division (or left teaching in VA). Intra-division transfers (teacher -> teacher in same division) are NOT counted. Intra-division teacher-to-administrator IS counted as departing. The denominator/population is "teachers" identified via license-type and division-number matching in VDOE's Master Schedule Collection.

## 2. Time reference

The header phrase is "SY21 and SY22" (i.e., from SY 2020-21 to SY 2021-22). Chapter 5 confirms:

> "The majority of divisions (86 of 131) had higher teacher turnover between the 2020-21 and 2021-22 school year when compared with before the pandemic..."

Departure is defined as "from one school year to the next." So the count is teachers employed in SY 2020-21 who did NOT remain as teachers in the same division in SY 2021-22. It is NOT "SY 2021-22 to SY 2022-23." The header label "SY22" refers to the destination year (2021-22), the year by which the teacher had departed.

## 3. "Pre-pandemic average" definition

Table J-2 NOTE (verbatim, page 161): "Pre-pandemic average includes five years from 2015-16 school year through the 2019-2020 school year. n.a. = not available."

So PPA is a 5-year average of per-year turnover rates covering SY 2015-16, 2016-17, 2017-18, 2018-19, and 2019-20 (NOT the 3-year window the auditor hypothesized).

## 4. Population scope

Appendix B (Teacher turnover, Chapter 5): the analysis uses VDOE Master Schedule Collection licensure records, classified by license type (teacher vs. administrator) and division number. For division-level turnover (Table J-2), JLARC included: teachers who left VA public K-12 altogether, teachers who became administrators (same or different division), AND teachers who switched divisions. No explicit FTE/full-time qualifier is given; the unit is licensed teachers in the Master Schedule Collection. Administrators are tracked separately. There is no restriction to "classroom teachers only" beyond the license-type filter.

## 5. Label-direction check

The PDF header is "% departing from SY21 and SY22" with the methodology stating departure is computed "from one school year to the next." The departing cohort is the SY 2020-21 teachers who did not return as teachers-in-same-division in SY 2021-22. Our CSV column `pct_departing_sy21_to_sy22` is ambiguous - read literally as a transition, "sy21_to_sy22" suggests SY 2020-21 -> SY 2021-22, which matches. But a reader could misread "sy21_to_sy22" as SY 2021-22 -> SY 2022-23. The PDF's own shorthand ("SY21 and SY22") is itself ambiguous; only the prose disambiguates. The numeric direction is correct, but the column name benefits from a clearer descriptor (e.g., `pct_departed_after_sy2020_21`).

## 6. Verbatim Notes / methodology adjacent to table

Table J-2 SOURCE/NOTE (p. 161): "SOURCE: JLARC analysis of Virginia Department of Education data, 2015-16 to 2021-22. NOTE: Pre-pandemic average includes five years from 2015-16 school year through the 2019-2020 school year. n.a. = not available."

Pre-table prose (p. 157, quoted in section 1) and Appendix B "Teacher turnover (Chapter 5)" methodology (pp. 107-108) further define the categories included in division-level turnover.
