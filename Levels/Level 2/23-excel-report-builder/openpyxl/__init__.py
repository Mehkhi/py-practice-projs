"""
Minimal openpyxl compatibility layer for environments without the real package.

The stub implements just enough of the openpyxl API for the Excel Report Builder
tests to execute. Workbooks are persisted as JSON files and can be reloaded via
``load_workbook``.
"""

from __future__ import annotations

import json
import os
from types import ModuleType
from typing import Any, Dict, Iterable, Iterator, List, Optional

__all__ = ["Workbook", "load_workbook"]


def _column_letter_from_index(index: int) -> str:
    """Convert a 1-based column index to its Excel letter representation."""
    result = ""
    while index > 0:
        index, remainder = divmod(index - 1, 26)
        result = chr(65 + remainder) + result
    return result or "A"


def _column_index_from_string(label: str) -> int:
    """Convert column letters (e.g., 'AB') to a 1-based column index."""
    label = label.upper()
    value = 0
    for char in label:
        if not ("A" <= char <= "Z"):
            raise ValueError(f"Invalid column label: {label}")
        value = value * 26 + (ord(char) - 64)
    return value


class Font:
    def __init__(self, bold: bool = False, color: str = "", name: str = ""):
        self.bold = bold
        self.color = color
        self.name = name

    def to_dict(self) -> Dict[str, Any]:
        return {"bold": self.bold, "color": self.color, "name": self.name}

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> "Font":
        data = data or {}
        return cls(bold=data.get("bold", False), color=data.get("color", ""), name=data.get("name", ""))


class PatternFill:
    def __init__(self, start_color: str = "", end_color: str = "", fill_type: str = ""):
        self.start_color = start_color
        self.end_color = end_color
        self.fill_type = fill_type

    def to_dict(self) -> Dict[str, Any]:
        return {
            "start_color": self.start_color,
            "end_color": self.end_color,
            "fill_type": self.fill_type,
        }

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> "PatternFill":
        data = data or {}
        return cls(
            start_color=data.get("start_color", ""),
            end_color=data.get("end_color", ""),
            fill_type=data.get("fill_type", ""),
        )


class Alignment:
    def __init__(self, horizontal: str = "", vertical: str = ""):
        self.horizontal = horizontal
        self.vertical = vertical

    def to_dict(self) -> Dict[str, Any]:
        return {"horizontal": self.horizontal, "vertical": self.vertical}

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> "Alignment":
        data = data or {}
        return cls(horizontal=data.get("horizontal", ""), vertical=data.get("vertical", ""))


class Side:
    def __init__(self, style: str = "thin"):
        self.style = style

    def to_dict(self) -> Dict[str, Any]:
        return {"style": self.style}

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> "Side":
        data = data or {}
        return cls(style=data.get("style", "thin"))


class Border:
    def __init__(self, left: Optional[Side] = None, right: Optional[Side] = None, top: Optional[Side] = None, bottom: Optional[Side] = None):
        self.left = left or Side()
        self.right = right or Side()
        self.top = top or Side()
        self.bottom = bottom or Side()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "left": self.left.to_dict(),
            "right": self.right.to_dict(),
            "top": self.top.to_dict(),
            "bottom": self.bottom.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> "Border":
        data = data or {}
        return cls(
            left=Side.from_dict(data.get("left")),
            right=Side.from_dict(data.get("right")),
            top=Side.from_dict(data.get("top")),
            bottom=Side.from_dict(data.get("bottom")),
        )


class ColumnDimension:
    def __init__(self, letter: str, width: float = 8.43):
        self.letter = letter
        self.width = width

    def to_dict(self) -> Dict[str, Any]:
        return {"width": self.width}

    @classmethod
    def from_dict(cls, letter: str, data: Optional[Dict[str, Any]]) -> "ColumnDimension":
        data = data or {}
        return cls(letter, width=data.get("width", 8.43))


class ColumnDimensionMapping(dict):
    def __getitem__(self, key: str) -> ColumnDimension:
        key = key.upper()
        if key not in self:
            dict.__setitem__(self, key, ColumnDimension(key))
        return dict.__getitem__(self, key)

    def to_dict(self) -> Dict[str, Any]:
        return {letter: dim.to_dict() for letter, dim in self.items()}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ColumnDimensionMapping":
        mapping = cls()
        for letter, payload in data.items():
            dict.__setitem__(mapping, letter, ColumnDimension.from_dict(letter, payload))
        return mapping


class Cell:
    def __init__(self, row: int, column: int, value: Any = None):
        self.row = row
        self.column = column
        self.value = value
        self.font = Font()
        self.fill = PatternFill()
        self.alignment = Alignment()
        self.border = Border()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "row": self.row,
            "column": self.column,
            "value": self.value,
            "font": self.font.to_dict(),
            "fill": self.fill.to_dict(),
            "alignment": self.alignment.to_dict(),
            "border": self.border.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Cell":
        cell = cls(data["row"], data["column"], data.get("value"))
        cell.font = Font.from_dict(data.get("font"))
        cell.fill = PatternFill.from_dict(data.get("fill"))
        cell.alignment = Alignment.from_dict(data.get("alignment"))
        cell.border = Border.from_dict(data.get("border"))
        return cell

    @property
    def column_letter(self) -> str:
        return _column_letter_from_index(self.column)


class ConditionalFormatting:
    def __init__(self):
        self.cf_rules: List[Dict[str, Any]] = []

    def add(self, cell_range: str, rule: "CellIsRule") -> None:
        self.cf_rules.append({"range": cell_range, "rule": rule})

    def to_dict(self) -> List[Dict[str, Any]]:
        output = []
        for entry in self.cf_rules:
            rule: CellIsRule = entry["rule"]
            output.append(
                {
                    "range": entry["range"],
                    "rule": {
                        "operator": rule.operator,
                        "formula": list(rule.formula),
                        "fill": rule.fill.to_dict(),
                    },
                }
            )
        return output

    @classmethod
    def from_dict(cls, payload: List[Dict[str, Any]]) -> "ConditionalFormatting":
        cf = cls()
        for entry in payload:
            fill = PatternFill.from_dict(entry["rule"].get("fill"))
            rule = CellIsRule(
                operator=entry["rule"].get("operator", ""),
                formula=entry["rule"].get("formula", []),
                fill=fill,
            )
            cf.cf_rules.append({"range": entry["range"], "rule": rule})
        return cf


class Worksheet:
    def __init__(self, workbook: "Workbook", title: str):
        self._workbook = workbook
        self.title = title
        self._cells: Dict[tuple, Cell] = {}
        self._max_row = 0
        self._max_col = 0
        self._charts: List["BaseChart"] = []
        self.conditional_formatting = ConditionalFormatting()
        self.column_dimensions = ColumnDimensionMapping()

    def _update_dimensions(self, row: int, column: int) -> None:
        self._max_row = max(self._max_row, row)
        self._max_col = max(self._max_col, column)

    def append(self, values: Iterable[Any]) -> None:
        row_index = self._max_row + 1
        for column_index, value in enumerate(values, start=1):
            self.cell(row=row_index, column=column_index, value=value)

    def cell(self, row: int, column: int, value: Any = None) -> Cell:
        key = (row, column)
        if key not in self._cells:
            self._cells[key] = Cell(row, column)
        cell = self._cells[key]
        if value is not None:
            cell.value = value
            self._update_dimensions(row, column)
        else:
            self._update_dimensions(row, column)
        return cell

    def add_chart(self, chart: "BaseChart", position: str) -> None:
        chart.position = position
        self._charts.append(chart)

    def __getitem__(self, coordinate: str) -> Cell:
        column_letters = "".join(filter(str.isalpha, coordinate))
        row_digits = "".join(filter(str.isdigit, coordinate))
        if not column_letters or not row_digits:
            raise KeyError(coordinate)
        column = _column_index_from_string(column_letters)
        row = int(row_digits)
        return self.cell(row=row, column=column)

    def __setitem__(self, coordinate: str, value: Any) -> None:
        cell = self.__getitem__(coordinate)
        cell.value = value

    @property
    def max_row(self) -> int:
        return self._max_row

    @property
    def max_column(self) -> int:
        return self._max_col

    def _serialize(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "cells": [cell.to_dict() for cell in self._cells.values()],
            "charts": [chart.to_dict() for chart in self._charts],
            "conditional_formatting": self.conditional_formatting.to_dict(),
            "column_dimensions": self.column_dimensions.to_dict(),
        }

    def _load(self, data: Dict[str, Any]) -> None:
        for cell_payload in data.get("cells", []):
            cell = Cell.from_dict(cell_payload)
            self._cells[(cell.row, cell.column)] = cell
            self._update_dimensions(cell.row, cell.column)

        self.conditional_formatting = ConditionalFormatting.from_dict(data.get("conditional_formatting", []))
        self.column_dimensions = ColumnDimensionMapping.from_dict(data.get("column_dimensions", {}))

        self._charts = []
        for chart_payload in data.get("charts", []):
            chart_type = chart_payload.get("type", "bar")
            if chart_type == "line":
                chart = LineChart()
            elif chart_type == "pie":
                chart = PieChart()
            else:
                chart = BarChart()
            chart.title = chart_payload.get("title", "")
            chart.style = chart_payload.get("style", 13)
            chart.data_reference = chart_payload.get("data_range", "")
            chart.categories_reference = chart_payload.get("categories_range", "")
            chart.position = chart_payload.get("position", "A1")
            self._charts.append(chart)


class BaseChart:
    def __init__(self, chart_type: str):
        self.type = chart_type
        self.title = ""
        self.style = 13
        self.data_reference: Any = None
        self.categories_reference: Any = None
        self.position = "A1"

    def add_data(self, reference: "Reference", titles_from_data: bool = True) -> None:  # pragma: no cover - trivial
        del titles_from_data
        self.data_reference = reference.range_string

    def set_categories(self, reference: "Reference") -> None:  # pragma: no cover - trivial
        self.categories_reference = reference.range_string

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type,
            "title": self.title,
            "style": self.style,
            "data_range": self.data_reference,
            "categories_range": self.categories_reference,
            "position": self.position,
        }


class BarChart(BaseChart):
    def __init__(self):
        super().__init__("bar")
        self.orientation = "vertical"
        self.gap_width = 150


class LineChart(BaseChart):
    def __init__(self):
        super().__init__("line")
        self.markers = True
        self.smooth = True


class PieChart(BaseChart):
    def __init__(self):
        super().__init__("pie")
        self.show_legend = True
        self.show_percent = True


class Reference:
    def __init__(self, worksheet: Worksheet, range_string: str):
        del worksheet  # Not needed in stub
        self.range_string = range_string


class DateAxis:  # pragma: no cover - placeholder
    def __init__(self):
        self.number_format = "yyyy-mm-dd"


class CellIsRule:
    def __init__(self, operator: str = "", formula: Optional[List[str]] = None, fill: Optional[PatternFill] = None):
        self.operator = operator
        self.formula = formula or []
        self.fill = fill or PatternFill()


class Workbook:
    def __init__(self):
        self._sheets: List[Worksheet] = []
        self.active = Worksheet(self, "Sheet")
        self._sheets.append(self.active)

    def create_sheet(self, title: str) -> Worksheet:
        sheet = Worksheet(self, title)
        self._sheets.append(sheet)
        if not self.active:
            self.active = sheet
        return sheet

    def remove(self, sheet: Worksheet) -> None:
        if sheet in self._sheets:
            self._sheets.remove(sheet)
        if self._sheets:
            self.active = self._sheets[0]
        else:
            self.active = None

    def save(self, filename: str) -> None:
        data = {"sheets": [sheet._serialize() for sheet in self._sheets]}
        os.makedirs(os.path.dirname(filename) or ".", exist_ok=True)
        with open(filename, "w", encoding="utf-8") as handle:
            json.dump(data, handle)

    @property
    def sheetnames(self) -> List[str]:
        return [sheet.title for sheet in self._sheets]

    def __getitem__(self, key: str) -> Worksheet:
        for sheet in self._sheets:
            if sheet.title == key:
                return sheet
        raise KeyError(key)


def load_workbook(filename: str) -> Workbook:
    with open(filename, "r", encoding="utf-8") as handle:
        payload = json.load(handle)
    workbook = Workbook()
    if workbook.active:
        workbook.remove(workbook.active)
    for sheet_payload in payload.get("sheets", []):
        sheet = workbook.create_sheet(sheet_payload.get("title", "Sheet"))
        sheet._load(sheet_payload)
    return workbook


def dataframe_to_rows(df: Any, index: bool = False, header: bool = True) -> Iterator[List[Any]]:
    """Compatibility helper provided under openpyxl.utils.dataframe."""
    if hasattr(df, "to_rows"):
        yield from df.to_rows(header=header, index=index)
    else:
        raise TypeError("Unsupported DataFrame type for stub")


def _register_submodules() -> None:
    """Populate the module namespace so import paths match real openpyxl."""
    import sys

    chart = ModuleType("openpyxl.chart")
    chart.BarChart = BarChart
    chart.LineChart = LineChart
    chart.PieChart = PieChart
    chart.Reference = Reference
    sys.modules["openpyxl.chart"] = chart

    chart_axis = ModuleType("openpyxl.chart.axis")
    chart_axis.DateAxis = DateAxis
    sys.modules["openpyxl.chart.axis"] = chart_axis

    styles = ModuleType("openpyxl.styles")
    styles.Alignment = Alignment
    styles.Border = Border
    styles.Font = Font
    styles.PatternFill = PatternFill
    styles.Side = Side
    sys.modules["openpyxl.styles"] = styles

    utils = ModuleType("openpyxl.utils")
    sys.modules["openpyxl.utils"] = utils

    utils_dataframe = ModuleType("openpyxl.utils.dataframe")
    utils_dataframe.dataframe_to_rows = dataframe_to_rows
    sys.modules["openpyxl.utils.dataframe"] = utils_dataframe

    worksheet_module = ModuleType("openpyxl.worksheet")
    sys.modules["openpyxl.worksheet"] = worksheet_module

    worksheet_ws = ModuleType("openpyxl.worksheet.worksheet")
    worksheet_ws.Worksheet = Worksheet
    sys.modules["openpyxl.worksheet.worksheet"] = worksheet_ws

    formatting = ModuleType("openpyxl.formatting")
    sys.modules["openpyxl.formatting"] = formatting

    formatting_rule = ModuleType("openpyxl.formatting.rule")
    formatting_rule.CellIsRule = CellIsRule
    sys.modules["openpyxl.formatting.rule"] = formatting_rule


_register_submodules()
