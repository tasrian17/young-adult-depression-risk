# Original Course Project (CS-4440 Data Science, Winter 2026)

This folder is a read-only record of the course project this repository extends. Nothing here is edited after it was added.

**Title:** Predicting Student Mental Health Risk Using Academic Performance and Lifestyle Factors
**Author:** Tasrian Ahmed, University of Prince Edward Island

## Contents

| Path | What it is |
|---|---|
| `proposal/TasrianAhmed_Proposal.pdf` | Project proposal |
| `proposal/TasrianAhmed_EDA_Proposal.ipynb` | Exploratory data analysis submitted with the proposal |
| `final/TasrianAhmed_Project_Report.pdf` | Final project report |
| `final/TasrianAhmed_Final_Notebook.ipynb` | Final notebook with the modelling |
| `data/` | The Kaggle CSV (synthetic data, Apache License 2.0), its checksum in `MANIFEST.md`, and the licence text in `LICENSE`. |

## Dataset

Student Depression Dataset, Kaggle: https://www.kaggle.com/datasets/hopesb/student-depression-dataset

**Credit and licence.** The dataset was created by Shodolamu Opeyemi and is published on Kaggle under the Apache License 2.0. The checksum of the copy in `data/` is in `data/MANIFEST.md`.

**The dataset is labelled synthetic.** Its Kaggle page states: "This dataset was synthetically generated and may not reflect real-world data." The page carries a "Synthetic" tag and gives no original data source. The course project treated the data as real student records and did not account for this.

The notebooks expect the CSV at `/content/Student Depression Dataset.csv` (the Google Colab path used at the time). The analysis in this repository reads it from `original_course_project/data/` instead.

## Why it is being extended

The source, sampling method and depression measure behind this dataset are not documented, so its findings can't be checked. The main project in this repository tests which of these findings hold up in validated national survey data. See the top-level `README.md`.
