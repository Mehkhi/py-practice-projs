"""Core CSV cleaning functionality."""

import logging
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any, Union
from pathlib import Path
import yaml
from datetime import datetime


class CSVCleaner:
    """Main class for CSV data cleaning operations."""

    def __init__(self, config_path: Optional[str] = None):
        """Initialize CSV cleaner with optional configuration.

        Args:
            config_path: Path to YAML configuration file
        """
        self.logger = logging.getLogger(__name__)
        self.config = self._load_config(config_path)
        self.cleaning_stats = {
            'original_rows': 0,
            'cleaned_rows': 0,
            'dropped_rows': 0,
            'missing_values_filled': 0,
            'columns_normalized': 0,
            'type_conversions': 0,
            'outliers_detected': 0
        }
        self.error_log = []

    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load configuration from YAML file or use defaults.

        Args:
            config_path: Path to configuration file

        Returns:
            Configuration dictionary
        """
        default_config = {
            'missing_value_strategies': {
                'drop': True,
                'fill_numeric': 'mean',
                'fill_categorical': 'mode',
                'fill_constant': ''
            },
            'column_normalization': {
                'lowercase': True,
                'strip_spaces': True,
                'replace_spaces': '_'
            },
            'type_detection': {
                'auto_detect': True,
                'force_types': {}
            },
            'outlier_detection': {
                'enabled': False,
                'method': 'iqr',
                'threshold': 1.5
            },
            'export': {
                'include_summary': True,
                'include_error_log': True
            }
        }

        def _deep_update(base: Dict[str, Any], updates: Dict[str, Any]) -> Dict[str, Any]:
            """Recursively merge update values into base dictionary."""
            for key, value in updates.items():
                if isinstance(value, dict) and isinstance(base.get(key), dict):
                    base[key] = _deep_update(dict(base[key]), value)
                else:
                    base[key] = value
            return base

        if config_path:
            if Path(config_path).exists():
                try:
                    with open(config_path, 'r') as f:
                        user_config = yaml.safe_load(f)
                    if not isinstance(user_config, dict):
                        raise ValueError("Configuration file must define a mapping at the root level.")
                    # Merge with defaults (deep merge to preserve nested defaults)
                    default_config = _deep_update(default_config, user_config)
                    self.logger.info(f"Loaded configuration from {config_path}")
                except Exception as e:
                    self.logger.warning(f"Failed to load config from {config_path}: {e}")
                    self.logger.info("Using default configuration")
            else:
                self.logger.warning(f"Configuration file not found: {config_path}")
                self.logger.info("Using default configuration")

        return default_config

    def load_csv(self, file_path: str) -> pd.DataFrame:
        """Load CSV file into pandas DataFrame.

        Args:
            file_path: Path to CSV file

        Returns:
            Loaded DataFrame

        Raises:
            FileNotFoundError: If file doesn't exist
            pd.errors.EmptyDataError: If file is empty
            pd.errors.ParserError: If file can't be parsed
        """
        try:
            self.logger.info(f"Loading CSV file: {file_path}")
            df = pd.read_csv(file_path)
            self.cleaning_stats['original_rows'] = len(df)
            self.logger.info(f"Loaded {len(df)} rows and {len(df.columns)} columns")
            return df
        except FileNotFoundError:
            self.logger.error(f"File not found: {file_path}")
            raise
        except pd.errors.EmptyDataError:
            self.logger.error(f"Empty file: {file_path}")
            raise
        except pd.errors.ParserError as e:
            self.logger.error(f"Failed to parse CSV: {e}")
            raise

    def normalize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalize column names according to configuration.

        Args:
            df: Input DataFrame

        Returns:
            DataFrame with normalized column names
        """
        self.logger.info("Normalizing column names")
        original_columns = df.columns.tolist()

        # Create normalized column names
        new_columns = []
        for col in original_columns:
            new_col = str(col)

            if self.config['column_normalization']['strip_spaces']:
                new_col = new_col.strip()

            if self.config['column_normalization']['lowercase']:
                new_col = new_col.lower()

            if self.config['column_normalization']['replace_spaces']:
                new_col = new_col.replace(' ', self.config['column_normalization']['replace_spaces'])

            new_columns.append(new_col)

        # Handle duplicate column names
        final_columns = []
        seen = set()
        for col in new_columns:
            if col in seen:
                counter = 1
                while f"{col}_{counter}" in seen:
                    counter += 1
                final_columns.append(f"{col}_{counter}")
                seen.add(f"{col}_{counter}")
            else:
                final_columns.append(col)
                seen.add(col)

        df.columns = final_columns
        self.cleaning_stats['columns_normalized'] = len([i for i, j in zip(original_columns, final_columns) if i != j])
        self.logger.info(f"Normalized {self.cleaning_stats['columns_normalized']} column names")

        return df

    def handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """Handle missing values according to configuration.

        Args:
            df: Input DataFrame

        Returns:
            DataFrame with missing values handled
        """
        self.logger.info("Handling missing values")
        original_len = len(df)
        fill_count = 0

        if df.isnull().sum().sum() == 0:
            self.logger.info("No missing values found")
            return df

        # Drop rows if configured
        if self.config['missing_value_strategies']['drop']:
            df = df.dropna()
            self.cleaning_stats['dropped_rows'] = original_len - len(df)
            self.logger.info(f"Dropped {self.cleaning_stats['dropped_rows']} rows with missing values")

        # Fill remaining missing values
        for col in df.columns:
            if df[col].isnull().any():
                missing_before_col = df[col].isnull().sum()
                if df[col].dtype in ['int64', 'float64']:
                    # Numeric column
                    fill_strategy = self.config['missing_value_strategies']['fill_numeric']
                    if fill_strategy == 'mean':
                        fill_value = df[col].mean()
                    elif fill_strategy == 'median':
                        fill_value = df[col].median()
                    elif fill_strategy == 'mode':
                        fill_value = df[col].mode().iloc[0] if not df[col].mode().empty else 0
                    else:
                        fill_value = 0
                    df[col] = df[col].fillna(fill_value)
                    self.logger.info(f"Filled numeric column '{col}' with {fill_strategy}: {fill_value}")

                else:
                    # Categorical column
                    fill_strategy = self.config['missing_value_strategies']['fill_categorical']
                    if fill_strategy == 'mode':
                        fill_value = df[col].mode().iloc[0] if not df[col].mode().empty else 'Unknown'
                    else:
                        fill_value = self.config['missing_value_strategies']['fill_constant']

                    df[col] = df[col].fillna(fill_value)
                    self.logger.info(f"Filled categorical column '{col}' with: {fill_value}")

                fill_count += missing_before_col - df[col].isnull().sum()

        self.cleaning_stats['missing_values_filled'] = fill_count
        self.logger.info(f"Filled {self.cleaning_stats['missing_values_filled']} missing values")

        return df

    def detect_outliers(self, df: pd.DataFrame) -> pd.DataFrame:
        """Detect outliers in numeric columns.

        Args:
            df: Input DataFrame

        Returns:
            DataFrame with outlier information
        """
        if not self.config['outlier_detection']['enabled']:
            return df

        self.logger.info("Detecting outliers")
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        outliers_detected = 0

        for col in numeric_columns:
            try:
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1

                # Skip if IQR is 0 (all values are the same)
                if IQR == 0:
                    continue

                lower_bound = Q1 - self.config['outlier_detection']['threshold'] * IQR
                upper_bound = Q3 + self.config['outlier_detection']['threshold'] * IQR

                outlier_mask = (df[col] < lower_bound) | (df[col] > upper_bound)
                outliers_count = outlier_mask.sum()

                if outliers_count > 0:
                    outliers_detected += outliers_count
                    # Add outlier flag column
                    df[f'{col}_outlier'] = outlier_mask
                    self.logger.info(f"Detected {outliers_count} outliers in column '{col}'")
            except Exception as e:
                self.logger.warning(f"Failed to detect outliers in column '{col}': {e}")
                continue

        self.cleaning_stats['outliers_detected'] = outliers_detected
        return df

    def coerce_types(self, df: pd.DataFrame) -> pd.DataFrame:
        """Coerce column types according to configuration.

        Args:
            df: Input DataFrame

        Returns:
            DataFrame with coerced types
        """
        self.logger.info("Coercing data types")
        type_conversions = 0

        for col in df.columns:
            if (self.config['type_detection']['force_types'] and
                col in self.config['type_detection']['force_types']):
                target_type = self.config['type_detection']['force_types'][col]
                try:
                    df[col] = df[col].astype(target_type)
                    type_conversions += 1
                    self.logger.info(f"Converted column '{col}' to {target_type}")
                except Exception as e:
                    self.logger.warning(f"Failed to convert column '{col}' to {target_type}: {e}")
                    self.error_log.append(f"Type conversion failed for column '{col}': {e}")

            elif self.config['type_detection']['auto_detect']:
                # Auto-detect and convert numeric columns
                if df[col].dtype == 'object':
                    # Try to convert to numeric first
                    numeric_converted = pd.to_numeric(df[col], errors='coerce')
                    # Only convert if all values converted successfully (100%)
                    if numeric_converted.notna().sum() == len(numeric_converted):
                        df[col] = numeric_converted
                        type_conversions += 1
                        self.logger.info(f"Auto-converted column '{col}' to numeric")
                    else:
                        # Try to convert to datetime only if numeric conversion failed
                        try:
                            datetime_converted = pd.to_datetime(df[col], errors='coerce')
                            if datetime_converted.notna().sum() == len(datetime_converted):
                                df[col] = datetime_converted
                                type_conversions += 1
                                self.logger.info(f"Auto-converted column '{col}' to datetime")
                        except:
                            pass  # Keep as object

        self.cleaning_stats['type_conversions'] = type_conversions
        return df

    def clean_csv(self, file_path: str) -> pd.DataFrame:
        """Complete CSV cleaning pipeline.

        Args:
            file_path: Path to input CSV file

        Returns:
            Cleaned DataFrame
        """
        self.logger.info(f"Starting CSV cleaning for: {file_path}")

        # Load CSV
        df = self.load_csv(file_path)

        # Apply cleaning steps
        df = self.normalize_columns(df)
        df = self.handle_missing_values(df)
        df = self.detect_outliers(df)
        df = self.coerce_types(df)

        self.cleaning_stats['cleaned_rows'] = len(df)
        self.logger.info("CSV cleaning completed successfully")

        return df

    def export_cleaned_csv(self, df: pd.DataFrame, output_path: str) -> None:
        """Export cleaned DataFrame to CSV with summary report.

        Args:
            df: Cleaned DataFrame
            output_path: Path for output CSV file
        """
        self.logger.info(f"Exporting cleaned CSV to: {output_path}")

        # Export main CSV
        df.to_csv(output_path, index=False)

        # Generate summary report
        if self.config['export']['include_summary']:
            summary_path = output_path.replace('.csv', '_summary.txt')
            self._generate_summary_report(summary_path, df)

        # Export error log
        if self.config['export']['include_error_log'] and self.error_log:
            error_log_path = output_path.replace('.csv', '_errors.csv')
            self._export_error_log(error_log_path)

    def _generate_summary_report(self, summary_path: str, df: pd.DataFrame) -> None:
        """Generate summary report of cleaning operations.

        Args:
            summary_path: Path for summary report
            df: Cleaned DataFrame
        """
        with open(summary_path, 'w') as f:
            f.write("CSV Cleaning Summary Report\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            f.write("Data Overview:\n")
            f.write(f"  Original rows: {self.cleaning_stats['original_rows']}\n")
            f.write(f"  Cleaned rows: {self.cleaning_stats['cleaned_rows']}\n")
            f.write(f"  Dropped rows: {self.cleaning_stats['dropped_rows']}\n")
            f.write(f"  Columns: {len(df.columns)}\n\n")

            f.write("Cleaning Operations:\n")
            f.write(f"  Columns normalized: {self.cleaning_stats['columns_normalized']}\n")
            f.write(f"  Missing values filled: {self.cleaning_stats['missing_values_filled']}\n")
            f.write(f"  Type conversions: {self.cleaning_stats['type_conversions']}\n")
            f.write(f"  Outliers detected: {self.cleaning_stats['outliers_detected']}\n\n")

            f.write("Column Information:\n")
            for col in df.columns:
                f.write(f"  {col}: {df[col].dtype} ({df[col].isnull().sum()} nulls)\n")

            if self.error_log:
                f.write(f"\nErrors/Warnings ({len(self.error_log)}):\n")
                for error in self.error_log:
                    f.write(f"  - {error}\n")

    def _export_error_log(self, error_log_path: str) -> None:
        """Export error log to CSV.

        Args:
            error_log_path: Path for error log CSV
        """
        error_df = pd.DataFrame({
            'timestamp': [datetime.now().strftime('%Y-%m-%d %H:%M:%S')] * len(self.error_log),
            'error_message': self.error_log
        })
        error_df.to_csv(error_log_path, index=False)
        self.logger.info(f"Error log exported to: {error_log_path}")
