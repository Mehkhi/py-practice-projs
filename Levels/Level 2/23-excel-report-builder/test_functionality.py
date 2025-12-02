#!/usr/bin/env python3
"""
Test script to verify Excel Report Builder functionality.
"""

import sys
import os
import tempfile
import pandas as pd

# Add current directory to path
sys.path.insert(0, '.')

try:
    from excel_report_builder.core import ExcelReportBuilder
    from excel_report_builder.utils import DataProcessor, ChartGenerator
    print("✅ Successfully imported core modules")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

def test_basic_functionality():
    """Test basic Excel generation functionality."""
    print("\n🧪 Testing basic functionality...")

    # Create test data
    df = pd.DataFrame({
        'Product': ['Widget A', 'Widget B', 'Widget C'],
        'Sales': [100, 200, 150],
        'Profit': [20, 40, 30]
    })

    # Test data processor
    processor = DataProcessor()
    numeric_cols = processor.detect_numeric_columns(df)
    print(f"   Detected numeric columns: {numeric_cols}")

    # Test Excel builder
    with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp:
        try:
            builder = ExcelReportBuilder(tmp.name)
            builder.create_sheet_from_dataframe(df, 'Test Sheet')
            builder.save_workbook()

            if os.path.exists(tmp.name):
                print("   ✅ Excel file created successfully")
                os.unlink(tmp.name)
                return True
            else:
                print("   ❌ Excel file creation failed")
                return False
        except Exception as e:
            print(f"   ❌ Error creating Excel file: {e}")
            return False

def test_chart_generation():
    """Test chart generation functionality."""
    print("\n📊 Testing chart generation...")

    df = pd.DataFrame({
        'Category': ['A', 'B', 'C'],
        'Value': [10, 20, 30]
    })

    with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp:
        try:
            builder = ExcelReportBuilder(tmp.name)
            builder.create_sheet_from_dataframe(df, 'Chart Test')
            builder.create_chart(
                'Chart Test',
                'bar',
                'B2:B4',
                'A2:A4',
                'Test Chart'
            )
            builder.save_workbook()

            if os.path.exists(tmp.name):
                print("   ✅ Chart created successfully")
                os.unlink(tmp.name)
                return True
            else:
                print("   ❌ Chart creation failed")
                return False
        except Exception as e:
            print(f"   ❌ Error creating chart: {e}")
            return False

def test_template_system():
    """Test template system functionality."""
    print("\n📋 Testing template system...")

    try:
        from excel_report_builder.templates import TemplateManager

        manager = TemplateManager()
        templates = manager.list_templates()
        print(f"   Available templates: {templates}")

        if templates:
            template = manager.get_template(templates[0])
            print(f"   Template '{templates[0]}': {template.description}")
            print("   ✅ Template system working")
            return True
        else:
            print("   ❌ No templates found")
            return False
    except Exception as e:
        print(f"   ❌ Error testing templates: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 Excel Report Builder - Functionality Test")
    print("=" * 50)

    tests = [
        test_basic_functionality,
        test_chart_generation,
        test_template_system
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        if test():
            passed += 1

    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! Excel Report Builder is working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
