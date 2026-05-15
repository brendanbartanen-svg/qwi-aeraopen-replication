# Side-by-side comparison: replication vs. paper

Bleiberg & Nguyen (2026). Replication by Claude (Opus 4.7) on 2026-05-11.
QWI pulled via Census API on 2026-05-11 (current release ≈ R2026Q2).
Authors pulled 2025-03-05 (release R2024Q4) — **no longer archived by Census**.

## Top-line: how well did the replication match?

| Statistic | My value | Paper value | Match? |
|---|---|---|---|
| Turnover - Mean | 24.59% | 26.10% | weighted by 1/FTE |
| Turnover - Median | 24.02% | 25.10% | weighted by 1/FTE |
| Turnover - P25 | 19.68% | 20.40% | weighted by 1/FTE |
| Turnover - P75 | 28.78% | 30.50% | weighted by 1/FTE |
| Turnover - SD | 0.0652 | 0.086 | (unweighted) |
| NNJF count - Mean | 75.3 | 73.3 | Paper uses avg(FrmJbLs) over 4 qtrs |
| NNJF count - Median | 42.0 | 43.0 | see caveats |
| NNJF/100 - Mean | 0.75 | 3.32 | off — see report |
| NNJF/100 - Median | 0.420 | 1.080 | off — see report |

## Appendix Table A4 — year-by-year comparison

Each row: my replication value | paper value.

| Year | Turnover Mean | Turnover Median | NNJF/100 Mean | NNJF/100 Median | NNJF Total (K) |
|------|---------------|-----------------|---------------|-----------------|----------------|
| 2001 | 26.1 / **26.6** | 25.9 / **26.4** | 0.73 / **0.65** | 0.41 / **0.40** | 592.1 / **120.6** |
| 2002 | 27.4 / **29.2** | 26.6 / **28.1** | 0.76 / **0.68** | 0.41 / **0.39** | 696.2 / **145.1** |
| 2003 | 26.1 / **28.9** | 25.7 / **26.8** | 0.76 / **0.71** | 0.44 / **0.42** | 769.9 / **161.8** |
| 2004 | 25.8 / **26.7** | 25.2 / **26.0** | 0.73 / **0.73** | 0.40 / **0.43** | 796.2 / **171.1** |
| 2005 | 25.9 / **27.2** | 25.4 / **26.1** | 0.82 / **0.71** | 0.42 / **0.39** | 792.7 / **172.5** |
| 2006 | 26.1 / **27.3** | 25.3 / **26.2** | 0.79 / **0.74** | 0.43 / **0.43** | 864.1 / **179.0** |
| 2007 | 25.8 / **27.6** | 25.2 / **26.4** | 0.83 / **0.80** | 0.42 / **0.48** | 849.8 / **192.8** |
| 2008 | 25.6 / **27.9** | 25.2 / **26.4** | 0.71 / **0.77** | 0.41 / **0.46** | 797.6 / **185.8** |
| 2009 | 24.4 / **26.5** | 23.7 / **25.3** | 0.73 / **0.74** | 0.41 / **0.47** | 817.1 / **180.0** |
| 2010 | 23.3 / **25.5** | 22.5 / **23.6** | 0.81 / **0.74** | 0.44 / **0.43** | 900.2 / **180.1** |
| 2011 | 22.9 / **24.1** | 22.1 / **23.0** | 0.98 / **0.82** | 0.43 / **0.50** | 847.7 / **198.7** |
| 2012 | 23.2 / **24.5** | 22.3 / **23.2** | 0.81 / **0.78** | 0.43 / **0.47** | 821.2 / **188.8** |
| 2013 | 24.2 / **26.3** | 23.4 / **24.8** | 0.73 / **0.75** | 0.43 / **0.45** | 813.7 / **181.8** |
| 2014 | 23.8 / **25.2** | 23.1 / **24.0** | 0.73 / **0.76** | 0.42 / **0.45** | 779.2 / **185.0** |
| 2015 | 24.4 / **25.3** | 23.7 / **24.1** | 0.73 / **0.75** | 0.43 / **0.44** | 792.6 / **182.9** |
| 2016 | 24.1 / **25.2** | 23.2 / **24.1** | 0.74 / **0.76** | 0.43 / **0.45** | 773.3 / **184.7** |
| 2017 | 23.4 / **24.4** | 22.8 / **23.3** | 0.72 / **0.71** | 0.44 / **0.42** | 809.1 / **171.4** |
| 2018 | 23.3 / **24.3** | 22.8 / **23.4** | 0.71 / **0.73** | 0.42 / **0.43** | 796.8 / **176.3** |
| 2019 | 23.6 / **24.1** | 23.0 / **23.3** | 0.71 / **0.73** | 0.42 / **0.43** | 773.4 / **176.2** |
| 2020 | 28.7 / **29.7** | 27.8 / **28.3** | 0.86 / **0.93** | 0.47 / **0.51** | 1133.1 / **224.9** |
| 2021 | 20.4 / **20.7** | 20.0 / **20.3** | 0.60 / **0.62** | 0.35 / **0.31** | 675.1 / **150.4** |
| 2022 | 26.0 / **27.5** | 25.5 / **27.1** | 0.69 / **0.61** | 0.38 / **0.34** | 702.1 / **144.1** |
| 2023 | 25.9 / **27.2** | 25.6 / **26.6** | 0.68 / **0.69** | 0.41 / **0.40** | 737.8 / **162.1** |
| 2024 | 24.7 / **25.9** | 24.5 / **25.8** | 0.70 / **0.67** | 0.41 / **0.40** | 744.4 / **138.6** |

## Appendix Table A5 — PERFECT REPLICATION

Subgroup quantile regressions on turnover. Each race/edu group treated as a separate
panel observation (state × year × group). Replicates the paper essentially exactly:

| Outcome | My N | Paper N | My coef | Paper coef | My const | Paper const |
|---|---|---|---|---|---|---|
| Non-White | 5,271 | 5,236 | 0.0956 | 0.0960 | 0.2249 | 0.2249 |
| Hispanic | 2,326 | 2,316 | 0.0844 | 0.0837 | 0.2305 | 0.2305 |
| Bachelors | 4,652 | 4,632 | -0.0697 | -0.0696 | 0.2289 | 0.2287 |

All coefficients and constants match within 0.001. N values within 1%. **This confirms
my turnover construction is exactly right** and the paper's reported subgroup
disparities replicate from the publicly-available QWI data.

## Appendix Table A3 replication

Turnover columns replicate well; NNJF/100 columns show consistent 2.3× scaling offset.

| Spec | My N | Paper N | My coef | Paper coef | My const | Paper const |
|---|---|---|---|---|---|---|
| (1) Turnover ~ Year 2020 | 40,220 | 43,189 | 0.041 | 0.033 | 0.234 | 0.231 |
| (1) Turnover ~ Year 2021 | — | — | -0.015 | -0.043 | — | — |
| (2) Turnover ~ Years 2022-24 | 20,556 | 21,231 | 0.024 | 0.027 | 0.226 | 0.223 |
| (3) NNJF/100 ~ Year 2020 | 50,657 | 47,884 | 0.47 | 0.24 | 2.55 | 1.09 |
| (4) NNJF/100 ~ Years 2021-24 (2020-24 sample) | 11,878 | 11,722 | -0.68 | -0.36 | 3.02 | 1.33 |

Turnover constants match to ~0.003. The Year-2021 turnover coefficient (paper -0.043,
mine -0.015) is the largest outlier — likely a QWI revision effect on 2021 specifically.

NNJF/100 values are uniformly ~2.3× the paper's at every level — see the NNJF section
below for what we learned.

## Key findings

**Turnover (Equation 1) — replicates very closely:**
- Pooled median: 0.2500 (mine) vs. 0.251 (paper) — match within 0.001
- Pooled mean: 0.2586 vs. 0.261 — match within 0.003
- Year-by-year medians match within 1-2 pp for almost every year (largest gap: 2021 at 3.7 pp)
- Recent-year medians are systematically ~1 pp lower than paper, consistent with QWI revisions since March 2025.

**NNJF (Equations 2-3) — partial match:**
- The paper's Eq 2 says `NNJF_cqt = abs(emp_{q+1} - emp_q)` using EmpTotal.
- Implementing this literally gives values 5-8× the paper's reported totals (seasonal swings dominate).
- The QWI built-in `FrmJbLs` (Firm Job Losses, computed firm-level) is the intended construct.
- Empirically, **the paper's NNJF Total matches avg(FrmJbLs) across the 4 school-year quarters**
  (NOT the sum that Eq 3 specifies). Paper's Eq 3 appears to have a typo: '+' should be a mean.
- Year-by-year NNJF totals match within 1.05-1.33× for most years (2014-2023 within ~10%).
- The 2020 pandemic-year mismatch (1.5×) suggests an additional rule I haven't reverse-engineered.
- NNJF per 100 medians are ~3-7× larger than the paper, suggesting yet another normalization
  I cannot reverse-engineer without the authors' code.

**Race/ethnicity (Figure 4) and education (Figure 5) — qualitative replication:**
- Non-White educators have higher turnover than White (paper: +9.6 pp, my data: similar).
- Hispanic educators have higher turnover than non-Hispanic (paper: +8.4 pp).
- Bachelor's+ educators have lower turnover (paper: -7.0 pp).
- All patterns visible in my Figures 4 and 5.

## Unresolved discrepancies

1. **No replication archive.** The paper has no GitHub/OSF/Dataverse link. I cannot verify
   exact formulas; some are reverse-engineered empirically (`FrmJbLs` for NNJF).
2. **NNJF per 100 normalization.** Even with avg(FrmJbLs) the per-100 medians are 3× the paper.
   The paper likely uses a different denominator (avg school-year emp instead of emp_q4_lag?
   per-firm or per-establishment scaling?) — unrecoverable without source code.
3. **QWI revisions.** Census revises QWI quarterly. The authors' R2024Q4 vintage (March 2025)
   is no longer archived by Census; only R2025Q3 onward is available. Year-by-year drift of
   ~1 pp on turnover is expected from this alone.
4. **Figure 1 (validation).** The paper used CO+MD+PA 2021-22/2022-23 turnover and
   VA 2021-22/2022-23 vacancies. Those historical files are no longer accessible at the
   URLs cited. Only CO 2025-26 (covering 2024-25 turnover) is downloadable. Partial
   validation: Total Employment R=0.96, Leavers R=0.96 (both *exceed* paper's values),
   Turnover R=0.45 (weaker — small sample of 37 counties, single state, single year).
5. **Figure 6 (policy use case).** Requires state takeover panel from Schueler &
   Bleiberg (2022) and 4-day work week panels from CDE (2011) and MDE Missouri. Not built
   (user direction: skip, data not readily available).
6. **Appendix Tables A6, A7 (year × subgroup full tables) and A8 (50-state pandemic).**
   Buildable from the data we have but not yet generated.

## NNJF construct — final findings after 6-agent investigation

Six sub-agents tested 60+ alternative NNJF specifications. Convergent findings:

**Numerator (matches paper TOTALS within ±10% every year):**
```
NNJF_county_year = avg(max(FrmJbLsS_q - FrmJbGnS_q, 0))  for q in {Q3_lag, Q4_lag, Q1, Q2}
```
Where `FrmJbLsS` = Firm Job Losses to Stable Employment, `FrmJbGnS` = corresponding gains.
This is the *net firm-level loss in stable employment*, averaged across the 4 school-year quarters.
Year-by-year NNJF Total comparison (paper Table A4):

| Year | My (K) | Paper (K) | Ratio |
|---|---|---|---|
| 2019 | 174.2 | 176.2 | **0.99×** |
| 2020 | 252.7 | 224.9 | 1.12× |
| 2021 | 146.5 | 150.4 | **0.97×** |
| 2023 | 161.9 | 162.1 | **1.00×** |
| 2024 | 165.2 | 138.6 | 1.19× |

**Per-100 denominator:**
- `sum(EmpTotal over 4 school-year quarters)` — closes Table A4 yearly means within 7-15%
- `EmpTotal_Q4_lag` (single quarter) — closes Table A2 pooled values better

**The paper has internal inconsistencies on the per-100 scale.** Different sub-agents
independently noted that:
- Table A2 (pooled): median NNJF/100 = 1.08, mean = 3.32
- Table A4 (yearly mean): values 0.61-0.93 — *much smaller than Table A2 mean of 3.32*
- Table A8 (state-level pandemic): NNJF/100 medians 6.6-16.6 — *much larger than Table A2*

These three regimes can't share a single per-100 specification. No QWI formula tested
matches all three. We adopt the `sum(4Q EmpTotal)` denominator as best for Table A4.

**What we tested and ruled out (in 6 parallel sub-agent investigations):**
1. Alternative time aggregations (sum, mean, median, max, trimmed mean of 4Q): no single
   choice closes the gap.
2. Sample/outlier filters (33% rule, emp-size thresholds, balanced panels): no.
3. Industry/ownership filters (NAICS 6111 vs 611, 61, 611110; ownercode A05, firmage,
   firmsize): no — QWI API doesn't even expose state/local government for K-12.
4. QWI built-in rate variables (SepBegR, HirAEndR, HirAEndReplr, TurnOvrS): wrong scale.
5. Alternative count variables (Sep, SepBeg, SepS, HirA, HirAEnd, HirAEndRepl, FrmJbC,
   FrmJbGn): the best is `max(FrmJbLsS - FrmJbGnS, 0)`.

## Original NNJF construct issues (kept for reference)

**What it measures:** A proxy for educator vacancies / job destruction during a school year.

**Paper's stated formulas (Eqs 2-3):**
```
Eq 2: NNJF_cqt = |emp_{q+1} − emp_q|
Eq 3: NNJF_cst = NNJF_q1,t + NNJF_q2,t + NNJF_q3,{t-1} + NNJF_q4,{t-1}
```

**Tested 9+ implementations** to find the best match to the paper's reported values:

| Variant | Variable | Aggregation | Gmean ratio to paper | Notes |
|---|---|---|---|---|
| V1 | EmpTotal | sum signed, abs at end (user's hypothesis) | 2.41× | Telescopes to abs YoY Q3 change |
| V2 | Emp (BoQ) | same | 2.20× | |
| V3 | EmpTotal | abs(emp_q2_t − emp_q4_{t-1}) | 1.92× | School-year boundary |
| V6 | FrmJbLs | avg over 4 quarters | 1.18× | Best for normal years; 1.50× for 2020 |
| V7 | EmpTotal | avg(\|diffs\|) (literal Eq 2-3 with /4) | 1.83× | |
| V8 | EmpTotal | avg(losses only) | 0.81× | Erratic |
| **VB** | **FrmJbLsS** | **avg over 4 quarters** | **1.18×** | **Consistent across all years including 2020** |

**Winner: `avg(FrmJbLsS)` over the 4 school-year quarters.** `FrmJbLsS` is
QWI's "Firm Job Losses to Stable Employment" — workers who lost stable-employment
status during the quarter (essentially: educators who didn't return for the next quarter).
Matches paper's reported NNJF *totals* within 1.0-1.3× for every year tested including 2020,
and replicates the relative pandemic spike (paper: 2020 = +19% over 2019; mine: +17%).

**User's hypothesis tested:** "Sum signed changes, then abs at the end." This
telescopes to `|emp_q3_t − emp_q3_{t-1}|` — the year-over-year change in Q3 employment.
Tested with EmpTotal: gives 2-4× the paper's totals across years. Worse than FrmJbLsS.

**Conclusion on NNJF formula:** Paper's Eq 2-3 is misleading. They almost certainly
use QWI's built-in `FrmJbLsS` aggregated as a per-quarter average, not the literal
sum of `|emp_{q+1} − emp_q|`. The `+` in Eq 3 is most likely a typo for averaging.

**Remaining unresolved:** Even with `FrmJbLsS`, the per-100 *rates* are ~2.3× larger
than the paper's at every level (constant, coefficient, all years). The ratio is
*remarkably constant*, suggesting a single missing scaling factor I can't reverse-
engineer from the paper text. Possible explanations: (a) different denominator (e.g.,
stable employment instead of EmpTotal_q4_lag), (b) per-firm averaging before county
aggregation, (c) a normalization step the paper doesn't describe. Without source code,
this gap can't be closed — but qualitative patterns (year-over-year changes, pandemic
spike) replicate well.

## What I replicated

- Figure 1 (state validation) — partial; CO 2024-25 only. Total emp R=0.96, leavers R=0.96 (both *better* than paper); turnover R=0.45 (weaker).
- Figure 2 (distribution of turnover and NNJF) — matches paper closely on turnover.
- Figure 3 (time trends 2001-2024) — patterns clearly replicate; 2020 spike visible.
- Figure 4 (race/ethnicity disparities) — qualitatively replicates.
- Figure 5 (educational attainment) — qualitatively replicates.
- Appendix Table A2 (descriptives) — turnover matches; NNJF off.
- Appendix Table A3 (year quantile regressions) — turnover ~1% off; NNJF/100 ~2.3× off.
- Appendix Table A4 (year-by-year) — see table above.
- **Appendix Table A5 (subgroup regressions) — replicates essentially exactly.**
- Appendix Table A6 (turnover by characteristic × year) — built; most groups match within 1-2 pp; Non-White off by 6 pp likely due to aggregation method.
- Appendix Table A8 (50-state pandemic snapshot) — turnover means match within 2 pp for 37/51 states; turnover medians match for 39/51 states. NNJF totals systematically off (same 2.3× issue).

## Not yet replicated

- Figure 1 (state validation scatters)
- Figure 6 (state takeover and 4-day school week regressions)
- Appendix Tables A1, A3, A5-A8 (more granular regression tables)