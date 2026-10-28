"""Realm QC pass 7 (28 Oct 2026): peoples drawn in the wrong place, the Americas before 1800.
Usage: python3 fix_qc7.py <site folder> [one year]

FIX-210 The South-West: the "Mogollon" territory lay in northern Mexico (Durango, Chihuahua): it is the Aridoamerican
        peoples, and the Mogollon culture (600-1400; south-west New Mexico and south-east Arizona, 31-34.5 N,
        110.5-107 W) and the Hohokam culture (300-1400; the Gila and Salt valleys, 32-34 N, 113-110.5 W) are drawn
        where they lived, over the peoples' territories there; on the 1450 and 1500 maps the Mesa Verde "Pueblos" is the
        Ute and Southern Paiute (Mesa Verde was left about 1285), and a "Hopi" over all of Arizona and "Pomo" over all of
        southern California (1500) are the South-Western and California peoples.
FIX-211 The North-East (1500): the "Iroquois" territory over New England is the New England Algonquian peoples, with
        the Iroquois (Haudenosaunee) west of 74 W.
FIX-212 The North-West coast (1530-1750): the Eyak lived on the Copper River delta; the rest of their territory is the
        Tlingit, and the Southern Tutchone and Tagish inland (north of 60.5 N, east of 143 W).
FIX-213 South America and the Caribbean: Norte Chico (3000-2000 BCE) is the Supe coast (north of 11.8 S, west of
        76.8 W), the rest Andean Archaic peoples; Valdivia (3000-2000 BCE) is the Ecuadorian coast (west of 79.6 W), the
        highlands Andean Archaic peoples; Chorrera and the regional cultures of Ecuador end at about 78.5 W, with the
        upper Amazon peoples to the east; the Kalinago on Trinidad are the Arawakan peoples of Trinidad (1200-1500).

The lines are approximate. Borders, areas and labels are re-traced with ../derive-2026/era_tools.py.
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


def gid(name, like=None):
    for i, g in enumerate(G):
        if g['n'] == name: return i
    if name in SEEN: return SEEN[name]
    c = G[like]['c'] if like is not None else '#948a70'
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
def P(fix, new, y0, y1, mask):                              # paint: the peoples' land inside mask becomes `new`
    OPS.append((fix, 'paint', y0, y1, None, dict(new=new, mask=mask, k=1)))

def box(la0, la1, lo0, lo1):
    return (LAT >= la0) & (LAT <= la1) & (LON >= lo0) & (LON <= lo1)

# FIX-210
R('FIX-210', 'Mogollon', 'Aridoamerican peoples', 600, 1400)
P('FIX-210', 'Mogollon culture', 600, 1400, box(31, 34.5, -110.5, -107))
P('FIX-210', 'Hohokam culture', 300, 1400, box(32, 34, -113, -110.5))
S('FIX-210', 'Pueblos', 'Ute and Southern Paiute', 1450, 1500, LAT > 36.8)
R('FIX-210', 'Hopi', 'South-Western peoples (O\'odham, Yuman, Hopi)', 1500, 1500)
S('FIX-210', 'Pomo', 'California peoples', 1500, 1500, LAT < 38.3)
# FIX-211
S('FIX-211', 'Iroquois', 'New England Algonquian peoples', 1500, 1500, LON >= -74)
R('FIX-211', 'Iroquois', 'Iroquois (Haudenosaunee)', 1500, 1500)
# FIX-212
S('FIX-212', 'Eyaq', 'Southern Tutchone and Tagish', 1530, 1750, (LAT > 60.5) & (LON > -143))
S('FIX-212', 'Eyaq', 'Tlingit', 1530, 1750, ~((LAT >= 59.5) & (LON <= -143.5)))
# FIX-213
S('FIX-213', 'Norte Chico', 'Andean Archaic peoples', -3000, -2000, ~((LAT > -11.8) & (LON < -76.8)))
S('FIX-213', 'Valdivia', 'Andean Archaic peoples', -3000, -2000, LON > -79.6)
for old in ('Chorrera', 'Regional cultures of Ecuador'):
    S('FIX-213', old, 'Upper Amazon peoples', -1500, 700, LON > -78.5)
for old in ('Kalinago', 'Kalinago (Island Carib)'):
    R('FIX-213', old, 'Arawakan peoples of Trinidad', 1200, 1500, realm='Arawakan peoples of Trinidad')

NOTE = {
    'FIX-210': 'South-western peoples are drawn where they lived: the Mogollon and Hohokam in New Mexico and Arizona, not northern Mexico (lines approximate).',
    'FIX-211': 'The Iroquois lived in central New York; New England was the land of Algonquian peoples (line approximate).',
    'FIX-212': 'The Eyak lived on the Copper River delta; the coast to the south-east was Tlingit (lines approximate).',
    'FIX-213': 'Early South American cultures are drawn where they lived (lines approximate).',
}
NEED_IDS = {'split', 'absorb', 'clear', 'paint'}


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
        notes.append(NOTE[fix])
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
    if y > 1800: continue
    r = fix_era(y, LAND)
    if r: print(y, r, flush=True)
for ix in EMETA['eras']:
    js = J(f"{SITE}/eras/{ix['f']}.json")
    ix['c'] = len(js['notes'])
    ix['n'] = sum(1 for e in js['ents'] if e.get('a') and e['k'] == 0)
    ix['m'] = sum(1 for e in js['ents'] if e.get('a') and e['k'] == 1)
open(f'{SITE}/data/eras.json', 'w', encoding='utf-8').write(json.dumps(EMETA, ensure_ascii=True, separators=(',', ':')))
