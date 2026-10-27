"""Culture and religion layers, second pass (26 Oct 2026). Usage: python3 fix_overlay_qc2.py <site folder>

Every culture and faith was checked for where it appears before its time (European peoples and Christianity outside
Europe before contact, modern nations before they formed):

FIX-158 Early medieval Europe: "French", "German", "Dutch" and "Italian" began on the 500 and 600 CE maps, three to four
        centuries before those languages and peoples (Old French and Old High German are first written in the 9th
        century). On the 500-800 maps they are Gallo-Romans (the Romance-speaking population of Frankish Gaul),
        Germanic tribes (Franks, Alemanni, Bavarians, Saxons, Thuringians) and Latin (Roman) Italy.
FIX-159 Arctic islands with no settled population were given the peoples and faiths of the mainland: Novaya Zemlya
        (Finnic, then Russian and Orthodox from 1400; Nenets settled there only in the 1870s) is n/a before 1871;
        Franz Josef Land, Severnaya Zemlya and the New Siberian Islands, never permanently inhabited, are n/a on every
        map; Wrangel Island (settled in 1926) is n/a before 1926.

Left as it is: Protestant Bohemia on the 1450-1500 maps is the Hussite (Utraquist) church, usually counted as the first
Reformation movement.

Areas in data/cultures.json and data/religions.json are adjusted by the pixels changed, and the main culture or faith
on a territory's card (data/ovmain.json) is recomputed by area where the old main one is gone from the territory, or
where the territory is mostly a repainted place and its old main one was repainted."""
import json, math, os, sys
import numpy as np
from PIL import Image
from scipy import ndimage
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'derive-2026'))
import era_tools as T

SITE = sys.argv[1]
J = lambda p: json.load(open(p, encoding='utf-8'))
EW, EH = T.EW, T.EH
YN = 1.988173047854812
meta = J(f'{SITE}/data/eras.json')['eras']
CUL, REL = J(f'{SITE}/data/cultures.json'), J(f'{SITE}/data/religions.json')
CID = {it['id']: i + 1 for i, it in enumerate(CUL['items'])}
RID = {it['id']: i + 1 for i, it in enumerate(REL['items'])}
KM = T.PIXKM


def box(x0, y0, x1, y1):
    """lon/lat box -> pixel slice of the era raster"""
    K = EW / (2 * math.pi)
    py = lambda lat: (YN - 1.25 * math.log(math.tan(math.pi / 4 + 0.4 * math.radians(lat)))) * K
    return (slice(max(0, int(py(y1))), min(EH, int(py(y0)) + 1)), slice(max(0, int((x0 + 180) / 360 * EW)), min(EW, int((x1 + 180) / 360 * EW) + 1)))


# (fix, place, box, first year, last year, layer, labels to replace (None: every land pixel), new label or 'nearest')
B = -10 ** 7
R = []
def add(fix, place, bx, y0, y1, layer, labels, new):
    R.append((fix, place, bx, y0, y1, layer, labels, new))

WEST_EU = [-10.0, 36.0, 20.0, 60.0]
add('FIX-158', 'Frankish Gaul', WEST_EU, 450, 899, 'cul', ['french'], 'gallo_roman')
add('FIX-158', 'Germany and the Low Countries', WEST_EU, 450, 899, 'cul', ['german', 'dutch'], 'germanic')
add('FIX-158', 'Italy', WEST_EU, 450, 899, 'cul', ['italian'], 'latin')
for place, bx, last in [('Novaya Zemlya', [51.4, 70.55, 61.0, 73.5], 1870), ('Novaya Zemlya', [54.0, 73.5, 69.2, 77.0], 1870),   # two boxes, clear of Yamal
                        ('Franz Josef Land', [44.0, 79.7, 66.0, 81.95], 9999),
                        ('Severnaya Zemlya', [89.0, 78.0, 107.5, 81.4], 9999),
                        ('New Siberian Islands', [134.0, 73.0, 158.0, 77.2], 9999),
                        ('Wrangel Island', [178.4, 70.6, 180.0, 71.7], 1925),
                        ('Wrangel Island', [-180.0, 70.6, -177.2, 71.7], 1925)]:
    add('FIX-159', place, bx, B, last, 'cul', None, 'na')
    add('FIX-159', place, bx, B, last, 'rel', None, 'na')

RENAME = {}


def read(layer, key):
    p = f'{SITE}/{layer}/{key}.png'
    if not os.path.exists(p):
        return None
    a = np.asarray(Image.open(p).convert('RGB')).astype(np.int32)
    return a[..., 0] + (a[..., 1] << 8) if layer == 'cul' else a[..., 0].copy()


def write(layer, key, L):
    p = f'{SITE}/{layer}/{key}.png'
    if layer == 'rel':
        Image.fromarray(L.astype(np.uint8), 'L').save(p, optimize=True)
    else:   # palette image whose colours carry the 16-bit culture index in red (low byte) and green (high byte)
        vals, inv = np.unique(L, return_inverse=True)
        assert len(vals) <= 256
        im = Image.fromarray(inv.reshape(L.shape).astype(np.uint8), 'P')
        pal = []
        for v in vals:
            pal += [int(v) & 255, int(v) >> 8, 0]
        im.putpalette(pal + [0] * (768 - len(pal)))
        im.save(p, optimize=True)
    try:
        import oxipng
        oxipng.optimize(p, level=4)
    except ImportError:
        pass


def main():
    log, ovm = [], J(f'{SITE}/data/ovmain.json')
    for cid, (n, d, w) in RENAME.items():
        for lst in ('items', 'faiths'):       # the file keeps the list under both names
            for it in CUL.get(lst, []):
                if it['id'] == cid:
                    it['n'], it['d'], it['w'] = n, d, w
    for e in meta:
        y, key = e['y'], e['f']
        rules = [r for r in R if r[3] <= y <= r[4]]
        if not rules:
            continue
        ids = None
        js = None
        for layer, ID, DATA, col in (('cul', CID, CUL, 1), ('rel', RID, REL, 0)):
            L = read(layer, key)
            if L is None:
                continue
            old = L.copy()
            for fix, place, bx, y0, y1, lay, labels, new in rules:
                if lay != layer:
                    continue
                sl = box(*bx)
                sub = L[sl]
                bad = (sub > 0) if labels is None else np.isin(sub, [ID[x] for x in labels])
                if not bad.any():
                    continue
                if new == 'nearest':
                    # the nearest pixel, in a window round the box, that is land and not one of the replaced labels
                    pad = 60
                    ys = slice(max(0, sl[0].start - pad), min(EH, sl[0].stop + pad)); xs = slice(max(0, sl[1].start - pad), min(EW, sl[1].stop + pad))
                    win = L[ys, xs]
                    ok = (win > 0) & ~np.isin(win, [ID[x] for x in labels])
                    if not ok.any():
                        continue
                    _, (iy, ix) = ndimage.distance_transform_edt(~ok, return_indices=True)
                    near = win[iy, ix][sl[0].start - ys.start: sl[0].stop - ys.start, sl[1].start - xs.start: sl[1].stop - xs.start]
                    sub[bad] = near[bad]
                else:
                    sub[bad] = ID[new]
                log.append((fix, place, y, layer, int(bad.sum())))
            ch = L != old
            if not ch.any():
                continue
            # areas: move the changed pixels' km2 from the old to the new label
            areas = {i: a for i, a in DATA['eras'][key]}
            rows = np.nonzero(ch)[0]
            for o, n, r in zip(old[ch], L[ch], rows):
                areas[int(o)] = areas.get(int(o), 0) - KM[r]
                areas[int(n)] = areas.get(int(n), 0) + KM[r]
            DATA['eras'][key] = [[i, int(round(a))] for i, a in sorted(areas.items(), key=lambda t: -t[1]) if round(a) > 0]
            # cards: a territory whose main culture or faith is no longer there at all, or that is mostly the repainted
            # place (half its pixels or more) and whose main one was repainted, gets the largest one it now has;
            # elsewhere the repainted islands are too small a part of the territory to change its main one (which
            # data/ovmain.json weighs by population)
            if ids is None:
                js = J(f'{SITE}/eras/{key}.json'); ids = T.read_ids(js)
            rowsv = ovm['eras'][key]
            for ent in np.unique(ids[ch]):
                if ent == 0:
                    continue
                m = ids == ent
                cur = rowsv[ent - 1][col]
                gone = not (m & (L == cur)).any()      # the old main one is no longer there at all
                if not gone and (not (ch & m & (old == cur)).any() or (ch & m).sum() * 2 < m.sum()):
                    continue
                v, c = np.unique(L[m & (L > 0)], return_counts=True)
                if len(v):
                    rowsv[ent - 1][col] = int(v[np.argmax(c)])
            write(layer, key, L)
    for path, D in ((f'{SITE}/data/cultures.json', CUL), (f'{SITE}/data/religions.json', REL)):
        json.dump(D, open(path, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    json.dump(ovm, open(f'{SITE}/data/ovmain.json', 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    for row in log:
        print(*row)


if __name__ == '__main__':
    main()
