"""Realm QC, third pass (27 Oct 2026): Africa, the Americas and South-East Asia before 1800, and a few names
that run past it. Usage: python3 fix_realm_qc3.py <site folder>

Africa
FIX-158 Funj: the Funj Sultanate of Sennar (1504-1821) was missing from the 1530-1750 maps; its lands were drawn as
        the Ottoman Empire (1530-1700) and Ethiopia (1715, 1750). The Ottomans held only the Red Sea coast and, from the
        1550s, Lower Nubia. Funj now has its 1783 outline on those maps (approximate).
FIX-159 The Kingdom of Benin and the Niger delta were labelled "Sotho" (a people of southern Africa) on the
        1783-1880 maps: Benin. A territory labelled "Africa" west of it on the 1783-1848 maps is the Yoruba states.
FIX-160 Egypt was an Ottoman province: on the 1715 map it was a separate realm, and on the 1700 map a sliver of the
        Western Desert was. Both are Ottoman.
FIX-161 The Blemmyes disappear from the record by the 7th century; on the 1279-1400 maps their land is the Beja.
FIX-162 Rozwi on the 1650 map: the Rozvi state was founded in the 1680s. In 1650 the south-west of the Zimbabwe
        plateau was the Butua (Torwa) kingdom.
FIX-163 The Cape on the 1800 map: Britain held the whole Cape Colony from 1795 to 1803; the Dutch settlements were
        part of it.
FIX-164 Zanzibar was not a separate sultanate until 1856. On the 1715-1800 maps the Swahili coast is under Omani
        overlordship, as on the 1700 map: Oman.
FIX-165 Names: the Wattasids and the Zayyanids were sultans, not caliphs. Wattasid Sultanate (1450-1530) and Zayyanid
        Kingdom of Tlemcen (1450-1500), as on the 1279 map.

The Americas
FIX-166 The Hän people of the Yukon were coloured as the Ming Empire on the 1450-1500 maps. They are their own people.
FIX-167 New Amsterdam on the 1700 map: England took New Netherland in 1664 (finally in 1674). It is New York, English.
FIX-168 Teotihuacan (abandoned about 550) and Monte Albán (about 850) were still on the 1279-1400 maps. Their land is
        the Mesoamerican city-states and the Zapotec realm. Classic Veracruz on the same maps is the Totonacs.
FIX-169 Andean and coastal cultures past their dates: Moche (to about 800) on the 900-1210 maps is the Sicán
        (Lambayeque) culture; Chavín (to about 200 BCE) on the 100 BCE-600 CE maps is the Recuay culture; Chorrera
        (to about 300 BCE) on the 250 BCE-600 CE maps is the regional cultures of Ecuador; Olmec (to about 400 BCE) on
        the 323-250 BCE maps is Epi-Olmec.

South-East Asia
FIX-170 800: the inland states of mainland South-East Asia were labelled "Rajput Clans and Small States", a name for
        India. They are the Mon-Khmer peoples, as on the 700 map.
FIX-171 1066 and 1100: "Lavo Kingdom" covered everything from Assam to Laos. Lavo (Lopburi) was a small kingdom on the
        Chao Phraya; the small Lopburi territory on those maps is Lavo, and the rest is the Mon-Khmer peoples (south of
        20.5 N) and the Tibeto-Burman and Mon peoples (north), as on the 1000 map.
FIX-172 1279: one territory of the "Hindu kingdoms of central India" reached Borneo and the Philippines. East of 92 E
        it is the minor Hindu and Buddhist kingdoms, as on the 1300 map.
FIX-173 Taiwan: the Dutch left in 1662 and the Qing took the island's west in 1683. Dutch Formosa on the 1700-1750 maps
        is Qing, and so is the same west coast on the 1783 and 1800 maps. The Middag kingdom on the 1650 map was
        independent, not Qing.
FIX-174 The Austronesian peoples of Taiwan and the islands were coloured as the Habsburg Monarchy on the 1700-1800 maps.
FIX-175 1800: a small piece of Siam was a separate realm; it is the Rattanakosin Kingdom.

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


_SEEN = None


def group(name, colour=None, kind=0):
    global _SEEN
    for i, g in enumerate(G):
        if g['n'] == name:
            return i
    if _SEEN is None:   # realm names as the era maps spell them, which can differ from the registry's own name
        _SEEN = {}
        for f in F.values():
            for r in J(f'{SITE}/eras/{f}.json')['realms']:
                _SEEN.setdefault(r['n'], r['g'])
    if name in _SEEN:
        return _SEEN[name]
    assert colour, f'new realm {name} needs a colour'
    G.append({'k': name.lower(), 'c': colour, 't': kind, 'n': name}); return len(G) - 1


def lonlat_mask(lon0, lat0, lon1, lat1):
    xs = (np.arange(T.EW) + 0.5) / T.EW * 360 - 180
    lat = T.LATR
    return ((lat[:, None] >= lat0) & (lat[:, None] <= lat1)) & ((xs[None, :] >= lon0) & (xs[None, :] <= lon1))


def realm_of(js, name, g):
    for i, r in enumerate(js['realms']):
        if r['n'] == name:
            return i
    js['realms'].append({'g': g() if callable(g) else g, 'n': name}); return len(js['realms']) - 1


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
    return out


def realm_name(js, e):
    return js['realms'][e['r']]['n'] if e['r'] >= 0 else None


def mask_of(year, pred):
    js = J(f'{SITE}/eras/{F[year]}.json'); ids = T.read_ids(js)
    return np.isin(ids, [i + 1 for i, e in enumerate(js['ents']) if e['r'] >= 0 and pred(e, js)])


# colours for realms new to the registry
NEW = {
    'Hän': ('#8f7f62', 1), 'Totonacs': ('#a58a5a', 1), 'Sicán (Lambayeque)': ('#b08850', 1), 'Recuay': ('#9b8566', 1),
    'Regional cultures of Ecuador': ('#a38f63', 1), 'Epi-Olmec': ('#9c7b55', 1), 'Butua (Torwa)': ('#b9855a', 0),
    'Middag Kingdom': ('#8aa06a', 0), 'Wattasid Sultanate': ('#b65f46', 0),
}


def fix_era(y, LAND, MASKS):
    key = F[y]; p = f'{SITE}/eras/{key}.json'; js = J(p)
    log = collections.Counter(); notes = []; new = []
    st = {'ids': None, 'orig': None}

    def ids():
        if st['ids'] is None:
            same, bad = T.check_roundtrip(js, LAND)
            assert same and all(x[1] == x[2] and x[3] == x[4] for x in bad), f'tracing does not reproduce the {key} map; stop'
            st['ids'] = T.read_ids(js); st['orig'] = st['ids'].copy()
        return st['ids']

    def g_for(name):
        c, k = NEW.get(name, (None, 0))
        return group(name, c, k)

    def set_realm(i, name, rename=None, kind=None):
        e = js['ents'][i - 1]
        e['r'] = realm_of(js, name, lambda: g_for(name)); e['x'] = 1
        if rename: e['n'] = rename
        if kind is not None: e['k'] = kind

    def ents(pred):
        return [i + 1 for i, e in enumerate(js['ents']) if e['r'] >= 0 and e.get('a') and pred(e)]

    def add_ent(name, realm, parent, kind=0):
        r = realm_of(js, realm, lambda: g_for(realm))
        js['ents'].append({'n': name, 'r': r, 'k': kind, 'p': 1, 'a': 0, 'x': 1}); i = len(js['ents'])
        new.append((i, parent)); return i

    def take(mask, frm, name, realm, kind=0, tag=''):
        I = ids(); m = mask & np.isin(I, frm)
        if not m.any(): return 0
        parent = int(np.bincount(I[m]).argmax())
        try:
            i = next(i + 1 for i, e in enumerate(js['ents']) if e['n'] == name and realm_name(js, e) == realm)
        except StopIteration:
            i = add_ent(name, realm, parent, kind)
        I[m] = i; log[tag + ' px'] += int(m.sum()); return int(m.sum())

    # ---------------- Africa
    if 1530 <= y <= 1750:   # FIX-158 Funj
        frm = ents(lambda e: realm_name(js, e) in ('Ottoman Empire', 'Ethiopia'))
        if take(MASKS['funj'], frm, 'Funj', 'Funj', tag='FIX-158'):
            notes.append('The Funj Sultanate of Sennar (1504-1821) is on the map; its lands were drawn as Ottoman or Ethiopian.')
    if 1783 <= y <= 1880:   # FIX-159 Benin, Yoruba states
        for i in ents(lambda e: realm_name(js, e) == 'Sotho' and e.get('l') and e['l']['y'] < 2700):
            set_realm(i, 'Benin', rename='Benin'); log['FIX-159 Benin'] += 1
        for i in ents(lambda e: realm_name(js, e) == 'Africa'):
            set_realm(i, 'Yoruba states', rename='Yoruba states'); log['FIX-159 Yoruba'] += 1
        if log['FIX-159 Benin'] or log['FIX-159 Yoruba']:
            notes.append('The Kingdom of Benin and the Niger delta were labelled "Sotho", a people of southern Africa; the land west of it was labelled "Africa".')
    if y in (1700, 1715):   # FIX-160 Egypt
        eg = ents(lambda e: realm_name(js, e) == 'Egypt')
        if y == 1715:
            for i in eg: set_realm(i, 'Ottoman Empire'); log['FIX-160'] += 1
        else:
            ott = ents(lambda e: e['n'] == 'Ottoman Empire' and realm_name(js, e) == 'Ottoman Empire')
            I = ids()
            for i in eg:
                m = I == i; I[m] = ott[0]; log['FIX-160 px'] += int(m.sum())
        notes.append('Egypt was an Ottoman province, not a separate realm.')
    if 1279 <= y <= 1400:   # FIX-161 Beja
        for i in ents(lambda e: realm_name(js, e) == 'Blemmyes'):
            set_realm(i, 'Beja people', rename='Beja'); log['FIX-161'] += 1
        if log['FIX-161']: notes.append('The Blemmyes disappear from the record by the 7th century; their land is the Beja.')
    if y == 1650:   # FIX-162 Butua
        for i in ents(lambda e: realm_name(js, e) == 'Rozwi'):
            set_realm(i, 'Butua (Torwa)', rename='Butua (Torwa)'); log['FIX-162'] += 1
        notes.append('The Rozvi state was founded in the 1680s; in 1650 the south-west of the Zimbabwe plateau was the Butua (Torwa) kingdom.')
    if y == 1800:   # FIX-163 Cape
        cape = ents(lambda e: e['n'] == 'Cape Colony')
        I = ids()
        for i in ents(lambda e: e['n'] == 'Dutch settlements' and realm_name(js, e) == 'Batavian Republic'):
            m = I == i; I[m] = cape[0]; log['FIX-163 px'] += int(m.sum())
        notes.append('Britain held the whole Cape Colony from 1795 to 1803.')
    if 1715 <= y <= 1800:   # FIX-164 Zanzibar
        for i in ents(lambda e: realm_name(js, e) == 'Zanzibar'):
            set_realm(i, 'Oman', rename='Swahili coast'); log['FIX-164'] += 1
        if log['FIX-164']: notes.append('Zanzibar was not a separate sultanate until 1856; the Swahili coast was under Omani overlordship.')
    if 1450 <= y <= 1530:   # FIX-165 names
        for i in ents(lambda e: realm_name(js, e) in ('Wattasid Caliphate', 'Watassid Morocco')):
            set_realm(i, 'Wattasid Sultanate', rename='Wattasid Sultanate'); log['FIX-165'] += 1
        for i in ents(lambda e: realm_name(js, e) == 'Zayyanid Caliphate'):
            set_realm(i, 'Zayyanid Kingdom of Tlemcen', rename='Zayyanid Kingdom of Tlemcen'); log['FIX-165'] += 1
        if log['FIX-165']: notes.append('The Wattasids and the Zayyanids were sultans, not caliphs.')
    # ---------------- the Americas
    if 1450 <= y <= 1500:   # FIX-166 Hän
        for i in ents(lambda e: realm_name(js, e) == 'Ming Empire' and e.get('l') and e['l']['x'] < 2000):
            set_realm(i, 'Hän', kind=1); log['FIX-166'] += 1
        if log['FIX-166']: notes.append('The Hän people of the Yukon were coloured as the Ming Empire.')
    if y == 1700:   # FIX-167 New York
        for i in ents(lambda e: e['n'] == 'New Amsterdam'):
            set_realm(i, 'Kingdom of England', rename='New York'); log['FIX-167'] += 1
        notes.append('England took New Netherland in 1664 (finally in 1674): New York.')
    if 1279 <= y <= 1400:   # FIX-168 Mesoamerica
        for i in ents(lambda e: realm_name(js, e) == 'Teotihuacan'):
            set_realm(i, 'Mesoamerican city-states', rename='Valley of Mexico city-states'); log['FIX-168'] += 1
        for i in ents(lambda e: realm_name(js, e) == 'Monte Albán'):
            set_realm(i, 'Zapotec Empire', rename='Valley of Oaxaca', kind=0); log['FIX-168'] += 1
        for i in ents(lambda e: realm_name(js, e) == 'Veracruz civilization'):
            set_realm(i, 'Totonacs', rename='Totonacs'); log['FIX-168'] += 1
        if log['FIX-168']: notes.append('Teotihuacan (abandoned about 550), Monte Albán (about 850) and Classic Veracruz are replaced by the peoples of this date.')
    for old, new_, y0, y1, note in (
        ('Moche', 'Sicán (Lambayeque)', 900, 1210, 'The Moche culture ended about 800; the north coast is the Sicán (Lambayeque) culture.'),
        ('Chavin', 'Recuay', -100, 600, 'The Chavín culture ended about 200 BCE; the highlands are the Recuay culture.'),
        ('Chorrera', 'Regional cultures of Ecuador', -250, 600, 'The Chorrera culture ended about 300 BCE; Ecuador is the regional cultures that followed it.'),
        ('Olmec', 'Epi-Olmec', -323, -250, 'The Olmec culture ended about 400 BCE; the Gulf coast is Epi-Olmec.'),
    ):   # FIX-169
        if y0 <= y <= y1:
            hit = ents(lambda e, o=old: realm_name(js, e) == o)
            for i in hit:
                set_realm(i, new_, rename=new_); log['FIX-169'] += 1
            if hit: notes.append(note)
    # ---------------- South-East Asia
    if y == 800:   # FIX-170
        for i in ents(lambda e: realm_name(js, e) == 'Rajput Clans and Small States' and e.get('l') and e['l']['x'] > 6200):
            set_realm(i, 'Mon-Khmer peoples', rename='Mon-Khmer peoples', kind=1); log['FIX-170'] += 1
        notes.append('The inland states of mainland South-East Asia were labelled "Rajput Clans and Small States", a name for India.')
    if y in (1066, 1100):   # FIX-171
        big = ents(lambda e: realm_name(js, e) == 'Lavo Kingdom' and e['n'] == 'Lavo Kingdom')
        north = lonlat_mask(80, 20.5, 115, 40)
        take(north, big, 'Tibeto-Burman and Mon peoples', 'Tibeto-Burman and Mon peoples', kind=1, tag='FIX-171')
        take(~north, big, 'Mon-Khmer peoples', 'Mon-Khmer peoples', kind=1, tag='FIX-171')
        for i in ents(lambda e: realm_name(js, e) == 'Lopburi Kingdom'):
            set_realm(i, 'Lavo Kingdom', rename='Lavo (Lopburi)')
        notes.append('Lavo (Lopburi) was a small kingdom on the Chao Phraya, not the whole interior of mainland South-East Asia.')
    if y == 1279:   # FIX-172
        hk = ents(lambda e: realm_name(js, e) == 'Hindu kingdoms of central India')
        take(lonlat_mask(92, -15, 140, 30), hk, 'minor Hindu and Buddhist kingdoms', 'minor Hindu and Buddhist kingdoms', tag='FIX-172')
        notes.append('Borneo and the Philippines were part of "Hindu kingdoms of central India"; they are the minor Hindu and Buddhist kingdoms.')
    if 1700 <= y <= 1800:   # FIX-173 Taiwan, FIX-174 Austronesians
        for i in ents(lambda e: realm_name(js, e) == 'Habsburg Monarchy' and e['k'] == 1 and e.get('l') and e['l']['x'] > 6000):
            set_realm(i, 'Austronesian peoples'); log['FIX-174'] += 1
        if log['FIX-174']: notes.append('The Austronesian peoples of Taiwan and the islands were coloured as the Habsburg Monarchy.')
        I = ids()
        frm = [i for i in range(1, len(js['ents']) + 1) if js['ents'][i - 1]['r'] >= 0 and realm_name(js, js['ents'][i - 1]) in ('Dutch Republic', 'Austronesian peoples')]
        if take(MASKS['formosa'], frm, 'Taiwan', 'Qing Empire', tag='FIX-173'):
            notes.append('The Dutch left Taiwan in 1662 and the Qing took the west of the island in 1683.')
    if y == 1650:
        for i in ents(lambda e: e['n'] == 'Middag Kingdom'):
            set_realm(i, 'Middag Kingdom'); log['FIX-173'] += 1
    if y == 1800:   # FIX-175
        for i in ents(lambda e: realm_name(js, e) == 'Siam'):
            set_realm(i, 'Rattanakosin Kingdom'); log['FIX-175'] += 1
    if not log:
        return None
    if st['ids'] is not None:
        I, orig = st['ids'], st['orig']
        changed = I != orig
        touched = set(np.unique(orig[changed]).tolist()) | set(np.unique(I[changed]).tolist()); touched.discard(0)
        for i in touched:
            e = js['ents'][i - 1]; a, b, l = T.stats(I, i)
            e['a'] = a
            for k, v in (('b', b), ('l', l)):
                if v is None: e.pop(k, None)
                else: e[k] = v
        js['borders'] = T.borders(I, LAND)
        js['_png'] = T.write_ids(I)
        try:
            import base64, oxipng
            js['_png'] = base64.b64encode(oxipng.optimize_from_memory(base64.b64decode(js['_png']), level=4)).decode('ascii')
        except ImportError:
            pass
        assert (T.read_ids(js) == I).all()
        if new:
            p2 = f'{SITE}/data/ovmain.json'; d = J(p2); rows = d['eras'][key]
            for ni, parent in new:
                while len(rows) < ni: rows.append(copy.deepcopy(rows[parent - 1]))
                fth, cul = overlay_main(key, I == ni)
                if fth: rows[ni - 1][0] = fth
                if cul: rows[ni - 1][1] = cul
            open(p2, 'w', encoding='utf-8').write(json.dumps(d, ensure_ascii=True, separators=(',', ':')))
    # drop realms no territory uses any more
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
MASKS = {
    'funj': mask_of(1783, lambda e, js: e['n'] == 'Funj'),
    'formosa': mask_of(1700, lambda e, js: e['n'] == 'Dutch Formosa'),
}
assert MASKS['funj'].sum() > 1000 and MASKS['formosa'].sum() > 50
years = sorted({y for y in F if -323 <= y <= 1880})
for y in years:
    r = fix_era(y, LAND, MASKS)
    if r: print(y, r, flush=True)
open(f'{SITE}/data/eras.json', 'w', encoding='utf-8').write(json.dumps(EMETA, ensure_ascii=True, separators=(',', ':')))
for ix in EMETA['eras']:
    js = J(f"{SITE}/eras/{ix['f']}.json")
    ix['c'] = len(js['notes'])
    ix['n'] = sum(1 for e in js['ents'] if e.get('a') and e['k'] == 0)
    ix['m'] = sum(1 for e in js['ents'] if e.get('a') and e['k'] == 1)
open(f'{SITE}/data/eras.json', 'w', encoding='utf-8').write(json.dumps(EMETA, ensure_ascii=True, separators=(',', ':')))
