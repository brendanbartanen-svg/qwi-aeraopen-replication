# Agent rates: hypothesis tests for NNJF/100 specification

## Paper target (Table A2, 1/Emp weighted, pooled)
- p25=0.53, p50=1.080, p75=2.6, mean=3.32, sd=9.30
- 2019: p50=0.43, mean=0.73 / 2020: 0.51, 0.93 / 2021: 0.31, 0.62 / 2023: 0.40, 0.69

## Naive baseline (current pipeline)
`100 * avg(FrmJbLsS over 4 sy-quarters) / emp_q4_lag` → median 2.96, mean 5.30 (~2.7× too big).

## Hypothesis results (school-year and pooled-quarter)

| Hypothesis | p25 | p50 | p75 | mean | sd | 2019 med | 2020 med | 2021 med | 2023 med |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| **PAPER** | 0.53 | **1.080** | 2.60 | 3.32 | 9.30 | 0.43 | 0.51 | 0.31 | 0.40 |
| H1_FJSEmpS_rate_avg | 2.81 | 3.863 | 5.23 | 8.24 | 80.45 | 3.56 | 4.36 | 3.10 | 3.65 |
| H2_FJSEmpS_rate_sum | 11.23 | 15.437 | 20.90 | 32.82 | 312.05 | 14.23 | 17.42 | 12.40 | 14.59 |
| H3_FJSEmpS_ratio_of_sums | 2.72 | 3.704 | 4.95 | 6.78 | 72.06 | 3.41 | 4.17 | 2.95 | 3.45 |
| H4_SepBegR_avg | 0.06 | 0.076 | 0.10 | 0.08 | 0.05 | 0.07 | 0.09 | 0.06 | 0.08 |
| H5_HirAEndReplr_avg | 0.03 | 0.039 | 0.05 | 0.04 | 0.02 | 0.04 | 0.03 | 0.03 | 0.04 |
| H6_TurnOvrS_avg | 0.05 | 0.061 | 0.08 | 0.07 | 0.03 | 0.06 | 0.06 | 0.06 | 0.06 |
| H7_SepEmp_rate_avg | 8.13 | 10.700 | 13.80 | 11.90 | 6.74 | 10.43 | 11.37 | 9.80 | 10.63 |
| H8_avgFJS_over_EmpEnd_q4 | 2.46 | 3.271 | 4.25 | 6.22 | 56.02 | 3.04 | 3.60 | 2.69 | 3.09 |
| H9_FJSEmpEnd_rate_avg | 2.64 | 3.620 | 4.91 | 7.14 | 65.84 | 3.31 | 4.12 | 2.85 | 3.35 |
| H14_avgFJS_over_sumEmpTotal4q | 0.57 | 0.765 | 0.99 | 0.88 | 0.85 | 0.72 | 0.87 | 0.63 | 0.72 |
| H10_FJSEmp_pooled_quarter | 0.00 | 0.794 | 5.57 | 3.70 | 6.35 | 0.70 | 2.28 | 0.62 | 0.76 |
| H11_FJEmpTotal_pooled_quarter | 0.00 | 0.735 | 4.44 | 3.50 | 6.29 | 0.68 | 2.15 | 0.71 | 0.65 |
| H12_FJSEmpEnd_pooled_quarter | 0.00 | 1.084 | 6.76 | 137.97 | 2065.02 | 0.94 | 2.68 | 0.66 | 0.91 |
| H13_FJSEmpS_pooled_quarter | 0.00 | 1.149 | 7.25 | 158.99 | 2333.99 | 1.01 | 2.76 | 0.74 | 0.96 |

## Ranked by closeness to paper (log-distance in pooled p50 & mean)

| Rank | Hypothesis | log-distance |
|---:|---|---:|
| 1 | H10_FJSEmp_pooled_quarter | 0.327 |
| 2 | H11_FJEmpTotal_pooled_quarter | 0.388 |
| 3 | H8_avgFJS_over_EmpEnd_q4 | 1.273 |
| 4 | H14_avgFJS_over_sumEmpTotal4q | 1.371 |
| 5 | H3_FJSEmpS_ratio_of_sums | 1.424 |
| 6 | H9_FJSEmpEnd_rate_avg | 1.431 |
| 7 | H1_FJSEmpS_rate_avg | 1.565 |
| 8 | H7_SepEmp_rate_avg | 2.625 |
| 9 | H2_FJSEmpS_rate_sum | 3.510 |
| 10 | H12_FJSEmpEnd_pooled_quarter | 3.727 |
| 11 | H13_FJSEmpS_pooled_quarter | 3.869 |
| 12 | H4_SepBegR_avg | 4.527 |
| 13 | H6_TurnOvrS_avg | 4.843 |
| 14 | H5_HirAEndReplr_avg | 5.537 |

## Conclusion

**Q: Do the QWI built-in rate variables (`SepBegR`, `HirAEndR`, `HirAEndReplr`, `TurnOvrS`) explain the 2.3× gap?**
**A: No.** They are decimal fractions in 0.04–0.08 (i.e. 4–8% per quarter) — over 10× *smaller* than paper's 1.08. Multiplied by 100 they're 4–8, but with SD 0.02–0.05 (paper SD = 9.30). None matches paper's distribution shape. **Conclusively rejected.** H4/H5/H6/H7 are at the bottom of the ranking table.

**However, the investigation surfaced a likely correct answer**: **H14 (`100 × avg(FrmJbLsS over 4 sy-q) / sum(EmpTotal over 4 sy-q)`)** matches paper Table A4's annual means very well:

| Year | Paper mean (A4) | H14 mean |
|---|---:|---:|
| 2019 | 0.73 | 0.79 |
| 2020 | 0.93 | 0.93 |
| 2021 | 0.62 | 0.69 |
| 2023 | 0.69 | 0.77 |

This is mathematically equivalent to dividing the existing pipeline's value by 4 (because `sum(Emp over 4 q) ≈ 4 × Emp_q4_lag` for low-seasonality counties). The implied paper formula: **NNJF per 100 = jobs lost per 100 employee-quarters, ratio-of-sums style** — i.e., denominator is total employee-quarters across the school year, not Q4-lag employment alone.

**H10/H11 (pooled-quarter) also produce p50≈0.79 and mean≈3.5**, somewhat closer to Table A2's 1.08/3.32 pair than H14 — but their distribution shape (p75=4.4–5.6, SD=6.3) is also off. H12 (FJS/EmpEnd pooled) hits Table A2's p50 of 1.08 exactly but only by coincidence; its mean and SD are wildly off due to extreme rates from low-EmpEnd counties.

**Paper internal inconsistency**: Table A2 says pooled mean=3.32 and median=1.08. Table A4 says EVERY YEAR's mean is in 0.61–0.93. A 24-year pooled mean cannot be 3.32 if every annual mean is <1. Table A4's year-by-year values are mathematically credible; Table A2's pooled stats are not. (Table A8's state-level pandemic medians of 6.6–16.6 are yet another regime, likely a different aggregation or denominator entirely.)

**Recommended fix for the replication**: switch the existing pipeline from `100 × avg(FrmJbLsS) / Emp_q4_lag` to `100 × avg(FrmJbLsS) / sum(EmpTotal over 4 sy-quarters)` (i.e. H14). This closes the gap with Table A4 to within 10–15% per year and is the most defensible interpretation of "jobs lost per 100 employees" in a school-year-aggregated rate.
