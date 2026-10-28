"""Realm QC pass 11 (28 Oct 2026): Constantinople and the Byzantine world on the 100 BCE, 1210 and 1400 maps.
Usage: python3 fix_qc11.py <site folder> [one year]

FIX-232 100 BCE: the Dacians were drawn south of the Danube over all of Thrace, to Byzantium. South of the Danube
        (43.65 N) that land goes to the Thracians, as on the 200 BCE map.
FIX-233 1210: the whole Byzantine world was one "Byzantine Empire", six years after the Fourth Crusade took
        Constantinople (1204). It is divided among the states of 1210: the Latin Empire (Constantinople, Thrace east
        of the Nestos and the Asian shore of the Dardanelles and the Sea of Marmara), the Kingdom of Thessalonica
        (Macedonia and Thessaly), the Despotate of Epirus, the Principality of Achaea (the Peloponnese), the Duchy of
        Athens (Attica, Boeotia, Euboea), Venice (Crete), the Duchy of the Archipelago (the Cyclades), the Empire of
        Trebizond (the Black Sea coast east of 33.5 E) and the Empire of Nicaea (the rest of western Anatolia, filed
        under the Byzantine Empire, which it restored in 1261).
FIX-234 1400: Constantinople was drawn as Ottoman; it stayed Byzantine until 1453. The Ottoman pixels inside the
        Byzantine outline of the 1450 map go back to the Byzantine Empire. The rest of Greece drawn as Byzantine goes
        to its holders in 1400: the Despotate of the Morea (Byzantine), the Despotate of Epirus (with the Ionian islands),
        the Albanian principalities (north of 40.4 N), the Duchy of Athens,
        the Ottoman Empire (Thessaly, taken in 1393), Venice (Crete), the Duchy of the Archipelago and the
        Knights Hospitaller (Rhodes and the Dodecanese).

All lines are approximate. Borders, areas and labels are re-traced with ../derive-2026/era_tools.py.
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


COLOUR = {'Latin Empire': '#b5473a', 'Kingdom of Thessalonica': '#c98b4a', 'Despotate of Epirus': '#7f9a5a',
          'Principality of Achaea': '#a8647e', 'Duchy of Athens': '#8a7bb5', 'Knights Hospitaller': '#5a8f9a',
          'Albanian principalities': '#9a5a5a'}


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

# Europe and Asia around the Straits: north-west of the Dardanelles, north of the Sea of Marmara, west of the Bosporus
EUR = (LON < 26.0) | ((LON < 29.05) & np.where(LON < 26.18, LAT > 40.0, np.where(LON < 26.7, LAT > 40.03 + (LON - 26.18) * 0.81, LAT > 40.45)))
CRETE, CYCLADES, DODEC = box(34.8, 35.7, 23.4, 26.4), box(36.3, 37.7, 24.2, 26.0), box(35.8, 37.5, 26.75, 28.3)
PELOP = EUR & (LAT < 38.3) & (LON < 23.1)
# FIX-232
S('FIX-232', 'Dacians', 'Thracians', -100, -100, LAT < 43.65, realm='Thracians', k=1)
# FIX-233
BZ = 'Byzantine Empire'
S('FIX-233', BZ, 'Venice', 1210, 1210, CRETE, realm='Venice')
S('FIX-233', BZ, 'Duchy of the Archipelago', 1210, 1210, CYCLADES, realm='Venice')
S('FIX-233', BZ, 'Empire of Trebizond', 1210, 1210, (LON >= 33.5) & (LAT >= 40.4), realm='Empire of Trebizond')
S('FIX-233', BZ, 'Latin Empire', 1210, 1210, (EUR & (LON >= 24.6) & (LAT >= 40.3)) | (~EUR & (LAT >= 39.6) & (LON >= 26.0) & (LON <= 28.6)), realm='Latin Empire')
S('FIX-233', BZ, 'Kingdom of Thessalonica', 1210, 1210, EUR & (LON >= 21.4) & (LON < 24.6) & (LAT >= 38.9), realm='Kingdom of Thessalonica')
S('FIX-233', BZ, 'Despotate of Epirus', 1210, 1210, EUR & ((LON < 21.4) | ((LAT >= 38.35) & (LON < 22.0))), realm='Despotate of Epirus')
S('FIX-233', BZ, 'Principality of Achaea', 1210, 1210, PELOP, realm='Principality of Achaea')
S('FIX-233', BZ, 'Duchy of Athens', 1210, 1210, EUR & (LAT < 38.9), realm='Duchy of Athens')
R('FIX-233', BZ, 'Empire of Nicaea', 1210, 1210, realm=BZ)
# FIX-234: the 1450 outline of the city
_js = J(f"{SITE}/eras/{F[1450]}.json"); _ids = T.read_ids(_js)
CITY = np.isin(_ids, [i + 1 for i, e in enumerate(_js['ents']) if e.get('a') and e['n'] == BZ]) & box(40.8, 41.6, 27.8, 29.3)
assert CITY.sum() > 3
del _ids
S('FIX-234', 'Ottoman Empire', BZ, 1400, 1400, CITY)
S('FIX-234', BZ, 'Albanian principalities', 1400, 1400, EUR & (LON < 21.6) & (LAT >= 40.4), realm='Albanian principalities')
S('FIX-234', BZ, 'Despotate of Epirus', 1400, 1400, EUR & (LON < 21.0), realm='Despotate of Epirus')
S('FIX-234', BZ, 'Despotate of the Morea', 1400, 1400, PELOP, realm=BZ)
S('FIX-234', BZ, 'Venice', 1400, 1400, CRETE, realm='Venice')
S('FIX-234', BZ, 'Duchy of the Archipelago', 1400, 1400, CYCLADES, realm='Venice')
S('FIX-234', BZ, 'Knights Hospitaller', 1400, 1400, DODEC, realm='Knights Hospitaller')
S('FIX-234', BZ, 'Despotate of Epirus', 1400, 1400, EUR & ((LON < 21.6) | ((LAT >= 38.3) & (LAT < 38.9) & (LON < 22.0))), realm='Despotate of Epirus')
S('FIX-234', BZ, 'Ottoman Empire', 1400, 1400, EUR & (LAT >= 38.9) & ~box(40.8, 41.6, 27.8, 29.3))
S('FIX-234', BZ, 'Duchy of Athens', 1400, 1400, EUR & (LAT < 38.9) & (LAT >= 37.6) & (LON >= 22.8) & (LON < 24.7), realm='Duchy of Athens')
S('FIX-234', BZ, 'Ottoman Empire', 1400, 1400, EUR & (LAT < 38.9) & (LAT >= 37.6) & (LON < 24.7))   # Phocis and Locris, taken in 1394

NOTE = {
    'FIX-232': 'South of the Danube, Thrace is the land of the Thracians; the Dacians lived north of the river (lines approximate).',
    'FIX-233': 'After the Fourth Crusade took Constantinople (1204), the Byzantine world was divided: the Latin Empire, the Kingdom of Thessalonica, the Principality of Achaea and the Duchy of Athens held by crusaders, Crete and the Cyclades by Venice, and the Greek successor states of Nicaea, Epirus and Trebizond (lines approximate).',
    'FIX-234': 'Constantinople is Byzantine until 1453. Greece in 1400 is divided among the Despotate of the Morea, the Despotate of Epirus, the Duchy of Athens, Venice, the Knights Hospitaller and the Ottoman Empire (lines approximate).',
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
            notes.append(NOTE[fix]); continue
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
    r = fix_era(y, LAND)
    if r: print(y, r, flush=True)
for ix in EMETA['eras']:
    js = J(f"{SITE}/eras/{ix['f']}.json")
    ix['c'] = len(js['notes'])
    ix['n'] = sum(1 for e in js['ents'] if e.get('a') and e['k'] == 0)
    ix['m'] = sum(1 for e in js['ents'] if e.get('a') and e['k'] == 1)
open(f'{SITE}/data/eras.json', 'w', encoding='utf-8').write(json.dumps(EMETA, ensure_ascii=True, separators=(',', ':')))
