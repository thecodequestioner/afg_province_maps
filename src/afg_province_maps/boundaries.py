"""Province boundaries from geoBoundaries ADM1. Requires geopandas."""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from .data import DataError
from .names import norm_name

NAME_FIELD = "shapeName"  # geoBoundaries field holding the province name
BOUNDARY_FILENAME = "geoBoundaries-AFG-ADM1_simplified.geojson"


def default_boundary_path() -> Path:
    """Return the boundary dataset shipped with the installed package."""
    return Path(__file__).resolve().parent / "data" / "boundaries" / BOUNDARY_FILENAME


def load_boundaries(path: Path):
    if not Path(path).exists():
        raise DataError(
            f"Boundary file not found: {path}\n"
            "Use the bundled default boundary file or check the path passed with --boundaries."
        )
    import geopandas as gpd

    gdf = gpd.read_file(path)
    if NAME_FIELD not in gdf.columns:
        raise DataError(f"Field '{NAME_FIELD}' missing from {Path(path).name}. Is this a geoBoundaries file?")
    gdf = gdf[[NAME_FIELD, "geometry"]].rename(columns={NAME_FIELD: "name"}).copy()
    gdf["key"] = gdf["name"].map(norm_name)
    dupes = gdf.loc[gdf["key"].duplicated(keep=False), "name"].tolist()
    if dupes:
        raise DataError(f"Duplicate province names in boundary file: {', '.join(dupes)}")
    if gdf.crs is None:
        gdf = gdf.set_crs(4326)
    return gdf.to_crs(4326)


def check_names(values: pd.DataFrame, boundaries) -> None:
    """Raise DataError if any province in the data matches no boundary."""
    unmatched = sorted(set(values["key"]) - set(boundaries["key"]))
    if unmatched:
        names = values.loc[values["key"].isin(unmatched), "name"].tolist()
        raise DataError(
            f"These provinces match no boundary: {', '.join(names)}. "
            "Correct the spelling in the data file, or add a spelling variant "
            "to ALIASES in names.py (see the README)."
        )


def join(values: pd.DataFrame, boundaries):
    """Attach values to boundaries. Returns (GeoDataFrame, names with no data)."""
    check_names(values, boundaries)
    merged = boundaries.merge(
        values.rename(columns={"name": "source_name"}),
        on="key", how="left", validate="one_to_one",
    )
    # Display the spelling from the data file; fall back to the boundary name.
    merged["name"] = merged["source_name"].fillna(merged["name"])
    no_data = merged.loc[merged["value"].isna(), "name"].tolist()
    return merged, no_data
