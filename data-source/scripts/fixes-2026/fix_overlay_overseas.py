"""Culture and religion layers: overseas and island territories given their modern country's people too early
(26 Oct 2026). Usage: python3 fix_overlay_overseas.py <site folder>

The culture and religion rules (../overlays/culture_rules.py, religion_rules.py) paint by modern country, and a
modern country includes its overseas parts. So French Guiana, Guadeloupe, Martinique, Reunion and Mayotte were
'French' (and before that Gauls, Gallo-Romans and Old European farmers, Celtic and Catholic) from prehistory, Bonaire
was Dutch from 1200, and the Azores, Madeira, Svalbard, the Galapagos and Easter Island had the peoples of Portugal,
Norway, Peru and Chile long before anyone lived there. This repaints those places on the existing rasters:

FIX-138 French overseas departments. French Guiana before French settlement (1664) and Guadeloupe and Martinique
        before 1635 take the culture and faith of their neighbours (the nearest pixels that do not carry the French
        rules' peoples or faiths). Reunion, uninhabited until 1665, is n/a before then. Mayotte is Swahili (Comorian)
        from its settlement, about 700, and Sunni from about 1500, also today, when it is still a Comorian, Muslim
        island; n/a before.
FIX-139 Bonaire before the Dutch (1636) takes its neighbours' culture and faith.
FIX-140 Late-settled islands: the Azores and Madeira (settled from 1420) and the Galapagos (1832) are n/a before
        then; Svalbard, with no settled population before the mining towns, is n/a before 1900; the Canary Islands
        are n/a before about 1000 BCE, and their Guanche faith is shown as Berber before the Castilian conquest
        (1496) instead of Iberian, Hellenic and Catholic; Easter Island is n/a before Polynesian settlement (about
        1000) and then Polynesian, in faith until the missions of 1864; the Falklands (2026 map: Amazonian peoples
        and South American religion) are n/a before 1833 and then English and Protestant; Bermuda is n/a before 1609,
        then English, and Afro-Caribbean from 1800, Protestant throughout; the Andaman and Nicobar Islands follow
        their own religions (shown as animism), not Hinduism, before the settlement of the 1950s.
FIX-141 Caribbean islands left with Native American religion (and some with hunter-gatherers) to the present day:
        Christian, Catholic or Protestant by island, from their colonisation; hunter-gatherers there become
        Afro-Caribbean. Also Saint Pierre and Miquelon, Catholic from 1650.
FIX-142 The Karelian Isthmus was drawn Russian and Orthodox from 1300 on modern Russia's outline. Its west, round
        Vyborg, was Swedish from 1293 and the whole isthmus from 1617 to 1944, with a Finnish, Lutheran population:
        Finnish and Catholic or Protestant on the 1300-1600 maps (west) and 1650-1938 maps (whole isthmus).

FIX-143 Island territories of states (under 3,000 pixels, with no land border) on the 1700-2026 maps kept a fringe
        of the world default, hunter-gatherers and animism, along their coasts (Jersey was half hunter-gatherers in
        2026). Where those coastal pixels are under half of the island, they take its main other culture or faith.
        Taiwan, whose coastal aboriginal peoples are real, is left as it is.

Areas in data/cultures.json and data/religions.json are adjusted by the pixels changed, and the main culture or
faith on a territory's card (data/ovmain.json) is recomputed by area where the old main one is gone from the territory,
or where the territory is mostly a repainted place and its old main one was repainted."""
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
KEEP_DEFAULT = {
    'Taiwan', 'Formosa', 'Republic of China (Taiwan)',   # Taiwanese aboriginal peoples are real
    'Kuril Islands',                                     # Ainu, until Japanese/Russian settlement
    'French Southern and Antarctic Lands', 'Heard Island and McDonald Islands',
    'South Georgia and the South Sandwich Islands',      # no permanent population to fill from
}


def box(x0, y0, x1, y1):
    """lon/lat box -> pixel slice of the era raster"""
    K = EW / (2 * math.pi)
    py = lambda lat: (YN - 1.25 * math.log(math.tan(math.pi / 4 + 0.4 * math.radians(lat)))) * K
    return (slice(max(0, int(py(y1))), min(EH, int(py(y0)) + 1)), slice(max(0, int((x0 + 180) / 360 * EW)), min(EW, int((x1 + 180) / 360 * EW) + 1)))


# (fix, place, box, first year, last year, layer, labels to replace (None: every land pixel), new label or 'nearest')
FR_C = ['old_euro', 'bronze_ie', 'gaulish', 'gallo_roman', 'french']
FR_R = ['old_european', 'celtic', 'hellenic', 'catholic']
NL_C = ['old_euro', 'bronze_ie', 'germanic', 'dutch']
NL_R = ['old_european', 'germanic', 'catholic', 'protestant']
B = -10 ** 7
R = []
def add(fix, place, bx, y0, y1, layer, labels, new):
    R.append((fix, place, bx, y0, y1, layer, labels, new))

GUIANA = [-54.7, 2.0, -51.5, 5.9]
ANTILLES_FR = [[-61.9, 15.8, -60.9, 16.6], [-61.3, 14.3, -60.7, 14.95]]
REUNION, MAYOTTE = [55.1, -21.5, 55.9, -20.8], [44.95, -13.05, 45.35, -12.6]
add('FIX-138', 'French Guiana', GUIANA, B, 1663, 'cul', FR_C, 'nearest')
add('FIX-138', 'French Guiana', GUIANA, B, 1663, 'rel', FR_R, 'nearest')
for bx in ANTILLES_FR:
    add('FIX-138', 'Guadeloupe and Martinique', bx, B, 1634, 'cul', FR_C, 'nearest')
    add('FIX-138', 'Guadeloupe and Martinique', bx, B, 1634, 'rel', FR_R, 'nearest')
add('FIX-138', 'Reunion', REUNION, B, 1664, 'cul', None, 'na')
add('FIX-138', 'Reunion', REUNION, B, 1664, 'rel', None, 'na')
add('FIX-138', 'Mayotte', MAYOTTE, B, 699, 'cul', None, 'na')
add('FIX-138', 'Mayotte', MAYOTTE, 700, 9999, 'cul', None, 'swahili')
add('FIX-138', 'Mayotte', MAYOTTE, B, 699, 'rel', None, 'na')
add('FIX-138', 'Mayotte', MAYOTTE, 700, 1499, 'rel', None, 'african')
add('FIX-138', 'Mayotte', MAYOTTE, 1500, 9999, 'rel', None, 'sunni')

BONAIRE = [-68.5, 12.0, -68.1, 12.4]
add('FIX-139', 'Bonaire', BONAIRE, B, 1635, 'cul', NL_C, 'nearest')
add('FIX-139', 'Bonaire', BONAIRE, B, 1635, 'rel', NL_R, 'nearest')

for place, bx, y in [('Azores', [-31.5, 36.8, -24.8, 39.8], 1419), ('Madeira', [-17.4, 32.3, -16.2, 33.2], 1419),
                     ('Galapagos', [-92.0, -1.6, -89.0, 0.8], 1831), ('Svalbard', [10.0, 74.0, 35.0, 81.0], 1899)]:
    add('FIX-140', place, bx, B, y, 'cul', None, 'na')
    add('FIX-140', place, bx, B, y, 'rel', None, 'na')
CANARIES = [-18.3, 27.6, -13.3, 29.5]
add('FIX-140', 'Canary Islands', CANARIES, B, -1001, 'cul', None, 'na')
add('FIX-140', 'Canary Islands', CANARIES, B, -1001, 'rel', None, 'na')
add('FIX-140', 'Canary Islands', CANARIES, -1000, 1495, 'rel', ['old_european', 'iberian', 'hellenic', 'catholic'], 'berber')
EASTER = [-109.5, -27.3, -109.1, -27.0]
add('FIX-140', 'Easter Island', EASTER, B, 999, 'cul', None, 'na')
add('FIX-140', 'Easter Island', EASTER, B, 999, 'rel', None, 'na')
add('FIX-140', 'Easter Island', EASTER, 1000, 1945, 'cul', None, 'polynesian')
add('FIX-140', 'Easter Island', EASTER, 1000, 1863, 'rel', None, 'oceanian')
FALKLANDS = [-61.5, -52.5, -57.6, -51.0]
add('FIX-140', 'Falkland Islands', FALKLANDS, B, 1832, 'cul', None, 'na')
add('FIX-140', 'Falkland Islands', FALKLANDS, B, 1832, 'rel', None, 'na')
add('FIX-140', 'Falkland Islands', FALKLANDS, 1833, 9999, 'cul', None, 'english')
add('FIX-140', 'Falkland Islands', FALKLANDS, 1833, 9999, 'rel', None, 'protestant')
BERMUDA = [-64.95, 32.2, -64.6, 32.45]
add('FIX-140', 'Bermuda', BERMUDA, B, 1608, 'cul', None, 'na')
add('FIX-140', 'Bermuda', BERMUDA, B, 1608, 'rel', None, 'na')
add('FIX-140', 'Bermuda', BERMUDA, 1609, 1799, 'cul', None, 'english')
add('FIX-140', 'Bermuda', BERMUDA, 1800, 9999, 'cul', None, 'afro_carib')
add('FIX-140', 'Bermuda', BERMUDA, 1609, 9999, 'rel', None, 'protestant')
add('FIX-140', 'Andaman and Nicobar Islands', [92.0, 6.5, 94.0, 13.7], B, 1959, 'rel', ['hindu'], 'animism')

CARIB = [  # place, box, religion, from
    ('Curacao', [-69.2, 12.0, -68.7, 12.4], 'catholic', 1700), ('Aruba', [-70.1, 12.4, -69.85, 12.65], 'catholic', 1700),
    ('Bonaire', BONAIRE, 'catholic', 1700), ('Trinidad', [-61.95, 10.0, -60.9, 10.9], 'catholic', 1700),
    ('Grenada', [-61.8, 11.95, -61.55, 12.25], 'catholic', 1700), ('Saint Lucia', [-61.1, 13.7, -60.85, 14.15], 'catholic', 1700),
    ('Dominica', [-61.5, 15.2, -61.2, 15.65], 'catholic', 1783), ('Saint Pierre and Miquelon', [-56.5, 46.7, -56.1, 47.15], 'catholic', 1650),
    ('Tobago', [-60.85, 11.1, -60.5, 11.4], 'protestant', 1800), ('Saint Vincent', [-61.3, 13.1, -61.1, 13.4], 'protestant', 1800),
    ('Antigua and Barbuda', [-61.95, 16.95, -61.65, 17.75], 'protestant', 1650), ('Saint Kitts and Nevis', [-62.9, 17.05, -62.5, 17.45], 'protestant', 1650),
    ('Montserrat', [-62.25, 16.65, -62.1, 16.85], 'protestant', 1650), ('US Virgin Islands', [-65.1, 17.65, -64.55, 18.45], 'protestant', 1700),
    ('British Virgin Islands', [-64.85, 18.3, -64.25, 18.8], 'protestant', 1700), ('Anguilla', [-63.2, 18.15, -62.95, 18.3], 'protestant', 1700),
    ('Cayman Islands', [-81.45, 19.25, -79.7, 19.8], 'protestant', 1800), ('Turks and Caicos Islands', [-72.5, 21.1, -71.0, 22.0], 'protestant', 1800),
]
for place, bx, faith, y in CARIB:
    add('FIX-141', place, bx, y, 9999, 'rel', ['native_na', 'animism', 'south_am'], faith)
    if place != 'Saint Pierre and Miquelon':
        add('FIX-141', place, bx, y, 9999, 'cul', ['foragers'], 'afro_carib')

ISTHMUS, ISTHMUS_W = [27.8, 60.1, 30.6, 61.2], [27.8, 60.1, 29.3, 61.2]
add('FIX-142', 'Karelian Isthmus', ISTHMUS_W, 1300, 1600, 'cul', ['russian'], 'finnish')
add('FIX-142', 'Karelian Isthmus', ISTHMUS_W, 1300, 1529, 'rel', ['orthodox'], 'catholic')
add('FIX-142', 'Karelian Isthmus', ISTHMUS_W, 1530, 1600, 'rel', ['orthodox'], 'protestant')
add('FIX-142', 'Karelian Isthmus', ISTHMUS, 1650, 1938, 'cul', ['russian'], 'finnish')
add('FIX-142', 'Karelian Isthmus', ISTHMUS, 1650, 1938, 'rel', ['orthodox'], 'protestant')


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
    for e in meta:
        y, key = e['y'], e['f']
        rules = [r for r in R if r[3] <= y <= r[4]]
        if not rules and y < 1700:
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
            if y >= 1700:   # FIX-143: the default's coastal fringe on small island states
                if ids is None:
                    js = J(f'{SITE}/eras/{key}.json'); ids = T.read_ids(js)
                dflt = ID['foragers' if layer == 'cul' else 'animism']
                cnt = np.bincount(ids.ravel(), minlength=len(js['ents']) + 1)
                coast = ndimage.binary_dilation(ids == 0, structure=np.ones((3, 3)))   # land pixels next to the sea
                objs = ndimage.find_objects(ids)
                for ent in np.unique(ids[(L == dflt) & coast]):
                    if ent == 0 or js['ents'][ent - 1].get('k') or cnt[ent] >= 3000 or js['ents'][ent - 1]['n'] in KEEP_DEFAULT:
                        continue
                    o = objs[ent - 1]
                    bx = (slice(max(0, o[0].start - 1), o[0].stop + 1), slice(max(0, o[1].start - 1), o[1].stop + 1))
                    sub_ids, sub_L = ids[bx], L[bx]
                    m = sub_ids == ent
                    ring = ndimage.binary_dilation(m, structure=np.ones((3, 3))) & ~m
                    if (sub_ids[ring] != 0).any():  # not an island: it has a land border
                        continue
                    v, c = np.unique(sub_L[m], return_counts=True)
                    keep = (v != dflt) & (v > 0)
                    if not keep.any() or c[v == dflt].sum() * 2 >= m.sum():
                        continue
                    fill = int(v[keep][np.argmax(c[keep])])
                    sel = m & (sub_L == dflt) & coast[bx]
                    sub_L[sel] = fill
                    log.append(('FIX-143', js['ents'][ent - 1]['n'], y, layer, int(sel.sum())))

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
