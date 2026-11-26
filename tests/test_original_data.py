"""Check that the course project's Kaggle CSV is exactly the file in MANIFEST.md.

If the file changes, every Aim 4 result built on it could change silently.
"""

import hashlib
import re
from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).resolve().parent.parent / "original_course_project" / "data"
CSV_PATH = DATA_DIR / "Student Depression Dataset.csv"
MANIFEST_PATH = DATA_DIR / "MANIFEST.md"


def manifest_sha256() -> str:
    """Return the SHA-256 recorded in MANIFEST.md."""
    match = re.search(r"SHA-256 \| `([0-9a-f]{64})`", MANIFEST_PATH.read_text())
    assert match, "MANIFEST.md has no SHA-256 entry"
    return match.group(1)


def test_checksum_matches_manifest():
    digest = hashlib.sha256(CSV_PATH.read_bytes()).hexdigest()
    assert digest == manifest_sha256()


def test_shape_and_missing_values():
    df = pd.read_csv(CSV_PATH)
    assert df.shape == (27901, 18)
    missing = df.isna().sum()
    assert missing.sum() == 3
    assert missing["Financial Stress"] == 3
