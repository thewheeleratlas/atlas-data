"""Realm QC pass 10 (28 Oct 2026): Istanbul and the Straits on the 1914 and 1920 maps.
Usage: python3 fix_qc10.py <site folder> [one year]

FIX-229 1914: Bulgaria was drawn over Eastern Thrace, Istanbul and the Gallipoli peninsula. The Treaty of
        Constantinople (September 1913) returned Eastern Thrace with Edirne to the Ottoman Empire, on a line that is
        today's Turkish border in Europe, so every Bulgarian pixel inside modern Turkey (the 2026 map) goes back to the
        Ottoman Empire. Bulgaria keeps Western Thrace, which it held from 1913 to 1919.
FIX-230 1920: Istanbul, the Straits and Lesbos were in no realm. The map follows the Treaty of Sevres (August 1920):
        Thrace west of the Chatalja lines (28.55 E), with the Gallipoli peninsula, goes to Greece, as does Lesbos (Greek
        since 1912); Istanbul and the Asian shore of the Straits stay with the Ottoman Sultanate, under Allied
        occupation (lines approximate).
FIX-231 1900-1920: Aegean islands left in no realm. 1900: Lemnos, Rhodes and the other Ottoman islands go to the
        Ottoman Empire. 1914: Crete (united with Greece in December 1913), Lesbos, Chios, Samos, Lemnos and the
        other islands taken in 1912 go to Greece; Rhodes and the Dodecanese, occupied in 1912, go to Italy.
        1920: Lemnos and Imbros go to Greece, Karpathos to Italy.

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

def F_(fix, new, y0, y1, mask):
    """fill: unclaimed land pixels (id 0) inside mask go to the existing realm-piece named new"""
    OPS.append((fix, 'fill', y0, y1, new, dict(new=new, mask=mask)))

# FIX-229: modern Turkey, from the 2026 map
_js = J(f"{SITE}/eras/{F[2026]}.json"); _ids = T.read_ids(_js)
TR = np.isin(_ids, [i + 1 for i, e in enumerate(_js['ents']) if e.get('a') and e['n'] in ('Turkey', 'Republic of Turkey')])
assert TR.sum() > 1000
del _ids
S('FIX-229', 'Bulgaria', 'Ottoman Empire', 1914, 1914, TR)
# FIX-230
STRAITS = box(39.4, 41.7, 26.0, 30.5)
# the European shore: north-west of the Dardanelles (40.03 N 26.18 E to 40.45 N 26.70 E), north of the Sea of Marmara
EUROPE = np.where(LON < 26.18, LAT > 40.0, np.where(LON < 26.7, LAT > 40.03 + (LON - 26.18) * 0.81, LAT > 40.45))
F_('FIX-230', 'Greece', 1920, 1920, STRAITS & EUROPE & (LON < 28.55))
F_('FIX-230', 'Ottoman Sultanate', 1920, 1920, STRAITS)
F_('FIX-230', 'Greece', 1920, 1920, box(38.9, 39.45, 25.7, 26.7))
# FIX-231
DODEC = box(35.3, 37.0, 26.75, 28.3)
F_('FIX-231', 'Ottoman Empire', 1900, 1900, box(35.3, 40.5, 24.9, 28.3))
F_('FIX-231', 'Kingdom of Italy', 1914, 1914, DODEC)   # the 1914 map names the Italian mainland piece so
F_('FIX-231', 'Italy', 1920, 1920, DODEC)
F_('FIX-231', 'Greece', 1914, 1914, box(34.8, 40.5, 22.5, 26.95))
F_('FIX-231', 'Greece', 1920, 1920, box(39.8, 40.5, 25.0, 26.0))

NOTE = {
    'FIX-229': 'Eastern Thrace, with Edirne and Istanbul, is Ottoman again, as the Treaty of Constantinople (1913) left it; Bulgaria keeps Western Thrace.',
    'FIX-230': 'Istanbul and the Straits are drawn as the Treaty of Sevres left them: Thrace west of the Chatalja lines Greek, Istanbul and the Asian shore Ottoman under Allied occupation (lines approximate).',
    'FIX-231': 'Aegean islands that were in no realm are given to the state that held them: Crete and the islands taken in 1912 to Greece, Rhodes and the Dodecanese to Italy, the rest to the Ottoman Empire before 1912.',
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
