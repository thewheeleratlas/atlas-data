"""Era borders: rasterize historical border snapshots onto the atlas land mask.

Inputs : historical-basemaps GeoJSON snapshots (GPL-3.0) + Natural Earth admin-0 for 2026
Outputs: site/data/eras.json            (era index, global realm registry + colours)
         site/eras/<key>.png            (4096-wide entity-id raster, R=low byte, G=high byte)
         site/eras/<key>.json           (entities, realms, labels, border polylines)
"""
import cv2, sys, re, unicodedata, collections
sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.abspath(__file__)))
from common import *
from scipy import ndimage

HB = os.environ.get('HHA_HB', os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'upstream', 'historical-basemaps')))
ER = 2                      # era raster = W / ER
EW, EH = W // ER, H // ER   # 4096 x 2111
os.makedirs(f'{OUT}/eras', exist_ok=True); os.makedirs(f'{OUT}/data', exist_ok=True)

land8 = np.load(f'{WORK}/land.npy').astype(np.float32) / 255
LAND = cv2.resize(land8, (EW, EH), interpolation=cv2.INTER_AREA) > 0.5
del land8
LATR = inv_lat(np.arange(EH) + 0.5, EW)
# km^2 per era pixel (Miller): dA = R^2 cos(phi) dlambda dphi, dphi = dy * cos(0.8 phi)
R = 6371.0
dl = 2 * np.pi / EW
PIXKM = (R * R * np.cos(np.radians(LATR)) * dl * dl * np.cos(np.radians(0.8 * LATR))).astype(np.float64)

# ------------------------------------------------------------------ naming
def clean(s):
    if s is None: return ''
    s = str(s).strip()
    return '' if s in ('?', '-', 'None') else re.sub(r'\s+', ' ', s)

def norm(s):
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode().lower()
    return re.sub(r'\s+', ' ', re.sub(r'[^a-z0-9 ]', ' ', s)).strip()

ALIASES = [
    (r'\byuan dynasty\b', 'mongol'),
    (r'\(taiwan\)|^taiwan$', 'taiwan'),
    (r'^jin empire$', 'jurchen jin'),
    (r'\bsouthern qi\b', 'china'),
    (r'\bgreat horde\b', 'golden horde'),
    (r'\b(east germany|german democratic)\b', 'gdr'),
    (r'\b(east francia|holy roman|german empire|germany|german confederation|north german|weimar|third reich)\b', 'germany'),
    (r'\b(eastern roman|byzantine)\b', 'byzantium'),
    (r'\b(western roman empire|roman empire|roman republic)\b|^rome$', 'rome'),
    (r'\b(netherlands|neterlands|dutch|batavian)\b', 'netherlands'),
    (r'\b(united states)\b|^usa$', 'usa'),
    (r'\b(united kingdom|great britain|england|english territory|kingdom of england|british)\b|^uk$', 'britain'),
    (r'\bnorthern yuan\b', 'mongol'),
    (r'\b(golden horde|white horde|blue horde)\b', 'golden horde'),
    (r'\b(manchu|qing)\b', 'china'),
    (r'\b(shogunate|ashikaga|kamakura)\b', 'japan'),
    (r'\bmorocc\w*', 'morocco'),
    (r'\b(white sheep|aq qoyunlu)\b', 'aq qoyunlu'),
    (r'\bbrazil\b', 'brazil'),
    (r'\bserbia\w*', 'serbia'),
    (r'\bromania\w*', 'romania'),
    (r'\bmali\b', 'mali'),
    (r'\bmexic\w*', 'mexico'),
    (r'\b(france|french|frankish|franks|west francia|carolingian)\b', 'france'),
    (r'\b(russia|russian|muscovy|moscow|ussr|soviet|tsardom)\b', 'russia'),
    (r'\b(ottoman|turkey)\b', 'ottoman'),
    (r'\b(spain|spanish|castil\w*|castille|new spain)\b', 'spain'),
    (r'\bportug\w*', 'portugal'),
    (r'\b(netherlands|neterlands|dutch|batavian)\b', 'netherlands'),
    (r'\b(denmark|danemark|danish)\b', 'denmark'),
    (r'\b(sweden|swedish)\b', 'sweden'),
    (r'\b(austria|austrian|habsburg|austro)\w*', 'austria'),
    (r'\b(prussia|brandenburg)\b', 'prussia'),
    (r'\b(poland|polish)\b', 'poland'),
    (r'\b(ming|qing|song|tang|yuan|sui|han|zhou|shang|jin|china|chinese)\b', 'china'),
    (r'\b(japan|japanese|yamato|tokugawa)\b', 'japan'),
    (r'\bmughal', 'mughal'),
    (r'\b(achaemenid|sasanian|sassanid|safavid|persia|persian|iran|parthia\w*|qajar|afsharid)\b', 'persia'),
    (r'\b(mongol|great khanate)\b', 'mongol'),
    (r'\b(umayyad|abbasid|rashidun)\b', 'caliphate'),
    (r'\b(egypt|ptolemaic)\b', 'egypt'),
    (r'\b(ethiopia|abyssinia|axum|aksum)\b', 'ethiopia'),
    (r'\b(italy|italian|sardinia|savoy)\b', 'italy'),
    (r'\bhungar\w*', 'hungary'),
    (r'\b(empire of alexander|macedon\w*)\b', 'macedon'),
    (r'\bcarthag\w*', 'carthage'),
    (r'\binca\b', 'inca'),
    (r'\baztec', 'aztec'),
    (r'^(india|republic of india)$', 'india'),
]
PRESET = {
    'britain': '#b3302c', 'france': '#2d4e9c', 'spain': '#d2a93a', 'portugal': '#2c7a58',
    'netherlands': '#df7a2a', 'denmark': '#b4485a', 'sweden': '#2b6f93', 'russia': '#3c6c38',
    'ottoman': '#b0602e', 'germany': '#5f6064', 'gdr': '#8a8b90', 'austria': '#e3d6ad',
    'prussia': '#2e3d5c', 'poland': '#c23a5b', 'rome': '#7b2b78', 'byzantium': '#6a3a9c',
    'china': '#d8b552', 'japan': '#c54a4a', 'mughal': '#2f8a4c', 'persia': '#2b8987',
    'mongol': '#5b7fa3', 'caliphate': '#3f7a3c', 'egypt': '#c79a42', 'usa': '#3a5ca8',
    'ethiopia': '#7c8a2a', 'italy': '#4f9d68', 'hungary': '#8a5636', 'macedon': '#d09a36',
    'carthage': '#8a3636', 'inca': '#c8772a', 'aztec': '#2f9787', 'india': '#e0873a',
}
STATE_PAL = ['#a8322d', '#2f5597', '#3d7a3a', '#c9a13b', '#6b3f8f', '#2f8584', '#cc6d2c', '#7a2839',
             '#5b93c9', '#8a8f3a', '#c26a86', '#5c6f8a', '#8a5a36', '#87a843', '#3d3f86', '#c7ae78',
             '#3fa0b0', '#8f4f7a', '#b04a2a', '#4f9a6f', '#d0894a', '#6f7f3a', '#a04f5f', '#4a6fa8',
             '#9a7a2a', '#2f6f5f', '#b85a7a', '#5a8f9a', '#7a5a9a', '#a87a5a', '#4a7a2a', '#c0503a',
             '#3a5a7a', '#8aa05a', '#a05a3a', '#6a8ac0']
PEOPLE_PAL = ['#9c8f6a', '#8a9a7a', '#a08a7a', '#7f8f9a', '#a89a6a', '#8a7a8f', '#9aa08a', '#b09a82',
              '#7a8a7a', '#a0907a', '#8f9f8f', '#9a8a6a', '#8a8a9a', '#a59576']

def realm_key(name):
    n = norm(name)
    for rx, k in ALIASES:
        if re.search(rx, n): return k
    return n

PEOPLE_KW = ['hunter', 'gatherer', 'culture', 'tribes', 'tribe', 'peoples', 'people', 'farmers', 'nomad',
             'pastoral', 'forager', 'aboriginal', 'homo ', 'neanderthal', 'complex', 'focus', 'mesolithic',
             'neolithic', 'fishers', 'herders', 'hunters', 'cultures', 'horizon', 'tradition']
STATE_KW = ['empire', 'kingdom', 'khanate', 'caliphate', 'sultanate', 'emirate', 'dynasty', 'republic',
            'confedera', 'duchy', 'principality', 'colony', 'viceroyalty', 'state', 'united', 'territory',
            'protectorate', 'crown', 'shogunate', 'imamate', 'sheikh', 'raj', 'company', 'federation', 'union',
            'polity', 'realm', 'league', 'commonwealth', 'dominion', 'mandate', 'ussr', 'reich', 'tsardom',
            'beylik', 'county', 'march', 'satrap', 'chiefdoms and states', 'city-states', 'city states']
STRONG_STATE = ['empire', 'kingdom', 'khanate', 'caliphate', 'sultanate']
AMERICAS_STATES = set(map(norm, ['mexico', 'brazil', 'peru', 'chile', 'argentina', 'colombia', 'gran colombia', 'venezuela',
    'bolivia', 'paraguay', 'uruguay', 'ecuador', 'haiti', 'canada', 'guatemala', 'honduras', 'el salvador', 'nicaragua',
    'costa rica', 'dominican republic', 'cuba', 'jamaica', 'bahamas', 'belize', 'guyana', 'suriname', 'french guiana',
    'british guiana', 'dutch guiana', "rupert's land", 'new france', 'louisiana', 'alaska', 'greenland', 'labrador',
    'newfoundland', 'quebec', 'upper canada', 'lower canada', 'oregon country', 'texas', 'california', 'florida',
    'puerto rico', 'barbados', 'trinidad', 'new granada', 'rio de la plata', 'la plata', 'panama', 'hispaniola',
    'saint domingue', 'new netherland', 'new sweden', 'acadia', 'virginia', 'massachusetts', 'thirteen colonies',
    'central america', 'federal republic of central america', 'confederate states', 'aztec empire', 'inca empire']))
POWER_SUFFIX = {'uk': 'United Kingdom', 'gb': 'United Kingdom', 'fr': 'France', 'france': 'France', 'portugal': 'Portugal',
                'spain': 'Spain', 'netherlands': 'Netherlands', 'nl': 'Netherlands', 'i': 'Italy', 'italy': 'Italy',
                'belgium': 'Belgium', 'germany': 'German Empire', 'denmark': 'Denmark', 'us': 'United States',
                'usa': 'United States', 'japan': 'Empire of Japan', 'russia': 'Russia', 'sweden': 'Sweden'}

PEOPLE_NAMES = set(map(norm, ['Khoisan', 'Austronesians', 'Saami', 'Samis', 'Sami', 'Ainu', 'Ainus', 'Siberians', 'Arabs',
    'Thule', 'Dorset', 'Inuit', 'Inupiat', 'Inupiaq', 'Berbers', 'Berber Tribes', 'Celts', 'Slavs', 'Balts', 'Ests', 'Chuds',
    'Polynesians', 'Melanesians', 'Papuans', 'Bedouins', 'Tuareg', 'Pygmies', 'Maori', 'Semites', 'Dravidians',
    'Afanasevo', 'Andronovo', 'Beaker', 'Saka', 'Scythians', 'Sarmatians', 'Cimerians', 'Cimmerians', 'Thracians',
    'Iberians', 'Celtiberians', 'Ligurians', 'Picts', 'Frisians', 'Saxons', 'Peshemegs', 'Blemmyes', 'Oromo',
    'Basques', 'Lapps', 'Samoyeds', 'Yakuts', 'Evenks', 'Chukchi', 'Koryaks', 'Bashkirs', 'Cumans', 'Pechenegs',
    'Polovtsy', 'Magyars', 'Germans', 'Goths', 'Vandals', 'Huns', 'Alans', 'Kurds', 'Somali', 'Somalis', 'Masai',
    'Zulu', 'Hottentots', 'Bushmen', 'Tasmanians', 'Uralic', 'Proto-Indo-Europeans', 'Indo-Europeans', 'Bantu',
    'Siberian tribes', 'Arameans', 'Amorites', 'Canaan']))
SOUTH_ASIA = lambda lon, lat: 62 < lon < 98 and 4 < lat < 37

def classify(name, subj, year, lon, lat, ptype):
    n = norm(name)
    if any(k in n for k in STRONG_STATE): return 0
    if realm_key(name) in PRESET: return 0
    if n in PEOPLE_NAMES: return 1
    if year < 1000 and re.fullmatch(r'[a-z]+(ians|ans|ites|ii)', n) and not SOUTH_ASIA(lon, lat): return 1
    if any(k in n for k in PEOPLE_KW): return 1
    if ptype == 'culture': return 1
    if any(k in n for k in STATE_KW): return 0
    if subj and norm(subj) != n: return 0
    if year < 1880:
        americas = lon < -30
        australia = 110 < lon < 156 and lat < -9
        if australia and year >= 1500: return 1
        if americas and n not in AMERICAS_STATES: return 1
    if year < -3000: return 1
    return 0

# ------------------------------------------------------------------ geometry
def ring_area(r):
    a = np.asarray(r, dtype=np.float64)
    if len(a) < 3: return 0.0
    return abs(np.sum(a[:-1, 0] * a[1:, 1] - a[1:, 0] * a[:-1, 1])) / 2

def feat_polys(geom):
    if geom is None: return []
    return rings_of(geom)

def poly_pts(rings):
    out = []
    for r in rings:
        a = np.asarray(r, dtype=np.float64)
        if a.ndim != 2 or len(a) < 3: continue
        x, y = proj(a[:, 0], a[:, 1], EW)
        out.append(np.round(np.stack([x, y], 1) * 16).astype(np.int32))
    return out

def rasterize(items):
    """items: list of (value, polys). Larger polygons first so small ones sit on top."""
    lab = np.full((EH, EW), -1, np.int32)
    order = []
    for val, polys in items:
        for p in polys:
            order.append((ring_area(p[0]) if p else 0, val, p))
    order.sort(key=lambda t: -t[0])
    for _, val, p in order:
        pts = poly_pts(p)
        if pts: cv2.fillPoly(lab, pts, int(val), lineType=cv2.LINE_8, shift=4)
    return lab

def fill_coasts(lab, D=8):
    covered = lab >= 0
    dist, (iy, ix) = ndimage.distance_transform_edt(~covered, return_indices=True)
    out = lab.copy()
    m = (~covered) & LAND & (dist <= D)
    out[m] = lab[iy[m], ix[m]]
    out[~LAND] = -1
    out[(out < 0) & LAND] = 0
    return out          # -1 sea, 0 unclaimed land, >0 entity

# ------------------------------------------------------------------ borders
def crack_chains(lab):
    h, w = lab.shape
    W1 = w + 1
    segs = []
    a, b = lab[:, :-1], lab[:, 1:]
    m = (a != b) & (a >= 0) & (b >= 0)
    ys, xs = np.nonzero(m)
    segs.append((ys * W1 + xs + 1, (ys + 1) * W1 + xs + 1, a[m], b[m]))
    a, b = lab[:-1, :], lab[1:, :]
    m = (a != b) & (a >= 0) & (b >= 0)
    ys, xs = np.nonzero(m)
    segs.append(((ys + 1) * W1 + xs, (ys + 1) * W1 + xs + 1, a[m], b[m]))
    v1 = np.concatenate([s[0] for s in segs]); v2 = np.concatenate([s[1] for s in segs])
    pa = np.concatenate([s[2] for s in segs]); pb = np.concatenate([s[3] for s in segs])
    lo, hi = np.minimum(pa, pb), np.maximum(pa, pb)
    pair = lo.astype(np.int64) * 70000 + hi
    n = len(v1)
    if n == 0: return []
    ends = np.concatenate([v1, v2]); eidx = np.concatenate([np.arange(n), np.arange(n)])
    order = np.argsort(ends, kind='stable')
    se, si = ends[order], eidx[order]
    # dict vertex -> list of edges
    inc = collections.defaultdict(list)
    for v, e in zip(se.tolist(), si.tolist()): inc[v].append(e)
    v1l, v2l, pl = v1.tolist(), v2.tolist(), pair.tolist()
    seen = bytearray(n)
    chains = []
    def nxt(v, e):
        lst = inc[v]
        if len(lst) != 2: return -1
        o = lst[0] if lst[1] == e else lst[1]
        if pl[o] != pl[e] or seen[o]: return -1
        return o
    for e0 in range(n):
        if seen[e0]: continue
        seen[e0] = 1
        fwd = [v1l[e0], v2l[e0]]
        # extend forward from v2
        e, v = e0, v2l[e0]
        while True:
            o = nxt(v, e)
            if o < 0: break
            seen[o] = 1
            v = v2l[o] if v1l[o] == v else v1l[o]
            fwd.append(v); e = o
        e, v = e0, v1l[e0]
        back = []
        while True:
            o = nxt(v, e)
            if o < 0: break
            seen[o] = 1
            v = v2l[o] if v1l[o] == v else v1l[o]
            back.append(v); e = o
        verts = back[::-1] + fwd
        p = pl[e0]
        chains.append((p // 70000, p % 70000, verts))
    out = []
    for a_, b_, verts in chains:
        vv = np.array(verts, dtype=np.int64)
        pts = np.stack([vv % W1, vv // W1], 1).astype(np.float32)
        if len(pts) > 2:
            closed = verts[0] == verts[-1]
            s = cv2.approxPolyDP(pts.reshape(-1, 1, 2), 0.7, closed).reshape(-1, 2)
            if closed and len(s) > 2: s = np.vstack([s, s[:1]])
            pts = chaikin(s, 2, closed)
        out.append((int(a_), int(b_), pts))
    return out

def chaikin(p, it, closed):
    p = np.asarray(p, dtype=np.float32)
    for _ in range(it):
        if len(p) < 3: break
        q = p[:-1] * 0.75 + p[1:] * 0.25
        r = p[:-1] * 0.25 + p[1:] * 0.75
        mid = np.empty((len(q) * 2, 2), np.float32); mid[0::2] = q; mid[1::2] = r
        p = mid if closed else np.vstack([p[:1], mid, p[-1:]])
        if closed: p = np.vstack([p, p[:1]])
    return p

def enc(pts):
    a = np.round(np.asarray(pts) * ER * 4).astype(np.int64)
    d = np.diff(a, axis=0, prepend=np.zeros((1, 2), np.int64))
    return d.reshape(-1).tolist()

# ------------------------------------------------------------------ labels
def label_for(sm, i, sl, DS):
    y0, y1 = max(0, sl[0].start - 2), min(sm.shape[0], sl[0].stop + 2)
    x0, x1 = max(0, sl[1].start - 2), min(sm.shape[1], sl[1].stop + 2)
    m = (sm[y0:y1, x0:x1] == i).astype(np.uint8)
    n, cc, stats, _ = cv2.connectedComponentsWithStats(m, connectivity=8)
    if n <= 1: return None
    k = 1 + int(np.argmax(stats[1:, cv2.CC_STAT_AREA]))
    mk = (cc == k).astype(np.uint8)
    dt = cv2.distanceTransform(np.pad(mk, 1), cv2.DIST_L2, 5)[1:-1, 1:-1]
    yy, xx = np.nonzero(mk)
    pts = np.stack([xx, yy], 1).astype(np.float64)
    mu = pts.mean(0)
    cov = np.cov((pts - mu).T) if len(pts) > 2 else np.eye(2)
    if not np.all(np.isfinite(cov)): cov = np.eye(2)
    ev, evec = np.linalg.eigh(cov)
    v = evec[:, 1]
    ang = math.degrees(math.atan2(v[1], v[0]))
    if ang > 90: ang -= 180
    if ang < -90: ang += 180
    length = float(np.ptp((pts - mu) @ v) + 1)
    score = dt[yy, xx] - 0.08 * np.hypot(xx - mu[0], yy - mu[1])
    j = int(np.argmax(score))
    r = float(dt[yy[j], xx[j]])
    aspect = math.sqrt(max(ev[1], 1e-6) / max(ev[0], 1e-6))
    if aspect < 1.6: ang = 0.0
    ang = max(-32, min(32, ang))
    f = DS * ER
    return {'x': round((x0 + xx[j] + 0.5) * f, 1), 'y': round((y0 + yy[j] + 0.5) * f, 1),
            'r': round(r * f, 1), 'len': round(length * f, 1), 'ang': round(ang, 1)}

# ------------------------------------------------------------------ era sources
def load_hb(fname, year):
    feats = json.load(open(f'{HB}/geojson/{fname}'))['features']
    ents = {}      # name -> dict
    items = []
    for f in feats:
        p = f['properties']
        polys = feat_polys(f['geometry'])
        if not polys: continue
        name = clean(p.get('NAME'))
        if not name:
            items.append((0, polys)); continue
        subj = clean(p.get('SUBJECTO'))
        if subj.isdigit(): subj = ''
        e = ents.get(name)
        if e is None:
            # rough centroid of the largest ring for the classifier
            big = max((r[0] for r in polys), key=ring_area)
            a = np.asarray(big)
            lon, lat = float(a[:, 0].mean()), float(a[:, 1].mean())
            realm = name
            mm = re.match(r'^(.*)\(([^)]+)\)\s*$', name)
            if subj and norm(subj) != norm(name):
                realm = subj
            elif mm and norm(mm.group(2)) in POWER_SUFFIX:
                realm = POWER_SUFFIX[norm(mm.group(2))]
            kind = classify(name, subj if realm != name else '', year, lon, lat, p.get('type'))
            if kind == 1: realm = name
            link = clean(p.get('weblinks') or p.get('weblnks') or p.get('wikipedia') or p.get('INFO_UR'))
            if link and not link.startswith('http'): link = ''
            e = ents[name] = {'n': name, 'realm': realm, 'k': kind,
                              'p': int(p.get('BORDERPRECISION') or 1), 'w': link, 'id': len(ents) + 1}
        else:
            e['p'] = max(e['p'], int(p.get('BORDERPRECISION') or 1))
        items.append((e['id'], polys))
    return list(ents.values()), items

def load_ne():
    feats = load('ne_10m_admin_0_countries')['features']
    ents, items = {}, []
    for f in feats:
        p = f['properties']
        if p.get('ADM0_A3') == 'ATA': continue
        name = p['NAME']; sov = p['SOVEREIGNT']; typ = p.get('TYPE', '')
        realm = name
        if sov and sov != name and typ in ('Dependency', 'Country', 'Lease'):
            realm = {'United States of America': 'United States'}.get(sov, sov)
        if name == 'United States of America': name = 'United States'
        e = ents.get(name)
        if e is None:
            e = ents[name] = {'n': name, 'realm': realm, 'k': 0, 'p': 3, 'w': '', 'id': len(ents) + 1,
                              'a3': p.get('ADM0_A3')}
        items.append((e['id'], feat_polys(f['geometry'])))
    return list(ents.values()), items

idx = json.load(open(f'{HB}/index.json'))['years']
ERAS = [(y['year'], y['filename']) for y in idx]
ERAS.sort()
ERAS.append((2026, None))
import era_edits as ED

def ekey(y): return f'bc{-y}' if y < 0 else f'{y}'

# ------------------------------------------------------------------ edit machinery
_a0 = np.load(f'{WORK}/ids.npy')[::2, ::2][:EH, :EW]
_meta = json.load(open(f'{WORK}/meta.json'))
A0_ID = {m['ADM0_A3']: i + 1 for i, m in enumerate(_meta)}
A0_CONT = {}
for i, m in enumerate(_meta): A0_CONT.setdefault(m['CONTINENT'], []).append(i + 1)
_a1f = load('ne_10m_admin_1_states_provinces')['features']
A1 = np.zeros((EH, EW), np.int32)
A1_ID = {}
for i, f in enumerate(_a1f, start=1):
    p = f['properties']; A1_ID[(p['adm0_a3'], str(p['name']))] = A1_ID.get((p['adm0_a3'], str(p['name'])), []) + [i]
    for poly in feat_polys(f['geometry']):
        pts = poly_pts(poly)
        if pts: cv2.fillPoly(A1, pts, i, lineType=cv2.LINE_8, shift=4)
A1_BY_C = collections.defaultdict(list)
for (c, n), ii in A1_ID.items(): A1_BY_C[c] += [(n, ii)]
WARN = []

_GEO = {}
def geo_mask(shape):
    """shape: [lon0,lat0,lon1,lat1] box or [[lon,lat],...] polygon -> raster mask (cached)."""
    key = json.dumps(shape)
    if key not in _GEO:
        if not isinstance(shape[0], (list, tuple)):
            x0, y0, x1, y1 = shape
            pts = [[x0, y0], [x1, y0], [x1, y1], [x0, y1]]
            # densify so the outline follows the projection exactly
            dense = []
            for a, b in zip(pts, pts[1:] + pts[:1]):
                for t in range(16): dense.append([a[0] + (b[0] - a[0]) * t / 16, a[1] + (b[1] - a[1]) * t / 16])
            pts = dense
        else:
            pts = shape
        mm = np.zeros((EH, EW), np.uint8)
        cv2.fillPoly(mm, poly_pts([pts]), 1, lineType=cv2.LINE_8, shift=4)
        _GEO[key] = mm.astype(bool)
    return _GEO[key]
def _boxes(v):
    if v is None: return []
    return [v] if not isinstance(v[0], (list, tuple)) else v
def _polys(v):
    if v is None: return []
    return [v] if not isinstance(v[0][0], (list, tuple)) else v

def where_mask(op, E):
    m = None
    def OR(x):
        nonlocal m
        m = x if m is None else (m | x)
    if 'a0' in op:
        ids = [A0_ID[c] for c in op['a0'] if c in A0_ID]
        for c in op['a0']:
            if c not in A0_ID: WARN.append(f"{E['year']}: unknown country {c}")
        OR(np.isin(_a0, ids))
    if 'cont' in op: OR(np.isin(_a0, A0_CONT[op['cont']]))
    for key, excl in (('a1', False), ('a1x', True)):
        if key not in op: continue
        for c, names in op[key].items():
            if excl:
                ids = [i for n, ii in A1_BY_C[c] if n not in names for i in ii]
                for n in names:
                    if (c, n) not in A1_ID: WARN.append(f"{E['year']}: unknown province {c}/{n}")
            else:
                ids = []
                for n in names:
                    if (c, n) in A1_ID: ids += A1_ID[(c, n)]
                    else: WARN.append(f"{E['year']}: unknown province {c}/{n}")
            OR(np.isin(A1, ids))
    for b in _boxes(op.get('box')): OR(geo_mask(b))
    for p in _polys(op.get('poly')): OR(geo_mask(p))
    if m is None: m = np.ones((EH, EW), bool)
    for b in _boxes(op.get('clip')): m = m & geo_mask(b)
    for p in _polys(op.get('clipoly')): m = m & geo_mask(p)
    for b in _boxes(op.get('cut')): m = m & ~geo_mask(b)
    if op.get('only0'): m = m & (E['lab'] == 0)
    if 'frm' in op:
        ids = [E['byname'][n] for n in op['frm'] if n in E['byname']]
        if not ids: WARN.append(f"{E['year']}: none of {op['frm']} present")
        m &= np.isin(E['lab'], ids)
    return m & LAND

def ent_get(E, name, realm=None, kind=None, create=True):
    i = E['byname'].get(name)
    if i is None:
        if not create: return None
        e = {'n': name, 'realm': realm or name, 'k': 0 if kind is None else kind, 'p': 1, 'w': '', 'id': len(E['ents']) + 1, 'x': 1}
        E['ents'].append(e); E['byname'][name] = e['id']; i = e['id']
    e = E['ents'][i - 1]
    if realm is not None: e['realm'] = realm
    if kind is not None:
        e['k'] = kind
        if kind == 1: e['realm'] = e['n']
    return i

def apply_op(E, op):
    ents, lab = E['ents'], E['lab']
    if 'ren' in op:
        i = E['byname'].get(op['ren'])
        if i is None: WARN.append(f"{E['year']}: rename source missing: {op['ren']}"); return
        to = op['to']; j = E['byname'].get(to)
        if j and j != i:
            lab[lab == i] = j; ents[i - 1]['dead'] = 1; del E['byname'][op['ren']]
            ent_get(E, to, op.get('realm'), op.get('kind'))
        else:
            e = ents[i - 1]; del E['byname'][e['n']]
            if e['realm'] == e['n']: e['realm'] = to
            e['n'] = to; E['byname'][to] = i; e['x'] = 1
            ent_get(E, to, op.get('realm'), op.get('kind'))
    elif 'set' in op:
        if op['set'] not in E['byname']: WARN.append(f"{E['year']}: set target missing: {op['set']}"); return
        ent_get(E, op['set'], op.get('realm'), op.get('kind'))
    elif 'asg' in op:
        m = where_mask(op, E)
        i = ent_get(E, op['asg'], op.get('realm'), op.get('kind'))
        lab[m] = i; ents[i - 1]['x'] = 1
        if not m.any(): WARN.append(f"{E['year']}: asg {op['asg']} matched no land")
    elif 'copy' in op:
        S_ = RAW[op['src']]; si = S_['byname'].get(op.get('srcname', op['copy']))
        if si is None: WARN.append(f"{E['year']}: copy source missing {op['copy']}"); return
        src = S_['ents'][si - 1]
        i = ent_get(E, op['copy'], op.get('realm') or (src['realm'] if src['realm'] != src['n'] else None), src['k'])
        lab[(S_['lab'] == si) & LAND] = i; ents[i - 1]['x'] = 1
    elif 'fill' in op:
        S_ = DONE.get(op['fill']) or RAW[op['fill']]
        m = where_mask(op, E)
        if op.get('force'):
            keep = [E['byname'][n] for n in op.get('keep', []) if n in E['byname']]
            m &= ~np.isin(lab, keep)
        else:
            m &= (lab == 0)
        src_ids = np.unique(S_['lab'][m]); src_ids = src_ids[src_ids > 0]
        for si in src_ids:
            se = S_['ents'][si - 1]
            if se['n'] in op.get('drop', []) or se.get('dead'): continue
            nm, rl = op.get('remap', {}).get(se['n'], (se['n'], se['realm']))
            if nm is None: continue
            i = ent_get(E, nm, rl, se['k'])
            lab[m & (S_['lab'] == si)] = i; ents[i - 1]['x'] = 1
    elif 'clear' in op:
        m = where_mask(op, E)
        if op['clear']:   # list of entity names to clear (optionally inside the mask)
            m &= np.isin(lab, [E['byname'][n] for n in op['clear'] if n in E['byname']])
        lab[m] = 0
    elif 'realm_ren' in op:
        hit = 0
        for e in ents:
            if e['realm'] == op['realm_ren']: e['realm'] = op['to']; hit += 1
        if not hit: WARN.append(f"{E['year']}: realm_ren none for {op['realm_ren']}")
    elif 'realm_reset' in op:
        for e in ents:
            if e['realm'] == op['realm_reset'] and e['n'] != op['realm_reset']:
                e['realm'] = op.get('remap', {}).get(e['n'], e['n'])
    elif 'realm_a0' in op:
        cm = np.isin(_a0, [A0_ID[c] for c in op['realm_a0']])
        cnt_in = np.bincount(lab[cm].ravel(), minlength=len(ents) + 1)
        cnt_all = np.bincount(lab.ravel(), minlength=len(ents) + 1)
        for e in ents:
            i = e['id']
            if e['k'] == 0 and e['n'] not in op.get('keep', []) and cnt_all[i] and cnt_in[i] > 0.5 * cnt_all[i]:
                e['realm'] = op['realm']
    if op.get('n'): E['notes'].append(op['n'])

def generic(E):
    y = E['year']
    for e in E['ents']:
        nl = e['n'].lower()
        for rx, y0, y1, ch in ED.GENERIC:
            if y0 <= y <= y1 and re.search(rx, nl):
                if 'to' in ch:
                    apply_op(E, {'ren': e['n'], 'to': ch['to'], 'realm': ch.get('realm'), 'kind': ch.get('kind')})
                else:
                    ent_get(E, e['n'], ch.get('realm'), ch.get('kind'))
                break
    for e in E['ents']:
        if e.get('dead') or e['realm'] != e['n'] or e['k'] == 1: continue
        nl = e['n'].lower()
        for rx, power, y0, y1 in ED.COLONIES:
            if y0 <= y <= y1 and re.search(rx, nl): e['realm'] = power; break
        else:
            for pre, power, y0, y1 in ED.PREFIX:
                if y0 <= y <= y1 and nl.startswith(pre): e['realm'] = power; break

# ------------------------------------------------------------------ phase 1: raw source rasters
RAW = {}
for year, fname in ERAS:
    ents, items = load_ne() if fname is None else load_hb(fname, year)
    lab = fill_coasts(rasterize(items))
    lab = np.where(lab > 0, lab, 0).astype(np.uint16)
    RAW[year] = {'year': year, 'ents': ents, 'lab': lab, 'byname': {e['n']: e['id'] for e in ents}}
print('phase 1 done', flush=True)

import copy as _copy
def clone(E, year):
    return {'year': year, 'ents': _copy.deepcopy(E['ents']), 'lab': E['lab'].copy(), 'byname': dict(E['byname']), 'notes': []}

# ------------------------------------------------------------------ phase 2: corrections (descending so 'fill' sources exist)
DONE = {}
for year, fname in sorted(ERAS, key=lambda t: -t[0]):
    E = clone(RAW[year], year)
    generic(E)
    for op in ED.EDITS.get(year, []): apply_op(E, op)
    DONE[year] = E
for year, spec in sorted(ED.DERIVED.items()):
    E = clone(DONE[spec['base']], year)
    E['notes'] = [f"Built from the {spec['base'] if spec['base'] > 0 else str(-spec['base']) + ' BCE'} map, adjusted to {year}."]
    for op in spec['ops']: apply_op(E, op)
    generic(E)
    E['derived'] = spec['base']; E['title'] = spec.get('title')
    DONE[year] = E
del RAW
import gc; gc.collect()
print('phase 2 done; warnings:', len(WARN), flush=True)
for w in WARN: print('  WARN', w)

# ------------------------------------------------------------------ phase 3: carry peoples into unclaimed land
YEARS = sorted(DONE)
nw0 = len(WARN)
PRE = {y: DONE[y]['lab'].copy() for y in YEARS if y < 2026}
def carry(y, cands, people_only):
    E = DONE[y]; lab = E['lab']; filled = 0
    for c in cands:
        un = (lab == 0) & LAND
        if not un.any(): break
        S_ = DONE[c]; sl = PRE[c]
        src_ids = np.unique(sl[un]); src_ids = src_ids[src_ids > 0]
        for si in src_ids:
            se = S_['ents'][si - 1]
            if se.get('dead') or (people_only and se['k'] != 1): continue
            j = E['byname'].get(se['n'])
            if people_only and j and E['ents'][j - 1]['k'] != 1: continue
            i = ent_get(E, se['n'], se['realm'] if not j else None, se['k'] if not j else None)
            mm = un & (sl == si); lab[mm] = i; filled += int(mm.sum())
            E['ents'][i - 1]['carry'] = c
    return filled
for y in YEARS:
    if y >= 1914: continue
    E = DONE[y]
    fut = 50 if y < 1000 else 15     # states from later maps only when very close, to avoid anachronisms
    near = sorted([c for c in YEARS if c != y and c in PRE and ((c < y and y - c <= 50) or (c > y and c - y <= fut))],
                  key=lambda c: (0 if c < y else 1, abs(c - y)))
    f1 = carry(y, near, False)
    far = sorted([c for c in YEARS if c != y and c in PRE and ((c < y and y - c <= 700) or (c > y and c - y <= 300))],
                 key=lambda c: (0 if c < y else 1, abs(c - y)))
    f2 = carry(y, far, True)
    if f1: E['notes'].append('Filled gaps in the source map from the nearest map (within 50 years).')
    if f2: E['notes'].append('Filled unclaimed land with peoples and cultures from neighbouring maps.')
    # last resort: regional peoples for land still unclaimed (only0 so nothing is overwritten)
    nf = 0
    for y0, y1, op in ED.FALLBACK:
        if y0 <= y <= y1:
            before = int((E['lab'] == 0).sum())
            op = dict(op, only0=True); op.setdefault('kind', 1); op.pop('n', None)
            m = where_mask(op, E)
            if m.any():
                i = ent_get(E, op['asg'], op.get('realm'), op['kind'])
                E['lab'][m] = i; E['ents'][i - 1]['x'] = 1; nf += int(m.sum())
    if nf: E['notes'].append('Named the remaining unclaimed regions after their regional peoples.')
# post-carry fixes (applied after gap filling, e.g. to rename carried entities)
for y in YEARS:
    for op in ED.POST.get(y, []): apply_op(DONE[y], op)
print('phase 3 done', flush=True)
for w in WARN[nw0:]: print('  WARN', w)

# ------------------------------------------------------------------ phase 4: stats, labels, borders, rasters
realm_reg = {}          # key -> {key, kind, area, names Counter}
realm_adj = collections.Counter()
era_out = []
for year in YEARS:
    E = DONE[year]
    ents = [e for e in E['ents']]
    ids = E['lab']
    lab = np.where(LAND, ids.astype(np.int32), -1)
    n = len(ents)
    cnt = np.bincount(ids.ravel(), weights=np.repeat(PIXKM, EW), minlength=n + 1)
    objs = ndimage.find_objects(ids.astype(np.int32))
    DS = 2
    sm = ids[::DS, ::DS].astype(np.int32)
    sobjs = ndimage.find_objects(sm)
    for e in ents:
        i = e['id']
        e['a'] = int(round(cnt[i])) if i < len(cnt) and not e.get('dead') else 0
        sl = objs[i - 1] if i - 1 < len(objs) else None
        e['b'] = [sl[1].start, sl[0].start, sl[1].stop, sl[0].stop] if (sl is not None and e['a']) else None
        ssl = sobjs[i - 1] if i - 1 < len(sobjs) else None
        e['l'] = label_for(sm, i, ssl, DS) if (ssl is not None and e['a']) else None
        e['rk'] = realm_key(e['realm'])
    chains = crack_chains(lab)
    by_id = {e['id']: e for e in ents}
    for e in ents:
        if not e['a']: continue
        R_ = realm_reg.setdefault(e['rk'], {'key': e['rk'], 'kind': e['k'], 'area': 0, 'names': collections.Counter()})
        R_['area'] += e['a']; R_['names'][e['realm']] += e['a']
        if e['k'] == 0: R_['kind'] = 0
    for a_, b_, pts in chains:
        if a_ > 0 and b_ > 0:
            ka, kb = by_id[a_]['rk'], by_id[b_]['rk']
            if ka != kb: realm_adj[tuple(sorted((ka, kb)))] += len(pts)
    img = np.zeros((EH, EW, 3), np.uint8)
    img[..., 2] = (ids & 255).astype(np.uint8); img[..., 1] = (ids >> 8).astype(np.uint8)
    cv2.imwrite(f'{OUT}/eras/{ekey(year)}.png', img, [cv2.IMWRITE_PNG_COMPRESSION, 9])
    era_out.append((year, ents, chains, E))
    print(year, 'ents', n, 'with area', sum(1 for e in ents if e['a']), 'chains', len(chains), 'notes', len(E['notes']), flush=True)

# ------------------------------------------------------------------ colours
def rgb(h): return np.array([int(h[i:i + 2], 16) for i in (1, 3, 5)], float)
nbrs = collections.defaultdict(dict)
for (a_, b_), w in realm_adj.items():
    nbrs[a_][b_] = w; nbrs[b_][a_] = w
color = {}
for k, c in PRESET.items():
    if k in realm_reg: color[k] = c
use = collections.Counter()
rng = np.random.default_rng(11)
for R_ in sorted(realm_reg.values(), key=lambda r: -r['area']):
    k = R_['key']
    if k in color: continue
    pal = STATE_PAL if R_['kind'] == 0 else PEOPLE_PAL
    best, bs = pal[0], -1e9
    for c in rng.permutation(pal):
        d = 400.0
        for nb, w in nbrs[k].items():
            if nb in color:
                d = min(d, np.linalg.norm(rgb(c) - rgb(color[nb])) - min(40, w / 40))
        s = d - use[c] * 3
        if s > bs: bs, best = s, c
    color[k] = str(best); use[best] += 1

keys = sorted(realm_reg, key=lambda k: -realm_reg[k]['area'])
gidx = {k: i for i, k in enumerate(keys)}
realms_out = [{'k': k, 'c': color[k], 't': realm_reg[k]['kind'],
               'n': realm_reg[k]['names'].most_common(1)[0][0]} for k in keys]

def period(y):
    for lim, name in [(-10000, 'Paleolithic'), (-3300, 'Neolithic'), (-1200, 'Bronze Age'), (-500, 'Iron Age'),
                      (500, 'Classical Antiquity'), (1000, 'Early Middle Ages'), (1500, 'Late Middle Ages'),
                      (1800, 'Early Modern Era'), (1914, 'Age of Revolutions & Empire'), (1945, 'World Wars'),
                      (1991, 'Cold War'), (99999, 'Contemporary Era')]:
        if y < lim: return name
eras_index = []
for year, ents, chains, EE in era_out:
    FIX = {'Neterlands': 'Netherlands', 'Danemark': 'Denmark'}
    disp = {}
    for e in ents:
        if e['rk'] not in gidx: continue
        d = disp.setdefault(e['rk'], {'self': None, 'kin': None, 'names': collections.Counter()})
        if norm(e['n']) == norm(e['realm']) and e['a'] >= (d['self'][1] if d['self'] else -1):
            d['self'] = (e['n'], e['a'])
        if realm_key(e['n']) == e['rk'] and e['a'] >= (d['kin'][1] if d['kin'] else -1):
            d['kin'] = (e['n'], e['a'])
        d['names'][FIX.get(e['realm'], e['realm'])] += e['a'] + 1
    local = {}
    realms_local = []
    out_e = []
    for e in ents:
        if e['rk'] not in gidx:     # no land at all in any era
            ri = -1
        else:
            if e['rk'] not in local:
                d = disp[e['rk']]
                local[e['rk']] = len(realms_local)
                top = d['names'].most_common(1)[0][0]
                if top in ('UK', 'GB'): top = 'Kingdom of England' if year < 1707 else 'Kingdom of Great Britain' if year < 1801 else 'United Kingdom'
                top = {'England': 'Kingdom of England', 'Spanish Habsburg': 'Spain (Habsburg)', 'Persi': 'Sasanian Empire'}.get(top, top)
                if (len(top) <= 3 or top.isdigit()) and d['kin']: top = d['kin'][0]
                realms_local.append({'g': gidx[e['rk']], 'n': d['self'][0] if d['self'] else top})
            ri = local[e['rk']]
        o = {'n': e['n'], 'r': ri, 'k': e['k'], 'p': e['p'], 'a': e['a']}
        if e['b']: o['b'] = e['b']
        if e['l']: o['l'] = e['l']
        if e.get('w'): o['w'] = e['w']
        if e.get('a3'): o['a3'] = e['a3']
        if e.get('x'): o['x'] = 1
        if e.get('carry'): o['c'] = e['carry']
        out_e.append(o)
    borders = [[a_, b_] + enc(pts) for a_, b_, pts in chains]
    js = {'y': year, 'src': 'Natural Earth' if year == 2026 else 'historical-basemaps',
          'realms': realms_local, 'ents': out_e, 'borders': borders, 'notes': EE['notes']}
    if EE.get('derived') is not None: js['d'] = EE['derived']
    p = f'{OUT}/eras/{ekey(year)}.json'
    json.dump(js, open(p, 'w'), separators=(',', ':'), ensure_ascii=True)
    ix = {'y': year, 'f': ekey(year), 'p': period(year), 'c': len(EE['notes'])}
    if EE.get('derived') is not None: ix['d'] = EE['derived']; ix['t'] = EE.get('title')
    eras_index.append(ix)
    ix.update({
                       'n': sum(1 for e in ents if e['a'] and e['k'] == 0),
                       'm': sum(1 for e in ents if e['a'] and e['k'] == 1)})
json.dump({'eras': eras_index, 'realms': realms_out, 'w': EW, 'h': EH, 'scale': ER,
           'source': 'historical-basemaps by A. Ourednik et al. (GPL-3.0); 2026 from Natural Earth'},
          open(f'{OUT}/data/eras.json', 'w'), separators=(',', ':'), ensure_ascii=True)
print('realms', len(realms_out))
