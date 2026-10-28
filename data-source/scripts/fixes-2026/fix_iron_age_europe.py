"""Iron Age Europe (27 Oct 2026): peoples and archaeological cultures named past their dates, 1500 BCE to 700 CE.
Usage: python3 fix_iron_age_europe.py <site folder>

FIX-176 Urnfield cultures (about 1300-750 BCE) were on the maps to 100 BCE. Central and western Europe is the
        Hallstatt culture on the 700-500 BCE maps, and the Celts (La Tène culture) from 400 BCE.
FIX-177 Hallstatt culture (about 800-450 BCE) was on the maps from 400 BCE to 300 CE, from Gaul to Poland. From 400 to
        100 BCE it is the Celts (La Tène culture), with the land north of about 51.5 N the Germanic peoples of the
        Jastorf culture; from 1 BCE to 300 CE, outside the Roman Empire, it is the Germanic tribes. A small "La Tène
        culture" on the 700-500 BCE maps, before La Tène began (about 450 BCE), is Hallstatt.
FIX-178 The Pontic steppe: the Cimmerians (spelled "Cimerians") were on the maps to 1 BCE. They are the Cimmerians on
        the 1000 and 700 BCE maps, the Scythians on the 550-250 BCE maps and the Sarmatians on the 200 BCE-1 BCE maps;
        the "Proto-Scythian culture" of the 700 BCE map is the Scythians from 550 BCE.
FIX-179 Between the Oder and the Vistula, cultures past their dates: the Lusatian culture (to about 500 BCE) is the
        Pomeranian culture on the 550-250 BCE maps and the Przeworsk culture on the 200 BCE-1 BCE maps; the Pomeranian
        and bell-shaped burials cultures (to about 150 BCE) are the Wielbark culture (the Goths) and the Przeworsk
        culture from 100 BCE to 300 CE, the Germanic tribes on the 400 map and the Slavic tribes from 500.
FIX-180 Further east and south: the Milograd culture (to about the 1st century) is the Balts from 100 CE; the
        Celtiberians on the 1000 BCE map, before they formed, are the Iberian Bronze Age peoples; the Illyrians on the
        1500 and 1250 BCE maps, before they appear, are the Balkan Bronze Age peoples.

Names only, except the Celtic-Germanic line in FIX-177, which is drawn as a straight latitude and is approximate.
Borders, areas and labels are re-traced with ../derive-2026/era_tools.py. Afterwards: python3 scripts/build_realm_index.py."""
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
SEEN = {}
for f in F.values():
    for r in J(f'{SITE}/eras/{f}.json')['realms']:
        SEEN.setdefault(r['n'], r['g'])
NEW = {'Celts (La Tène culture)': '#7d9a5e', 'Sarmatians': '#a2876a', 'Przeworsk culture': '#8c8f6d',
       'Wielbark culture (Goths)': '#8a8a72', 'Balkan Bronze Age peoples': '#93866c', 'Cimmerians': '#9b8a6e',
       'Hallstatt culture': '#7f9a6a', 'Germanic tribes': '#8a9566', 'Iberian Bronze Age peoples': '#8a8a9a'}


def gid(name):
    for i, g in enumerate(G):
        if g['n'] == name: return i
    if name in SEEN: return SEEN[name]
    G.append({'k': name.lower(), 'c': NEW[name], 't': 1, 'n': name}); SEEN[name] = len(G) - 1; return SEEN[name]


def realm_of(js, name):
    for i, r in enumerate(js['realms']):
        if r['n'] == name: return i
    js['realms'].append({'g': gid(name), 'n': name}); return len(js['realms']) - 1


# (old realm name, new name, first year, last year)
RENAME = [
    ('Urnfield cultures', 'Hallstatt culture', -700, -500), ('Urnfield cultures', 'Celts (La Tène culture)', -400, -100),
    ('Hallstatt culture', 'Germanic tribes', -1, 300),
    ('La Tène culture', 'Hallstatt culture', -700, -500),
    ('Cimerians', 'Cimmerians', -1000, -700), ('Cimerians', 'Scythians', -550, -250), ('Cimerians', 'Sarmatians', -200, -1),
    ('Proto-Scythian culture', 'Scythians', -550, -1),
    ('Lusatian culture', 'Pomeranian culture', -550, -250), ('Lusatian culture', 'Przeworsk culture', -200, -1),
    ('Pomeranian culture', 'Wielbark culture (Goths)', -100, 300), ('Pomeranian culture', 'Germanic tribes', 400, 400),
    ('Pomeranian culture', 'Slavic tribes', 500, 700),
    ('Bell-shaped burials culture', 'Przeworsk culture', -100, 300), ('Bell-shaped burials culture', 'Germanic tribes', 400, 400),
    ('Bell-shaped burials culture', 'Slavic tribes', 500, 700),
    ('Milograd culture', 'Balts', 100, 700),
    ('Celtiberians', 'Iberian Bronze Age peoples', -1000, -1000),
    ('Illyrians', 'Balkan Bronze Age peoples', -1500, -1250),
]
NOTE = {
    'FIX-176': 'The Urnfield cultures ended about 750 BCE: central Europe is Hallstatt, then the Celts of the La Tène culture.',
    'FIX-177': 'The Hallstatt culture ended about 450 BCE: central Europe is the Celts of the La Tène culture, with the Germanic peoples to the north, and later the Germanic tribes.',
    'FIX-178': 'The Pontic steppe is the Scythians, then the Sarmatians; the Cimmerians are gone by about 600 BCE.',
    'FIX-179': 'Between the Oder and the Vistula, Bronze Age culture names give way to the Przeworsk and Wielbark cultures, the Germanic tribes and the Slavs.',
    'FIX-180': 'Peoples named before or after their time are renamed for this date.',
}
FIXN = {'Urnfield cultures': 'FIX-176', 'Hallstatt culture': 'FIX-177', 'La Tène culture': 'FIX-177', 'Cimerians': 'FIX-178',
        'Proto-Scythian culture': 'FIX-178', 'Lusatian culture': 'FIX-179', 'Pomeranian culture': 'FIX-179',
        'Bell-shaped burials culture': 'FIX-179', 'Milograd culture': 'FIX-180', 'Celtiberians': 'FIX-180', 'Illyrians': 'FIX-180'}


def lat_mask(lat0):
    return (T.LATR >= lat0)[:, None] & np.ones((1, T.EW), bool)


def fix_era(y, LAND):
    key = F[y]; p = f'{SITE}/eras/{key}.json'; js = J(p)
    log = collections.Counter(); notes = []
    ids = None
    # FIX-177 split first, while the Hallstatt territory still has its old name: north of 51.5 N is Germanic
    if -400 <= y <= -100:
        hs = [i + 1 for i, e in enumerate(js['ents']) if e['r'] >= 0 and js['realms'][e['r']]['n'] == 'Hallstatt culture' and e.get('a')]
        if hs:
            same, bad = T.check_roundtrip(js, LAND)
            assert same and all(x[1] == x[2] and x[3] == x[4] for x in bad), f'tracing does not reproduce the {key} map; stop'
            ids = T.read_ids(js); orig = ids.copy()
            m = lat_mask(51.5) & np.isin(ids, hs)
            if m.any():
                js['ents'].append({'n': 'Germanic peoples (Jastorf culture)', 'r': realm_of(js, 'Germanic tribes'), 'k': 1, 'p': 1, 'a': 0, 'x': 1})
                ni = len(js['ents']); ids[m] = ni; log['FIX-177 px'] += int(m.sum())
                ov = J(f'{SITE}/data/ovmain.json'); rows = ov['eras'][key]
                while len(rows) < ni: rows.append(list(rows[int(np.bincount(orig[m]).argmax()) - 1]))
                open(f'{SITE}/data/ovmain.json', 'w', encoding='utf-8').write(json.dumps(ov, ensure_ascii=True, separators=(',', ':')))
            for i in hs:
                e = js['ents'][i - 1]; e['r'] = realm_of(js, 'Celts (La Tène culture)'); e['n'] = 'Celts (La Tène culture)'; e['x'] = 1
            notes.append(NOTE['FIX-177'])
    for old, new, y0, y1 in RENAME:
        if not (y0 <= y <= y1): continue
        hit = [e for e in js['ents'] if e['r'] >= 0 and e.get('a') and js['realms'][e['r']]['n'] == old]
        for e in hit:
            e['r'] = realm_of(js, new); e['n'] = new; e['x'] = 1; log[FIXN[old]] += 1
        if hit: notes.append(NOTE[FIXN[old]])
    if not log:
        return None
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
for y in sorted(y for y in F if -1500 <= y <= 700):
    r = fix_era(y, LAND)
    if r: print(y, r, flush=True)
for ix in EMETA['eras']:
    js = J(f"{SITE}/eras/{ix['f']}.json")
    ix['c'] = len(js['notes'])
    ix['n'] = sum(1 for e in js['ents'] if e.get('a') and e['k'] == 0)
    ix['m'] = sum(1 for e in js['ents'] if e.get('a') and e['k'] == 1)
open(f'{SITE}/data/eras.json', 'w', encoding='utf-8').write(json.dumps(EMETA, ensure_ascii=True, separators=(',', ':')))
