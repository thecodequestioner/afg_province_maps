# Afghanistan ADM1 boundaries

The simplified geoBoundaries GeoJSON is included in this repository at:

```text
data/boundaries/geoBoundaries-AFG-ADM1_simplified.geojson
```

The same file is included as package data in `src/afg_province_maps/data/boundaries/`, so the installed command finds it from any working directory. A test checks that both copies are identical. The CLI uses the packaged copy by default; pass `--boundaries PATH` to use another file.

| Item | Details |
|---|---|
| Source | geoBoundaries, Afghanistan (ISO `AFG`), ADM1 provinces, simplified GeoJSON |
| Release | geoBoundaries gbOpen, commit `9469f09` (built 12 December 2023) |
| Accessed | 1 November 2026 |
| SHA-256 | `c0ae276c6df08d6619ce738720ea7a052079e2cb186f1d6e2de9a1d7aef7a86b` |
| Licence | Public Domain, per geoBoundaries metadata. Matching Commons file: [File:Afghanistan locator map.svg](https://commons.wikimedia.org/wiki/File:Afghanistan_locator_map.svg) (public domain, 2007) |
| Currency | Boundaries represent 2007 |

Province names are in the `shapeName` property. `Ghanzi` is handled as a spelling variant of Ghazni in `src/afg_province_maps/names.py`.

These boundaries are simplified and not authoritative, and the map does not express a position on borders. See [`THIRD_PARTY_NOTICES.md`](../../THIRD_PARTY_NOTICES.md) for attribution.
