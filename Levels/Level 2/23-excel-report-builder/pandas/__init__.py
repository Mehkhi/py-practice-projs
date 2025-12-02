"""
Minimal pandas compatibility layer used when the real library is unavailable.

This stub implements the limited subset of pandas features exercised by the
Excel Report Builder tests. The goal is to provide a drop-in module named
``pandas`` that supports basic DataFrame and Series operations without pulling
in the actual dependency.
"""

from __future__ import annotations

import csv
import datetime as _dt
import math
import random
import statistics
from types import SimpleNamespace
from typing import Any, Dict, Iterable, Iterator, List, Optional, Sequence, Union

__all__ = [
    "DataFrame",
    "Series",
    "read_csv",
    "to_numeric",
    "to_datetime",
    "date_range",
    "errors",
    "api",
]

_IS_STUB = True


def _is_null(value: Any) -> bool:
    """Return True when a value should be treated as missing."""
    if value is None:
        return True
    if isinstance(value, float) and math.isnan(value):
        return True
    return False


def _coerce_numeric(value: Any) -> float:
    """Convert a value to float, raising ValueError on failure."""
    if _is_null(value):
        raise ValueError("Null value")
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return float(value)
    if isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            raise ValueError("Empty string")
        return float(stripped)
    raise ValueError(f"Cannot convert {value!r} to numeric")


def _coerce_datetime(value: Any) -> _dt.datetime:
    """Convert a value to datetime, raising ValueError on failure."""
    if isinstance(value, _dt.datetime):
        return value
    if isinstance(value, _dt.date):
        return _dt.datetime.combine(value, _dt.time.min)
    if isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            raise ValueError("Empty string")
        try:
            return _dt.datetime.fromisoformat(stripped)
        except ValueError as exc:
            # Fallback to common formats
            for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%m/%d/%Y"):
                try:
                    return _dt.datetime.strptime(stripped, fmt)
                except ValueError:
                    continue
            raise ValueError(f"Cannot parse datetime: {value}") from exc
    raise ValueError(f"Cannot convert {value!r} to datetime")


class Index(Sequence[str]):
    """Lightweight immutable sequence for column labels."""

    def __init__(self, data: Iterable[str]):
        self._data = list(data)

    def __iter__(self) -> Iterator[str]:
        return iter(self._data)

    def __len__(self) -> int:  # pragma: no cover - trivial
        return len(self._data)

    def __getitem__(self, item: Union[int, slice]) -> Union[str, List[str]]:
        return self._data[item]

    def __contains__(self, item: object) -> bool:  # pragma: no cover - trivial
        return item in self._data

    def tolist(self) -> List[str]:
        return list(self._data)

    def get_loc(self, key: str) -> int:
        if key not in self._data:
            raise KeyError(key)
        return self._data.index(key)

    def __repr__(self) -> str:  # pragma: no cover - trivial
        return f"Index({self._data!r})"


class Series:
    """Simple one-dimensional labeled array."""

    def __init__(
        self,
        data: Iterable[Any],
        index: Optional[Iterable[Any]] = None,
        name: Optional[str] = None,
    ):
        self._data = list(data)
        if index is None:
            index = range(len(self._data))
        self._index = list(index)
        if len(self._index) != len(self._data):
            raise ValueError("Index length must match data length")
        self.name = name

    def __len__(self) -> int:  # pragma: no cover - trivial
        return len(self._data)

    def __iter__(self) -> Iterator[Any]:  # pragma: no cover - trivial
        return iter(self._data)

    def __getitem__(self, key: Union[int, slice, Any]) -> Any:
        if isinstance(key, slice):
            return Series(self._data[key], self._index[key], name=self.name)
        if isinstance(key, int):
            return self._data[key]
        if key in self._index:
            position = self._index.index(key)
            return self._data[position]
        raise KeyError(key)

    @property
    def index(self) -> Index:
        return Index(self._index)

    @property
    def values(self) -> List[Any]:  # pragma: no cover - trivial
        return list(self._data)

    @property
    def dtype(self) -> str:
        for value in self._data:
            if _is_null(value):
                continue
            if isinstance(value, bool):
                return "bool"
            if isinstance(value, int):
                return "int64"
            if isinstance(value, float):
                return "float64"
            if isinstance(value, (_dt.datetime, _dt.date)):
                return "datetime64[ns]"
            return "object"
        return "object"

    def tolist(self) -> List[Any]:
        return list(self._data)

    def to_dict(self) -> Dict[Any, Any]:
        return dict(zip(self._index, self._data))

    def fillna(self, value: Any) -> "Series":
        filled = [value if _is_null(item) else item for item in self._data]
        return Series(filled, self._index, name=self.name)

    def astype(self, dtype: Any) -> "Series":
        dtype_name = dtype.__name__ if isinstance(dtype, type) else str(dtype)
        dtype_name = dtype_name.lower()
        if dtype_name in {"str", "string"}:
            converted = [str(item) if not _is_null(item) else "" for item in self._data]
            return Series(converted, self._index, name=self.name)
        if dtype_name in {"int", "int64"}:
            converted = []
            for item in self._data:
                if _is_null(item):
                    raise ValueError("Cannot convert null to int")
                converted.append(int(float(item)))
            return Series(converted, self._index, name=self.name)
        if dtype_name in {"float", "float64"}:
            converted = []
            for item in self._data:
                if _is_null(item):
                    converted.append(math.nan)
                else:
                    converted.append(float(item))
            return Series(converted, self._index, name=self.name)
        raise TypeError(f"Unsupported dtype conversion: {dtype}")

    def isnull(self) -> "Series":
        return Series([_is_null(item) for item in self._data], self._index, name=self.name)

    def nunique(self) -> int:
        seen = set()
        for item in self._data:
            if _is_null(item):
                continue
            seen.add(item)
        return len(seen)

    def _numeric_values(self, errors: str = "raise") -> List[float]:
        numeric_values = []
        for item in self._data:
            try:
                numeric_values.append(_coerce_numeric(item))
            except ValueError:
                if errors == "coerce":
                    numeric_values.append(math.nan)
                else:
                    raise
        return numeric_values

    def sum(self) -> float:
        total = 0.0
        any_value = False
        all_bool = True
        for item in self._data:
            if isinstance(item, bool):
                total += int(item)
                any_value = True
            else:
                all_bool = False
                try:
                    total += _coerce_numeric(item)
                    any_value = True
                except ValueError:
                    continue
        if not any_value:
            return 0.0
        return int(total) if all_bool else total

    def mean(self) -> float:
        values = [val for val in self._numeric_values(errors="raise") if not math.isnan(val)]
        if not values:
            return math.nan
        return sum(values) / len(values)

    def median(self) -> float:
        values = [val for val in self._numeric_values(errors="raise") if not math.isnan(val)]
        if not values:
            return math.nan
        values.sort()
        midpoint = len(values) // 2
        if len(values) % 2 == 1:
            return values[midpoint]
        return (values[midpoint - 1] + values[midpoint]) / 2

    def std(self) -> float:
        values = [val for val in self._numeric_values(errors="raise") if not math.isnan(val)]
        if len(values) < 2:
            return 0.0
        return statistics.stdev(values)

    def min(self) -> float:
        values = [val for val in self._numeric_values(errors="raise") if not math.isnan(val)]
        return min(values) if values else math.nan

    def max(self) -> float:
        values = [val for val in self._numeric_values(errors="raise") if not math.isnan(val)]
        return max(values) if values else math.nan

    def __repr__(self) -> str:  # pragma: no cover - cosmetic
        return f"Series({self._data!r}, index={self._index!r}, name={self.name!r})"


class DataFrame:
    """Bare-bones tabular structure supporting column access and summary stats."""

    def __init__(self, data: Optional[Any] = None, columns: Optional[List[str]] = None):
        if data is None:
            data = {}

        if isinstance(data, dict):
            self._columns = list(data.keys()) if columns is None else list(columns)
            if not self._columns:
                self._rows: List[Dict[str, Any]] = []
            else:
                lengths = {len(data[col]) for col in self._columns}
                if len(lengths) > 1:
                    raise ValueError("All columns must be same length")
                row_count = lengths.pop() if lengths else 0
                self._rows = []
                for idx in range(row_count):
                    row = {}
                    for col in self._columns:
                        row[col] = data[col][idx]
                    self._rows.append(row)
        elif isinstance(data, list) and data and isinstance(data[0], dict):
            if columns is None:
                column_set = set()
                for row in data:
                    column_set.update(row.keys())
                self._columns = list(column_set)
            else:
                self._columns = list(columns)
            self._rows = []
            for entry in data:
                row = {col: entry.get(col) for col in self._columns}
                self._rows.append(row)
        else:
            raise TypeError("Unsupported data type for DataFrame")

    def __len__(self) -> int:  # pragma: no cover - trivial
        return len(self._rows)

    def __iter__(self) -> Iterator[str]:  # pragma: no cover - trivial
        return iter(self._columns)

    def __getitem__(self, key: Union[str, List[str]]) -> Union[Series, "DataFrame"]:
        if isinstance(key, list):
            data = {col: [row.get(col) for row in self._rows] for col in key}
            return DataFrame(data)
        if key not in self._columns:
            raise KeyError(key)
        column_data = [row.get(key) for row in self._rows]
        return Series(column_data, index=range(len(self._rows)), name=key)

    @property
    def columns(self) -> Index:
        return Index(self._columns)

    @property
    def empty(self) -> bool:
        return not self._rows

    @property
    def shape(self) -> tuple:  # pragma: no cover - trivial
        return (len(self._rows), len(self._columns))

    def to_rows(self, header: bool = True, index: bool = False) -> Iterator[List[Any]]:
        if header:
            yield list(self._columns)
        for pos, row in enumerate(self._rows):
            values = [row.get(col) for col in self._columns]
            if index:
                yield [pos] + values
            else:
                yield values

    def to_csv(self, path: str, index: bool = True) -> None:
        with open(path, "w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            header = ["index"] + self._columns if index else list(self._columns)
            writer.writerow(header)
            for idx, row_values in enumerate(self.to_rows(header=False)):
                if index:
                    writer.writerow([idx] + row_values)
                else:
                    writer.writerow(row_values)

    def dropna(self, how: str = "any", axis: int = 0) -> "DataFrame":
        if axis == 0:
            if how == "all":
                filtered_rows = []
                for row in self._rows:
                    if any(not _is_null(row.get(col)) for col in self._columns):
                        filtered_rows.append(dict(row))
            else:
                filtered_rows = [
                    dict(row)
                    for row in self._rows
                    if all(not _is_null(row.get(col)) for col in self._columns)
                ]
            return DataFrame(filtered_rows, columns=self._columns)
        if axis == 1:
            keep_columns = []
            for col in self._columns:
                if how == "all":
                    if any(not _is_null(row.get(col)) for row in self._rows):
                        keep_columns.append(col)
                else:
                    if all(not _is_null(row.get(col)) for row in self._rows):
                        keep_columns.append(col)
            return DataFrame([{col: row.get(col) for col in keep_columns} for row in self._rows], columns=keep_columns)
        raise ValueError("axis must be 0 or 1")

    def reset_index(self, drop: bool = False) -> "DataFrame":
        if drop:
            return DataFrame(self._rows, columns=self._columns)
        data = [{"index": idx, **row} for idx, row in enumerate(self._rows)]
        return DataFrame(data)

    def sample(self, n: int, random_state: Optional[int] = None) -> "DataFrame":
        if n >= len(self._rows):
            return DataFrame(self._rows, columns=self._columns)
        rng = random.Random(random_state)
        indices = rng.sample(range(len(self._rows)), n)
        sampled = [self._rows[i] for i in indices]
        return DataFrame(sampled, columns=self._columns)

    def isnull(self) -> "DataFrame":
        data = [
            {col: _is_null(row.get(col)) for col in self._columns}
            for row in self._rows
        ]
        return DataFrame(data, columns=self._columns)

    def _numeric_columns(self) -> List[str]:
        numeric_cols = []
        for col in self._columns:
            series = self[col]
            try:
                series._numeric_values()
                numeric_cols.append(col)
            except ValueError:
                continue
        return numeric_cols

    def _aggregate(self, func: str) -> Series:
        results = []
        labels = []
        for col in self._columns:
            series = self[col]
            try:
                if func == "sum":
                    value = series.sum()
                elif func == "mean":
                    value = series.mean()
                elif func == "median":
                    value = series.median()
                elif func == "std":
                    value = series.std()
                elif func == "min":
                    value = series.min()
                elif func == "max":
                    value = series.max()
                else:
                    raise ValueError(f"Unsupported aggregate: {func}")
            except ValueError:
                continue
            if isinstance(value, float) and math.isnan(value):
                continue
            results.append(value)
            labels.append(col)
        return Series(results, index=labels, name=func)

    def sum(self) -> Series:
        return self._aggregate("sum")

    def mean(self) -> Series:
        return self._aggregate("mean")

    def median(self) -> Series:
        return self._aggregate("median")

    def std(self) -> Series:
        return self._aggregate("std")

    def min(self) -> Series:
        return self._aggregate("min")

    def max(self) -> Series:
        return self._aggregate("max")

    @property
    def dtypes(self) -> Series:
        dtype_map = {col: self[col].dtype for col in self._columns}
        return Series(list(dtype_map.values()), index=list(dtype_map.keys()), name="dtypes")

    def nunique(self) -> Series:  # pragma: no cover - unused helper
        values = [self[col].nunique() for col in self._columns]
        return Series(values, index=self._columns, name="nunique")

    def __repr__(self) -> str:  # pragma: no cover - cosmetic
        return f"DataFrame(rows={len(self._rows)}, columns={self._columns!r})"


class EmptyDataError(ValueError):
    """Raised when attempting to load data from an empty CSV."""


def read_csv(path: str, nrows: Optional[int] = None) -> DataFrame:
    with open(path, "r", encoding="utf-8") as handle:
        reader = csv.reader(handle)
        try:
            header = next(reader)
        except StopIteration as exc:
            raise EmptyDataError("CSV file is empty") from exc
        rows = []
        for row in reader:
            rows.append(row)
            if nrows is not None and len(rows) >= nrows:
                break
    if not rows and nrows != 0:
        # Header present but no data rows – return an empty DataFrame.
        empty_data = {col: [] for col in header}
        return DataFrame(empty_data, columns=header)
    data: Dict[str, List[Any]] = {col: [] for col in header}
    for raw_row in rows:
        for idx, col in enumerate(header):
            data[col].append(raw_row[idx] if idx < len(raw_row) else None)
    return DataFrame(data, columns=header)


def to_numeric(values: Union[Series, Iterable[Any]], errors: str = "raise") -> Series:
    if isinstance(values, Series):
        numeric = values._numeric_values(errors=errors)
        return Series(numeric, index=values.index, name=values.name)
    series = Series(list(values))
    return Series(series._numeric_values(errors=errors), index=series.index)


def to_datetime(values: Union[Series, Iterable[Any]], errors: str = "raise") -> Series:
    data = []
    for item in values:
        try:
            data.append(_coerce_datetime(item))
        except ValueError:
            if errors == "coerce":
                data.append(None)
            else:
                raise
    if isinstance(values, Series):
        return Series(data, index=values.index, name=values.name)
    return Series(data)


def date_range(start: Union[str, _dt.datetime], periods: int) -> List[_dt.datetime]:
    base = _coerce_datetime(start)
    return [base + _dt.timedelta(days=offset) for offset in range(periods)]


def _is_numeric_dtype(obj: Any) -> bool:
    if isinstance(obj, Series):
        try:
            obj._numeric_values(errors="raise")
            return True
        except ValueError:
            return False
    return False


def _is_datetime_dtype(obj: Any) -> bool:
    if isinstance(obj, Series):
        return obj.dtype == "datetime64[ns]"
    return False


errors = SimpleNamespace(EmptyDataError=EmptyDataError)
api = SimpleNamespace(types=SimpleNamespace(
    is_numeric_dtype=_is_numeric_dtype,
    is_datetime64_any_dtype=_is_datetime_dtype,
))
