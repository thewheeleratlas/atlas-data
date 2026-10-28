"""Realm QC pass 9 (28 Oct 2026): borders redrawn where a map showed the wrong state over a large area.
Usage: python3 fix_qc9.py <site folder> [one year]

FIX-225 300 BCE: after Ipsus (301 BCE) the Kingdom of Antigonus was divided. Western and central Anatolia go to
        Lysimachus (west of 33.6 E, or north of 38 N west of 35.5 E), Coele-Syria and Phoenicia (south of 33.3 N) to
        Ptolemy, and Cilicia and northern Syria to Seleucus; its few Aegean pieces west of 26 E join their neighbours.
        Leftover slivers of the Empire of Alexander (300 BCE) and of the Kingdom of Lysimachus (250 BCE, after his death
        in 281) join their neighbours.
FIX-226 1800: the patchwork of small imperial states labelled "Swabia" is the Holy Roman Empire, as on the 1700-1783
        maps (the empire lasted until 1806).
FIX-227 1815: the Maratha Confederacy had grown over Rajputana, the Punjab, Sindh, Bahawalpur, part of Nepal and the
        Nizam's lands. Each of those pixels goes back to the state that held it on the 1800 map, under its 1815 name
        (the Sikh Empire for the Sikh misls, the British East India Company for the Northern Circars and Bundelkhand).
FIX-228 1914-1975: the Panama Canal Zone (1903-1979), a strip about ten miles wide along the canal, is drawn as
        United States territory (line approximate).

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
def A(fix, old, y0, y1, mask=None):
    OPS.append((fix, 'absorb', y0, y1, old, dict(mask=mask)))

def box(la0, la1, lo0, lo1):
    return (LAT >= la0) & (LAT <= la1) & (LON >= lo0) & (LON <= lo1)

# FIX-225
LYS = (LON >= 26) & (((LON < 33.6) & (LAT >= 36.2)) | ((LON < 35.5) & (LAT >= 38.0)))
S('FIX-225', 'Kingdom of Antigonus', 'Kingdom of Lysimachus', -300, -300, LYS)
S('FIX-225', 'Kingdom of Antigonus', 'Ptolemaic Kingdom', -300, -300, (LON >= 26) & (LAT < 33.3))
S('FIX-225', 'Kingdom of Antigonus', 'Seleucid Kingdom', -300, -300, LON >= 26)
A('FIX-225', 'Kingdom of Antigonus', -300, -300)
A('FIX-225', 'Empire of Alexander', -300, -300)
A('FIX-225', 'Kingdom of Lysimachus', -250, -250)
# FIX-226
R('FIX-226', 'Swabia', 'Holy Roman Empire', 1800, 1800, realm='Holy Roman Empire')
# FIX-227: masks from the 1800 map
_js = J(f"{SITE}/eras/{F[1800]}.json"); _ids = T.read_ids(_js)
def owned1800(*names):
    return np.isin(_ids, [i + 1 for i, e in enumerate(_js['ents']) if e.get('a') and e['n'] in names])
for old1800, new, realm in (('Rajputs', 'Rajput states', 'Rajput states'), ('Sikhs', 'Sikh Empire', 'Sikh Empire'),
                            ('Durrani Empire', 'Durrani Empire', 'Durrani Empire'), ("Nizam's Dominions", 'Hyderabad State', 'Hyderabad State'),
                            ('Sindh', 'Sindh', 'Sindh'), ('Nepal', 'Nepal', 'Nepal'), ('Bahawalpur', 'Bahawalpur', 'Bahawalpur'),
                            ('Circars', 'British East India Company', 'United Kingdom of Great Britain and Ireland'),
                            ('Bundelkhand', 'British East India Company', 'United Kingdom of Great Britain and Ireland'),
                            ('Mysore', 'Mysore (Indian princely state)', 'Mysore (Indian princely state)')):
    S('FIX-227', 'Maratha Confederacy', new, 1815, 1815, owned1800(old1800), realm=realm, k=0)
A('FIX-227', 'Maratha Confederacy', 1815, 1815, owned1800('Kazakh Khanate (three juzes)'))
del _ids
# FIX-228
def canal_strip():
    (la0, lo0), (la1, lo1) = (9.36, -79.93), (8.93, -79.54)
    vx, vy = lo1 - lo0, la1 - la0
    t = np.clip(((LON - lo0) * vx + (LAT - la0) * vy) / (vx * vx + vy * vy), 0, 1)
    return np.hypot(LON - (lo0 + t * vx), LAT - (la0 + t * vy)) < 0.075
S('FIX-228', 'Panama', 'Panama Canal Zone', 1914, 1975, canal_strip(), realm='United States', k=0)

NOTE = {
    'FIX-225': 'After the battle of Ipsus (301 BCE) the Kingdom of Antigonus was divided among Lysimachus, Seleucus and Ptolemy (lines approximate).',
    'FIX-226': 'The small imperial states between the larger German states are the Holy Roman Empire, which lasted until 1806.',
    'FIX-227': 'The Maratha Confederacy is cut back to its own lands; Rajputana, the Punjab, Sindh and the other states around it are drawn as they were.',
    'FIX-228': 'The Panama Canal Zone (1903-1979) is drawn as United States territory (line approximate).',
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
    r = fix_era(y, LAND)
    if r: print(y, r, flush=True)
for ix in EMETA['eras']:
    js = J(f"{SITE}/eras/{ix['f']}.json")
    ix['c'] = len(js['notes'])
    ix['n'] = sum(1 for e in js['ents'] if e.get('a') and e['k'] == 0)
    ix['m'] = sum(1 for e in js['ents'] if e.get('a') and e['k'] == 1)
open(f'{SITE}/data/eras.json', 'w', encoding='utf-8').write(json.dumps(EMETA, ensure_ascii=True, separators=(',', ':')))
