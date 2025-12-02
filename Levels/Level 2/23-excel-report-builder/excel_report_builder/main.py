"""
Main entry point for Excel Report Builder.

This module provides the CLI interface for the Excel Report Builder tool.
"""

import logging
import sys
from pathlib import Path
from typing import Optional

import click
import pandas as pd

from .core import ExcelReportBuilder
from .utils import DataProcessor, ChartGenerator, create_sample_data, validate_output_path
from .templates import TemplateManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@click.group()
@click.version_option(version="1.0.0")
def cli():
    """
    Excel Report Builder - Generate professional Excel reports from CSV data.

    This tool allows you to create formatted Excel reports with charts,
    formulas, and conditional formatting from CSV data files.
    """
    pass


@cli.command()
@click.option('--input', '-i', required=True, help='Input CSV file path')
@click.option('--output', '-o', required=True, help='Output Excel file path')
@click.option('--sheet-name', '-s', default='Data', help='Name for the data sheet')
@click.option('--chart-type', '-c', type=click.Choice(['bar', 'line', 'pie']),
              help='Type of chart to create')
@click.option('--x-column', help='Column name for x-axis (required for charts)')
@click.option('--y-column', help='Column name for y-axis (required for charts)')
@click.option('--chart-title', help='Title for the chart')
@click.option('--add-summary', is_flag=True, help='Add a summary sheet')
@click.option('--add-formulas', is_flag=True, help='Add basic formulas')
@click.option('--conditional-format', is_flag=True, help='Add conditional formatting')
@click.option('--template', '-t', help='Use a predefined template (sales_report, financial_report, employee_report)')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
def generate(
    input: str,
    output: str,
    sheet_name: str,
    chart_type: Optional[str],
    x_column: Optional[str],
    y_column: Optional[str],
    chart_title: Optional[str],
    add_summary: bool,
    add_formulas: bool,
    conditional_format: bool,
    template: Optional[str],
    verbose: bool
):
    """
    Generate an Excel report from CSV data.

    Examples:

    \b
    # Basic report generation
    python -m excel_report_builder generate -i data.csv -o report.xlsx

    \b
    # Generate with bar chart
    python -m excel_report_builder generate -i data.csv -o report.xlsx \\
        --chart-type bar --x-column Product --y-column Sales

    \b
    # Generate with all features
    python -m excel_report_builder generate -i data.csv -o report.xlsx \\
        --add-summary --add-formulas --conditional-format \\
        --chart-type line --x-column Date --y-column Sales
    """
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    try:
        # Validate inputs
        if not DataProcessor.validate_csv_file(input):
            click.echo(f"Error: Invalid CSV file: {input}", err=True)
            sys.exit(1)

        if not validate_output_path(output):
            click.echo(f"Error: Invalid output path: {output}", err=True)
            sys.exit(1)

        # Load data
        click.echo(f"Loading data from {input}...")
        df = pd.read_csv(input)

        if df.empty:
            click.echo("Error: CSV file is empty", err=True)
            sys.exit(1)

        # Clean data
        df_cleaned = DataProcessor.clean_dataframe(df)

        # Create Excel report builder
        click.echo("Creating Excel report...")
        builder = ExcelReportBuilder(output)

        # Apply template if specified
        if template:
            click.echo(f"Applying template: {template}")
            template_manager = TemplateManager()
            template_obj = template_manager.get_template(template)
            if not template_obj:
                click.echo(f"Error: Template '{template}' not found", err=True)
                sys.exit(1)

        # Create data sheet
        builder.create_sheet_from_dataframe(df_cleaned, sheet_name)

        # Add formulas if requested
        if add_formulas:
            click.echo("Adding formulas...")
            numeric_cols = DataProcessor.detect_numeric_columns(df_cleaned)
            if numeric_cols:
                # Add sum formulas for numeric columns
                formulas = {}
                for i, col in enumerate(numeric_cols, 1):
                    col_letter = chr(65 + i)  # A, B, C, etc.
                    formulas[f"{col_letter}{len(df_cleaned) + 3}"] = f"=SUM({col_letter}2:{col_letter}{len(df_cleaned) + 1})"

                builder.add_formulas(sheet_name, formulas)

        # Add conditional formatting if requested
        if conditional_format:
            click.echo("Adding conditional formatting...")
            numeric_cols = DataProcessor.detect_numeric_columns(df_cleaned)
            for col in numeric_cols[:3]:  # Limit to first 3 numeric columns
                col_index = df_cleaned.columns.get_loc(col) + 1
                col_letter = chr(65 + col_index)
                cell_range = f"{col_letter}2:{col_letter}{len(df_cleaned) + 1}"

                # Add conditional formatting for values above average
                builder.add_conditional_formatting(
                    sheet_name,
                    cell_range,
                    'greater_than',
                    f"=AVERAGE({cell_range})",
                    "90EE90"  # Light green
                )

        # Add chart if requested
        if chart_type and x_column and y_column:
            if x_column not in df_cleaned.columns or y_column not in df_cleaned.columns:
                click.echo(f"Error: Columns '{x_column}' or '{y_column}' not found in data", err=True)
                sys.exit(1)

            click.echo(f"Creating {chart_type} chart...")
            chart_title = chart_title or f"{y_column} by {x_column}"

            # Calculate data range
            x_col_index = df_cleaned.columns.get_loc(x_column) + 1
            y_col_index = df_cleaned.columns.get_loc(y_column) + 1
            x_col_letter = chr(65 + x_col_index)
            y_col_letter = chr(65 + y_col_index)

            data_range = f"{y_col_letter}2:{y_col_letter}{len(df_cleaned) + 1}"
            categories_range = f"{x_col_letter}2:{x_col_letter}{len(df_cleaned) + 1}"

            builder.create_chart(
                sheet_name,
                chart_type,
                data_range,
                categories_range,
                chart_title
            )

        # Add summary sheet if requested
        if add_summary:
            click.echo("Creating summary sheet...")
            builder.create_summary_sheet(sheet_name)

        # Save workbook
        click.echo(f"Saving Excel report to {output}...")
        builder.save_workbook()

        # Display summary
        click.echo("\n✅ Excel report generated successfully!")
        click.echo(f"📊 Data: {len(df_cleaned)} rows, {len(df_cleaned.columns)} columns")
        click.echo(f"📁 Sheets: {', '.join(builder.get_sheet_names())}")
        click.echo(f"💾 File: {output}")

    except Exception as e:
        logger.error(f"Error generating Excel report: {str(e)}")
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--output', '-o', default='sample_data.csv', help='Output CSV file path')
@click.option('--rows', '-r', default=100, help='Number of rows to generate')
def sample_data(output: str, rows: int):
    """
    Generate sample CSV data for testing.

    This command creates a sample CSV file with sales data that can be used
    to test the Excel Report Builder functionality.

    Example:

    \b
    # Generate sample data with 50 rows
    python -m excel_report_builder sample-data --rows 50 --output test_data.csv
    """
    try:
        click.echo(f"Generating sample data with {rows} rows...")
        create_sample_data(output, rows)
        click.echo(f"✅ Sample data created: {output}")

    except Exception as e:
        logger.error(f"Error creating sample data: {str(e)}")
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--input', '-i', required=True, help='Input CSV file path')
def analyze(input: str):
    """
    Analyze a CSV file and suggest report configuration.

    This command examines a CSV file and provides suggestions for
    chart types, column usage, and formatting options.

    Example:

    \b
    # Analyze a CSV file
    python -m excel_report_builder analyze -i data.csv
    """
    try:
        if not DataProcessor.validate_csv_file(input):
            click.echo(f"Error: Invalid CSV file: {input}", err=True)
            sys.exit(1)

        click.echo(f"Analyzing {input}...")
        df = pd.read_csv(input)
        df_cleaned = DataProcessor.clean_dataframe(df)

        # Get analysis
        stats = DataProcessor.calculate_summary_stats(df_cleaned)

        # Display analysis
        click.echo("\n📊 Data Analysis:")
        click.echo(f"   Rows: {stats['total_rows']}")
        click.echo(f"   Columns: {stats['total_columns']}")
        click.echo(f"   Numeric columns: {', '.join(stats['numeric_columns'])}")
        click.echo(f"   Date columns: {', '.join(stats['date_columns'])}")

        # Suggest chart configurations
        if len(stats['numeric_columns']) >= 2:
            click.echo("\n📈 Chart Suggestions:")
            for i, y_col in enumerate(stats['numeric_columns'][:3]):
                for x_col in df_cleaned.columns:
                    if x_col != y_col:
                        chart_type = ChartGenerator.suggest_chart_type(df_cleaned, x_col, y_col)
                        click.echo(f"   {chart_type.title()} chart: {y_col} by {x_col}")
                        break

        # Show missing values
        missing = {k: v for k, v in stats['missing_values'].items() if v > 0}
        if missing:
            click.echo("\n⚠️  Missing Values:")
            for col, count in missing.items():
                click.echo(f"   {col}: {count} missing values")

        click.echo("\n✅ Analysis complete!")

    except Exception as e:
        logger.error(f"Error analyzing CSV file: {str(e)}")
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
def list_templates():
    """
    List available report templates.

    This command shows all available built-in templates that can be used
    with the --template option in the generate command.

    Example:

    \b
    # List all available templates
    python -m excel_report_builder list-templates
    """
    try:
        template_manager = TemplateManager()
        templates = template_manager.list_templates()

        click.echo("📋 Available Report Templates:")
        click.echo()

        for template_name in templates:
            template = template_manager.get_template(template_name)
            click.echo(f"🔹 {template_name}")
            click.echo(f"   {template.description}")
            click.echo(f"   Sheets: {len(template.sheets)}")
            click.echo(f"   Charts: {len(template.charts)}")
            click.echo(f"   Formulas: {len(template.formulas)}")
            click.echo()

        click.echo("Usage:")
        click.echo("  python -m excel_report_builder generate -i data.csv -o report.xlsx --template sales_report")

    except Exception as e:
        logger.error(f"Error listing templates: {str(e)}")
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    cli()
