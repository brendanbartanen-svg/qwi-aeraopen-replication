# NNJF Per-100 Denominator Investigation

**Date:** 2026-05-11
**Question:** Why is replicated NNJF/100 ~2.3× (pooled) to 6.5× (median) larger than Bleiberg & Nguyen (2026) Tables A2/A4?

## TL;DR

1. **Major progress on the numerator, not the denominator.** Switching the NNJF count from `avg(FrmJbLsS)` to `avg(max(FrmJbLsS - FrmJbGnS, 0))` — the **net-negative** firm job flow — makes our NNJF *totals* match the paper's Table A4 totals **almost exactly** (e.g. 2019: 174K vs paper 176K; 2023: 162K vs paper 162K). Our previous numerator was inflating totals by 1.1-1.3×.
2. **Combined with denominator = `4 × EmpTotal_q4_lag`** (i.e., dividing the per-100 by 4), this closes the gap from **6.5× to ~1.6×** across every year — a constant residual that no single denominator choice eliminated.
3. **No hypothesis fully closes the 6.5× gap.** The remaining ~1.6× residual is suspiciously uniform across years, suggesting an *additional* unidentified normalization step (possibly aggregation level, an unreported scaling, or a definitional choice that affects all observations equally).
4. **There is internal inconsistency in the paper.** Pooled mean in Table A2 (3.32) is roughly the *cross-year average* of Table A4 means (~0.74) × 4.5, and Table A8 state-level means (~10–20) sit on yet another scale. The "Per 100" label appears to be used inconsistently across tables.

## Hypotheses tested

| # | Description | Pool med | Pool mean | 2019 med | 2020 med | Closeness |
|---|---|---:|---:|---:|---:|---:|
| PAPER | Target | 1.080 | 3.32 | 0.43 | 0.51 | – |
| H5c | **`100 × avg(max(FrmJbLsS−FrmJbGnS,0)) / (4 × EmpTotal_q4_lag)`** | **0.701** | 1.33 | 0.660 | 0.738 | **0.47** |
| H2 | `100 × avg(FrmJbLsS) / sum(EmpTotal over 4q)` = BASELINE÷4 | 0.761 | 0.88 | 0.711 | 0.855 | 0.53 |
| H7 | `100 × avg(FrmJbLsS over Q3,Q4,Q1) / EmpTotal_q4_lag` (drop Q2) | 1.036 | 4.41 | 1.026 | 2.056 | 0.96 |
| H11 | median across 4 per-quarter `FrmJbLsS/EmpS` rates | 1.647 | 2.17 | 1.552 | 2.928 | 1.28 |
| H5 | `100 × avg(max(FrmJbLsS−FrmJbGnS,0)) / EmpTotal_q4_lag` | 2.802 | 5.33 | 2.641 | 2.950 | 1.68 |
| H6 | state-aggregated `sum(NNJF)/sum(emp)` assigned to county | 2.627 | 2.67 | 2.481 | 3.144 | 1.69 |
| H5b | `100 × sum(max(FrmJbLsS−FrmJbGnS,0)) / sum(EmpTotal)` | 2.868 | 3.32 | 2.676 | 3.102 | 1.70 |
| BASE | `100 × avg(FrmJbLsS) / EmpTotal_q4_lag` (current) | 2.985 | 5.55 | 2.786 | 3.271 | 1.76 |
| H1 | `100 × sum(FrmJbLsS) / sum(EmpTotal over 4q)` | 3.046 | 3.52 | 2.843 | 3.420 | 1.78 |
| H3 | mean of 4 per-quarter `FrmJbLsS/EmpTotal` rates | 3.039 | 3.40 | 2.835 | 3.489 | 1.78 |
| H9 | `100 × avg(FrmJbLsS) / avg(EmpS)` | 3.677 | 7.16 | 3.371 | 4.118 | 1.95 |
| H8 | `100 × FrmJbLsS_Q2 / EmpTotal_q4_lag` (Q2 only) | 8.163 | 9.00 | 7.407 | 6.075 | 2.61 |

*Closeness = mean |log(ratio)| across pooled median + 4 year medians (2019, 2020, 2021, 2023).*

## Key findings

### Finding 1 — The numerator should be `max(FrmJbLsS − FrmJbGnS, 0)`, not `FrmJbLsS`

Paper Eq. 2 says `NNJF = abs(emp_{q+1} − emp_q)`, but read carefully: it's a **net-negative** flow. The actual analogue in QWI is `max(FrmJbLsS − FrmJbGnS, 0)` per quarter — i.e., quarters where stable-employment losses exceed gains. NNJF totals using this definition:

| Year | Replication (H5 num.) | Paper A4 | Ratio |
|------|----:|----:|----:|
| 2019 | 174.2K | 176.2K | 0.99 |
| 2020 | 252.7K | 224.9K | 1.12 |
| 2021 | 146.5K | 150.4K | 0.97 |
| 2023 | 161.9K | 162.1K | 1.00 |

This is a near-perfect match to the paper's totals and supersedes the previous "avg(FrmJbLsS)" choice. **Recommend updating `code/10_construct_measures.py` to use the net-negative numerator.**

### Finding 2 — Denominator must be scaled ≈ 4× larger than EmpTotal_q4_lag

The implied denominator that would make the paper's medians work, given the median NNJF count of ~26 in 2019, is ~6,000 (vs our 1,046 = median `EmpTotal_q4_lag`). That's roughly 6× a single quarter's employment. The closest tractable scaling we found is the **sum of EmpTotal across 4 school-year quarters** (~4× single-quarter), giving median rate 0.70 — about 1.6× the paper's 0.43.

### Finding 3 — Constant ~1.6× residual is uniform across years

With H5c (best hypothesis), the year-by-year ratio to paper sits in **1.45–1.88** with mean 1.63 and almost no temporal pattern. That's the signature of a multiplicative constant we haven't found — not an analytical mismatch. Possible explanations:

- The paper might be computing rates at quarter-level (`FrmJbLsS_q / EmpTotal_q` summed/averaged differently with extra `/2`-style filtering).
- The paper may divide by a factor of "annualized employee-quarters" with weights we haven't replicated.
- The paper may filter the numerator to specific subgroup quarters (e.g., only summer quarters Q3/Q4) — but the year-by-year shape doesn't strongly suggest seasonal filtering.

### Finding 4 — Paper has internal inconsistencies that bound how cleanly any single denominator can fit

- Table A4 pooled mean ≈ 0.74 (averaging the 24 yearly means)
- Table A2 pooled mean = **3.32**
- Table A8 (state-pandemic) means ≈ 8–20

These can't all be the same statistic. Table A8's "NNJF mean" looks like a 5-year-summed rate (consistent with our baseline scale). Table A4 is on a fundamentally different (5-7× smaller) scale.

## Conclusion / Recommendation

- **Adopt H5c** as the new replication formula:
  ```
  NNJF = avg(max(FrmJbLsS - FrmJbGnS, 0)) over 4 school-year quarters
  NNJF/100 = 100 × NNJF / (4 × EmpTotal_q4_lag)
  ```
  This matches paper's NNJF *totals* to 0.97–1.12× and shrinks the per-100 gap from 6.5× to ~1.6× (uniform residual).
- **Document the residual** ~1.6× gap as unresolved; flag the internal inconsistency between Tables A2, A4, A8 of the published paper.
- Future work: it would be worth contacting the authors. Given the consistency of the residual, the most likely remaining issues are (a) an undisclosed scaling step in the paper's per-100 construction, or (b) the published Table A4 medians use a different definition than Table A2.

## Files

- Code: `code/91_agent_denominator.py`
- Results CSV: `output/tables/agent_denominator_results.csv`
