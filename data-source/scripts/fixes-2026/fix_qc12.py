"""Realm QC pass 12 (28 Oct 2026): the realm review list of 28 October, items still open on the maps.
Usage: python3 fix_qc12.py <site folder> [one year]

FIX-235 Names of the time: the Union of South Africa (1914, formed 1910); French Somaliland (1900-1914, the colony
        that became Djibouti in 1977); Dahomey (1960, renamed Benin in 1975, filed under Benin); Ruanda-Urundi
        (1920-1960, the Belgian mandate over Rwanda and Burundi until 1962); Burundi as part of German East Africa
        (1900); Sweden in the union of Sweden-Norway (1900, dissolved 1905); one Buyid Emirate (1000, where
        "Buwayhid Emirates" was a second name for it).
FIX-236 1900: the Tukular Caliphate, conquered by France in 1890-1893, joins the neighbouring French territory.
FIX-237 Rhodes, an independent Greek republic, was drawn as part of the Phrygians (200 and 100 BCE). On the 1400 map
        Lesbos (the Genoese Gattilusi, from 1355) and Chios (the Genoese Maona, from 1346) are Genoese; they were drawn
        as Ottoman and as the Beylik of Aydin.
FIX-238 1210: the Second Bulgarian Empire was drawn over Epirus and Albania. Epirus (south of 40.9 N, west of 21 E)
        goes to the Despotate of Epirus and central Albania to the Principality of Arbanon; Bulgaria keeps Ohrid and
        western Macedonia (lines approximate). Pieces of southern Italy that pass 11 had given to Epirus (the old map
        showed them as Byzantine, though Byzantium lost Italy in 1071) join their Italian neighbours.
(The Hoover Dam item in the list is not a fix: those pixels are water on the atlas's base raster.)

Borders, areas and labels are re-traced with ../derive-2026/era_tools.py.
Afterwards: python3 scripts/build_realm_index.py, overlays/ovsecond_build.py and scripts/build_content_pages.py."""
import collections, json, os, sys
import numpy as np
from scipy import ndimage
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'derive-2026'))
import era_tools as T

SITE = sys.argv[1]
J = lambda p: json.load(open(p, encoding='utf-8'))
ORDER = ['n', 'r', 'k', 'p', 'a', 'b', 'l', 'w', 'a3', 'x', 'c']
EMETA = J(f'{SITE}/data/eras.json')
F = {e['y']: e['f'] for e in EMETA['eras']}
G = EMETA['realms']
SEEN = {}
for f in F.values():
    for r in J(f'{SITE}/eras/{f}.json')['realms']:
        SEEN.setdefault(r['n'], r['g'])
LAT = T.LATR[:, None] * np.ones((1, T.EW))
LON = ((np.arange(T.EW) + 0.5) / T.EW * 360 - 180)[None, :] * np.ones((T.EH, 1))
ALL = np.ones((T.EH, T.EW), bool)


COLOUR = {'Rhodes': '#4f8fb0', 'Principality of Arbanon': '#9a5a5a', 'Despotate of Epirus': '#7f9a5a'}


def gid(name, like=None):
    for i, g in enumerate(G):
        if g['n'] == name: return i
    if name in SEEN: return SEEN[name]
    c = COLOUR.get(name) or (G[like]['c'] if like is not None else '#948a70')
    G.append({'k': name.lower(), 'c': c, 't': 1, 'n': name}); SEEN[name] = len(G) - 1; return SEEN[name]


def realm_of(js, name, like=None):
    for i, r in enumerate(js['realms']):
        if r['n'] == name: return i
    js['realms'].append({'g': gid(name, like), 'n': name}); return len(js['realms']) - 1


OPS = []
def R(fix, old, new, y0, y1, realm=None, k=None):
    OPS.append((fix, 'rename', y0, y1, old, dict(new=new, realm=realm, k=k)))
def S(fix, old, new, y0, y1, mask, realm=None, k=None):
    OPS.append((fix, 'split', y0, y1, old, dict(new=new, mask=mask, realm=realm, k=k)))
def A(fix, old, y0, y1, mask=None):
    OPS.append((fix, 'absorb', y0, y1, old, dict(mask=mask)))

def box(la0, la1, lo0, lo1):
    return (LAT >= la0) & (LAT <= la1) & (LON >= lo0) & (LON <= lo1)

def F_(fix, new, y0, y1, mask):
    """fill: unclaimed land pixels (id 0) inside mask go to the existing realm-piece named new"""
    OPS.append((fix, 'fill', y0, y1, new, dict(new=new, mask=mask)))

# FIX-235
R('FIX-235', 'South Africa', 'Union of South Africa', 1914, 1914)
R('FIX-235', 'Djibouti', 'French Somaliland', 1900, 1914)
R('FIX-235', 'Benin', 'Dahomey', 1960, 1960, realm='Benin')
R('FIX-235', 'Burundi', 'Ruanda-Urundi', 1920, 1960, realm='Belgium')
R('FIX-235', 'Rwanda', 'Ruanda-Urundi', 1920, 1960, realm='Belgium')
R('FIX-235', 'Burundi', 'Burundi', 1900, 1900, realm='German Empire')
R('FIX-235', 'Sweden', 'Sweden', 1900, 1900, realm='Sweden\u2013Norway')
R('FIX-235', 'Buwayhid Emirates', 'Buyid Emirate', 1000, 1000, realm='Buyid Emirate')
# FIX-236
A('FIX-236', 'Tukular Caliphate', 1900, 1900)
# FIX-237
S('FIX-237', 'Phrygians', 'Rhodes', -200, -100, box(35.85, 36.5, 27.65, 28.3), realm='Rhodes', k=0)
S('FIX-237', 'Ottoman Empire', 'Lesbos (Gattilusi)', 1400, 1400, box(38.95, 39.45, 25.8, 26.65), realm='Genoa')
S('FIX-237', 'Beylik of Aydin', 'Chios (Genoese Maona)', 1400, 1400, box(38.1, 38.65, 25.8, 26.2), realm='Genoa')
# FIX-238
S('FIX-238', 'Second Bulgarian Empire', 'Despotate of Epirus', 1210, 1210, (LAT < 40.9) & (LAT > 38.5) & (LON > 19.0) & (LON < 21.0))
S('FIX-238', 'Second Bulgarian Empire', 'Principality of Arbanon', 1210, 1210, box(40.9, 41.9, 19.3, 20.25), realm='Principality of Arbanon')
A('FIX-238', 'Despotate of Epirus', 1210, 1210, LON < 19.0)   # pieces of southern Italy, Byzantine on the old map, join their neighbours

NOTE = {
    'FIX-235': 'Names are the ones in use on this map\u2019s date.',
    'FIX-236': 'The Tukular Caliphate was conquered by France in 1890\u20131893.',
    'FIX-237': 'Rhodes was an independent Greek republic until Rome took it in the 1st century BCE.' ,
    'FIX-238': 'After the Fourth Crusade, Epirus and central Albania were ruled by the Despotate of Epirus and the Principality of Arbanon (lines approximate).',
}
NEED_IDS = {'split', 'absorb', 'clear', 'paint', 'fill'}


def ents_named(js, name):
    return [i + 1 for i, e in enumerate(js['ents']) if e.get('a') and e['n'] == name]


def fix_era(y, LAND):
    key = F[y]; p = f'{SITE}/eras/{key}.json'; js = J(p)
    log = collections.Counter(); notes = []
    todo = [op for op in OPS if op[2] <= y <= op[3] and (op[1] == 'paint' or ents_named(js, op[4]))]
    if not todo:
        return None
    ids = orig = None
    ov = J(f'{SITE}/data/ovmain.json'); rows = ov['eras'][key]
    if any(op[1] in NEED_IDS for op in todo):
        same, bad = T.check_roundtrip(js, LAND)
        assert same and all(x[1] == x[2] and x[3] == x[4] for x in bad), f'tracing does not reproduce the {key} map; stop'
        ids = T.read_ids(js); orig = ids.copy()
    for fix, kind, y0, y1, old, o in OPS:
        if not (y0 <= y <= y1): continue
        if kind == 'paint':
            hit = [i for i, e in enumerate(js['ents'], 1) if e.get('a') and e['k'] == 1 and e['n'] != o['new']]
        else:
            hit = ents_named(js, old)
        if not hit: continue
        if kind == 'rename':
            for i in hit:
                e = js['ents'][i - 1]; rn = js['realms'][e['r']]['n'] if e['r'] >= 0 else None
                like = js['realms'][e['r']]['g'] if e['r'] >= 0 else None
                target = o['realm'] or (o['new'] if rn == old or rn is None else None)
                if target: e['r'] = realm_of(js, target, like)
                for e2 in js['ents']:                      # the rest of a realm of that name follows it
                    if e2 is not e and e2['r'] >= 0 and rn == old and js['realms'][e2['r']]['n'] == old and target:
                        e2['r'] = e['r']
                e['n'] = o['new']; e['x'] = 1
                if o['k'] is not None: e['k'] = o['k']
                log[fix] += 1
        elif kind in ('split', 'paint'):
            o = dict(o, realm=o.get('realm'), k=o.get('k'))
            m = np.isin(ids, hit) & o['mask']
            if not m.any(): continue
            src = js['ents'][hit[0] - 1]
            like = js['realms'][src['r']]['g'] if src['r'] >= 0 else None
            ex = [i for i in ents_named(js, o['new']) if i not in hit]
            if ex:
                ni = ex[0]
            else:
                js['ents'].append({'n': o['new'], 'r': realm_of(js, o['realm'] or o['new'], like), 'k': src['k'] if o['k'] is None else o['k'],
                                   'p': 1, 'a': 1, 'x': 1})
                ni = len(js['ents'])
                while len(rows) < ni: rows.append(list(rows[int(np.bincount(orig[m]).argmax()) - 1]))
            ids[m] = ni; log[fix + ' px'] += int(m.sum())
        elif kind == 'fill':
            m = (ids == 0) & LAND & o['mask']
            if not m.any(): continue
            ids[m] = hit[0]; log[fix + ' filled px'] += int(m.sum())
            notes.append(NOTE[fix] if not (fix == 'FIX-237' and y >= 1400) else 'Lesbos and Chios are Genoese: the Gattilusi lords of Lesbos (from 1355) and the Maona of Chios (from 1346).'); continue
        elif kind == 'clear':
            m = np.isin(ids, hit) & (ALL if o['mask'] is None else o['mask'])
            ids[m] = 0; log[fix + ' cleared px'] += int(m.sum())
        elif kind == 'absorb':
            m = np.isin(ids, hit) & (ALL if o['mask'] is None else o['mask'])
            lab, n = ndimage.label(m)
            for c in range(1, n + 1):
                cm = lab == c
                ring = ndimage.binary_dilation(cm) & ~cm & (ids > 0) & ~np.isin(ids, hit)
                if ring.any():
                    ids[cm] = np.bincount(ids[ring]).argmax()
                else:
                    near = ndimage.binary_dilation(cm, iterations=12) & ~cm & (ids > 0) & ~np.isin(ids, hit)
                    if near.any(): ids[cm] = np.bincount(ids[near]).argmax()
                log[fix + ' joined'] += 1
        notes.append(NOTE[fix] if not (fix == 'FIX-237' and y >= 1400) else 'Lesbos and Chios are Genoese: the Gattilusi lords of Lesbos (from 1355) and the Maona of Chios (from 1346).')
        if ids is not None:                                 # names later ops look up must reflect pixels now
            for i in hit:
                if not (ids == i).any(): js['ents'][i - 1]['a'] = 0
    if ids is not None:
        changed = ids != orig
        touched = set(np.unique(orig[changed]).tolist()) | set(np.unique(ids[changed]).tolist()); touched.discard(0)
        for i in touched:
            e = js['ents'][i - 1]; a, b, l = T.stats(ids, i)
            e['a'] = a
            for k, v in (('b', b), ('l', l)):
                if v is None: e.pop(k, None)
                else: e[k] = v
        js['borders'] = T.borders(ids, LAND)
        js['_png'] = T.write_ids(ids)
        assert (T.read_ids(js) == ids).all()
    open(f'{SITE}/data/ovmain.json', 'w', encoding='utf-8').write(json.dumps(ov, ensure_ascii=True, separators=(',', ':')))
    used = sorted({e['r'] for e in js['ents'] if e['r'] >= 0})
    remap = {r: k for k, r in enumerate(used)}
    js['realms'] = [js['realms'][r] for r in used]
    for e in js['ents']:
        if e['r'] >= 0: e['r'] = remap[e['r']]
    js['ents'] = [{k: e[k] for k in ORDER if k in e} for e in js['ents']]
    js['notes'] += [n for n in dict.fromkeys(notes) if n not in js['notes']]
    open(p, 'w', encoding='utf-8').write(json.dumps(js, ensure_ascii=False, separators=(',', ':')))
    return dict(log)


LAND = T.land_mask(f'{SITE}/eras', list(F.values()))
for y in sorted(y for y in F if len(sys.argv) < 3 or y == int(sys.argv[2])):
    r = fix_era(y, LAND)
    if r: print(y, r, flush=True)
for ix in EMETA['eras']:
    js = J(f"{SITE}/eras/{ix['f']}.json")
    ix['c'] = len(js['notes'])
    ix['n'] = sum(1 for e in js['ents'] if e.get('a') and e['k'] == 0)
    ix['m'] = sum(1 for e in js['ents'] if e.get('a') and e['k'] == 1)
open(f'{SITE}/data/eras.json', 'w', encoding='utf-8').write(json.dumps(EMETA, ensure_ascii=True, separators=(',', ':')))
