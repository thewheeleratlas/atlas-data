"""Recompute the main faith and main culture of the territories a layer repaint touched (28 Oct 2026).

Usage (from data-source/scripts/overlays/):
    HHA_ATLAS=<site>/ python3 ovmain_refresh.py <site>/ <terrain4096.npy> <git ref of the layers before the repaint>

For every era map whose rel/ or cul/ picture differs from the one at <git ref>, each territory that has a changed pixel
gets, as ovmain_build.py would give it, the largest group of its estimated people (pixel area x (development + 2)^1.5,
ice caps discounted), with ovmain_build.py's hand corrections (CURATED) kept. Then run ovsecond_build.py."""
import io, json, os, re, subprocess, sys
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'derive-2026'))
import era_tools as T
from popw import row_lat

SITE, TER, REF = sys.argv[1], sys.argv[2], sys.argv[3]
ROOT = subprocess.run(['git', '-C', SITE, 'rev-parse', '--show-toplevel'], capture_output=True, text=True).stdout.strip()
REL_SITE = os.path.relpath(os.path.abspath(SITE), ROOT)
src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ovmain_build.py'), encoding='utf-8').read()
CURATED = eval(src[src.index('CURATED = [') + len('CURATED = '):src.index(']\nfor names, y0, y1, rf, cf in CURATED') + 1])
ALIAS = json.loads(re.search(r'const ASSET_ALIAS = (\{.*?\});', open(SITE + 'atlas.js', encoding='utf-8').read()).group(1))
RI = json.load(open(SITE + 'data/religions.json'))['items']; CI = json.load(open(SITE + 'data/cultures.json'))['items']
RN = {x['n']: i + 1 for i, x in enumerate(RI)}; CN = {x['n']: i + 1 for i, x in enumerate(CI)}
H = 2111
lat_e = np.array([row_lat(y) for y in range(H + 1)]); A = np.abs(np.sin(lat_e[:-1]) - np.sin(lat_e[1:]))[:, None]
Tr = np.load(TER).astype(float); br = Tr.mean(axis=2); sat = Tr.max(axis=2) - Tr.min(axis=2)
HAB = np.where((br > 205) & (sat < 28), 0.03, 1.0)


def lab(img, layer):
    a = np.asarray(img.convert('RGB')).astype(np.int64)
    return a[..., 0] | (a[..., 1] << 8) if layer == 'cul' else a[..., 0]


def old(layer, f):
    b = subprocess.run(['git', '-C', ROOT, 'show', f'{REF}:{REL_SITE}/{layer}/{f}.png'], capture_output=True).stdout
    return lab(Image.open(io.BytesIO(b)), layer) if b else None


ovp = SITE + 'data/ovmain.json'; ov = json.load(open(ovp))
changed_n = 0
for e in json.load(open(SITE + 'data/eras.json'))['eras']:
    f, yr = e['f'], e['y']
    layers = {}
    for layer in ('rel', 'cul'):
        p = ALIAS.get(f'{layer}/{f}.png', f'{layer}/{f}.png')
        new = lab(Image.open(SITE + p), layer); o = old(layer, p[len(layer) + 1:-4])
        layers[layer] = (new, None if o is None else (new != o))
    if not any(c is not None and c.any() for _, c in layers.values()):
        continue
    js = json.load(open(SITE + f'eras/{f}.json')); ids = T.read_ids(js).astype(np.int64); n = len(js['ents']) + 1
    dp = SITE + ALIAS.get(f'dev/{f}.png', f'dev/{f}.png')
    dev = lab(Image.open(dp), 'rel').astype(float)
    w = (A * HAB * (dev + 2) ** 1.5).ravel(); flat = ids.ravel(); rows = ov['eras'][f]
    for col, layer, items, NM in ((0, 'rel', RI, RN), (1, 'cul', CI, CN)):
        L, ch = layers[layer]
        if ch is None or not ch.any(): continue
        k = len(items) + 1
        M = np.bincount(flat * k + L.ravel(), weights=w, minlength=n * k).reshape(n, k); M[:, 0] = 0
        na = next((i + 1 for i, x in enumerate(items) if x['id'] == 'na'), None)
        for ent in np.unique(ids[ch]):
            if ent == 0: continue
            en = js['ents'][ent - 1]['n']
            cur = [c for names, y0, y1, rf, cf in CURATED if en in names and y0 <= yr <= y1 for c in [(rf, cf)[col]] if c]
            if cur:
                best = NM[cur[0]]
            else:
                m = M[ent].copy(); tot = m.sum()
                if na and m[na] > 0.5 * tot: best = na
                else:
                    if na: m[na] = 0
                    best = int(m.argmax()) if m.max() > 0 else 0
            if best and rows[ent - 1][col] != best:
                rows[ent - 1][col] = best; changed_n += 1
open(ovp, 'w').write(json.dumps(ov, separators=(',', ':')))
print('main faith/culture changed on', changed_n, 'territory rows')
