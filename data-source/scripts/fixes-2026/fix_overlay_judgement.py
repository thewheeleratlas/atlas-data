"""Culture layer: judgement calls on peoples the modern-country rules carried too far back or too far out
(26 Oct 2026). Usage: python3 fix_overlay_judgement.py <site folder>

The culture rules (../overlays/culture_rules.py) paint by modern country and province, so some places show a people
before it arrived or a neighbour's people instead of their own. Repainted on the existing rasters:

FIX-144 South Slavs before they settled. On the 600 map the Balkans were already Bulgarian, Serbian, Croatian and
        Slovene; the Slavs crossed the Danube from the 580s, the Serbs and Croats are dated to the 620s-630s and the
        Bulgars arrived in 681. They are Early Slavs on the 600 map, and North Macedonia, Bulgarian only from the
        840s, also on the 700 and 800 maps.
FIX-145 Guinea-Bissau's east (Gabu, Bafata) was the Mandinka kingdom of Kaabu from the 13th century until the Fula
        took Kansala in 1867: Mande on the 1279-1848 maps, Fula from 1871. It was drawn as the coastal Atlantic
        peoples throughout.
FIX-146 Panama: its Caribbean coast was "hunter-gatherers" on every map; its peoples (Guna, Ngabe, Bugle) are
        Chibchan, shown from the 500 BCE map (the Gran Cocle cultures). The Isthmus route (Panama City, founded 1519, Nombre de Dios and Portobelo) is Spanish-colonial
        (Central American) from the 1530 map, not Chibchan until 1800.
FIX-147 Texas was Caddo from the Red River to the Rio Grande until 1848 (San Antonio until 1871). The Caddo lived in
        the east; south-central Texas (San Antonio to the Gulf) was Coahuiltecan before 1700, Lipan Apache on the
        1700 and 1715 maps and Comanche (Comancheria) on the 1750-1815 maps, and American from Texan
        independence (1848 map on).
FIX-148 Danzig (Gdansk), Elbing (Elblag), Marienburg (Malbork), Marienwerder (Kwidzyn) and the Vistula delta were
        Polish from 900 to today. Their towns and the delta were German-speaking from the Teutonic Order's takeover
        (1308) to 1945: German on the 1400-1938 maps. The Kashubian countryside to the west is unchanged.

Also in data/cultures.json: "Serbian" is renamed "Serbian and Montenegrin" (Montenegro was drawn Serbian; most
Montenegrins counted themselves Serbs until Yugoslavia recognised a Montenegrin nation in 1945).

Areas in data/cultures.json are adjusted by the pixels changed, and the main culture on a territory's card
(data/ovmain.json) is recomputed by area where the old main one is gone from the territory, or where the territory
is mostly a repainted place and its old main one was repainted."""
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

add('FIX-144', 'Balkans', [13.3, 39.5, 29.8, 47.0], 600, 600, 'cul', ['bulgarian', 'serbian', 'croatian', 'slovene', 'bosniak'], 'slavic')
add('FIX-144', 'North Macedonia', [20.4, 40.85, 23.05, 42.4], 700, 800, 'cul', ['bulgarian'], 'slavic')
KAABU = [-15.0, 10.9, -13.6, 12.7]
add('FIX-145', 'Kaabu (eastern Guinea-Bissau)', KAABU, 1250, 1866, 'cul', ['kru'], 'mande')
add('FIX-145', 'Kaabu (eastern Guinea-Bissau)', KAABU, 1867, 9999, 'cul', ['kru'], 'fula')
add('FIX-146', 'Panama', [-83.1, 7.0, -77.15, 9.75], -500, 9999, 'cul', ['foragers'], 'muisca')
add('FIX-146', 'Isthmus of Panama', [-80.3, 8.6, -78.95, 9.7], 1520, 9999, 'cul', ['muisca'], 'central_am')
STX = [-100.0, 27.8, -96.3, 31.0]
add('FIX-147', 'South-central Texas', STX, B, 1699, 'cul', ['caddoan'], 'aridoamerican')
add('FIX-147', 'South-central Texas', STX, 1700, 1740, 'cul', ['caddoan'], 'apache')
add('FIX-147', 'South-central Texas', STX, 1741, 1835, 'cul', ['caddoan'], 'numic')
add('FIX-147', 'South-central Texas', STX, 1836, 9999, 'cul', ['caddoan'], 'anglo_american')
add('FIX-148', 'Danzig and the Vistula delta', [18.45, 53.65, 19.75, 54.45], 1308, 1944, 'cul', ['polish'], 'german')

RENAME = {'serbian': ('Serbian and Montenegrin', 'The Serbs of Serbia and eastern Bosnia, and the Montenegrins, who mostly counted themselves Serbs until Yugoslavia recognised a Montenegrin nation in 1945.', 'Serbs and Montenegrins')}


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
