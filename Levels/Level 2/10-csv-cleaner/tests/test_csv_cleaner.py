"""Comprehensive tests for CSV Cleaner."""

import pytest
import pandas as pd
import numpy as np
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, mock_open

from csv_cleaner.core import CSVCleaner


class TestCSVCleaner:
    """Test cases for CSVCleaner class."""

    def setup_method(self):
        """Setup test fixtures before each test method."""
        self.cleaner = CSVCleaner()
        self.sample_data = {
            'Name': ['John', 'Jane', 'Bob', 'Alice', 'Charlie'],
            'Age': [25, 30, None, 28, 35],
            'Salary': [50000, 60000, 55000, None, 70000],
            'Department': ['Engineering', 'Marketing', 'Engineering', 'Sales', None],
            'Email': ['john@email.com', 'jane@email.com', 'bob@email.com', 'alice@email.com', 'charlie@email.com']
        }
        self.sample_df = pd.DataFrame(self.sample_data)

    def test_initialization(self):
        """Test CSVCleaner initialization."""
        cleaner = CSVCleaner()
        assert cleaner.config is not None
        assert cleaner.cleaning_stats['original_rows'] == 0
        assert len(cleaner.error_log) == 0

    def test_initialization_with_config(self):
        """Test CSVCleaner initialization with config file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("""
missing_value_strategies:
  drop: true
  fill_numeric: "median"
column_normalization:
  lowercase: false
""")
            config_path = f.name

        try:
            cleaner = CSVCleaner(config_path)
            assert cleaner.config['missing_value_strategies']['drop'] is True
            assert cleaner.config['missing_value_strategies']['fill_numeric'] == "median"
            assert cleaner.config['column_normalization']['lowercase'] is False
        finally:
            os.unlink(config_path)

    def test_partial_config_preserves_default_options(self):
        """Partial nested config overrides should retain unspecified defaults."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("""
type_detection:
  force_types:
    age: int64
""")
            config_path = f.name

        try:
            cleaner = CSVCleaner(config_path)
            assert cleaner.config['type_detection']['auto_detect'] is True
            assert cleaner.config['type_detection']['force_types']['age'] == 'int64'
        finally:
            os.unlink(config_path)

    def test_load_csv_success(self):
        """Test successful CSV loading."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            self.sample_df.to_csv(f.name, index=False)
            file_path = f.name

        try:
            df = self.cleaner.load_csv(file_path)
            assert len(df) == 5
            assert len(df.columns) == 5
            assert self.cleaner.cleaning_stats['original_rows'] == 5
        finally:
            os.unlink(file_path)

    def test_load_csv_file_not_found(self):
        """Test CSV loading with non-existent file."""
        with pytest.raises(FileNotFoundError):
            self.cleaner.load_csv('nonexistent.csv')

    def test_load_csv_empty_file(self):
        """Test CSV loading with empty file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write('')
            file_path = f.name

        try:
            with pytest.raises(pd.errors.EmptyDataError):
                self.cleaner.load_csv(file_path)
        finally:
            os.unlink(file_path)

    def test_normalize_columns(self):
        """Test column name normalization."""
        df_with_spaces = pd.DataFrame({
            ' First Name ': ['John', 'Jane'],
            'Last Name': ['Doe', 'Smith'],
            'Email Address': ['john@email.com', 'jane@email.com']
        })

        normalized_df = self.cleaner.normalize_columns(df_with_spaces)

        expected_columns = ['first_name', 'last_name', 'email_address']
        assert list(normalized_df.columns) == expected_columns
        assert self.cleaner.cleaning_stats['columns_normalized'] == 3

    def test_normalize_columns_duplicates(self):
        """Test column normalization with duplicate names."""
        df_with_duplicates = pd.DataFrame({
            'Name': ['John', 'Jane'],
            'name': ['Doe', 'Smith'],
            'NAME': ['Engineer', 'Manager']
        })

        normalized_df = self.cleaner.normalize_columns(df_with_duplicates)

        # Should have unique column names
        assert len(normalized_df.columns) == 3
        assert len(set(normalized_df.columns)) == 3

    def test_handle_missing_values_drop(self):
        """Test missing value handling with drop strategy."""
        self.cleaner.config['missing_value_strategies']['drop'] = True

        df_cleaned = self.cleaner.handle_missing_values(self.sample_df.copy())

        # Should drop rows with any missing values
        assert len(df_cleaned) == 2  # Only rows without missing values
        assert self.cleaner.cleaning_stats['dropped_rows'] == 3
        assert self.cleaner.cleaning_stats['missing_values_filled'] == 0

    def test_handle_missing_values_fill(self):
        """Test missing value handling with fill strategy."""
        self.cleaner.config['missing_value_strategies']['drop'] = False
        self.cleaner.config['missing_value_strategies']['fill_numeric'] = 'mean'
        self.cleaner.config['missing_value_strategies']['fill_categorical'] = 'mode'

        df_cleaned = self.cleaner.handle_missing_values(self.sample_df.copy())

        # Should fill missing values
        assert len(df_cleaned) == 5  # No rows dropped
        assert df_cleaned['Age'].isnull().sum() == 0
        assert df_cleaned['Salary'].isnull().sum() == 0
        assert df_cleaned['Department'].isnull().sum() == 0
        assert self.cleaner.cleaning_stats['missing_values_filled'] == 3

    def test_detect_outliers_enabled(self):
        """Test outlier detection when enabled."""
        self.cleaner.config['outlier_detection']['enabled'] = True

        # Create data with outliers
        outlier_data = {
            'values': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 100]  # 100 is an outlier
        }
        df_with_outliers = pd.DataFrame(outlier_data)

        df_cleaned = self.cleaner.detect_outliers(df_with_outliers)

        # Should add outlier flag column
        assert 'values_outlier' in df_cleaned.columns
        assert df_cleaned['values_outlier'].sum() == 1  # One outlier detected

    def test_detect_outliers_disabled(self):
        """Test outlier detection when disabled."""
        self.cleaner.config['outlier_detection']['enabled'] = False

        df_cleaned = self.cleaner.detect_outliers(self.sample_df.copy())

        # Should not add outlier columns
        outlier_columns = [col for col in df_cleaned.columns if col.endswith('_outlier')]
        assert len(outlier_columns) == 0

    def test_coerce_types_auto_detect(self):
        """Test automatic type detection and conversion."""
        self.cleaner.config['type_detection']['auto_detect'] = True

        # Create data with string numbers
        data = {
            'numeric_strings': ['1', '2', '3', '4', '5'],
            'mixed_data': ['1', '2', 'not_a_number', '4', '5']
        }
        df = pd.DataFrame(data)

        df_cleaned = self.cleaner.coerce_types(df)

        # Should convert numeric strings to numeric
        assert pd.api.types.is_numeric_dtype(df_cleaned['numeric_strings'])
        # Mixed data should remain as object
        assert df_cleaned['mixed_data'].dtype == 'object'

    def test_coerce_types_force_types(self):
        """Test forced type conversion."""
        self.cleaner.config['type_detection']['force_types'] = {
            'Age': 'int64',
            'Salary': 'float64'
        }

        # Create a DataFrame without NaN values for int conversion
        test_df = pd.DataFrame({
            'Age': [25, 30, 28, 35],
            'Salary': [50000.0, 60000.0, 55000.0, 70000.0]
        })

        df_cleaned = self.cleaner.coerce_types(test_df)

        assert df_cleaned['Age'].dtype == 'int64'
        assert df_cleaned['Salary'].dtype == 'float64'

    def test_clean_csv_full_pipeline(self):
        """Test complete CSV cleaning pipeline."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            self.sample_df.to_csv(f.name, index=False)
            file_path = f.name

        try:
            df_cleaned = self.cleaner.clean_csv(file_path)

            # Should have cleaned data
            assert len(df_cleaned) > 0
            assert self.cleaner.cleaning_stats['original_rows'] == 5
            assert self.cleaner.cleaning_stats['cleaned_rows'] > 0
        finally:
            os.unlink(file_path)

    def test_export_cleaned_csv(self):
        """Test CSV export functionality."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            self.sample_df.to_csv(f.name, index=False)
            input_path = f.name

        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as f:
            output_path = f.name

        try:
            # Clean and export
            df_cleaned = self.cleaner.clean_csv(input_path)
            self.cleaner.export_cleaned_csv(df_cleaned, output_path)

            # Check if files were created
            assert os.path.exists(output_path)
            assert os.path.exists(output_path.replace('.csv', '_summary.txt'))

            # Verify exported CSV
            exported_df = pd.read_csv(output_path)
            assert len(exported_df) == self.cleaner.cleaning_stats['cleaned_rows']
        finally:
            for path in [input_path, output_path, output_path.replace('.csv', '_summary.txt')]:
                if os.path.exists(path):
                    os.unlink(path)

    def test_error_logging(self):
        """Test error logging functionality."""
        # Force an error by trying to convert invalid data
        self.cleaner.config['type_detection']['force_types'] = {
            'Name': 'int64'  # This should fail
        }

        self.cleaner.coerce_types(self.sample_df.copy())

        # Should have logged an error
        assert len(self.cleaner.error_log) > 0
        assert 'Type conversion failed' in self.cleaner.error_log[0]

    def test_config_loading_error(self):
        """Test configuration loading with invalid file."""
        # Should not raise exception, should use defaults and log warning
        cleaner = CSVCleaner('nonexistent_config.yaml')
        assert cleaner.config is not None
        # Check that it's using default config
        assert cleaner.config['missing_value_strategies']['drop'] is True

    def test_config_loading_invalid_yaml(self):
        """Test configuration loading with invalid YAML."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("invalid: yaml: content: [")
            config_path = f.name

        try:
            # Should not raise exception, should use defaults
            cleaner = CSVCleaner(config_path)
            assert cleaner.config is not None
        finally:
            os.unlink(config_path)

    def test_edge_case_empty_dataframe(self):
        """Test handling of empty DataFrame."""
        empty_df = pd.DataFrame()

        # Should handle empty DataFrame gracefully
        normalized_df = self.cleaner.normalize_columns(empty_df)
        assert len(normalized_df) == 0

        cleaned_df = self.cleaner.handle_missing_values(empty_df)
        assert len(cleaned_df) == 0

    def test_edge_case_all_missing_values(self):
        """Test handling of DataFrame with all missing values."""
        all_missing_df = pd.DataFrame({
            'col1': [None, None, None],
            'col2': [None, None, None]
        })

        self.cleaner.config['missing_value_strategies']['drop'] = True
        cleaned_df = self.cleaner.handle_missing_values(all_missing_df)

        # Should result in empty DataFrame
        assert len(cleaned_df) == 0
        assert self.cleaner.cleaning_stats['dropped_rows'] == 3


class TestIntegration:
    """Integration tests for CSV Cleaner."""

    def test_end_to_end_workflow(self):
        """Test complete end-to-end workflow."""
        # Create test data
        test_data = {
            ' Name ': ['John', 'Jane', 'Bob', 'Alice'],
            'Age': [25, None, 30, 28],
            'Salary': [50000, 60000, None, 70000],
            'Department': ['Engineering', 'Marketing', 'Engineering', None]
        }
        test_df = pd.DataFrame(test_data)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            test_df.to_csv(f.name, index=False)
            input_path = f.name

        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as f:
            output_path = f.name

        try:
            # Run complete cleaning process
            cleaner = CSVCleaner()
            cleaned_df = cleaner.clean_csv(input_path)
            cleaner.export_cleaned_csv(cleaned_df, output_path)

            # Verify results
            assert os.path.exists(output_path)
            assert os.path.exists(output_path.replace('.csv', '_summary.txt'))

            # Load and verify cleaned data
            result_df = pd.read_csv(output_path)
            assert len(result_df) > 0
            assert 'name' in result_df.columns  # Should be normalized

        finally:
            for path in [input_path, output_path, output_path.replace('.csv', '_summary.txt')]:
                if os.path.exists(path):
                    os.unlink(path)
