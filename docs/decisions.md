# Decision log

Every non-obvious decision, newest at the bottom of each checkpoint. Each entry says what was decided, why, and what the alternative was.

## Checkpoint 1 (literature and downloads)

**D1. File names come from the CDC listing pages, not from a naming pattern.**
`src/download.py` reads the CDC data listing page for each cycle and component page (Demographics, Questionnaire, Examination, Laboratory) and picks a file only if CDC lists its exact name. Why: CLAUDE.md forbids assuming a pattern, and the newer cycles break the old one (`P_` prefix in 2017-March 2020, `BPXO` instead of `BPX`). Alternative: build URLs from `{component}_{suffix}`. That would have failed silently where CDC renamed or dropped a file.

**D2. Listing-page columns are found by header name.**
The 2017-March 2020 listing pages have an extra "Years" column before "Data File Name". All 30 other pages checked do not. Reading cells by position would have shifted every field on those pages. The parser now finds columns by header and stops if one of the four needed headers is missing.

**D3. Exact file-name matching per cycle.**
A component matches only `{prefix}{component}{suffix}` for that cycle. This keeps look-alikes out (for example `RXQ_DRUG`, `SMQFAM`, `PAQY`, and `HSCRP` when looking for `CRP`). Unit tests cover these cases.

**D4. No 2017-2018 (`_J`) files.**
The `P_` files already contain the 2017-2018 participants (CLAUDE.md 5.1). The cycle list has no `_J` cycle, and `select_files` refuses any `_J` name.

**D5. One manifest holds both CDC metadata and download records.**
`data/nhanes_manifest.csv` records the CDC "Date Published" text (exactly as shown, including "Updated ..."), the date the listing was checked, and for each file its SHA-256, size, download date, the "Date Published" text at download, and CDC's `Last-Modified` header. Why: you asked for the download date and the CDC release or revision date in the manifest. The `Last-Modified` header is a second revision signal, because "Date Published" is only month-level text. The manifest is committed, so later sessions can check they got the same bytes.

**D6. A checksum mismatch is treated as a possible CDC revision, not a silent overwrite.**
If a fresh download differs from the recorded SHA-256, the new copy is kept as `<file>.candidate`. The old and new checksums, dates and "Date Published" text (re-read from CDC) are written to `data/nhanes_revisions.log` and to the terminal, and `make data` exits with an error. `make data ACCEPT_REVISIONS=1` accepts the new version and updates the manifest. Why: CDC does revise files (22 of the 134 are marked "Updated"), and a quiet change of input data would change results without anyone noticing. Alternative: fail with a bare checksum error. That gives no hint of the likely cause.

**D7. Every downloaded file must start with the SAS transport header.**
A HEAD request for `DPQ_L.xpt` reported a size of 20 bytes, but a full GET returned a valid 560,000-byte file. HEAD answers can't be trusted on this server, so the downloader always uses GET and checks the first bytes. This stops an HTML error page from being saved as data.

**D8. Download scope: every CLAUDE.md component for all 8 cycles, including candidate labs.**
You confirmed this. It includes both blood pressure files (`BPX` to 2015-2016, `BPXO` after) and both CRP files (`CRP` 2005-2010, `HSCRP` from 2015), so Checkpoint 2 can decide on harmonisation from the actual files.

**D9. Literature: cite only what was opened; mark abstract-only sources.**
You confirmed this. Each reference in `reports/related_work.md` is marked "[full text]" or "[abstract only]".

**D10. The arXiv review 2508.09809 is not cited.**
CLAUDE.md lists it as a starting point, and I read its abstract. It is a preprint, and your working rules say to cite only peer-reviewed papers or official reports, so I left it out. It is listed as an open question in the Checkpoint 1 summary.

**D11. Papers that could not be opened are not cited.**
ScienceDirect refused automated access (HTTP 403), and I did not try to get around that. The IBRO paper is open access and has a full-text record in Europe PMC (PMC13563247), the public archive run by EMBL-EBI. I read it there. Please tell me if you would rather I treat the publisher page as the only acceptable source. A 2024 *Innovation in Aging* conference abstract and Tubbs et al. 2020 appeared in searches, but I could not read the relevant text, so they are not cited.
