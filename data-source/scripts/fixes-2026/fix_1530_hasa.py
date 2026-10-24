"""1530 map (24 Oct 2026): al-Hasa was not yet Ottoman in 1530. Usage: python3 fix_1530_hasa.py <site folder>
FIX-126: the Ottomans reached al-Hasa (eastern Arabia, with Qatif) only in 1550, when it became the Eyalet of Lahsa.
In 1530 the coast and oases from Kuwait Bay to the base of Qatar were held by the Jabrid sultans, weakened by the
Portuguese capture of Bahrain in 1521. The 1530 map showed this land as Ottoman. This moves the Ottoman-held
land inside the outline below to a new Jabrid Sultanate territory. Borders, areas and labels are re-traced with the
s6_eras.py code in ../derive-2026/era_tools.py, after checking that it reproduces the unchanged map exactly.
Afterwards rebuild the search index (build_realm_index.py)."""
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'derive-2026'))
import era_tools as T

SITE = sys.argv[1]
J = lambda p: json.load(open(p, encoding='utf-8'))
meta = J(f'{SITE}/data/eras.json')
p = f'{SITE}/eras/1530.json'; js = J(p)
LAND = T.land_mask(f'{SITE}/eras', [e['f'] for e in meta['eras']])
same, bad = T.check_roundtrip(js, LAND)
assert same and not bad, 'tracing does not reproduce the 1530 map; stop'
ids = T.read_ids(js)
by = {e['n']: i + 1 for i, e in enumerate(js['ents'])}
ott = by['Ottoman Empire']
HASA = [[47.4, 29.6], [48.6, 29.6], [50.2, 27.0], [51.9, 24.2], [51.0, 22.8], [48.5, 22.8], [47.4, 25.0]]
m = T.geo_mask(HASA) & (ids == ott)
assert m.sum() > 200, int(m.sum())
# a new realm (registry entry added) and its territory
key = 'jabrid sultanate'
g = next((i for i, r in enumerate(meta['realms']) if r['k'] == key), None)
if g is None:
    g = len(meta['realms']); meta['realms'].append({'k': key, 'c': '#9a6b3c', 't': 0, 'n': 'Jabrid Sultanate'})
js['realms'].append({'g': g, 'n': 'Jabrid Sultanate'}); r = len(js['realms']) - 1
js['ents'].append({'n': 'Jabrid Sultanate', 'r': r, 'k': 0, 'p': 1, 'a': 0, 'x': 1}); jab = len(js['ents'])
ids[m] = jab
for i in (ott, jab):
    e = js['ents'][i - 1]; a, b, l = T.stats(ids, i)
    e['a'] = a
    for k, v in (('b', b), ('l', l)):
        if v is None: e.pop(k, None)
        else: e[k] = v
order = ['n', 'r', 'k', 'p', 'a', 'b', 'l', 'w', 'a3', 'x', 'c']
js['ents'] = [{k: e[k] for k in order if k in e} for e in js['ents']]
js['borders'] = T.borders(ids, LAND)
js['notes'].append('Al-Hasa and Qatif were held by the Jabrid sultans; the Ottomans took al-Hasa only in 1550.')
js['_png'] = T.write_ids(ids)
assert (T.read_ids(js) == ids).all()
open(p, 'w', encoding='utf-8').write(json.dumps(js, ensure_ascii=False, separators=(',', ':')))
ix = next(e for e in meta['eras'] if e['f'] == '1530')
ix['c'] = len(js['notes']); ix['n'] = sum(1 for e in js['ents'] if e.get('a') and e['k'] == 0)
open(f'{SITE}/data/eras.json', 'w', encoding='utf-8').write(json.dumps(meta, ensure_ascii=True, separators=(',', ':')))
# the new territory takes the Ottoman row in the per-territory summaries
p2 = f'{SITE}/data/ovmain.json'
if os.path.exists(p2):
    import copy
    d = J(p2); rows = d['eras']['1530']
    while len(rows) < len(js['ents']): rows.append(copy.deepcopy(rows[ott - 1]))
    open(p2, 'w', encoding='utf-8').write(json.dumps(d, ensure_ascii=True, separators=(',', ':')))
print(f"FIX-126 1530: {int(m.sum())} pixels of al-Hasa Ottoman -> Jabrid Sultanate ({js['ents'][jab - 1]['a']:,} km2); Ottoman {js['ents'][ott - 1]['a']:,} km2")
