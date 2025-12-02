#!/usr/bin/env python3
"""
Demo script for Excel Report Builder.
"""

import sys
import os
import tempfile
import pandas as pd

# Add current directory to path
sys.path.insert(0, '.')

def demo_excel_generation():
    """Demonstrate Excel generation functionality."""
    print("🚀 Excel Report Builder Demo")
    print("=" * 40)

    try:
        from excel_report_builder.core import ExcelReportBuilder
        from excel_report_builder.utils import DataProcessor
        print("✅ Successfully imported modules")
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

    # Create sample data
    print("\n📊 Creating sample data...")
    df = pd.DataFrame({
        'Product': ['Widget A', 'Widget B', 'Widget C', 'Widget D'],
        'Sales': [100, 200, 150, 300],
        'Profit': [20, 40, 30, 60],
        'Region': ['North', 'South', 'East', 'West']
    })
    print(f"   Created DataFrame with {len(df)} rows and {len(df.columns)} columns")

    # Test data processing
    print("\n🔍 Analyzing data...")
    processor = DataProcessor()
    numeric_cols = processor.detect_numeric_columns(df)
    print(f"   Numeric columns: {numeric_cols}")

    # Create Excel report
    print("\n📝 Creating Excel report...")
    with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp:
        try:
            builder = ExcelReportBuilder(tmp.name)
            builder.create_sheet_from_dataframe(df, 'Sales Data')

            # Add formulas
            formulas = {
                'B6': '=SUM(B2:B5)',
                'C6': '=SUM(C2:C5)',
                'B7': '=AVERAGE(B2:B5)',
                'C7': '=AVERAGE(C2:C5)'
            }
            builder.add_formulas('Sales Data', formulas)

            # Add chart
            builder.create_chart(
                'Sales Data',
                'bar',
                'B2:B5',
                'A2:A5',
                'Sales by Product'
            )

            # Add conditional formatting
            builder.add_conditional_formatting(
                'Sales Data',
                'B2:B5',
                'greater_than',
                150,
                '90EE90'
            )

            # Create summary sheet
            builder.create_summary_sheet('Sales Data', 'Summary')

            # Save workbook
            builder.save_workbook()

            if os.path.exists(tmp.name):
                file_size = os.path.getsize(tmp.name)
                print(f"   ✅ Excel file created: {tmp.name}")
                print(f"   📁 File size: {file_size} bytes")
                print(f"   📋 Sheets: {', '.join(builder.get_sheet_names())}")

                # Clean up
                os.unlink(tmp.name)
                return True
            else:
                print("   ❌ Excel file creation failed")
                return False

        except Exception as e:
            print(f"   ❌ Error: {e}")
            return False

def demo_template_system():
    """Demonstrate template system."""
    print("\n📋 Testing template system...")

    try:
        from excel_report_builder.templates import TemplateManager

        manager = TemplateManager()
        templates = manager.list_templates()
        print(f"   Available templates: {templates}")

        if templates:
            template = manager.get_template(templates[0])
            print(f"   Template '{templates[0]}': {template.description}")
            print(f"   Sheets: {len(template.sheets)}")
            print(f"   Charts: {len(template.charts)}")
            print(f"   Formulas: {len(template.formulas)}")
            return True
        else:
            print("   ❌ No templates found")
            return False

    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def main():
    """Run demo."""
    print("Starting Excel Report Builder Demo...")

    # Test Excel generation
    excel_success = demo_excel_generation()

    # Test template system
    template_success = demo_template_system()

    print("\n" + "=" * 40)
    if excel_success and template_success:
        print("🎉 Demo completed successfully!")
        print("✅ Excel Report Builder is working correctly")
        return 0
    else:
        print("⚠️  Demo completed with some issues")
        return 1

if __name__ == '__main__':
    sys.exit(main())
