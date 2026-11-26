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

**D10. The arXiv review 2508.09809 is cited as a preprint, for background only.**
At first I left it out, because the working rules allow only peer-reviewed papers or official reports. After review you decided to cite it, clearly labelled as a preprint and used for background only, never for a key claim. Preprints are labelled "preprint, not peer reviewed" in the reference list.

**D11. Papers that could not be opened are not cited.**
ScienceDirect refused automated access (HTTP 403), and I did not try to get around that. The IBRO paper is open access and has a full-text record in Europe PMC (PMC13563247), the public archive run by EMBL-EBI. I read it there. You confirmed that Europe PMC is an acceptable source for open-access versions.

### Decisions made at the Checkpoint 1 review

**D12. Aim 2 is framed as an outcome-side ablation, with named comparisons.**
The literature showed that parts of Aim 2 exist already: removing sleep predictors (Salimi et al. 2026) and removing item 3 from the outcome in a small convenience sample (Al-Ghadban and Salman 2026). You decided to keep Aim 2 as follows: remove both the sleep (`DPQ030`) and tiredness (`DPQ040`) items from the outcome, for both regression and prediction, in young adults, with survey weights. Both papers are named comparisons. Alternative: drop or narrow Aim 2. We rejected that because neither paper removes both items, uses a national sample of young adults, or applies the ablation to predictive models.

**D13. Malik and En (preprint, 2026) added as a comparison for Aim 2.**
You asked me to check it. It overlaps partly. It uses survey-weighted NHANES 2007-2018, treats "reported trouble sleeping" as "measured independently of the PHQ-9" (OR 4.03), and re-tests the sleep domain against an outcome it calls "PHQ-8, which removes the sleep item". That conflicts with the standard PHQ-8, which drops item 9. Its methods do not say which item was removed, and the result is given without numbers. It does not remove tiredness, does not study young adults, and does not cover 2021-2023. It is in `related_work.md` section 3 as a preprint comparison.

**D14. 2021-2023 comparisons will be described as mixing real change with the interview mode change.**
To be written into `docs/analysis_plan.md` at Checkpoint 3, as you decided. The depression questions moved from an interviewer (CAPI) to self-administered ACASI. NCHS documents the change (Vital and Health Statistics Series 1, No. 66, and the DPQ_L codebook) but has published no analysis of its effect on PHQ-9 scores that I could find. Response rates also fell, from 51.0% and 46.9% (interview and examination, 2017-March 2020) to 34.6% and 25.7% (NHANES 2021-2023 brief overview). The plan will state both points. Alternative: adjust for mode. That isn't possible, because mode and period are perfectly confounded: everyone in 2021-2023 used ACASI and nobody before did.

**D15. The antidepressant ablation uses 2005-2016 and 2017-March 2020 only.**
Why: the 2021-2023 medication file has no drug names. CDC states that "the detailed prescription medication name, duration of use, and reason for use were not collected in this survey cycle." Secondary ablations belong on development data anyway, so the locked test set is not touched. To be stated in `analysis_plan.md`.

**D16. Optional sensitivity check: also remove the appetite item.**
Factor analyses, including one in NHANES, place appetite (item 5, `DPQ050`) in the somatic factor with sleep and tiredness. A pre-registered optional check will drop items 3, 4 and 5 together, on top of the main two-item ablation, not instead of it.

**D17. Aim 4 and CLAUDE.md stay unchanged until the Kaggle page is checked.**
A peer-reviewed paper describes the Kaggle dataset as synthetic, but I could not confirm this on Kaggle itself. You will check the page. Until then, nothing in CLAUDE.md or Aim 4 changes.

**D18. The planning file is not a project file.**
`you-are-working-on-humming-bee.md` is Claude's own working plan, stored outside the repository (`/root/.claude/plans/`). It was never committed, so there was nothing to remove. A 2024 *Innovation in Aging* conference abstract and Tubbs et al. 2020 appeared in searches, but I could not read the relevant text, so they are not cited.
