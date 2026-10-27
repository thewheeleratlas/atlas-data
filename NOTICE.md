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
- October 2026 name-only corrections (for example Kamakura shogunate, Qing Empire, Afsharid Iran, and colonial names in 1945) were applied by `data-source/scripts/fixes-2026/fix_batch3.py` and `fix_batch4.py`, and on 22 October 2026 a further batch of misspelt, garbled and out-of-date realm names (for example Satavahana Empire, Mamluk Sultanate, Malay sultanates, Kyivan Rus') by `fix_batch5.py`. Those scripts did not change border shapes. `fix_1530_ottoman.py` (22 October 2026) moved the 1530 map's leftover Mamluk territory (Barqa) and an Aq Qoyunlu sliver into the Ottoman Empire, changing which realm they belong to but not their shapes. On 23 October 2026 a new 117 CE map was derived from the 100 CE map by `data-source/scripts/derive-2026/make_117.py` (Trajan's Dacia, Arabia Petraea, Armenia and Mesopotamia), and `fixes-2026/fix_1530_iraq.py` returned Iraq, Azerbaijan and western Iran to the Safavid Empire on the 1530 map. On 24 October `fixes-2026/fix_1530_hasa.py` gave al-Hasa (Ottoman only from 1550) to the Jabrid Sultanate on the 1530 map. `fix_slivers.py` (25 October) gave tiny stray pieces of realms (up to 3 map pixels) to the territory around them on every map, removed leftover Kalmar Union and Denmark-Norway fragments (1492, 1500, 1530) and the not-yet-founded crusader states (1066), corrected Hanover and Mecklenburg-Strelitz (1783, 1800), and split Holstein and the Mecklenburg duchies out of a territory labelled Lübeck (1715, 1750). `fix_hre_split.py` (25 October) gave Bavaria, Saxony, Württemberg, the Electoral Palatinate and the other larger German states their own territories inside the Holy Roman Empire on the 1650–1750 maps, using outlines from the 1715, 1783, 1800 and 1815 maps, and corrected Silesia and Bavaria on the 1783 map and the realms of Hanover and Mecklenburg-Strelitz on the 1800 map. `fix_hre_1600.py` (25 October) did the same for the 1600 map, with the Habsburg lands, Brandenburg, Pomerania and the Upper Palatinate cut to their 1600 extent. `derive-2026/make_bc550.py` derived a new 550 BCE map from the 500 BCE map (Media, Lydia, the Neo-Babylonian Empire and Saite Egypt before Cyrus), and `make_bc525.py` a 525 BCE map from it (the Persian Empire of Cyrus and Cambyses). On 24 October `derive-2026/make_bc250.py` derived a 250 BCE map from the 300 BCE map (Rome in Italy and most of Sicily, the Hellenistic kingdoms after Ipsus and Corupedium, Ashoka's Mauryan Empire, and Qin before the unification of China). On 26 October `fixes-2026/fix_overlay_overseas.py` corrected the culture and religion layers where they had carried a modern country's people and faith onto its overseas parts or onto islands before anyone lived there: French Guiana, Guadeloupe, Martinique, Réunion, Mayotte and Bonaire before European settlement; the Azores, Madeira, Galápagos, Svalbard, Canaries, Easter Island, Falklands and Bermuda, now n/a until settled; the Andaman religion; Caribbean small-island religion after colonisation; the Karelian Isthmus 1300–1938; and a coastal hunter-gatherer and animism rim on small island states from 1700. It also recomputed the area totals in `site/data/cultures.json` and `religions.json` and the affected main values in `site/data/ovmain.json`. `fixes-2026/fix_overlay_judgement.py` (26 October) made judgement calls on the culture layer: Early Slavs instead of Bulgarians, Serbs, Croats and Slovenes on the 600 map (and in North Macedonia on the 700 and 800 maps); Mande, then Fula, for the kingdom of Kaabu in eastern Guinea-Bissau; Chibchan peoples on Panama's Caribbean coast from 500 BCE and a Spanish-colonial isthmus from 1530; Coahuiltecan, Apache, Comanche and then American peoples in south-central Texas instead of the Caddo; German in Danzig, Elbing and the Vistula delta from 1400 to 1938; and "Serbian" renamed "Serbian and Montenegrin". It recomputed the areas in `site/data/cultures.json` and the affected main values in `site/data/ovmain.json`. `fixes-2026/fix_realm_qc.py` (26 October) corrected realms shown outside their time: the Guanche Canary Islands are Castilian, then Spanish, from 1500; Hong Kong joins the Qing Empire on the 1650-1800 maps; names that did not fit their date are renamed (European hunter-gatherers and Neolithic farmers before the Bronze Age, the Northern European Iron Age from 550 BCE, the Susiana and the Halaf, Ubaid and Gawra cultures instead of Elam and the Hurrian kingdoms in 5000-4000 BCE, Saint-Domingue, the Malay sultanates and the Somali sultanates); and Brittany, Burgundy, Rajasthan and The Gambia are spelled correctly. Judgement calls in the same script name the Wolof and Fula kingdoms instead of "Senegal" (1530-1815) and the Bay of Honduras settlements instead of "Belize" (1650-1750), leave the Turks and Caicos Islands unclaimed on the 1530-1650 maps, and name the Nordic Bronze Age on the 1500 BCE map. `fixes-2026/fix_realm_qc2.py` (26 October) shows Korea as Goryeo (1279, 1300) and Joseon (1400) instead of part of the Yuan, Java and Bali as Majapahit and the Sunda Kingdom instead of the Malay sultanates (1450-1530), names the Danish realm of 1000 Denmark (with Norway), and removes a one-pixel leftover of Alexander's empire on the 250 BCE map.

The 331 pre-launch corrections are part of these GPL modifications. They are the `notes` arrays in `site/eras/*.json`: 331 notes across 57 of the 62 era files. Each note is a short string recorded with that year's map. They are not a separate layer and they are not withheld from this release.

A further file-by-file account of the build, including the n/a register, is in [`data-source/NOTICE.md`](data-source/NOTICE.md) and [`data-source/README.md`](data-source/README.md). The per-polity records in `data-source/hb-gpl/` have their own notice in [`data-source/hb-gpl/NOTICE.md`](data-source/hb-gpl/NOTICE.md).
