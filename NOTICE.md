# Notice

This repository is the complete corresponding source, under the GNU General Public License v3.0, for the historical map data used by [The Wheeler Atlas](https://thewheeleratlas.com). The license text is [`LICENSE`](LICENSE). The same text is also in [`data-source/hb-gpl/LICENSE`](data-source/hb-gpl/LICENSE).

The modifications described below were made by Gregory D Wheeler in 2026 and last revised in October 2026.

"The Wheeler Atlas" and the Compass Helm logo are trademarks of The Wheeler Atlas, LLC. This license does not grant trademark rights (GPL-3.0 section 7(e)).

## historical-basemaps

The border data is a modified version of:

> **historical-basemaps** by André Ourednik and contributors
> https://github.com/aourednik/historical-basemaps
> Licensed under the GNU General Public License v3.0.
> Snapshot used: commit `da7a4b735ecef70aebdc9c73e409d8a2500d50f3` (15 September 2026)
> https://github.com/aourednik/historical-basemaps/tree/da7a4b735ecef70aebdc9c73e409d8a2500d50f3

The unmodified upstream files are not copied into this repository. Check them out at that commit. The border build reads them from the directory set by `HHA_HB`, which defaults to `data-source/upstream/historical-basemaps`.

`site/data/eras.json` records the same origin in its `source` field: "historical-basemaps by A. Ourednik et al. (GPL-3.0); 2026 from Natural Earth".

## Natural Earth

Coastlines, lakes, glaciers, rivers, and the 2026 country and province outlines come from [Natural Earth](https://www.naturalearthdata.com/), which is in the public domain. They are not vendored here. [`data-source/scripts/fetch_natural_earth.py`](data-source/scripts/fetch_natural_earth.py) downloads the 1:10m GeoJSON layers from the [nvkelso/natural-earth-vector](https://github.com/nvkelso/natural-earth-vector) repository:

- `ne_10m_land`
- `ne_10m_lakes`
- `ne_10m_glaciated_areas`
- `ne_10m_rivers_lake_centerlines`
- `ne_10m_admin_0_countries`
- `ne_10m_admin_1_states_provinces`

## Maddison Project Database 2020

[`data-source/scripts/overlays/maddison2020.csv`](data-source/scripts/overlays/maddison2020.csv) is the Maddison Project Database 2020 (Bolt and van Zanden), distributed via [Our World in Data](https://github.com/owid/owid-datasets). It is under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). It stays under that license. It is an input to the development score from 1815, read by `devindex.py`. It is not relicensed under the GPL.

## Modifications (GPL-3.0 section 5)

The files in `site/` were produced from the upstream GeoJSON by the scripts in `data-source/scripts/`, with these changes:

- Polygons were rasterized onto a Miller-projection grid (4096 × 2111) and snapped to Natural Earth coastlines. Small coastal gaps were filled.
- `data-source/scripts/era_edits.py` applies the hand corrections for each year. Realms are split, merged, renamed, re-dated, added, removed and re-coloured, and borders are corrected with boxes and polygons.
- Later corrections from 2026, including new maps for 1210, 1450 and 1750 and fixes to 1200, 1453, 1900, 1914 and 1945, are stored as data records in `data-source/hb-gpl/`. Their results are in `site/eras/`.
- Unclaimed land is filled by carrying peoples forward or backward from neighbouring years.
- A 2026 snapshot was added from Natural Earth admin-0 boundaries (public domain).
- The religion, culture and development layers in `site/rel/`, `site/cul/` and `site/dev/` are painted onto this border data by the rules and scripts in `data-source/scripts/overlays/`.
- October 2026 name-only corrections (for example Kamakura shogunate, Qing Empire, Afsharid Iran, and colonial names in 1945) were applied by `data-source/scripts/fixes-2026/fix_batch3.py` and `fix_batch4.py`, and on 22 October 2026 a further batch of misspelt, garbled and out-of-date realm names (for example Satavahana Empire, Mamluk Sultanate, Malay sultanates, Kyivan Rus') by `fix_batch5.py`. Those scripts did not change border shapes. `fix_1530_ottoman.py` (22 October 2026) moved the 1530 map's leftover Mamluk territory (Barqa) and an Aq Qoyunlu sliver into the Ottoman Empire, changing which realm they belong to but not their shapes.

The 331 pre-launch corrections are part of these GPL modifications. They are the `notes` arrays in `site/eras/*.json`: 331 notes across 57 of the 62 era files. Each note is a short string recorded with that year's map. They are not a separate layer and they are not withheld from this release.

A further file-by-file account of the build, including the n/a register, is in [`data-source/NOTICE.md`](data-source/NOTICE.md) and [`data-source/README.md`](data-source/README.md). The per-polity records in `data-source/hb-gpl/` have their own notice in [`data-source/hb-gpl/NOTICE.md`](data-source/hb-gpl/NOTICE.md).
