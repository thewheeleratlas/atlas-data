"""The 1960 map: the West Bank and Gaza (27 Oct 2026). Usage: python3 fix_1960_palestine.py <site folder>

FIX-164 The 1960 map drew the West Bank and the Gaza Strip as part of Israel. From the 1949 armistice to the war of
        June 1967 the West Bank, with East Jerusalem, was held by Jordan (annexed in 1950) and the Gaza Strip was under
        Egyptian administration. They are territories of Jordan and of Egypt (then part of the United Arab Republic),
        outlined as the 2026 map's Palestine. Israel occupied both in 1967 (the 1975 and later maps).

Borders, areas and labels are re-traced with ../derive-2026/era_tools.py after checking that it reproduces the map; the
new territories get their main faith and culture from the layers and their development from the territory they leave.
Afterwards: python3 scripts/build_realm_index.py."""
import copy, json, os, sys
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'derive-2026'))
import era_tools as T

SITE = sys.argv[1]
J = lambda p: json.load(open(p, encoding='utf-8'))
ORDER = ['n', 'r', 'k', 'p', 'a', 'b', 'l', 'w', 'a3', 'x', 'c']
EMETA = J(f'{SITE}/data/eras.json')
F = {e['y']: e['f'] for e in EMETA['eras']}
LAND = T.land_mask(f'{SITE}/eras', list(F.values()))
key = F[1960]; p = f'{SITE}/eras/{key}.json'; js = J(p)
same, bad = T.check_roundtrip(js, LAND)
assert same and all(x[1] == x[2] and x[3] == x[4] for x in bad), 'tracing does not reproduce the 1960 map; stop'
ids = T.read_ids(js); orig = ids.copy()
j26 = J(f'{SITE}/eras/{F[2026]}.json'); i26 = T.read_ids(j26)
pal = np.isin(i26, [i + 1 for i, e in enumerate(j26['ents']) if e['n'] == 'Palestine'])
lat = T.LATR[:, None]; lon = (np.arange(T.EW)[None, :] + 0.5) / T.EW * 360 - 180
gaza = pal & (lon < 34.65) & (lat < 31.7)
ent = lambda n: next(i + 1 for i, e in enumerate(js['ents']) if e['n'] == n and e.get('a'))
realm = lambda n: next(i for i, r in enumerate(js['realms']) if r['n'] == n)
isr = ent('Israel'); new = []
for name, rn, m in (('West Bank', 'Jordan', pal & ~gaza), ('Gaza Strip (Egyptian-administered)', 'Egypt', gaza)):
    m = m & (ids == isr); assert m.sum() > 5, name
    js['ents'].append({'n': name, 'r': realm(rn), 'k': 0, 'p': 1, 'a': 0, 'x': 1}); i = len(js['ents'])
    ids[m] = i; new.append(i); print(name, int(m.sum()), 'px')
changed = ids != orig
for i in set(np.unique(orig[changed]).tolist()) | set(np.unique(ids[changed]).tolist()):
    e = js['ents'][i - 1]; a, b, l = T.stats(ids, i); e['a'] = a
    for k, v in (('b', b), ('l', l)):
        if v is None: e.pop(k, None)
        else: e[k] = v
js['borders'] = T.borders(ids, LAND)
js['_png'] = T.write_ids(ids)
try:
    import base64, oxipng
    js['_png'] = base64.b64encode(oxipng.optimize_from_memory(base64.b64decode(js['_png']), level=4)).decode('ascii')
except ImportError:
    pass
assert (T.read_ids(js) == ids).all()
js['ents'] = [{k: e[k] for k in ORDER if k in e} for e in js['ents']]
note = 'The West Bank (with East Jerusalem) was held by Jordan and the Gaza Strip was under Egyptian administration from 1949 to 1967.'
if note not in js['notes']: js['notes'].append(note)
open(p, 'w', encoding='utf-8').write(json.dumps(js, ensure_ascii=False, separators=(',', ':')))
# card rows: main faith and culture from the layers, development from Israel's row
pd = f'{SITE}/data/ovmain.json'; d = J(pd); rows = d['eras'][key]
def layer(dr, wide):
    a = np.asarray(Image.open(f'{SITE}/{dr}/{key}.png').convert('RGB')).astype(np.int64)
    return a[..., 0] + (a[..., 1] << 8) if wide else a[..., 0]
rel, cul = layer('rel', False), layer('cul', True)
for i in new:
    while len(rows) < i: rows.append(copy.deepcopy(rows[isr - 1]))
    m = ids == i
    for col, L in ((0, rel), (1, cul)):
        v = L[m]; v = v[v > 0]
        if len(v): rows[i - 1][col] = int(np.bincount(v).argmax())
open(pd, 'w', encoding='utf-8').write(json.dumps(d, ensure_ascii=True, separators=(',', ':')))
for ix in EMETA['eras']:
    if ix['f'] == key:
        ix['c'] = len(js['notes']); ix['n'] = sum(1 for e in js['ents'] if e.get('a') and e['k'] == 0)
open(f'{SITE}/data/eras.json', 'w', encoding='utf-8').write(json.dumps(EMETA, ensure_ascii=True, separators=(',', ':')))
