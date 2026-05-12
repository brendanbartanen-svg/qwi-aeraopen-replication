# Replication of Bleiberg & Nguyen (2026)

Independent replication of:

> Bleiberg, J. & Nguyen, T. D. (2026). Leveraging Quarterly Workforce Indicators to Analyze K–12 Education Labor Market Dynamics: Inequitable Trends in Turnover. *AERA Open*, 12(1), 1–18. [DOI: 10.1177/23328584261443298](https://doi.org/10.1177/23328584261443298)

**Headline:** All 12 substantive claims tested replicate (11 quantitatively, 1 not tested per the original scope). Full report: [`REPLICATION_REPORT.md`](REPLICATION_REPORT.md).

Built by Claude (Opus 4.7, 1M context), supervised by Brendan Bartanen.

---

## What's in this repo

| Path | Contents |
|---|---|
| [`REPLICATION_REPORT.md`](REPLICATION_REPORT.md) | Main deliverable. Claim-by-claim verdict table, methodology issues, validation findings. |
| `replication/code/` | All Python scripts: data pulls, measure construction, figures, appendix tables, sub-agent investigation scripts. |
| `replication/data/derived/` | Built measures (parquet) — county-school-year panel, validation panel, etc. |
| `replication/data/raw/state_validation/` | State administrative validation data (small CSVs and PDFs). Excludes PA per-person files (see below). |
| `replication/output/figures/` | Replicated paper figures. |
| `replication/output/tables/` | Replicated appendix tables (markdown + CSV). |
| `replication/output/reports/` | Sub-agent investigation reports (NNJF formula reverse-engineering, state-data-recovery write-ups, paper-comparison report). |
| `replication/output/validation/` | Multi-agent validation of the state administrative extractions: per-method extraction CSVs, cell-level reconciliation, semantic audits. |

## What's NOT in this repo (and where to get it)

The `.gitignore` excludes these. They're either large, re-downloadable, copyright-restricted, or contain personnel data.

| Excluded | Where to get | Why excluded |
|---|---|---|
| `bleiberg-nguyen-2026-*.pdf` and `sj-docx-1-ero-*.pdf` | [DOI link](https://doi.org/10.1177/23328584261443298) | Copyright |
| `replication/data/raw/qwi_current/` (QWI parquet pulls, ~14 MB) | Re-pull via the code: `python3 replication/code/01b_pull_qwi_county_emp.py` etc. (needs Census API key) | Re-downloadable |
| `replication/data/raw/qwi_vintage_2025q1/` (paper's data vintage) | Census QWI archives; no longer available from current API | Vintage not preserved by Census after revisions |
| `replication/data/raw/ccd/` (NCES Common Core of Data, ~72 MB) | [NCES CCD](https://nces.ed.gov/ccd/files.asp) — files for LEA universe and EDGE LEA-county crosswalks | Large + re-downloadable |
| `replication/data/raw/state_validation/pa_*_individual_staff.xlsx` (PA Professional Personnel Individual Staff files, ~165 MB) | [PA PDE](https://www.education.pa.gov/DataAndReporting/ProfPerSummary/Pages/default.aspx) → Professional Personnel Individual Staff Reports | Large + per-person records |
| `.env` | Make your own: `cp replication/.env.example replication/.env` and add a [Census API key](https://api.census.gov/data/key_signup.html) | Secrets |

## Quickstart: reproduce the analysis

```bash
# 1. Get a Census API key (free, instant)
#    https://api.census.gov/data/key_signup.html
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

# 3. Build measures (county-school-year panel, turnover, NNJF)
python3 code/10_construct_measures.py

# 4. Figures
python3 code/20_figure_2_distribution.py
python3 code/21_figure_3_time_trends.py
python3 code/22_figure_4_race_ethnicity.py
python3 code/23_figure_5_education.py
python3 code/30_figure_1_validation.py

# 5. Appendix tables
python3 code/40_appendix_table_a3.py
python3 code/41_appendix_table_a5.py
python3 code/42_appendix_tables_a6_a7.py
python3 code/43_appendix_table_a8.py
python3 code/44_appendix_table_a7.py

# 6. Paper-comparison report
python3 code/90_build_comparison_report.py
```

State administrative validation data (CO, PA, VA, MD) was recovered manually; recovery write-ups are in `replication/output/reports/state_data_hunt_*.md`. The PA per-person personnel files have to be downloaded separately from PDE if you want to re-compute the PA all-staff turnover (`code/15_compute_pa_all_staff_turnover.py`).

## Reusing this work

If you want to extend the QWI K-12 approach the paper introduces, the most useful artifacts here are probably:

- **`replication/code/10_construct_measures.py`** — the working NNJF formula (`avg over 4 school-year quarters of max(FrmJbLsS - FrmJbGnS, 0)`) reverse-engineered from the paper's reported values. The paper's stated Equations 2-3 do not produce its reported numbers; see [`REPLICATION_REPORT.md`](REPLICATION_REPORT.md) §"Implementation issues" for the full story.
- **`replication/output/reports/agent_*.md`** — the 6 parallel sub-agent investigations that tested 60+ alternative NNJF specifications.
- **`replication/output/validation/`** — the multi-agent validation framework for state-administrative-data extraction. Applies to any PDF-source dataset, not just this paper.

## Key methodology footnotes

A few non-obvious details surfaced by replication and semantic auditing:

1. **NNJF formula.** Paper Eq 2-3 are insufficient to reproduce the paper's reported values. The actual formula uses QWI variables `FrmJbLsS` and `FrmJbGnS` (firm-level stable job losses/gains), which the paper doesn't reference.
2. **Per-100 NNJF normalization is not consistent across tables.** Tables A2, A4, A7, A8, and Figure 2 use at least three different normalizations.
3. **JLARC VA vacancy snapshots changed between years.** SY 2022-23 unfilled FTE = "reported vacant as of October 1, 2022". SY 2023-24 unfilled FTE = "actual or assumed to be vacant on the first day of school". Year-over-year comparisons inherit this definitional change.
4. **JLARC pre-pandemic average is 5 years**, not 3: averages SY 2015-16 through SY 2019-20.
5. **MD chart title vs. data direction.** TWS-2024 page 11 is titled "SY 2023-2024" but the data measures the 2022-23 → 2023-24 transition (the title is the year of non-return, not the cohort year).

## License

Code: MIT.  
Replicated figures and tables follow AERA Open's CC BY-NC 4.0 license on the original paper.  
State administrative data files are public; sources are linked above.
