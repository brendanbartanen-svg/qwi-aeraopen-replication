# Semantic Audit: md_2020-21_to_2021-22_LEA_attrition_TWS-2022_p7.csv

**Source:** Maryland Teacher Workforce Study 2022 (TWS-2022), p.7, chart titled "Maryland Teacher Attrition by LEA".

---

## 1. What does the percentage measure?

The percentage measures teachers who did not return to teach **in the same LEA** the following year. From the chart's own annotation (p.7, verbatim):

> "Rates indicate the percentage of teachers in an LEA in 2020-21 who did not return to teach in the same LEA in 2021-22"

The p.6 definitions panel further clarifies LEA-level attrition (verbatim):

> "LEA — The percentage of Maryland public school teachers in the prior year who did not return as a teacher in the same LEA in the following year"

This is **LEA-level attrition** (leaving the LEA), NOT state-level attrition (leaving Maryland teaching entirely). A teacher who moves from LEA A to LEA B is counted as attrition for LEA A. A teacher who leaves teaching entirely is also counted. A teacher who moves between schools within the same LEA is NOT counted (that is "School" attrition only). So this captures both (a) teachers leaving teaching entirely and (b) teachers transferring to a different Maryland LEA — but excludes intra-LEA school transfers.

## 2. What is the time reference?

The transition is from school year **2020-21 to 2021-22**. Verbatim from p.7 annotation:

> "...teachers in an LEA in 2020-21 who did not return to teach in the same LEA in 2021-22"

The chart's narrative sentence (p.7) labels the rate by the LATER year: "In the 2021-2022 school year, 10% of teachers did not return to teach from the prior school year." But the cohort being measured is the 2020-21 teaching workforce; non-return is observed as of the 2021-22 snapshot. Source note: "MSDE Staff Data, As of October 15 of each school year."

## 3. What is "LEA" scope?

LEA = Local Education Agency. In Maryland, LEAs correspond to the 24 local school systems: 23 counties + **Baltimore City** as a separate LEA. The chart explicitly lists all 24, including "Baltimore City" and "Baltimore County" as separate bars (verbatim from chart: "Allegany, Anne Arundel, Baltimore City, Baltimore County, Calvert, Caroline, Carroll, Cecil, Charles, Dorchester, Frederick, Garrett, Harford, Howard, Kent, Montgomery, Prince George's, Queen Anne's, Saint Mary's, Somerset, Talbot, Washington, Wicomico, Worcester").

## 4. What is the population scope?

Verbatim definition (p.6): "Maryland public school teachers". No further restriction (e.g., to "classroom teachers" or "full-time") is provided in the chart or its adjacent annotation. The data source is "MSDE Staff Data, As of October 15 of each school year" — i.e., the October 15 staff snapshot. No FTE filter is documented on these pages.

## 5. Are intra-LEA transfers (school-to-school within the same LEA) counted as attrition?

**No.** Per the p.6 definition panel, intra-LEA school-to-school moves are captured under the "School" measure ("did not return as a teacher in the same school"), not the "LEA" measure. The LEA measure requires that the teacher did not return to teach in the same LEA. A teacher who switches schools but stays within the LEA still counts as returning to the LEA and is NOT in this numerator.

## 6. Does our column labeling match the PDF's measure?

**Yes — LABEL_OK.** Our column header `pct_teachers_2020-21_did_not_return_2021-22` correctly references the cohort (2020-21 teachers) and the non-return year (2021-22). The CSV filename `md_2020-21_to_2021-22_LEA_attrition_TWS-2022_p7.csv` matches the chart's scope (LEA-level attrition). The only refinement would be to make explicit that "did not return" is "to the same LEA" (vs. to teaching entirely), but the file path's `LEA_attrition` token disambiguates this.

## 7. Verbatim footnote / methodology adjacent to the chart

From p.7:

> "Maryland Teacher Attrition by LEA
> In the 2021-2022 school year, 10% of teachers did not return to teach from the prior school year. Attrition by LEA varied with a low of 7% in Allegany and Cecil to a high of 18% in Dorchester.
> ...
> Rates indicate the percentage of teachers in an LEA in 2020-21 who did not return to teach in the same LEA in 2021-22
> Statewide LEA%: 10.0%
> Source: MSDE Staff Data, As of October 15 of each school year."
