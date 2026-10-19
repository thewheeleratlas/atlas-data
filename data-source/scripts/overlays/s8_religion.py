"""Religion layer: majority faith of the population, painted per era on the same raster as the era borders.

Inputs : site/eras/<key>.png + .json (era rasters from s6), Natural Earth admin-0/admin-1 masks
Rules  : build/religion_rules.py  (ordered; a later rule overrides an earlier one where both apply)
Outputs: site/rel/<key>.png        8-bit faith index per era pixel (0 = none / sea / unclaimed)
         site/data/religions.json  faith list (name, family, colour, notes) + area per faith per era
"""
import cv2, sys, json, os, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
import importlib
LAYER = sys.argv[1] if len(sys.argv) > 1 else 'religion'
RR = importlib.import_module({'religion': 'religion_rules', 'culture': 'culture_rules'}[LAYER])
ODIR = {'religion': 'rel', 'culture': 'cul'}[LAYER]
OJSON = {'religion': 'religions', 'culture': 'cultures'}[LAYER]

EW, EH = W // 2, H // 2
os.makedirs(f'{OUT}/{ODIR}', exist_ok=True)
land8 = np.load(f'{WORK}/land.npy').astype(np.float32) / 255
LAND = cv2.resize(land8, (EW, EH), interpolation=cv2.INTER_AREA) > 0.5
del land8
LATR = inv_lat(np.arange(EH) + 0.5, EW)
R_ = 6371.0; dl = 2 * np.pi / EW
PIXKM = (R_ * R_ * np.cos(np.radians(LATR)) * dl * dl * np.cos(np.radians(0.8 * LATR))).astype(np.float64)

# ------------------------------------------------------------------ admin masks (cached)
_a0 = np.load(f'{WORK}/ids.npy')[::2, ::2][:EH, :EW]
_meta = json.load(open(f'{WORK}/meta.json'))
A0_ID = {m['ADM0_A3']: i + 1 for i, m in enumerate(_meta)}
A0_CONT = collections.defaultdict(list)
for i, m in enumerate(_meta): A0_CONT[m['CONTINENT']].append(i + 1)

def poly_pts(rings):
    out = []
    for r in rings:
        a = np.asarray(r, dtype=np.float64)
        if a.ndim != 2 or len(a) < 3: continue
        x, y = proj(a[:, 0], a[:, 1], EW)
        out.append(np.round(np.stack([x, y], 1) * 16).astype(np.int32))
    return out

A1_CACHE = f'{WORK}/a1_era.npy'
if os.path.exists(A1_CACHE) and os.path.exists(A1_CACHE + '.json'):
    A1 = np.load(A1_CACHE); A1_ID = {tuple(k.split('|', 1)): v for k, v in json.load(open(A1_CACHE + '.json')).items()}
else:
    A1 = np.zeros((EH, EW), np.int32); A1_ID = {}
    for i, f in enumerate(load('ne_10m_admin_1_states_provinces')['features'], start=1):
        p = f['properties']; key = (p['adm0_a3'], str(p['name']))
        A1_ID.setdefault(key, []).append(i)
        for poly in rings_of(f['geometry']):
            pts = poly_pts(poly)
            if pts: cv2.fillPoly(A1, pts, i, lineType=cv2.LINE_8, shift=4)
    np.save(A1_CACHE, A1); json.dump({'|'.join(k): v for k, v in A1_ID.items()}, open(A1_CACHE + '.json', 'w'))
A1_BY_C = collections.defaultdict(list)
for (c, n), ii in A1_ID.items(): A1_BY_C[c].append((n, ii))

_GEO = {}
def geo_mask(shape):
    key = json.dumps(shape)
    if key not in _GEO:
        if not isinstance(shape[0], (list, tuple)):
            x0, y0, x1, y1 = shape
            c = [[x0, y0], [x1, y0], [x1, y1], [x0, y1]]
            pts = []
            for a, b in zip(c, c[1:] + c[:1]):
                for t in range(16): pts.append([a[0] + (b[0] - a[0]) * t / 16, a[1] + (b[1] - a[1]) * t / 16])
        else:
            pts = shape
        mm = np.zeros((EH, EW), np.uint8)
        cv2.fillPoly(mm, poly_pts([pts]), 1, lineType=cv2.LINE_8, shift=4)
        _GEO[key] = mm.astype(bool)
    return _GEO[key]
_boxes = lambda v: [] if v is None else ([v] if not isinstance(v[0], (list, tuple)) else v)
_polys = lambda v: [] if v is None else ([v] if not isinstance(v[0][0], (list, tuple)) else v)

WARN = set()
_mcache = {}
def static_mask(w):
    """Mask from the geographic parts of a rule (no era dependence); cached by rule identity."""
    key = id(w)
    if key in _mcache: return _mcache[key]
    m = None
    def OR(x):
        nonlocal m
        m = x if m is None else (m | x)
    if 'a0' in w:
        for c in w['a0']:
            if c not in A0_ID: WARN.add(f'unknown country {c}')
        OR(np.isin(_a0, [A0_ID[c] for c in w['a0'] if c in A0_ID]))
    if 'cont' in w: OR(np.isin(_a0, A0_CONT[w['cont']]))
    for key2, excl in (('a1', False), ('a1x', True)):
        for c, names in w.get(key2, {}).items():
            for n in names:
                if (c, n) not in A1_ID: WARN.add(f'unknown province {c}/{n}')
            if excl: ids = [i for n, ii in A1_BY_C[c] if n not in names for i in ii]
            else: ids = [i for n in names for i in A1_ID.get((c, n), [])]
            OR(np.isin(A1, ids))
    for b in _boxes(w.get('box')): OR(geo_mask(b))
    for p in _polys(w.get('poly')): OR(geo_mask(p))
    has_geo = m is not None
    if m is None: m = np.ones((EH, EW), bool)
    for b in _boxes(w.get('clip')): m = m & geo_mask(b)
    for p in _polys(w.get('clipoly')): m = m & geo_mask(p)
    for b in _boxes(w.get('cut')): m = m & ~geo_mask(b)
    ys, xs = np.nonzero(m.any(1))[0], np.nonzero(m.any(0))[0]
    if len(ys) == 0: _mcache[key] = None
    else:
        y0, y1, x0, x1 = ys[0], ys[-1] + 1, xs[0], xs[-1] + 1
        _mcache[key] = ((slice(y0, y1), slice(x0, x1)), m[y0:y1, x0:x1].copy())
    return _mcache[key]

# ------------------------------------------------------------------ faiths
FAITHS = RR.FAITHS
FIDX = {f['id']: i + 1 for i, f in enumerate(FAITHS)}
WIDE = len(FAITHS) > 255
for y0, y1, rel, w in RR.RULES:
    if rel not in FIDX and rel != '@like': raise SystemExit(f'unknown item {rel}')
# Gap rules (where['gap']) paint only pixels still holding the world default from the first (base) rule, so they can
# never overwrite a deliberate choice. '@like' copies the most common value of the area given in where['like'].
NA_LOG = []

idx = json.load(open(f'{OUT}/data/eras.json'))
out_areas = {}
for meta in idx['eras']:
    y, key = meta['y'], meta['f']
    im = cv2.imread(f'{OUT}/eras/{key}.png')
    ids = im[..., 2].astype(np.int32) | (im[..., 1].astype(np.int32) << 8)
    js = json.load(open(f'{OUT}/eras/{key}.json'))
    names = {e['n']: i + 1 for i, e in enumerate(js['ents'])}
    realm_of = {i + 1: js['realms'][e['r']]['n'] if e['r'] >= 0 else '' for i, e in enumerate(js['ents'])}
    claimed = (ids > 0) & LAND
    rel = np.zeros((EH, EW), np.uint16 if WIDE else np.uint8)
    isbase = np.zeros((EH, EW), bool)
    for ri, (y0, y1, r, w) in enumerate(RR.RULES):
        if not (y0 <= y <= y1): continue
        sm = static_mask(w)
        if sm is None: continue
        sl, m = sm
        if 'ent' in w or 'realm' in w:
            sel = [names[n] for n in w.get('ent', []) if n in names]
            sel += [i for i, rn in realm_of.items() if rn in w.get('realm', [])]
            m = m & np.isin(ids[sl], sel)
        m = m & claimed[sl]
        if w.get('gap'): m = m & isbase[sl]
        if not m.any(): continue
        if r == '@like':
            lsl, lm = static_mask(w['like'])
            src = rel[lsl][lm & claimed[lsl] & ~isbase[lsl]]; src = src[src > 0]
            if not len(src): continue
            v = int(np.bincount(src).argmax())
        else: v = FIDX[r]
        rel[sl][m] = v; isbase[sl][m] = (ri == 0)
        if r == 'na': NA_LOG.append([y, w.get('note', ''), int(m.sum())])
    if WIDE:
        out = np.zeros((EH, EW, 3), np.uint8); out[..., 2] = rel & 255; out[..., 1] = rel >> 8
    else: out = rel
    cv2.imwrite(f'{OUT}/{ODIR}/{key}.png', out, [cv2.IMWRITE_PNG_COMPRESSION, 9])
    area = np.bincount(rel.ravel(), weights=np.repeat(PIXKM, EW), minlength=len(FAITHS) + 1)
    out_areas[key] = [[int(i), int(round(area[i]))] for i in np.argsort(-area) if i > 0 and area[i] > 500]
    print(y, LAYER, len(out_areas[key]), flush=True)

items = [{k: f[k] for k in ('id', 'n', 'fam', 'c', 'd', 'w') if k in f} for f in FAITHS]
json.dump({'faiths': items, 'items': items, 'wide': WIDE,
           'families': RR.FAMILIES, 'eras': out_areas},
          open(f'{OUT}/data/{OJSON}.json', 'w'), separators=(',', ':'), ensure_ascii=True)
for w in sorted(WARN): print('WARN', w)
json.dump(NA_LOG, open(f'{OUT}/{ODIR}_na_log.json', 'w'))
