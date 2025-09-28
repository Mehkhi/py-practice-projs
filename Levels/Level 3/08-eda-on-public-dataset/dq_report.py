import pandas as pd
import os
import numpy as np
from scipy import stats

# Load cleaned data
data_path = os.path.join('data', 'iris_cleaned.csv')
df = pd.read_csv(data_path)

# Descriptive statistics
print("Descriptive Statistics:")
desc_stats = df.describe()
print(desc_stats)

# Group by species
print("\nDescriptive Statistics by Species:")
grouped_stats = df.groupby('species').describe()
print(grouped_stats)

# Data Quality Checks
print("\nData Quality Report:")
print("=" * 50)

# Missing values
missing = df.isnull().sum()
print("Missing Values:")
print(missing[missing > 0] if missing.any() else "No missing values.")

# Duplicates
duplicates = df.duplicated().sum()
print(f"\nNumber of duplicate rows: {duplicates}")

# Outliers using IQR
print("\nOutlier Detection (IQR method):")
for col in df.select_dtypes(include=[np.number]).columns:
    Q1 = df[col].quantile(0.25)
    Q3 = df[col].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)]
    print(f"{col}: {len(outliers)} outliers")

# Distribution checks (skewness and kurtosis)
print("\nDistribution Checks:")
for col in df.select_dtypes(include=[np.number]).columns:
    skew = df[col].skew()
    kurt = df[col].kurtosis()
    print(f"{col} - Skewness: {skew:.2f}, Kurtosis: {kurt:.2f}")

# Unique values
print("\nUnique Values per Column:")
for col in df.columns:
    unique_count = df[col].nunique()
    print(f"{col}: {unique_count} unique values")

# Save DQ report to markdown
report_path = os.path.join('reports', 'dq_report.md')
os.makedirs('reports', exist_ok=True)

with open(report_path, 'w') as f:
    f.write("# Data Quality Report\n\n")
    f.write("## Descriptive Statistics\n")
    f.write(desc_stats.to_markdown() + "\n\n")
    f.write("## Statistics by Species\n")
    f.write(grouped_stats.to_markdown() + "\n\n")
    f.write("## Data Quality Checks\n")
    f.write(f"- Missing Values: {missing.sum()}\n")
    f.write(f"- Duplicate Rows: {duplicates}\n")
    f.write("- Outliers detected using IQR method.\n")
    f.write("- Distribution checks performed for skewness and kurtosis.\n")

print(f"\nDQ report saved to {report_path}")
