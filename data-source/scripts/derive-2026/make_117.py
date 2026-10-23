"""Derive the 117 CE map, the Roman Empire at its greatest extent under Trajan, from the 100 CE map.
Usage: python3 make_117.py <site folder>     (writes <site>/eras/117.json and updates <site>/data/*.json)

Changes from 100 CE:
  - Dacia (conquered 101-106) becomes the province of Dacia;
  - the Nabataean Kingdom (annexed 106) becomes the province of Arabia Petraea;
  - Armenia (annexed 114) becomes the province of Armenia;
  - Mesopotamia and Assyria (116): the Parthian lands between the Euphrates, the Tigris and the Zagros
    foothills, down to the head of the Persian Gulf, become the province of Mesopotamia.
Hadrian gave up Armenia, Mesopotamia and Assyria in 117-118, so they appear on this map only.
Everything else, including the faith, culture and development layers, is the 100 CE map's. Borders,
areas and labels are re-traced with the s6_eras.py code (era_tools.py), so the new map is drawn like
the others. Run from data-source/scripts/derive-2026/."""
import json, sys, os, copy
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, era_tools as T

SITE = sys.argv[1]
D = lambda *p: os.path.join(SITE, *p)
J = lambda p: json.load(open(p, encoding='utf-8'))
meta = J(D('data', 'eras.json'))
assert not any(e['y'] == 117 for e in meta['eras']), '117 is already in eras.json'
LAND = T.land_mask(D('eras'), [e['f'] for e in meta['eras']])
src = J(D('eras', '100.json'))
same, bad = T.check_roundtrip(src, LAND)
assert same and not bad, 'tracing does not reproduce the 100 CE map; stop'

js = copy.deepcopy(src); ids = T.read_ids(src).copy(); ents = js['ents']
byname = {e['n']: i + 1 for i, e in enumerate(ents)}
rome = byname['Roman Empire']; R_ROME = ents[rome - 1]['r']
def to_rome(old, new):
    i = byname.pop(old); e = ents[i - 1]; e['n'] = new; e['r'] = R_ROME; e['k'] = 0; e['x'] = 1; byname[new] = i
to_rome('Dacia', 'Dacia')
to_rome('Nabatean Kingdom', 'Arabia Petraea')
to_rome('Armenia', 'Armenia')
# Mesopotamia: carved out of the Parthian Empire
MESO = [[37.6, 38.0], [40.0, 38.2], [42.5, 37.7], [44.4, 37.3], [45.1, 35.8], [45.8, 34.4], [46.8, 32.9], [47.9, 31.4],
        [48.7, 30.1], [47.6, 29.6], [46.0, 30.2], [44.0, 31.0], [42.0, 32.5], [40.0, 34.3], [38.4, 35.6], [37.6, 36.6]]
parth = byname['Parthian Empire']
m = T.geo_mask(MESO) & (ids == parth)
assert m.sum() > 1000
ents.append({'n': 'Mesopotamia', 'r': R_ROME, 'k': 0, 'p': 1, 'a': 0, 'x': 1})
meso = len(ents); ids[m] = meso
# drop realms nobody uses any more and renumber
used = sorted({e['r'] for e in ents if e['r'] >= 0})
remap = {r: k for k, r in enumerate(used)}
js['realms'] = [js['realms'][r] for r in used]
for e in ents:
    if e['r'] >= 0: e['r'] = remap[e['r']]
# re-measure every changed entity, then re-trace the borders
for i in (rome, parth, meso, byname['Dacia'], byname['Arabia Petraea'], byname['Armenia']):
    e = ents[i - 1]; a, b, l = T.stats(ids, i)
    e['a'] = a
    for k, v in (('b', b), ('l', l)):
        if v is None: e.pop(k, None)
        else: e[k] = v
# key order as s6_eras.py writes it
order = ['n', 'r', 'k', 'p', 'a', 'b', 'l', 'w', 'a3', 'x', 'c']
js['ents'] = [{k: e[k] for k in order if k in e} for e in ents]
js['y'] = 117; js['d'] = 100
js['borders'] = T.borders(ids, LAND)
js['notes'] = ['Built from the 100 CE map, adjusted to 117.',
               'Trajan annexed Dacia (106), the Nabataean Kingdom as Arabia Petraea (106) and Armenia (114), and took Mesopotamia and Assyria from Parthia (116), reaching the Persian Gulf.',
               'Hadrian gave up Armenia, Mesopotamia and Assyria in 117–118; Dacia and Arabia stayed Roman.'] + src['notes']
js['_png'] = T.write_ids(ids)
keys = ['y', 'src', 'realms', 'ents', 'borders', 'notes', 'd', '_png']
js = {k: js[k] for k in keys if k in js}
assert (T.read_ids(js) == ids).all()
open(D('eras', '117.json'), 'w', encoding='utf-8').write(json.dumps(js, ensure_ascii=False, separators=(',', ':')))

# era index: after 100 CE
i100 = next(e for e in meta['eras'] if e['y'] == 100)
ix = {'y': 117, 'f': '117', 'p': i100['p'], 'c': len(js['notes']), 'd': 100, 't': 'Rome at its greatest extent',
      'n': sum(1 for e in js['ents'] if e.get('a') and e['k'] == 0), 'm': sum(1 for e in js['ents'] if e.get('a') and e['k'] == 1)}
meta['eras'].insert(meta['eras'].index(i100) + 1, ix)
open(D('data', 'eras.json'), 'w', encoding='utf-8').write(json.dumps(meta, ensure_ascii=True, separators=(',', ':')))
# layers painted per era: reuse the 100 CE summaries; the new Mesopotamia territory takes Parthia's row
for name in ('religions', 'cultures', 'develop'):
    p = D('data', f'{name}.json')
    if not os.path.exists(p): continue
    d = J(p); d['eras']['117'] = copy.deepcopy(d['eras']['100'])
    open(p, 'w', encoding='utf-8').write(json.dumps(d, ensure_ascii=True, separators=(',', ':')))
p = D('data', 'ovmain.json')
if os.path.exists(p):
    d = J(p); rows = copy.deepcopy(d['eras']['100']); rows.append(copy.deepcopy(rows[parth - 1]))
    d['eras']['117'] = rows
    open(p, 'w', encoding='utf-8').write(json.dumps(d, ensure_ascii=True, separators=(',', ':')))
p = D('data', 'flags.json')
if os.path.exists(p):
    d = J(p)
    for r in js['realms']:
        nm = r['n']
        if nm in d['r'] and '100' in d['r'][nm]: d['r'][nm]['117'] = d['r'][nm]['100']
    open(p, 'w', encoding='utf-8').write(json.dumps(d, ensure_ascii=False, separators=(',', ':')))
rome_e = js['ents'][rome - 1]; me = js['ents'][meso - 1]
print(f"117 CE written: Roman Empire territory {rome_e['a']:,} km2; Mesopotamia {me['a']:,} km2; Parthia {js['ents'][parth - 1]['a']:,} km2; "
      f"{len(js['borders'])} border lines; {ix['n']} states, {ix['m']} peoples")
