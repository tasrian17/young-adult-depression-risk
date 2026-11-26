# Related work

Every source below was opened during Checkpoint 1 (November 2026). The reference list says whether the full text or only the abstract was read, and labels preprints, which are not peer reviewed. Claims taken from an abstract go no further than the abstract. Preprints are used for background or as comparisons, never as the only support for a key claim.

## 1. The outcome and the national picture

The PHQ-9 scores the nine DSM-IV depression criteria from 0 to 3 each. Against a clinician interview, a score of 10 or more had 88% sensitivity and 88% specificity for major depression [1]. An individual participant data meta-analysis of 58 studies found that the cutoff of 10 maximised combined sensitivity (0.88) and specificity (0.85) in studies that used semistructured interviews [2]. A positive screen is still not a diagnosis.

NCHS reports that the share of people aged 12 and older with PHQ-9 ≥ 10 rose from 8.2% in 2013-2014 to 13.1% in August 2021-August 2023. It was 16.6% among adults aged 20 to 39 [3]. Public files hold only participants aged 18 and older [4, 5].

**Two changes in 2021-2023 affect comparisons across periods (Aim 3).**
- **The depression questions changed mode.** Up to 2017-March 2020 an interviewer asked them in the mobile examination centre (CAPI). In 2021-2023 participants answered them alone on a computer with audio (ACASI) [3, 4, 5]. The NCHS plan and operations report for the cycle states that all MEC interview questions except the COVID-19 questions were self-administered [6].
- **Response rates fell.** Unweighted interview and examination response rates were 34.6% and 25.7% in 2021-2023, against 51.0% and 46.9% in 2017-March 2020. NCHS's nonresponse bias assessment found no major sources of bias that weighting did not address [7].

I found no NCHS analysis of how the mode change affects PHQ-9 scores. NCHS describes an analysis of a different mode change (dietary recall) as "forthcoming" [7]. So differences between 2021-2023 and earlier periods combine real change with the change in mode, and this data cannot separate them.

## 2. Machine learning for depression in NHANES

This area is crowded. Two examples show the usual design.

- Vu et al. used NHANES 2013-2014 (n = 5,372, 9.5% positive), a single 80/20 split and random undersampling, with no mention of survey weights. Their best model (XGBoost) had an AUC of 0.69. The top SHAP features were income-to-poverty ratio, sex and hypertension [8]. Sleep was not among their predictors.
- Salimi et al. pooled 2005-2006 to 2017-March 2020 (n = 37,959) without survey weights. They used PHQ-9 ≥ 5 and eight predictors (age, sex, education, sleep duration, trouble sleeping, daytime sleepiness, energy and fat intake). LightGBM reached a full-population ROC-AUC of 0.726, with poor calibration. "Self-reported trouble sleeping" was the dominant SHAP feature. Removing the three sleep predictors lowered ROC-AUC to 0.611 [9].

Neither study focuses on 18 to 25 year olds or uses design-based estimates. Neither touches the 2021-2023 cycle.

## 3. Does the PHQ-9 sleep item inflate sleep's importance? (search a)

The PHQ-9 itself asks about sleep (item 3, `DPQ030`) and tiredness (item 4, `DPQ040`). A sleep predictor can therefore look strong partly because the outcome contains a sleep question. Earlier work has handled this in five ways.

1. **Remove the sleep predictors** (Salimi et al. [9]). The authors name the "conceptual overlap between sleep predictors and PHQ-9 symptom content". However, a large drop in AUC after removing the predictors fits two explanations: sleep is truly associated with depression, or the outcome partly measures sleep. This design cannot tell the two apart. It is the same as our Model B.
2. **Adjust for the sleep item as a covariate.** Niu et al. (NHANES 2007-2014, ages 60 and older) added `DPQ030` to their Model 5 while it was still part of the outcome score [10].
3. **Remove item 3 from the outcome.** Al-Ghadban and Salman studied 389 Kuwait University students (mean age 20.2) recruited by convenience. They used linear regression on the total score and a reworded item 3. After removing item 3, sleep quality, disturbance and duration stayed associated with symptoms, but sleep-onset latency did not [11]. This is the closest precedent for the regression half of Aim 2.
4. **Keep sleep predictors that are "measured independently of the PHQ-9".** Malik and En (preprint) pooled NHANES 2007-2018 (31,460 adults) and used survey-weighted logistic regression. They kept predictors asked in separate questions, and set aside those whose wording overlaps with the outcome, such as functional limitations caused by a mental problem. Their largest such association was "reported trouble sleeping" (OR 4.03, 95% CI 3.63 to 4.47) [12]. In one sensitivity analysis they re-tested the sleep domain against "a PHQ-8 outcome, which removes the sleep item". They report only that the sleep contribution "shrank but did not disappear", with no numbers [12]. The standard PHQ-8 drops item 9, not the sleep item [13], and their methods do not say which item they removed. Being asked in a separate question does not remove content overlap: a trouble-sleeping question and PHQ-9 item 3 ask about the same experience. That overlap is what Aim 2 measures.
5. **Rebuild a symptom network without item 3.** In 2,108 Chinese students, the network structure stayed stable [14].

What I did not find:
- an outcome rebuilt without both the sleep and the tiredness items, with a matched binary cutoff;
- that ablation applied to predictive models and SHAP importance;
- that ablation in a national probability sample of young adults, or compared across time periods.

**How Aim 2 is framed in light of this.** Aim 2 removes both `DPQ030` and `DPQ040` from the outcome and rescores it with a matched cutoff. It does this for both the survey-weighted regressions and the predictive models, in 18 to 25 year olds and in all adults, using survey weights. Salimi et al. [9] and Al-Ghadban and Salman [11] are the named comparisons: the first for the predictor-removal approach (Model B), the second for removing an item from the outcome. Malik and En [12] are also compared, as a preprint. Removing the appetite item (item 5) as well is an optional extra sensitivity check (see section 4).

**The PHQ-8 is not prior work on this question.** The PHQ-8 omits item 9 (thoughts of death or self-harm) [13]. It keeps the sleep and tiredness items, so studies using the standard PHQ-8 do not test sleep overlap.

## 4. Somatic items and physical illness (wider context for search a)

Many factor analyses split the PHQ-9 into somatic and cognitive-affective parts.
- In 2,615 Army National Guard soldiers, a two-factor somatic and non-somatic model fit better than a one-factor model [15].
- In NHANES 2005-2021 data on women, the somatic factor was sleep, fatigue and appetite [16].
- After myocardial infarction, somatic-affective symptoms on the Beck Depression Inventory tracked cardiac health status. Cognitive-affective symptoms did so only marginally [17].

This work asks a measurement question: do somatic items measure depression, physical illness, or both? Aim 2 asks something narrower. When a predictor and the outcome share content (self-reported sleep on both sides), how much of the predictor's association and model importance comes from that shared content? The factor literature does support treating items 3 and 4 as the overlap candidates. It also motivates the optional check that removes appetite (item 5) too.

## 5. Kaggle and convenience data checked against validated data (search b)

I found no study that tests findings from a Kaggle mental health dataset against validated survey data. Related work:
- **Kaggle provenance, and the precedent for our paper audit.** Gibson et al. audited two widely used Kaggle datasets on stroke and diabetes [18]. They searched Google Scholar (on 15 August 2025) using identifying terms from the datasets' Kaggle web addresses. They did not use PubMed because those terms retrieved nothing relevant there. They checked full texts to confirm each paper used the dataset, and kept only peer-reviewed prediction model studies (no preprints, conference abstracts or theses). Of 653 search results, 125 studies were included and assessed against nine TRIPOD+AI checklist items. Neither dataset could be verified as authentic [18]. This is the closest methodological precedent for the bounded paper audit in Aim 4. Ours differs in three ways:
  1. It is about mental health data.
  2. Its dataset is openly labelled synthetic, so the question is whether papers acknowledge that, not whether the data are authentic.
  3. It sits beside a direct comparison of the dataset's patterns with validated national data. It also counts preprints, labelled as such, which Gibson et al. excluded.
- **Clinical mental health datasets.** As background only, a review posted as a preprint describes them as scattered, under-documented and often inaccessible [19].
- **Convenience versus representative samples.** An online convenience sample of older adults reported better mental health than a representative sample. It also lacked the representative sample's rise in depression with age [20].
- **The course project's own dataset is labelled synthetic.** Washton et al. describe the Kaggle Student Depression Dataset (27,901 records) as synthetic. They say its depression label "was generated algorithmically based on weighted combinations of the predictor variables" [21]. The Kaggle page confirms the synthetic label directly. It states: "This dataset was synthetically generated and may not reflect real-world data." It carries a "Synthetic" tag and gives no original data source [22]. The page gives no details of how the data were generated, so the statement about the label's construction rests on Washton et al. alone. Either way, patterns in this dataset are not evidence about real students. Aim 4 asks which of them happen to match validated data.

## 6. Where this project fits

This project adds four things that earlier work does not cover:
1. design-based estimates for 18 to 25 year olds in NHANES;
2. an outcome-side sleep ablation (dropping `DPQ030` and `DPQ040`), applied to both regression and prediction;
3. a three-period comparison that states plainly that 2021-2023 differences mix real change with the change in interview mode and lower response;
4. a test of whether findings from a dataset labelled synthetic hold up in validated data, with a count of published papers that use it and whether they say it is synthetic.

## References

1. Kroenke K, Spitzer RL, Williams JB. The PHQ-9: validity of a brief depression severity measure. *J Gen Intern Med*. 2001;16(9):606-613. doi:10.1046/j.1525-1497.2001.016009606.x [abstract only]
2. Levis B, Benedetti A, Thombs BD; DEPRESSD Collaboration. Accuracy of Patient Health Questionnaire-9 (PHQ-9) for screening to detect major depression: individual participant data meta-analysis. *BMJ*. 2019;365:l1476. doi:10.1136/bmj.l1476 [abstract only]
3. Brody DJ, Hughes JP. Depression prevalence in adolescents and adults: United States, August 2021-August 2023. NCHS Data Brief No. 527. April 2025. doi:10.15620/cdc/174579 [full text]
4. National Center for Health Statistics. NHANES August 2021-August 2023 Data Documentation: Mental Health - Depression Screener (DPQ_L). First published September 2024. https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2021/DataFiles/DPQ_L.htm [full text]
5. National Center for Health Statistics. NHANES 2017-March 2020 Pre-pandemic Data Documentation: Mental Health - Depression Screener (P_DPQ). First published June 2021. https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2017/DataFiles/P_DPQ.htm [full text]
6. National Center for Health Statistics. Plan and operations of the National Health and Nutrition Examination Survey, August 2021-August 2023. Vital and Health Statistics, Series 1, No. 66. May 2024. https://www.cdc.gov/nchs/data/series/sr_01/sr01-066.pdf [full text]
7. National Center for Health Statistics. Brief overview of sample design, nonresponse bias assessment, and analytic guidelines for NHANES August 2021-August 2023. https://wwwn.cdc.gov/nchs/nhanes/ContinuousNhanes/OverviewBrief.aspx?Cycle=2021-2023 (accessed 26 November 2026) [full text]
8. Vu T, Dawadi R, Yamamoto M, et al. Prediction of depressive disorder using machine learning approaches: findings from the NHANES. *BMC Med Inform Decis Mak*. 2025;25:83. doi:10.1186/s12911-025-02903-1 [full text]
9. Salimi O, Ghahramani Z, Taghavi Zenouz M, et al. Interpretable machine learning for depression symptom classification in NHANES: performance in a curated high-confidence corpus and the full survey population. *IBRO Neurosci Rep*. 2026;21:738-746. doi:10.1016/j.ibneur.2026.08.009 [full text, open-access copy in Europe PMC, PMC13563247]
10. Niu Y, Sun Y, Xie Y, Yu S. Association between sleep patterns and depression in older adults: a cross-sectional study using data from the National Health and Nutrition Examination Survey 2007-2014. *BMC Geriatr*. 2025;25:56. doi:10.1186/s12877-024-05633-7 [full text]
11. Al-Ghadban F, Salman A. Sleep characteristics and mental health among Kuwait University students: sensitivity analyses for item overlap. *Behav Sci (Basel)*. 2026;16:1446. doi:10.3390/bs16081446 [full text]
12. Malik MI, En WQ. Socioeconomic and sleep correlates of a positive depression screen, and the limited added value of laboratory measurement: a design-based analysis of NHANES 2007-2018. Research Square. Posted 6 August 2026. doi:10.21203/rs.3.rs-10577122/v1 [full text; preprint, not peer reviewed]
13. Wu Y, Levis B, Riehm KE, et al. Equivalency of the diagnostic accuracy of the PHQ-8 and PHQ-9: a systematic review and individual participant data meta-analysis. *Psychol Med*. 2020;50(8):1368-1380. doi:10.1017/S0033291719001314 [abstract only]
14. Wu X, Wang X. Depression, anxiety, and sleep problems among Chinese university students enrolled in basketball elective courses: a network psychometric analysis. *Front Psychol*. 2026;17:1738600. doi:10.3389/fpsyg.2026.1738600 [abstract only]
15. Elhai JD, Contractor AA, Tamburrino M, et al. The factor structure of major depression symptoms: a test of four competing models using the Patient Health Questionnaire-9. *Psychiatry Res*. 2012;199(3):169-173. doi:10.1016/j.psychres.2012.05.018 [abstract only]
16. Srisurapanont M, Suradom C, Maneeton N, Oon-Arom A, Maneeton B. Depressive symptom profiles across pregnant, postpartum, and nonperipartum women: measurement invariance and differential item functioning analyses of 2005-2021 NHANES data. *BMC Public Health*. 2026;26:2523. doi:10.1186/s12889-026-28575-8 [abstract only]
17. de Jonge P, Ormel J, van den Brink RH, et al. Symptom dimensions of depression following myocardial infarction and their relationship with somatic health status and cardiovascular prognosis. *Am J Psychiatry*. 2006;163(1):138-144. doi:10.1176/appi.ajp.163.1.138 [abstract only]
18. Gibson AD, White NM, Collins GS, Barnett AG. Evidence of unreliable data and poor data provenance in clinical prediction model research and clinical practice. *BMC Med*. 2026;24:386. doi:10.1186/s12916-026-04981-y [full text]
19. Mandal A, Adhikary PK, Arnaout H, Gurevych I, Chakraborty T. A comprehensive review of datasets for clinical mental health AI systems. arXiv:2508.09809v2. 2025. https://arxiv.org/abs/2508.09809 [abstract only; preprint, not peer reviewed; background only]
20. Georgi H, Dragomirecká E, Tichá Z, Mana J. Depression and anxiety in older adults: a comparison between online convenience and conventional representative sampling. *Depress Anxiety*. 2025;2025:2522358. doi:10.1155/da/2522358 [abstract only]
21. Washton J, Owens T, Sierra A, Toma M. Identifying predictors of student depression through validated machine learning pipelines. *Front Med*. 2026;13:1864665. doi:10.3389/fmed.2026.1864665 [full text, data section]
22. Opeyemi S. Student Depression Dataset. Kaggle. Apache License 2.0. https://www.kaggle.com/datasets/hopesb/student-depression-dataset (accessed 26 November 2026; read in a browser by the project author, because the page returned no content to automated requests from this environment) [full text]
