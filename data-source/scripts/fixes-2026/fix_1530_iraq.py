"""1530 map (23 Oct 2026): Iraq, Azerbaijan and western Iran were still Safavid in 1530. Usage: python3 fix_1530_iraq.py <site folder>
FIX-125: Shah Ismail took Baghdad in 1508; the Ottomans took it, with Mosul, only in Suleiman's campaign of
1534-35 (Basra followed in 1546). The 1530 map showed all of Iraq as Ottoman. This moves the Ottoman-held land
inside the outline below (Mosul and the Tigris-Euphrates lowlands down to the Gulf; Diyarbakir, Mardin and Urfa,
Ottoman since 1515-17, stay Ottoman) to the Safavid Empire. The source map also had the Ottomans in Azerbaijan,
on the Caspian and in the Zagros of western Iran, which they held only after 1534 (Tabriz briefly) or 1590; that
Ottoman land east of 43.5 deg E (Van, Tabriz, Shirvan) goes to the Safavids too (Van fell to the Ottomans in 1548;
Shirvan was a Safavid vassal, annexed in 1538). Borders, areas and labels are re-traced with the
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
ott, saf = by['Ottoman Empire'], by['Safavid Empire']
# the east side runs well into Iran: only Ottoman land is taken, so it stops at the Safavid border
IRAQ = [[40.6, 34.4], [42.3, 36.9], [43.6, 37.2], [45.2, 37.3], [47.5, 35.9], [48.5, 34.5], [49.0, 33.0], [49.5, 31.4],
        [49.5, 29.8], [47.8, 28.9], [46.0, 29.0], [44.0, 30.2], [42.2, 31.3], [40.8, 32.6]]
EAST = [[43.5, 37.0], [43.5, 44.5], [52.0, 44.5], [52.0, 31.5], [48.5, 31.5]]
m = (T.geo_mask(IRAQ) | T.geo_mask(EAST)) & (ids == ott)
assert m.sum() > 1000
ids[m] = saf
for i in (ott, saf):
    e = js['ents'][i - 1]; a, b, l = T.stats(ids, i)
    e['a'] = a; e['b'] = b; e['l'] = l
js['borders'] = T.borders(ids, LAND)
old = [n for n in js['notes'] if n.startswith('The Ottomans conquered the Mamluk Sultanate in 1517')]
new = 'The Ottomans conquered the Mamluk Sultanate in 1517; Egypt, Syria, the Hejaz and the Mamluk claim to Barqa (Cyrenaica) were Ottoman. Iraq, Azerbaijan and western Iran were still Safavid: the Ottomans took Baghdad and Mosul only in 1534–35, Basra in 1546 and Van in 1548, and held Tabriz only briefly before 1590.'
if old: js['notes'][js['notes'].index(old[0])] = new
else: js['notes'].insert(0, new)
js['_png'] = T.write_ids(ids)
assert (T.read_ids(js) == ids).all()
open(p, 'w', encoding='utf-8').write(json.dumps(js, ensure_ascii=False, separators=(',', ':')))
print(f"FIX-125 1530: {int(m.sum())} pixels of Iraq, Azerbaijan and western Iran Ottoman -> Safavid; Safavid {js['ents'][saf - 1]['a']:,} km2, Ottoman {js['ents'][ott - 1]['a']:,} km2")
