# hb-gpl: notice of origin and modification

The snapshot geometry, lineages and crosswalk in this folder are a **modified version** of
**historical-basemaps** by André Ourednik and contributors (https://github.com/aourednik/historical-basemaps),
commit `da7a4b735ecef70aebdc9c73e409d8a2500d50f3`, licensed under the GNU GPL v3.0 (see `LICENSE`).

Modifications (2026): rasterized to the atlas grid, corrected and extended by the atlas build's `era_edits.py`,
then split in M2 (Oct 2026) into one record and one mask per polity per era. The complete corresponding source
(upstream files + build and edit scripts) is published in the public borders repository: https://github.com/thewheeleratlas/atlas-data.

This dataset is deliberately separate from the owned `hha-core` data so it can be replaced by our own
borders (`hha-borders`) or another source without touching anything else.
