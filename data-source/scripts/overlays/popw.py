"""Population-weight raster (4096x2111, Miller): modern country density x true pixel area, boosted near cities by the era's development layer."""
import numpy as np, json, math, os
from PIL import Image
SP = os.environ.get('HHA_ATLAS', './atlas/')   # an atlas site folder with data/world.json and tiles/ids/0_0_0.png
W = json.load(open(SP + 'data/world.json')); Wd, yN = W['W'], W['yN']; K = Wd / (2 * math.pi)
def row_lat(y4096):
    wy = y4096 * (Wd / 4096); my = yN - wy / K
    return (2.5 * math.atan(math.exp(0.8 * my)) - 0.625 * math.pi)
def base():
    a = np.array(Image.open(SP + 'tiles/ids/0_0_0.png').convert('RGB')).astype(np.int64)
    cid = a[..., 0] | (a[..., 1] << 8)                       # 2048x1056 country index (0 = none)
    cid = np.array(Image.fromarray(cid.astype(np.int32)).resize((4096, 2111), Image.NEAREST)).astype(np.int64)
    H = cid.shape[0]
    lat_e = np.array([row_lat(y) for y in range(H + 1)])
    area_row = np.abs(np.sin(lat_e[:-1]) - np.sin(lat_e[1:]))       # true area per pixel row (sphere), up to a constant
    A = np.repeat(area_row[:, None], 4096, axis=1)
    pops = {c['id']: (c.get('pop') or 0) for c in W['countries']}
    n = cid.max() + 1
    area_by = np.bincount(cid.ravel(), weights=A.ravel(), minlength=n)
    dens = np.zeros(n)
    for i in range(1, n):
        if area_by[i] > 0: dens[i] = pops.get(i, 0) / area_by[i]
    return dens[cid] * A                                           # modern population per pixel (relative)
_B = None
def weights(dev):
    global _B
    if _B is None: _B = base()
    boost = 1 + np.maximum(dev.astype(float) - 8, 0) / 40
    return _B * boost + 1e-9
