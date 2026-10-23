# Notice of origin and modification

This repository contains a **modified version** of historical border data from:

> **historical-basemaps** by André Ourednik and contributors
> https://github.com/aourednik/historical-basemaps
> Licensed under the GNU General Public License v3.0.
> Snapshot used: commit `da7a4b735ecef70aebdc9c73e409d8a2500d50f3` (15 Sep 2026)

The unmodified upstream files are not copied here. Get them from the repository above at that commit.

## What was changed (GPL-3.0 §5a)

The era and overlay files in `../site/` were produced from the upstream GeoJSON by the scripts in `scripts/`, with these changes:
- The polygons were rasterized onto a Miller-projection grid (4096 × 2111) and snapped to Natural Earth coastlines. Small coastal gaps were filled.
- `scripts/era_edits.py` applies hand corrections for each year. Realms are split, merged, renamed, re-dated, added, removed and re-coloured, and borders are corrected with boxes and polygons.
- Later corrections (2026), including new 1210, 1450 and 1750 maps and fixes to 1200, 1453, 1900, 1914 and 1945, were made as data records. Their GPL records are in `hb-gpl/`, and their results are in `../site/eras/`.
- Unclaimed land is filled by carrying peoples forward or backward from neighbouring years.
- A 2026 snapshot was added from Natural Earth admin-0 boundaries (public domain).
- The religion, culture and development layers in `../site/rel/`, `../site/cul/` and `../site/dev/` are painted onto this border data by the rules and scripts in `scripts/overlays/`.

- October 2026: name-only corrections (for example Kamakura shogunate, Qing Empire, Afsharid Iran, colonial names in 1945) applied by `scripts/fixes-2026/fix_batch3.py`, `fix_batch4.py` and `fix_batch5.py` (22 October: misspelt, garbled and out-of-date realm names). Border shapes were not changed by these. `scripts/fixes-2026/fix_1530_ottoman.py` (22 October) moved the 1530 map's leftover Mamluk territory (Barqa) and an Aq Qoyunlu sliver into the Ottoman Empire; their shapes are unchanged. `scripts/derive-2026/make_117.py` (23 October) derives a new 117 CE map from the 100 CE map: Dacia, Arabia Petraea and Armenia join the Roman Empire and Mesopotamia is carved from Parthia.

These modifications were made by Gregory D Wheeler in 2026 and last revised in October 2026. The 331 pre-launch corrections are part of this GPL work; they are the `notes` arrays in `../site/eras/*.json`. The public corresponding source is https://github.com/thewheeleratlas/atlas-data.

## Other inputs (public domain, not included)

Natural Earth 1:10m layers (land, lakes, glaciers, rivers, admin-0, admin-1). Fetch them with `scripts/fetch_natural_earth.py`.
