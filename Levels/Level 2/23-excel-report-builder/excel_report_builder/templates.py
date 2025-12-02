"""
Template system for Excel Report Builder.

This module provides predefined templates for common report types
and allows users to create custom report templates.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class ReportTemplate:
    """
    Template class for Excel reports.

    Templates define the structure, formatting, and charts for reports.
    """

    def __init__(self, name: str, description: str = ""):
        """
        Initialize a report template.

        Args:
            name: Template name
            description: Template description
        """
        self.name = name
        self.description = description
        self.sheets: List[Dict[str, Any]] = []
        self.charts: List[Dict[str, Any]] = []
        self.formulas: List[Dict[str, Any]] = []
        self.conditional_formatting: List[Dict[str, Any]] = []
        self.styles: Dict[str, Any] = {}

    def add_sheet(self, sheet_config: Dict[str, Any]) -> None:
        """
        Add a sheet configuration to the template.

        Args:
            sheet_config: Sheet configuration dictionary
        """
        self.sheets.append(sheet_config)

    def add_chart(self, chart_config: Dict[str, Any]) -> None:
        """
        Add a chart configuration to the template.

        Args:
            chart_config: Chart configuration dictionary
        """
        self.charts.append(chart_config)

    def add_formula(self, formula_config: Dict[str, Any]) -> None:
        """
        Add a formula configuration to the template.

        Args:
            formula_config: Formula configuration dictionary
        """
        self.formulas.append(formula_config)

    def add_conditional_formatting(self, cf_config: Dict[str, Any]) -> None:
        """
        Add conditional formatting configuration to the template.

        Args:
            cf_config: Conditional formatting configuration dictionary
        """
        self.conditional_formatting.append(cf_config)

    def set_styles(self, styles: Dict[str, Any]) -> None:
        """
        Set template styles.

        Args:
            styles: Styles configuration dictionary
        """
        self.styles = styles

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert template to dictionary.

        Returns:
            Template as dictionary
        """
        return {
            "name": self.name,
            "description": self.description,
            "sheets": self.sheets,
            "charts": self.charts,
            "formulas": self.formulas,
            "conditional_formatting": self.conditional_formatting,
            "styles": self.styles
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ReportTemplate':
        """
        Create template from dictionary.

        Args:
            data: Template data dictionary

        Returns:
            ReportTemplate instance
        """
        template = cls(data["name"], data.get("description", ""))
        template.sheets = data.get("sheets", [])
        template.charts = data.get("charts", [])
        template.formulas = data.get("formulas", [])
        template.conditional_formatting = data.get("conditional_formatting", [])
        template.styles = data.get("styles", {})
        return template


class TemplateManager:
    """
    Manager class for report templates.
    """

    def __init__(self):
        """Initialize template manager."""
        self.templates: Dict[str, ReportTemplate] = {}
        self._load_builtin_templates()

    def _load_builtin_templates(self) -> None:
        """Load built-in templates."""
        # Sales Report Template
        sales_template = ReportTemplate(
            "sales_report",
            "Template for sales data analysis with charts and summary"
        )
        sales_template.add_sheet({
            "name": "Sales Data",
            "data_sheet": True,
            "formatting": "professional"
        })
        sales_template.add_sheet({
            "name": "Summary",
            "type": "summary",
            "formulas": ["total_sales", "average_sales", "top_product"]
        })
        sales_template.add_chart({
            "type": "bar",
            "title": "Sales by Product",
            "x_column": "Product",
            "y_column": "Sales",
            "position": "E2"
        })
        sales_template.add_chart({
            "type": "line",
            "title": "Sales Trend",
            "x_column": "Date",
            "y_column": "Sales",
            "position": "E20"
        })
        sales_template.add_formula({
            "cell": "B{last_row+2}",
            "formula": "=SUM(B2:B{last_row})",
            "description": "Total Sales"
        })
        sales_template.add_conditional_formatting({
            "range": "B2:B{last_row}",
            "rule": "greater_than",
            "value": "=AVERAGE(B2:B{last_row})",
            "color": "90EE90",
            "description": "Above average sales"
        })
        self.templates["sales_report"] = sales_template

        # Financial Report Template
        financial_template = ReportTemplate(
            "financial_report",
            "Template for financial data with profit/loss analysis"
        )
        financial_template.add_sheet({
            "name": "Financial Data",
            "data_sheet": True,
            "formatting": "financial"
        })
        financial_template.add_sheet({
            "name": "P&L Summary",
            "type": "summary",
            "formulas": ["total_revenue", "total_expenses", "net_profit"]
        })
        financial_template.add_chart({
            "type": "pie",
            "title": "Revenue Distribution",
            "x_column": "Category",
            "y_column": "Amount",
            "position": "E2"
        })
        financial_template.add_formula({
            "cell": "C{last_row+2}",
            "formula": "=SUM(C2:C{last_row})",
            "description": "Total Revenue"
        })
        financial_template.add_formula({
            "cell": "D{last_row+2}",
            "formula": "=SUM(D2:D{last_row})",
            "description": "Total Expenses"
        })
        financial_template.add_formula({
            "cell": "E{last_row+2}",
            "formula": "=C{last_row+2}-D{last_row+2}",
            "description": "Net Profit"
        })
        self.templates["financial_report"] = financial_template

        # Employee Report Template
        employee_template = ReportTemplate(
            "employee_report",
            "Template for employee data analysis with department insights"
        )
        employee_template.add_sheet({
            "name": "Employee Data",
            "data_sheet": True,
            "formatting": "professional"
        })
        employee_template.add_sheet({
            "name": "Department Summary",
            "type": "summary",
            "formulas": ["avg_salary", "employee_count", "performance_avg"]
        })
        employee_template.add_chart({
            "type": "bar",
            "title": "Average Salary by Department",
            "x_column": "Department",
            "y_column": "Salary",
            "position": "E2"
        })
        employee_template.add_chart({
            "type": "pie",
            "title": "Employee Distribution",
            "x_column": "Department",
            "y_column": "Employee_ID",
            "position": "E20"
        })
        employee_template.add_conditional_formatting({
            "range": "E2:E{last_row}",
            "rule": "greater_than",
            "value": "=AVERAGE(E2:E{last_row})",
            "color": "FFD700",
            "description": "Above average salary"
        })
        self.templates["employee_report"] = employee_template

    def get_template(self, name: str) -> Optional[ReportTemplate]:
        """
        Get a template by name.

        Args:
            name: Template name

        Returns:
            ReportTemplate instance or None
        """
        return self.templates.get(name)

    def list_templates(self) -> List[str]:
        """
        List available template names.

        Returns:
            List of template names
        """
        return list(self.templates.keys())

    def save_template(self, template: ReportTemplate, file_path: str) -> None:
        """
        Save template to file.

        Args:
            template: Template to save
            file_path: Path to save template
        """
        try:
            with open(file_path, 'w') as f:
                json.dump(template.to_dict(), f, indent=2)
            logger.info(f"Template saved to {file_path}")
        except Exception as e:
            logger.error(f"Error saving template: {str(e)}")
            raise

    def load_template(self, file_path: str) -> ReportTemplate:
        """
        Load template from file.

        Args:
            file_path: Path to template file

        Returns:
            ReportTemplate instance
        """
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            template = ReportTemplate.from_dict(data)
            logger.info(f"Template loaded from {file_path}")
            return template
        except Exception as e:
            logger.error(f"Error loading template: {str(e)}")
            raise

    def create_custom_template(
        self,
        name: str,
        description: str,
        config: Dict[str, Any]
    ) -> ReportTemplate:
        """
        Create a custom template from configuration.

        Args:
            name: Template name
            description: Template description
            config: Template configuration

        Returns:
            ReportTemplate instance
        """
        template = ReportTemplate(name, description)

        # Add sheets
        for sheet_config in config.get("sheets", []):
            template.add_sheet(sheet_config)

        # Add charts
        for chart_config in config.get("charts", []):
            template.add_chart(chart_config)

        # Add formulas
        for formula_config in config.get("formulas", []):
            template.add_formula(formula_config)

        # Add conditional formatting
        for cf_config in config.get("conditional_formatting", []):
            template.add_conditional_formatting(cf_config)

        # Set styles
        if "styles" in config:
            template.set_styles(config["styles"])

        self.templates[name] = template
        logger.info(f"Custom template '{name}' created")
        return template


def get_builtin_templates() -> Dict[str, Dict[str, Any]]:
    """
    Get built-in template configurations.

    Returns:
        Dictionary of template configurations
    """
    manager = TemplateManager()
    return {
        name: template.to_dict()
        for name, template in manager.templates.items()
    }


def create_template_from_existing(
    template_name: str,
    custom_name: str,
    modifications: Dict[str, Any]
) -> ReportTemplate:
    """
    Create a custom template based on an existing template.

    Args:
        template_name: Name of existing template
        custom_name: Name for new template
        modifications: Modifications to apply

        Returns:
            New ReportTemplate instance
    """
    manager = TemplateManager()
    base_template = manager.get_template(template_name)

    if not base_template:
        raise ValueError(f"Template '{template_name}' not found")

    # Create new template based on existing
    new_template = ReportTemplate(custom_name, modifications.get("description", ""))

    # Copy base template configuration
    base_dict = base_template.to_dict()

    # Apply modifications
    for key, value in modifications.items():
        if key in base_dict:
            base_dict[key] = value

    # Create new template from modified configuration
    new_template = ReportTemplate.from_dict(base_dict)
    new_template.name = custom_name

    return new_template
