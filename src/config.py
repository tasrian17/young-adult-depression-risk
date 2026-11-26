"""Project-wide constants: NHANES cycles, analysis periods, components and paths.

Every file name used by the pipeline is read from the CDC listing pages
(see ``src/download.py``). This module only says which cycles and which
components we want, and how cycles group into the three analysis periods
defined in CLAUDE.md Section 5.1.
"""

from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "data"
RAW_NHANES_DIR = DATA_DIR / "raw" / "nhanes"
MANIFEST_PATH = DATA_DIR / "nhanes_manifest.csv"
AVAILABILITY_PATH = DATA_DIR / "nhanes_availability.csv"
FILE_SUMMARY_PATH = DATA_DIR / "nhanes_file_summary.csv"
REVISIONS_LOG_PATH = DATA_DIR / "nhanes_revisions.log"

CDC_BASE_URL = "https://wwwn.cdc.gov"
CDC_LISTING_URL = CDC_BASE_URL + "/nchs/nhanes/search/datapage.aspx"

# Analysis periods (CLAUDE.md Section 5.1). "recent" is the locked test set
# for the predictive models (CLAUDE.md Section 6, rule 2).
PERIOD_EARLIER = "earlier"
PERIOD_PRE_PANDEMIC = "pre_pandemic"
PERIOD_RECENT = "recent"
PERIOD_LABELS = {
    PERIOD_EARLIER: "2005-2016",
    PERIOD_PRE_PANDEMIC: "2017-March 2020",
    PERIOD_RECENT: "Aug 2021-Aug 2023",
}


@dataclass(frozen=True)
class Cycle:
    """One NHANES release and how its files are named on the CDC site.

    ``name`` is the value the CDC listing page takes as its ``Cycle``
    parameter. A file for component ``X`` is ``{prefix}X{suffix}``.
    """

    name: str
    period: str
    prefix: str
    suffix: str

    def file_name(self, component: str) -> str:
        """Return the CDC file name (without extension) for a component."""
        return f"{self.prefix}{component}{self.suffix}"


# 2017-2018 (suffix _J) is deliberately absent: the 2017-March 2020
# pre-pandemic files (prefix P_) already contain those participants.
CYCLES = (
    Cycle("2005-2006", PERIOD_EARLIER, "", "_D"),
    Cycle("2007-2008", PERIOD_EARLIER, "", "_E"),
    Cycle("2009-2010", PERIOD_EARLIER, "", "_F"),
    Cycle("2011-2012", PERIOD_EARLIER, "", "_G"),
    Cycle("2013-2014", PERIOD_EARLIER, "", "_H"),
    Cycle("2015-2016", PERIOD_EARLIER, "", "_I"),
    Cycle("2017-2020", PERIOD_PRE_PANDEMIC, "P_", ""),
    Cycle("2021-2023", PERIOD_RECENT, "", "_L"),
)
CYCLES_BY_NAME = {c.name: c for c in CYCLES}

# Component base names (CLAUDE.md Section 5.1), grouped by the CDC listing
# page they appear on. Some are alternatives that only exist in some cycles
# (BPX vs BPXO, CRP vs HSCRP); the availability table records which.
COMPONENTS_BY_PAGE = {
    "Demographics": ("DEMO",),
    "Questionnaire": (
        "DPQ", "SLQ", "SMQ", "ALQ", "PAQ", "MCQ", "DIQ", "HIQ", "HUQ",
        "FSQ", "RXQ_RX",
    ),
    "Examination": ("BMX", "BPX", "BPXO"),
    "Laboratory": ("GHB", "TCHOL", "HSCRP", "CRP"),
}

# The nine PHQ-9 items. DPQ100 (difficulty) is never part of the score.
PHQ9_ITEMS = tuple(f"DPQ0{i}0" for i in range(1, 10))

# Files where one participant can have several rows (one per medication).
MULTI_ROW_COMPONENTS = ("RXQ_RX",)


def period_of(cycle_name: str) -> str:
    """Return the analysis period ("earlier", "pre_pandemic", "recent") of a cycle."""
    return CYCLES_BY_NAME[cycle_name].period
