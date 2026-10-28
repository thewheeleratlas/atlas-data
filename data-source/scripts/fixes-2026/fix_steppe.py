"""Central Asia and the steppe (27 Oct 2026): peoples named past their dates, misspelt, or named after a theory,
2500 BCE to 1000 CE. Usage: python3 fix_steppe.py <site folder>

FIX-181 The Karasuk culture (about 1500-800 BCE) was on the maps to 1 BCE across Kazakhstan: the Saka and Scythian
        nomads on the 700-250 BCE maps, the Saka and Wusun nomads on the 200 BCE-1 BCE maps.
FIX-182 "Scythians" covered the steppe from the Volga to the Altai until 500 CE. From 200 BCE, west of 60 E it is the
        Sarmatians (to 300 CE) and then the Huns and Oghur tribes (400, 500); east of 60 E it is the Saka and Wusun
        nomads. The line at 60 E is approximate. On the 600 and 700 maps the Pontic "Scythians" are the Bulgar and
        Onogur tribes.
FIX-183 Mongolia: "Proto-Altaic pastoralists" names a disputed language theory, not a people. They are the deer stone
        and khirigsuur herders (1500-1000 BCE), the Slab Grave culture (700-250 BCE) and the Xianbei (1 BCE-200 CE).
        The Hu nomads after the Xiongnu broke up are the Xianbei (100-300 CE).
FIX-184 "Proto-Thai cultures" on China's northern frontier (Thai peoples lived far to the south): the Rong and Di
        peoples (550-250 BCE) and the Wuhuan and northern frontier peoples (200 BCE-300 CE).
FIX-185 Spelling and small dates: Turcik -> Dingling and early Turkic tribes; Peshemegs -> Pechenegs; Kwarezm ->
        Khwarazm; the Jeulmun culture on the 1250 BCE map (it ended about 1500 BCE) is the Mumun culture; the Oghuz
        and Kimek tribes on the 400 and 500 maps, before they appear, are the Huns and Oghur tribes.

Names only, except the 60 E line in FIX-182. Borders, areas and labels are re-traced with ../derive-2026/era_tools.py.
Afterwards: python3 scripts/build_realm_index.py."""
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
NEW = {'Saka and Scythian nomads': '#a08a66', 'Saka and Wusun nomads': '#9c8c6a', 'Sarmatians': '#a2876a',
       'Huns and Oghur tribes': '#94806a', 'Bulgar and Onogur tribes': '#98866a', 'Deer stone and khirigsuur herders': '#8f8a74',
       'Slab Grave culture': '#8d8670', 'Xianbei': '#8e8c70', 'Rong and Di peoples': '#9a8c6c', 'Wuhuan and northern frontier peoples': '#988a6e',
       'Dingling and early Turkic tribes': '#8f8a6c', 'Pechenegs': '#9a856a', 'Khwarazm': '#b0805a', 'Mumun pottery culture': '#9a8f74'}


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
    ('Karasuk culture', 'Saka and Scythian nomads', -700, -250), ('Karasuk culture', 'Saka and Wusun nomads', -200, -1),
    ('Scythians', 'Bulgar and Onogur tribes', 600, 700),
    ('Proto-Altaic pastoralists', 'Deer stone and khirigsuur herders', -1500, -1000), ('Proto-Altaic pastoralists', 'Slab Grave culture', -700, -250),
    ('Proto-Altaic pastoralists', 'Xianbei', -1, 200), ('Hu nomads (proto-Xiongnu)', 'Xianbei', 100, 300),
    ('Proto-Thai cultures', 'Rong and Di peoples', -550, -250), ('Proto-Thai cultures', 'Wuhuan and northern frontier peoples', -200, 300),
    ('Turcik tribes', 'Dingling and early Turkic tribes', -200, 500), ('Peshemegs', 'Pechenegs', 700, 1000), ('Kwarezm', 'Khwarazm', 700, 700),
    ('Jeulmun pottery culture', 'Mumun pottery culture', -1250, -1250), ('Oghuz and Kimek tribes', 'Huns and Oghur tribes', 400, 500),
]
NOTE = {
    'FIX-181': 'The Karasuk culture ended about 800 BCE: the Kazakh steppe is the Saka (Scythian) nomads, then the Saka and Wusun.',
    'FIX-182': 'The steppe was not all Scythian: west of the Aral it is the Sarmatians, then the Huns and Oghurs; east of it the Saka and Wusun.',
    'FIX-183': 'Mongolia is named for its peoples and cultures of the time, not for the disputed "Proto-Altaic" language theory; after the Xiongnu, the Xianbei.',
    'FIX-184': 'China\'s northern frontier was the land of the Rong and Di, later the Wuhuan; Thai peoples lived far to the south.',
    'FIX-185': 'Names respelled or dated correctly.',
}
FIXN = {'Karasuk culture': 'FIX-181', 'Scythians': 'FIX-182', 'Proto-Altaic pastoralists': 'FIX-183', 'Hu nomads (proto-Xiongnu)': 'FIX-183',
        'Proto-Thai cultures': 'FIX-184', 'Turcik tribes': 'FIX-185', 'Peshemegs': 'FIX-185', 'Kwarezm': 'FIX-185',
        'Jeulmun pottery culture': 'FIX-185', 'Oghuz and Kimek tribes': 'FIX-185'}


def lon_mask(lon0):
    xs = (np.arange(T.EW) + 0.5) / T.EW * 360 - 180
    return np.ones((T.EH, 1), bool) & (xs >= lon0)[None, :]


def fix_era(y, LAND):
    key = F[y]; p = f'{SITE}/eras/{key}.json'; js = J(p)
    log = collections.Counter(); notes = []
    ids = None
    # FIX-182: from 200 BCE to 500 CE the steppe "Scythians" are split at 60 E
    if -200 <= y <= 500:
        sc = [i + 1 for i, e in enumerate(js['ents']) if e['r'] >= 0 and js['realms'][e['r']]['n'] == 'Scythians' and e.get('a')]
        if sc:
            same, bad = T.check_roundtrip(js, LAND)
            assert same and all(x[1] == x[2] and x[3] == x[4] for x in bad), f'tracing does not reproduce the {key} map; stop'
            ids = T.read_ids(js); orig = ids.copy()
            east_name = 'Saka and Wusun nomads'; west_name = 'Sarmatians' if y <= 300 else 'Huns and Oghur tribes'
            m = lon_mask(60.0) & np.isin(ids, sc)
            if m.any():
                js['ents'].append({'n': east_name, 'r': realm_of(js, east_name), 'k': 1, 'p': 1, 'a': 0, 'x': 1})
                ni = len(js['ents']); ids[m] = ni; log['FIX-182 px'] += int(m.sum())
                ov = J(f'{SITE}/data/ovmain.json'); rows = ov['eras'][key]
                while len(rows) < ni: rows.append(list(rows[int(np.bincount(orig[m]).argmax()) - 1]))
                open(f'{SITE}/data/ovmain.json', 'w', encoding='utf-8').write(json.dumps(ov, ensure_ascii=True, separators=(',', ':')))
            for i in sc:
                e = js['ents'][i - 1]; e['r'] = realm_of(js, west_name); e['n'] = west_name; e['x'] = 1
            notes.append(NOTE['FIX-182'])
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
for y in sorted(y for y in F if -2500 <= y <= 1000):
    r = fix_era(y, LAND)
    if r: print(y, r, flush=True)
for ix in EMETA['eras']:
    js = J(f"{SITE}/eras/{ix['f']}.json")
    ix['c'] = len(js['notes'])
    ix['n'] = sum(1 for e in js['ents'] if e.get('a') and e['k'] == 0)
    ix['m'] = sum(1 for e in js['ents'] if e.get('a') and e['k'] == 1)
open(f'{SITE}/data/eras.json', 'w', encoding='utf-8').write(json.dumps(EMETA, ensure_ascii=True, separators=(',', ':')))
