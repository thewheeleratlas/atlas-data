"""Realm QC pass 6 (28 Oct 2026): colonial North America drawn as the land held, not the land claimed, 1650-1800.
Usage: python3 fix_qc6.py <site folder>

The atlas shows the land a European power actually held at each date: its towns, missions, posts and forts and the
land around them. Paper claims over land its native peoples still held are given back to those peoples. Where a map
has no native territory to give back, the peoples are taken from the nearest earlier map (most recent first) at the
same place, with the same names, faith, culture and development rows; where no earlier map has one either, a named
fallback is used. All lines and boxes below are approximate.

FIX-205 New Spain north of about 31.5 N (1650-1800) keeps only the Rio Grande corridor of New Mexico (32-36.5 N,
        107.5-105.5 W), El Paso, Pimería Alta and Tucson (from 1700), the Texas line from San Antonio to Nacogdoches
        (from 1715) and the Alta California mission coast (from 1783); Baja California north of 28 N, and all of it in
        1650, is its peoples' own. The rest is the Apache, Navajo, Comanche, Ute, Paiute, Yokuts and other peoples.
FIX-206 Spanish Louisiana (1783, 1800) is the Mississippi corridor (29-39 N, 92-89.5 W) and Natchitoches; the Plains
        are the Osage, Pawnee, Wichita, Lakota and other peoples.
FIX-207 Rupert's Land (1700-1800) is the Hudson Bay and James Bay coasts (51-59 N, 95-78 W), with the Saskatchewan
        River posts from 1783 (52-55 N, 107-95 W); the rest is the Cree, Assiniboine, Chipewyan, Dene and other
        peoples.
FIX-208 Spanish Florida (1715, 1750) is St Augustine, Pensacola and St Marks after the mission belt was destroyed in
        1702-06; the rest is the Yamasee and Lower Creek in the north and the Calusa and Tequesta in the south.
FIX-209 The Ohio country north of the Ohio River (1783; in 1800 west of 84.8 W and, in Ohio, north of the Greenville
        line, about 40.3 N) was held by the Shawnee, Miami, Delaware and Wyandot until 1795: no longer part of the USA.
        The Province of Quebec (1783) and Lower Canada (1800) keep the St Lawrence valley; the interior north of about
        48.5 N is the Innu and Cree.

Borders, areas and labels are re-traced with ../derive-2026/era_tools.py. Afterwards: python3 scripts/build_realm_index.py,
data-source/scripts/overlays/ovsecond_build.py and scripts/build_content_pages.py."""
import collections, json, os, sys
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'derive-2026'))
import era_tools as T

SITE = sys.argv[1]
J = lambda p: json.load(open(p, encoding='utf-8'))
ORDER = ['n', 'r', 'k', 'p', 'a', 'b', 'l', 'w', 'a3', 'x', 'c']
EMETA = J(f'{SITE}/data/eras.json')
F = {e['y']: e['f'] for e in EMETA['eras']}
G = EMETA['realms']
LAT = T.LATR[:, None] * np.ones((1, T.EW))
LON = ((np.arange(T.EW) + 0.5) / T.EW * 360 - 180)[None, :] * np.ones((T.EH, 1))
COLONIAL = {'Spain', 'Spain (Habsburg)', 'Kingdom of Great Britain', 'Kingdom of England', 'Commonwealth of England', 'France',
            'Dutch Republic', 'United States of America', 'Russian Empire', 'Tsardom of Russia', 'Denmark-Norway', 'Sweden'}
SOURCES = [1530, 1600, 1650, 1700, 1715, 1750, 1783]


def box(la0, la1, lo0, lo1):
    return (LAT >= la0) & (LAT <= la1) & (LON >= lo0) & (LON <= lo1)


# The California coast runs north-west: the mission strip is the land within about 0.9 degrees of it.
_cl = np.interp(LAT, [32.5, 34.0, 34.5, 36.0, 38.0], [-117.1, -118.6, -120.6, -121.9, -122.9])
CA_STRIP = (LAT >= 32.5) & (LAT <= 38.0) & (LON <= _cl + 0.9)
NM = box(32, 36.5, -107.5, -105.5)
EL_PASO = box(31.5, 32.2, -107, -106)
TUCSON = box(31.5, 32.3, -112, -110.5)
TEXAS = box(28.5, 32, -100, -93.5)
BAJA = (LON < -109.5) & (LAT < 32.8) & (LAT > 22.5) & (LON > -118) & ~((LAT > 31.3) & (LON > -114.8))


def ns_restore(y):
    keep = NM | EL_PASO
    if y >= 1700: keep |= TUCSON
    if y >= 1715: keep |= TEXAS
    if y >= 1783: keep |= CA_STRIP
    north = (LAT >= 31.5) & (LON < -93)
    baja = BAJA & ((LAT >= 28) if y >= 1700 else np.ones_like(BAJA))
    return (north | baja) & ~keep


RL_KEEP = box(51, 59, -95, -78)
RL_KEEP_1783 = RL_KEEP | box(52, 55, -107, -95)
FL_KEEP = box(29.4, 30.4, -81.8, -81.1) | box(30.2, 30.7, -87.6, -86.9) | box(30.0, 30.3, -84.4, -84.0)
river = 40.4 + (LON + 80) * 0.3736                 # the Ohio River, Pittsburgh to Cairo, as a straight line
OHIO = (LON < -80.5) & (LON > -91.5) & (LAT > river) & (LAT < 42.3)
OHIO_1800 = OHIO & ((LON < -84.8) | (LAT > 40.3))

# (fix, year, colonial territory names, mask to give back, fallback name for land no map gives a people to;
#  a leading ! uses the fallback name for all of it: the Timucua and Apalachee of the earlier maps were gone by 1715)
PLAN = []
for y in (1650, 1700, 1715, 1750, 1783, 1800):
    PLAN.append(('FIX-205', y, ['Viceroyalty of New Spain'], ns_restore(y), 'Apache and other peoples of the north'))
for y in (1783, 1800):
    PLAN.append(('FIX-206', y, ['Spanish Louisiana'], ~(box(29, 39, -92, -89.5) | box(31, 32.2, -94, -92)), 'Plains peoples'))
for y in (1700, 1715, 1750, 1783, 1800):
    PLAN.append(('FIX-207', y, ["Rupert's Land"], ~(RL_KEEP_1783 if y >= 1783 else RL_KEEP), 'Cree and Dene peoples'))
for y in (1715, 1750):
    PLAN.append(('FIX-208', y, ['Florida (Spain)'], ~FL_KEEP & (LAT >= 28.5), '!Yamasee and Lower Creek'))   # ! = always this name
    PLAN.append(('FIX-208', y, ['Florida (Spain)'], ~FL_KEEP & (LAT < 28.5), 'Calusa'))
PLAN.append(('FIX-209', 1783, ['United States of America'], OHIO, 'Shawnee, Miami, Delaware and Wyandot'))
PLAN.append(('FIX-209', 1800, ['United States of America'], OHIO_1800, 'Shawnee, Miami, Delaware and Wyandot'))
PLAN.append(('FIX-209', 1783, ['Province of Quebec'], (LAT > 48.5) & ~((LAT < 50.3) & (LON > -70) & (LON < -64)), 'Innu and Cree'))
PLAN.append(('FIX-209', 1800, ['Lower Canada'], (LAT > 48.5) & ~((LAT < 50.3) & (LON > -70) & (LON < -64)), 'Innu and Cree'))

NOTE = {
    'FIX-205': 'New Spain is shown where Spain held it: in the north, the Rio Grande of New Mexico, its missions and presidios, not the lands of the Apache, Comanche and other peoples (lines approximate).',
    'FIX-206': 'Spanish Louisiana is shown as the Mississippi towns Spain held; the Plains were the lands of their peoples (lines approximate).',
    'FIX-207': 'Rupert\'s Land is shown as the Hudson\'s Bay Company\'s posts on the Bay and, later, the Saskatchewan; the rest was Cree, Assiniboine and Dene land (lines approximate).',
    'FIX-208': 'After 1706 Spanish Florida was St Augustine, Pensacola and St Marks; the rest was Creek, Yamasee and Calusa land (lines approximate).',
    'FIX-209': 'The Ohio country was held by the Shawnee, Miami, Delaware and Wyandot until 1795, and the north of Quebec by the Innu and Cree (lines approximate).',
}
DEFAULT_ROW = None


def load(y):
    js = J(f'{SITE}/eras/{F[y]}.json')
    return js, T.read_ids(js)


def native_ids(js):
    out = np.zeros(len(js['ents']) + 1, bool)
    for i, e in enumerate(js['ents'], 1):
        if e.get('a') and e['r'] >= 0 and js['realms'][e['r']]['n'] not in COLONIAL: out[i] = True
    return out


def realm_of(js, name, g):
    for i, r in enumerate(js['realms']):
        if r['n'] == name: return i
    js['realms'].append({'g': g, 'n': name}); return len(js['realms']) - 1


def gid_new(name):
    for i, g in enumerate(G):
        if g['n'] == name: return i
    G.append({'k': name.lower(), 'c': '#9a8a6e', 't': 1, 'n': name}); return len(G) - 1


def fix_era(y, plan, LAND, ov):
    key = F[y]; p = f'{SITE}/eras/{key}.json'
    js, ids = load(y)
    same, bad = T.check_roundtrip(js, LAND)
    assert same and all(x[1] == x[2] and x[3] == x[4] for x in bad), f'tracing does not reproduce the {key} map; stop'
    orig = ids.copy(); rows = ov['eras'][key]
    log = collections.Counter(); notes = []
    by_name = {}
    for i, e in enumerate(js['ents'], 1):
        if e.get('a') and e['k'] == 1 and e['r'] >= 0 and js['realms'][e['r']]['n'] not in COLONIAL:
            by_name.setdefault(e['n'], i)

    def ent_for(name, src_js=None, src_i=None):
        if name in by_name: return by_name[name]
        if src_js is not None:
            se = src_js['ents'][src_i - 1]; sr = src_js['realms'][se['r']]
            e = {k: se[k] for k in ('n', 'k', 'p', 'w') if k in se}
            e['r'] = realm_of(js, sr['n'], sr['g']); row = list(ov['eras'][F[src_y]][src_i - 1])
        else:
            e = {'n': name, 'k': 1, 'p': 1}; e['r'] = realm_of(js, name, gid_new(name)); row = None
        e['x'] = 1; e['a'] = 1
        js['ents'].append(e); ni = len(js['ents'])
        if row is None:                                   # a fallback people: the faith and culture of the land it takes
            row = list(rows[int(np.bincount(orig[todo]).argmax()) - 1])
        rows.append(row); by_name[name] = ni
        return ni

    for fix, _, names, mask, fallback in plan:
        col = [i for i, e in enumerate(js['ents'], 1) if e.get('a') and e['n'] in names]
        todo = np.isin(ids, col) & mask
        if not todo.any(): continue
        log[fix + ' px'] += int(todo.sum())
        left = todo.copy()
        force = fallback.startswith('!'); fallback = fallback.lstrip('!')
        for src_y in [] if force else sorted((s for s in SOURCES if s < y), reverse=True):
            if not left.any(): break
            sjs, sids = SRC[src_y]
            nat = native_ids(sjs)[sids] & left
            if not nat.any(): continue
            for si in np.unique(sids[nat]):
                m = nat & (sids == si)
                ids[m] = ent_for(sjs['ents'][si - 1]['n'], sjs, int(si))
                log[fix + ' peoples'] += 1
            left &= ~nat
        if left.any():
            ids[left] = ent_for(fallback); log[fix + ' fallback px'] += int(left.sum())
        notes.append(NOTE[fix])
    if not log:
        return None
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
    used = sorted({e['r'] for e in js['ents'] if e['r'] >= 0})
    remap = {r: k for k, r in enumerate(used)}
    js['realms'] = [js['realms'][r] for r in used]
    for e in js['ents']:
        if e['r'] >= 0: e['r'] = remap[e['r']]
    js['ents'] = [{k: e[k] for k in ORDER if k in e} for e in js['ents']]
    js['notes'] += [n for n in dict.fromkeys(notes) if n not in js['notes']]
    assert len(rows) == len(js['ents'])
    open(p, 'w', encoding='utf-8').write(json.dumps(js, ensure_ascii=False, separators=(',', ':')))
    SRC[y] = (js, ids)                                    # later maps take peoples from this one, as fixed
    return dict(log)


LAND = T.land_mask(f'{SITE}/eras', list(F.values()))
SRC = {y: load(y) for y in SOURCES}
ov = J(f'{SITE}/data/ovmain.json')
for y in (1650, 1700, 1715, 1750, 1783, 1800):
    r = fix_era(y, [p for p in PLAN if p[1] == y], LAND, ov)
    if r: print(y, r, flush=True)
open(f'{SITE}/data/ovmain.json', 'w', encoding='utf-8').write(json.dumps(ov, ensure_ascii=True, separators=(',', ':')))
for ix in EMETA['eras']:
    js = J(f"{SITE}/eras/{ix['f']}.json")
    ix['c'] = len(js['notes'])
    ix['n'] = sum(1 for e in js['ents'] if e.get('a') and e['k'] == 0)
    ix['m'] = sum(1 for e in js['ents'] if e.get('a') and e['k'] == 1)
open(f'{SITE}/data/eras.json', 'w', encoding='utf-8').write(json.dumps(EMETA, ensure_ascii=True, separators=(',', ':')))
