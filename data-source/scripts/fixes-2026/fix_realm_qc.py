"""Realm names and territories shown outside their time (26 Oct 2026). Usage: python3 fix_realm_qc.py <site folder>

A sweep of every realm name on the era maps against when it existed found these:

FIX-149 Guanches: the native Guanche territory of the Canary Islands was kept on every map to 1848, though Castile
        finished conquering the islands in 1496. From the 1500 map on, the islands are Castilian, then Spanish.
FIX-150 Hong Kong: drawn as its own territory on the 1650-1800 maps; Britain took Hong Kong Island only in 1841. It
        joins the Qing Empire around it.
FIX-151 Names for their age:
        "European Bronze Age peoples" covered Europe on the 10,000-4,000 BCE maps, before the Bronze Age (about
        3300 BCE): European hunter-gatherers (Mesolithic) on the 10,000 and 8000 BCE maps, European Neolithic
        farmers on the 5000 and 4000 BCE maps.
        "N. European Bronze Age cultures" from 550 BCE: the Northern European Iron Age (the Jastorf culture and its
        neighbours) had begun by about 600 BCE.
        "Elam" on the 5000 and 4000 BCE maps, before Elam (about 3200 BCE): the Susiana cultures (Susa was founded
        about 4200 BCE).
        "Hurrian Kingdoms" on the 5000 and 4000 BCE maps, long before the Hurrian kingdoms (from about 2300 BCE): the
        Halaf and Ubaid cultures, and the Ubaid and Gawra cultures.
        "Haiti" on the 1715-1800 maps: the French colony of Saint-Domingue, which became Haiti in 1804.
        "Malaya" on the 1650-1880 maps, a British-era name: the Malay sultanates, as on the 1450-1600 maps.
        "Somalia" on the 1800-1880 maps, a 20th-century state: the Somali sultanates.
FIX-152 Spelling: Britany (Brittany), Burgandy (Burgundy), Rajastan (Rajasthan), and "Gambia, The" (The Gambia from
        independence in 1965, also where the 2026 map had "Gambia"; Gambia before).

Borders, areas and labels are re-traced with ../derive-2026/era_tools.py where a territory changes (Hong Kong); the
other fixes change names or the realm a territory belongs to. Afterwards: python3 scripts/build_realm_index.py."""
import collections, json, os, sys
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'derive-2026'))
import era_tools as T

SITE = sys.argv[1]
J = lambda p: json.load(open(p, encoding='utf-8'))
ORDER = ['n', 'r', 'k', 'p', 'a', 'b', 'l', 'w', 'a3', 'x', 'c']

# (first year, last year, old name, new name): applied to territory and realm names on those maps
RENAME = [
    (-10000, -8000, 'European Bronze Age peoples', 'European hunter-gatherers (Mesolithic)'),
    (-5000, -4000, 'European Bronze Age peoples', 'European Neolithic farmers'),
    (-550, -1, 'N. European Bronze Age cultures', 'N. European Iron Age cultures'),
    (-5000, -4000, 'Elam', 'Susiana cultures'),
    (-5000, -5000, 'Hurrian Kingdoms', 'Halaf and Ubaid cultures'),
    (-4000, -4000, 'Hurrian Kingdoms', 'Ubaid and Gawra cultures'),
    (1715, 1800, 'Haiti', 'Saint-Domingue'),
    (1650, 1880, 'Malaya', 'Malay sultanates'),
    (1800, 1880, 'Somalia', 'Somali sultanates'),
    (-10 ** 7, 9999, 'Britany', 'Brittany'),
    (-10 ** 7, 9999, 'Burgandy', 'Burgundy'),
    (-10 ** 7, 9999, 'Rajastan', 'Rajasthan'),
    (-10 ** 7, 1964, 'Gambia, The', 'Gambia'),
    (1965, 9999, 'Gambia, The', 'The Gambia'),
    (1965, 9999, 'Gambia', 'The Gambia'),
]
NOTE = {
    'European Bronze Age peoples': 'Europe was labelled "European Bronze Age peoples" before the Bronze Age; it is named for its age.',
    'N. European Bronze Age cultures': 'Northern Europe is in the Iron Age by this date (the Jastorf culture and its neighbours).',
    'Elam': 'Elam arose about 3200 BCE; this area is the Susiana cultures (Susa was founded about 4200 BCE).',
    'Hurrian Kingdoms': 'The Hurrian kingdoms date from about 2300 BCE; this area is named for its Neolithic and Chalcolithic cultures.',
    'Haiti': 'Haiti was the French colony of Saint-Domingue until independence in 1804.',
    'Malaya': '"Malaya" is a British-era name; the peninsula and its neighbours were Malay sultanates.',
    'Somalia': 'Somalia is a 20th-century state; the region was held by Somali sultanates and clans.',
}


def realm_named(js, names):
    for n in names:
        for i, r in enumerate(js['realms']):
            if r['n'] == n:
                return i
    return None


def fix_era(key, y, LAND):
    p = f'{SITE}/eras/{key}.json'; js = J(p)
    log = collections.Counter(); notes = []
    retrace = False
    # FIX-151 / FIX-152 renames
    for y0, y1, old, new in RENAME:
        if not (y0 <= y <= y1):
            continue
        hit = False
        for e in js['ents']:
            if e['n'] == old: e['n'] = new; hit = True
        for r in js['realms']:
            if r['n'] == old: r['n'] = new; hit = True
        if hit:
            log[f'FIX-15{1 if old in NOTE else 2} {old} -> {new}'] += 1
            if old in NOTE: notes.append(NOTE[old])
    # FIX-149 Guanches: Castilian, then Spanish, from 1500
    if y >= 1500:
        g = [i for i, e in enumerate(js['ents']) if e['n'] == 'Guanches']
        if g:
            heir = realm_named(js, ['Castille', 'Spain', 'Spain (Habsburg)'])
            assert heir is not None, key
            for i in g:
                e = js['ents'][i]; e['r'] = heir; e['n'] = js['realms'][heir]['n']; e['x'] = 1
                if 'l' in e: e.pop('l')
            log['FIX-149 Guanches'] += 1
            notes.append('The Canary Islands were conquered by Castile by 1496; the Guanche territory is Castilian/Spanish here.')
    # FIX-150 Hong Kong joins the Qing territory it borders most
    if 1650 <= y <= 1800:
        hk = [i + 1 for i, e in enumerate(js['ents']) if e['n'] == 'Hong Kong' and e.get('a')]
        if hk:
            same, bad = T.check_roundtrip(js, LAND)
            assert same and all(x[1] == x[2] and x[3] == x[4] for x in bad), f'tracing does not reproduce the {key} map; stop'
            ids = T.read_ids(js); orig = ids.copy()
            qing = realm_named(js, ['Qing Empire'])
            for i in hk:
                m = ids == i
                ring = np.zeros_like(m)
                ring[1:] |= m[:-1]; ring[:-1] |= m[1:]; ring[:, 1:] |= m[:, :-1]; ring[:, :-1] |= m[:, 1:]
                ring &= ~m
                nb = ids[ring]; nb = nb[nb > 0]
                cand = [v for v in nb if js['ents'][v - 1]['r'] == qing]
                t = collections.Counter(cand).most_common(1)[0][0]
                ids[m] = t; log['FIX-150 Hong Kong px'] += int(m.sum())
            notes.append('Hong Kong was part of Qing China until 1841; it no longer shows as a separate territory.')
            for i in set(np.unique(orig[ids != orig]).tolist()) | set(np.unique(ids[ids != orig]).tolist()):
                if i == 0: continue
                e = js['ents'][i - 1]; a, b, l = T.stats(ids, i)
                e['a'] = a
                for k, v in (('b', b), ('l', l)):
                    if v is None: e.pop(k, None)
                    else: e[k] = v
            js['borders'] = T.borders(ids, LAND)
            js['_png'] = T.write_ids(ids)
            try:
                import base64, oxipng
                js['_png'] = base64.b64encode(oxipng.optimize_from_memory(base64.b64decode(js['_png']), level=4)).decode('ascii')
            except ImportError:
                pass
            assert (T.read_ids(js) == ids).all()
            retrace = True
    if not log:
        return None
    js['ents'] = [{k: e[k] for k in ORDER if k in e} for e in js['ents']]
    js['notes'] += [n for n in dict.fromkeys(notes) if n not in js['notes']]
    open(p, 'w', encoding='utf-8').write(json.dumps(js, ensure_ascii=False, separators=(',', ':')))
    return dict(log), retrace


meta = J(f'{SITE}/data/eras.json')
LAND = None
total = collections.Counter()
for e in meta['eras']:
    y, key = e['y'], e['f']
    if 1650 <= y <= 1800 and LAND is None:
        LAND = T.land_mask(f'{SITE}/eras', [x['f'] for x in meta['eras']])
    r = fix_era(key, y, LAND)
    if r:
        total.update(r[0]); print(y, r[0], 're-traced' if r[1] else '', flush=True)
for ix in meta['eras']:
    js = J(f"{SITE}/eras/{ix['f']}.json")
    ix['c'] = len(js['notes'])
    ix['n'] = sum(1 for e in js['ents'] if e.get('a') and e['k'] == 0)
    ix['m'] = sum(1 for e in js['ents'] if e.get('a') and e['k'] == 1)
open(f'{SITE}/data/eras.json', 'w', encoding='utf-8').write(json.dumps(meta, ensure_ascii=True, separators=(',', ':')))
print('TOTAL', dict(total))
