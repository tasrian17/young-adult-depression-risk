"""Tests for src/download.py and the cycle/period settings in src/config.py.

No network access: listing pages come from trimmed copies of real CDC pages
in tests/fixtures/, and downloads are replaced by a fake that writes bytes.
"""

from pathlib import Path

import pandas as pd
import pytest

from src import config, download

FIXTURES = Path(__file__).parent / "fixtures"


def load_listing(name: str) -> dict:
    """Parse a saved CDC listing page fixture."""
    return download.parse_listing((FIXTURES / name).read_text())


# ---------------------------------------------------------------- periods

def test_period_split_matches_claude_md():
    """Six earlier cycles, one pre-pandemic, one recent (the locked test set)."""
    by_period = {}
    for cycle in config.CYCLES:
        by_period.setdefault(cycle.period, []).append(cycle.name)
    assert by_period[config.PERIOD_EARLIER] == [
        "2005-2006", "2007-2008", "2009-2010", "2011-2012", "2013-2014", "2015-2016",
    ]
    assert by_period[config.PERIOD_PRE_PANDEMIC] == ["2017-2020"]
    assert by_period[config.PERIOD_RECENT] == ["2021-2023"]
    assert config.period_of("2021-2023") == config.PERIOD_RECENT


def test_no_2017_2018_cycle():
    """2017-2018 (_J) must not be used alongside the P_ files."""
    assert all(c.suffix != "_J" for c in config.CYCLES)
    assert "2017-2018" not in config.CYCLES_BY_NAME


def test_file_name_pattern_per_cycle():
    assert config.CYCLES_BY_NAME["2005-2006"].file_name("DPQ") == "DPQ_D"
    assert config.CYCLES_BY_NAME["2017-2020"].file_name("DPQ") == "P_DPQ"
    assert config.CYCLES_BY_NAME["2021-2023"].file_name("RXQ_RX") == "RXQ_RX_L"


def test_phq9_items_exclude_dpq100():
    assert config.PHQ9_ITEMS == (
        "DPQ010", "DPQ020", "DPQ030", "DPQ040", "DPQ050",
        "DPQ060", "DPQ070", "DPQ080", "DPQ090",
    )


# ---------------------------------------------------------------- listing

def test_parse_listing_with_years_column():
    """The 2017-2020 page has an extra 'Years' column; fields must not shift."""
    rows = load_listing("listing_questionnaire_2017-2020.html")
    dpq = rows["P_DPQ"]
    assert dpq["description"] == "Mental Health - Depression Screener"
    assert dpq["data_url"] == "https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2017/DataFiles/P_DPQ.xpt"
    assert dpq["doc_url"] == "https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2017/DataFiles/P_DPQ.htm"
    assert dpq["date_published"] == "June 2021"


def test_parse_listing_without_years_column():
    rows = load_listing("listing_laboratory_2015-2016.html")
    assert set(rows) == {"TCHOL_I", "GHB_I", "HSCRP_I"}
    assert all(r["date_published"] for r in rows.values())


def test_parse_listing_rejects_unknown_layout():
    html = "<table id='GridView1'><tr><th>Name</th><th>File</th></tr></table>"
    with pytest.raises(ValueError, match="lacks columns"):
        download.parse_listing(html)


def test_select_files_exact_names_only():
    """RXQ_DRUG, SMQFAM and PAQY look similar but must not be selected."""
    listing = load_listing("listing_questionnaire_2017-2020.html")
    cycle = config.CYCLES_BY_NAME["2017-2020"]
    picked = {r["component"]: r["file"] for r in download.select_files(listing, cycle, "Questionnaire")}
    assert picked == {"DPQ": "P_DPQ", "SLQ": "P_SLQ", "SMQ": "P_SMQ", "RXQ_RX": "P_RXQ_RX"}


def test_select_files_crp_is_not_hscrp():
    """Looking for CRP must not match HSCRP_I."""
    listing = load_listing("listing_laboratory_2015-2016.html")
    cycle = config.CYCLES_BY_NAME["2015-2016"]
    picked = {r["component"] for r in download.select_files(listing, cycle, "Laboratory")}
    assert picked == {"GHB", "TCHOL", "HSCRP"}


def test_select_files_refuses_j_suffix():
    bad = config.Cycle("2017-2018", config.PERIOD_PRE_PANDEMIC, "", "_J")
    with pytest.raises(ValueError, match="2017-2018"):
        download.select_files({}, bad, "Questionnaire")


# ---------------------------------------------------------------- fetching

XPT_BODY_V1 = download.XPT_MAGIC + b" version one"
XPT_BODY_V2 = download.XPT_MAGIC + b" version two"


@pytest.fixture
def sandbox(tmp_path, monkeypatch):
    """Point raw data and the revisions log at a temporary directory."""
    monkeypatch.setattr(config, "RAW_NHANES_DIR", tmp_path / "raw")
    monkeypatch.setattr(config, "REVISIONS_LOG_PATH", tmp_path / "revisions.log")
    return tmp_path


def fake_downloader(monkeypatch, body: bytes, calls: list):
    """Replace download_to with a function that writes ``body``."""
    def fake(session, url, dest):
        calls.append(url)
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(body)
        return "Wed, 08 Nov 2023 23:15:07 GMT"
    monkeypatch.setattr(download, "download_to", fake)


def one_row_manifest() -> pd.DataFrame:
    row = {c: "" for c in download.MANIFEST_COLUMNS}
    row.update(cycle="2021-2023", period="recent", page="Questionnaire",
               component="DPQ", file="DPQ_L", data_url="https://example/DPQ_L.xpt",
               cdc_date_published="September 2024")
    return pd.DataFrame([row])


def test_first_download_records_checksum_and_dates(sandbox, monkeypatch):
    calls = []
    fake_downloader(monkeypatch, XPT_BODY_V1, calls)
    m = one_row_manifest()
    status = download.fetch_one(None, m, 0, "2026-11-26", accept_revisions=False)
    assert status == "downloaded"
    assert m.loc[0, "sha256"] == download.sha256_of(sandbox / "raw" / "2021-2023" / "DPQ_L.xpt")
    assert m.loc[0, "downloaded_on"] == "2026-11-26"
    assert m.loc[0, "cdc_date_published_at_download"] == "September 2024"
    assert m.loc[0, "cdc_last_modified"] == "Wed, 08 Nov 2023 23:15:07 GMT"


def test_matching_file_is_not_downloaded_again(sandbox, monkeypatch):
    calls = []
    fake_downloader(monkeypatch, XPT_BODY_V1, calls)
    m = one_row_manifest()
    download.fetch_one(None, m, 0, "2026-11-26", accept_revisions=False)
    assert download.fetch_one(None, m, 0, "2026-11-27", accept_revisions=False) == "present"
    assert len(calls) == 1
    assert m.loc[0, "downloaded_on"] == "2026-11-26"


def test_corrupted_local_file_is_restored(sandbox, monkeypatch):
    calls = []
    fake_downloader(monkeypatch, XPT_BODY_V1, calls)
    m = one_row_manifest()
    download.fetch_one(None, m, 0, "2026-11-26", accept_revisions=False)
    path = sandbox / "raw" / "2021-2023" / "DPQ_L.xpt"
    path.write_bytes(b"damaged")
    assert download.fetch_one(None, m, 0, "2026-11-27", accept_revisions=False) == "restored"
    assert path.read_bytes() == XPT_BODY_V1
    assert len(calls) == 2


def test_changed_checksum_is_reported_as_possible_revision(sandbox, monkeypatch):
    calls = []
    fake_downloader(monkeypatch, XPT_BODY_V1, calls)
    m = one_row_manifest()
    download.fetch_one(None, m, 0, "2026-11-26", accept_revisions=False)
    old_sha = m.loc[0, "sha256"]
    path = sandbox / "raw" / "2021-2023" / "DPQ_L.xpt"
    path.unlink()  # a fresh session: no local copy

    fake_downloader(monkeypatch, XPT_BODY_V2, calls)
    status = download.fetch_one(None, m, 0, "2027-01-05", accept_revisions=False,
                                current_published=lambda row: "Updated January 2027")
    assert status == "possible_revision"
    assert m.loc[0, "sha256"] == old_sha  # recorded checksum unchanged
    assert not path.exists()
    assert path.with_suffix(".candidate").read_bytes() == XPT_BODY_V2
    log = (sandbox / "revisions.log").read_text()
    assert "may be a CDC revision" in log
    assert "Updated January 2027" in log and "September 2024" in log
    assert old_sha in log


def test_accepting_a_revision_updates_manifest(sandbox, monkeypatch):
    calls = []
    fake_downloader(monkeypatch, XPT_BODY_V1, calls)
    m = one_row_manifest()
    download.fetch_one(None, m, 0, "2026-11-26", accept_revisions=False)
    fake_downloader(monkeypatch, XPT_BODY_V2, calls)
    (sandbox / "raw" / "2021-2023" / "DPQ_L.xpt").unlink()
    status = download.fetch_one(None, m, 0, "2027-01-05", accept_revisions=True,
                                current_published=lambda row: "Updated January 2027")
    assert status == "revision_accepted"
    assert m.loc[0, "downloaded_on"] == "2027-01-05"
    assert m.loc[0, "cdc_date_published"] == "Updated January 2027"
    assert "ACCEPTED" in (sandbox / "revisions.log").read_text()


def test_html_error_page_is_rejected(tmp_path, monkeypatch):
    """A body that is not an XPT file must raise, not be saved as data."""
    class FakeResponse:
        headers = {}
        def raise_for_status(self):
            pass
        def iter_content(self, size):
            yield b"<html>Page not found</html>"

    class FakeSession:
        def get(self, url, timeout, stream):
            return FakeResponse()

    with pytest.raises(download.DownloadError, match="not a SAS transport"):
        download.download_to(FakeSession(), "https://example/x.xpt", tmp_path / "x.part")


# ---------------------------------------------------------------- manifest

def test_merge_keeps_recorded_checksums():
    new = one_row_manifest().drop(columns=download.CHECKSUM_COLUMNS)
    old = one_row_manifest()
    old.loc[0, "sha256"] = "abc"
    old.loc[0, "downloaded_on"] = "2026-11-26"
    merged = download.merge_checksums(new, old)
    assert merged.loc[0, "sha256"] == "abc"
    assert list(merged.columns) == download.MANIFEST_COLUMNS


def test_availability_table_marks_missing_components():
    m = pd.DataFrame([
        {"component": "BPX", "cycle": "2015-2016", "file": "BPX_I"},
        {"component": "BPXO", "cycle": "2021-2023", "file": "BPXO_L"},
    ])
    table = download.availability_table(m).set_index("component")
    assert table.loc["BPX", "2015-2016"] == "BPX_I"
    assert table.loc["BPX", "2021-2023"] == ""
    assert table.loc["BPXO", "2021-2023"] == "BPXO_L"


# ---------------------------------------------------------------- checks

def test_verify_reports_missing_file(sandbox, monkeypatch, capsys):
    """A file listed in the manifest but not on disk is a clear error, not a crash."""
    monkeypatch.setattr(download, "read_manifest", one_row_manifest)
    monkeypatch.setattr(config, "FILE_SUMMARY_PATH", sandbox / "summary.csv")
    assert download.cmd_verify() == 1
    assert "DPQ_L: not downloaded" in capsys.readouterr().err


def test_check_summary_flags_problems():
    ok = {"rows": 10, "has_seqn": True, "seqn_unique_per_row": True, "phq9_items_present": True}
    assert download.check_summary(ok, "DPQ") == []
    assert "missing PHQ-9 items" in download.check_summary({**ok, "phq9_items_present": False}, "DPQ")
    assert "SEQN not unique" in download.check_summary({**ok, "seqn_unique_per_row": False}, "DEMO")
    # The medication file has one row per drug, so repeated SEQN is expected there.
    assert download.check_summary({**ok, "seqn_unique_per_row": False}, "RXQ_RX") == []
