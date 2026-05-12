"""Test 5+ sample-restriction hypotheses on NNJF/100 to close the ~3x rate gap.

Goal: paper reports pooled (weighted by 1/emp) median NNJF/100 ≈ 1.080 and mean ≈ 3.32,
plus year medians ~0.43/0.51/0.31/0.40 for 2019/2020/2021/2023. We get medians ~5-6x
higher.  Paper N for regression samples (Table A3): 47,884 / 11,722 / 24,001 for
2001-2021 / 2020-2024 / 2013-2024.  Mine: 50,657 / 11,878 / 29,003.

Approach: build per-quarter wide data with quarter-level FrmJbLsS plus EmpS so each
candidate filter can be applied to the school-year panel, and we recompute weighted
median/mean and year medians and the three regression-sample N values.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPL = Path('/Users/yvp3tf/Documents/CC Sandbox/replication/qwi_aeraopen/replication')
sys.path.insert(0, str(REPL / 'code'))


def weighted_quantile(values, weights, q=0.5):
    values = np.asarray(values, dtype=float)
    weights = np.asarray(weights, dtype=float)
    mask = np.isfinite(values) & np.isfinite(weights) & (weights > 0)
    values, weights = values[mask], weights[mask]
    if len(values) == 0:
        return np.nan
    idx = np.argsort(values)
    cum = np.cumsum(weights[idx]) / weights.sum()
    return float(values[idx][np.searchsorted(cum, q)])


def summarize(df: pd.DataFrame, label: str) -> dict:
    """Return key stats for a filtered NNJF panel."""
    s = df.dropna(subset=['nnjf_per_100', 'emp_lag']).copy()
    s = s[s['emp_lag'] > 0]
    n_2001_21 = ((s['school_year'] >= 2001) & (s['school_year'] <= 2021)).sum()
    n_2020_24 = ((s['school_year'] >= 2020) & (s['school_year'] <= 2024)).sum()
    n_2013_24 = ((s['school_year'] >= 2013) & (s['school_year'] <= 2024)).sum()
    w = 1.0 / s['emp_lag'].astype(float).values
    v = s['nnjf_per_100'].astype(float).values
    wmed = weighted_quantile(v, w, 0.5)
    wmean = (v * w).sum() / w.sum() if w.sum() > 0 else np.nan
    year_meds = {}
    for y in (2019, 2020, 2021, 2023):
        sy = s[s['school_year'] == y]
        if len(sy) > 0:
            year_meds[y] = float(sy['nnjf_per_100'].median())
        else:
            year_meds[y] = np.nan
    return {
        'label': label,
        'n_total': int(len(s)),
        'n_2001_2021': int(n_2001_21),
        'n_2020_2024': int(n_2020_24),
        'n_2013_2024': int(n_2013_24),
        'wmed_pooled': wmed,
        'wmean_pooled': wmean,
        'med_2019': year_meds[2019],
        'med_2020': year_meds[2020],
        'med_2021': year_meds[2021],
        'med_2023': year_meds[2023],
    }


def fmt(stats: dict) -> str:
    return (f"  N(2001-21)={stats['n_2001_2021']:>6}  "
            f"N(2020-24)={stats['n_2020_2024']:>6}  "
            f"N(2013-24)={stats['n_2013_2024']:>6}  "
            f"w-med={stats['wmed_pooled']:.3f}  w-mean={stats['wmean_pooled']:.3f}\n"
            f"  yr-medians 2019={stats['med_2019']:.3f}  2020={stats['med_2020']:.3f}  "
            f"2021={stats['med_2021']:.3f}  2023={stats['med_2023']:.3f}")


# ----------------------------------------------------------------------------
# Build wide panel with quarter-level FrmJbLsS / FrmJbLs / EmpTotal / EmpS
# ----------------------------------------------------------------------------

def build_wide() -> pd.DataFrame:
    main = pd.read_parquet(REPL / 'data/raw/qwi_current/county_sex0_full_2025q2.parquet')
    sstable = pd.read_parquet(REPL / 'data/raw/qwi_current/county_sex0_frmjblss.parquet')
    for c in ('EmpTotal', 'HirN', 'FrmJbLs'):
        if c in main.columns:
            main[c] = pd.to_numeric(main[c], errors='coerce')
    for c in ('FrmJbLsS', 'FrmJbGnS', 'EmpS', 'EmpEnd'):
        if c in sstable.columns:
            sstable[c] = pd.to_numeric(sstable[c], errors='coerce')

    pivots = []
    for src, prefix in [('EmpTotal', 'emp'), ('HirN', 'hir'), ('FrmJbLs', 'frmjbls')]:
        p = main.pivot_table(index=['fips', 'year'], columns='quarter', values=src, aggfunc='first')
        p.columns = [f'{prefix}_q{int(c)}' for c in p.columns]
        pivots.append(p)
    for src, prefix in [('FrmJbLsS', 'frmjblss'), ('FrmJbGnS', 'frmjbgns'),
                        ('EmpS', 'emps'), ('EmpEnd', 'empend')]:
        if src in sstable.columns:
            p = sstable.pivot_table(index=['fips', 'year'], columns='quarter', values=src, aggfunc='first')
            p.columns = [f'{prefix}_q{int(c)}' for c in p.columns]
            pivots.append(p)
    wide = pd.concat(pivots, axis=1).reset_index()
    return wide


def build_sy(wide: pd.DataFrame) -> pd.DataFrame:
    wide = wide.sort_values(['fips', 'year']).reset_index(drop=True)
    lag_cols = ['fips', 'year']
    base = ['emp', 'hir', 'frmjbls', 'frmjblss', 'frmjbgns', 'emps', 'empend']
    for b in base:
        for q in (3, 4):
            c = f'{b}_q{q}'
            if c in wide.columns:
                lag_cols.append(c)
    prev = wide[lag_cols].copy().rename(columns={'year': 'prev_year'})
    rename = {c: f'{c}_lag' for c in prev.columns if c not in ('fips', 'prev_year')}
    prev = prev.rename(columns=rename)
    wide['prev_year'] = wide['year'] - 1
    merged = wide.merge(prev, on=['fips', 'prev_year'], how='left')
    merged['school_year'] = merged['year']
    for c in merged.columns:
        if c.startswith(('emp', 'hir', 'frmjbls', 'frmjbgns', 'emps', 'empend')):
            merged[c] = merged[c].astype('Float64')

    sum_hir = merged['hir_q3_lag'] + merged['hir_q4_lag'] + merged['hir_q1'] + merged['hir_q2']
    merged['leavers'] = sum_hir - (merged['emp_q2'] - merged['emp_q4_lag'])
    merged['emp_lag'] = merged['emp_q4_lag']

    # quarter-level vectors of FrmJbLsS and FrmJbLs
    merged['frmjblss_sy_sum'] = (merged['frmjblss_q3_lag'] + merged['frmjblss_q4_lag']
                                 + merged['frmjblss_q1'] + merged['frmjblss_q2'])
    merged['frmjblss_sy_avg'] = merged['frmjblss_sy_sum'] / 4.0
    merged['frmjbls_sy_sum'] = (merged['frmjbls_q3_lag'] + merged['frmjbls_q4_lag']
                                + merged['frmjbls_q1'] + merged['frmjbls_q2'])
    merged['frmjbgns_sy_sum'] = (merged['frmjbgns_q3_lag'] + merged['frmjbgns_q4_lag']
                                 + merged['frmjbgns_q1'] + merged['frmjbgns_q2'])

    # NNJF as paper baseline (current best): avg over 4 school-year quarters
    merged['nnjf'] = merged['frmjblss_sy_avg']
    merged['nnjf_per_100'] = 100.0 * merged['nnjf'] / merged['emp_lag']

    # number of quarters where FrmJbLsS was NaN or zero (suppression proxy)
    quarters = ['frmjblss_q3_lag', 'frmjblss_q4_lag', 'frmjblss_q1', 'frmjblss_q2']
    merged['n_nan_q'] = merged[quarters].isna().sum(axis=1)
    merged['n_zero_q'] = (merged[quarters].fillna(0) == 0).sum(axis=1)

    sy = merged[(merged['school_year'] >= 2001) & (merged['school_year'] <= 2024)].copy()
    return sy


def main() -> None:
    print('Loading and building wide panel...')
    wide = build_wide()
    sy = build_sy(wide)
    print(f'Built {len(sy):,} school-year rows')

    paper = {
        'N(2001-21)': 47884,
        'N(2020-24)': 11722,
        'N(2013-24)': 24001,
        'w-med pooled': 1.080,
        'w-mean pooled': 3.32,
        'med 2019': 0.43, 'med 2020': 0.51, 'med 2021': 0.31, 'med 2023': 0.40,
    }
    print('\nPaper targets:', paper)
    print()

    results = []
    # ------------------------------------------------------------------
    # Baseline
    # ------------------------------------------------------------------
    base = summarize(sy, 'BASELINE (no extra filter)')
    results.append(base)
    print('BASELINE'); print(fmt(base)); print()

    # ------------------------------------------------------------------
    # H1: Apply the 33% outlier rule on NNJF (analogous to turnover/leavers).
    # Drop county-years where NNJF differs from county-mean(NNJF) by >=33%.
    # ------------------------------------------------------------------
    s = sy.copy()
    cmean = s.groupby('fips')['nnjf'].transform('mean')
    dev = (s['nnjf'] - cmean).abs() / cmean
    s.loc[(dev >= 0.33) | cmean.isna() | (cmean == 0), 'nnjf_per_100'] = np.nan
    r = summarize(s, 'H1: 33% outlier rule on NNJF (county-mean)')
    results.append(r); print('H1: 33% outlier rule on NNJF'); print(fmt(r)); print()

    # ------------------------------------------------------------------
    # H2: Drop small denominators (emp_lag < 100). Tiny districts inflate rates.
    # ------------------------------------------------------------------
    s = sy.copy()
    s.loc[s['emp_lag'] < 100, 'nnjf_per_100'] = np.nan
    r = summarize(s, 'H2: emp_lag >= 100')
    results.append(r); print('H2: emp_lag >= 100'); print(fmt(r)); print()

    # And the threshold matters — also try 200, 500, 1000
    for thresh in (200, 500, 1000):
        s = sy.copy()
        s.loc[s['emp_lag'] < thresh, 'nnjf_per_100'] = np.nan
        r = summarize(s, f'H2.{thresh}: emp_lag >= {thresh}')
        results.append(r); print(f'H2: emp_lag >= {thresh}'); print(fmt(r)); print()

    # ------------------------------------------------------------------
    # H3: Cap on rate — drop county-years where NNJF/100 > X%
    # ------------------------------------------------------------------
    for cap in (10, 5, 3):
        s = sy.copy()
        s.loc[s['nnjf_per_100'] > cap, 'nnjf_per_100'] = np.nan
        r = summarize(s, f'H3.{cap}: drop NNJF/100 > {cap}')
        results.append(r); print(f'H3: drop NNJF/100 > {cap}'); print(fmt(r)); print()

    # ------------------------------------------------------------------
    # H4: Drop any school-year with NaN in any of the 4 quarters (suppression).
    # ------------------------------------------------------------------
    s = sy.copy()
    s.loc[s['n_nan_q'] > 0, 'nnjf_per_100'] = np.nan
    r = summarize(s, 'H4: drop SYs with any NaN among 4 FrmJbLsS quarters')
    results.append(r); print('H4: all 4 quarters non-NaN'); print(fmt(r)); print()

    # ------------------------------------------------------------------
    # H5: Balanced panel — counties observed in every year 2001-2024
    # ------------------------------------------------------------------
    cy_counts = sy.dropna(subset=['nnjf', 'emp_lag']).groupby('fips')['school_year'].nunique()
    full_fips = cy_counts[cy_counts >= (2024 - 2001 + 1)].index
    s = sy.copy()
    s.loc[~s['fips'].isin(full_fips), 'nnjf_per_100'] = np.nan
    r = summarize(s, f'H5: balanced panel (counties w/ all 24 yrs, n={len(full_fips)})')
    results.append(r); print(f'H5: balanced panel n_counties={len(full_fips)}'); print(fmt(r)); print()

    # ------------------------------------------------------------------
    # H6 (bonus): use FrmJbLsS-sum (not avg) — paper Eq 3 says sum of 4 quarters,
    # but compare denominator on 4*emp_lag. (NNJF/100 = sum / (4*emp)*100 same as avg/emp*100)
    # Already same. Try instead: per-100 of EmpS_lag (stable emp) as denom.
    # ------------------------------------------------------------------
    s = sy.copy()
    if 'emps_q4_lag' in s.columns:
        s['nnjf_per_100'] = 100.0 * s['nnjf'] / s['emps_q4_lag']
        r = summarize(s, 'H6: rate normalized by EmpS (stable emp) Q4-lag')
        results.append(r); print('H6: denom = EmpS_q4_lag'); print(fmt(r)); print()

    # ------------------------------------------------------------------
    # H7: combine the most promising — 33% outlier rule + small-denom drop.
    # ------------------------------------------------------------------
    s = sy.copy()
    cmean = s.groupby('fips')['nnjf'].transform('mean')
    dev = (s['nnjf'] - cmean).abs() / cmean
    out_mask = (dev >= 0.33) | cmean.isna() | (cmean == 0)
    s.loc[out_mask | (s['emp_lag'] < 100), 'nnjf_per_100'] = np.nan
    r = summarize(s, 'H7: combine 33%-NNJF + emp_lag>=100')
    results.append(r); print('H7: combined 33% rule + emp_lag>=100'); print(fmt(r)); print()

    # ------------------------------------------------------------------
    # H8: drop counties where FrmJbLs > FrmJbGn always (constant net job-shedders)
    # ------------------------------------------------------------------
    # implausibly high churn: ratio of avg FrmJbLs / avg FrmJbGn > some threshold
    s = sy.copy()
    ratio = s.groupby('fips').apply(
        lambda g: (g['frmjbls_sy_sum'].mean() / g['frmjbgns_sy_sum'].replace(0, np.nan).mean())
        if g['frmjbgns_sy_sum'].notna().any() else np.nan
    )
    high_churn = ratio[ratio > 1.5].index
    s.loc[s['fips'].isin(high_churn), 'nnjf_per_100'] = np.nan
    r = summarize(s, f'H8: drop counties w/ FrmJbLs/FrmJbGn > 1.5 mean (n={len(high_churn)})')
    results.append(r); print(f'H8: high-churn drop n={len(high_churn)}'); print(fmt(r)); print()

    # ------------------------------------------------------------------
    # H9: drop county-years with zero in any FrmJbLsS quarter (suppression+true-zero)
    # ------------------------------------------------------------------
    s = sy.copy()
    s.loc[s['n_zero_q'] >= 2, 'nnjf_per_100'] = np.nan
    r = summarize(s, 'H9: drop SYs with 2+ zero quarters')
    results.append(r); print('H9: drop 2+ zero quarters'); print(fmt(r)); print()

    # ------------------------------------------------------------------
    # H10 (bonus): 33% outlier rule on NNJF (county-mean) computed on
    # post-2012 sub-period only (to address the 5K gap in 2013-24 sample)
    # ------------------------------------------------------------------
    s = sy.copy()
    s13 = s[s['school_year'] >= 2013]
    cmean = s13.groupby('fips')['nnjf'].transform('mean')
    dev = (s13['nnjf'] - cmean).abs() / cmean
    s13_drop_idx = s13[(dev >= 0.33) | cmean.isna() | (cmean == 0)].index
    s.loc[s13_drop_idx, 'nnjf_per_100'] = np.nan
    r = summarize(s, 'H10: 33% rule using 2013+ county-mean')
    results.append(r); print('H10: 33% rule 2013+ county-mean'); print(fmt(r)); print()

    # ------------------------------------------------------------------
    # Save table
    # ------------------------------------------------------------------
    rdf = pd.DataFrame(results)
    rdf.to_csv(REPL / 'output/reports/agent_filters_results.csv', index=False)
    print('\nSaved results table.\nPaper:', paper)
    print(rdf[['label', 'n_2013_2024', 'wmed_pooled', 'med_2019', 'med_2020',
              'med_2021', 'med_2023']].to_string(index=False))


if __name__ == '__main__':
    main()
