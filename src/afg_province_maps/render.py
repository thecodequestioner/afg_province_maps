"""Draw static province maps in PNG or PDF with matplotlib.

Imports are inside functions so that `afg-province-maps check` runs without plotting libraries.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np

NO_DATA = "No data"
NO_DATA_COLOUR = "#d9d9d9"


def palette(cmap: str, n: int) -> list[str]:
    """n evenly spaced colours from a matplotlib colormap, as hex strings."""
    import matplotlib
    from matplotlib.colors import to_hex

    cm = matplotlib.colormaps[cmap]
    return [to_hex(cm(x)) for x in np.linspace(0.2, 0.9, max(n, 2))[:n]]


def static_map(gdf, labels, *, cmap, title, legend_title, note, stem, formats):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Patch

    colours = dict(zip(labels, palette(cmap, len(labels))))
    fills = [colours.get(c, NO_DATA_COLOUR) for c in gdf["class"]]

    # Separate axes keep the legend from covering any province.
    fig, (ax, legend_ax) = plt.subplots(
        1,
        2,
        figsize=(12, 7.5),
        gridspec_kw={"width_ratios": [4.5, 1.5], "wspace": 0.04},
    )
    gdf.plot(ax=ax, color=fills, edgecolor="white", linewidth=0.6)
    for _, row in gdf.iterrows():
        pt = row.geometry.representative_point()
        ax.annotate(row["name"], (pt.x, pt.y), ha="center", va="center", fontsize=5.5, color="#222")

    handles = [Patch(facecolor=colours[l], label=l) for l in labels if (gdf["class"] == l).any()]
    if gdf["value"].isna().any():
        handles.append(Patch(facecolor=NO_DATA_COLOUR, label=NO_DATA))
    legend_ax.set_axis_off()
    legend_ax.legend(
        handles=handles,
        title=legend_title,
        loc="lower right",
        frameon=True,
        fontsize=8,
        title_fontsize=9,
        borderpad=0.8,
        labelspacing=0.55,
    )
    ax.set_title(title, fontsize=13, loc="left")
    ax.set_axis_off()
    fig.text(0.02, 0.025, note, fontsize=7, color="#555")

    stem = Path(stem)
    stem.parent.mkdir(parents=True, exist_ok=True)

    for fmt in formats:
        fig.savefig(
            f"{stem}.{fmt}",
            dpi=300 if fmt == "png" else None,
            bbox_inches="tight",
        )

        if fmt == "png":
            transparent_path = stem.with_name(f"{stem.name}_transparent.png")
            fig.savefig(
                transparent_path,
                dpi=300,
                bbox_inches="tight",
                transparent=True,
            )

    plt.close(fig)  # release memory when the function is called in a loop

