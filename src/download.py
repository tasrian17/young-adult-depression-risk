"""Download NHANES files listed on the CDC website and verify them.

Three steps, each a sub-command:

``manifest``
    Read the CDC listing pages for every cycle and component page, and write
    ``data/nhanes_manifest.csv``: one row per file we need, with the exact
    file name, URLs and the "Date Published" text shown by CDC. File names
    come from CDC, not from a naming pattern. Checksums already recorded in
    an existing manifest are kept.

``fetch``
    Download every file in the manifest into ``data/raw/nhanes/<cycle>/``.
    Files whose SHA-256 already matches the manifest are skipped, so the step
    is idempotent. A new download that does not match the recorded checksum
    is treated as a possible CDC revision: it is kept aside as
    ``<file>.candidate``, logged, and the run exits with an error so a person
    decides. ``--accept-revisions`` replaces the old file and checksum.

``verify``
    Open every file with pandas, check it has SEQN (unique, except in the
    medication file), check DPQ files have all nine PHQ-9 items, and write
    ``data/nhanes_file_summary.csv``.

Usage: ``python -m src.download {manifest,fetch,verify} [--accept-revisions]``
"""

import argparse
import datetime as dt
import hashlib
import re
import shutil
import sys
from pathlib import Path
from urllib.parse import urljoin

import pandas as pd
import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from src import config

# Every SAS transport (XPT) file starts with this header. Checking it stops
# an HTML error page from being saved as data.
XPT_MAGIC = b"HEADER RECORD*******LIBRARY HEADER RECORD!!!!!!!"

MANIFEST_COLUMNS = [
    "cycle", "period", "page", "component", "file", "data_url", "doc_url",
    "cdc_date_published", "listing_checked_on",
    "sha256", "bytes", "downloaded_on", "cdc_date_published_at_download",
    "cdc_last_modified",
]
CHECKSUM_COLUMNS = [
    "sha256", "bytes", "downloaded_on", "cdc_date_published_at_download",
    "cdc_last_modified",
]


class DownloadError(RuntimeError):
    """A file could not be downloaded or is not a valid XPT file."""


# --------------------------------------------------------------------------
# Listing pages
# --------------------------------------------------------------------------

def make_session() -> requests.Session:
    """Return a requests session that retries transient network errors."""
    retry = Retry(
        total=4, backoff_factor=2, status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=("GET",),
    )
    session = requests.Session()
    session.mount("https://", HTTPAdapter(max_retries=retry))
    return session


def fetch_listing_html(session: requests.Session, page: str, cycle: str) -> str:
    """Download the CDC data listing page for one component page and cycle."""
    resp = session.get(
        config.CDC_LISTING_URL, params={"Component": page, "Cycle": cycle},
        timeout=60,
    )
    resp.raise_for_status()
    return resp.text


def parse_listing(html: str) -> dict:
    """Parse a CDC listing page into ``{FILE_NAME: row}``.

    Each row holds ``description``, ``data_url``, ``doc_url`` and
    ``date_published``. The file name is upper case without ``.xpt``.
    Rows without an XPT link (for example, withdrawn files) are skipped.
    """
    soup = BeautifulSoup(html, "lxml")
    table = soup.find("table", id="GridView1")
    if table is None:
        raise ValueError("CDC listing page has no GridView1 table")
    # Columns are found by header name because the layout differs between
    # cycles (the 2017-March 2020 pages have an extra "Years" column first).
    headers = [th.get_text(strip=True) for th in table.find_all("th")]
    needed = ["Data File Name", "Doc File", "Data File", "Date Published"]
    missing = [h for h in needed if h not in headers]
    if missing:
        raise ValueError(f"CDC listing page lacks columns {missing}; found {headers}")
    col = {h: headers.index(h) for h in needed}

    rows = {}
    for tr in table.find_all("tr"):
        cells = tr.find_all("td")
        if len(cells) != len(headers):
            continue
        data_link = cells[col["Data File"]].find("a", href=re.compile(r"\.xpt$", re.I))
        if data_link is None:
            continue
        href = data_link["href"]
        name = Path(href).stem.upper()
        if name in rows:
            raise ValueError(f"{name} is listed twice on one CDC listing page")
        doc_link = cells[col["Doc File"]].find("a")
        rows[name] = {
            "description": cells[col["Data File Name"]].get_text(" ", strip=True),
            "data_url": urljoin(config.CDC_BASE_URL, href),
            "doc_url": urljoin(config.CDC_BASE_URL, doc_link["href"]) if doc_link else "",
            "date_published": cells[col["Date Published"]].get_text(" ", strip=True),
        }
    return rows


def select_files(listing: dict, cycle: config.Cycle, page: str) -> list:
    """Pick the wanted components for one cycle from a parsed listing page.

    A component matches only if CDC lists the exact name
    ``{prefix}{component}{suffix}`` for this cycle, so look-alikes such as
    ``RXQ_DRUG`` or ``HSCRP`` (when looking for ``CRP``) are never picked.
    """
    selected = []
    for component in config.COMPONENTS_BY_PAGE[page]:
        name = cycle.file_name(component).upper()
        if name.endswith("_J"):
            raise ValueError(f"{name}: 2017-2018 files must not be mixed with P_ files")
        if name in listing:
            selected.append({"component": component, "file": name, **listing[name]})
    return selected


def build_manifest(session: requests.Session, today: str) -> pd.DataFrame:
    """Read every listing page and return the manifest (without checksums)."""
    records = []
    for cycle in config.CYCLES:
        for page in config.COMPONENTS_BY_PAGE:
            listing = parse_listing(fetch_listing_html(session, page, cycle.name))
            for row in select_files(listing, cycle, page):
                records.append({
                    "cycle": cycle.name, "period": cycle.period, "page": page,
                    "component": row["component"], "file": row["file"],
                    "data_url": row["data_url"], "doc_url": row["doc_url"],
                    "cdc_date_published": row["date_published"],
                    "listing_checked_on": today,
                })
    return pd.DataFrame.from_records(records)


def merge_checksums(new: pd.DataFrame, old) -> pd.DataFrame:
    """Carry recorded checksum columns from an old manifest into a new one."""
    if old is None or old.empty:
        merged = new.copy()
        for col in CHECKSUM_COLUMNS:
            merged[col] = ""
    else:
        keep = old[["cycle", "file", *CHECKSUM_COLUMNS]]
        merged = new.merge(keep, on=["cycle", "file"], how="left")
    return merged.fillna("")[MANIFEST_COLUMNS]


def availability_table(manifest: pd.DataFrame) -> pd.DataFrame:
    """Return a component-by-cycle table of the file name, or "" if not listed."""
    table = manifest.pivot(index="component", columns="cycle", values="file")
    order = [c for page in config.COMPONENTS_BY_PAGE.values() for c in page]
    table = table.reindex(index=order, columns=[c.name for c in config.CYCLES])
    return table.fillna("").reset_index()


# --------------------------------------------------------------------------
# Downloading
# --------------------------------------------------------------------------

def sha256_of(path: Path) -> str:
    """Return the SHA-256 hex digest of a file."""
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def download_to(session: requests.Session, url: str, dest: Path) -> str:
    """Download ``url`` to ``dest`` and return CDC's Last-Modified header.

    Raises DownloadError if the request fails or the body is not an XPT file.
    """
    try:
        resp = session.get(url, timeout=300, stream=True)
        resp.raise_for_status()
        dest.parent.mkdir(parents=True, exist_ok=True)
        with dest.open("wb") as fh:
            for chunk in resp.iter_content(1 << 20):
                fh.write(chunk)
    except requests.RequestException as exc:
        raise DownloadError(f"{url}: {exc}") from exc
    with dest.open("rb") as fh:
        if fh.read(len(XPT_MAGIC)) != XPT_MAGIC:
            raise DownloadError(f"{url}: response is not a SAS transport (XPT) file")
    return resp.headers.get("Last-Modified", "")


def local_path(row) -> Path:
    """Return where a manifest row's file is stored locally."""
    return config.RAW_NHANES_DIR / row["cycle"] / f"{row['file']}.xpt"


def log_revision(row, new_sha: str, new_last_modified: str, today: str,
                 current_published: str, accepted: bool) -> str:
    """Append a possible-revision entry to the revisions log and return it."""
    entry = (
        f"[{today}] {row['cycle']} {row['file']}: checksum differs from manifest. "
        "This may be a CDC revision of the file.\n"
        f"  recorded: sha256={row['sha256']} downloaded_on={row['downloaded_on']} "
        f"date_published='{row['cdc_date_published_at_download']}' "
        f"last_modified='{row['cdc_last_modified']}'\n"
        f"  new:      sha256={new_sha} downloaded_on={today} "
        f"date_published='{current_published}' last_modified='{new_last_modified}'\n"
        f"  action:   {'ACCEPTED, manifest updated' if accepted else 'NOT accepted, new copy kept as .candidate'}\n"
    )
    config.REVISIONS_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with config.REVISIONS_LOG_PATH.open("a") as fh:
        fh.write(entry)
    return entry


def record_checksum(manifest: pd.DataFrame, idx, path: Path, last_modified: str,
                    today: str) -> None:
    """Write a file's checksum, size and download details into the manifest."""
    manifest.loc[idx, "sha256"] = sha256_of(path)
    manifest.loc[idx, "bytes"] = str(path.stat().st_size)
    manifest.loc[idx, "downloaded_on"] = today
    manifest.loc[idx, "cdc_date_published_at_download"] = manifest.loc[idx, "cdc_date_published"]
    manifest.loc[idx, "cdc_last_modified"] = last_modified


def fetch_one(session, manifest: pd.DataFrame, idx, today: str,
              accept_revisions: bool, current_published=None) -> str:
    """Make sure one manifest file is present and matches its checksum.

    Returns a status: "present", "downloaded", "restored" (a local copy was
    damaged and the fresh copy matches), "revision_accepted" or
    "possible_revision". ``current_published`` is a function returning the
    "Date Published" text CDC shows now; it is only called on a mismatch.
    """
    row = manifest.loc[idx]
    dest = local_path(row)
    recorded = row["sha256"]

    if dest.exists() and recorded and sha256_of(dest) == recorded:
        return "present"

    tmp = dest.with_suffix(".part")
    last_modified = download_to(session, row["data_url"], tmp)
    new_sha = sha256_of(tmp)

    if not recorded:
        tmp.replace(dest)
        record_checksum(manifest, idx, dest, last_modified, today)
        return "downloaded"
    if new_sha == recorded:
        tmp.replace(dest)
        return "restored"

    published = current_published(row) if current_published else row["cdc_date_published"]
    entry = log_revision(row, new_sha, last_modified, today, published, accept_revisions)
    print("WARNING: " + entry, file=sys.stderr)
    if accept_revisions:
        tmp.replace(dest)
        manifest.loc[idx, "cdc_date_published"] = published
        record_checksum(manifest, idx, dest, last_modified, today)
        return "revision_accepted"
    shutil.move(tmp, dest.with_suffix(".candidate"))
    return "possible_revision"


def current_published_lookup(session):
    """Return a function giving the "Date Published" text CDC shows now for a row."""
    cache = {}

    def lookup(row) -> str:
        key = (row["page"], row["cycle"])
        if key not in cache:
            cache[key] = parse_listing(fetch_listing_html(session, *key))
        return cache[key].get(row["file"], {}).get("date_published", "not listed")

    return lookup


# --------------------------------------------------------------------------
# Verification
# --------------------------------------------------------------------------

def summarize_file(path: Path, component: str) -> dict:
    """Open one XPT file and return basic checks used to confirm it is sound."""
    df = pd.read_sas(path, format="xport")
    has_seqn = "SEQN" in df.columns
    n_unique = int(df["SEQN"].nunique()) if has_seqn else 0
    summary = {
        "rows": len(df),
        "columns": df.shape[1],
        "has_seqn": has_seqn,
        "unique_seqn": n_unique,
        "seqn_unique_per_row": has_seqn and n_unique == len(df),
        "phq9_items_present": "",
    }
    if component == "DPQ":
        summary["phq9_items_present"] = all(c in df.columns for c in config.PHQ9_ITEMS)
    return summary


def check_summary(summary: dict, component: str) -> list:
    """Return a list of problems with a file summary (empty if none)."""
    problems = []
    if not summary["has_seqn"]:
        problems.append("no SEQN column")
    elif component not in config.MULTI_ROW_COMPONENTS and not summary["seqn_unique_per_row"]:
        problems.append("SEQN not unique")
    if component == "DPQ" and summary["phq9_items_present"] is not True:
        problems.append("missing PHQ-9 items")
    if summary["rows"] == 0:
        problems.append("no rows")
    return problems


# --------------------------------------------------------------------------
# Commands
# --------------------------------------------------------------------------

def read_manifest() -> pd.DataFrame:
    """Read the committed manifest with every column as text."""
    return pd.read_csv(config.MANIFEST_PATH, dtype=str, keep_default_na=False)


def cmd_manifest(today: str) -> int:
    """Rebuild the manifest from CDC listing pages, keeping recorded checksums."""
    old = read_manifest() if config.MANIFEST_PATH.exists() else None
    manifest = merge_checksums(build_manifest(make_session(), today), old)
    config.DATA_DIR.mkdir(parents=True, exist_ok=True)
    manifest.to_csv(config.MANIFEST_PATH, index=False)
    availability_table(manifest).to_csv(config.AVAILABILITY_PATH, index=False)
    print(f"Manifest: {len(manifest)} files -> {config.MANIFEST_PATH}")
    if old is not None:
        dropped = set(old["file"]) - set(manifest["file"])
        if dropped:
            print(f"WARNING: no longer listed by CDC: {sorted(dropped)}", file=sys.stderr)
    return 0


def cmd_fetch(today: str, accept_revisions: bool) -> int:
    """Download missing files and check every checksum."""
    manifest = read_manifest()
    session = make_session()
    lookup = current_published_lookup(session)
    statuses = {}
    try:
        for idx in manifest.index:
            status = fetch_one(session, manifest, idx, today, accept_revisions, lookup)
            statuses[status] = statuses.get(status, 0) + 1
            if status != "present":
                print(f"{status:>18}: {manifest.loc[idx, 'cycle']} {manifest.loc[idx, 'file']}")
    finally:
        # Save checksums of whatever was downloaded, even if a later file failed.
        manifest.to_csv(config.MANIFEST_PATH, index=False)
    print(f"Fetch summary: {statuses}")
    if statuses.get("possible_revision"):
        print(
            "ERROR: some files differ from the recorded checksums, possibly because "
            f"CDC revised them. See {config.REVISIONS_LOG_PATH}. Review, then rerun with "
            "ACCEPT_REVISIONS=1 to accept and record the new versions.",
            file=sys.stderr,
        )
        return 2
    return 0


def cmd_verify() -> int:
    """Open every downloaded file, check it, and write the file summary."""
    manifest = read_manifest()
    records, failures = [], []
    for _, row in manifest.iterrows():
        path = local_path(row)
        if not path.exists():
            failures.append(f"{row['cycle']} {row['file']}: not downloaded (run `make data`)")
            continue
        summary = summarize_file(path, row["component"])
        problems = check_summary(summary, row["component"])
        records.append({"cycle": row["cycle"], "component": row["component"],
                        "file": row["file"], **summary,
                        "problems": "; ".join(problems)})
        if problems:
            failures.append(f"{row['cycle']} {row['file']}: {', '.join(problems)}")
    pd.DataFrame.from_records(records).to_csv(config.FILE_SUMMARY_PATH, index=False)
    print(f"Verified {len(records)} files -> {config.FILE_SUMMARY_PATH}")
    if failures:
        print("ERROR:\n  " + "\n  ".join(failures), file=sys.stderr)
        return 1
    return 0


def main(argv=None) -> int:
    """Command-line entry point."""
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("command", choices=["manifest", "fetch", "verify"])
    parser.add_argument("--accept-revisions", action="store_true",
                        help="replace files whose checksum changed (possible CDC revision)")
    args = parser.parse_args(argv)
    today = dt.datetime.now(dt.timezone.utc).date().isoformat()
    try:
        if args.command == "manifest":
            return cmd_manifest(today)
        if args.command == "fetch":
            return cmd_fetch(today, args.accept_revisions)
        return cmd_verify()
    except DownloadError as exc:
        print(f"ERROR: download failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
