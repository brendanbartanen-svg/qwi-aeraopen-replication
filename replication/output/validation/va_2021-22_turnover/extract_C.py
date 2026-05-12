"""Extract Table J-2 (teacher turnover) from JLARC Report 568 using pdfplumber text extraction + regex."""
import csv
import re
import pdfplumber

PDF_PATH = '/Users/yvp3tf/Documents/CC Sandbox/replication/qwi_aeraopen/replication/data/raw/state_validation/va_jlarc_rpt568_pandemic_impact.pdf'
OUT_CSV = '/Users/yvp3tf/Documents/CC Sandbox/replication/qwi_aeraopen/replication/output/validation/va_2021-22_turnover/extract_C_textregex.csv'

# Table J-2 spans pages 157-161 (1-indexed). Start capturing after the header
# "Division SY21 and SY22 SY21 and SY22 departing per year change"
# Stop at "SOURCE:" footer.

# Regex for normal data rows:
#   <name>  <int_count>  <pct>%  <pct>%  <signed_pct>%
# Special row (Charlotte): "Charlotte 120 n.a. n.a. n.a."
NORMAL_ROW = re.compile(
    r'^(?P<name>[A-Za-z][A-Za-z .\-]+?)\s+'
    r'(?P<count>\d+)\s+'
    r'(?P<pct1>-?\d+%)\s+'
    r'(?P<pct2>-?\d+%)\s+'
    r'(?P<pct3>-?\d+%)\s*$'
)
NA_ROW = re.compile(
    r'^(?P<name>[A-Za-z][A-Za-z .\-]+?)\s+'
    r'(?P<count>\d+)\s+'
    r'n\.a\.\s+n\.a\.\s+n\.a\.\s*$'
)

rows = []
with pdfplumber.open(PDF_PATH) as pdf:
    in_table = False
    for i in range(156, 161):  # pages 157-161 (0-indexed 156-160)
        text = pdf.pages[i].extract_text() or ''
        for line in text.split('\n'):
            line = line.strip()
            if not line:
                continue
            # Detect end of table
            if line.startswith('SOURCE:') or line.startswith('NOTE:') or line.startswith('Teacher quality'):
                in_table = False
                continue
            # Detect start: header row ends with "departing per year change"
            if 'departing per year change' in line:
                in_table = True
                continue
            # Skip "Appendixes" header and other non-data lines
            if not in_table:
                # Pre-table content on page 157 — start capturing once we see
                # the first division row "Accomack County 62 21% 14% 7%"
                pass
            m = NORMAL_ROW.match(line)
            if m:
                rows.append({
                    'school_division': m.group('name').strip(),
                    'num_departing_sy21_to_sy22': m.group('count'),
                    'pct_departing_sy21_to_sy22': m.group('pct1'),
                    'pre_pandemic_avg_pct_departing': m.group('pct2'),
                    'pct_point_change': m.group('pct3'),
                })
                continue
            m = NA_ROW.match(line)
            if m:
                rows.append({
                    'school_division': m.group('name').strip(),
                    'num_departing_sy21_to_sy22': m.group('count'),
                    'pct_departing_sy21_to_sy22': 'n.a.',
                    'pre_pandemic_avg_pct_departing': 'n.a.',
                    'pct_point_change': 'n.a.',
                })

# Deduplicate (in case J-1 vacancy rows match the pattern). J-1 has 4 numeric
# columns (PPA float, SY22 float, pct, pct_change). The float values like
# "5.8" won't match \d+ for count, and J-1 pct_change can be 1,344% (has comma)
# while J-2 pct_point_change is a small integer percentage. To be safe, filter
# by page range above (we only look at pages 157-161).

with open(OUT_CSV, 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=[
        'school_division',
        'num_departing_sy21_to_sy22',
        'pct_departing_sy21_to_sy22',
        'pre_pandemic_avg_pct_departing',
        'pct_point_change',
    ])
    writer.writeheader()
    writer.writerows(rows)

print(f"Wrote {len(rows)} rows to {OUT_CSV}")
# Show first/last few rows for sanity
for r in rows[:3]:
    print(r)
print('...')
for r in rows[-3:]:
    print(r)
