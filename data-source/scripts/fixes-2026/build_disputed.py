"""Builds cand/data/disputed.json: hatched disputed areas (Natural Earth 10m admin-0 disputed areas, public domain).
'from' = first map year the area is hatched (compared with the era snapshot year)."""
import json, sys
SRC = sys.argv[1] if len(sys.argv) > 1 else '../ne_disp/disp10.geojson'
OUT = sys.argv[2] if len(sys.argv) > 2 else 'cand/data/disputed.json'
G = [
 ('kashmir', 'Kashmir', 1947, ['Jammu and Kashmir', 'Aksai Chin', 'Shaksam Valley', 'Gilgit-Baltistan', 'Azad Kashmir', 'Siachen Glacier'],
  'Disputed since 1947. India, Pakistan and China each administer part of the former princely state of Jammu and Kashmir, and India and Pakistan each claim the parts held by the others. The map shows the areas each country administers.'),
 ('taiwan', 'Taiwan', 1949, ['Taiwan'],
  'Governed by the Republic of China (Taiwan) since 1949 and claimed by the People’s Republic of China. Most countries do not formally recognize Taiwan as a state but keep unofficial relations with it. The map shows Taiwan as it is governed.'),
 ('palestine', 'West Bank and Gaza', 1967, ['West Bank', 'Gaza', 'East Jerusalem', 'No Man\'s Land (Jerusalem)', 'No Man\'s Land (Fort Latrun)', 'Mount Scopus'],
  'Palestinian territories (the West Bank, including East Jerusalem, and Gaza), under Israeli occupation since 1967. Most UN members recognize the State of Palestine; Israel and some others do not. Their final status and borders are disputed.'),
 ('golan', 'Golan Heights', 1967, ['Golan Heights'],
  'Syrian territory under Israeli control since 1967. Israel annexed it in 1981; most countries and the UN Security Council do not recognize the annexation.'),
 ('wsahara', 'Western Sahara', 1975, ['W. Sahara'],
  'Disputed since Spain withdrew in 1975–76. Morocco administers most of it and claims all of it; the Polisario Front’s Sahrawi Arab Democratic Republic controls the area east of the Moroccan sand wall and also claims all of it. A UN-supervised referendum has never been held.'),
 ('crimea', 'Crimea', 2014, ['Crimea'],
  'Internationally recognized as part of Ukraine. Russia annexed it in 2014 and administers it; the UN General Assembly declared the annexation invalid (Resolution 68/262). The map shows the area as administered.'),
]
def dp(pts, tol):
    if len(pts) < 4: return pts
    a, b = pts[0], pts[-1]; dmax, idx = 0, 0
    ax, ay = a; bx, by = b; L = ((bx-ax)**2 + (by-ay)**2) ** .5 or 1e-12
    for i in range(1, len(pts)-1):
        x, y = pts[i]; d = abs((bx-ax)*(ay-y) - (ax-x)*(by-ay)) / L
        if d > dmax: dmax, idx = d, i
    if dmax <= tol: return [a, b]
    return dp(pts[:idx+1], tol)[:-1] + dp(pts[idx:], tol)
feats = json.load(open(SRC))['features']
out = []
for key, name, frm, brks, note in G:
    rings = []
    for f in feats:
        if f['properties'].get('BRK_NAME', '').replace('﻿', '') not in brks: continue
        g = f['geometry']; polys = g['coordinates'] if g['type'] == 'MultiPolygon' else [g['coordinates']]
        for poly in polys:
            r = poly[0]
            pts = [tuple(p[:2]) for p in r]; h = len(pts) // 2
            s = dp(pts[:h+1], 0.015)[:-1] + dp(pts[h:], 0.015)   # closed ring: simplify the two halves
            if len(s) >= 4: rings.append([[round(x, 3), round(y, 3)] for x, y in s])
    found = {f['properties'].get('BRK_NAME', '').replace('﻿', '') for f in feats} & set(brks)
    assert found == set(brks), (key, set(brks) - found)
    out.append({'k': key, 'n': name, 'from': frm, 'note': note, 'rings': rings})
    print(key, len(rings), sum(len(r) for r in rings))
json.dump({'source': 'Natural Earth 1:10m admin-0 disputed areas (public domain)', 'regions': out}, open(OUT, 'w'), separators=(',', ':'))
import os; print(OUT, os.path.getsize(OUT))
