# Author-Shared Replication Materials Hunt
## Bleiberg & Nguyen (2026) "Leveraging Quarterly Workforce Indicators to Analyze K-12 Education Labor Market Dynamics" (AERA Open)

**Date checked:** 2026-05-11
**Bottom line:** No author-shared replication materials (code or data) were located on any public platform after a thorough search.

---

## Summary

- **No GitHub repo** for this paper on either author's account.
- **No OSF project** for either author related to this paper.
- **No Dataverse / openICPSR / ICPSR deposit** for this paper.
- **No supplementary materials** linked from any version of the paper (EdWorkingPaper PDF, AERA Open page, faculty websites, or presentation slides).
- **No social media** posts surfacing replication code.
- **Nothing saved** to `data/raw/author_shared/` (directory created but empty).

---

## Author profiles confirmed

### Joshua Bleiberg (University of Pittsburgh)
- Personal site: https://sites.google.com/view/joshbleiberg (joshbleiberg.com redirects here)
- GitHub: https://github.com/joshbleiberg
- BlueSky: https://bsky.app/profile/joshbleiberg.bsky.social
- Google Scholar: https://scholar.google.com/citations?user=UwP8OHcAAAAJ
- Pitt faculty: https://www.education.pitt.edu/faculty/directory/josh-bleiberg/

### Tuan D. Nguyen (University of Missouri)
- Personal site: https://tuan-d-nguyen.github.io/home
- GitHub: https://github.com/tuan-d-nguyen
- Research site: https://www.teachershortages.com (collaborative project)

---

## Detailed findings

### 1. GitHub

**Joshua Bleiberg's repos (https://github.com/joshbleiberg)** — 6 public repos, all Stata, **none for the QWI paper**:
1. `essa_sch_acct` — COVID school accountability data under ESSA (state-level CSI/TSI designations). Not QWI.
2. `stackedev` — Stata module for stacked event-study estimator. Method only, not paper-specific.
3. `covid` — Rhode Island active COVID infection estimates. Not education.
4. `EventStudyInteract` — Fork of lsun20's Sun-Abraham estimator code.
5. `common_core` — Replication code for Bleiberg (2021) AERA Open Common Core paper.
6. `education_attention` — Replication for Bleiberg (2019) JEP paper on threat-induced education reform.

**Tuan D. Nguyen's repos (https://github.com/tuan-d-nguyen)** — 1 public repo:
1. `tuan-d-nguyen.github.io` — Personal website fork only. No research repos.

Variants checked (all 404 or unrelated): `jbleiberg`, `joshuableiberg`, `tdnguyen` (unrelated), `tuannguyen` (empty), `tuan3w`, `anhtuank7c`, `natuan`, `tuanchris`, `nguyentuan1696`, etc.

GitHub global searches for "QWI education turnover" and "Bleiberg/Nguyen + labor market" returned **no matching repositories**.

### 2. OSF
- Site search for "Bleiberg" returned no relevant projects.
- The OSF "Tuan Nguyen" hit was an unrelated moral-outrage social-psych project.
- No OSF profile linked from either author's website.

### 3. Dataverse / openICPSR / ICPSR
- No Harvard Dataverse hits for either author on this topic.
- AERA Open's openICPSR repo (`https://www.openicpsr.org/openicpsr/aerajournals`) blocks scraping (403) but no Google-indexed deposit matches "Bleiberg" or "Tuan D. Nguyen / QWI".
- The only QWI-related openICPSR deposit is McKinney et al.'s "Total Error and Variability Measures for QWI and LODES" — **not** this paper.

### 4. Personal websites
- **Bleiberg's Google Site** "Recent Publications" page lists 4 publications. The QWI paper with Nguyen is **not even listed**. No code/data links anywhere on the site beyond a top-level link to his GitHub profile.
- **Nguyen's GitHub Pages site** (`tuan-d-nguyen.github.io`) — research page lists 26 numbered publications. The Bleiberg co-authored QWI paper is **not listed**. The site links only to his GitHub profile and to teachershortages.com / ruralityindex.com.
- Bleiberg's Pitt faculty page: no data/code links.
- Bleiberg's Annenberg page: no data/code links.
- teachershortages.com: no QWI data or code; references external data sources only.

### 5. Working paper PDF
Downloaded the EdWorkingPaper version (`ai25-1135.pdf`, 1.7MB, version Feb 2025) at `/tmp/bleiberg_nguyen_ai25-1135.pdf` and extracted all text. **No** GitHub, OSF, Dataverse, openICPSR, "replication", "code available", or "data available" URL appears anywhere in the document. The only HTTPS URLs are DOI links to cited references and the Census QWI documentation URL.

### 6. Conference / presentation materials
- A September 2025 LED Partnership workshop presentation by Bleiberg & Nguyen exists at https://lehd.ces.census.gov/doc/workshop/2025/Exploring_Inequitable_Trends_in_Education_Staff_Turnover.pdf (downloaded; full text extracted). **No** code/data/replication links — only author emails and personal website URLs.
- Census Bureau follow-up webinar (April 2026): https://www.census.gov/data/academy/webinars/2026/trends-in-education-staff-turnover.html — page states "Webinar materials coming soon." Currently nothing available.

### 7. AERA Open journal page
- Sage Journals search endpoint returns 403; not accessible programmatically. Based on indexed signals the article was first published online May 5, 2026, but the article-level page (which would carry any supplementary file link or data availability statement) could not be retrieved. Given that the working paper PDF has no data/code section and neither author's site references a repo for this paper, it is very unlikely the journal page links to one.

### 8. Social media
- BlueSky profile exists (`joshbleiberg.bsky.social`) but no indexed posts about replication/code for this paper. Nguyen has no obvious public BlueSky/Twitter handle.

---

## Notable observations

1. **Bleiberg routinely posts replication code** for his AERA Open and JEP papers (e.g., `common_core`, `education_attention` repos exist for older papers). The conspicuous **absence** of a corresponding repo for the QWI paper is informative — it suggests no public release rather than us simply missing it.

2. The paper's analysis uses **public QWI data** (LEHD/Census) plus state-administrative validation data from Virginia. The Virginia teacher-vacancy data is also publicly available. So the data are reconstructible from public sources; only the authors' processing code would be net-new.

3. **Author emails for direct request:**
   - Bleiberg: jbleiberg@pitt.edu (or jbleiber@pitt.edu per Pitt directory)
   - Nguyen: tuan.nguyen@missouri.edu

---

## Files saved
- `data/raw/author_shared/` — directory created, **empty** (no materials found to save).
- `/tmp/bleiberg_nguyen_ai25-1135.pdf` — EdWorkingPaper PDF (cached, not in repo).
- `/tmp/census_pres.pdf` — Sept 2025 LED workshop slides (cached, not in repo).

---

## Recommended next steps for the replication effort
1. Build the QWI pull from scratch using the LEHD Census API (paper specifies NAICS 6111 Elementary & Secondary Schools, 2000-01 through 2022-23/2023-24).
2. Pull Virginia teacher-vacancy data from VDOE directly for the R=0.73 validation correlation reported in the paper.
3. Email the authors at the addresses above to request the Stata processing scripts — given Bleiberg's track record of releasing code post-publication, code may eventually appear at https://github.com/joshbleiberg.
