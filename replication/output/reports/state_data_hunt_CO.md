# Colorado Personnel Turnover Data Hunt

## Outcome: Both files found

Downloaded to `replication/data/raw/state_validation/`:

- `co_2021-22_turnover.xlsx` (132,675 bytes) — "Personnel Turnover Rate by District and Position Categories (2021-2022 compared with 2020-2021)". Sheets: Organization, State, Job Classifications, Key.
- `co_2022-23_turnover.xlsx` (137,758 bytes) — "Personnel Turnover Rate by District and Position Categories (2022-2023 compared with 2021-2022)". Same sheet structure.

Both files are valid Microsoft Excel 2007+ workbooks with identical schema to the existing `co_2025-26_turnover.xlsx`, with `District Code`, `District Name`, `Position (Job) Categories`, `<prior year> Head Count`, `<current year> Head Count`, `Difference`, `People Returned`, `People Left`.

## What worked

1. **CDE Data Insights, Resources & Archives page** — `https://ed.cde.state.co.us/cdereval/staffstatistics/data-insights-resources-archives` lists historical files going back several years. Found via Google search `site:ed.cde.state.co.us turnover`.

2. **2022-23 file** — Downloaded directly from CDE's current resource manager: `https://ed.cde.state.co.us/fs/resource-manager/view/73214412-265c-4e2b-aef3-cae32e1e0d9a` (the canonical UUID listed on the archives page; file name on server: `20222023PersonelTurnoverRates.xlsx`).

3. **2021-22 file** — The archive page links to the old-host path `https://www.cde.state.co.us/cdereval/2021-22personnelturnoverratebydistrictandpositioncategoriesxls`. The host `www.cde.state.co.us` was unreachable from this environment (connection refused at TCP level on both 443 and 80; `ed.cde.state.co.us` resolved/served fine via Cloudflare). I fetched from the Wayback Machine using the `if_` raw modifier on capture `20250830194653` of the same URL.

## What didn't work / wasn't needed

- Direct guess URLs like `/sites/default/files/documents/cdereval/download/...` — all 404 or unreachable.
- Wayback CDX API (`/cdx/search/cdx`) — frequent 504 gateway timeouts on prefix searches. The `archive.org/wayback/available` JSON endpoint also returned no snapshots on the first try, but the simple `web.archive.org/web/<year>/<url>` redirect resolution did find captures.
- Colorado Open Data Portal — not needed once the CDE archive page was located.

## Notes for downstream use

- 2021-22 file's `District Code` column is text (zero-padded, e.g. `"0010"`); 2022-23 file's is integer. Standardize before joining.
- Column header in 2021-22 file misspells "Administrators" as "Adminstrators"; same typo present in 2022-23 file, so no harmonization needed across these two.
