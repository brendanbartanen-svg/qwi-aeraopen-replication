# Replication Feasibility Report

**Paper:** Bleiberg, J. & Nguyen, T. D. (2026). Leveraging Quarterly Workforce Indicators to Analyze K–12 Education Labor Market Dynamics: Inequitable Trends in Turnover. *AERA Open*, 12(1), 1–18. [DOI: 10.1177/23328584261443298](https://doi.org/10.1177/23328584261443298)

**Date:** 2026-05-11
**Prepared by:** Claude (Opus 4.7, 1M ctx)
**Working directory:** `/Users/yvp3tf/Documents/CC Sandbox/replication/qwi_aeraopen/`

---

## 1. TL;DR

- **Feasibility:** **HIGH.** All data are public; the paper is fully methodological; the appendix provides exact target values for validation.
- **Biggest gap:** **No replication archive, no GitHub repo, no data availability statement.** Authors share no code. Everything must be reconstructed from the paper text.
- **Effort estimate:** Moderate. ~1–3 days of programming to pull QWI via API, build equations 1–3, merge CCD weights, pull state validation data, and produce all 6 figures + 8 appendix tables.
- **Confidence in replication accuracy:** **Cannot be exact** because (a) QWI is re-revised quarterly and our pull will differ slightly from the authors' March 5, 2025 pull; (b) a few methodological choices in the paper are ambiguous (see §5). But we should match within 1–2 percentage points on most targets.

---

## 2. Paper at a glance

The paper does two things:
1. **Methodology:** Demonstrates how to transform quarter-level QWI data (Census Bureau) into school-year, county-level measures of *educator turnover* and *net-negative job flow* (a proxy for vacancies). Validates against state administrative data.
2. **Descriptive analysis:** Describes how those measures vary over time, geography, race/ethnicity, and educational attainment, with a focus on the COVID pandemic. A use-case section shows the measures correlate with state takeover and 4-day school week policies.

The output is **6 main figures + 8 appendix tables**. There is no causal claim; everything is descriptive (the only regression with policy variables is Figure 6, with state and year fixed effects and FTE weights).

---

## 3. Data required (all public)

### 3.1 Primary — QWI (Census Bureau)
- **Access:** Free Census API. Requires an API key (registration at https://api.census.gov/data/key_signup.html).
- **Endpoint:** `https://api.census.gov/data/timeseries/qwi/...` — exact path TBD (see issue §5.2).
- **Industry filter:** NAICS **6111** (Elementary and Secondary Schools).
- **Geography:** county (FIPS 5-digit).
- **Time:** 2000 Q1 to 2024 Q2 (school years 2000-01 through 2023-24).
- **Variables (per footnotes 3, 4):**
  - **`hirn`** — newly hired employees
  - **`emptotal`** — flow employment count
  - Optionally `emp`, `sep`, `hira` etc. for cross-checks
- **Cross-tabulations:** By race, ethnicity, education, and sex.
- **Authors' extraction date:** 2025-03-05 (Footnote 1).

### 3.2 Validation — State administrative data

| State | Construct | URL (as cited) |
|---|---|---|
| Colorado | Personnel turnover by district & position | https://www.cde.state.co.us/cdereval/staffcurrent |
| Maryland | Staff data | https://reportcard.msde.maryland.gov/Graphs/#/DataDownloads/datadownload/3/17/6/02/XXXX/2023 |
| Pennsylvania | Professional staff summary | https://www.pa.gov/en/agencies/education/data-and-reporting/school-staff/professional-and-support-personnel.html |
| Virginia | Staffing and vacancy report | https://www.doe.virginia.gov/teaching-learning-assessment/teaching-in-virginia/education-workforce-datareports |

All four sites are publicly accessible; the data are downloadable (CSV/Excel). Note: these are snapshot URLs; the data on these sites get updated annually, and the version the authors used may no longer be the version currently displayed. The Wayback Machine may need to be used to recover the 2024-vintage versions.

### 3.3 Auxiliary
- **CCD (Common Core of Data):** https://nces.ed.gov/ccd/ccddata.asp — used to obtain FTE counts by county-year, used as inverse weights.
- **CPS / EPI extracts:** https://microdata.epi.org/#citations — only needed for Appendix Figure A1 (occupation composition).

### 3.4 Policy use-case (Figure 6)
- **State takeover:** Coded from Schueler & Bleiberg (2022), JPAM 41(1), 162–192 (open access).
- **4-day school week:**
  - Colorado: https://www.cde.state.co.us/cdeedserv/coloradofourdayandfivedaydistricts
  - Missouri: https://docs.google.com/spreadsheets/d/1zfoLZhi2vQzgQzxpFho7NEdvOeiWbWtdrF1A0CjeWN4/edit?gid=2070092708

---

## 4. Target values for validation (from the supplementary appendix)

The supplementary materials give **exact numbers** to validate against:

- **Table A1** — Validation correlations (8 numbers): turnover-state 0.892536, leavers-state 0.854932, NNJF-VA 0.843126, etc.
- **Table A2** — Pooled descriptives: turnover mean=0.261, median=0.251, between-SD=0.066, within-SD=0.041; NNJF/100 mean=3.32, median=1.080.
- **Table A3** — Quantile-regression coefficients on year dummies: 2020 effect on turnover = +0.0331***, 2022–2024 effect = +0.0268***, etc., with sample sizes (N=43,189; N=21,231; N=47,884; N=11,722; N=24,001).
- **Table A4** — Year-level turnover & NNJF (24 rows × 5 columns) — direct reproduction target for Figure 3.
- **Table A5** — Subgroup quantile-regression coefficients: Non-White +0.0960***, Hispanic +0.0837***, Bachelors -0.0696***, etc.
- **Tables A6–A7** — Year × subgroup turnover and NNJF (24 rows × 6 columns each).
- **Table A8** — 50-state pandemic-era stats (Alaska missing; Connecticut missing turnover).

These give us a tight cross-check at the **table level** and at the **figure level** for every figure in the paper.

---

## 5. Open questions and issues for the user

The following ambiguities need resolution before replication can finish. Some can be settled by experimentation; others may benefit from contacting the authors.

### 5.1 No replication archive (most important)
The paper has **no code release, no data archive, no OSF/GitHub/Dataverse link**, and no data availability statement. Anything we produce must be reconstructed from the paper text alone.
**Question for user:** Should we proceed without contacting the authors, or should we email them first to ask whether they will share a replication script? Their contact info is in the paper (Pittsburgh, Mizzou). My recommendation: try replicating from text first; the appendix tables are tight enough to validate against.

### 5.2 QWI API endpoint selection
The QWI API has multiple endpoints with different cross-tab capabilities:
- `/qwi/sa` — state, by demographics
- `/qwi/rh` — county/MSA, by demographics
- `/qwi/se` — by sex × education
- etc.

Industry × race × ethnicity × county is not all available on a single endpoint. We will likely need multiple API pulls (one per cross-tab) and merge them. **Not an obstacle**, just additional engineering. Will identify the right endpoints once we start coding.

### 5.3 Outlier rule wording (Footnote 2) — AMBIGUOUS
> "We consider the turnover measure to be missing in years in which the number of leavers in a county differs from the county average by 33% or more."

Three plausible interpretations:
1. Drop county-year if `|leavers_cy - mean(leavers_c)| / mean(leavers_c) > 0.33` (i.e., 33% deviation from the all-time county mean)
2. Drop if same condition using a rolling window
3. Drop if it differs by **33 percentage points** (less likely — phrasing says 33% not 33pp)

The footnote also says "Consequently, the number of counties/years with observed turnover **decreased from about 23% to about 35%**." This is itself awkwardly phrased — likely means the share of obs flagged ranges from ~23% to ~35% across years (or possibly that the share of obs that are *available* goes from 23% to 35% — unclear).

**Replication strategy:** Implement interpretation #1 first, compare resulting N to Appendix Table A3 sample sizes (e.g., N=43,189 for the turnover/year-2020 regression). If we hit the same N, we've nailed the rule.

### 5.4 "Non-White" composition
QWI uses non-mutually-exclusive race and ethnicity dimensions. The paper aggregates to "non-White" without explicitly defining the composition. Standard interpretation is anyone whose race is not "White alone" (which includes Black, Asian, AIAN, NHPI, Two-or-more-races). Appendix Table A6 gives target turnover values for "Non-White" — we'll calibrate against those.

### 5.5 CCD file specifics
- Authors cite "U.S. Department of Education, 2024" → https://nces.ed.gov/ccd/ccddata.asp
- Which **file**? CCD has: District (LEA) Universe, Public School Universe, Staff file (district-level), Membership file, etc.
- Likely: **District-level staff file (FTE counts)** aggregated to county-year by mapping districts to counties (LEA crosswalk file). Or potentially the **school-level staff file**.
- **Replication strategy:** Try district-staff → county-year aggregation first. Test whether the resulting weights produce the same weighted means as in Table A4.

### 5.6 Public vs. all schools
Paper says: "we include public and private schools. ... the results below are substantively similar to auxiliary analyses that include only public schools." So we will follow that — keep NAICS 6111 as a single union of public + private. Optional: also do a public-only auxiliary pass.

### 5.7 Software stack
Authors don't specify their software. The use of quantile regressions and weighted regressions suggests Stata or R. I'll default to **R + tidyverse + `tidycensus`/`censusapi` for the API + `quantreg` for quantile regressions** unless you prefer Python or Stata.
**Question for user:** R, Python, or Stata?

### 5.8 Minor inconsistencies in the paper itself
These don't affect feasibility but should be flagged so we can pick the right target:
- Abstract: "~250,000 education positions lost during pandemic"; Body text: "225,000"; Appendix Table A4: total NNJF in 2020 = 224.9 (in 1000s) = 224,900. → Abstract figure is loose.
- Body text: median NNJF = 43; Figure 2B label: median = 108. → Probably weighted vs unweighted; Table A2 says median = 43 (unweighted county median) so the figure is the weighted version.
- Body text: post-pandemic median turnover ≈ 26.9%; Table A4 (2022, 2023, 2024 medians): 27.1, 26.6, 25.8 → average 26.5 → close to but not exactly 26.9.

### 5.9 QWI revisions since extraction
QWI is revised approximately quarterly. The authors extracted on **2025-03-05**. If we pull today (2026-05-11), we'll have additional quarters and revised values for older quarters. We will likely come within ~1 pp of the authors' numbers but won't match exactly.
**Question for user:** Are you OK with "close but not exact" replication, or do you want us to attempt to pin the data vintage (e.g., by checking if Census archives older snapshots, which they generally do not)?

### 5.10 Census API key
- The user needs a Census API key. It's free.
- **Action needed from user:** Sign up at https://api.census.gov/data/key_signup.html and provide the key (we can store it as an env var, not in code).

---

## 6. What we have on hand

```
qwi_aeraopen/
├── bleiberg-nguyen-2026-...pdf                  # main paper (18pp)
├── sj-docx-1-ero-10.1177_23328584261443298.pdf  # supplementary appendix (15pp)
├── bleiberg-nguyen-...text.md                   # structured extract (this read)
├── REPLICATION_FEASIBILITY.md                   # this report
└── qwi_aeraopen_build/                          # working files (splits)
```

---

## 7. Recommended plan if you give the green light

### Phase 1 — Setup (1–2 hours)
- Get Census API key
- Decide R / Python / Stata
- Create project structure with separate folders for: raw QWI pulls, raw state validation data, raw CCD, derived data, figures, tables

### Phase 2 — QWI data pull (3–5 hours)
- Pull county-level emptotal and hirn for NAICS 6111, all quarters 2000 Q1 – 2024 Q2 (or latest)
- Pull county-level cross-tabs by race, ethnicity, education
- Save raw pulls; never re-pull unless needed

### Phase 3 — Construct measures (2–3 hours)
- Implement Equations 1, 2, 3
- Apply outlier rule (Footnote 2)
- Merge CCD FTE weights at county-year level

### Phase 4 — Validation (2–3 hours)
- Pull CO, MD, PA, VA state data
- Reproduce Appendix Table A1 (validation correlations)
- Reproduce Figure 1 scatterplots

### Phase 5 — Descriptive results (4–6 hours)
- Reproduce Figures 2–5 and Appendix Figures A1–A4
- Reproduce Appendix Tables A2–A8

### Phase 6 — Policy use case (2–3 hours)
- Pull state takeover data from Schueler & Bleiberg (2022)
- Pull 4-day week data from CDE and MDE
- Reproduce Figure 6 (regression with state + year FE)

### Phase 7 — Write replication report (2–3 hours)
- Compare our numbers to the appendix targets
- Document any non-matching values and the likely reasons

**Total: ~16–25 hours of effort spread over 1–3 days.**

---

## 8. Decisions I need from you before starting

1. **Software preference:** R, Python, or Stata?
2. **Census API key:** Will you obtain one, or want me to walk you through?
3. **Contact authors?** Email Bleiberg / Nguyen to request code, or proceed from text alone?
4. **Data vintage:** OK with newest-pull values, or attempt to reconstruct the March 2025 vintage?
5. **Scope:** Full replication (every figure and every table), or main-body only (Figures 1–6)?
6. **Output format:** Replication report as markdown + side-by-side comparison tables, or a fuller writeup?
