"""Per-territory second faith and second culture for every era -> appended to data/ovmain.json rows (28 October 2026).

Uses the same population estimate as ovmain_build.py: true pixel area x (development + 2)^1.5, with ice caps
discounted. The second group is the largest after the main one already stored in ovmain.json (hand corrections
included), leaving out "n/a" (unknown or unpeopled). It is kept only when it holds at least MIN_SHARE of the
territory's estimated people, so a few border pixels of a neighbour's faith do not show as a second faith.

Rows become [main faith, main culture, development score, GDP per person, second faith, second culture], the last
two 1-based indexes into religions.json / cultures.json items, or 0 for none.

Usage (from data-source/scripts/overlays/):
    HHA_ATLAS=<site>/ python3 ovsecond_build.py <site>/ <terrain4096.npy>
terrain4096.npy is the 4096 x 2111 RGB terrain picture ovmain_build.py uses to find ice caps.
<site> is the website's site folder: the layer aliases of derived maps are read from its atlas.js (ASSET_ALIAS)."""
import json, os, sys
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'derive-2026'))
import era_tools as T
from popw import row_lat

SITE, TER = sys.argv[1], sys.argv[2]
MIN_SHARE = 0.10
import re
# derived maps reuse another map's layers (ASSET_ALIAS in atlas.js)
ALIAS = json.loads(re.search(r'const ASSET_ALIAS = (\{.*?\});', open(SITE + 'atlas.js', encoding='utf-8').read()).group(1))
def px(p): return np.array(Image.open(SITE + ALIAS.get(p, p)).convert('RGB')).astype(np.int64)
RI = json.load(open(SITE + 'data/religions.json'))['items']; CI = json.load(open(SITE + 'data/cultures.json'))['items']
H = 2111
lat_e = np.array([row_lat(y) for y in range(H + 1)]); A = np.abs(np.sin(lat_e[:-1]) - np.sin(lat_e[1:]))[:, None]
Tr = np.load(TER).astype(float); br = Tr.mean(axis=2); sat = Tr.max(axis=2) - Tr.min(axis=2)
HAB = np.where((br > 205) & (sat < 28), 0.03, 1.0)
ovp = SITE + 'data/ovmain.json'; ov = json.load(open(ovp))
shown = [0, 0]; total = 0
for e in json.load(open(SITE + 'data/eras.json'))['eras']:
    f = e['f']; js = json.load(open(SITE + f'eras/{f}.json')); n = len(js['ents']) + 1
    ids = T.read_ids(js).astype(np.int64)
    rel = px(f'rel/{f}.png')[..., 0]; c = px(f'cul/{f}.png'); cul = c[..., 0] | (c[..., 1] << 8)
    dev = px(f'dev/{f}.png')[..., 0].astype(float)
    w = (A * HAB * (dev + 2) ** 1.5).ravel(); flat = ids.ravel()
    rows = ov['eras'][f]
    assert len(rows) == n - 1, (f, len(rows), n - 1)
    seconds = []
    for col, (arr, items) in enumerate([(rel, RI), (cul, CI)]):
        k = len(items) + 1
        M = np.bincount(flat * k + arr.ravel(), weights=w, minlength=n * k).reshape(n, k); M[:, 0] = 0
        na = next((i + 1 for i, x in enumerate(items) if x['id'] == 'na'), None)
        if na: M[:, na] = 0
        tot = M.sum(axis=1)
        sec = np.zeros(n, int)
        for i in range(1, n):
            main = rows[i - 1][col]
            m = M[i].copy()
            if main: m[main] = 0
            b = int(m.argmax())
            if tot[i] > 0 and m[b] >= MIN_SHARE * tot[i]: sec[i] = b
        seconds.append(sec)
    for i, r in enumerate(rows):
        del r[4:]
        r += [int(seconds[0][i + 1]), int(seconds[1][i + 1])]
        total += 1; shown[0] += r[4] > 0; shown[1] += r[5] > 0
ov['about'] = ('Per territory and era: [main faith, main culture (1-based indexes into religions.json / cultures.json items), '
               'development score 0-100 relative to its era, GDP per person in 2011 dollars (0 before 1815), second faith, '
               'second culture (indexes as before, 0 when no other group holds 10% of the people)]. Population-weighted '
               'estimates plus hand corrections.')
open(ovp, 'w').write(json.dumps(ov, separators=(',', ':')))
print(f'{total} territories: second faith on {shown[0]}, second culture on {shown[1]}')
