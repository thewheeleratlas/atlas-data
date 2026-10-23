# The Wheeler Atlas map data

Public corresponding source, under the **GNU General Public License v3.0**, for the historical map data used by **[The Wheeler Atlas](https://thewheeleratlas.com)**.

The license text is [`LICENSE`](LICENSE). Upstream attribution, the Natural Earth and Maddison inputs, and the list of modifications are in [`NOTICE.md`](NOTICE.md). [`MANIFEST.txt`](MANIFEST.txt) lists every other file in this repository with its size in bytes.

## What this is

Historical borders for each year the atlas shows, plus the religion, culture and development layers painted on those borders, plus the scripts and records that build and correct them.

| What | Where | License |
|---|---|---|
| Historical borders, one JSON file per year, including that year's territory raster | `site/eras/` | GPL-3.0, modified from [historical-basemaps](https://github.com/aourednik/historical-basemaps) by André Ourednik and contributors, snapshot `da7a4b735ecef70aebdc9c73e409d8a2500d50f3` |
| Era index and realm registry | `site/data/eras.json` | GPL-3.0 |
| Realm search index: which era maps each realm name appears on, built from `site/eras/` by `data-source/scripts/build_realm_index.py` | `site/data/realm-index.json` | GPL-3.0 |
| Religion, culture and development rasters | `site/rel/`, `site/cul/`, `site/dev/` | GPL-3.0 |
| Layer indexes and the per-territory summaries made from them | `site/data/religions.json`, `cultures.json`, `develop.json`, `ovmain.json` | GPL-3.0 |
| Build scripts, correction scripts, the n/a register, and the 2026 correction records | `data-source/` | GPL-3.0 |
| Income figures used by the development score from 1815 | `data-source/scripts/overlays/maddison2020.csv` | **CC BY 4.0**, Maddison Project Database 2020 (Bolt and van Zanden) via [Our World in Data](https://github.com/owid/owid-datasets). This file stays under CC BY 4.0. |

The border data started from historical-basemaps. It was rasterized onto the atlas grid, snapped to Natural Earth coastlines, and corrected by hand. The 331 pre-launch corrections are part of that GPL work: they are the `notes` arrays inside `site/eras/*.json`.

## How thewheeleratlas.com uses it

[thewheeleratlas.com](https://thewheeleratlas.com) is a static map. For each year it reads `site/data/eras.json`, then `site/eras/<key>.json`. The `_png` field in that file is the 4096 × 2111 entity-id raster (id = R + 256·G; 0 is unclaimed land or sea), stored as base64 so the site can ship one file per year. Religion, culture and development are the PNGs in `site/rel/`, `site/cul/` and `site/dev/`. Names, colours and the per-territory card (main faith, main culture, development score, GDP per person) come from `site/data/religions.json`, `cultures.json`, `develop.json` and `ovmain.json`.

The website keeps its own copies of these files so the map can be served from the site repository. This repository is the corresponding source for those GPL parts. The website source is [thewheeleratlas/website](https://github.com/thewheeleratlas/website).

Six overlay images are identical to a neighbouring year, so they are stored once. The site maps the missing names onto the file that is present:

| Requested file | File used |
|---|---|
| `cul/1453.png` | `cul/1450.png` |
| `rel/1210.png` | `rel/1200.png` |
| `rel/1453.png` | `rel/1450.png` |
| `rel/2010.png` | `rel/2000.png` |
| `dev/bc123000.png` | `dev/bc10000.png` |
| `dev/bc8000.png` | `dev/bc10000.png` |

That leaves 59 religion rasters, 61 culture rasters and 60 development rasters for 62 eras. Every era still has its own file in `site/eras/`.

These files are enough to read and reuse the map data. Rebuilding from upstream needs the extra inputs in the next section.

## What stays in the website repository

The atlas application and its interface, the page text, the logo and shop art, the fonts, the flags, the climate layer, and the trade-route, battles, natural-disasters, wonders, roads and railways layers are published with the website, under their own terms. The application, page text, logo, shop art and those six layers are © 2026 The Wheeler Atlas, LLC. All rights reserved. Climate data is CC BY 4.0. Fonts are SIL OFL 1.1. Modern flags are MIT. Terrain and elevation are derived from public-domain sources. None of that is in this repository.

## How to rebuild

The copies under `site/` are the data the website serves. You do not need to rebuild them to use the atlas data. To regenerate them from upstream:

Python 3.11, with the packages in [`data-source/requirements.txt`](data-source/requirements.txt) (`numpy`, `opencv-python-headless`, `scipy`). `devindex.py`, `popw.py` and `ovmain_build.py` also import Pillow.

From `data-source/scripts/`, with a work directory and an output directory:

```
export HHA_WORKDIR=../workdir
export HHA_SITE=../../site
export HHA_HB=../upstream/historical-basemaps

python3 fetch_natural_earth.py
python3 s1_masks.py
python3 s6_eras.py
```

`fetch_natural_earth.py` downloads the public-domain Natural Earth layers listed in `NOTICE.md`. `s6_eras.py` reads historical-basemaps from `HHA_HB`. Check that repository out at commit `da7a4b735ecef70aebdc9c73e409d8a2500d50f3`. The script applies `era_edits.py` while it writes each year.

Then apply the October 2026 name corrections, and rebuild the search index, from `data-source/scripts/`. They are already present in the files shipped here. `fix_batch4.py` also reads `flags.json` from the data folder, which is the website's flag rules and is not part of this repository:

```
python3 fixes-2026/fix_batch3.py "$HHA_SITE/eras" "$HHA_SITE/data"
python3 fixes-2026/fix_batch4.py "$HHA_SITE/eras" "$HHA_SITE/data"
python3 fixes-2026/fix_batch5.py "$HHA_SITE/eras" "$HHA_SITE/data"
python3 fixes-2026/fix_1530_ottoman.py "$HHA_SITE/eras"
python3 build_realm_index.py
```

`fix_batch5.py` uses `flags.json` when the data folder has one and skips it otherwise.

The overlay scripts use the same `HHA_WORKDIR` and `HHA_SITE`. Run them from `data-source/scripts/overlays/`:

```
python3 s8_religion.py religion
python3 s8_religion.py culture
python3 s10_develop.py
```

Each layer is a list of ordered rules in `religion_rules.py` and `culture_rules.py`: first year, last year, faith or culture, and where. A later rule overrides an earlier one. Where a faith or culture is unknown, too mixed, too disputed, or the land was uninhabited, the rules use `na` instead of guessing. Every such area is listed in [`data-source/NA-REGISTER.csv`](data-source/NA-REGISTER.csv).

`ovmain.json` is built by `ovmain_build.py`. Run it in a directory that contains `terrain4096.npy`, a terrain raster from the atlas basemap used to discount ice. That raster is not part of this GPL tree. Population weights (`popw.py`, `devindex.py`) read the modern country grid, `data/world.json` and `tiles/ids/0_0_0.png`, from the directory set by `HHA_ATLAS` (default `./atlas/`). Those basemap files are derived from public-domain sources and are served with the website. They are not included here. From 1815 the development score uses income per person from `maddison2020.csv` (CC BY 4.0). Before 1815 it uses urbanisation from the development layer.

`python3 data-source/scripts/unpack_eras.py site/eras eras-unpacked` writes each era raster back out as a plain PNG, and writes the JSON without the `_png` field.

Work directories (`workdir/`, `build-output/`, `eras-unpacked/`) are local build output. They are not part of this source tree.

## Data format

- `site/eras/<key>.json`: `{y, src, realms, ents, borders, notes, _png}` for one year. Seven years also carry `d`, the year that map was adjusted from. `<key>` is the year, for example `1453`. BCE years are written as `bc500`.
- `site/rel/` and `site/cul/`: majority faith or culture per pixel, as an index into `religions.json` or `cultures.json`. `site/dev/`: urbanisation and development, 0–255.
- `site/data/ovmain.json`: for each territory and era, main faith, main culture, a development score from 0 to 100 relative to that era, and GDP per person in 2011 dollars (0 before 1815).

## Accuracy

Borders, faiths and cultures are approximate and often disputed, especially before about 1800. The GPL data is offered as an illustration, with no warranty. See the GPL text for the full disclaimer.

## Corrections

Spotted an error in a border, date or label? Open an issue in this repository, or write to hello@thewheeleratlas.com.
