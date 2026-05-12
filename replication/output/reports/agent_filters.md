# Agent Investigation: Sample Restrictions / Outlier Filters / County Filters on NNJF

**Question:** Can a sample-restriction or outlier filter rule (analogous to Footnote 2's
33% turnover rule, or a small-county/cap/balanced-panel rule) bring our NNJF/100
distribution into line with Bleiberg & Nguyen's reported values?

**Short answer: No.** Across 10 filter variants the year-2019 median moves from 2.48 down at
best to 2.16 (cap NNJF/100 > 3) — still far from the paper's 0.43. The gap is
*structural in the construction*, not in the sample.

## Targets

| Quantity | Paper | Mine (baseline) | Ratio |
|---|---|---|---|
| N(2001-2021) | 47,884 | 50,657 | 1.06x |
| N(2020-2024) | 11,722 | 11,878 | 1.01x |
| N(2013-2024) | 24,001 | 29,003 | 1.21x |
| Pooled (1/emp) w-median NNJF/100 | 1.080 | 2.958 | 2.74x |
| Pooled (1/emp) w-mean | 3.32 | 5.30 (w) / 2.96 (unweighted) | 1.60x / 0.89x |
| NNJF/100 SD | 9.30 | 10.91 (unweighted) | 1.17x |
| Median 2019 / 2020 / 2021 / 2023 | 0.43 / 0.51 / 0.31 / 0.40 | 2.48 / 3.02 / 2.24 / 2.44 | ~5.5x |

## Hypotheses tested

| # | Filter rule | N(2001-21) | N(2013-24) | w-med pooled | 2019 / 2020 / 2021 / 2023 |
|---|---|---|---|---|---|
| 0 | Baseline (no filter) | 50,657 | 29,003 | 2.96 | 2.48 / 3.02 / 2.24 / 2.44 |
| 1 | 33% outlier rule on NNJF (county-mean) | 39,369 | 22,276 | 3.00 | 2.55 / 2.92 / 2.48 / 2.53 |
| 2a | emp_lag >= 100 | 50,227 | 28,794 | 2.89 | 2.48 / 3.01 / 2.24 / 2.44 |
| 2b | emp_lag >= 200 | 48,253 | 27,614 | 2.80 | 2.45 / 3.00 / 2.22 / 2.41 |
| 2c | emp_lag >= 500 | 37,903 | 21,635 | 2.59 | 2.34 / 2.94 / 2.15 / 2.30 |
| 2d | emp_lag >= 1000 | 26,120 | 14,855 | 2.45 | 2.22 / 2.91 / 2.05 / 2.18 |
| 3a | Cap NNJF/100 <= 10 | 50,290 | 28,847 | 2.94 | 2.48 / 3.00 / 2.24 / 2.43 |
| 3b | Cap NNJF/100 <= 5 | 48,817 | 28,206 | 2.84 | 2.46 / 2.97 / 2.22 / 2.41 |
| 3c | Cap NNJF/100 <= 3 | 33,884 | 19,817 | 2.27 | 2.16 / 2.53 / 2.05 / 2.11 |
| 4 | Drop SYs with any NaN in 4 quarters | 50,657 | 29,003 | 2.96 | 2.48 / 3.02 / 2.24 / 2.44 |
| 5 | Balanced panel (all 24 yrs, 1,775 counties) | 37,275 | 21,300 | 2.96 | 2.48 / 3.04 / 2.20 / 2.41 |
| 6 | Rate denom = EmpS (stable emp) Q4-lag | 50,656 | 29,002 | 3.59 | 2.89 / 3.54 / 2.61 / 2.86 |
| 7 | 33%-rule + emp_lag >= 100 | 39,136 | 22,172 | 2.95 | 2.54 / 2.91 / 2.48 / 2.53 |
| 8 | Drop high-churn counties (FrmJbLs/FrmJbGn > 1.5) | 50,066 | 28,707 | 2.96 | 2.49 / 3.02 / 2.25 / 2.44 |
| 9 | Drop SYs with 2+ zero quarters | 35,514 | 20,866 | 2.91 | 2.39 / 3.03 / 2.20 / 2.38 |
| 10 | 33% rule using 2013+ county-mean | 46,624 | 23,529 | 2.98 | 2.49 / 2.87 / 2.44 / 2.49 |

## Reading the table

- **N alignment.** H10 (33% rule using only 2013+ county-mean as the reference)
  hits the paper's 2013-2024 N nearly on the nose: **23,529 vs paper 24,001** (within
  2%). It also drops N(2001-21) to 46,624 (paper 47,884, within 3%). This is the only
  filter that closes both N gaps simultaneously.
- **Per-100 alignment.** No filter closes the rate gap. The most aggressive (cap
  NNJF/100 <= 3) shaves the year medians only ~10-15%, while paper medians are
  ~5-6x lower. Even *normalizing by EmpS_lag* (H6) moves the rate up, not down.
- **Outlier rule on NNJF (H1).** Drops 22% of obs but barely changes the rate
  distribution — confirms outliers are not driving the gap. Median actually rises
  slightly (3.00 vs 2.96 baseline) because the rule preferentially drops county-years
  with anomalously LOW (or high) values around stable means.
- **Balanced panel (H5).** Drops to 1,775 of ~3,140 counties but rate distribution
  is unchanged. Selection on stability is not the answer.
- **Small denominators (H2).** Bigger emp_lag thresholds do lower medians, but
  monotonically and slowly: emp_lag >= 1000 still gives median 2.45 vs paper 1.08.

## Why filters can't close this gap

Distribution shape (current construction, all county-years):

| | p5 | p10 | p25 | p50 | p75 | p90 | p95 |
|---|---|---|---|---|---|---|---|
| Mine | 1.31 | 1.55 | 1.99 | 2.55 | 3.23 | 4.01 | 4.63 |
| Paper (inferred from median/mean/SD) | ~0 | ~0 | <0.5 | 1.08 | ~3 | ~7 | ~15 |

My NNJF/100 is roughly log-normally tight around ~2.5. The paper's distribution is
heavily right-skewed (mean 3.32, median 1.08, SD 9.30) — most counties have small or
near-zero NNJF rates with a long tail. Only ~1.9% of my observations are below 1.0;
paper has roughly half below 1.08. **No sample filter can convert a distribution
concentrated in the 1.5-4.5 range into one concentrated near zero.**

This is consistent with the construction issue we already suspected: paper's NNJF
appears to be ~2.5x smaller per typical county than what `avg(FrmJbLsS over 4 SY
quarters)` produces, while totals are correct. Likely candidates (outside this
agent's filter mandate):

1. NNJF is `sum(FrmJbLsS)` / `sum(emp across 4 quarters)` rather than
   `avg(FrmJbLsS) / emp_q4_lag` — that scales the denominator ~4x (employment is
   seasonal, so the sum is ~3.5-4x emp_q4) and would bring medians from ~2.5 down to
   ~0.7, plus push lots of mass toward zero.
2. NNJF only counts true firm closings (`emp_q -> 0`) rather than `FrmJbLsS`. The
   QWI flag `FrmJbLs` minus `FrmJbLsS` is closer in scale.
3. Paper uses a different industry slice (e.g., NAICS 6111 *and* sector S = "Local
   Government", which the public QWI API may not expose at county level).

## Recommended filter (the only useful one found)

**H10: apply the 33% outlier rule to NNJF using the 2013+ county-mean as the
reference** lands within 2-3% of paper N for all three regression samples
(46,624 / 8,913 / 23,529 vs paper 47,884 / 11,722 / 24,001 — note 2020-24 still 24%
low; this filter overshoots that window). It does NOT close the per-100 rate gap.

The 2013-2024 N gap (mine 29,003 -> paper 24,001) is mostly closed by H1 (22,276),
H5 (21,300), or H10 (23,529). H10 is the cleanest because it's analogous to the
documented Footnote 2 rule.

## Conclusion

The per-100 rate gap of ~3x is **not solvable by sample filters**. Filters can
modestly trim the right tail but cannot shift the central tendency of the
distribution from ~2.5 to ~1.0. The discrepancy is in the NNJF *construction*
(numerator/denominator definition), not in the *sample* of county-years. Diagnostic
evidence: my SD (10.9) and unweighted mean (2.96) are close to paper's (9.30, 3.32),
but my median (2.55) is ~2.4x too high — paper's distribution is much more
right-skewed, with a large mass of small/near-zero values absent from our build.

The only filter worth keeping for downstream regression-sample alignment is the
33%-outlier-rule-on-NNJF analog of Footnote 2; using the 2013+ county-mean variant
(H10) lands closest to paper N. This should be combined with a fresh look at NNJF
*construction* (denominator = sum of employment across the four school-year
quarters, not Q4-lag) — outside this agent's scope.

## Files

- Code: `code/94_agent_filters.py`
- Results CSV: `output/reports/agent_filters_results.csv`
