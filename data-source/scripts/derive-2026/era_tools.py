"""Helpers for deriving a new era map from a deployed one (site/eras/<key>.json), without the full
s6_eras.py rebuild. The border tracing, smoothing, encoding and label code is taken verbatim from
s6_eras.py so a derived map is drawn exactly like the others; check_roundtrip() proves it by
re-tracing an unchanged map and comparing with the file."""
import base64, collections, io, json, math, os, re, sys
import numpy as np, cv2
from PIL import Image
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from common import proj, inv_lat, W

ER = 2
EW, EH = W // ER, 2111
_src = open(os.path.join(os.path.dirname(HERE), 's6_eras.py'), encoding='utf-8').read()
def _grab(name):
    m = re.search(rf'^def {name}\(.*?(?=^def |^# -{{10}})', _src, re.S | re.M)
    return m.group(0)
exec(compile(''.join(_grab(n) for n in ('crack_chains', 'chaikin', 'enc', 'label_for', 'poly_pts')), 's6_eras.py', 'exec'))

LATR = inv_lat(np.arange(EH) + 0.5, EW)
R_ = 6371.0; _dl = 2 * np.pi / EW
PIXKM = (R_ * R_ * np.cos(np.radians(LATR)) * _dl * _dl * np.cos(np.radians(0.8 * LATR))).astype(np.float64)

def read_ids(js):
    im = Image.open(io.BytesIO(base64.b64decode(js['_png']))).convert('RGB')
    a = np.asarray(im).astype(np.int32)
    return (a[..., 0] | (a[..., 1] << 8)).astype(np.int32)

def write_ids(ids):
    """PNG with R = low byte, G = high byte, as the deployed files: a palette image when there are at most
    256 distinct ids, otherwise plain RGB."""
    vals = np.unique(ids)
    if len(vals) > 256:
        rgb = np.zeros(ids.shape + (3,), np.uint8); rgb[..., 0] = ids & 255; rgb[..., 1] = ids >> 8
        b = io.BytesIO(); Image.fromarray(rgb, 'RGB').save(b, 'PNG', optimize=True)
        return base64.b64encode(b.getvalue()).decode('ascii')
    lut = np.zeros(int(vals.max()) + 1, np.uint8); lut[vals] = np.arange(len(vals))
    im = Image.fromarray(lut[ids], 'P')
    pal = []
    for v in vals: pal += [int(v) & 255, int(v) >> 8, 0]
    im.putpalette(pal + [0] * (768 - len(pal)))
    b = io.BytesIO(); im.save(b, 'PNG', optimize=True)
    return base64.b64encode(b.getvalue()).decode('ascii')

def land_mask(eras_dir, keys):
    """Land = anywhere any era map claims (sea is never claimed). The era files hold no separate land mask."""
    m = np.zeros((EH, EW), bool)
    for k in keys:
        m |= read_ids(json.load(open(f'{eras_dir}/{k}.json', encoding='utf-8'))) > 0
    return m

def borders(ids, LAND):
    lab = np.where(LAND, ids, -1)
    return [[a_, b_] + enc(pts) for a_, b_, pts in crack_chains(lab)]

def geo_mask(poly):
    mm = np.zeros((EH, EW), np.uint8)
    cv2.fillPoly(mm, poly_pts([poly]), 1, lineType=cv2.LINE_8, shift=4)
    return mm.astype(bool)

def stats(ids, i):
    """area (km2), bbox and label for entity id i, as s6_eras.py computes them."""
    m = ids == i
    a = int(round(float((m * PIXKM[:, None]).sum())))
    if not a: return 0, None, None
    ys, xs = np.nonzero(m)
    b = [int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1]
    DS = 2; sm = ids[::DS, ::DS]
    objs = ndimage.find_objects((sm == i).astype(np.int32))
    return a, b, (label_for(sm, i, objs[0], DS) if objs and objs[0] is not None else None)

def check_roundtrip(js, LAND):
    """Re-trace an unchanged map: borders and per-entity stats must match the deployed file."""
    ids = read_ids(js)
    same_b = borders(ids, LAND) == js['borders']
    bad = []
    for i, e in enumerate(js['ents'], 1):
        if not e.get('a'): continue
        a, b, l = stats(ids, i)
        if a != e['a'] or b != e.get('b') or l != e.get('l'): bad.append((e['n'], a, e['a'], b, e.get('b'), l, e.get('l')))
    return same_b, bad


# ------------------------------------------------------------------ deriving a new era map
class Derive:
    """Start a new era map from a deployed one. Typical use:
        D = Derive(site, 'bc500'); D.rename(...); D.take(...); D.save(-550, 'bc550', 'Title', notes)
    Every change only touches the source map's own territories, and every territory whose pixels or
    realm change is re-measured; borders are re-traced at the end."""
    ORDER = ['n', 'r', 'k', 'p', 'a', 'b', 'l', 'w', 'a3', 'x', 'c']

    def __init__(self, site, src_key):
        self.site = site
        self.meta = json.load(open(f'{site}/data/eras.json', encoding='utf-8'))
        self.LAND = land_mask(f'{site}/eras', [e['f'] for e in self.meta['eras']])
        self.src_key = src_key
        self.src = json.load(open(f'{site}/eras/{src_key}.json', encoding='utf-8'))
        same, bad = check_roundtrip(self.src, self.LAND)
        assert same and not bad, f'tracing does not reproduce the {src_key} map; stop'
        import copy
        self.js = copy.deepcopy(self.src); self.ids = read_ids(self.src).copy()
        self.touched = set(); self.parent = {}

    def ent(self, name):
        hits = [i + 1 for i, e in enumerate(self.js['ents']) if e['n'] == name]
        assert len(hits) == 1, (name, hits)
        return hits[0]

    def realm(self, name, g=None, colour=None, kind=0):
        """Index of a realm on this map, added if missing. A new realm reuses registry entry g, or adds one."""
        R = self.js['realms']
        for i, r in enumerate(R):
            if r['n'] == name: return i
        if g is None:
            key = name.lower()
            g = len(self.meta['realms'])
            self.meta['realms'].append({'k': key, 'c': colour, 't': kind, 'n': name})
        R.append({'g': g, 'n': name}); return len(R) - 1

    def rename(self, old, new, realm=None):
        i = self.ent(old); e = self.js['ents'][i - 1]; e['n'] = new; e['x'] = 1
        if realm is not None: e['r'] = realm
        self.touched.add(i); return i

    def rename_realm(self, old, new):
        for r in self.js['realms']:
            if r['n'] == old: r['n'] = new; return
        raise KeyError(old)

    def take(self, name, realm, mask, frm, kind=0):
        """Give the pixels of mask that belong to entities frm (names) to entity name (created if new)."""
        frm_ids = [self.ent(n) for n in frm]
        m = mask & np.isin(self.ids, frm_ids)
        assert m.any(), f'{name}: nothing to take'
        try: i = self.ent(name)
        except AssertionError:
            self.js['ents'].append({'n': name, 'r': realm, 'k': kind, 'p': 1, 'a': 0, 'x': 1}); i = len(self.js['ents'])
            self.parent[i] = frm_ids[0]
        self.ids[m] = i; self.touched.update([i] + frm_ids)
        return int(m.sum())

    def lon_box(self, lon0, lat0, lon1, lat1):
        return geo_mask([[lon0, lat0], [lon1, lat0], [lon1, lat1], [lon0, lat1]])

    def save(self, year, key, title, notes, base_year):
        js, ids = self.js, self.ids
        for i in self.touched:
            e = js['ents'][i - 1]; a, b, l = stats(ids, i)
            e['a'] = a
            for k, v in (('b', b), ('l', l)):
                if v is None: e.pop(k, None)
                else: e[k] = v
        used = sorted({e['r'] for e in js['ents'] if e['r'] >= 0 and e.get('a')})
        remap = {r: k for k, r in enumerate(used)}
        js['realms'] = [js['realms'][r] for r in used]
        for e in js['ents']:
            if e['r'] >= 0: e['r'] = remap.get(e['r'], -1)
        js['ents'] = [{k: e[k] for k in self.ORDER if k in e} for e in js['ents']]
        js['y'] = year; js['d'] = base_year
        js['borders'] = borders(ids, self.LAND)
        js['notes'] = notes + self.src['notes']
        js['_png'] = write_ids(ids)
        out = {k: js[k] for k in ['y', 'src', 'realms', 'ents', 'borders', 'notes', 'd', '_png'] if k in js}
        assert (read_ids(out) == ids).all()
        S = self.site
        open(f'{S}/eras/{key}.json', 'w', encoding='utf-8').write(json.dumps(out, ensure_ascii=False, separators=(',', ':')))
        meta = self.meta; eras = meta['eras']
        assert not any(e['y'] == year for e in eras), f'{year} is already in eras.json'
        def period(y):
            for lim, name in [(-10000, 'Paleolithic'), (-3300, 'Neolithic'), (-1200, 'Bronze Age'), (-500, 'Iron Age'),
                              (500, 'Classical Antiquity'), (1000, 'Early Middle Ages'), (1500, 'Late Middle Ages'),
                              (1800, 'Early Modern Era'), (1914, 'Age of Revolutions & Empire'), (1945, 'World Wars'),
                              (1991, 'Cold War'), (99999, 'Contemporary Era')]:
                if y < lim: return name
        ix = {'y': year, 'f': key, 'p': period(year), 'c': len(out['notes']), 'd': base_year, 't': title,
              'n': sum(1 for e in out['ents'] if e.get('a') and e['k'] == 0), 'm': sum(1 for e in out['ents'] if e.get('a') and e['k'] == 1)}
        pos = next((k for k, e in enumerate(eras) if e['y'] > year), len(eras))
        eras.insert(pos, ix)
        open(f'{S}/data/eras.json', 'w', encoding='utf-8').write(json.dumps(meta, ensure_ascii=True, separators=(',', ':')))
        import copy
        for name in ('religions', 'cultures', 'develop'):
            p = f'{S}/data/{name}.json'
            if not os.path.exists(p): continue
            d = json.load(open(p, encoding='utf-8')); d['eras'][key] = copy.deepcopy(d['eras'][self.src_key])
            open(p, 'w', encoding='utf-8').write(json.dumps(d, ensure_ascii=True, separators=(',', ':')))
        p = f'{S}/data/ovmain.json'
        if os.path.exists(p):
            d = json.load(open(p, encoding='utf-8')); rows = copy.deepcopy(d['eras'][self.src_key])
            for i in range(len(rows) + 1, len(out['ents']) + 1):
                rows.append(copy.deepcopy(rows[self.parent.get(i, 1) - 1]))
            d['eras'][key] = rows
            open(p, 'w', encoding='utf-8').write(json.dumps(d, ensure_ascii=True, separators=(',', ':')))
        return out, ix
