# Third-party data notices

The MIT licence in `LICENSE` covers the project's code. It does not cover the data files in this repository, which remain under their providers' terms.

## geoBoundaries ADM1 geometry

File: `data/boundaries/geoBoundaries-AFG-ADM1_simplified.geojson` (also packaged in `src/afg_province_maps/data/boundaries/`).

- Project: [geoBoundaries](https://www.geoboundaries.org/)
- Dataset: Afghanistan (`AFG`), ADM1, simplified GeoJSON (gbOpen)
- Release: geoBoundaries commit `9469f09` (built 12 December 2023)
- Source URL: https://github.com/wmgeolab/geoBoundaries/raw/9469f09/releaseData/gbOpen/AFG/ADM1/geoBoundaries-AFG-ADM1_simplified.geojson
- Accessed: 1 November 2026
- SHA-256: `c0ae276c6df08d6619ce738720ea7a052079e2cb186f1d6e2de9a1d7aef7a86b`
- Licence: Public Domain, per geoBoundaries metadata. The metadata names Wikimedia Commons as the source. The matching Commons file is [File:Afghanistan locator map.svg](https://commons.wikimedia.org/wiki/File:Afghanistan_locator_map.svg), released into the public domain by its author (MarsRover, 2007).
- Represents: boundaries as of 2007.
- Suggested citation: Runfola, D. et al. (2020). "geoBoundaries: A global database of political administrative boundaries." *PLOS ONE*, 15(4), e0231866.

## Example population CSV

File: `examples/population_2027_ocha.csv`

- Source: Afghanistan Data Working Group, contributed by OCHA Afghanistan. "Afghanistan - Subnational Population Statistics", Humanitarian Data Exchange, dataset `cod-ps-afg`, https://data.humdata.org/dataset/cod-ps-afg
- Resource: "Afghanistan: Estimated Population 2027 for Admin 1 (province)", file `AFG_Estimated_Population_2027_DWG_202607_Admin1.csv`, last modified 21 October 2026.
- Licence: Creative Commons Attribution 4.0 International (CC BY 4.0), https://creativecommons.org/licenses/by/4.0/
- Changes: columns selected and renamed. Values are unchanged. Kept: province, P-code, total, rural and urban population. Removed: age and sex breakdowns.
- Accessed: 1 November 2026
- These are interim operational estimates, not census results.