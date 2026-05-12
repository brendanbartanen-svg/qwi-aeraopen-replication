# Semantic Audit: VA JLARC Report 568, Appendix J-1 (Teacher Vacancies)

## 1. Column headers and what each measures

The table is titled **"TABLE J-1 — Number of teacher vacancies by school division"**.

The column headers appear in two rows. Verbatim:

- `Division`
- `PPA* # vacant` (PPA = "Pre-pandemic average")
- `SY22 # vacant`
- `SY22 % vacant`
- `% change`

A starred footnote clarifies: **"*PPA: Pre-pandemic average"**.

The introductory paragraph for the appendix states:
> "The Virginia Department of Education (VDOE) collects data on the number of **vacant teacher positions** in each division in October of each year. Prior to 2021, this data was collected through Supply and Demand reports. In 2021, VDOE started collecting vacancy data through the Positions and Exits Collection (PEC) system. For both data collection methods, **data is as of a specific point in time**."

So "vacancies" measures **vacant teacher positions** (positions, not unfilled FTEs reported in headcount-equivalent terms — though PPA values include fractional numbers because they are five-year averages of integer counts). They are measured as a **point-in-time October snapshot**, NOT as of the first day of school. The Notes section confirms: **"SY22 vacancies are as of October 2021."**

## 2. What is "pre-pandemic average"?

From the table's NOTE line verbatim:
> "Pre-pandemic average represents a **five-year average from 2015–16 through 2019–20**."

So PPA = mean of vacant-position counts across school years 2015-16, 2016-17, 2017-18, 2018-19, and 2019-20.

## 3. What is "SY 2022" / "SY22"?

The SOURCE line states the data spans "2015–16 through 2021–22." The NOTE specifies "SY22 vacancies are as of October 2021." Therefore **SY22 = SY 2021-22** (the academic year that began in fall 2021 and ended in spring 2022). It is NOT SY 2022-23.

## 4. Population scope

The appendix introduction states it provides data on the **"teacher workforce"** including **"(1) teacher vacancies, (2) number of teachers leaving each division (i.e., turnover), and (3) teacher quality data."** Table J-1 specifically measures **"vacant teacher positions"** — teaching positions only, not all school staff (no administrators, support staff, etc., are included in this table).

## 5. Does our column labeling correctly describe the data?

**LABEL_OK.** The CSV columns map cleanly:

- `school_division` <- `Division`
- `pre_pandemic_avg_vacancies` <- `PPA # vacant` (5-yr avg, 2015-16 through 2019-20)
- `num_vacant_sy22` <- `SY22 # vacant` (October 2021 snapshot, i.e., SY 2021-22)
- `pct_vacant_sy22` <- `SY22 % vacant`
- `pct_change_from_ppa` <- `% change`

The `_sy22` suffix correctly denotes **SY 2021-22** (the year ending in 2022), consistent with JLARC's own "SY22" shorthand in the published table. No mislabeling detected.

## 6. Exact methodology / Notes adjacent to the table

Verbatim from the page 153 introduction:
> "The Virginia Department of Education (VDOE) collects data on the number of vacant teacher positions in each division in October of each year. Prior to 2021, this data was collected through Supply and Demand reports. In 2021, VDOE started collecting vacancy data through the Positions and Exits Collection (PEC) system. For both data collection methods, data is as of a specific point in time."

Verbatim SOURCE and NOTE under Table J-1 (page 157):
> "SOURCE: JLARC analysis of Virginia Department of Education vacancy data, 2015–16 through 2021–22"
>
> "NOTE: SY22 vacancies are as of October 2021. Pre-pandemic average represents a five-year average from 2015–16 through 2019–20."
