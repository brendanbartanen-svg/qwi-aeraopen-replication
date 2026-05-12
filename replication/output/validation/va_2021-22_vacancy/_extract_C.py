"""Extract VA JLARC Report 568 Appendix J-1 vacancy table via text+regex."""
import csv
import re
import pdfplumber

PDF = "/Users/yvp3tf/Documents/CC Sandbox/replication/qwi_aeraopen/replication/data/raw/state_validation/va_jlarc_rpt568_pandemic_impact.pdf"
OUT = "/Users/yvp3tf/Documents/CC Sandbox/replication/qwi_aeraopen/replication/output/validation/va_2021-22_vacancy/extract_C_textregex.csv"

# Table J-1 spans pages 153-157 (1-indexed). Page 153 has the header lines, page 157 ends with a SOURCE line.
PAGES_1IDX = [153, 154, 155, 156, 157]

# Each data row pattern (4 numeric columns at the end):
#   <division name (letters/spaces/hyphens/apostrophes)> <PPA float> <SY22 float> <pct vacant int>% <pct change int|'-'>%?
# Examples seen:
#   "Accomack County 5.8 12.0 3% 107%"
#   "Bristol City 0.0 0.0 0%"          -> missing pct_change (blank)
#   "Nelson County 0.0 1.7 1% -"       -> pct_change literally "-"
#   "Salem City 0.0 0.0 0% -"
#   "Lynchburg City 0.6 29.3 5% 4,783%" -> commas inside pct_change
ROW_RE = re.compile(
    r"^(?P<name>[A-Za-z][A-Za-z .'\-]+?)\s+"
    r"(?P<ppa>\d+\.\d+)\s+"
    r"(?P<sy22>\d+\.\d+)\s+"
    r"(?P<pct_vac>\d+)%"
    r"(?:\s+(?P<pct_chg>-?[\d,]+%|-))?\s*$"
)


def parse_pages():
    rows = []
    with pdfplumber.open(PDF) as pdf:
        for pno in PAGES_1IDX:
            text = pdf.pages[pno - 1].extract_text() or ""
            for line in text.splitlines():
                line = line.strip()
                if not line:
                    continue
                # Skip non-row lines: header, footer, SOURCE/NOTE
                if line.startswith(("Appendix", "TABLE", "SOURCE", "NOTE", "Teacher",
                                     "This appendix", "The Virginia", "each year",
                                     "the Positions", "For both", "*PPA", "Division",
                                     "PPA*", "Appendixes")):
                    continue
                m = ROW_RE.match(line)
                if not m:
                    continue
                name = m.group("name").strip()
                # filter out caption fragments that happen to end in numbers
                if name.lower().startswith(("number of", "this appendix")):
                    continue
                ppa = m.group("ppa")
                sy22 = m.group("sy22")
                pct_vac = m.group("pct_vac") + "%"
                pct_chg = m.group("pct_chg")
                if pct_chg is None:
                    pct_chg = ""  # blank in PDF (e.g., Bristol City, Buckingham County)
                rows.append((name, ppa, sy22, pct_vac, pct_chg))
    return rows


def main():
    rows = parse_pages()
    with open(OUT, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow([
            "school_division", "pre_pandemic_avg_vacancies",
            "num_vacant_sy22", "pct_vacant_sy22", "pct_change_from_ppa",
        ])
        w.writerows(rows)
    print(f"wrote {len(rows)} rows -> {OUT}")
    # print first/last few for sanity
    for r in rows[:3]:
        print(r)
    print("...")
    for r in rows[-3:]:
        print(r)


if __name__ == "__main__":
    main()
