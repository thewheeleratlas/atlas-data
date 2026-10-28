# hb-gpl: notice of origin and modification

The snapshot geometry, lineages and crosswalk in this folder are a **modified version** of
**historical-basemaps** by André Ourednik and contributors (https://github.com/aourednik/historical-basemaps),
commit `da7a4b735ecef70aebdc9c73e409d8a2500d50f3`, licensed under the GNU GPL v3.0 (see `LICENSE`).

Modifications (2026): rasterized to the atlas grid, corrected and extended by `era_edits.py`,
then split in October 2026 into one record and one mask per polity per era. The complete corresponding source
(the modified data, plus the build and edit scripts) is this repository: https://github.com/thewheeleratlas/atlas-data.

These records are kept separate from the rest of the atlas data, so this border layer can be replaced
by another source without changing anything else.
