# Semantic Audit — md_2022-23_to_2023-24_LEA_attrition_TWS-2024_p11.csv

Source: Maryland Teacher Workforce Study (TWS) 2024, "Maryland's Teacher Workforce: Supply, Demand, and Diversity" (MSDE, 05.21.2024), chart on **page 11** (slide 9).

## 1. What does the percentage measure?

Chart title (verbatim): **"Maryland Teacher Attrition by LEA, SY 2023-2024"**

Subtitle / lead text (verbatim): **"In the SY2023-2024, 12% of teachers did not return to teach in the same LEA from the prior school year. Attrition by LEA varied from a low of 7% to a high of 18%."**

Source/footnote (verbatim, page 11): **"Source: MSDE Staff Data, As of October 15 of each school year. Rates indicate the percentage of teachers in an LEA in 2022-23 who did not return to teach in the same LEA in 2023-24."**

The footnote disambiguates: the title's "SY 2023-2024" refers to the **year of measurement / non-return** (the year teachers were observed as having left). The base population is teachers **employed in 2022-23**; the percentage is those who **did not return in 2023-24**. So the transition measured is **2022-23 -> 2023-24**.

## 2. Time reference

The data describes the transition from school year **2022-23 to 2023-24**. Exact wording: "the percentage of teachers in an LEA in 2022-23 who did not return to teach in the same LEA in 2023-24." Snapshot dates are October 15 of each school year.

## 3. LEA scope

"LEA" = Local Education Agency. Per the report's framing on page 1: "the Maryland State Department of Education (MSDE) is collaborating with local education agencies (LEAs)..." The page-11 chart's x-axis lists the 24 Maryland LEAs (Allegany, Anne Arundel, Baltimore City, Baltimore County, Calvert, Caroline, Carroll, Cecil, Charles, Dorchester, Frederick, Garrett, Harford, Howard, Kent, Montgomery, Prince George's, Queen Anne's, Saint Mary's, Somerset, Talbot, Washington, Wicomico, Worcester). Rates are LEA-specific same-LEA non-return rates.

## 4. Population scope

Verbatim from page 10 (companion chart definition for the LEA series): **"The percentage of Maryland public school teachers in the prior year who did not return as a teacher in the same LEA in the following year."**

Population = **Maryland public school teachers** (no narrower "classroom-only" restriction stated). The denominator is teachers employed in the LEA in 2022-23; the numerator is those not employed as a teacher in that same LEA in 2023-24. Source is "MSDE Staff Data" snapshot at October 15.

## 5. Are intra-LEA transfers counted as attrition?

No. The footnote specifies "did not return to teach in the **same LEA**." Page 10 separately distinguishes three nested attrition definitions — School, LEA, and State — explicitly showing that LEA attrition does NOT count school-to-school moves within the same LEA, and State attrition does not count LEA-to-LEA moves within Maryland. Intra-LEA school transfers therefore do **not** count toward the LEA attrition rate shown on page 11. Inter-LEA transfers within Maryland **do** count as LEA attrition (they are excluded only at the State level).

## 6. Does the column label match?

Column: `pct_teachers_2022-23_did_not_return_2023-24`.

Per the page-11 footnote: "percentage of teachers in an LEA in **2022-23** who did not return to teach in the same LEA in **2023-24**."

The column label matches the PDF semantics exactly — base year 2022-23, non-return year 2023-24, LEA-level same-LEA non-return rate. **LABEL_OK.**

The chart title's "SY 2023-2024" is the observation/non-return year and is consistent with our labeling convention of naming the transition by both endpoints.

## 7. Exact footnote / methodology adjacent to the chart

Page 11, directly under the bar chart:

> "Source: MSDE Staff Data, As of October 15 of each school year. Rates indicate the percentage of teachers in an LEA in 2022-23 who did not return to teach in the same LEA in 2023-24."

Companion definitions, page 10 (left-hand sidebar):

> "LEA — The percentage of Maryland public school teachers in the prior year who did not return as a teacher in the same LEA in the following year."
