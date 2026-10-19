"""Development layer: a CK3-style heat field of urban development for every era map.

Urban population (historical gazetteer in cities_hist.py, plus Natural Earth places scaled by regional urban growth from 1900)
is splatted onto the era raster and blurred at two scales (regional ~220 km and local ~45 km), turned into people per km2,
and mapped on a log scale.  The final value blends an absolute scale (so 2026 is brighter than 100 CE) with a scale relative
to that era's most developed area (so each era's cores stand out).  Land held by states gets a faint floor.
Outputs: site/dev/<key>.png (8-bit, 0-255) and site/data/develop.json (largest cities per era).
"""
import cv2, sys, json, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
from scipy.ndimage import gaussian_filter
from cities_hist import CITIES

EW, EH = W // 2, H // 2
os.makedirs(f'{OUT}/dev', exist_ok=True)
land8 = np.load(f'{WORK}/land.npy').astype(np.float32) / 255
LAND = cv2.resize(land8, (EW, EH), interpolation=cv2.INTER_AREA) > 0.5
del land8
LATR = inv_lat(np.arange(EH) + 0.5, EW)
R_ = 6371.0; dl = 2 * np.pi / EW
PIXKM = (R_ * R_ * np.cos(np.radians(LATR)) * dl * dl * np.cos(np.radians(0.8 * LATR))).astype(np.float64)

def interp(anchors, y):
    ks = sorted(anchors)
    if y < ks[0]: return 0.0
    if y >= ks[-1]: return float(anchors[ks[-1]]) if y - ks[-1] < 400 or anchors[ks[-1]] == 0 else 0.0
    for a, b in zip(ks, ks[1:]):
        if a <= y <= b:
            pa, pb = anchors[a], anchors[b]
            if pa <= 0 or pb <= 0:
                # founding or abandonment: linear
                return pa + (pb - pa) * (y - a) / (b - a)
            t = (y - a) / (b - a)
            return math.exp(math.log(pa) + (math.log(pb) - math.log(pa)) * t)
    return 0.0

# ------------------------------------------------------------------ Natural Earth places for the modern era
meta = json.load(open(f'{WORK}/meta.json'))
CONT = {m['ADM0_A3']: m['CONTINENT'] for m in meta}
# share of each place's c. 2020 population present in a given year, by continent
GROWTH = {
    'Europe':        {800: .01, 1000: .015, 1300: .03, 1500: .035, 1700: .06, 1800: .12, 1850: .25, 1900: .45, 1914: .50, 1930: .55, 1950: .60, 1960: .70, 1994: .90, 2000: .92, 2010: .96, 2026: 1.0},
    'North America': {1800: .01, 1850: .05, 1900: .17, 1914: .22, 1930: .30, 1950: .40, 1960: .50, 1994: .80, 2000: .85, 2010: .93, 2026: 1.0},
    'South America': {1800: .01, 1850: .02, 1900: .05, 1914: .07, 1930: .10, 1950: .15, 1960: .25, 1994: .70, 2000: .75, 2010: .88, 2026: 1.0},
    'Asia':          {-500: .01, 1000: .02, 1500: .025, 1800: .025, 1850: .03, 1900: .05, 1914: .06, 1930: .08, 1950: .12, 1960: .17, 1994: .55, 2000: .62, 2010: .82, 2026: 1.0},
    'Africa':        {1850: .01, 1900: .02, 1914: .025, 1930: .03, 1950: .05, 1960: .08, 1994: .40, 2000: .48, 2010: .70, 2026: 1.0},
    'Oceania':       {1850: .05, 1900: .20, 1914: .25, 1930: .30, 1950: .40, 1960: .50, 1994: .80, 2000: .85, 2010: .92, 2026: 1.0},
}
ne = json.load(open(f'{S}/dl/ne_10m_populated_places_simple.geojson'))['features'] if os.path.exists(f'{S}/dl/ne_10m_populated_places_simple.geojson') else []
NAFRICA = {'EGY', 'LBY', 'TUN', 'DZA', 'MAR'}
NE = []
for f in ne:
    p = f['properties']; pop = p.get('pop_max') or 0
    if pop < 20000: continue
    lon, lat = p['longitude'], p['latitude']
    if any(abs(lon - c[1]) < 0.35 and abs(lat - c[2]) < 0.35 for c in CITIES): continue
    cont = CONT.get(p.get('adm0_a3'), 'Asia')
    if cont not in GROWTH: cont = 'North America' if cont.startswith('North') else 'South America' if cont.startswith('South') else 'Asia'
    if p.get('adm0_a3') in NAFRICA: cont = 'Asia'
    NE.append((p['name'], lon, lat, pop / 1000.0, cont))
print('NE places', len(NE))


def ne_factor(cont, y):
    return interp(GROWTH[cont], y)

# names that changed over time: (name in the gazetteer) -> [(from year, name), ...]
RENAME = {
    'Edo (Tokyo)': [(-9999, 'Edo'), (1868, 'Tokyo')],
    "Chang'an (Xi'an)": [(-9999, "Chang'an"), (904, "Xi'an")],
    'Tenochtitlan (Mexico City)': [(-9999, 'Tenochtitlan'), (1521, 'Mexico City')],
    'Batavia (Jakarta)': [(-9999, 'Batavia'), (1942, 'Jakarta')],
    'Constantinople': [(-9999, 'Byzantium'), (330, 'Constantinople'), (1930, 'Istanbul')],
    'Ava (Mandalay)': [(-9999, 'Ava'), (1857, 'Mandalay')],
    'Pingcheng (Datong)': [(-9999, 'Pingcheng'), (1048, 'Datong')],
    'Ye (Handan)': [(-9999, 'Ye')],
    'Yinxu (Anyang)': [(-9999, 'Yin (Anyang)')],
    'Saigon': [(-9999, 'Saigon'), (1976, 'Ho Chi Minh City')],
    'St Petersburg': [(-9999, 'St Petersburg'), (1914, 'Petrograd'), (1924, 'Leningrad'), (1991, 'St Petersburg')],
    'Mumbai': [(-9999, 'Bombay'), (1995, 'Mumbai')],
    'Chennai': [(-9999, 'Madras'), (1996, 'Chennai')],
    'Kolkata': [(-9999, 'Calcutta'), (2001, 'Kolkata')],
    'Yangon': [(-9999, 'Rangoon'), (1989, 'Yangon')],
    'Kiev': [(-9999, 'Kiev'), (1994, 'Kyiv')],
    'Smyrna': [(-9999, 'Smyrna'), (1930, 'Izmir')],
    'Adrianople': [(-9999, 'Adrianople'), (1930, 'Edirne')],
    'Trebizond': [(-9999, 'Trebizond'), (1930, 'Trabzon')],
    'Thessalonica': [(-9999, 'Thessalonica'), (1937, 'Thessaloniki')],
    'Pataliputra': [(-9999, 'Pataliputra'), (1500, 'Patna')],
    'Urga': [(-9999, 'Urga'), (1924, 'Ulaanbaatar')],
    'Hamadan': [(-9999, 'Ecbatana'), (700, 'Hamadan')],
    'Gyeongju': [(-9999, 'Gyeongju (Seorabeol)')],
    'Seoul': [(-9999, 'Hanyang'), (1945, 'Seoul')],
    'Cairo': [(-9999, 'Fustat'), (970, 'Cairo')],
    'Ragusa': [(-9999, 'Ragusa'), (1918, 'Dubrovnik')],
    'Lubeck': [(-9999, 'Lubeck')],
    'Ctesiphon': [(-9999, 'Seleucia-Ctesiphon')],
}
def disp(name, y):
    r = RENAME.get(name)
    if not r: return name
    out = r[0][1]
    for y0, n in r:
        if y >= y0: out = n
    return out

idx = json.load(open(f'{OUT}/data/eras.json'))
SIG_BIG, SIG_MID, SIG_SMALL = 30.0, 9.0, 3.5
L0, L1 = math.log10(0.05), math.log10(80.0)
out = {}
for meta_e in idx['eras']:
    y, key = meta_e['y'], meta_e['f']
    grid = np.zeros((EH, EW), np.float64); grid_s = np.zeros((EH, EW), np.float64); grid_m = np.zeros((EH, EW), np.float64)
    pts = []
    for name, lon, lat, anc in CITIES:
        pk = interp(anc, y)
        if pk > 0.5: pts.append((name, lon, lat, pk, 0))
    for name, lon, lat, pk, cont in NE:
        f = ne_factor(cont, y)
        if y < 1850:
            # before 1850 modern towns only stand in for the historical town network of the old farming heartlands
            if lon > 58 and lat > 50 and y < 1750: continue                       # Siberia before Russian settlement
            if cont == 'Europe' and lon > 44 and y < 1600: continue                # Volga and Urals before Muscovy
            v = min(pk * f, 10.0)
            if cont == 'Europe' and y < 1750:                                          # thinly urbanised north and east, fading smoothly
                v *= 1 - 0.7 * min(1.0, max(0.0, (lon - 11) / 14, (lat - 54) / 5))
            if cont == 'Asia' and lat > 44 and y < 1800: v *= 0.4                       # steppe and Manchuria
        else:
            v = pk * f
            if cont == 'Europe' and lon > 20 and y < 1930: v *= 0.45                # eastern Europe urbanised late
            if cont == 'Asia' and y < 1950: v *= 0.7
        if f > 0 and v > 2: pts.append((name, lon, lat, v, 1 if y < 1850 else 0))
    for name, lon, lat, pk, proxy in pts:
        x, yy = proj(lon, lat, EW)
        xi, yi = int(x) % EW, min(EH - 1, max(0, int(yy)))
        grid[yi, xi] += pk * 1000.0
        if not proxy: grid_s[yi, xi] += pk * 1000.0; grid_m[yi, xi] += pk * 1000.0
    big = gaussian_filter(grid, SIG_BIG, mode=('nearest', 'wrap'), truncate=3.5)
    mid = gaussian_filter(grid_m, SIG_MID, mode=('nearest', 'wrap'), truncate=3.5)
    small = gaussian_filter(grid_s, SIG_SMALL, mode=('nearest', 'wrap'), truncate=3.5)
    def score(D, lo, hi):
        lg = np.log10(D + 1e-9)
        ab = np.clip((lg - lo) / (hi - lo), 0, 1)
        m = LAND & (D > 10 ** lo)
        ref = np.percentile(lg[m], 99.8) if m.sum() > 50 else hi
        rel = np.clip((lg - lo) / max(0.6, ref - lo), 0, 1)
        return 0.4 * ab + 0.6 * rel
    # the bar for "developed" rises as the world urbanises, so modern maps keep their contrast
    lo_r = interp({-5000: 0.03, 1700: 0.03, 1850: 0.06, 1900: 0.12, 1950: 0.3, 2000: 0.9, 2026: 1.2}, max(y, -5000))
    hi_r = interp({-5000: 30.0, 1700: 30.0, 1900: 80.0, 2000: 250.0, 2026: 300.0}, max(y, -5000))
    reg = score(big / PIXKM[:, None], math.log10(lo_r), math.log10(hi_r))              # regional (~270 km)
    mid = score(mid / PIXKM[:, None], math.log10(lo_r * 3), math.log10(hi_r * 8))      # town hinterlands (~80 km)
    loc = score(small / PIXKM[:, None], math.log10(0.5), math.log10(3000.0))           # the cities themselves
    dev = np.clip(0.22 * reg ** 1.8 + 0.72 * mid ** 1.55 + 0.24 * loc ** 1.4, 0, 1)
    # faint floor on land held by states (farming kingdoms are never wholly undeveloped)
    im = cv2.imread(f'{OUT}/eras/{key}.png')
    ids = im[..., 2].astype(np.int32) | (im[..., 1].astype(np.int32) << 8)
    js = json.load(open(f'{OUT}/eras/{key}.json'))
    state_ids = np.array([0] + [0 if e.get('k') else 1 for e in js['ents']], np.uint8)
    statel = state_ids[np.clip(ids, 0, len(state_ids) - 1)].astype(bool)
    dev = np.where(statel, np.maximum(dev, 0.03), dev)
    dev[~LAND] = 0
    cv2.imwrite(f'{OUT}/dev/{key}.png', np.round(dev * 255).astype(np.uint8), [cv2.IMWRITE_PNG_COMPRESSION, 9])
    pts.sort(key=lambda t: -t[3])
    seen, top = [], []
    for name, lon, lat, pk, proxy in pts:
        if proxy: continue
        if any(abs(lon - a) < 0.4 and abs(lat - b) < 0.4 for a, b in seen): continue
        seen.append((lon, lat)); top.append([disp(name, y), round(lon, 3), round(lat, 3), int(round(pk))])
        if len(top) >= 40: break
    out[key] = {'top': top}
    print(y, 'cities', len(pts), 'max dev', round(float(dev.max()), 2), 'top', top[0][0] if top else '-', flush=True)
json.dump({'eras': out}, open(f'{OUT}/data/develop.json', 'w'), separators=(',', ':'), ensure_ascii=True)
