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
