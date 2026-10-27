"""Realm QC, second pass (26 Oct 2026). Usage: python3 fix_realm_qc2.py <site folder>

Major states were checked against every map year inside and outside their lifetimes:

FIX-154 Korea: the peninsula was part of the Yuan dynasty on the 1279 and 1300 maps and of the Northern Yuan on the
        1400 map. Goryeo ruled it (as a Yuan vassal from 1270) until 1392, and Joseon after. Korea is Goryeo on the
        1279 and 1300 maps and Joseon on the 1400 map, with Joseon's outline from the 1450 map (approximate: the
        Yuan held the far north-east until 1356).
FIX-155 Java: on the 1450-1500 maps Java and Bali were part of the "Malay sultanates". Majapahit ruled the east of
        Java, Madura and Bali until about 1527, and the Hindu Sunda Kingdom the west (to 1579). East and central
        Java, Madura and Bali (east of 108.6 E) are Majapahit on the 1450-1500 maps; West Java is the Sunda Kingdom
        on the 1450-1530 maps. Outlines follow the coast; the line between them is approximate.
FIX-156 The 1000 map called the Danish realm "Denmark-Norway", the name of the union of 1524-1814. In 1000 Norway was
        under Danish overlordship after the battle of Svolder: Denmark (with Norway).
FIX-157 250 BCE: a one-pixel piece of the "Empire of Alexander", which broke up after 323 BCE, joins the territory
        around it.

Borders, areas and labels are re-traced with ../derive-2026/era_tools.py; new territories get their main faith and
culture from the overlay rasters (data/ovmain.json). Afterwards: python3 scripts/build_realm_index.py."""
import collections, copy, json, os, sys
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'derive-2026'))
import era_tools as T

SITE = sys.argv[1]
J = lambda p: json.load(open(p, encoding='utf-8'))
ORDER = ['n', 'r', 'k', 'p', 'a', 'b', 'l', 'w', 'a3', 'x', 'c']
EMETA = J(f'{SITE}/data/eras.json')
F = {e['y']: e['f'] for e in EMETA['eras']}
G = EMETA['realms']


def group(name, colour=None, key=None):
    for i, g in enumerate(G):
        if g['n'] == name:
            return i
    G.append({'k': key, 'c': colour, 't': 0, 'n': name}); return len(G) - 1


def lonlat_mask(lon0, lat0, lon1, lat1):
    xs = (np.arange(T.EW) + 0.5) / T.EW * 360 - 180
    lat = T.LATR
    return ((lat[:, None] >= lat0) & (lat[:, None] <= lat1)) & ((xs[None, :] >= lon0) & (xs[None, :] <= lon1))


def realm_of(js, name, g):
    for i, r in enumerate(js['realms']):
        if r['n'] == name:
            return i
    js['realms'].append({'g': g, 'n': name}); return len(js['realms']) - 1


def overlay_main(key, m):
    out = []
    for d, wide in (('rel', False), ('cul', True)):
        p = f'{SITE}/{d}/{key}.png'
        if not os.path.exists(p): out.append(0); continue
        if wide:
            a = np.asarray(Image.open(p).convert('RGB')).astype(np.int64); L = a[..., 0] + (a[..., 1] << 8)
        else:
            L = np.asarray(Image.open(p)).astype(np.int64)
        v = L[m]; v = v[v > 0]
        out.append(int(np.bincount(v).argmax()) if len(v) else 0)
    return out   # [faith, culture]


JOSEON_1450 = None


def fix_era(y, LAND):
    key = F[y]; p = f'{SITE}/eras/{key}.json'; js = J(p)
    log = collections.Counter(); notes = []; new = []   # new: (ent id, parent id)
    ids = None
    def load():
        same, bad = T.check_roundtrip(js, LAND)
        assert same and all(x[1] == x[2] and x[3] == x[4] for x in bad), f'tracing does not reproduce the {key} map; stop'
        return T.read_ids(js)
    def add_ent(name, g, parent):
        r = realm_of(js, name, g)
        js['ents'].append({'n': name, 'r': r, 'k': 0, 'p': 1, 'a': 0, 'x': 1}); i = len(js['ents'])
        new.append((i, parent)); return i
    # FIX-154 Korea
    if y in (1279, 1300, 1400):
        ids = load(); orig = ids.copy()
        name, g = ('Joseon', group('Joseon')) if y == 1400 else ('Goryeo', group('Goryeo'))
        yuan = {i + 1 for i, e in enumerate(js['ents']) if js['realms'][e['r']]['n'] in ('Yuan dynasty', 'Northern Yuan') if e['r'] >= 0}
        m = JOSEON_1450 & np.isin(ids, list(yuan))
        parent = int(np.bincount(ids[m]).argmax())
        i = add_ent(name, g, parent); ids[m] = i; log[f'FIX-154 {name} px'] += int(m.sum())
        notes.append('Korea was ruled by Goryeo (a Yuan vassal from 1270) until 1392 and by Joseon after; it no longer shows as part of the Yuan.'
                     if y < 1400 else 'Korea was ruled by Joseon from 1392; it no longer shows as part of the Northern Yuan.')
    # FIX-155 Java
    if 1450 <= y <= 1530:
        if ids is None:
            ids = load(); orig = ids.copy()
        malay = {i + 1 for i, e in enumerate(js['ents']) if e['n'] == 'Malay sultanates'}
        java = np.isin(ids, list(malay)) & lonlat_mask(105.0, -9.0, 115.8, -5.7)
        west = java & lonlat_mask(105.0, -9.0, 108.6, -5.7)
        east = java & ~west
        if west.any():
            parent = int(np.bincount(ids[west]).argmax())
            i = add_ent('Sunda Kingdom', group('Sunda Kingdom', '#5e8a6e', 'sunda'), parent); ids[west] = i
            log['FIX-155 Sunda px'] += int(west.sum())
        if y <= 1500 and east.any():
            parent = int(np.bincount(ids[east]).argmax())
            i = add_ent('Majapahit', group('Majapahit'), parent); ids[east] = i
            log['FIX-155 Majapahit px'] += int(east.sum())
        notes.append('Java was not Malay sultanates: Majapahit ruled East Java, Madura and Bali until about 1527, and the Hindu Sunda Kingdom West Java until 1579.'
                     if y <= 1500 else 'West Java was the Hindu Sunda Kingdom until 1579.')
    # FIX-156 Denmark in 1000
    if y == 1000:
        for x in js['ents'] + js['realms']:
            if x['n'] == 'Denmark-Norway': x['n'] = 'Denmark (with Norway)'
        log['FIX-156'] += 1
        notes.append('"Denmark-Norway" is the name of the union of 1524-1814; in 1000 Norway was under Danish overlordship.')
    # FIX-157 Alexander speck
    if y == -250:
        ids = load(); orig = ids.copy()
        for i, e in enumerate(js['ents']):
            if e['n'] != 'Empire of Alexander' or not e.get('a'): continue
            m = ids == i + 1
            ring = np.zeros_like(m); ring[1:] |= m[:-1]; ring[:-1] |= m[1:]; ring[:, 1:] |= m[:, :-1]; ring[:, :-1] |= m[:, 1:]
            nb = ids[ring & ~m]; nb = nb[nb > 0]
            if len(nb): ids[m] = int(np.bincount(nb).argmax()); log['FIX-157 px'] += int(m.sum())
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
        try:
            import base64, oxipng
            js['_png'] = base64.b64encode(oxipng.optimize_from_memory(base64.b64decode(js['_png']), level=4)).decode('ascii')
        except ImportError:
            pass
        assert (T.read_ids(js) == ids).all()
        if new:   # new territories: their own main faith and culture, the parent's score and wealth
            p2 = f'{SITE}/data/ovmain.json'; d = J(p2); rows = d['eras'][key]
            for ni, parent in new:
                while len(rows) < ni: rows.append(copy.deepcopy(rows[parent - 1]))
                fth, cul = overlay_main(key, ids == ni)
                if fth: rows[ni - 1][0] = fth
                if cul: rows[ni - 1][1] = cul
            open(p2, 'w', encoding='utf-8').write(json.dumps(d, ensure_ascii=True, separators=(',', ':')))
    js['ents'] = [{k: e[k] for k in ORDER if k in e} for e in js['ents']]
    js['notes'] += [n for n in dict.fromkeys(notes) if n not in js['notes']]
    open(p, 'w', encoding='utf-8').write(json.dumps(js, ensure_ascii=False, separators=(',', ':')))
    return dict(log)


LAND = T.land_mask(f'{SITE}/eras', list(F.values()))
j50 = J(f'{SITE}/eras/{F[1450]}.json'); ids50 = T.read_ids(j50)
JOSEON_1450 = np.isin(ids50, [i + 1 for i, e in enumerate(j50['ents']) if e['n'] == 'Joseon'])
assert JOSEON_1450.sum() > 100
for y in (-250, 1000, 1279, 1300, 1400, 1450, 1453, 1492, 1500, 1530):
    r = fix_era(y, LAND)
    if r: print(y, r, flush=True)
for ix in EMETA['eras']:
    js = J(f"{SITE}/eras/{ix['f']}.json")
    ix['c'] = len(js['notes'])
    ix['n'] = sum(1 for e in js['ents'] if e.get('a') and e['k'] == 0)
    ix['m'] = sum(1 for e in js['ents'] if e.get('a') and e['k'] == 1)
open(f'{SITE}/data/eras.json', 'w', encoding='utf-8').write(json.dumps(EMETA, ensure_ascii=True, separators=(',', ':')))
