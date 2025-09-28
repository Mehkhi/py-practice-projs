# EDA on Public Dataset - Iris Dataset

This project performs exploratory data analysis (EDA) on the Iris dataset from the UCI Machine Learning Repository.

## Project Structure

- `data/`: Contains the raw and cleaned datasets
- `plots/`: Saved visualizations
- `reports/`: Data quality report
- `eda.py`: Main script for data loading and cleaning
- `dq_report.py`: Script for generating descriptive statistics and DQ report
- `visualizations.py`: Script for creating visualizations
- `eda_notebook.ipynb`: Jupyter notebook with the full analysis
- `download_dataset.py`: Script to download the dataset

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Download the dataset:
   ```bash
   python download_dataset.py
   ```

3. Run the analysis:
   ```bash
   python eda.py
   python dq_report.py
   python visualizations.py
   ```

4. Open the notebook:
   ```bash
   jupyter notebook eda_notebook.ipynb
   ```

## Key Findings

- The dataset contains 150 samples with 4 features and 3 species
- No missing values or duplicates
- Features have different scales, with petal features showing more variation
- Species are well-separated, especially by petal length and width
- Some outliers present in sepal width

## Bonus Features

- Baseline model implementation
- Parameterized pipeline
- Pre-commit hooks

## Reproducibility

All scripts are designed to be reproducible. The notebook runs top-to-bottom without errors.
