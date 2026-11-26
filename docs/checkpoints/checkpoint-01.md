# Checkpoint 1: literature review and NHANES downloads

Branch: `checkpoint-01-literature`. Date: 2026-11-26.

## What I did

1. Added the project scaffolding: `requirements.txt` (pinned), `Makefile` (`make data`, `make test`, `make all`), `src/config.py` (cycles, periods, components) and `.gitignore` entries that keep `data/raw/` out of git.
2. Wrote `src/download.py`. It reads the CDC listing pages to find exact file names, downloads every file, records checksums and dates in `data/nhanes_manifest.csv`, and checks that every file opens correctly.
3. Downloaded all 134 files for the 8 cycles and checked each one.
4. Wrote `tests/test_download.py` (20 tests, all passing, no network needed).
5. Searched the literature, read the sources, and wrote `reports/related_work.md` (17 references, each marked "full text" or "abstract only").
6. Started `docs/decisions.md` (11 entries so far).

## Key numbers

All numbers below come from `data/nhanes_manifest.csv` and `data/nhanes_file_summary.csv`, which are produced by code.

| Cycle | Period | Files | Size (MB) | DEMO rows | DPQ rows (age 18+) |
|---|---|---|---|---|---|
| 2005-2006 | earlier | 17 | 33.0 | 10,348 | 5,334 |
| 2007-2008 | earlier | 17 | 33.3 | 10,149 | 5,995 |
| 2009-2010 | earlier | 17 | 31.1 | 10,537 | 6,360 |
| 2011-2012 | earlier | 16 | 31.7 | 9,756 | 5,615 |
| 2013-2014 | earlier | 16 | 45.7 | 10,175 | 5,924 |
| 2015-2016 | earlier | 17 | 45.6 | 9,971 | 5,735 |
| 2017-2020 | pre_pandemic | 17 | 45.2 | 15,560 | 8,965 |
| 2021-2023 | recent | 17 | 16.2 | 11,933 | 6,337 |
| **Total** | | 134 | 281.8 | 88,429 | 50,265 |

"DPQ rows" counts everyone with a depression-screener record, whether or not they answered all nine items. Complete PHQ-9 counts and the 18 to 25 year old counts come at Checkpoint 2, as planned.

File availability by component and cycle (`data/nhanes_availability.csv`):

| component | 2005-2006 | 2007-2008 | 2009-2010 | 2011-2012 | 2013-2014 | 2015-2016 | 2017-2020 | 2021-2023 |
|---|---|---|---|---|---|---|---|---|
| DEMO | `DEMO_D` | `DEMO_E` | `DEMO_F` | `DEMO_G` | `DEMO_H` | `DEMO_I` | `P_DEMO` | `DEMO_L` |
| DPQ | `DPQ_D` | `DPQ_E` | `DPQ_F` | `DPQ_G` | `DPQ_H` | `DPQ_I` | `P_DPQ` | `DPQ_L` |
| SLQ | `SLQ_D` | `SLQ_E` | `SLQ_F` | `SLQ_G` | `SLQ_H` | `SLQ_I` | `P_SLQ` | `SLQ_L` |
| SMQ | `SMQ_D` | `SMQ_E` | `SMQ_F` | `SMQ_G` | `SMQ_H` | `SMQ_I` | `P_SMQ` | `SMQ_L` |
| ALQ | `ALQ_D` | `ALQ_E` | `ALQ_F` | `ALQ_G` | `ALQ_H` | `ALQ_I` | `P_ALQ` | `ALQ_L` |
| PAQ | `PAQ_D` | `PAQ_E` | `PAQ_F` | `PAQ_G` | `PAQ_H` | `PAQ_I` | `P_PAQ` | `PAQ_L` |
| MCQ | `MCQ_D` | `MCQ_E` | `MCQ_F` | `MCQ_G` | `MCQ_H` | `MCQ_I` | `P_MCQ` | `MCQ_L` |
| DIQ | `DIQ_D` | `DIQ_E` | `DIQ_F` | `DIQ_G` | `DIQ_H` | `DIQ_I` | `P_DIQ` | `DIQ_L` |
| HIQ | `HIQ_D` | `HIQ_E` | `HIQ_F` | `HIQ_G` | `HIQ_H` | `HIQ_I` | `P_HIQ` | `HIQ_L` |
| HUQ | `HUQ_D` | `HUQ_E` | `HUQ_F` | `HUQ_G` | `HUQ_H` | `HUQ_I` | `P_HUQ` | `HUQ_L` |
| FSQ | `FSQ_D` | `FSQ_E` | `FSQ_F` | `FSQ_G` | `FSQ_H` | `FSQ_I` | `P_FSQ` | `FSQ_L` |
| RXQ_RX | `RXQ_RX_D` | `RXQ_RX_E` | `RXQ_RX_F` | `RXQ_RX_G` | `RXQ_RX_H` | `RXQ_RX_I` | `P_RXQ_RX` | `RXQ_RX_L` |
| BMX | `BMX_D` | `BMX_E` | `BMX_F` | `BMX_G` | `BMX_H` | `BMX_I` | `P_BMX` | `BMX_L` |
| BPX | `BPX_D` | `BPX_E` | `BPX_F` | `BPX_G` | `BPX_H` | `BPX_I` | not listed | not listed |
| BPXO | not listed | not listed | not listed | not listed | not listed | not listed | `P_BPXO` | `BPXO_L` |
| GHB | `GHB_D` | `GHB_E` | `GHB_F` | `GHB_G` | `GHB_H` | `GHB_I` | `P_GHB` | `GHB_L` |
| TCHOL | `TCHOL_D` | `TCHOL_E` | `TCHOL_F` | `TCHOL_G` | `TCHOL_H` | `TCHOL_I` | `P_TCHOL` | `TCHOL_L` |
| HSCRP | not listed | not listed | not listed | not listed | not listed | `HSCRP_I` | `P_HSCRP` | `HSCRP_L` |
| CRP | `CRP_D` | `CRP_E` | `CRP_F` | not listed | not listed | not listed | not listed | not listed |

A file existing in every cycle does not mean its questions are comparable. That is checked variable by variable at Checkpoint 2.

## Literature findings

**Search (a), sleep overlap.** There is partial prior work. Details are in `reports/related_work.md`, sections 3 and 4.
- Salimi et al. 2026 (NHANES 2005-March 2020, unweighted, PHQ-9 ≥ 5) found that removing sleep predictors lowered ROC-AUC from 0.726 to 0.611. That is our Model B. They did not rebuild the outcome without the sleep items (our Model C).
- Al-Ghadban and Salman 2026 removed PHQ-9 item 3 from the outcome in a regression analysis of 389 Kuwait University students recruited by convenience. That is a small-sample version of the regression half of Aim 2. It removed only the sleep item, not tiredness, and fitted no predictive models.
- Niu et al. 2025 added `DPQ030` as a covariate (NHANES, ages 60 and older). Wu and Wang 2026 rebuilt a symptom network without item 3.
- **Not found:** removing both `DPQ030` and `DPQ040` with a matched cutoff; doing that for predictive models and SHAP; doing it in a national probability sample of young adults; or comparing it across periods.
- **Somatic-factor work (your addition):** two-factor models (somatic: sleep, fatigue, appetite) are common, including in NHANES. That work asks whether the items measure depression or physical illness. Aim 2 asks whether shared content between a sleep predictor and the outcome inflates the predictor. The difference is explained in section 4 of `related_work.md`.
- **PHQ-8 (your addition):** it omits item 9, not the sleep item (Wu et al. 2020). This is stated in section 3 of `related_work.md`.

**Search (b), Kaggle or convenience data against validated data.** I found no study that tests findings from a Kaggle mental health dataset against validated survey data. Related work covers Kaggle provenance (Gibson et al. 2026, on stroke and diabetes datasets) and convenience versus representative samples (Georgi et al. 2025).

## Surprises

1. **The course project's dataset may be synthetic.** Washton et al. (2026, *Frontiers in Medicine*) describe the Kaggle Student Depression Dataset (27,901 records) as synthetic. They say its depression label "was generated algorithmically based on weighted combinations of the predictor variables". Their only source is the Kaggle page. That page loads its content with JavaScript, so I could only read its title, and I have not confirmed this. Your report and proposal do not say the data are synthetic.
2. **The depression questions changed mode in 2021-2023.** They were interviewer-administered (CAPI) up to 2017-March 2020 and self-administered (ACASI) in Aug 2021-Aug 2023. Both CDC codebooks and Data Brief 527 say so. People often report more sensitive symptoms when no interviewer is present. Some of the rise from 8.3% to 13.1% (ages 12 and older, Data Brief 527) may therefore come from the mode change. Our data cannot separate the two, and this directly affects Aim 3.
3. **No medication names in 2021-2023.** `RXQ_RX_L` has only "took any prescription medicine in the past month" (`RXQ033`) and "how many" (`RXQ050`). The CDC codebook says: "The detailed prescription medication name, duration of use, and reason for use were not collected in this survey cycle." Antidepressant use can only be identified in 2005-2016 and 2017-March 2020.
4. **Some components change between cycles.** C-reactive protein is `CRP` in 2005-2010, missing in 2011-2014, and `HSCRP` from 2015. Blood pressure is manual (`BPX`) through 2015-2016 and oscillometric (`BPXO`) after that. Neither fully meets the "all periods" rule as is. These are Checkpoint 2 decisions.
5. **Two quirks in the CDC website** (both handled and tested). The 2017-March 2020 listing pages have an extra "Years" column, and HEAD requests report wrong file sizes. Both would have caused silent errors.
6. `FSQ_L` (food security, 2021-2023) was published in December 2025, about 15 months after the rest of the cycle. That's not a problem, just worth knowing.

## Assumptions

- The CDC listing pages are the authoritative list of files. I did not check the CDC FTP mirror.
- The public DPQ files contain everyone aged 18 and older who answered the screener. Every file's ages run from 18 to 80 or 85 (checked by merging with DEMO), and the codebooks say youth data are only available in the Research Data Center. This confirms CLAUDE.md 5.1.
- Data Brief 527 covers ages 12 and older and uses restricted youth data, so our 18+ estimate at Checkpoint 2 can only be roughly compared with it.

## What I checked and how

| Check | How | Result |
|---|---|---|
| CDC reachable | GET on listing pages and files | Yes, no network change needed |
| Every file is real XPT | First bytes must equal the SAS transport header | 134 of 134 |
| Every file opens | `pandas.read_sas` on each file | 134 of 134 |
| SEQN present and unique | Per file (medication files allow repeats) | No problems |
| DPQ has all nine PHQ-9 items | `DPQ010` to `DPQ090` in each DPQ file | 8 of 8 cycles |
| No 2017-2018 `_J` files | Manifest and code check | 0 found |
| Idempotent download | `make data` run three times | 2nd and 3rd runs: 134 "present", 0 downloaded |
| Revision handling | Unit tests with a changed file | Warns, logs, keeps old checksum, exits with error |
| Data Brief 527 numbers in CLAUDE.md | Read the brief | 8.2% to 13.1% confirmed, April 2025 |
| Original project numbers in CLAUDE.md | Text of the report PDF | 71.8%, 77.30%, 80.23%, 90.74%, 85.17% and the five importances all match |
| Each citation opened | Recorded per reference | 17 cited; 8 full text, 9 abstract only |
| Writing style | Scan for em dashes | None |

## Open questions and decisions I need from you

1. **Aim 2 overlap (stop rule).** Parts of Aim 2 already exist: Model B (Salimi et al.) and an item-3-only regression in a small convenience sample (Al-Ghadban and Salman). My recommendation is to keep Aim 2. Frame its contribution as the outcome-side ablation (Model C, dropping both `DPQ030` and `DPQ040`), applied to both regression and predictive models, in a national sample of 18 to 25 year olds with survey weights. Name both papers as direct comparisons. Do you agree, or do you want to change the aim?
2. **Is the Kaggle dataset synthetic?** Please open https://www.kaggle.com/datasets/hopesb/student-depression-dataset in a browser and tell me what the description and tags say. If it is synthetic, Aim 4 and CLAUDE.md Section 3 should describe it that way, not as convenience data. The question would become "do patterns in a synthetic dataset widely used for student depression ML match validated data?" I will not edit CLAUDE.md without your go-ahead.
3. **Mode change and Aim 3.** My recommendation: state in `analysis_plan.md` (Checkpoint 3) that period differences involving 2021-2023 combine real change with a change in interview mode, and that this data cannot separate them. Agree?
4. **Antidepressant ablation.** My recommendation: run it on 2005-2016 and 2017-March 2020 only, the development data where secondary ablations belong anyway, and say so in the plan. Agree?
5. **arXiv 2508.09809.** I read its abstract but did not cite it, because it is a preprint (your rule 11). Keep it out, or cite it clearly labelled as a preprint?
6. **Appetite item.** The factor literature puts appetite (item 5) in the somatic factor too. Should I add a pre-registered sensitivity analysis that also drops item 5? This would be on top of the main sleep and tiredness ablation, not instead of it.
7. **Europe PMC.** ScienceDirect blocked automated access, so I read the open-access IBRO paper through Europe PMC. Is that acceptable as a source?

## Next (only after you say "approved")

Checkpoint 2: `docs/harmonization.md`, `src/harmonize.py`, participant flow and the actual 18 to 25 sample sizes per period.
