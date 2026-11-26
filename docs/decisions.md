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
A peer-reviewed paper describes the Kaggle dataset as synthetic, but I could not confirm this on Kaggle itself. You will check the page. Until then, nothing in CLAUDE.md or Aim 4 changes. *Resolved by D19 to D25.*

**D18. The planning file is not a project file.**
`you-are-working-on-humming-bee.md` is Claude's own working plan, stored outside the repository (`/root/.claude/plans/`). It was never committed, so there was nothing to remove. A 2024 *Innovation in Aging* conference abstract and Tubbs et al. 2020 appeared in searches, but I could not read the relevant text, so they are not cited.

### Decisions made after the Kaggle page was checked

**D19. The Kaggle dataset is treated as synthetic data.**
You checked the Kaggle page in a browser. It states: "This dataset was synthetically generated and may not reflect real-world data." It has a "Synthetic" tag and gives no original data source. Author: Shodolamu Opeyemi. Licence: Apache 2.0. From now on every document calls it synthetic data. Comparisons with NHANES are synthetic data versus real survey data, not two samples of people.

**D20. `main` merged into `checkpoint-01-literature`.**
You added the CSV to `main` (commit `32e7c42`). I merged `main` into the branch with a merge commit and no rebase, so the branch history stays as pushed. The merge added only the CSV, with no conflicts.

**D21. The CSV is pinned by a manifest and a test.**
`original_course_project/data/MANIFEST.md` records the SHA-256, size, shape (27,901 rows, 18 columns) and missing values (3, all in `Financial Stress`). All of these match what you expected. `tests/test_original_data.py` checks them on every `make test`, so a changed file can't silently change Aim 4 results. The manifest is a new file in `original_course_project/data/`, added because you asked for it.

**D22. `original_course_project/README.md`: credit and synthetic label only.**
This is the only existing file in `original_course_project/` that I edited, as you allowed. I added two short paragraphs: credit (author, Kaggle URL, Apache 2.0, pointer to the checksum) and the synthetic label. I did not call the copy "unmodified", because I could not compare it with a fresh Kaggle download with the Kaggle quote. Nothing else in that folder changed. The README's table row for `data/` still says "The Kaggle CSV, if its license allows redistribution", which is now out of date. I left it because changing it is outside what you allowed. It is listed as an open question.

**D23. `reports/related_work.md` updated.**
- Section 5 now cites the Kaggle page (accessed 26 November 2026, read in your browser) alongside Washton et al.
- Gibson et al. is described as the closest methodological precedent for the paper audit, with how ours differs: mental health, a dataset openly labelled synthetic, preprints counted, and a direct comparison with validated national data.
- I read Gibson et al. in full to describe their method (Google Scholar, full-text screening, peer-reviewed studies only, nine TRIPOD+AI items), so its reference is now marked full text.
- Section 6 item 4 now says "labelled synthetic".
- Washton et al. remain the only source for how the label was built. The Kaggle page does not describe the generation method.

**D24. CLAUDE.md updated, with your go-ahead.**
- Section 2, Aim 4: reframed as "Synthetic data versus validated data". It keeps the replication scorecard and adds the paper audit.
- Section 3: the dataset line now gives the author, the licence and the Kaggle synthetic statement, and says the course project did not account for this. The provenance weakness bullet now says the data are labelled synthetic.
- Section 5.3: it now gives the CSV location and manifest, and says to use the data only for Aim 4 and always describe them as synthetic.
- Section 7.8: added a note that "Holds up" does not mean the synthetic data are valid, marked step 1 as the Checkpoint 4 baseline, and added step 6 (the bounded literature audit).
- Checkpoint 4 is unchanged.
- Not changed, because they were outside what you approved: Section 1 ("Its data has no documented source..."), Section 4 ("replication of convenience-data findings"), and the Section 9 tree comment "(Kaggle CSV, if its license allows)". They are now slightly out of step with Aim 4 and are listed as an open question.

**D25. The paper audit is designed at Checkpoint 3, not now.**
Search sources, terms, inclusion rules and stopping rule go into `analysis_plan.md` before the audit runs, as you said. One practical point for that design: Gibson et al. searched Google Scholar, which may block automated searches from this environment. Checkpoint 3 should name sources that can be searched here, such as Europe PMC full-text search and Crossref, and say how Google Scholar is handled if it can't be.

**D26. Apache 2.0 notice: flagged, not acted on.**
Apache License 2.0, section 4(a), says: "You must give any other recipients of the Work or Derivative Works a copy of this License" (checked against https://www.apache.org/licenses/LICENSE-2.0.txt). The repository credits the licence but does not include its text. Adding `original_course_project/data/LICENSE` would be a new file in a folder you protect, so I have not done it. It is listed as an open question.

### Decisions that close Checkpoint 1

**D27. README table row for `data/` updated.**
You approved it. The row in `original_course_project/README.md` now says `data/` holds the synthetic Kaggle CSV (Apache License 2.0), its checksum in `MANIFEST.md`, and the licence text in `LICENSE`. This resolves the open point in D22.

**D28. Three CLAUDE.md phrases aligned with the new Aim 4.**
You approved it.
- Section 1: "Its data has no documented source..." now says the dataset is labelled synthetic, gives no source, sampling method or validated questionnaire, and that the course project did not account for this.
- Section 4: "the replication of convenience-data findings" is now "the comparison of patterns in a widely used synthetic dataset with validated national data".
- Section 9 tree comment: now "(synthetic Kaggle CSV, MANIFEST.md, LICENSE)".

I left the search (b) instruction in Section 4 ("papers that test convenience or Kaggle mental health datasets against validated data") as it was. It records the search that was run, not a description of the dataset.

**D29. Apache 2.0 licence text added as `original_course_project/data/LICENSE`.**
You approved it. The file is the official text from https://www.apache.org/licenses/LICENSE-2.0.txt, copied unchanged on 26 November 2026. It is 202 lines and 11,358 bytes, SHA-256 `cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30`, and the manifest records this. This meets section 4(a) of the licence (D26).

**D30. Audit search sources: proposed at Checkpoint 3; Google Scholar by hand if needed.**
At Checkpoint 3 I will propose the search sources for the paper audit. If Google Scholar cannot be reached from this environment, you will run that part of the search by hand. The plan will then give the exact query strings, the date run and what to record, so the manual part is reproducible.

**D31. Kaggle access date confirmed.**
You confirmed that you checked the Kaggle page on 26 November 2026, the date used in `related_work.md` reference 22 and in the manifest.

