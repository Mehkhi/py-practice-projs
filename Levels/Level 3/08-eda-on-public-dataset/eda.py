import pandas as pd
import os

# Load the dataset
data_path = os.path.join('data', 'iris.csv')
df = pd.read_csv(data_path)

# Initial inspection
print("Dataset shape:", df.shape)
print("\nFirst 5 rows:")
print(df.head())

print("\nData types:")
print(df.dtypes)

print("\nColumn names:")
print(df.columns.tolist())

print("\nSummary info:")
print(df.info())

# Check for missing values
print("\nMissing values per column:")
print(df.isnull().sum())

# Basic statistics
print("\nBasic statistics:")
print(df.describe())

# Data cleaning
# For Iris dataset, it's clean, but let's add some steps for demonstration

# Remove duplicates if any
initial_shape = df.shape
df = df.drop_duplicates()
print(f"\nRemoved {initial_shape[0] - df.shape[0]} duplicate rows.")

# Type coercion: Ensure numerical columns are float
numerical_cols = ['sepal_length', 'sepal_width', 'petal_length', 'petal_width']
for col in numerical_cols:
    df[col] = pd.to_numeric(df[col], errors='coerce')

# Check for any NaN introduced
print("\nMissing values after coercion:")
print(df.isnull().sum())

# Drop any rows with NaN (though Iris has none)
df = df.dropna()
print(f"\nShape after cleaning: {df.shape}")

# Save cleaned data
cleaned_path = os.path.join('data', 'iris_cleaned.csv')
df.to_csv(cleaned_path, index=False)
print(f"\nCleaned data saved to {cleaned_path}")
