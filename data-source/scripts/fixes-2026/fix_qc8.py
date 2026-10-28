"""Realm QC pass 8 (28 Oct 2026): realms filed under the wrong state, names used before or after their time, and
states drawn after they ended. Found by the realm-page review (docs/realm-flags-2026-10-28.json) and a scan of every
territory whose name shares nothing with its realm's.
Usage: python3 fix_qc8.py <site folder> [one year]

FIX-221 Territories filed under the wrong realm (mostly by a name that began alike): the Austronesian peoples of the
        islands and Taiwan were counted as part of the Austrian Empire and Austria-Hungary (1815-1900), and the
        Austronesians and the Austroasiatic rice farmers as each other (3000 BCE-300 CE); the Netherlands itself was
        inside the "Netherlands East Indies" (1945); Travancore and Cochin were Dutch (1783-1800), Malabar Dutch in
        1800 (British from 1792) and Goa British in 1848 (Portuguese); Cochin China was Qing (1783-1848: Tay Son in
        1783, the Nguyen lords in 1800, then Vietnam); Sardinia was Savoyard in 1530-1600 (Spanish crown until 1708) and
        Sardinia, Naples and Sicily were Austrian or Savoyard in 1700 (Spanish until 1707-1713).
FIX-222 Names used before or after their time: Castile (not "Castille"); the Far Eastern Republic (1920, not an
        SSR); Upper Volta (1960); the United Kingdom of Great Britain and Northern Ireland (1930; "and Ireland" until
        1922-27); the Union of South Africa (1945, 1960; the Republic from 1961); the Emirate of Nejd and Hasa (1920);
        French Somaliland (1945, 1960) and Spanish Guinea (1900-1960) for the later Djibouti and Equatorial Guinea;
        Ethiopia (not also "Abyssinia", 1900-1914); the Emirate of Afghanistan (1848; Durrani rule ended in the 1820s);
        Gandhara as an Achaemenid satrapy (500 BCE).
FIX-223 One name for two different states: the Kingdom of Kongo (1450-1880; "Congo" is kept for the modern
        republic), the Mali Empire (1279-1530) and the Manden kingdoms after it (1650-1750), the Kingdom of Benin
        (1279-1880; "Benin" is the modern republic), the Ghana Empire (800-1100), the Western and Eastern Jin (300,
        400) and the Jurchen Jin (1200-1210), the Rajput kingdoms (1450-1500, not "Rajasthan", a 1949 name), Oman
        (1000-1530, not "Muscat").
FIX-224 States drawn after they ended or before they began: Funj in 1848 and Darfur in 1878-1880 were the Egyptian
        Sudan (conquered 1821 and 1874); the Songhai Empire fell in 1591, so 1650-1848 show the Dendi kingdom; Wadai
        was founded about 1635, so 1530-1600 show the Tunjur kingdom; Meroe had fallen by about 350 (the Noba, 400);
        the Fulani (Sokoto) jihad began in 1804 (the Hausa kingdoms, 1800); Tibet was divided from 842 to 1253
        (Tibetan principalities, 1000-1210); the Carolingian Empire broke up in 887-888 (West Francia and Lotharingia
        and Burgundy, 900); the Ostrogothic kingdom ended in 553-554 and the Khazar khaganate about 969 (their land
        goes to the neighbouring realms on the 600 and 1000 maps).

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
def A(fix, old, y0, y1, mask=None):                         # absorb: the territory joins its neighbours
    OPS.append((fix, 'absorb', y0, y1, old, dict(mask=mask)))

# FIX-221 (the name is kept; the territory goes to its own realm or the right one)
for n in ('Austronesian peoples', 'Taiwanese Austronesians'):
    R('FIX-221', n, n, 1815, 1900, realm=n)
for n in ('Austronesians', 'Austronesian peoples'):
    R('FIX-221', n, n, -2000, -250, realm='Austronesians')
R('FIX-221', 'Austroasiatic rice farmers', 'Austroasiatic rice farmers', -3000, 300, realm='Austroasiatic rice farmers')
R('FIX-221', 'Netherlands', 'Netherlands', 1945, 1945, realm='Netherlands')
R('FIX-221', 'Batavian Republic', 'United Kingdom of the Netherlands', 1815, 1815, realm='United Kingdom of the Netherlands')
R('FIX-221', 'Batavian Republic', 'Netherlands', 1848, 1848, realm='Netherlands')
R('FIX-221', 'Travancore', 'Travancore', 1783, 1800, realm='Travancore')
R('FIX-221', 'Cochin', 'Kingdom of Cochin', 1783, 1800, realm='Kingdom of Cochin')
R('FIX-221', 'Malabar', 'Malabar', 1800, 1800, realm='Kingdom of Great Britain')
R('FIX-221', 'Goa', 'Goa', 1848, 1848, realm='Portugal')
R('FIX-221', 'Cochin China', 'Cochin China', 1783, 1783, realm='Tây Sơn')
R('FIX-221', 'Cochin China', 'Cochin China', 1800, 1800, realm='Nguyễn lords')
R('FIX-221', 'Cochin China', 'Cochin China', 1815, 1848, realm='Vietnam (Nguyễn dynasty)')
R('FIX-221', 'Sardinia', 'Sardinia', 1530, 1600, realm='Sardinia')
for n in ('Sardinia', 'Naples', 'Sicily'):
    R('FIX-221', n, n, 1700, 1700, realm='Spain (Habsburg)')
# FIX-222
R('FIX-222', 'Castille', 'Castile', 1450, 1500)
R('FIX-222', 'Far Eastern SSR', 'Far Eastern Republic', 1920, 1920)
R('FIX-222', 'Burkina Faso', 'Upper Volta', 1960, 1960, realm='Upper Volta')
R('FIX-222', 'United Kingdom of Great Britain and Ireland', 'United Kingdom', 1930, 1930, realm='United Kingdom')
R('FIX-222', 'South Africa', 'Union of South Africa', 1945, 1960, realm='Union of South Africa')
R('FIX-222', 'Sultanate of Nejd', 'Emirate of Nejd and Hasa', 1920, 1920)
R('FIX-222', 'Djibouti', 'French Somaliland', 1945, 1960, realm='France')
R('FIX-222', 'Equatorial Guinea', 'Spanish Guinea', 1900, 1960, realm='Spain')
R('FIX-222', 'Abyssinia', 'Ethiopia', 1900, 1914, realm='Ethiopia')
R('FIX-222', 'Ethiopia', 'Ethiopia', 1900, 1914, realm='Ethiopia')
R('FIX-222', 'Durrani Empire', 'Emirate of Afghanistan', 1848, 1848)
R('FIX-222', 'Gandhāra', 'Gandhāra', -500, -500, realm='Achaemenid Empire')
# FIX-223
R('FIX-223', 'Congo', 'Kingdom of Kongo', 1450, 1880)
R('FIX-223', 'Mali', 'Mali Empire', 1279, 1530)
R('FIX-223', 'Mali', 'Manden kingdoms', 1650, 1750)
R('FIX-223', 'Benin', 'Kingdom of Benin', 1279, 1880)
R('FIX-223', 'Ghana', 'Ghana Empire', 800, 1100)
R('FIX-223', 'Jin', 'Western Jin', 300, 300)
R('FIX-223', 'Jin', 'Eastern Jin', 400, 400)
R('FIX-223', 'Jin Empire', 'Jurchen Jin', 1200, 1210)
R('FIX-223', 'Rajasthan', 'Rajput kingdoms', 1450, 1500)
R('FIX-223', 'Muscat', 'Oman', 1000, 1530, realm='Oman')
# FIX-224
R('FIX-224', 'Funj', 'Egyptian Sudan', 1848, 1848, realm='Ottoman Empire')
R('FIX-224', 'Sultanate of Darfur', 'Egyptian Sudan', 1878, 1880, realm='Ottoman Empire')
R('FIX-224', 'Songhai', 'Dendi kingdom', 1650, 1848)
R('FIX-224', 'Wadai', 'Tunjur kingdom', 1530, 1600)
R('FIX-224', 'Meroe', 'Noba', 400, 400)
R('FIX-224', 'Fulani Empire', 'Hausa kingdoms', 1800, 1800)
R('FIX-224', 'Tibet', 'Tibetan principalities', 1000, 1210)
R('FIX-224', 'West Francia', 'West Francia', 900, 900, realm='West Francia')
R('FIX-224', 'Carolingian Empire', 'Lotharingia and Burgundy', 900, 900)
A('FIX-224', 'Ostrogoths', 600, 600)
A('FIX-224', 'Khazars', 1000, 1000)

NOTE = {
    'FIX-221': 'Territories filed under the wrong realm are moved to their own (for example the islands of South-East Asia, Travancore and Cochin, Cochin China, Sardinia).',
    'FIX-222': 'Names are the ones in use on this map\u2019s date.',
    'FIX-223': 'Two different states with one name are named apart (for example the Kingdom of Kongo and the modern Congo).',
    'FIX-224': 'States drawn after they ended, or before they began, are replaced by what held the land on this map\u2019s date.',
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
