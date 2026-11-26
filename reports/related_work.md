# Related work

Every source below was opened during Checkpoint 1 (November 2026). The reference list says whether the full text or only the abstract was read. Claims taken from an abstract go no further than the abstract.

## 1. The outcome and the national picture

The PHQ-9 scores the nine DSM-IV depression criteria from 0 to 3 each. Against a clinician interview, a score of 10 or more had 88% sensitivity and 88% specificity for major depression [1]. An individual participant data meta-analysis of 58 studies found that the cutoff of 10 maximised combined sensitivity (0.88) and specificity (0.85) in studies that used semistructured interviews [2]. A positive screen is still not a diagnosis.

NCHS reports that the share of people aged 12 and older with PHQ-9 ≥ 10 rose from 8.2% in 2013-2014 to 13.1% in August 2021-August 2023. It was 16.6% among adults aged 20 to 39 [3]. The same report notes that in 2021-2023 the depression questions moved to audio computer-assisted self-interview (ACASI) [3]. The CDC codebooks confirm that earlier cycles used an interviewer (CAPI). They also confirm that public files hold only participants aged 18 and older [4, 5]. Any comparison across periods (Aim 3) has to treat this mode change as a possible cause of the rise, not just a real change in depression.

## 2. Machine learning for depression in NHANES

This area is crowded. Two examples show the usual design.

- Vu et al. used NHANES 2013-2014 (n = 5,372, 9.5% positive), a single 80/20 split and random undersampling, with no mention of survey weights. Their best model (XGBoost) had an AUC of 0.69. The top SHAP features were income-to-poverty ratio, sex and hypertension [6]. Sleep was not among their predictors.
- Salimi et al. pooled 2005-2006 to 2017-March 2020 (n = 37,959) without survey weights. They used PHQ-9 ≥ 5 and eight predictors (age, sex, education, sleep duration, trouble sleeping, daytime sleepiness, energy and fat intake). LightGBM reached a full-population ROC-AUC of 0.726, with poor calibration. "Self-reported trouble sleeping" was the dominant SHAP feature. Removing the three sleep predictors lowered ROC-AUC to 0.611 [7].

Neither study focuses on 18 to 25 year olds or uses design-based estimates. Neither touches the 2021-2023 cycle.

## 3. Does the PHQ-9 sleep item inflate sleep's importance? (search a)

The PHQ-9 itself asks about sleep (item 3, `DPQ030`) and tiredness (item 4, `DPQ040`). A sleep predictor can therefore look strong partly because the outcome contains a sleep question. I found four ways that earlier work has handled this.

1. **Remove the sleep predictors** (Salimi et al. [7]). The authors name the "conceptual overlap between sleep predictors and PHQ-9 symptom content". However, a large drop in AUC after removing the predictors fits two explanations: sleep is truly associated with depression, or the outcome partly measures sleep. This design cannot tell the two apart. It is the same as our Model B.
2. **Adjust for the sleep item as a covariate.** Niu et al. (NHANES 2007-2014, ages 60 and older) added `DPQ030` to their Model 5 while it was still part of the outcome score [8].
3. **Remove item 3 from the outcome.** Al-Ghadban and Salman studied 389 Kuwait University students (mean age 20.2) recruited by convenience. They used linear regression on the total score and a reworded item 3. After removing item 3, sleep quality, disturbance and duration stayed associated with symptoms, but sleep-onset latency did not [9]. This is the closest precedent for the regression half of Aim 2.
4. **Rebuild a symptom network without item 3.** In 2,108 Chinese students, the network structure stayed stable [10].

What I did not find:
- an outcome rebuilt without both the sleep and the tiredness items, with a matched binary cutoff;
- that ablation applied to predictive models and SHAP importance;
- that ablation in a national probability sample of young adults, or compared across time periods.

**The PHQ-8 is not prior work on this question.** The PHQ-8 omits item 9 (thoughts of death or self-harm) [11]. It keeps the sleep and tiredness items, so studies using it do not test sleep overlap.

## 4. Somatic items and physical illness (wider context for search a)

Many factor analyses split the PHQ-9 into somatic and cognitive-affective parts.
- In 2,615 Army National Guard soldiers, a two-factor somatic and non-somatic model fit better than a one-factor model [12].
- In NHANES 2005-2021 data on women, the somatic factor was sleep, fatigue and appetite [13].
- After myocardial infarction, somatic-affective symptoms on the Beck Depression Inventory tracked cardiac health status. Cognitive-affective symptoms did so only marginally [14].

This work asks a measurement question: do somatic items measure depression, physical illness, or both? Aim 2 asks something narrower. When a predictor and the outcome share content (self-reported sleep on both sides), how much of the predictor's association and model importance comes from that shared content? The factor literature does support treating items 3 and 4 as the overlap candidates. It also suggests appetite (item 5) as an optional extra sensitivity check.

## 5. Kaggle and convenience data checked against validated data (search b)

I found no study that tests findings from a Kaggle mental health dataset against validated survey data. Related work:
- **Kaggle provenance.** Gibson et al. audited two widely used Kaggle datasets on stroke and diabetes. Neither could be verified as authentic, yet 125 published prediction models were built on them [15].
- **Convenience versus representative samples.** An online convenience sample of older adults reported better mental health than a representative sample. It also lacked the representative sample's rise in depression with age [16].
- **The course project's own dataset.** Washton et al. describe the Kaggle Student Depression Dataset (27,901 records) as synthetic. They say its depression label "was generated algorithmically based on weighted combinations of the predictor variables", and that the data "do not originate from any real-world location, population, or data collection effort" [17]. Their only source for this is the Kaggle page. I could not open that page from this environment, so this is not yet confirmed. If it is correct, the original project's feature rankings describe how the data were generated, not real students. Aim 4 would then compare a simulation with survey data, not two samples of people.

## 6. Where this project fits

This project adds four things that earlier work does not cover:
1. design-based estimates for 18 to 25 year olds in NHANES;
2. an outcome-side sleep ablation (dropping `DPQ030` and `DPQ040`), applied to both regression and prediction;
3. a three-period comparison that accounts for the 2021 change in interview mode;
4. a test of whether findings from an undocumented, possibly synthetic, dataset hold up in validated data.

## References

1. Kroenke K, Spitzer RL, Williams JB. The PHQ-9: validity of a brief depression severity measure. *J Gen Intern Med*. 2001;16(9):606-613. doi:10.1046/j.1525-1497.2001.016009606.x [abstract only]
2. Levis B, Benedetti A, Thombs BD; DEPRESSD Collaboration. Accuracy of Patient Health Questionnaire-9 (PHQ-9) for screening to detect major depression: individual participant data meta-analysis. *BMJ*. 2019;365:l1476. doi:10.1136/bmj.l1476 [abstract only]
3. Brody DJ, Hughes JP. Depression prevalence in adolescents and adults: United States, August 2021-August 2023. NCHS Data Brief No. 527. April 2025. doi:10.15620/cdc/174579 [full text]
4. National Center for Health Statistics. NHANES August 2021-August 2023 Data Documentation: Mental Health - Depression Screener (DPQ_L). First published September 2024. https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2021/DataFiles/DPQ_L.htm [full text]
5. National Center for Health Statistics. NHANES 2017-March 2020 Pre-pandemic Data Documentation: Mental Health - Depression Screener (P_DPQ). First published June 2021. https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2017/DataFiles/P_DPQ.htm [full text]
6. Vu T, Dawadi R, Yamamoto M, et al. Prediction of depressive disorder using machine learning approaches: findings from the NHANES. *BMC Med Inform Decis Mak*. 2025;25:83. doi:10.1186/s12911-025-02903-1 [full text]
7. Salimi O, Ghahramani Z, Taghavi Zenouz M, et al. Interpretable machine learning for depression symptom classification in NHANES: performance in a curated high-confidence corpus and the full survey population. *IBRO Neurosci Rep*. 2026;21:738-746. doi:10.1016/j.ibneur.2026.08.009 [full text, via Europe PMC PMC13563247]
8. Niu Y, Sun Y, Xie Y, Yu S. Association between sleep patterns and depression in older adults: a cross-sectional study using data from the National Health and Nutrition Examination Survey 2007-2014. *BMC Geriatr*. 2025;25:56. doi:10.1186/s12877-024-05633-7 [full text]
9. Al-Ghadban F, Salman A. Sleep characteristics and mental health among Kuwait University students: sensitivity analyses for item overlap. *Behav Sci (Basel)*. 2026;16:1446. doi:10.3390/bs16081446 [full text]
10. Wu X, Wang X. Depression, anxiety, and sleep problems among Chinese university students enrolled in basketball elective courses: a network psychometric analysis. *Front Psychol*. 2026;17:1738600. doi:10.3389/fpsyg.2026.1738600 [abstract only]
11. Wu Y, Levis B, Riehm KE, et al. Equivalency of the diagnostic accuracy of the PHQ-8 and PHQ-9: a systematic review and individual participant data meta-analysis. *Psychol Med*. 2020;50(8):1368-1380. doi:10.1017/S0033291719001314 [abstract only]
12. Elhai JD, Contractor AA, Tamburrino M, et al. The factor structure of major depression symptoms: a test of four competing models using the Patient Health Questionnaire-9. *Psychiatry Res*. 2012;199(3):169-173. doi:10.1016/j.psychres.2012.05.018 [abstract only]
13. Srisurapanont M, Suradom C, Maneeton N, Oon-Arom A, Maneeton B. Depressive symptom profiles across pregnant, postpartum, and nonperipartum women: measurement invariance and differential item functioning analyses of 2005-2021 NHANES data. *BMC Public Health*. 2026;26:2523. doi:10.1186/s12889-026-28575-8 [abstract only]
14. de Jonge P, Ormel J, van den Brink RH, et al. Symptom dimensions of depression following myocardial infarction and their relationship with somatic health status and cardiovascular prognosis. *Am J Psychiatry*. 2006;163(1):138-144. doi:10.1176/appi.ajp.163.1.138 [abstract only]
15. Gibson AD, White NM, Collins GS, Barnett AG. Evidence of unreliable data and poor data provenance in clinical prediction model research and clinical practice. *BMC Med*. 2026;24:386. doi:10.1186/s12916-026-04981-y [abstract only]
16. Georgi H, Dragomirecká E, Tichá Z, Mana J. Depression and anxiety in older adults: a comparison between online convenience and conventional representative sampling. *Depress Anxiety*. 2025;2025:2522358. doi:10.1155/da/2522358 [abstract only]
17. Washton J, Owens T, Sierra A, Toma M. Identifying predictors of student depression through validated machine learning pipelines. *Front Med*. 2026;13:1864665. doi:10.3389/fmed.2026.1864665 [full text, data section]
