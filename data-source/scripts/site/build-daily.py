#!/usr/bin/env python3
"""The daily "Find it on the map" puzzle list (site/data/daily.json), 28 October 2026.

One realm a day, the same for everyone: the realms that have a page on the site (so a player can read about the
answer), at the map where each is largest, from 1000 BCE on, states only. The order is shuffled once with a fixed seed
and then fixed: day 1 is START, and the list repeats after its last day. Each entry has the realm's name as the map
writes it, the map year and era file, and the centre of its largest territory (for the distance and direction hints).

Rerun only to add realms at the end (the existing order keeps today's and past puzzles where they are): python3 scripts/build-daily.py
"""
import json
import random
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
sys.path.insert(0, str(ROOT / "data-source/scripts/derive-2026"))
import era_tools as T  # noqa: E402

START = "2026-10-28"
SEED = 1453
GROUPS = re.compile(r"\b(chiefdoms|tribes|peoples|principalities|kingdoms|sultanates|city-states|cultures|emirates|khanates|"
                    r"states|settlements|territories|colonies|clans|groups|confederations|nomads)\b", re.I)


def main():
    pages = json.loads((SITE / "data/realm-pages.json").read_text())["p"]
    eras = {e["y"]: e for e in json.loads((SITE / "data/eras.json").read_text())["eras"]}
    by_slug = {}
    for name, slug in pages.items():
        by_slug.setdefault(slug, []).append(name)
    picks = []
    cache = {}
    for slug, names in sorted(by_slug.items()):
        best = None
        for e in eras.values():
            if e["y"] < -1000:
                continue
            js = cache.get(e["f"])
            if js is None:
                js = json.loads((SITE / "eras" / f"{e['f']}.json").read_text()); js.pop("_png", None)
                cache.clear(); cache[e["f"]] = js
            for ri, R in enumerate(js["realms"]):
                if R["n"] not in names or "(" in R["n"] or (GROUPS.search(R["n"]) and not R["n"].startswith("United States")):
                    continue
                ents = [x for x in js["ents"] if x.get("r") == ri and x.get("a")]
                if not ents or any(x.get("k") for x in ents):
                    continue
                area = sum(x["a"] for x in ents)
                if area >= 250000 and (best is None or area > best[0]):
                    big = max(ents, key=lambda x: x["a"])
                    # the hints point at the largest territory: skip empires whose largest piece is a colony or
                    # another named land (the United Kingdom in 1930 is largest in Canada)
                    if not big.get("l") or big["n"] != R["n"]:
                        continue
                    lon = big["l"]["x"] / 8192 * 360 - 180
                    lat = float(T.LATR[min(int(big["l"]["y"] / 2), T.EH - 1)])
                    best = (area, {"n": R["n"], "y": e["y"], "f": e["f"], "lat": round(lat, 2), "lon": round(lon, 2), "slug": slug})
        if best:
            picks.append((best[0], best[1]))
        print(slug, "ok" if best else "-", flush=True)
    # two well-known realms (the 120 largest) for every lesser-known one, so most days are findable
    picks.sort(key=lambda t: -t[0])
    famous, rest = [p for _, p in picks[:120]], [p for _, p in picks[120:]]
    rnd = random.Random(SEED); rnd.shuffle(famous); rnd.shuffle(rest)
    picks = []
    while famous or rest:
        picks += famous[:2] + rest[:1]; famous, rest = famous[2:], rest[1:]
    out = SITE / "data/daily.json"
    if out.exists():   # keep the order already published; new realms go at the end
        old = json.loads(out.read_text())["list"]
        seen = {(x["n"], x["y"]) for x in old}
        picks = old + [p for p in picks if (p["n"], p["y"]) not in seen]
    out.write_text(json.dumps({"start": START, "list": picks}, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(len(picks), "puzzles")


if __name__ == "__main__":
    main()
