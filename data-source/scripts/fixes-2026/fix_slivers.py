"""Stray specks and leftover realms on the era maps (25 Oct 2026). Usage: python3 fix_slivers.py <site folder> [era keys]

The era maps were rasterised from source maps whose neighbouring outlines did not always line up, so some realms have
tiny detached pieces lying on a neighbour's coast or just inside its border. Each draws a small ring of border line,
which shows as dark dashes and specks along coasts (for example around Iceland and Norway in 1500).

FIX-127 specks: a detached piece of a realm, at most 3 map pixels (about 300 km2), that is not the realm's main body
        and whose land neighbours are at least 75% one other realm, joins the neighbouring territory it touches most.
        Pieces near the known real coastal enclaves and forts listed in KEEP are left alone, and a piece with no land
        neighbour (an island) is never moved.
FIX-128 Scandinavia: realms left over from the source maps. 1492 and 1530 kept fragments of a Kalmar Union beside
        Denmark-Norway and Sweden (the union had broken up in 1523, and the 1492 map shows Denmark-Norway and Sweden);
        1500 kept fragments of Denmark-Norway inside the Kalmar Union it shows. The leftover pieces join the territory
        around them, and any that touch no other land join the realm named below.
FIX-129 1066: the County of Edessa and the Principality of Antioch were founded only in 1098, in the First Crusade.
        Their pieces on the 1066 map join the Byzantine territory around them.
FIX-130 1783 and 1800: the Electorate of Hanover was labelled Mecklenburg-Strelitz, and the real Mecklenburg-Strelitz
        (in the east of Mecklenburg) was part of Mecklenburg-Schwerin. The large territory now joins Hanover, and
        Mecklenburg-Strelitz takes the same outline it has on the 1815 map.
FIX-131 1715 and 1750: a territory labelled Lubeck covered Holstein and the two Mecklenburg duchies (about 30,000 km2;
        the free city and prince-bishopric of Lubeck were a few hundred). Holstein, Mecklenburg-Schwerin and
        Mecklenburg-Strelitz take the outlines they have on the 1783 map; what is left keeps the name Lubeck.

Borders, areas and labels are re-traced with the s6_eras.py code in ../derive-2026/era_tools.py, after checking that it
reproduces each unchanged map exactly. Afterwards rebuild the search index (build_realm_index.py)."""
import collections, copy, json, math, os, sys
import numpy as np
from scipy import ndimage
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'derive-2026'))
import era_tools as T

SITE = sys.argv[1]
ONLY = set(sys.argv[2:])
J = lambda p: json.load(open(p, encoding='utf-8'))
S4 = np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]])
ORDER = ['n', 'r', 'k', 'p', 'a', 'b', 'l', 'w', 'a3', 'x', 'c']

# real coastal enclaves, presidios and forts (lat, lon): pieces within 0.35 degrees are never moved
KEEP = [(35.89, -5.32), (35.29, -2.94), (35.17, -4.30), (35.21, -3.89), (36.14, -5.35), (50.95, 1.86), (35.70, -0.63),
        (33.25, -8.50), (35.78, -5.81), (22.20, 113.55), (15.50, 73.83), (20.42, 72.83), (20.71, 70.98), (2.19, 102.25),
        (22.30, 114.17), (12.80, 45.03), (42.46, 1.98), (51.44, 4.93), (45.97, 8.97), (47.70, 8.69), (43.74, 7.42),
        (41.90, 12.45), (43.94, 12.45), (31.60, -8.0), (34.03, -6.83), (32.30, -9.24), (31.51, -9.77), (30.42, -9.60),
        (5.10, -1.25), (5.20, -1.70), (6.10, 1.20), (14.67, -17.43), (-8.84, 13.23), (-25.97, 32.57), (-15.03, 40.73)]
LEFTOVER = {  # era: [(leftover realm, realm that takes any piece with no land neighbour)]
    '1492': [('Kalmar Union', 'Denmark-Norway')],
    '1500': [('Denmark-Norway', 'Kalmar Union')],
    '1530': [('Kalmar Union', 'Denmark-Norway')],
    '1066': [('County of Edessa', 'Byzantine Empire'), ('Principality of Antioch', 'Byzantine Empire')],
}


def latlon(x, y):
    lat = float(T.LATR[min(T.EH - 1, max(0, int(y)))])
    return lat, (x + 0.5) / T.EW * 360 - 180


def near_keep(x, y):
    lat, lon = latlon(x, y)
    return any(abs(lat - a) < 0.35 and abs(lon - b) < 0.35 / max(0.2, math.cos(math.radians(lat))) for a, b in KEEP)


def neighbours(ids, R, m, sl):
    """land entities and realms on the 4-neighbour ring around mask m (in slice sl)."""
    ring = ndimage.binary_dilation(m, S4) & ~m
    return ids[sl][ring], R[sl][ring]


def piece_target(ids, R, m, sl, share_min):
    ni, nr = neighbours(ids, R, m, sl)
    land = nr >= 0
    if not land.any(): return None
    cnt = collections.Counter(nr[land].tolist()); top, tn = cnt.most_common(1)[0]
    if tn / land.sum() < share_min: return None
    ent = collections.Counter(ni[land & (nr == top)].tolist()).most_common(1)[0][0]
    return int(ent)


def realm_pieces(R, r, box=None):
    """connected pieces of realm r: list of (slice, mask, size)."""
    H, W = R.shape
    x0, y0, x1, y1 = box if box else (0, 0, W, H)
    x0, y0, x1, y1 = max(0, x0 - 1), max(0, y0 - 1), min(W, x1 + 1), min(H, y1 + 1)
    lab, n = ndimage.label(R[y0:y1, x0:x1] == r, S4)
    out = []
    for c, sl in enumerate(ndimage.find_objects(lab), 1):
        if sl is None: continue
        ya, yb = max(0, sl[0].start - 1), min(y1 - y0, sl[0].stop + 1)
        xa, xb = max(0, sl[1].start - 1), min(x1 - x0, sl[1].stop + 1)
        m = lab[ya:yb, xa:xb] == c
        out.append(((slice(y0 + ya, y0 + yb), slice(x0 + xa, x0 + xb)), m, int(m.sum())))
    return out


def fix_era(key, meta, LAND, js1815):
    p = f'{SITE}/eras/{key}.json'; js = J(p)
    same, bad = T.check_roundtrip(js, LAND)
    # a few territories have hand-placed labels (for example Song Empire in 1200); only those may differ, and they are kept
    hand = {x[0] for x in bad if x[1] == x[2] and x[3] == x[4]}
    assert same and len(hand) == len(bad), f'tracing does not reproduce the {key} map; stop'
    ids = T.read_ids(js); orig = ids.copy()
    rname = [r['n'] for r in js['realms']]
    def rOf_arr():
        a = np.array([-1] + [e['r'] for e in js['ents']], dtype=np.int64); R = a[ids]; R[ids == 0] = -2; return R
    log = collections.Counter(); notes = []; new_ents = []
    by_ent = {e['n']: i + 1 for i, e in enumerate(js['ents'])}
    realm_ix = lambda n: rname.index(n)

    # FIX-130 Hanover / Mecklenburg-Strelitz (1783, 1800)
    if key in ('1783', '1800'):
        st, han, sch = by_ent['Mecklenburg-Strelitz'], by_ent['Hanover'], by_ent['Mecklenburg-Schwerin']
        assert js['ents'][st - 1]['b'][0] < 2140, 'Mecklenburg-Strelitz is not the western territory; stop'
        n1 = int((ids == st).sum()); ids[ids == st] = han
        ids15 = T.read_ids(js1815)
        st15 = next(i + 1 for i, e in enumerate(js1815['ents']) if e['n'] == 'Mecklenburg-Strelitz')
        m = (ids15 == st15) & (ids == sch)
        ids[m] = st; n2 = int(m.sum())
        notes.append('The Electorate of Hanover was labelled Mecklenburg-Strelitz; Mecklenburg-Strelitz is now drawn in the east of Mecklenburg, as on the 1815 map.')
        log['FIX-130 Hanover px'] += n1; log['FIX-130 Strelitz px'] += n2

    # FIX-131 Holstein and Mecklenburg (1715, 1750)
    if key in ('1715', '1750'):
        lub = by_ent['Lübeck']
        js83 = J(f'{SITE}/eras/1783.json'); ids83 = T.read_ids(js83)
        for name in ('Holstein', 'Mecklenburg-Schwerin', 'Mecklenburg-Strelitz'):
            i83 = next(i + 1 for i, e in enumerate(js83['ents']) if e['n'] == name)
            g = js83['realms'][js83['ents'][i83 - 1]['r']]['g']
            m = (ids83 == i83) & (ids == lub)
            if name not in rname: js['realms'].append({'g': g, 'n': name}); rname.append(name)
            js['ents'].append({'n': name, 'r': rname.index(name), 'k': 0, 'p': 1, 'a': 0, 'x': 1}); ni = len(js['ents'])
            new_ents.append((ni, lub)); ids[m] = ni; log[f'FIX-131 {name} px'] += int(m.sum())
        log['FIX-131 Lubeck px left'] += int((ids == lub).sum())
        notes.append('Holstein and the duchies of Mecklenburg-Schwerin and Mecklenburg-Strelitz were drawn as one territory labelled Lübeck; they now have the outlines of the 1783 map.')

    # FIX-128 / FIX-129 leftover realms
    for old, heir in LEFTOVER.get(key, []):
        if old not in rname: continue
        r = realm_ix(old); R = rOf_arr()
        for sl, m, s in sorted(realm_pieces(R, r), key=lambda t: t[2]):
            R = rOf_arr()
            t = piece_target(ids, R, m & (R[sl] == r), sl, 0.0)
            if t is not None:
                ids[sl][m & (ids[sl] != 0) & (R[sl] == r)] = t; log[f'{old} px to neighbours'] += s
        left = [i + 1 for i, e in enumerate(js['ents']) if e['r'] == r and (ids == i + 1).any()]
        if left:
            hr = realm_ix(heir)
            for i in left:
                e = js['ents'][i - 1]; e['r'] = hr; e['n'] = heir; e['x'] = 1
                log[f'{old} island px to {heir}'] += int((ids == i).sum())
        if key == '1066': notes.append(f'The {old} was founded only in 1098; its pieces on this map are Byzantine.')
    # FIX-127 specks
    R = rOf_arr()
    bb = {}
    for e in js['ents']:
        if e['r'] < 0 or not e.get('b'): continue
        b = e['b']; o = bb.get(e['r'])
        bb[e['r']] = b if o is None else [min(o[0], b[0]), min(o[1], b[1]), max(o[2], b[2]), max(o[3], b[3])]
    moves = []
    for r, b in bb.items():
        pieces = realm_pieces(R, r, b)
        if len(pieces) < 2: continue
        main = max(s for _, _, s in pieces)
        for sl, m, s in pieces:
            if s > 3 or s == main: continue
            if near_keep(sl[1].start, sl[0].start): log['kept (known enclave)'] += 1; continue
            t = piece_target(ids, R, m, sl, 0.75)
            if t is None: continue
            moves.append((sl, m, t, s))
    for sl, m, t, s in moves:
        ids[sl][m] = t; log['FIX-127 specks'] += 1; log['FIX-127 px'] += s
    changed = ids != orig
    if not changed.any() and not any('island' in k for k in log): return None
    touched = set(np.unique(orig[changed]).tolist()) | set(np.unique(ids[changed]).tolist()); touched.discard(0)
    for i in touched:
        e = js['ents'][i - 1]; a, b, l = T.stats(ids, i)
        if e['n'] in hand and a and e.get('l'): l = e['l']
        e['a'] = a
        for k, v in (('b', b), ('l', l)):
            if v is None: e.pop(k, None)
            else: e[k] = v
    js['ents'] = [{k: e[k] for k in ORDER if k in e} for e in js['ents']]
    js['borders'] = T.borders(ids, LAND)
    js['notes'] += notes
    js['_png'] = T.write_ids(ids)
    try:   # the deployed rasters are oxipng-compressed (level 4); without it the files are about 40% larger
        import base64, oxipng
        js['_png'] = base64.b64encode(oxipng.optimize_from_memory(base64.b64decode(js['_png']), level=4)).decode('ascii')
    except ImportError:
        pass
    assert (T.read_ids(js) == ids).all()
    open(p, 'w', encoding='utf-8').write(json.dumps(js, ensure_ascii=False, separators=(',', ':')))
    if new_ents:   # new territories take their parent's row in the per-territory summaries
        p2 = f'{SITE}/data/ovmain.json'
        if os.path.exists(p2):
            d = J(p2); rows = d['eras'][key]
            for ni, parent in new_ents:
                while len(rows) < ni: rows.append(copy.deepcopy(rows[parent - 1]))
            open(p2, 'w', encoding='utf-8').write(json.dumps(d, ensure_ascii=True, separators=(',', ':')))
    return dict(log), len(js['borders'])


meta = J(f'{SITE}/data/eras.json')
LAND = T.land_mask(f'{SITE}/eras', [e['f'] for e in meta['eras']])
js1815 = J(f'{SITE}/eras/1815.json')
total = collections.Counter()
for e in meta['eras']:
    if ONLY and e['f'] not in ONLY: continue
    r = fix_era(e['f'], meta, LAND, js1815)
    if r:
        total.update(r[0]); print(e['f'], r[0], 'borders', r[1], flush=True)
# the era index keeps each map's counts of states, peoples and notes
for ix in meta['eras']:
    js = J(f"{SITE}/eras/{ix['f']}.json")
    ix['c'] = len(js['notes'])
    ix['n'] = sum(1 for e in js['ents'] if e.get('a') and e['k'] == 0)
    ix['m'] = sum(1 for e in js['ents'] if e.get('a') and e['k'] == 1)
open(f'{SITE}/data/eras.json', 'w', encoding='utf-8').write(json.dumps(meta, ensure_ascii=True, separators=(',', ':')))
print('TOTAL', dict(total))
