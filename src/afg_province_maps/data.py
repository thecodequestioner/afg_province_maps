"""Load, validate and classify province-level values.

Pure pandas, so data checks run without GIS dependencies.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from .names import norm_name

DEFAULT_NAME_COLUMN = "province"


class DataError(ValueError):
    """The input cannot be mapped. The message says what to fix."""


@dataclass(frozen=True)
class Scheme:
    """Class boundaries and labels. Class i covers [edges[i], edges[i+1])."""

    edges: list[float]
    labels: list[str]


def format_number(x: float) -> str:
    if abs(x) >= 1000:
        return f"{x:,.0f}"
    if abs(x) >= 10:
        return f"{x:.0f}"
    return f"{x:.3g}"


def load_values(path: Path, column: str, name_column: str = DEFAULT_NAME_COLUMN) -> pd.DataFrame:
    """Return columns name, value, key. Missing values stay NaN."""
    if not Path(path).exists():
        raise DataError(f"Data file not found: {path}")
    raw = pd.read_csv(path)
    for col in (name_column, column):
        if col not in raw.columns:
            raise DataError(
                f"Column '{col}' not found in {Path(path).name}. "
                f"Available columns: {', '.join(raw.columns)}"
            )
    if raw[name_column].isna().any():
        raise DataError(f"Blank province names in column '{name_column}'.")

    values = pd.to_numeric(raw[column], errors="coerce")
    bad = raw.loc[values.isna() & raw[column].notna(), name_column].astype(str).tolist()
    if bad:
        raise DataError(f"Column '{column}' has non-numeric values for: {', '.join(bad)}")

    out = pd.DataFrame({
        "name": raw[name_column].astype(str).str.strip(),
        "value": values.astype(float),
    })
    out["key"] = out["name"].map(norm_name)
    dupes = out.loc[out["key"].duplicated(keep=False), "name"].tolist()
    if dupes:
        raise DataError(f"Duplicate provinces (after name matching): {', '.join(dupes)}")
    return out.reset_index(drop=True)


def make_scheme(
    values: pd.Series,
    bins: list[float] | None = None,
    classes: int = 5,
    scheme: str = "quantile",
) -> Scheme:
    """Choose class boundaries.

    With explicit ``bins`` the edges are used as given. Otherwise ``quantile``
    gives equal counts per class and ``equal`` gives equal value ranges.
    Values outside the outer edges are placed in the first or last class.
    """
    data = values.dropna()
    if data.empty:
        raise DataError("The column has no numeric values to map.")

    if bins:
        edges = sorted({float(b) for b in bins})
        if len(edges) < 2:
            raise DataError("--bins needs at least two distinct values.")
    else:
        if classes < 2:
            raise DataError("--classes must be at least 2.")
        if scheme == "quantile":
            raw_edges = np.quantile(data, np.linspace(0, 1, classes + 1))
        elif scheme == "equal":
            raw_edges = np.linspace(data.min(), data.max(), classes + 1)
        else:
            raise DataError(f"Unknown scheme '{scheme}'. Use 'quantile' or 'equal'.")
        edges = sorted({float(e) for e in raw_edges})
        if len(edges) < 2:
            raise DataError("All values are identical, so they cannot be classed. Use --bins.")

    labels = [f"{format_number(lo)} to {format_number(hi)}" for lo, hi in zip(edges[:-1], edges[1:])]
    if len(set(labels)) != len(labels):
        # Rounding made two classes read the same; show more significant digits.
        labels = [f"{lo:.6g} to {hi:.6g}" for lo, hi in zip(edges[:-1], edges[1:])]
    if len(set(labels)) != len(labels):
        raise DataError("Class edges are too close to label distinctly. Use --bins with wider spacing.")
    return Scheme(edges=edges, labels=labels)


def assign(values: pd.Series, scheme: Scheme) -> pd.Series:
    """Return the class label for each value, or None where the value is missing."""
    cut_edges = [-math.inf, *scheme.edges[1:-1], math.inf]
    classed = pd.cut(values, bins=cut_edges, labels=scheme.labels, right=False, include_lowest=True)
    return classed.astype(object).where(values.notna(), None)
