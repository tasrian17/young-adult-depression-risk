# Project Brief: What Actually Predicts Depression in Young Adults?

Read this whole file before doing anything. It defines the research question, the data, the rules and the deliverables. If something here turns out to be wrong once you look at the actual data or literature, stop and tell me instead of guessing.

## 1. What this project is

I'm Tasrian Ahmed, a 4th-year BSc Computer Science (Honours) student at UPEI. This is an **independent research project** that extends my CS-4440 Data Science course project (Winter 2026).

The original project predicted "mental health risk" in students using a Kaggle dataset. Its data has no documented source, sampling method or validated questionnaire, so its findings can't be trusted. This project asks the same kind of question with real, validated data, tests which of the original findings hold up, and turns the results into a public tool people can use.

The original course work is in `original_course_project/`. **Never modify anything in that folder.** Treat it as a historical record.

I'm new to this kind of research. Explain your reasoning in plain language as you go, and stop at every checkpoint in Section 12.

## 2. Research question

**What actually predicts clinically significant depressive symptoms in young adults (18 to 25), and how much of what is commonly reported comes from weak data and measurement overlap?**

Five aims (Aims 1 to 4 use NHANES; Aim 5 is a second stage):

1. **Risk factors in real data.** Which factors (sleep, income, physical activity, smoking, alcohol, BMI, chronic conditions, insurance, and others) are associated with a positive depression screen in 18 to 25 year olds? How do they differ from older adults?
2. **The sleep question.** Sleep is often reported as a top predictor of depression. But the PHQ-9 itself asks about sleep (DPQ030) and tiredness (DPQ040). How much of sleep's apparent importance is the outcome partly measuring itself?
3. **Change over time.** Have the risk factors for young adults changed across 2005-2016, 2017-March 2020 and Aug 2021-Aug 2023? Frame this as "has the picture changed recently," not "what COVID did." The data is cross-sectional and cannot show causes.
4. **Synthetic data versus validated data.** A dataset labelled synthetic is widely used in depression research. Which of the patterns it shows match validated national data? This covers the findings of my course project, which used this dataset. Each comparison is synthetic data versus real survey data, not two samples of people. The results go into a replication scorecard (7.8), alongside a bounded audit of published papers that use the dataset.
5. **Canadian replication.** Do the main findings (Aims 1 and 2) hold up in Canadian data from the Canadian Community Health Survey (CCHS)? Report Atlantic Canada separately only if the sample allows. Start this only after the NHANES main analysis (Checkpoint 6) is done.

## 3. What the original project claimed

Source: `original_course_project/final/TasrianAhmed_Project_Report.pdf` and the notebook next to it.

- Dataset: Kaggle "Student Depression Dataset," 27,901 rows, 18 columns, by Shodolamu Opeyemi, Apache 2.0 licence. Its Kaggle page states: "This dataset was synthetically generated and may not reflect real-world data." The page carries a "Synthetic" tag and gives no original data source. The course project treated the data as real student records and did not account for this.
- Target: "high risk" = `Depression == 1` OR `Have you ever had suicidal thoughts? == Yes`. 71.8% positive.
- Features: Age, Academic Pressure, Work Pressure, CGPA, Study Satisfaction, Job Satisfaction, Work/Study Hours, Financial Stress, Gender, Sleep Duration, Dietary Habits, Family History of Mental Illness.
- Method: label encoding, single stratified 80/20 split, default Logistic Regression, Decision Tree (depth 10), Random Forest (depth 15). No tuning, no CV, no calibration.
- Reported test results: Logistic Regression accuracy 77.30%, precision 80.23%, recall 90.74%, F1 85.17%.
- Reported top Random Forest importances: CGPA (20.0%), Academic Pressure (16.6%), Age (14.5%), Work/Study Hours (12.9%), Financial Stress (10.9%).

Known weaknesses to document (verify each one yourself):

- A majority-class baseline already scores 71.8% accuracy, so 77.3% is only about 5.5 points better. No baseline was reported.
- The target mixes a current state (depression) with a lifetime item (ever had suicidal thoughts).
- Label encoding imposed a false order on categories such as Dietary Habits and Sleep Duration.
- Impurity-based importance is biased toward continuous, high-cardinality features like CGPA and Age.
- The dataset is labelled synthetic on its Kaggle page, with no original data source, sampling method or depression measure given. The course project did not mention this, so its findings cannot be read as evidence about real students.

## 4. Positioning against existing work

NHANES + machine learning + SHAP for depression has been done many times. The contribution here is the young adult focus, the sleep overlap analysis, the over-time comparison, and the replication of convenience-data findings. Starting points (open and verify each before citing; never cite something you haven't read):

- Brody and Hughes (2025), NCHS Data Brief No. 527: depression prevalence rose from 8.2% (2013-2014) to 13.1% (Aug 2021-Aug 2023) in people 12 and older.
- Vu et al. (2025), "Prediction of depressive disorder using machine learning approaches: findings from the NHANES," BMC Medical Informatics and Decision Making.
- "Interpretable machine learning for depression symptom classification in NHANES: Performance in a curated high-confidence corpus and the full survey population," IBRO Neuroscience Reports (2026), DOI 10.1016/j.ibneur.2026.08.009. Reports that sleep variables dominate.
- "A Comprehensive Review of Datasets for Clinical Mental Health AI Systems," arXiv 2508.09809.

Write `reports/related_work.md` (about one page): what has been done, what hasn't, and where this project fits. **Specifically search for**: (a) papers that already test whether the PHQ-9 sleep item inflates sleep's predictive importance, and (b) papers that test convenience or Kaggle mental health datasets against validated data. If either already exists, tell me before continuing so we can adjust the aims.

## 5. Data

### 5.1 NHANES (primary, public, free)

Download `.XPT` files from the CDC. Verify exact URLs and file names on the CDC site; do not assume a pattern. Check whether `wwwn.cdc.gov` is reachable first (see Section 11).

| Period | Cycles | File suffix |
|---|---|---|
| Earlier | 2005-2006 to 2015-2016 | D, E, F, G, H, I |
| Pre-pandemic | 2017-March 2020 | P_ prefix |
| Recent | Aug 2021-Aug 2023 | L |

Do not use 2017-2018 (J) files together with P_ files, because P_ already includes those participants.

Components to merge on `SEQN` (check availability in every period):

- Outcome: Depression Screener (`DPQ`)
- Demographics and weights (`DEMO`)
- Sleep (`SLQ`), Smoking (`SMQ`), Alcohol (`ALQ`), Physical activity (`PAQ`)
- Body measures (`BMX`), Blood pressure (`BPX` or `BPXO`)
- Medical conditions (`MCQ`), Diabetes (`DIQ`), Health insurance (`HIQ`), Hospital utilization (`HUQ`)
- Food security (`FSQ`) if available in all periods, as a financial hardship measure
- Labs only if available in all periods (for example `GHB`, `HSCRP`, `TCHOL`)
- Prescription medications (`RXQ_RX`), only for the secondary ablation in 7.6

Known issues:

- The Aug 2021-Aug 2023 cycle was redesigned. Build `docs/harmonization.md`: every feature, its variable name in each period, any recoding, and whether it exists in all periods. Only features available in all periods go into the main analysis.
- The public DPQ file covers adults 18+ only.
- Codes like 7, 9, 77, 99, 777, 999 mean refused or don't know. They are missing values, not numbers. Check each codebook.
- When pooling cycles, rescale weights following NCHS analytic guidelines. P_ files have their own weights (for example `WTMECPRP`). Verify every weight rule against the NCHS tutorials and cite them.
- **Sample size for 18 to 25 year olds will be small per cycle.** Report the actual counts early. If the recent period has too few young adults for a given analysis, say so and adjust, rather than reporting unstable numbers.

### 5.2 Outcome

- PHQ-9 total = sum of DPQ010 to DPQ090 (each 0 to 3). Require all nine items.
- **Primary outcome:** PHQ-9 ≥ 10. Always call it "clinically significant depressive symptoms" or "a positive depression screen," never a diagnosis.
- **Sensitivity outcome:** PHQ-9 ≥ 5.
- DPQ100 is never a feature.

### 5.3 Original Kaggle dataset

The CSV is at `original_course_project/data/Student Depression Dataset.csv` (Apache 2.0 licence; checksum and shape in `original_course_project/data/MANIFEST.md`). Its Kaggle page labels it synthetically generated, and the course project did not account for this. Use it only for Aim 4, and always describe it as synthetic data.

### 5.4 Healthy Minds Study (optional, only if I add it)

I've requested access to the Healthy Minds Study (U.S. university students). If I add files to `data/raw/hms/`, propose how to use them, especially to test the academic claims (academic pressure, CGPA) that NHANES can't test. Never try to download it yourself, and never commit it to the repo: its terms will almost certainly forbid redistribution.

### 5.5 CCHS (Canada, second stage for Aim 5)

The Canadian Community Health Survey Public Use Microdata File (PUMF) is published by Statistics Canada as a direct download (CSV) under the Statistics Canada Open Licence: https://www150.statcan.gc.ca/n1/en/catalogue/82M0013X. Confirm the licence terms before committing any derived files.

- **Cycles:** CCHS annual component 2015-2016, 2017-2018 and 2019-2020 (check which years are available and what each file contains). The PHQ-9 was used to screen adults 18+ in CCHS cycles from 2015 to 2019.
- **Check provincial coverage first.** Some CCHS modules are optional content asked only in some provinces or some years. Before any analysis, report which provinces answered the PHQ-9 module in each cycle, and limit the analysis to those.
- **PUMF limitations.** Some variables are grouped or suppressed for privacy (for example age in bands, income in categories). The design variables available for variance estimation differ from NHANES; follow Statistics Canada's guidance for PUMF variance estimation and cite it.
- **Geography.** Report Canada overall. Report Atlantic Canada only if the weighted and unweighted counts support stable estimates. Do not report PEI alone; the sample is too small.
- **The 2020 data collection** was disrupted by the pandemic. Read the user guide and note any changes in mode, response rate or sample before using that cycle.

Design note for now: write the NHANES harmonization and analysis code so the outcome scoring, the seven-item sleep ablation, and the model and reporting functions are reusable for a second survey. Do not build CCHS code until Aim 5 starts.

## 6. Rules (non-negotiable)

1. **Pre-register.** Before running any main analysis, write `docs/analysis_plan.md` describing every model, metric, subgroup and replication criterion. Commit it. Later changes get logged in a "Deviations" section with reasons.
2. **Hold out the recent period for prediction.** For the predictive models in 7.4, the Aug 2021-Aug 2023 data is a locked test set until final evaluation. Don't tune or select features on it.
3. **No leakage.** No DPQ item, no DPQ100, no antidepressant use in the main models. Fit all preprocessing inside CV folds with pipelines.
4. **Respect the survey design.** Use weights for prevalence and association estimates, with design-based standard errors using `SDMVSTRA` and `SDMVPSU` (R `survey` package or Python `samplics`). Report weighted and unweighted predictive metrics and explain the difference.
5. **Uncertainty on every headline number.** 95% confidence intervals. Bootstrap CIs need at least 1,000 resamples.
6. **Reproducible.** Fixed seeds, pinned versions in `requirements.txt` (and `renv.lock` if R is used), one command to run everything (`make all`).
7. **No fabrication.** Never invent a number, citation, variable name or result. If something fails, say so.
8. **Honest framing.** Cross-sectional data. Associations, not causes. SHAP describes the model, not biology.

## 7. Analysis plan

### 7.1 Data pipeline
- `src/download.py`: fetch files into `data/raw/`, log checksums, skip files already downloaded.
- `src/harmonize.py`: recode and merge into one table per period, saved as Parquet in `data/processed/`.
- Participant flow diagram for each period, overall and for ages 18 to 25.

### 7.2 Descriptive results
- Table 1: weighted characteristics by outcome, for 18 to 25 and 26+, per period.
- Weighted prevalence of PHQ-9 ≥ 10 by period, age band (18-25, 26-44, 45-64, 65+), sex and income-to-poverty band.
- Sanity check: the recent-period overall estimate should be in the same range as NCHS Data Brief 527 (which covers ages 12+, so it won't match exactly). If it's far off, there's a bug.

### 7.3 Risk factors (Aim 1)
- Survey-weighted logistic regression for each candidate factor, adjusted for age, sex, race/ethnicity and income. Report odds ratios (and prevalence ratios if feasible) with design-based CIs.
- Fit separately for 18 to 25 and 26+, and test age-group interactions.
- Correct for multiple comparisons (for example Benjamini-Hochberg) and say which method you used.

### 7.4 Predictive models
- Majority-class baseline, Logistic Regression (L2 and elastic net), Random Forest, LightGBM.
- One-hot encoding for nominal categories. Stratified 5-fold CV for tuning. Optimize log loss or AUPRC.
- Report AUROC, AUPRC, Brier score, calibration slope and intercept, calibration plots, and performance at a pre-specified threshold (for example 80% sensitivity on development data).
- Evaluate on development CV, then once on the locked recent period.
- Subgroup performance by sex, race/ethnicity and income band, with CIs. Say clearly when groups are too small to interpret.

### 7.5 Explanations and stability
- SHAP (TreeSHAP for tree models; coefficients or linear SHAP for LR).
- Stability across at least 10 seeds and 100 bootstrap resamples: Kendall's tau of rankings, Jaccard overlap of the top 10, spread of mean |SHAP|.
- Compare SHAP, permutation importance and LR coefficients.
- Show a correlation matrix and point out where correlated features split importance.

### 7.6 Sleep overlap (Aim 2, key result)
- **A:** full model with sleep variables.
- **B:** same model without sleep variables.
- **C:** sleep variables kept, outcome rebuilt without DPQ030 and DPQ040 (seven-item score with a matched cutoff). Justify the cutoff choice, and test at least one alternative.
- Do the same for the regression analysis in 7.3: does the sleep association shrink when the sleep and tiredness items are removed from the outcome?
- Report results for 18 to 25 and for all adults. Explain what this means for published claims that sleep "drives" depression risk.
- Secondary ablations: adding antidepressant use, adding self-rated general health. Explain why each stays out of the main model.

### 7.7 Change over time (Aim 3)
- Compare weighted prevalence and adjusted associations across the three periods (period-by-factor interactions).
- Predictive transfer: train on 2005-2016, evaluate on 2017-March 2020 and on Aug 2021-Aug 2023. Report discrimination and calibration for each.
- Compare SHAP rankings across periods.

### 7.8 Replication scorecard (Aim 4)
Every comparison here is synthetic data versus real survey data. "Holds up" means a pattern in the synthetic data is also seen in NHANES. It does not mean the synthetic data are valid.

1. **Reproduce** the original notebook's numbers exactly from the Kaggle file. If they don't match, document why. This is the baseline for the scorecard (Checkpoint 4).
2. **Re-evaluate** the original approach properly on the Kaggle data: majority baseline, AUROC, CV, one-hot encoding, permutation importance.
3. **Map** each original claim to NHANES: testable directly, testable through a proxy (label proxies clearly, for example income-to-poverty ratio or food insecurity for "financial stress"), or not testable (CGPA, academic pressure, family history).
4. **Score** each testable claim against criteria fixed in `analysis_plan.md` before you look: same direction, CI excludes the null, and effect size comparison. Labels: Holds up / Weaker / Doesn't hold up / Not testable.
5. Produce `results/tables/replication_scorecard.csv` and a figure.
6. **Literature audit (bounded).** Find published papers that use this dataset: peer-reviewed papers, plus preprints clearly labelled as preprints. For each, record whether it acknowledges that the data are synthetic. Follow the approach of Gibson et al. (2026, *BMC Medicine*, doi:10.1186/s12916-026-04981-y) where it fits. Fix the search sources, search terms, inclusion rules and stopping rule in `analysis_plan.md` at Checkpoint 3, before the audit runs. Report counts, not judgments about individual authors.

### 7.9 Canadian replication (Aim 5)
- Harmonize CCHS variables to the NHANES feature set. Document every mapping, proxy and gap in `docs/harmonization_cchs.md`.
- Repeat the survey-weighted risk factor analysis (7.3) and the sleep ablation (7.6) for 18 to 25 and 26+.
- Compare effect directions and sizes with NHANES using the same replication criteria as 7.8, fixed in `analysis_plan.md` before running.
- Add the Canadian results to the Explorer as a country option.
- Be explicit about what can't be compared: different years, sampling, variable wording and age or income groupings.

### 7.10 Robustness
- PHQ-9 ≥ 5 outcome.
- Complete-case vs multiple imputation.
- Alternative age cut (18-29) to check the young adult findings aren't fragile to the cutoff.

## 8. The Risk Factor Explorer (public web tool)

A free static website, hosted on GitHub Pages, that presents the results to non-statisticians such as campus counsellors, program planners and students.

Requirements:

- **Population-level only.** It shows precomputed results. It never asks for personal information and never gives an individual risk score.
- **Pages:**
  - *Risk factors:* pick age group, sex, income band and period; see associations with CIs.
  - *The sleep question:* a toggle between the standard PHQ-9 outcome and the version without sleep and tiredness items.
  - *Over time:* how prevalence and key associations changed across periods.
  - *Replication scorecard:* what held up from the original project.
  - *About:* data, methods, limitations, how to cite, link to the repo and report.
- **Plain language** under every chart: what it shows and what it does not show.
- **Uncertainty visible** on every estimate. Grey out or flag estimates from small groups.
- **Safety note** on every page: this is research, not a diagnostic tool, and if someone is struggling they should contact a professional or a crisis line (in Canada and the U.S., call or text 988).
- **Accessible:** colour-blind safe palette, keyboard navigable, readable on phones.
- **Build:** a script exports results to JSON in `explorer/data/`, and the site in `explorer/` reads it. Keep dependencies minimal (plain HTML, CSS and JavaScript, plus one charting library from a CDN). Include instructions for turning on GitHub Pages.

## 9. Repository structure

```
.
├── CLAUDE.md
├── README.md
├── Makefile
├── requirements.txt
├── original_course_project/     (read-only record of the CS-4440 project)
│   ├── README.md
│   ├── proposal/
│   ├── final/
│   └── data/                    (Kaggle CSV, if its license allows)
├── data/
│   ├── raw/                     (gitignored)
│   └── processed/
├── docs/
│   ├── analysis_plan.md
│   ├── harmonization.md
│   └── data_dictionary.md
├── notebooks/                   (exploration only, numbered 01_, 02_, ...)
├── src/                         (all reusable code)
├── tests/
├── results/
│   ├── figures/
│   └── tables/
├── reports/
│   ├── related_work.md
│   ├── paper.md
│   ├── model_card.md
│   └── plain_language_summary.md
└── explorer/                    (the public web tool)
```

Unit tests for anything where a silent error would wreck results: PHQ-9 scoring (including the seven-item version), missing-code handling, weight rescaling, the period split, and the JSON export.

## 10. Deliverables

1. This GitHub repository, clean and reproducible.
2. `reports/paper.md`: a 6 to 10 page paper-style report (abstract, introduction, related work, data, methods, results, discussion, limitations, ethics, references).
3. Publication-quality figures: 300 dpi, labelled axes, colour-blind safe, consistent style.
4. The Risk Factor Explorer, live on GitHub Pages.
5. `reports/model_card.md` for the predictive models.
6. `reports/plain_language_summary.md`: one page for a general reader.
7. A top-level `README.md` explaining the project, how it extends the course project, how to reproduce it, and a link to the Explorer.

## 11. Working in Claude Code on the web

- Each session starts from a fresh clone. `make data` must be idempotent and should skip work that's already done.
- The CDC site may be blocked by the default network setting. If downloads fail, tell me and I'll add `wwwn.cdc.gov` and `www.cdc.gov` (and later `www150.statcan.gc.ca` for CCHS) to the environment's allowed domains.
- NHANES data is public domain. Raw `.XPT` files stay out of git. Processed Parquet files may be committed if their total size stays under about 50 MB, so later sessions start faster. Never commit Healthy Minds data.
- Use clear commit messages. Work on a branch per checkpoint so I can review each one as a pull request.

## 12. Checkpoints (stop and wait for my go-ahead)

1. Literature summary, plus confirmation that NHANES files download correctly.
2. Harmonization table, participant flow and the actual young adult sample sizes, before any modelling.
3. `analysis_plan.md` written and committed, including replication criteria.
4. Reproduction of the original course project numbers.
5. Development-set results (risk factors, models, sleep ablation).
6. Final evaluation on the recent period and the full replication scorecard.
7. CCHS coverage check (which provinces and years have the PHQ-9, and sample sizes), before any Canadian analysis.
8. Canadian replication results.
9. Explorer prototype.
10. First full draft of the paper.

At each checkpoint: what you did, what you found, anything surprising, and any decision you need from me.

## 13. Writing style for all documents

- Plain, direct English. Short sentences.
- No em dashes. No hype words ("groundbreaking," "novel," "robust" unless defined).
- Every claim backed by a number, a figure or a citation.
- Report null and negative results as clearly as positive ones.
- Describe the original course project accurately and without exaggeration, including its flaws.
