"""
Utility functions for Excel Report Builder.

This module contains helper functions for data processing,
validation, and chart generation.
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import pandas as pd

logger = logging.getLogger(__name__)


class DataProcessor:
    """
    Utility class for processing and validating data.
    """

    @staticmethod
    def validate_csv_file(file_path: str) -> bool:
        """
        Validate that a CSV file exists and is readable.

        Args:
            file_path: Path to the CSV file

        Returns:
            True if file is valid, False otherwise
        """
        try:
            path = Path(file_path)
            if not path.exists():
                logger.error(f"File does not exist: {file_path}")
                return False

            if not path.suffix.lower() == '.csv':
                logger.error(f"File is not a CSV: {file_path}")
                return False

            # Try to read the file
            pd.read_csv(file_path, nrows=1)
            return True

        except Exception as e:
            logger.error(f"Error validating CSV file {file_path}: {str(e)}")
            return False

    @staticmethod
    def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean a pandas DataFrame by removing empty rows and columns.

        Args:
            df: Input DataFrame

        Returns:
            Cleaned DataFrame
        """
        logger.info("Cleaning DataFrame")

        # Remove completely empty rows
        df_cleaned = df.dropna(how='all')

        # Remove completely empty columns
        df_cleaned = df_cleaned.dropna(axis=1, how='all')

        # Remove rows that still contain missing values
        df_cleaned = df_cleaned.dropna()

        # Reset index
        df_cleaned = df_cleaned.reset_index(drop=True)

        logger.info(f"Cleaned DataFrame: {len(df)} -> {len(df_cleaned)} rows")
        return df_cleaned

    @staticmethod
    def detect_numeric_columns(df: pd.DataFrame) -> List[str]:
        """
        Detect columns that contain numeric data.

        Args:
            df: Input DataFrame

        Returns:
            List of column names that contain numeric data
        """
        numeric_columns = []

        for col in df.columns:
            if pd.api.types.is_numeric_dtype(df[col]):
                numeric_columns.append(col)
            else:
                # Try to convert to numeric
                try:
                    pd.to_numeric(df[col], errors='raise')
                    numeric_columns.append(col)
                except (ValueError, TypeError):
                    pass

        logger.info(f"Detected {len(numeric_columns)} numeric columns: {numeric_columns}")
        return numeric_columns

    @staticmethod
    def detect_date_columns(df: pd.DataFrame) -> List[str]:
        """
        Detect columns that contain date data.

        Args:
            df: Input DataFrame

        Returns:
            List of column names that contain date data
        """
        date_columns = []

        for col in df.columns:
            if pd.api.types.is_datetime64_any_dtype(df[col]):
                date_columns.append(col)
            else:
                # Try to convert to datetime
                try:
                    pd.to_datetime(df[col], errors='raise')
                    date_columns.append(col)
                except (ValueError, TypeError):
                    pass

        logger.info(f"Detected {len(date_columns)} date columns: {date_columns}")
        return date_columns

    @staticmethod
    def calculate_summary_stats(df: pd.DataFrame) -> Dict[str, Any]:
        """
        Calculate summary statistics for a DataFrame.

        Args:
            df: Input DataFrame

        Returns:
            Dictionary with summary statistics
        """
        stats = {
            "total_rows": len(df),
            "total_columns": len(df.columns),
            "numeric_columns": DataProcessor.detect_numeric_columns(df),
            "date_columns": DataProcessor.detect_date_columns(df),
            "missing_values": df.isnull().sum().to_dict(),
            "data_types": df.dtypes.to_dict()
        }

        # Add numeric statistics
        numeric_cols = stats["numeric_columns"]
        if numeric_cols:
            numeric_df = df[numeric_cols]
            stats["numeric_summary"] = {
                "mean": numeric_df.mean().to_dict(),
                "median": numeric_df.median().to_dict(),
                "std": numeric_df.std().to_dict(),
                "min": numeric_df.min().to_dict(),
                "max": numeric_df.max().to_dict()
            }

        logger.info("Calculated summary statistics")
        return stats

    @staticmethod
    def prepare_chart_data(
        df: pd.DataFrame,
        x_column: str,
        y_column: str,
        max_points: int = 100
    ) -> Tuple[List[str], List[float]]:
        """
        Prepare data for chart generation.

        Args:
            df: Input DataFrame
            x_column: Column name for x-axis
            y_column: Column name for y-axis
            max_points: Maximum number of data points

        Returns:
            Tuple of (x_values, y_values)
        """
        if x_column not in df.columns or y_column not in df.columns:
            raise ValueError(f"Columns {x_column} or {y_column} not found in DataFrame")

        # Limit data points if necessary
        if len(df) > max_points:
            df_sample = df.sample(n=max_points, random_state=42)
        else:
            df_sample = df

        # Extract values
        x_values = df_sample[x_column].astype(str).tolist()
        y_values = pd.to_numeric(df_sample[y_column], errors='coerce').fillna(0).tolist()

        logger.info(f"Prepared chart data: {len(x_values)} points")
        return x_values, y_values


class ChartGenerator:
    """
    Utility class for generating chart configurations.
    """

    @staticmethod
    def get_chart_config(
        chart_type: str,
        title: str,
        x_label: str = "",
        y_label: str = ""
    ) -> Dict[str, Any]:
        """
        Get configuration for a chart type.

        Args:
            chart_type: Type of chart ('bar', 'line', 'pie')
            title: Chart title
            x_label: X-axis label
            y_label: Y-axis label

        Returns:
            Dictionary with chart configuration
        """
        base_config = {
            "title": title,
            "x_label": x_label,
            "y_label": y_label,
            "style": 13,
            "width": 15,
            "height": 10
        }

        if chart_type.lower() == 'bar':
            base_config.update({
                "type": "bar",
                "orientation": "vertical",
                "gap_width": 150
            })
        elif chart_type.lower() == 'line':
            base_config.update({
                "type": "line",
                "markers": True,
                "smooth": True
            })
        elif chart_type.lower() == 'pie':
            base_config.update({
                "type": "pie",
                "show_legend": True,
                "show_percent": True
            })
        else:
            raise ValueError(f"Unsupported chart type: {chart_type}")

        return base_config

    @staticmethod
    def suggest_chart_type(df: pd.DataFrame, x_column: str, y_column: str) -> str:
        """
        Suggest the best chart type based on data characteristics.

        Args:
            df: Input DataFrame
            x_column: Column name for x-axis
            y_column: Column name for y-axis

        Returns:
            Suggested chart type ('bar', 'line', 'pie')
        """
        # Check if y_column is numeric
        if not pd.api.types.is_numeric_dtype(df[y_column]):
            try:
                pd.to_numeric(df[y_column], errors='raise')
            except (ValueError, TypeError):
                return "bar"  # Default to bar chart

        # Check data characteristics
        unique_x = df[x_column].nunique()
        total_rows = len(df)

        # If few unique x values, suggest bar chart
        if unique_x <= 10:
            return "bar"

        # If many data points, suggest line chart
        if total_rows > 20:
            return "line"

        # If y values sum to 100 or close, suggest pie chart
        y_numeric = pd.to_numeric(df[y_column], errors='coerce')
        if abs(y_numeric.sum() - 100) < 5:
            return "pie"

        return "bar"  # Default

    @staticmethod
    def get_color_scheme(scheme_name: str = "default") -> List[str]:
        """
        Get a color scheme for charts.

        Args:
            scheme_name: Name of the color scheme

        Returns:
            List of hex color codes
        """
        schemes = {
            "default": ["#366092", "#70AD47", "#FFC000", "#C5504B", "#5B9BD5"],
            "pastel": ["#FFB6C1", "#98FB98", "#F0E68C", "#DDA0DD", "#87CEEB"],
            "dark": ["#2F4F4F", "#8B4513", "#800080", "#008B8B", "#B22222"],
            "bright": ["#FF0000", "#00FF00", "#0000FF", "#FFFF00", "#FF00FF"]
        }

        return schemes.get(scheme_name, schemes["default"])


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format.

    Args:
        size_bytes: Size in bytes

    Returns:
        Formatted size string
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


def validate_output_path(output_path: str) -> bool:
    """
    Validate that the output path is writable.

    Args:
        output_path: Path to the output file

    Returns:
        True if path is valid, False otherwise
    """
    try:
        path = Path(output_path)

        # Check if parent directory exists or can be created
        parent = path.parent
        if not parent.exists():
            parent.mkdir(parents=True, exist_ok=True)

        # Check if file extension is .xlsx
        if not path.suffix.lower() == '.xlsx':
            logger.warning(f"Output file should have .xlsx extension: {output_path}")

        return True

    except Exception as e:
        logger.error(f"Error validating output path {output_path}: {str(e)}")
        return False


def get_column_letter(column_index: int) -> str:
    """
    Convert column index to Excel column letter.

    Args:
        column_index: 1-based column index

    Returns:
        Excel column letter (A, B, C, etc.)
    """
    result = ""
    while column_index > 0:
        column_index -= 1
        result = chr(65 + column_index % 26) + result
        column_index //= 26
    return result


def create_sample_data(output_file: str, num_rows: int = 100) -> None:
    """
    Create sample CSV data for testing.

    Args:
        output_file: Path to the output CSV file
        num_rows: Number of rows to generate
    """
    import random
    from datetime import datetime, timedelta

    # Generate sample data
    data = {
        'Date': [],
        'Product': [],
        'Sales': [],
        'Quantity': [],
        'Region': [],
        'Profit': []
    }

    products = ['Widget A', 'Widget B', 'Widget C', 'Gadget X', 'Gadget Y']
    regions = ['North', 'South', 'East', 'West', 'Central']

    start_date = datetime.now() - timedelta(days=num_rows)

    for i in range(num_rows):
        data['Date'].append((start_date + timedelta(days=i)).strftime('%Y-%m-%d'))
        data['Product'].append(random.choice(products))
        data['Sales'].append(round(random.uniform(100, 1000), 2))
        data['Quantity'].append(random.randint(1, 50))
        data['Region'].append(random.choice(regions))
        data['Profit'].append(round(random.uniform(10, 200), 2))

    # Create DataFrame and save
    df = pd.DataFrame(data)
    df.to_csv(output_file, index=False)
    logger.info(f"Created sample data file: {output_file} with {num_rows} rows")
