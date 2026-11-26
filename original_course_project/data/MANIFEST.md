# Data manifest

| Field | Value |
|---|---|
| File | `Student Depression Dataset.csv` |
| SHA-256 | `a3e159e246789be5a61dcc7b4290fbc238f0140f3d95727585af50a61fd35404` |
| Size | 2,807,716 bytes |
| Rows | 27,901 (plus one header row) |
| Columns | 18 |
| Missing values | 3, all in `Financial Stress` (no other column has missing values) |
| Source | Kaggle, https://www.kaggle.com/datasets/hopesb/student-depression-dataset |
| Author | Shodolamu Opeyemi |
| Licence | Apache License 2.0 |
| Status on Kaggle | Labelled synthetic: "This dataset was synthetically generated and may not reflect real-world data." Tagged "Synthetic". No original data source given. |
| Added to this repository | Commit `32e7c42` on `main` |

Columns: `id`, `Gender`, `Age`, `City`, `Profession`, `Academic Pressure`, `Work Pressure`, `CGPA`, `Study Satisfaction`, `Job Satisfaction`, `Sleep Duration`, `Dietary Habits`, `Degree`, `Have you ever had suicidal thoughts ?`, `Work/Study Hours`, `Financial Stress`, `Family History of Mental Illness`, `Depression`.

## How these values were computed

The checksum comes from `sha256sum`. The row, column and missing-value counts come from `pandas.read_csv` with default settings (pandas 3.0.5). `tests/test_original_data.py` checks all of them on every `make test`.
