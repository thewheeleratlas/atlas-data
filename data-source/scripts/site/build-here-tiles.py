#!/usr/bin/env python3
"""Tiles for "Who ruled here" (28 October 2026): what held each spot on every era map, cut into small regional files.

A tap on the map downloads one tile (site/here/<tx>_<ty>.json) instead of all 70 era maps. Each tile covers TILE x TILE
pixels of the 4096-wide era rasters, sampled every STEP pixels (about 20 km at the equator). Every sample point has a
history (what held it on each era map, oldest first); points with the same history share it.

  {"v": 1, "step": 2, "n": 64,
   "p": [[realm name, territory name, colour, 1 if a people], ...],   palette of this tile
   "h": [[palette index per era, -1 for none], ...],                   unique histories
   "g": "<base64 of n*n little-endian uint16 history indexes, row by row>"}

Tiles where every era is empty (open sea) are not written. The era order is site/data/eras.json.
Run after any map-data change: python3 scripts/build-here-tiles.py
"""
import base64
import hashlib
import json
import shutil
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
sys.path.insert(0, str(ROOT / "data-source/scripts/derive-2026"))
import era_tools as T  # noqa: E402

TILE, STEP = 128, 2
N = TILE // STEP


def main():
    meta = json.loads((SITE / "data/eras.json").read_text())
    groups = meta["realms"]
    eras = meta["eras"]
    nty, ntx = -(-T.EH // TILE), T.EW // TILE
    # per era: sampled id grid and the per-entity palette entry
    layers, pals = [], []
    for e in eras:
        js = json.loads((SITE / "eras" / f"{e['f']}.json").read_text())
        ids = T.read_ids(js)
        pad = np.zeros((nty * TILE, ntx * TILE), ids.dtype)
        pad[:ids.shape[0], :ids.shape[1]] = ids
        layers.append(pad[STEP // 2::STEP, STEP // 2::STEP])
        pal = [None]
        for ent in js["ents"]:
            if ent.get("r", -1) < 0 or not ent.get("a"):
                pal.append(None); continue
            R = js["realms"][ent["r"]]
            pal.append((R["n"], ent["n"], groups[R["g"]]["c"] or "#8a7a5a", 1 if ent.get("k") else 0))
        pals.append(pal)
        print("read", e["f"], flush=True)
    out = SITE / "here"
    if out.exists():
        shutil.rmtree(out)
    out.mkdir()
    stack = np.stack(layers, axis=-1)            # rows, cols, eras
    written, total = 0, 0
    digest = hashlib.sha1()
    for ty in range(nty):
        for tx in range(ntx):
            block = stack[ty * N:(ty + 1) * N, tx * N:(tx + 1) * N]
            if not block.any():
                continue
            palette, pidx, hist, hidx = [], {}, [], {}
            grid = np.zeros((N, N), np.uint16)
            for yy in range(N):
                for xx in range(N):
                    key = tuple(int(v) for v in block[yy, xx])
                    h = hidx.get(key)
                    if h is None:
                        row = []
                        for ei, eid in enumerate(key):
                            entry = pals[ei][eid] if eid < len(pals[ei]) else None
                            if entry is None:
                                row.append(-1); continue
                            pi = pidx.get(entry)
                            if pi is None:
                                pi = pidx[entry] = len(palette); palette.append(list(entry))
                            row.append(pi)
                        h = hidx[key] = len(hist); hist.append(row)
                    grid[yy, xx] = h
            doc = {"v": 1, "step": STEP, "n": N, "p": palette, "h": hist,
                   "g": base64.b64encode(grid.astype("<u2").tobytes()).decode()}
            data = json.dumps(doc, ensure_ascii=False, separators=(",", ":"))
            (out / f"{tx}_{ty}.json").write_text(data, encoding="utf-8")
            digest.update(data.encode())
            written += 1; total += len(data)
    (out / "index.json").write_text(json.dumps({"v": 1, "ver": digest.hexdigest()[:12], "tile": TILE, "step": STEP, "w": T.EW, "h": T.EH,
                                                "eras": [[e["y"], e["f"]] for e in eras]}, separators=(",", ":")))
    print(f"{written} tiles, {total / 1e6:.1f} MB")


if __name__ == "__main__":
    main()
