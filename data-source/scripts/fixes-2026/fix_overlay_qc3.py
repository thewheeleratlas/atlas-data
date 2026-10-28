"""Culture and religion layers, the Americas and Africa (28 Oct 2026). Usage: python3 fix_overlay_qc3.py <site folder>

Two fact-checks of the layers (a 5-degree grid of the Americas and a 4-degree grid of Africa, on 12 maps from 3000 BCE
to 2026) found peoples painted where or when they did not live, and faiths painted before they arrived or where
another is the majority. Repainted on the existing rasters, inside the stated boxes (lon/lat, approximate) and only
over the stated labels:

FIX-214 The southern Plains: the Comanche (a new culture item, parted from the Great Basin peoples) only from 1750,
        where they lived (30-39 N, 104-97 W); the Mescalero Apache's land in south-east New Mexico, and the Plains
        Apache on the Llano Estacado before 1750, not Comanche or Caddoan; the Lipan Apache and the Coahuiltecan
        peoples on the Edwards Plateau; the Pawnee on the Republican River; Hispanic eastern New Mexico (1880-2026).
FIX-215 North America to 1900: Chickasaw west Tennessee and Cherokee north Georgia (1783-1815) and the Abenaki
        interior of Maine (1650-1715), not Anglo-American; native religion in Spanish East Texas and on the Edwards
        Plateau (1750-1815); Cochimí northern Baja California before 1752; Cree and Innu inland Quebec and Dene on the
        Liard (1880-1945); Catholic and Anglican missions in the subarctic (1900-1945).
FIX-216 Today's majority faiths: Protestant Honduras; Catholic south Texas, southern New England, eastern Ontario and
        northern New Brunswick (2010, 2026).
FIX-217 Mesoamerica, the Andes and the Caribbean before contact: the Nahua arrived about 500 CE (Otomanguean peoples
        in central Mexico before then, n/a in the west); early Andeans, not Amazonians, on the Peruvian coast in 3000
        BCE; the coastal Ecuadorian peoples (a new item) from Valdivia to the Manteño, not Amazonian or Quechua;
        Andean religion at Nazca and Paracas; foragers in eastern Cuba before the Ostionoid farmers and on the
        Brazilian coast before the Tupi.
FIX-218 South America after contact: Catholic Potosí and Charcas (1600-1815) and Guaraní missions (1700-1750); the
        Pampas and southern Cuyo were Ranquel, Pehuenche and Tehuelche land until the 1879 campaign, with native
        religion; Mapuche, not Diaguita, at 35 S (1530-1650); Amazonian, Ge and Chaco peoples, with native religion,
        in the Colombian Amazon, the Xingu, Mato Grosso do Sul and the Chaco Boreal before their colonisation.
FIX-219 Africa, peoples: Bantu farmers by the Great Lakes from about 500 BCE; Khoisan on the highveld (to 1300), in
        the Kalahari (to 1715) and in northern Namibia (300-900); the Habesha (Ge'ez-speaking) peoples of Aksum (from
        700 BCE) and Christian Shewa (1279-1530), not Cushitic; Cushitic, not Somali, on the Juba before 900; Sudanese
        Arabs, not Central Sudanic, in the Gezira (1450-1530); the Toubou at Kufra (to 1815) and the Tuareg in the
        Adrar des Ifoghas, not Arabs; West African peoples, not Hausa, before 1000.
FIX-220 Africa, faiths: Islam among the Hausa from 1800 and in Senegambia from 1880, but not yet among the inland
        Makua (to 1815), the Somali interior (1000) or southern Ethiopia (to 1938, Protestant today); Orthodox Shewa
        (1800-2026); Kongo's court Catholic from 1491 but not the kingdom until 1509; Christianity today on Kilimanjaro;
        Islam in northern Ghana today; Nubian Isis worship to 537; native religion in the Danakil (300-900).

Areas in data/cultures.json and data/religions.json follow the pixels changed; the main culture or faith on a card
(data/ovmain.json) is recomputed where its old one is gone or was repainted over most of the territory.
Afterwards run overlays/ovsecond_build.py."""
import json, math, os, sys
import numpy as np
from PIL import Image
from scipy import ndimage
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'derive-2026')); sys.path.insert(0, os.path.join(HERE, '..', 'overlays'))
import era_tools as T
import culture_rules

SITE = sys.argv[1]
J = lambda p: json.load(open(p, encoding='utf-8'))
EW, EH = T.EW, T.EH
YN = 1.988173047854812
meta = J(f'{SITE}/data/eras.json')['eras']
CUL, REL = J(f'{SITE}/data/cultures.json'), J(f'{SITE}/data/religions.json')
have = {it['id'] for it in CUL['items']}
for f in culture_rules.FAITHS[[x['id'] for x in culture_rules.FAITHS].index('na') + 1:]:
    if f['id'] not in have: CUL['items'].append({k: f[k] for k in ('id', 'n', 'fam', 'c', 'd', 'w') if k in f})
CUL['faiths'] = CUL['items']
assert [x['id'] for x in CUL['items']] == [x['id'] for x in culture_rules.FAITHS], 'cultures.json and culture_rules.py differ'
CID = {it['id']: i + 1 for i, it in enumerate(CUL['items'])}
RID = {it['id']: i + 1 for i, it in enumerate(REL['items'])}
KM = T.PIXKM


def box(x0, y0, x1, y1):
    """lon/lat box -> pixel slice of the era raster"""
    K = EW / (2 * math.pi)
    py = lambda lat: (YN - 1.25 * math.log(math.tan(math.pi / 4 + 0.4 * math.radians(lat)))) * K
    return (slice(max(0, int(py(y1))), min(EH, int(py(y0)) + 1)), slice(max(0, int((x0 + 180) / 360 * EW)), min(EW, int((x1 + 180) / 360 * EW) + 1)))


R = []
def add(fix, place, bx, y0, y1, layer, labels, new):     # bx = [lon0, lat0, lon1, lat1]
    R.append((fix, place, bx, y0, y1, layer, labels, new))

# FIX-214 the southern Plains (the Mescalero first, so the Comanche split below does not reach their land)
add('FIX-214', 'Mescalero lands, south-east New Mexico', [-106.3, 32.0, -104.2, 34.5], 1650, 1871, 'cul', ['numic'], 'apache')
add('FIX-214', 'Llano Estacado (Plains Apache)', [-104, 32, -98, 38], 1650, 1715, 'cul', ['numic'], 'apache')
add('FIX-214', 'Llano Estacado (Querechos)', [-104, 32, -100, 37], 1530, 1600, 'cul', ['caddoan'], 'apache')
add('FIX-214', 'Edwards Plateau', [-102, 28, -98, 31], 1650, 1715, 'cul', ['numic'], 'aridoamerican')
add('FIX-214', 'Edwards Plateau (Lipan)', [-102, 28, -98, 31], 1750, 1815, 'cul', ['numic'], 'apache')
add('FIX-214', 'Republican River (Pawnee)', [-101, 39, -97, 42], 1783, 1815, 'cul', ['numic'], 'caddoan')
add('FIX-214', 'Comanchería', [-104, 30, -97, 39], 1750, 1871, 'cul', ['numic'], 'comanche')
add('FIX-214', 'Eastern New Mexico (Hispano)', [-105.5, 34, -103, 37], 1880, 9999, 'cul', ['apache'], 'mexican')
# FIX-215
add('FIX-215', 'West Tennessee (Chickasaw)', [-90, 34, -88, 36.5], 1783, 1815, 'cul', ['anglo_american'], 'muskogean')
add('FIX-215', 'West Tennessee (Chickasaw)', [-90, 34, -88, 36.5], 1783, 1815, 'rel', ['protestant'], 'native_na')
add('FIX-215', 'North Georgia (Cherokee)', [-86, 34, -83.5, 35.5], 1783, 1815, 'cul', ['anglo_american'], 'iroquoian')
add('FIX-215', 'North Georgia (Cherokee)', [-86, 34, -83.5, 35.5], 1783, 1815, 'rel', ['protestant'], 'native_na')
add('FIX-215', 'Interior Maine (Abenaki)', [-71, 44.5, -68, 47], 1650, 1715, 'cul', ['anglo_american'], 'algonquian')
add('FIX-215', 'Interior Maine (Abenaki)', [-71, 44.5, -68, 47], 1650, 1715, 'rel', ['protestant'], 'native_na')
add('FIX-215', 'East Texas coast', [-97, 28, -93, 31], 1750, 1815, 'rel', ['catholic'], 'native_na')
add('FIX-215', 'Edwards Plateau', [-102, 28, -98, 31], 1750, 1815, 'rel', ['catholic'], 'native_na')
add('FIX-215', 'Northern Baja California (Cochimí)', [-117, 28, -113, 32.5], 1650, 1750, 'cul', ['mexican'], 'aridoamerican')
add('FIX-215', 'Inland Quebec (Cree and Innu)', [-76, 49.5, -69, 52], 1880, 1945, 'cul', ['quebecois'], 'algonquian')
add('FIX-215', 'Liard (Dene)', [-131, 58, -122, 62], 1880, 1945, 'cul', ['anglo_canadian'], 'dene')
add('FIX-215', 'Western subarctic (Oblate missions)', [-135, 54, -100, 68], 1900, 1945, 'rel', ['native_na'], 'catholic')
add('FIX-215', 'Hudson Bay lowlands (Anglican missions)', [-95, 50, -78, 58], 1900, 1945, 'rel', ['native_na'], 'protestant')
# FIX-216
add('FIX-216', 'Honduras', [-89.4, 13, -83.2, 16.5], 2010, 9999, 'rel', ['catholic'], 'protestant')
for place, bx in (('South Texas', [-101, 26, -97, 30]), ('Southern New England', [-72, 41, -70, 42.9]),
                  ('Eastern Ontario', [-77, 45, -74, 46.5]), ('Northern New Brunswick', [-67, 45.5, -64, 48])):
    add('FIX-216', place, bx, 2010, 9999, 'rel', ['protestant'], 'catholic')
# FIX-217
add('FIX-217', 'Central Mexico before the Nahua', [-101, 18, -98, 23], -5000, 400, 'cul', ['nahua'], 'otomanguean')
add('FIX-217', 'West Mexico before the Nahua', [-106, 18, -101, 23], -5000, 400, 'cul', ['nahua'], 'na')
add('FIX-217', 'Peruvian coast and highlands', [-81, -16, -75, -3], -4000, -2000, 'cul', ['amazonian'], 'chavin')
add('FIX-217', 'Coastal Ecuador', [-81, -3, -79, 1.5], -4000, 1530, 'cul', ['amazonian', 'quechua'], 'coastal_ecuador')
add('FIX-217', 'Nazca and Paracas', [-77, -17, -74, -12], -1000, 1530, 'rel', ['south_am'], 'andean')
add('FIX-217', 'Ica (colonial)', [-77, -17, -74, -12], 1531, 1914, 'rel', ['south_am'], 'catholic')
add('FIX-217', 'Eastern Cuba', [-78, 19, -74, 21], -400, 600, 'cul', ['arawak'], 'foragers')
add('FIX-217', 'Brazilian Atlantic coast', [-50, -30, -34, -3], -1500, -200, 'cul', ['tupi'], 'foragers')
# FIX-218
add('FIX-218', 'Potosí and Charcas', [-67, -22, -63, -18], 1600, 1815, 'rel', ['south_am'], 'catholic')
add('FIX-218', 'Guaraní missions', [-57, -30, -53, -27], 1700, 1750, 'rel', ['south_am'], 'catholic')
add('FIX-218', 'Pampas and southern Cuyo', [-71, -37, -62.5, -33.5], 1530, 1871, 'rel', ['catholic'], 'south_am')
add('FIX-218', 'Pampas (Ranquel and Tehuelche)', [-69, -37, -62.5, -33.5], 1650, 1871, 'cul', ['argentine'], 'patagonian')
add('FIX-218', 'Southern Cuyo (Pehuenche)', [-71, -37, -69, -33.5], 1650, 1871, 'cul', ['argentine'], 'mapuche')
add('FIX-218', 'Southern Chile at 35 S', [-71, -36, -69, -34], 1530, 1650, 'cul', ['diaguita'], 'mapuche')
for place, bx, old, new, y0, y1 in (('Colombian Amazon', [-75, -2, -69, 2], 'colombian', 'amazonian', 1650, 1900),
                                    ('Xingu and Araguaia', [-57, -12, -48, -6], 'brazilian', 'ge', 1700, 1900),
                                    ('Mato Grosso do Sul (Mbayá)', [-57, -22, -53, -18], 'brazilian', 'chaco', 1750, 1815),
                                    ('Chaco Boreal', [-62, -22, -58, -19], 'paraguayan', 'chaco', 1650, 1914)):
    add('FIX-218', place, bx, y0, y1, 'cul', [old], new)
    add('FIX-218', place, bx, y0, y1, 'rel', ['catholic'], 'south_am')
# FIX-219
add('FIX-219', 'Great Lakes (Urewe farmers)', [28, -6, 34, 1], -550, 600, 'cul', ['khoisan'], 'bantu')
add('FIX-219', 'Highveld and Karoo', [23, -31, 28, -25], 300, 1300, 'cul', ['bantu', 'sotho'], 'khoisan')
add('FIX-219', 'Kalahari', [16, -25, 24, -21], 300, 1715, 'cul', ['bantu'], 'khoisan')
add('FIX-219', 'Northern Namibia', [12, -21, 20, -17], 300, 900, 'cul', ['bantu'], 'khoisan')
add('FIX-219', 'Aksum highlands', [36.5, 12, 40, 16], -700, 700, 'cul', ['cushitic'], 'habesha')
add('FIX-219', 'Shewa', [37, 8, 40, 11], 1279, 1530, 'cul', ['cushitic'], 'habesha')
add('FIX-219', 'Juba valley', [40, -2, 43, 3], -550, 900, 'cul', ['somali'], 'cushitic')
add('FIX-219', 'Gezira', [32, 12, 35.5, 15], 1450, 1530, 'cul', ['sudanic'], 'sudanese_arab')
add('FIX-219', 'Kufra', [20, 23, 24, 27], 1450, 1815, 'cul', ['arab'], 'toubou')
add('FIX-219', 'Adrar des Ifoghas', [0, 19, 4, 23], 1450, 9999, 'cul', ['arab'], 'tuareg')
add('FIX-219', 'Hausaland before the Hausa states', [4, 9, 16, 18], -1000, 900, 'cul', ['hausa'], 'w_african')
# FIX-220
add('FIX-220', 'Hausaland', [8, 11, 12, 15], 1800, 9999, 'rel', ['african'], 'sunni')
add('FIX-220', 'Senegambia', [-16, 11, -12, 15], 1880, 9999, 'rel', ['african'], 'sunni')
add('FIX-220', 'Kilimanjaro and Tsavo', [36, -5, 40, -1], 1960, 9999, 'rel', ['african'], 'protestant')
add('FIX-220', 'Inland Makua', [36, -17, 39.5, -13], 1500, 1815, 'rel', ['sunni'], 'african')
add('FIX-220', 'Kongo (before Afonso I)', [12, -9, 16, -5], 1491, 1508, 'rel', ['catholic'], 'african')
add('FIX-220', 'Shewa', [37, 8, 40, 10.5], 1800, 9999, 'rel', ['sunni'], 'oriental')
add('FIX-220', 'Southern Ethiopia', [36, 3, 40, 7], 1783, 1938, 'rel', ['sunni'], 'african')
add('FIX-220', 'Southern Ethiopia', [36, 3, 40, 7], 2010, 9999, 'rel', ['sunni'], 'protestant')
add('FIX-220', 'Northern Ghana', [-3, 8.5, 0, 11], 2010, 9999, 'rel', ['african'], 'sunni')
add('FIX-220', 'Somali interior', [40, -1, 48, 7], 900, 1100, 'rel', ['sunni'], 'african')
add('FIX-220', 'Danakil', [40, 11, 43, 14], 300, 900, 'rel', ['oriental'], 'african')
add('FIX-220', 'Nubia (Nobatia)', [25, 18, 34, 24], 400, 500, 'rel', ['animism'], 'egyptian')

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
