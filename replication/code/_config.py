"""Shared configuration: paths, API key loading, target values."""

from pathlib import Path
import os

REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_RAW = REPO_ROOT / "data" / "raw"
DATA_DERIVED = REPO_ROOT / "data" / "derived"
OUTPUT = REPO_ROOT / "output"
FIGURES = OUTPUT / "figures"
TABLES = OUTPUT / "tables"

QWI_CURRENT_DIR = DATA_RAW / "qwi_current"
QWI_VINTAGE_DIR = DATA_RAW / "qwi_vintage_2025q1"
STATE_VAL_DIR = DATA_RAW / "state_validation"
CCD_DIR = DATA_RAW / "ccd"
POLICY_DIR = DATA_RAW / "policy"

NAICS_K12 = "6111"
QWI_API_BASE = "https://api.census.gov/data/timeseries/qwi"

AUTHORS_EXTRACTION_DATE = "2025-03-05"
AUTHORS_LATEST_QUARTER = "2024-Q2"


def census_api_key() -> str:
    key = os.environ.get("CENSUS_API_KEY")
    if not key or key == "your_key_here":
        env_path = REPO_ROOT / ".env"
        if env_path.exists():
            for line in env_path.read_text().splitlines():
                line = line.strip()
                if line.startswith("CENSUS_API_KEY="):
                    key = line.split("=", 1)[1].strip().strip('"').strip("'")
                    break
    if not key or key == "your_key_here":
        raise RuntimeError(
            "Census API key not found. Add it to "
            f"{REPO_ROOT}/.env as CENSUS_API_KEY=... "
            "(get one at https://api.census.gov/data/key_signup.html)."
        )
    return key
