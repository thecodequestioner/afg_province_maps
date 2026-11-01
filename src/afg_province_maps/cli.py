"""Command-line interface.

    afg-province-maps check --data FILE --column COL
    afg-province-maps map   --data FILE --column COL [options]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

from . import __version__
from .boundaries import check_names, default_boundary_path, join, load_boundaries
from .data import DataError, assign, format_number, load_values, make_scheme
from .render import static_map

EXPECTED_PROVINCES = 34
DEFAULT_BOUNDARIES = default_boundary_path()
FORMATS = ("png", "pdf")


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="afg-province-maps",
        description="Map any province-level variable onto Afghanistan's provinces.",
    )
    p.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = p.add_subparsers(dest="command", required=True)

    def add_data_args(sp):
        sp.add_argument("--data", required=True, type=Path, help="CSV with one row per province")
        sp.add_argument("--column", required=True, help="column holding the value to map")
        sp.add_argument("--name-column", default="province",
                        help="column holding province names (default: province)")

    check = sub.add_parser("check", help="validate a data file and print summary statistics")
    add_data_args(check)
    check.add_argument("--boundaries", type=Path, default=DEFAULT_BOUNDARIES,
                       help="optional alternative ADM1 boundary file (default: bundled GeoJSON)")

    m = sub.add_parser("map", help="draw the province map in PNG and/or PDF")
    add_data_args(m)
    m.add_argument("--label", help="legend title (default: the column name)")
    m.add_argument("--title", help="map title (default: derived from the label)")
    m.add_argument("--bins", help="comma-separated class edges, e.g. 0,250000,500000,1000000")
    m.add_argument("--classes", type=int, default=5,
                   help="number of classes when --bins is not given (default: 5)")
    m.add_argument("--scheme", choices=["quantile", "equal"], default="quantile",
                   help="quantile = equal counts per class; equal = equal value ranges (default: quantile)")
    m.add_argument("--cmap", default="YlOrRd", help="matplotlib colormap name (default: YlOrRd)")
    m.add_argument("--boundaries", type=Path, default=DEFAULT_BOUNDARIES,
                   help="optional alternative ADM1 GeoJSON or shapefile (default: bundled GeoJSON)")
    m.add_argument("--out", type=Path, default=Path("outputs"), help="output folder (default: outputs)")
    m.add_argument("--stem", help="output file name without extension (default: from the column name)")
    m.add_argument("--formats", default="png,pdf", help="comma-separated: png,pdf (default: png,pdf)")
    return p


def _check(args) -> int:
    values = load_values(args.data, args.column, args.name_column)
    check_names(values, load_boundaries(Path(args.boundaries)))
    v = values["value"]
    print(f"File:       {args.data}")
    print(f"Column:     {args.column}")
    print(f"Provinces:  {len(values)} rows, {int(v.notna().sum())} with values")
    if v.notna().any():
        print(f"Range:      {format_number(v.min())} to {format_number(v.max())} "
              f"(median {format_number(v.median())})")
    missing = values.loc[v.isna(), "name"].tolist()
    if missing:
        print(f"Missing:    {', '.join(missing)}")
    if len(values) != EXPECTED_PROVINCES:
        print(f"Note:       Afghanistan has {EXPECTED_PROVINCES} provinces; this file has {len(values)} rows.")
    print("Check passed.")
    return 0


def _map(args) -> int:
    formats = list(dict.fromkeys(f.strip().lower() for f in args.formats.split(",") if f.strip()))
    if not formats:
        raise DataError("Choose at least one output format: png or pdf.")
    bad_formats = set(formats) - set(FORMATS)
    if bad_formats:
        raise DataError(f"Unknown format(s): {', '.join(sorted(bad_formats))}. Choose from png, pdf.")
    bins = None
    if args.bins:
        try:
            bins = [float(b) for b in args.bins.split(",") if b.strip()]
        except ValueError:
            raise DataError(f"--bins must be comma-separated numbers, e.g. 0,250000,500000. Got: {args.bins}")

    label = args.label or args.column
    title = args.title or f"Afghanistan: {label} by province"
    stem_name = args.stem or re.sub(r"[^A-Za-z0-9_-]+", "_", args.column).strip("_")
    stem = args.out / stem_name

    values = load_values(args.data, args.column, args.name_column)
    scheme = make_scheme(values["value"], bins=bins, classes=args.classes, scheme=args.scheme)
    values["class"] = assign(values["value"], scheme)
    boundary_path = Path(args.boundaries)
    gdf, no_data = join(values, load_boundaries(boundary_path))

    note = ("Boundaries: geoBoundaries (gbOpen), simplified and not authoritative. "
            "Map does not express a position on borders.")
    static_map(gdf, scheme.labels, cmap=args.cmap, title=title, legend_title=label,
               note=note, stem=stem, formats=formats)
    meta = {
        "afg_province_maps_version": __version__,
        "input_file": Path(args.data).name,
        "input_sha256": hashlib.sha256(Path(args.data).read_bytes()).hexdigest(),
        "column": args.column,
        "name_column": args.name_column,
        "legend_title": label,
        "title": title,
        "scheme": "custom bins" if bins else args.scheme,
        "class_edges": scheme.edges,
        "class_labels": scheme.labels,
        "cmap": args.cmap,
        "provinces_mapped": int(gdf["value"].notna().sum()),
        "provinces_without_data": no_data,
        "boundaries_file": boundary_path.name,
        "boundaries_sha256": hashlib.sha256(boundary_path.read_bytes()).hexdigest(),
    }
    Path(f"{stem}.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")

    counts = gdf["class"].value_counts()
    print(f"Mapped {meta['provinces_mapped']} provinces.")
    for lab in scheme.labels:
        print(f"  {lab:<24} {int(counts.get(lab, 0))}")
    if no_data:
        print(f"No data for: {', '.join(no_data)}")
    outputs = [f"{stem}.{fmt}" for fmt in formats]
    if "png" in formats:
        outputs.append(f"{stem}_transparent.png")

    print(f"Wrote {', '.join(outputs)} and {stem}.json.")
    return 0


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return _check(args) if args.command == "check" else _map(args)
    except DataError as err:
        print(f"error: {err}", file=sys.stderr)
        return 2
