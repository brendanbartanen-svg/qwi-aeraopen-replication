# Replication of Bleiberg & Nguyen (2026)

Independent replication of:

> Bleiberg, J. & Nguyen, T. D. (2026). Leveraging Quarterly Workforce Indicators to Analyze K–12 Education Labor Market Dynamics: Inequitable Trends in Turnover. *AERA Open*, 12(1), 1–18. [DOI: 10.1177/23328584261443298](https://doi.org/10.1177/23328584261443298)

**Headline:** Of 12 substantive claims tested, 10 are confirmed quantitatively, 1 is **mixed** (Claim 6: pandemic-year direction holds, but the specific "~225,000 jobs lost" magnitude is contingent on a gross-loss formula not described in the paper), and 1 was not independently tested. No claim is contradicted. Full report: [`REPLICATION_REPORT.md`](REPLICATION_REPORT.md).

A bit-for-bit replication of the paper's reported numbers is structurally impossible because Census revises QWI quarterly and does not preserve historical vintages — see the "perfect replication" note in the main report.

**Releases:**
- [`v1.0-independent-replication`](https://github.com/brendanbartanen-svg/qwi-aeraopen-replication/releases/tag/v1.0-independent-replication) — independent replication using only public data and the paper's text
- [`v2.0-with-author-code`](https://github.com/brendanbartanen-svg/qwi-aeraopen-replication/releases/tag/v2.0-with-author-code) — intermediate snapshot after the authors shared their Stata code privately
- **Current `main` (v2.1)** — adds NCES CCD teacher FTE for the `1/FTE` weighting in the authors' code

Built by Claude (Opus 4.7, 1M context), supervised by Brendan Bartanen.

---

## What's in this repo

| Path | Contents |
|---|---|
| [`REPLICATION_REPORT.md`](REPLICATION_REPORT.md) | Main deliverable. Claim-by-claim verdict, methodology issues, multi-agent validation findings. |
| `replication/code/` | 30 Python scripts: data pulls (`01*-05*`), measure construction (`10`), figures (`20-23`, `30`), appendix tables (`40-45`), paper-comparison report (`90`), and NNJF reverse-engineering sub-agent investigations (`91-96`). |
| `replication/data/raw/state_validation/` | 38 state administrative source files (CO/MD/PA/VA — small CSVs, xlsx, PDFs). The 5 large PA `*_individual_staff.xlsx` per-person files are gitignored (see below). |
| `replication/output/figures/` | 5 replicated paper figures (PNG). |
| `replication/output/tables/` | Replicated appendix tables (markdown + CSV). |
| `replication/output/reports/` | Sub-agent investigation reports (NNJF reverse-engineering 6 reports; state-data-recovery write-ups for CO/MD/PA/VA, 6 reports; paper-comparison report; author-archive-hunt report). |
| `replication/output/validation/` | Multi-agent validation of state administrative extractions: per-method extraction CSVs, cell-level reconciliation, semantic audits across 6 source files. |

## What's NOT in this repo (and where to get it)

`.gitignore` excludes these. They're either large, re-downloadable, copyright-restricted, or contain per-person data.

| Excluded | Where to get | Why excluded |
|---|---|---|
| `bleiberg-nguyen-2026-*.pdf` and `sj-docx-1-ero-*.pdf` | [DOI link](https://doi.org/10.1177/23328584261443298) | Copyright |
| `replication/data/raw/qwi_current/` (QWI parquet pulls, ~14 MB) | Re-pull via `python3 replication/code/01b_pull_qwi_county_emp.py` etc. (needs Census API key) | Re-downloadable |
| `replication/data/raw/qwi_vintage_2025q1/` (paper's data vintage) | No longer available from Census API | Vintage not preserved publicly |
| `replication/data/raw/ccd/` (NCES Common Core of Data + LEA-staff FTE source files, ~190 MB) | [NCES CCD bulk files](https://nces.ed.gov/ccd/files.asp) — `ccd_lea_059_*` series for FTE; EDGE LEA-county crosswalks | Large + re-downloadable |
| `replication/data/derived/*.parquet` (built measures, ~3 MB) | Regenerate via `python3 replication/code/10_construct_measures.py` | Re-buildable from code |
| `replication/data/raw/state_validation/pa_*_individual_staff.xlsx` (PA Professional Personnel Individual Staff files, ~165 MB total across 5 years) | [PA PDE](https://www.education.pa.gov/DataAndReporting/ProfPerSummary/Pages/default.aspx) → Professional Personnel Individual Staff Reports | Large + per-person records |
| `.env` | Make your own: `cp replication/.env.example replication/.env` and add a [Census API key](https://api.census.gov/data/key_signup.html) | Secrets |

## Quickstart: reproduce the analysis

```bash
# 1. Get a Census API key (free, instant): https://api.census.gov/data/key_signup.html
cp replication/.env.example replication/.env
# Edit replication/.env and set CENSUS_API_KEY=<your key>

# 2. Pull QWI data (~20 minutes total over Census API)
cd replication
python3 code/01b_pull_qwi_county_emp.py
python3 code/01c_pull_qwi_county_extended.py
python3 code/01d_pull_qwi_county_frmjblss.py
python3 code/02_pull_qwi_race.py
python3 code/03_pull_qwi_education.py
python3 code/04_pull_qwi_race_nnjf.py
python3 code/05_pull_qwi_edu_nnjf.py

# 3. (Optional) Pull NCES CCD LEA-staff FTE for the 1/FTE weighting per authors' code.
#    Without this, the pipeline falls back to 1/EmpTotal (covers ~98% of county-years
#    either way; FTE just tightens the match to paper Table A4 by ~0.5 pp on average).
#    See `replication/data/raw/ccd/` README in the code for the source URLs.

# 4. Build measures (county-school-year panel: turnover, NNJF, weights, outliers)
python3 code/10_construct_measures.py

# 5. Figures
python3 code/20_figure_2_distribution.py
python3 code/21_figure_3_time_trends.py
python3 code/22_figure_4_race_ethnicity.py
python3 code/23_figure_5_education.py
python3 code/30_figure_1_validation.py

# 6. Appendix tables
python3 code/40_appendix_table_a3.py
python3 code/41_appendix_table_a5.py
python3 code/42_appendix_tables_a6_a7.py
python3 code/43_appendix_table_a8.py
python3 code/44_appendix_table_a7.py
python3 code/45_appendix_table_a4.py

# 7. Paper-comparison report
python3 code/90_build_comparison_report.py
```

State administrative validation data (CO, PA, VA, MD) was recovered manually; recovery write-ups are in `replication/output/reports/state_data_hunt_*.md`.

## Reusing this work

If you want to extend the QWI K-12 approach the paper introduces, the most useful artifacts here are:

- **`replication/code/10_construct_measures.py`** — the working NNJF measure construction. The current implementation (v2.1) uses `sum(FrmJbLsS)` over the four school-year quarters per the authors' code. The script also computes an alternative window and the truly-net variant (`sum(FrmJbLsS − FrmJbGnS)`) so you can switch.
- **`replication/code/_config.py`** — helpers including Stata-style aweight sum/mean/quantile that reproduce `collapse (sum) [aw=w]` exactly. Useful for any QWI work where you want to match a Stata pipeline from Python.
- **`replication/output/reports/agent_*.md`** — the 6 parallel sub-agent investigations that tested 60+ alternative NNJF specifications during v1.0 (before the authors' code was available). Documents what each variant produces.
- **`replication/output/validation/`** — the multi-agent validation framework for state-administrative-data extraction. Applies to any PDF-source dataset, not just this paper.

## Key methodology footnotes

A few non-obvious details surfaced by replication and semantic auditing:

1. **NNJF formula.** Paper Equations 2-3 (`|emp_{q+1} − emp_q|` using `EmpTotal`) are insufficient — implementing them literally gives values 5-8× the paper's reported totals. The actual operational formula sums QWI's `FrmJbLsS` (firm-level stable job losses) across the four school-year quarters. The paper doesn't reference this variable in its equations.
2. **"Net-Negative" is misleading.** Despite the construct's name, the operational formula does NOT subtract `FrmJbGnS` (firm-level stable job gains). The reported magnitude is gross loss at contracting districts. A truly *net* formula yields roughly half the magnitude.
3. **Per-100 NNJF normalization is not consistent across appendix tables.** Tables A2, A4, A6/A7, and A8 each use a different denominator/formula despite sharing the column header "NNJF Per 100". See REPLICATION_REPORT.md for the per-table specifics.
4. **JLARC VA vacancy snapshots changed between years.** SY 2022-23 unfilled FTE = "reported vacant as of October 1, 2022". SY 2023-24 unfilled FTE = "actual or assumed to be vacant on the first day of school". Year-over-year comparisons inherit this definitional change.
5. **JLARC pre-pandemic average is 5 years**, not 3: averages SY 2015-16 through SY 2019-20.
6. **MD TWS-2024 chart title vs. data direction.** Page 11 is titled "SY 2023-2024" but the data measures the 2022-23 → 2023-24 transition (the title is the year of non-return, not the cohort year).

## License

Code: MIT.  
Replicated figures and tables follow AERA Open's CC BY-NC 4.0 license on the original paper.  
State administrative data files are public; sources are linked above.
