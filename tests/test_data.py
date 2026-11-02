from pathlib import Path

import pandas as pd
import pytest

from afg_province_maps.data import DataError, assign, load_values, make_scheme

EXAMPLE = Path(__file__).resolve().parents[1] / "examples" / "population_2027_ocha.csv"


def test_example_loads_all_provinces():
    df = load_values(EXAMPLE, "population_2027")
    assert len(df) == 34
    assert df["value"].notna().all()


def test_quantile_scheme_assigns_every_value():
    values = pd.Series([1, 2, 3, 4, 10, 20, 30, 40, 100, None], dtype=float)
    scheme = make_scheme(values, classes=4, scheme="quantile")
    labels = assign(values, scheme)
    assert labels.isna().sum() == 1  # only the missing value
    assert labels.dropna().isin(scheme.labels).all()


def test_explicit_bins_clamp_outside_values():
    values = pd.Series([-5, 50, 5000], dtype=float)
    scheme = make_scheme(values, bins=[0, 100, 1000])
    labels = assign(values, scheme).tolist()
    assert labels == [scheme.labels[0], scheme.labels[0], scheme.labels[1]]


def test_identical_values_need_bins():
    with pytest.raises(DataError, match="identical"):
        make_scheme(pd.Series([7.0, 7.0, 7.0]), classes=3)


def test_duplicate_after_name_matching(tmp_path):
    path = tmp_path / "d.csv"
    path.write_text("province,x\nKabul,1\nKabol,2\n")
    with pytest.raises(DataError, match="Duplicate"):
        load_values(path, "x")


def test_missing_column_message(tmp_path):
    path = tmp_path / "d.csv"
    path.write_text("province,x\nKabul,1\n")
    with pytest.raises(DataError, match="Available columns"):
        load_values(path, "nope")


def test_non_numeric_value_rejected(tmp_path):
    path = tmp_path / "d.csv"
    path.write_text("province,x\nKabul,abc\n")
    with pytest.raises(DataError, match="non-numeric"):
        load_values(path, "x")


def test_labels_stay_distinct_when_rounding_would_collide():
    edges = [1.2345, 1.2346, 1.2347, 9.0]
    scheme = make_scheme(pd.Series(edges), bins=edges)
    assert len(set(scheme.labels)) == len(scheme.labels)


def test_class_labels_exclude_upper_limit_except_top_class():
    scheme = make_scheme(pd.Series([1.0, 3.0]), bins=[0, 2, 4, 6])
    assert scheme.labels == ["under 2", "2 to under 4", "4 and above"]


def test_two_class_labels():
    scheme = make_scheme(pd.Series([1.0, 3.0]), bins=[0, 2, 4])
    assert scheme.labels == ["under 2", "2 and above"]