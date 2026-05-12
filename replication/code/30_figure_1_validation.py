"""Figure 1: Validation of QWI measures against state administrative data.

Now uses (per sub-agent state-data hunts):
  - CO 2021-22 and 2022-23 turnover XLSX (Wayback) ← Panel A, B, C
  - PA 2021-22 and 2022-23 termination + prof_staff XLSX ← Panel A, B, C
  - VA 2021-22 and 2022-23 vacancy (JLARC PDFs) ← Panel D
  - MD skipped: only PDFs, 2022-23 LEA-level attrition missing
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from _config import DATA_DERIVED, FIGURES, OUTPUT, QWI_CURRENT_DIR


def load_ccd_lea_xwalk():
    """Build LEA → county FIPS crosswalk via NCES CCD + EDGE."""
    ccd = pd.read_csv("data/raw/ccd/ccd_lea_029_2324_w_1a_073124.csv",
                      low_memory=False, dtype={"LEAID": str, "ST_LEAID": str})
    edge = pd.read_parquet("data/raw/ccd/lea_to_county_2425.parquet")
    edge = edge[["LEAID", "CNTY", "NMCNTY"]].copy()
    edge["LEAID"] = edge["LEAID"].astype(str)
    ccd = ccd[["LEAID", "ST_LEAID", "ST", "LEA_NAME"]].merge(edge, on="LEAID", how="left")
    return ccd


# ===== Colorado =====
def load_co_turnover(year_label: str, file_path: str) -> pd.DataFrame:
    """Load CO LEA-level turnover for a school year. Uses positional access."""
    xl = pd.ExcelFile(file_path)
    # Try both sheet naming conventions
    sheet = "Organization" if "Organization" in xl.sheet_names else ("LEA Level" if "LEA Level" in xl.sheet_names else xl.sheet_names[0])
    # Header row differs across vintages — find it
    for h in [2, 3, 4]:
        try:
            df = pd.read_excel(xl, sheet_name=sheet, header=h)
            if any("District Code" in str(c) or "LEA Code" in str(c) for c in df.columns):
                break
        except Exception:
            continue
    # Standard column structure:
    #  0: District Code, 1: District Name, 2: Position Category, 3: rural_status?,
    #  3-4: Year_t-1 Head Count, Year_t Head Count
    df.columns = [str(c).strip() for c in df.columns]
    # Find the two head-count columns and "People Left"
    hc_cols = [c for c in df.columns if "Head Count" in c or "Headcount" in c]
    pleft_col = next((c for c in df.columns if c.lower().startswith("people left")), None)
    poscat_col = next((c for c in df.columns if "Position" in c or "Category" in c), None)
    code_col = next((c for c in df.columns if c.lower().startswith("district code") or c.lower().startswith("lea code")), None)
    if not hc_cols or not pleft_col or not code_col:
        raise ValueError(f"Missing required columns in {file_path}: {df.columns.tolist()}")
    has_all_row = "All Job Categories" in df[poscat_col].unique()
    if has_all_row:
        df = df[df[poscat_col] == "All Job Categories"].copy()
    df["co_code"] = df[code_col].astype(str).str.strip().str.lstrip("0")
    # hc_cols ordered: prev year, current year
    df["hc_prev"] = pd.to_numeric(df[hc_cols[0]], errors="coerce")
    df["hc_curr"] = pd.to_numeric(df[hc_cols[1]], errors="coerce") if len(hc_cols) > 1 else np.nan
    df["leavers"] = pd.to_numeric(df[pleft_col], errors="coerce")
    df["state"] = "CO"
    df["year"] = year_label
    df = df[["co_code", "state", "year", "hc_prev", "hc_curr", "leavers"]]
    if not has_all_row:
        # Aggregate position categories per district
        df = df.groupby(["co_code", "state", "year"]).agg(
            hc_prev=("hc_prev", "sum"),
            hc_curr=("hc_curr", "sum"),
            leavers=("leavers", "sum"),
        ).reset_index()
    return df


def co_turnover_to_county(co_df: pd.DataFrame, ccd_xw: pd.DataFrame) -> pd.DataFrame:
    """Aggregate CO LEA data to county FIPS via NCES crosswalk."""
    xw = ccd_xw[ccd_xw["ST"] == "CO"][["ST_LEAID", "CNTY"]].copy()
    xw["co_code"] = xw["ST_LEAID"].str.replace("CO-", "", regex=False).str.lstrip("0")
    merged = co_df.merge(xw[["co_code", "CNTY"]], on="co_code", how="left")
    merged = merged.dropna(subset=["CNTY"])
    agg = merged.groupby(["CNTY", "year"]).agg(
        hc_prev=("hc_prev", "sum"),
        hc_curr=("hc_curr", "sum"),
        leavers=("leavers", "sum"),
        n_leas=("co_code", "count"),
    ).reset_index()
    agg["turnover_state"] = agg["leavers"] / agg["hc_prev"]
    agg = agg.rename(columns={"CNTY": "fips"})
    return agg


# ===== Pennsylvania =====
def load_pa_all_staff(file_path: str, sheet: str, year_label: str) -> pd.DataFrame:
    """Load PA computed all-staff turnover file (from PDE Individual Staff records).

    Columns include AUN, headcount_all, leaver_all, turnover_all (leavers+movers),
    turnover_rate_all, etc. The 'turnover_all' is the proper full-turnover definition
    (matches paper's turnover concept = anyone who left the district).
    """
    df = pd.read_excel(file_path, sheet_name=sheet, header=7)
    df["DISTRICT_CODE"] = df["AUN"].astype(str).str.replace(r"\.0$","",regex=True)
    df["staff_ct"] = pd.to_numeric(df["headcount_all"], errors="coerce")
    # Use turnover_all (leavers + movers) to match paper's "people who left their district"
    df["leavers"] = pd.to_numeric(df["turnover_all"], errors="coerce")
    df["ORG_TYPE"] = ""
    df["COUNTY_CD"] = ""
    df["year"] = year_label
    return df[["DISTRICT_CODE", "ORG_TYPE", "COUNTY_CD", "leavers", "staff_ct", "year"]]


def load_pa_retention(file_path: str, year_label: str) -> pd.DataFrame:
    """Load PA classroom-teacher retention file → district-level total CT, retained, leavers.

    Turnover = (GROUP_SIZE - N RETAINED CT) / GROUP_SIZE = full turnover rate
    """
    df = pd.read_excel(file_path, sheet_name="All", header=0)
    df = df[df["GROUP"] == "ALL CT"].copy() if "GROUP" in df.columns else df.copy()
    df["DISTRICT_CODE"] = df["DISTRICT_KEY"].astype(str).str.replace(r"\.0$","",regex=True)
    df["staff_ct"] = pd.to_numeric(df["GROUP_SIZE"], errors="coerce")
    df["retained_ct"] = pd.to_numeric(df["N RETAINED CT"], errors="coerce")
    df["leavers"] = df["staff_ct"] - df["retained_ct"]
    df["year"] = year_label
    df["ORG_TYPE"] = df.get("ORG_TYPE_LONG", "")
    df["COUNTY_CD"] = df.get("COUNTY_CODE", "")
    return df[["DISTRICT_CODE", "ORG_TYPE", "COUNTY_CD", "leavers", "staff_ct", "year"]]


def load_pa_termination(file_path: str, year_label: str) -> pd.DataFrame:
    """Load PA district-level total leavers for a school year."""
    df = pd.read_excel(file_path, sheet_name=year_label, header=1)
    df = df[df["DISTRICT_CODE"].notna()].copy()
    df["DISTRICT_CODE"] = df["DISTRICT_CODE"].astype(str).str.replace(r"\.0$", "", regex=True)
    df["COUNT"] = pd.to_numeric(df["COUNT"], errors="coerce")
    # Sum leavers across termination codes per district
    agg = df.groupby(["DISTRICT_CODE", "ORG_TYPE", "COUNTY_CD"]).agg(
        leavers=("COUNT", "sum")
    ).reset_index()
    agg["year"] = year_label
    return agg


def load_pa_staff(file_path: str) -> pd.DataFrame:
    """Load PA LEA-level total full-time staff (Classroom Teachers as primary)."""
    # Header row in row 5 (0-indexed) for both 2021-22 and 2022-23 prof staff files
    df = pd.read_excel(file_path, sheet_name="LEA_FT+PT", header=5)
    df.columns = [str(c).strip() for c in df.columns]
    df = df.rename(columns={df.columns[0]: "AUN"})
    df["AUN"] = df["AUN"].astype(str).str.replace(r"\.0$", "", regex=True).str.strip()
    # CT = classroom teachers count (total)
    if "CT" in df.columns:
        df["staff_ct"] = pd.to_numeric(df["CT"], errors="coerce")
    else:
        # Try to find column with classroom teacher counts
        ct_col = next((c for c in df.columns if str(c).strip().upper() == "CT"), None)
        if ct_col:
            df["staff_ct"] = pd.to_numeric(df[ct_col], errors="coerce")
        else:
            df["staff_ct"] = np.nan
    return df[["AUN", "staff_ct"]]


def pa_to_county(panel: pd.DataFrame, staff_df: pd.DataFrame | None, ccd_xw: pd.DataFrame) -> pd.DataFrame:
    """Aggregate PA district-level (panel has leavers + optional staff_ct) to county FIPS.

    If `panel` already has staff_ct (e.g. retention file), staff_df is ignored.
    """
    xw = ccd_xw[ccd_xw["ST"] == "PA"][["LEAID", "ST_LEAID", "CNTY", "LEA_NAME"]].copy()
    xw["AUN"] = xw["ST_LEAID"].str.replace("PA-", "", regex=False)
    if "staff_ct" not in panel.columns and staff_df is not None:
        m = panel.merge(staff_df, left_on="DISTRICT_CODE", right_on="AUN", how="left")
    else:
        m = panel.copy()
        m["AUN"] = m["DISTRICT_CODE"]
    m = m.merge(xw[["AUN", "CNTY"]], on="AUN", how="left")
    m = m.dropna(subset=["CNTY"])
    agg = m.groupby(["CNTY", "year"]).agg(
        leavers=("leavers", "sum"),
        hc_curr=("staff_ct", "sum"),
        n_leas=("AUN", "count"),
    ).reset_index()
    agg["turnover_state"] = agg["leavers"] / agg["hc_curr"]
    agg = agg.rename(columns={"CNTY": "fips"})
    return agg


# ===== Maryland =====
MD_LEA_TO_FIPS = {
    "Allegany":"24001", "Anne Arundel":"24003", "Baltimore City":"24510", "Baltimore County":"24005",
    "Calvert":"24009", "Caroline":"24011", "Carroll":"24013", "Cecil":"24015", "Charles":"24017",
    "Dorchester":"24019", "Frederick":"24021", "Garrett":"24023", "Harford":"24025", "Howard":"24027",
    "Kent":"24029", "Montgomery":"24031", "Prince George's":"24033", "Queen Anne's":"24035",
    "St. Mary's":"24037", "Somerset":"24039", "Talbot":"24041", "Washington":"24043",
    "Wicomico":"24045", "Worcester":"24047",
}


def load_md_attrition(file_path: str, year_label: str) -> pd.DataFrame:
    """MD has turnover rates per LEA but no headcount; one row per LEA = one row per county."""
    df = pd.read_csv(file_path)
    # The rate column name varies — find it
    rate_col = next((c for c in df.columns if "did_not_return" in c or "pct" in c.lower()), None)
    df["turnover_state"] = pd.to_numeric(df[rate_col], errors="coerce") / 100.0
    df["fips"] = df["LEA"].map(MD_LEA_TO_FIPS)
    df = df.dropna(subset=["fips", "turnover_state"])
    df["state"] = "MD"
    df["year"] = year_label
    df["hc_curr"] = np.nan  # not available from the chart
    df["leavers"] = np.nan
    return df[["fips","state","year","hc_curr","leavers","turnover_state"]]


# ===== Virginia =====
def load_va_vacancy(file_path: str, year_label: str) -> pd.DataFrame:
    """Load VA division-level vacancy data. Column names differ across vintages."""
    df = pd.read_excel(file_path)
    df.columns = [c.lower().strip() for c in df.columns]
    rename = {"school_division": "division",
              "total_fte_teacher_positions": "fte_pos",
              "total_unfilled_fte": "vacant_fte",
              "vacancy_rate_pct": "vacancy_pct",
              # SY 2021-22 file uses different names
              "num_vacant_sy22": "vacant_fte",
              "pct_vacant_sy22": "vacancy_pct"}
    df = df.rename(columns=rename)
    for c in ["fte_pos", "vacant_fte", "vacancy_pct"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    df["year"] = year_label
    return df


def va_to_county(va_df: pd.DataFrame, ccd_xw: pd.DataFrame) -> pd.DataFrame:
    """Match VA divisions to county FIPS via name match to NCES LEA_NAME."""
    xw = ccd_xw[ccd_xw["ST"] == "VA"][["LEA_NAME", "CNTY"]].copy()
    # Normalize names
    def norm(s: str) -> str:
        s = str(s).lower().strip()
        s = re.sub(r"\b(public schools|school division|county|city)\b", "", s).strip()
        s = re.sub(r"\s+", " ", s)
        return s
    xw["name_norm"] = xw["LEA_NAME"].apply(norm)
    va_df = va_df.copy()
    va_df["name_norm"] = va_df["division"].apply(norm)
    merged = va_df.merge(xw[["name_norm", "CNTY"]], on="name_norm", how="left")
    # Some VA divisions: name like "Richmond City Public Schools" → match "Richmond City"
    # If no match, try first-word match
    unmatched_mask = merged["CNTY"].isna()
    if unmatched_mask.any():
        # Try just first word
        merged.loc[unmatched_mask, "name_norm2"] = merged.loc[unmatched_mask, "division"].str.lower().str.split().str[0]
        xw["name_first"] = xw["LEA_NAME"].str.lower().str.split().str[0]
        retry = merged[unmatched_mask].merge(xw[["name_first", "CNTY"]].drop_duplicates("name_first"),
                                              left_on="name_norm2", right_on="name_first", how="left")
        merged.loc[unmatched_mask, "CNTY"] = retry["CNTY_y"].values if "CNTY_y" in retry.columns else retry["CNTY"].values
    merged = merged.dropna(subset=["CNTY"])
    agg = merged.groupby(["CNTY", "year"]).agg(
        fte_pos=("fte_pos", "sum"),
        vacant_fte=("vacant_fte", "sum"),
        n_divisions=("division", "count"),
    ).reset_index()
    agg = agg.rename(columns={"CNTY": "fips"})
    return agg


# ===== Main =====
def main() -> None:
    FIGURES.mkdir(parents=True, exist_ok=True)
    ccd_xw = load_ccd_lea_xwalk()

    # CO
    co1 = load_co_turnover("2021-22", "data/raw/state_validation/co_2021-22_turnover.xlsx")
    co2 = load_co_turnover("2022-23", "data/raw/state_validation/co_2022-23_turnover.xlsx")
    co3 = load_co_turnover("2024-25", "data/raw/state_validation/co_2025-26_turnover.xlsx")
    co = pd.concat([co1, co2, co3], ignore_index=True)
    co_county = co_turnover_to_county(co, ccd_xw)
    co_county["state"] = "CO"
    print(f"CO county-years: {len(co_county)}")

    # MD — only turnover rate available (no headcount/leaver counts) from MSDE TWS reports
    md_panels = []
    md1 = load_md_attrition("data/raw/state_validation/md_2020-21_to_2021-22_LEA_attrition_TWS-2022_p7.csv", "2021-22")
    md_panels.append(md1)
    md2 = load_md_attrition("data/raw/state_validation/md_2022-23_to_2023-24_LEA_attrition_TWS-2024_p11.csv", "2023-24")
    md_panels.append(md2)
    md_county = pd.concat(md_panels, ignore_index=True)
    md_county["n_leas"] = 1
    print(f"MD county-years: {len(md_county)}")

    # PA — use the all-staff turnover file computed from PDE Individual Staff records
    # This is the proper apples-to-apples match with CO (all-staff, not just CT)
    pa_panels = []
    pa_all_22 = load_pa_all_staff(
        "data/raw/state_validation/pa_all_staff_turnover_computed.xlsx",
        "Turnover_2021-22_to_2022-23", "2021-22")
    pa_panels.append(pa_to_county(pa_all_22, None, ccd_xw))
    pa_all_23 = load_pa_all_staff(
        "data/raw/state_validation/pa_all_staff_turnover_computed.xlsx",
        "Turnover_2022-23_to_2023-24", "2022-23")
    pa_panels.append(pa_to_county(pa_all_23, None, ccd_xw))
    if pa_panels:
        pa_county = pd.concat(pa_panels, ignore_index=True)
        pa_county["state"] = "PA"
        print(f"PA county-years: {len(pa_county)}")

    # VA
    va_files = [
        ("2021-22", "data/raw/state_validation/va_2021-22_vacancy.xlsx"),
        ("2022-23", "data/raw/state_validation/va_2022-23_vacancy.xlsx"),
        ("2023-24", "data/raw/state_validation/va_2023-24_vacancy.xlsx"),
    ]
    va_dfs = [load_va_vacancy(p, y) for y, p in va_files]
    va = pd.concat(va_dfs, ignore_index=True)
    va_county = va_to_county(va, ccd_xw)
    va_county["state"] = "VA"
    print(f"VA county-years: {len(va_county)}")

    # Save the state-side panel — combine CO + PA (have full data) + MD (turnover only)
    state_panel = pd.concat([co_county, pa_county, md_county], ignore_index=True, sort=False)
    state_panel.to_parquet(DATA_DERIVED / "state_validation_panel.parquet")
    va_county.to_parquet(DATA_DERIVED / "va_vacancy_county.parquet")
    print(f"\nCombined CO+PA panel: {len(state_panel)} county-years")
    print(state_panel.head())
    print()
    print(va_county.head())

    # Load my QWI measures (need school years 2022, 2023, 2024, 2025)
    sy = pd.read_parquet(DATA_DERIVED / "county_school_year_measures.parquet")
    sy["year_label"] = sy["school_year"].apply(lambda y: f"{y-1}-{str(y)[-2:]}")
    sy["state"] = sy["fips"].str[:2]
    sy["emp_lag"] = pd.to_numeric(sy["emp_lag"], errors="coerce")
    sy["turnover"] = pd.to_numeric(sy["turnover"], errors="coerce")
    sy["nnjf"] = pd.to_numeric(sy["nnjf"], errors="coerce")
    sy["leavers"] = pd.to_numeric(sy["leavers"], errors="coerce")

    # Merge CO+PA panel with QWI
    state_panel["fips"] = state_panel["fips"].astype(str)
    merged = state_panel.merge(sy[["fips","year_label","turnover","leavers","emp_lag","nnjf"]],
                                left_on=["fips","year"], right_on=["fips","year_label"], how="inner",
                                suffixes=("_state","_qwi"))
    merged = merged.dropna(subset=["turnover_state","turnover","emp_lag","leavers_qwi"])
    print(f"\nMerged CO+PA validation: {len(merged)} obs")

    # Compute correlations
    state_lev_col = "leavers_state"
    qwi_lev_col = "leavers_qwi"
    # Coerce everything to float
    for c in ["hc_curr", "emp_lag", state_lev_col, qwi_lev_col, "turnover_state", "turnover"]:
        merged[c] = pd.to_numeric(merged[c], errors="coerce")

    # Turnover panel uses ALL valid obs (including MD which has no hc/leaver counts)
    turn_panel = merged.dropna(subset=["turnover_state", "turnover", "emp_lag"])
    turn_panel = turn_panel[(turn_panel["emp_lag"] > 0) & np.isfinite(turn_panel["turnover"])
                              & np.isfinite(turn_panel["turnover_state"])]

    # Emp/leavers panel excludes MD (no hc/leaver counts)
    cnt_panel = merged.dropna(subset=["hc_curr", "emp_lag", state_lev_col, qwi_lev_col])
    cnt_panel = cnt_panel[(cnt_panel["emp_lag"] > 0) & (cnt_panel["hc_curr"] > 0)]
    print(f"Post-cleanup N = {len(cnt_panel)} (emp/leavers); {len(turn_panel)} (turnover, incl. MD)")

    r_emp = np.corrcoef(cnt_panel["hc_curr"], cnt_panel["emp_lag"])[0,1]
    r_lev = np.corrcoef(cnt_panel[state_lev_col], cnt_panel[qwi_lev_col])[0,1]
    r_to = np.corrcoef(turn_panel["turnover_state"], turn_panel["turnover"])[0,1]

    # Also compute log-log correlations
    r_emp_log = np.corrcoef(np.log(cnt_panel["hc_curr"]), np.log(cnt_panel["emp_lag"]))[0, 1]
    r_lev_log = np.corrcoef(np.log(cnt_panel[state_lev_col] + 1), np.log(cnt_panel[qwi_lev_col] + 1))[0, 1]
    merged = turn_panel  # for downstream code expecting `merged`

    print(f"\n=== Validation correlations (CO+PA combined, {merged['state'].nunique()} states) ===")
    print(f"Total Employment:  linear R = {r_emp:.4f}   log-log R = {r_emp_log:.4f}  (paper: 0.91)")
    print(f"Leavers:           linear R = {r_lev:.4f}   log-log R = {r_lev_log:.4f}  (paper: 0.85)")
    print(f"Turnover:          linear R = {r_to:.4f}                          (paper: 0.89)")

    # VA — NNJF validation
    va_county["fips"] = va_county["fips"].astype(str)
    va_merged = va_county.merge(sy[["fips","year_label","nnjf"]],
                                  left_on=["fips","year"], right_on=["fips","year_label"], how="inner")
    va_merged["vacant_fte"] = pd.to_numeric(va_merged["vacant_fte"], errors="coerce")
    va_merged["nnjf"] = pd.to_numeric(va_merged["nnjf"], errors="coerce")
    va_merged = va_merged.dropna(subset=["vacant_fte","nnjf"])
    va_merged = va_merged[(va_merged["vacant_fte"] >= 0) & (va_merged["nnjf"] >= 0)]
    # Drop divisions that report zero vacancies AND we have no NNJF observations (likely missing data)
    va_nz = va_merged[va_merged["vacant_fte"] > 0]
    print(f"\nVA NNJF validation: {len(va_merged)} county-years total; {len(va_nz)} with non-zero vacancy")
    if len(va_nz) >= 2:
        r_nnjf = np.corrcoef(va_nz["vacant_fte"], va_nz["nnjf"])[0,1]
        r_nnjf_log = np.corrcoef(np.log(va_nz["vacant_fte"]), np.log(va_nz["nnjf"]+1))[0,1]
        print(f"NNJF vs vacancies (non-zero only): linear R = {r_nnjf:.4f}   log-log R = {r_nnjf_log:.4f}  (paper: 0.84)")
    else:
        r_nnjf = r_nnjf_log = np.nan
    # Also compute by year
    for yr, sub in va_nz.groupby("year"):
        if len(sub) < 5: continue
        r_yr = np.corrcoef(sub["vacant_fte"], sub["nnjf"])[0,1]
        print(f"  {yr}: R = {r_yr:.4f} (n={len(sub)})")
    va_merged = va_nz  # use non-zero subset for the figure

    # ===== Build 4-panel figure =====
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))

    # Panel A: Total employment (log-log)
    ax = axes[0,0]
    for st_name, st_data in merged.groupby("state"):
        ax.scatter(st_data["hc_curr"], st_data["emp_lag"].astype(float),
                    label=st_name, alpha=0.6, s=25)
    xmax = max(merged["hc_curr"].max(), merged["emp_lag"].astype(float).max())
    ax.plot([10, xmax], [10, xmax], "--", color="gray", alpha=0.4, lw=1)
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlabel("Total Employment-State Records (log scale)")
    ax.set_ylabel("Total Employment-QWI Data (log scale)")
    ax.set_title("Panel A. Total Employment")
    ax.legend(fontsize=9)
    ax.text(0.05, 0.95, f"log-log R = {r_emp_log:.2f}\nlinear R = {r_emp:.2f}\nN = {len(merged)}\nStates: {', '.join(sorted(merged['state'].unique()))}",
             transform=ax.transAxes, fontsize=8, verticalalignment="top",
             bbox=dict(facecolor="white", edgecolor="black", boxstyle="round,pad=0.3"))

    # Panel B: Leavers (log-log)
    ax = axes[0,1]
    for st_name, st_data in merged.groupby("state"):
        ax.scatter(st_data[state_lev_col].astype(float) + 1, st_data[qwi_lev_col].astype(float) + 1,
                    label=st_name, alpha=0.6, s=25)
    ax.set_xlabel("Leavers-State Records (log scale)")
    ax.set_ylabel("Leavers-QWI Data (log scale)")
    ax.set_title("Panel B. Leavers")
    ax.set_xscale("log"); ax.set_yscale("log")
    xmax = max(merged[state_lev_col].max(), merged[qwi_lev_col].max())
    ax.plot([1, xmax], [1, xmax], "--", color="gray", alpha=0.4, lw=1)
    ax.legend(fontsize=9)
    ax.text(0.05, 0.95, f"log-log R = {r_lev_log:.2f}\nlinear R = {r_lev:.2f}\nN = {len(merged)}",
             transform=ax.transAxes, fontsize=8, verticalalignment="top",
             bbox=dict(facecolor="white", edgecolor="black", boxstyle="round,pad=0.3"))

    # Panel C: Turnover
    ax = axes[1,0]
    for st_name, st_data in merged.groupby("state"):
        ax.scatter(st_data["turnover_state"].astype(float)*100, st_data["turnover"].astype(float)*100,
                    label=st_name, alpha=0.6, s=25)
    ax.set_xlabel("Turnover-State Records (%)")
    ax.set_ylabel("Turnover-QWI Data (%)")
    ax.set_title("Panel C. Turnover")
    ax.set_xlim(0, 50); ax.set_ylim(0, 50)
    ax.plot([0, 50], [0, 50], "--", color="gray", alpha=0.4, lw=1)
    ax.legend(fontsize=9)
    ax.text(0.05, 0.95, f"R = {r_to:.2f}\nN = {len(merged)}",
             transform=ax.transAxes, fontsize=9, verticalalignment="top",
             bbox=dict(facecolor="white", edgecolor="black", boxstyle="round,pad=0.3"))

    # Panel D: NNJF vs Virginia vacancies
    ax = axes[1,1]
    if len(va_merged) >= 2:
        for yr, sub in va_merged.groupby("year"):
            ax.scatter(sub["vacant_fte"], sub["nnjf"],
                        alpha=0.6, s=25, label=f"VA {yr}")
        ax.set_xlabel("Teacher Vacancies-VA State Records")
        ax.set_ylabel("Net-Negative Job Flow-QWI Data")
        ax.set_title("Panel D. Net-Negative Job-Flow vs Vacancies")
        ax.legend(fontsize=8)
        ax.text(0.05, 0.95, f"linear R = {r_nnjf:.2f}\nlog-log R = {r_nnjf_log:.2f}\nN = {len(va_merged)}\n(paper: R=0.84)",
                 transform=ax.transAxes, fontsize=8, verticalalignment="top",
                 bbox=dict(facecolor="white", edgecolor="black", boxstyle="round,pad=0.3"))
    else:
        ax.text(0.5, 0.5, "VA NNJF validation\nN too small", ha="center", va="center",
                 transform=ax.transAxes)

    fig.suptitle("Figure 1. Validating QWI measures against state administrative data\n"
                  f"(CO + PA 2021-22, 2022-23 + VA 2021-22, 2022-23, 2023-24)", fontsize=12)
    fig.tight_layout()
    out_path = FIGURES / "figure_1_validation.png"
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    print(f"\nWrote {out_path}")

    # Save validation summary
    summary = pd.DataFrame({
        "construct": ["Total Employment", "Leavers", "Turnover", "NNJF vs Vacancies"],
        "paper_R": [0.91, 0.85, 0.89, 0.84],
        "paper_source": ["CO+MD+PA 2021-23", "CO+MD+PA 2021-23", "CO+MD+PA 2021-23", "VA 2021-23"],
        "my_R": [round(r_emp,4), round(r_lev,4), round(r_to,4), round(r_nnjf,4) if not np.isnan(r_nnjf) else None],
        "my_source": [f"CO+PA, n={len(merged)}", f"CO+PA, n={len(merged)}",
                       f"CO+PA, n={len(merged)}", f"VA, n={len(va_merged)}"],
    })
    summary.to_csv(OUTPUT / "tables" / "figure_1_validation_summary.csv", index=False)
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
