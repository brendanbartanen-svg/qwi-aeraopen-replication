# Draft email to authors

**To:** jbleiberg@pitt.edu, tuan.nguyen@missouri.edu
**Subject:** Questions about replicating your AERA Open paper on QWI / K-12 labor markets

---

Dear Drs. Bleiberg and Nguyen,

I recently conducted an independent replication of your AERA Open paper "Leveraging Quarterly Workforce Indicators to Analyze K–12 Education Labor Market Dynamics" (DOI: 10.1177/23328584261443298). I wanted to share what I found and ask about three specific issues that came up during the process. I hope you'll have a moment to clarify.

**The substantive findings replicate.** Using only the public QWI API and independently recovered state administrative data, I reproduced 11 of the 12 main claims I tested:

- Turnover Equation 1 replicates exactly. My Appendix Table A5 subgroup coefficients match yours to four decimal places (Non-White +0.0956 vs your +0.0960; Hispanic +0.0844 vs +0.0837; Bachelor's −0.0697 vs −0.0696).
- The 2020 pandemic turnover spike, post-pandemic elevation, racial/ethnic disparities, and educational attainment gradient all replicate quantitatively.
- The total NNJF for school year 2019-20 in my replication is 252.7K vs your 224.9K (1.12×); year-by-year totals match within ±5% for non-pandemic years.
- Regional patterns during the pandemic match — the three regions you highlight (Mid-Atlantic, South Atlantic, East South Central) are the bottom three in my pandemic-era turnover ranking across the nine Census regions.

**Three things, however, I could not resolve from the published text alone, and I'd be grateful for your perspective on:**

### 1. The NNJF formula in Equations 2-3

Implementing Equation 2 literally with `EmpTotal` (the variable Footnote 4 references) gives values 5-8× your reported NNJF totals. The seasonal swing in EmpTotal between Q2 (school in session) and Q3 (summer) appears to dominate the `|emp_{q+1} - emp_q|` calculation.

After testing about 60 alternative specifications, the formula that matches your reported NNJF Totals within ±10% every year (including the pandemic year) is:

```
NNJF_cst = avg over 4 school-year quarters of max(FrmJbLsS_q − FrmJbGnS_q, 0)
```

That is, the *net firm-level loss in stable employment*, averaged across the four school-year quarters. **Is this the formula you actually used?** If so, I think a footnote or a slight revision to Equations 2-3 would help readers, since the published formula reads as `abs()` of `EmpTotal` differences and doesn't reference `FrmJbLsS` or `FrmJbGnS`.

### 2. The per-100 NNJF normalization differs across tables

The NNJF/100 values reported across your appendix tables and figures don't seem to share a single normalization. Specifically:

- **Table A2 (pooled)**: median 1.08, mean 3.32
- **Table A4 (yearly means 2001-2024)**: 0.61 to 0.93. A 24-year average of values ≤ 0.93 cannot give a pooled mean of 3.32.
- **Table A7 (by group × year)**: 8.98 to 19.03 — about 10× larger than Table A4.
- **Table A8 (state pandemic)**: 6.6 to 16.6 — similar scale to A7.
- **Figure 2 Panel B**: unweighted median 108, P99 3,660 (this matches `sum(FrmJbLsS over 4Q)` unweighted) while Table A2's weighted stats match the same measure under 1/emp weighting.

I was able to identify a best-fit formula for each table separately (e.g., Table A4 = `avg(net stable losses) / sum(EmpTotal over 4 quarters)`; Table A7 = `sum(FrmJbLsS over 4Q) / EmpTotal_Q4_lag`) and replicate each within ±10-15%. **But there doesn't appear to be a single per-100 formula that matches all the tables.** Was this intentional, or could you share the specific normalization used in each one?

### 3. Replication code and data

The paper doesn't link to a replication archive (GitHub, OSF, Dataverse), and I couldn't find one elsewhere. The state administrative data sources cited in the paper also pose challenges for current readers:

- The CDE Personnel Turnover URL no longer hosts the 2021-22 / 2022-23 files (I recovered them via the Wayback Machine).
- The MSDE Staff data URL is a JavaScript-rendered single-page app; the actual LEA-level attrition file for SY 2022-23 isn't in the publicly indexed downloads.
- The PDE Professional Staff Summary files contain only snapshot headcounts; the all-staff turnover requires computing from PDE's underlying Professional Personnel Individual Staff per-person files.
- The VDOE Staffing and Vacancy Report URL is captcha-gated; I obtained the same data from JLARC Reports 568 and 576, which republish the VDOE PEC source.

Given that QWI itself is revised quarterly (the R2024Q4 release you used in March 2025 is no longer archived by Census), **would you be willing to share your replication code and/or the cleaned state datasets?** Even a partial release — for example, the NNJF construction code or a frozen copy of the four state files — would help future readers extend the QWI approach without independently re-discovering the implementation choices.

---

I'm happy to share my replication materials (Python code, recovered state datasets, comparison tables) if it would be helpful. The replication compares my values to yours side-by-side for every table and figure I tested.

Thank you for the paper — the QWI-based approach is a real contribution, and the substantive findings clearly hold up. I'd be grateful for any clarification on the points above.

Best,
Brendan Bartanen
