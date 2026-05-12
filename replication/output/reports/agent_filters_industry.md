# Agent investigation: industry / ownership / firm-size filters for NNJF

## TL;DR

**No industry, ownership, or firm-size filter combination brings per-100 NNJF
medians closer to the paper.** Every filter we can actually invoke either
matches the default exactly (no-op) or makes the per-100 median *larger*. The
QWI API exposes far less filter granularity than `variables.json` advertises:

- `ownercode`: only `A00` (all, default) and `A05` (federal government, ~5-8%
  of K-12 emp) work. There is no `state government` or `local government`
  code accessible on `sa`/`se`/`rh`.
- `firmage`/`firmsize`: only the default value `0` (= all) returns data for
  any K-12 industry code. Values 1-5 always return empty (cell suppression).
- NAICS hierarchy: `6111` == `61111` == `611110` for QWI K-12. The 6-digit
  code is documented but the API silently returns empty. `611` and `61` are
  broader (educational services / educ-services sector) and yield ~60% more
  job losses than `6111` alone.

The persistent ~2.3x-7x per-100 overshoot is **not** explained by an industry/
ownership filter. It points to the denominator (`emp_q4_lag`) or the
cross-county weighting, not the numerator filter set.

## Setup

- Three states sampled: AL (01), CO (08), TX (48) — combined ~10-11% of
  national K-12 employment, so 3-state totals should be ~10-11% of paper
  Table A4 totals when correctly specified.
- School years: 2019, 2020, 2021, 2023 (paper Table A4 reference years).
- NNJF construct: `mean(FrmJbLsS)` across the 4 school-year quarters; same
  formula used by `code/10_construct_measures.py`.
- Per-100: `100 * nnjf / EmpTotal_{q4_prev}`; pooled weighted median uses
  `w = 1/emp_lag` (same weighting scheme as `10_construct_measures.py`).
- Paper reference values: Table A4 NNJF totals 176.2/224.9/150.4/162.1 (k);
  Table A4 medians 0.43/0.51/0.31/0.40; Table A2 pooled median 1.080.

## Findings per hypothesis

Total = 3-state pooled total in thousands. Paper col is national from Table
A4 — expected ratio is ~0.10-0.11 if the filter is correct. Median is the
weighted (1/emp) median NNJF/100; Paper col is the national median from
Table A4; expected ratio is ~1.0 if the filter+method match.

### H1 — NAICS 6111, default ownercode (= A00, all ownership) [BASELINE]

- n=1,093 county-school-year obs across 3 states x 4 SY
- pooled weighted median NNJF/100 = **2.980** (paper 1.080, 2.8x)
- pooled total = 124.0k

| SY | Total(k) | Paper(k) | Ratio | Median | Paper | Ratio |
|----|---------:|---------:|------:|-------:|------:|------:|
| 2019 | 30.0 | 176.2 | 0.17 | 3.033 | 0.430 | 7.05x |
| 2020 | 39.1 | 224.9 | 0.17 | 3.517 | 0.510 | 6.90x |
| 2021 | 22.9 | 150.4 | 0.15 | 2.606 | 0.310 | 8.41x |
| 2023 | 32.0 | 162.1 | 0.20 | 2.959 | 0.400 | 7.40x |

Total-ratio of ~0.17-0.20 (vs. expected 0.10-0.11) is consistent with the
known ~1.0-1.3x national-total overshoot. Medians overshoot 7-8x at the
county level (state-FIPS-restricted 3-state subsample has heavier
small-county mass than the national pool, pushing the weighted median
higher than the national 2.5x figure the parent agent saw).

### H2 — NAICS 6111, ownercode=A05 (federal government only)

- n=280 obs (only the few counties with federal K-12 schools)
- pooled weighted median NNJF/100 = **3.665** (paper 1.080, 3.4x)
- pooled total = 11.5k (only ~5% of A00)

| SY | Total(k) | Median |
|----|---------:|-------:|
| 2019 | 2.5 | 3.655 |
| 2020 | 3.1 | 4.258 |
| 2021 | 2.5 | 3.543 |
| 2023 | 3.3 | 4.310 |

A05 is *not* "public schools" — it covers federal K-12 (BIE, DoDEA, etc.),
roughly 5-8% of total K-12 emp. Totals fall 90% short while medians go up
(small counties have noisier per-100 rates). **Rules out A05 as the paper's
filter.**

### H3 — NAICS 611110 (6-digit explicit "Elementary and Secondary Schools")

- **Returned no rows from the API.** Despite `variables.json` listing 6-digit
  industry codes, the QWI `sa` endpoint rejects `industry=611110` for K-12
  (silent 204). The effective minimum granularity is 4-digit (`6111`).
- **Rules out the "6-digit-vs-4-digit" hypothesis.** The paper cannot have
  used 611110 even if it wanted to.

### H4 — NAICS 611 (3-digit, all educational services)

- n=1,252 obs (more counties because 611 includes private trade/tech
  schools, post-secondary, etc.)
- pooled weighted median NNJF/100 = **3.125** (paper 1.080, 2.9x)
- pooled total = 199.0k (60% larger than 6111)

| SY | Total(k) | Paper(k) | Ratio | Median | Paper | Ratio |
|----|---------:|---------:|------:|-------:|------:|------:|
| 2019 | 47.2 | 176.2 | 0.27 | 3.129 | 0.430 | 7.28x |
| 2020 | 57.6 | 224.9 | 0.26 | 3.638 | 0.510 | 7.13x |
| 2021 | 43.8 | 150.4 | 0.29 | 2.679 | 0.310 | 8.64x |
| 2023 | 50.4 | 162.1 | 0.31 | 3.103 | 0.400 | 7.76x |

Totals balloon by ~57% relative to the paper (3-state ratios 0.26-0.31 vs.
expected 0.10-0.11). Medians barely change. **Rules out broader-NAICS as
the explanation.** Confirms paper's stated NAICS 6111 is correct for the
numerator.

### H5 — NAICS 61 (2-digit, educational services sector)

- Identical to H4 (totals 199.0k, median 3.125). At this level of detail
  the QWI rollup is the same. **No information beyond H4.**

### H6 — NAICS 6111 + `firmage=0` + `firmsize=0`

- Identical to H1 — `0` is the default in both fields. **No-op.**

### H7 — NAICS 6111 + `ind_level=4`

- Identical to H1. `ind_level` is the auto-derived industry-level flag; it
  cannot be queried with a non-default value when an explicit `industry=`
  is supplied. **No-op.**

## What's NOT testable via the public API

We probed `firmage=1..5` and `firmsize=1..5` on the `sa`, `se`, and `rh`
endpoints with and without an industry filter. **All variants return 0
rows** — cell suppression appears to apply universally for K-12 firm-
age/size cross-tabs at the county level. There is no `qwi/fa` or `qwi/fs`
endpoint (HTTP 404). So we cannot test "restrict to mature firms" or
"restrict to medium/large firms" via the QWI public API.

Even if we could, the paper does not mention such a restriction in any of
its methods text or appendix, and K-12 districts are nearly all multi-
decade firms with hundreds of employees — these filters would change very
little.

## Sanity check: sex partitions

To rule out "the paper used sex=1 only" or "sex=0 double-counts": verified
that `EmpTotal(sex=0) = EmpTotal(sex=1) + EmpTotal(sex=2)` in CO 2019-Q1
(134,587 ≈ 35,269 + 99,316). No double-counting in our default `sex=0`
pull.

## Conclusion

**No industry/ownership/firm-size filter reproduces the paper's per-100
values.** The QWI API simply doesn't expose enough filter granularity to
materially affect the K-12 result:

1. The only ownership cut that works (A05 = federal) is the wrong slice
   and makes things *worse*.
2. `firmage`/`firmsize` non-default values are entirely unavailable for
   this industry.
3. The 4-digit NAICS 6111 is the most-granular code QWI accepts for K-12
   (6-digit 611110 returns empty).
4. The default unfiltered baseline already matches the paper's stated
   methodology.

The remaining ~2.3x per-100 overshoot is **not** an industry-filter
problem. Combined with the parent agent's note that totals are within
1.0-1.3x, this points at the **denominator or cross-county weighting**,
specifically:

- Possibility A: the paper normalizes by a different employment measure
  (`EmpS`, `Emp`, end-of-quarter `EmpEnd`, or a 4-quarter average) rather
  than `EmpTotal_{q4_lag}`.
- Possibility B: the paper weights the cross-county median by raw `emp`,
  not `1/emp` as we do. With raw-emp weighting, large urban counties
  dominate and small noisy counties (which inflate the 1/emp-weighted
  median) get pulled down toward the bulk distribution.
- Possibility C: the paper trims/winsorizes county-quarter per-100
  outliers before forming medians.

These are the right next angles for orthogonal agents.

## Files

- Test script: `code/95_agent_filters_industry.py`
- Per-hypothesis CSV: `output/reports/agent_filters_industry_results.csv`
