import pandas as pd
import click
import os

@click.command()
@click.option('--input-path', default='data/iris.csv', help='Path to input dataset')
@click.option('--output-path', default='data/cleaned.csv', help='Path to output cleaned dataset')
@click.option('--remove-duplicates', is_flag=True, help='Remove duplicate rows')
@click.option('--fill-missing', type=str, help='Method to fill missing values (mean, median, mode)')
def etl_pipeline(input_path, output_path, remove_duplicates, fill_missing):
    """Parameterized ETL pipeline for data cleaning."""

    # Load data
    df = pd.read_csv(input_path)
    print(f"Loaded data from {input_path}, shape: {df.shape}")

    # Remove duplicates if flag is set
    if remove_duplicates:
        initial_shape = df.shape
        df = df.drop_duplicates()
        print(f"Removed {initial_shape[0] - df.shape[0]} duplicate rows.")

    # Fill missing values if specified
    if fill_missing:
        for col in df.select_dtypes(include=[np.number]).columns:
            if fill_missing == 'mean':
                df[col].fillna(df[col].mean(), inplace=True)
            elif fill_missing == 'median':
                df[col].fillna(df[col].median(), inplace=True)
            elif fill_missing == 'mode':
                df[col].fillna(df[col].mode()[0], inplace=True)
        print(f"Filled missing values using {fill_missing} method.")

    # Save cleaned data
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"Cleaned data saved to {output_path}")

if __name__ == '__main__':
    etl_pipeline()
