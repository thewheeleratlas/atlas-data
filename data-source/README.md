# Corresponding source for the GPL-3.0 data

This folder holds the scripts and records that build and correct The Wheeler Atlas's historical border data and its religion, culture and development layers. The scripts, the correction records and the map layers they produce are licensed under the **GNU GPL v3.0** ([`../LICENSE`](../LICENSE); the same text is in `hb-gpl/LICENSE`). `scripts/overlays/maddison2020.csv` is an input under **CC BY 4.0** (Maddison Project Database 2020, Bolt and van Zanden, via Our World in Data) and is not relicensed. This repository is the public corresponding source: https://github.com/thewheeleratlas/atlas-data. See `NOTICE.md` for the origin of the data and what was changed.

The border data is a modified version of **[historical-basemaps](https://github.com/aourednik/historical-basemaps)** by André Ourednik and contributors. The data itself, as deployed, is in `../site/` (see the table in `../README.md`).

## What's here

```
NOTICE.md                 origin, upstream snapshot and the modifications made (GPL-3.0 §5a)
NA-REGISTER.csv           every area shown as n/a (unknown, mixed or disputed), by era
requirements.txt          Python packages for the scripts
hb-gpl/                   GPL records behind the 2026 corrections (snapshots, lineages, geometry, era notes)
scripts/
  common.py, fetch_natural_earth.py, s1_masks.py, s6_eras.py, era_edits.py    border build
  overlays/               religion_rules.py, culture_rules.py, s8_religion.py, s10_develop.py, cities_hist.py,
                          ovmain_build.py, popw.py, devindex.py (+ maddison2020.csv)
  fixes-2026/             fix_batch3.py, fix_batch4.py: October 2026 name corrections applied to the era files;
                          build_disputed.py: hatched disputed areas (Natural Earth, public domain)
  unpack_eras.py          writes the deployed era rasters back out as PNG files
  build_realm_index.py    writes site/data/realm-index.json (which era maps each realm name is on) for the map's search
```

## Rebuilding

The border pipeline:
1. `fetch_natural_earth.py`
2. `s1_masks.py`
3. `s6_eras.py` (reads historical-basemaps from `HHA_HB`, default `upstream/historical-basemaps`)

Then apply the 2026 name corrections: `python3 fixes-2026/fix_batch3.py <eras folder> <data folder>` and the same for `fix_batch4.py`.

After any change to `site/eras/`, rebuild the search index: `python3 build_realm_index.py` (writes `site/data/realm-index.json`).

The overlay scripts read an atlas site folder set by `HHA_SITE`, and a work folder set by `HHA_WORKDIR` that holds the Natural Earth masks:

```
python3 s8_religion.py religion
python3 s8_religion.py culture
python3 s10_develop.py
```

`ovmain.json` is built by `ovmain_build.py` (run it in a folder holding `terrain4096.npy`, made by the border pipeline). Its population weights (`popw.py`, `devindex.py`) read the atlas's modern country grid (`data/world.json`, `tiles/ids/0_0_0.png`) from a folder set by `HHA_ATLAS`.

Each layer is defined by ordered rules: (first year, last year, faith or culture, where). A later rule overrides an earlier one, so most corrections are a single added line.

## Data format

- `site/eras/<key>.json`: `{y, src, realms, ents, borders, notes, _png}` for one year. `_png` is the 4096 × 2111 entity-ID raster (id = R + 256·G; 0 = unclaimed or sea) as base64. `<key>` is the year, for example `1453`; BCE years are written as `bc500`.
- `site/rel/`, `site/cul/`: majority faith or culture per pixel (index into `religions.json` / `cultures.json` items). `site/dev/`: urbanisation and development, 0–255. Identical images are stored once; `site/data/eras.json` maps each era to its file.

## n/a register

Where a faith or culture is unknown, too mixed or too disputed to name one group, or the land was uninhabited, the layers use the value `na` ("n/a (unknown or uncertain)") instead of guessing. `NA-REGISTER.csv` lists every such area and territory by era, plus border-map oddities found while compiling it. In `religion_rules.py` and `culture_rules.py`, rules with `gap=True` only repaint pixels that would otherwise keep the world default (animism / hunter-gatherers), and `s8_religion.py` writes a log of every n/a area it paints.

## Development score in ovmain.json

The third value per territory is a development score from 0 to 100, relative to its era; the fourth is GDP per person in 2011 dollars. Both are built by `devindex.py`. From 1815 the score is income per person: each pixel takes the GDP per capita of its modern country from the Maddison Project Database 2020 (Bolt and van Zanden, CC BY 4.0; `maddison2020.csv`, from Our World in Data), and the values are combined over the realm, weighted by population. Before 1815 it is urbanisation, the population-weighted mean of the development layer. Either way 0 marks the 5th and 100 the 95th percentile of that era's territories.

## Not covered by this license

The trade-route, battles, natural-disasters, wonders, roads and railways layers, and the atlas application itself, are © 2026 The Wheeler Atlas, LLC. All rights reserved.

## Corrections

Spotted an error? Open an issue, or write to hello@thewheeleratlas.com.
