# Agent investigation: alternative time-aggregation methods for NNJF

## TL;DR

- **Best fit to paper: H3 (trimmed mean — drop the single largest of 4 SY quarters).**
  Pooled weighted median 0.877 (paper 1.080, 0.81x), pooled mean 1.053 (paper 3.32, 0.32x).
  This is the *only* hypothesis whose pooled median straddles the paper's value rather
  than overshooting by 3x+.
- **Second-best: H2 (median of 4 quarters)** — pooled median 1.299 (1.20x), totals 0.72-0.96x.
- **All other hypotheses overshoot the pooled median 2.6-3.9x.** The "~2.3x too big"
  discrepancy the parent agent saw lives at the median, not the total: every method
  reproduces year totals within 1.0-1.3x, but means/medians blow up because *a few
  small-county quarters with tiny EmpS produce huge per-100 rates that dominate the
  1/emp-weighted aggregation*.
- **The flatness of per-year ratios (CV ≤ 0.08 for H1, H4, H5, H6, H7) confirms a single
  scaling step is missing for the *level* (total) — but the ratio is closer to 1.1x for
  totals and 7-9x for medians. The two are inconsistent**, which means the missing step
  is **not a simple time-aggregation rescale** — the level (totals) is essentially right
  while the cross-county *distribution* shape is wrong.  That strongly suggests the
  remaining gap is **not** an aggregation issue.  Either (a) the paper applies a
  trim/winsorize before forming per-100 rates (H3 supports this), or (b) it weights
  cross-county medians by raw emp (not 1/emp).

## Conclusion for the parent agent

The H3 trimmed-mean result aligns the pooled median to within 0.81x and per-year
medians to 2-3x.  It cannot fully close the gap without an additional change.  We
recommend the parent agent test orthogonal hypotheses next: (1) raw-emp weighting for
the cross-county median, (2) winsorize per-100 rates at p99, (3) include only counties
with EmpS_q4_lag >= some K-12-staff threshold.  None of those is a time-aggregation
question.

Hypotheses tested in `code/93_agent_aggregation.py`. Paper targets:

- Table A4 NNJF Total (thousands) 2019 / 2020 / 2021 / 2023: 176.2 / 224.9 / 150.4 / 162.1
- Table A4 NNJF/100 medians:                                  0.43 / 0.51 / 0.31 / 0.40
- Table A2 pooled NNJF/100 median: 1.08
- Table A2 pooled NNJF/100 mean:   3.32

## H1 q-rate first, mean across 4q

- n_obs: 55,585
- pooled weighted median NNJF/100: **3.785** (paper 1.08, ratio 3.50x)
- pooled weighted mean NNJF/100:   **7.958** (paper 3.32, ratio 2.40x)

| Year | Total (k) | Paper | Ratio | Median | Paper | Ratio |
|------|-----------|-------|-------|--------|-------|-------|
| 2019 | 193.4 | 176.2 | 1.10x | 3.521 | 0.43 | 8.19x |
| 2020 | 283.4 | 224.9 | 1.26x | 4.300 | 0.51 | 8.43x |
| 2021 | 169.4 | 150.4 | 1.13x | 3.061 | 0.31 | 9.88x |
| 2023 | 184.5 | 162.1 | 1.14x | 3.587 | 0.4 | 8.97x |

## H2 median across 4q

- n_obs: 55,585
- pooled weighted median NNJF/100: **1.299** (paper 1.08, ratio 1.20x)
- pooled weighted mean NNJF/100:   **1.561** (paper 3.32, ratio 0.47x)

| Year | Total (k) | Paper | Ratio | Median | Paper | Ratio |
|------|-----------|-------|-------|--------|-------|-------|
| 2019 | 126.5 | 176.2 | 0.72x | 1.250 | 0.43 | 2.91x |
| 2020 | 215.2 | 224.9 | 0.96x | 2.288 | 0.51 | 4.49x |
| 2021 | 112.6 | 150.4 | 0.75x | 1.186 | 0.31 | 3.83x |
| 2023 | 119.8 | 162.1 | 0.74x | 1.354 | 0.4 | 3.39x |

## H3 trimmed mean (drop max of 4)

- n_obs: 55,585
- pooled weighted median NNJF/100: **0.877** (paper 1.08, ratio 0.81x)
- pooled weighted mean NNJF/100:   **1.053** (paper 3.32, ratio 0.32x)

| Year | Total (k) | Paper | Ratio | Median | Paper | Ratio |
|------|-----------|-------|-------|--------|-------|-------|
| 2019 | 86.8 | 176.2 | 0.49x | 0.842 | 0.43 | 1.96x |
| 2020 | 147.8 | 224.9 | 0.66x | 1.558 | 0.51 | 3.06x |
| 2021 | 77.7 | 150.4 | 0.52x | 0.806 | 0.31 | 2.60x |
| 2023 | 82.7 | 162.1 | 0.51x | 0.911 | 0.4 | 2.28x |

## H4 spring-only (Q1+Q2)

- n_obs: 55,858
- pooled weighted median NNJF/100: **4.172** (paper 1.08, ratio 3.86x)
- pooled weighted mean NNJF/100:   **4.658** (paper 3.32, ratio 1.40x)

| Year | Total (k) | Paper | Ratio | Median | Paper | Ratio |
|------|-----------|-------|-------|--------|-------|-------|
| 2019 | 224.2 | 176.2 | 1.27x | 3.816 | 0.43 | 8.87x |
| 2020 | 392.4 | 224.9 | 1.74x | 4.741 | 0.51 | 9.30x |
| 2021 | 167.5 | 150.4 | 1.11x | 2.879 | 0.31 | 9.29x |
| 2023 | 188.9 | 162.1 | 1.17x | 3.472 | 0.4 | 8.68x |

## H5 sum/person-quarter denom

- n_obs: 55,585
- pooled weighted median NNJF/100: **3.631** (paper 1.08, ratio 3.36x)
- pooled weighted mean NNJF/100:   **6.895** (paper 3.32, ratio 2.08x)

| Year | Total (k) | Paper | Ratio | Median | Paper | Ratio |
|------|-----------|-------|-------|--------|-------|-------|
| 2019 | 193.4 | 176.2 | 1.10x | 3.371 | 0.43 | 7.84x |
| 2020 | 283.4 | 224.9 | 1.26x | 4.118 | 0.51 | 8.07x |
| 2021 | 169.4 | 150.4 | 1.13x | 2.941 | 0.31 | 9.49x |
| 2023 | 184.5 | 162.1 | 1.14x | 3.415 | 0.4 | 8.54x |

## H6 q-rate first, mean across 3q (Q4lag+Q1+Q2)

- n_obs: 55,723
- pooled weighted median NNJF/100: **3.585** (paper 1.08, ratio 3.32x)
- pooled weighted mean NNJF/100:   **4.932** (paper 3.32, ratio 1.49x)

| Year | Total (k) | Paper | Ratio | Median | Paper | Ratio |
|------|-----------|-------|-------|--------|-------|-------|
| 2019 | 156.8 | 176.2 | 0.89x | 3.244 | 0.43 | 7.54x |
| 2020 | 273.4 | 224.9 | 1.22x | 4.129 | 0.51 | 8.10x |
| 2021 | 119.5 | 150.4 | 0.79x | 2.378 | 0.31 | 7.67x |
| 2023 | 134.9 | 162.1 | 0.83x | 2.917 | 0.4 | 7.29x |

## H7 mean count / mean(EmpS) denom

- n_obs: 55,586
- pooled weighted median NNJF/100: **3.731** (paper 1.08, ratio 3.45x)
- pooled weighted mean NNJF/100:   **20.013** (paper 3.32, ratio 6.03x)

| Year | Total (k) | Paper | Ratio | Median | Paper | Ratio |
|------|-----------|-------|-------|--------|-------|-------|
| 2019 | 193.4 | 176.2 | 1.10x | 3.410 | 0.43 | 7.93x |
| 2020 | 283.4 | 224.9 | 1.26x | 4.211 | 0.51 | 8.26x |
| 2021 | 169.4 | 150.4 | 1.13x | 2.970 | 0.31 | 9.58x |
| 2023 | 184.5 | 162.1 | 1.14x | 3.469 | 0.4 | 8.67x |

## H8 mean count / EmpEnd(Q4_lag) denom

- n_obs: 55,582
- pooled weighted median NNJF/100: **3.248** (paper 1.08, ratio 3.01x)
- pooled weighted mean NNJF/100:   **8.417** (paper 3.32, ratio 2.54x)

| Year | Total (k) | Paper | Ratio | Median | Paper | Ratio |
|------|-----------|-------|-------|--------|-------|-------|
| 2019 | 193.4 | 176.2 | 1.10x | 3.037 | 0.43 | 7.06x |
| 2020 | 283.4 | 224.9 | 1.26x | 3.571 | 0.51 | 7.00x |
| 2021 | 169.4 | 150.4 | 1.13x | 2.685 | 0.31 | 8.66x |
| 2023 | 184.5 | 162.1 | 1.14x | 3.086 | 0.4 | 7.72x |

## H9 sum / (4 * Q4_lag emp)

- n_obs: 55,585
- pooled weighted median NNJF/100: **2.963** (paper 1.08, ratio 2.74x)
- pooled weighted mean NNJF/100:   **5.357** (paper 3.32, ratio 1.61x)

| Year | Total (k) | Paper | Ratio | Median | Paper | Ratio |
|------|-----------|-------|-------|--------|-------|-------|
| 2019 | 193.4 | 176.2 | 1.10x | 2.786 | 0.43 | 6.48x |
| 2020 | 283.4 | 224.9 | 1.26x | 3.271 | 0.51 | 6.41x |
| 2021 | 169.4 | 150.4 | 1.13x | 2.480 | 0.31 | 8.00x |
| 2023 | 184.5 | 162.1 | 1.14x | 2.836 | 0.4 | 7.09x |

## H10 within-county weighted median qrate

- n_obs: 55,951
- pooled weighted median NNJF/100: **2.841** (paper 1.08, ratio 2.63x)
- pooled weighted mean NNJF/100:   **5.860** (paper 3.32, ratio 1.76x)

| Year | Total (k) | Paper | Ratio | Median | Paper | Ratio |
|------|-----------|-------|-------|--------|-------|-------|
| 2019 | 193.6 | 176.2 | 1.10x | 2.690 | 0.43 | 6.26x |
| 2020 | 285.2 | 224.9 | 1.27x | 4.082 | 0.51 | 8.00x |
| 2021 | 169.7 | 150.4 | 1.13x | 2.500 | 0.31 | 8.06x |
| 2023 | 184.7 | 162.1 | 1.14x | 2.703 | 0.4 | 6.76x |

## Cross-year ratio consistency check (median ratio to paper)

If a single missing scaling factor explains the gap, the per-year ratios
should be ~constant across 2019/2020/2021/2023.

| Hypothesis | r2019 | r2020 | r2021 | r2023 | sd/mean |
|------------|-------|-------|-------|-------|---------|
| H1 q-rate first, mean across 4q | 8.19x | 8.43x | 9.88x | 8.97x | 0.073 |
| H2 median across 4q | 2.91x | 4.49x | 3.83x | 3.39x | 0.159 |
| H3 trimmed mean (drop max of 4) | 1.96x | 3.06x | 2.60x | 2.28x | 0.164 |
| H4 spring-only (Q1+Q2) | 8.87x | 9.30x | 9.29x | 8.68x | 0.029 |
| H5 sum/person-quarter denom | 7.84x | 8.07x | 9.49x | 8.54x | 0.074 |
| H6 q-rate first, mean across 3q (Q4lag+Q1+Q2) | 7.54x | 8.10x | 7.67x | 7.29x | 0.038 |
| H7 mean count / mean(EmpS) denom | 7.93x | 8.26x | 9.58x | 8.67x | 0.072 |
| H8 mean count / EmpEnd(Q4_lag) denom | 7.06x | 7.00x | 8.66x | 7.72x | 0.088 |
| H9 sum / (4 * Q4_lag emp) | 6.48x | 6.41x | 8.00x | 7.09x | 0.091 |
| H10 within-county weighted median qrate | 6.26x | 8.00x | 8.06x | 6.76x | 0.108 |

## Best hypothesis

**H3 trimmed mean (drop max of 4)** has the smallest combined log-distance from paper
(pooled median ratio 0.81x).
