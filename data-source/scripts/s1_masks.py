import cv2, sys
sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.abspath(__file__)))
from common import *

SH = 4; F = 1 << SH

def poly_pts(rings, w):
    out = []
    for r in rings:
        a = np.array(r, dtype=np.float64)
        x, y = proj(a[:, 0], a[:, 1], w)
        out.append(np.round(np.stack([x, y], 1) * F).astype(np.int32))
    return out

def raster_polys(feats, w, h, ss=2, filt=None):
    img = np.zeros((h * ss, w * ss), np.uint8)
    for f in feats:
        if filt and not filt(f): continue
        for poly in rings_of(f['geometry']):
            cv2.fillPoly(img, poly_pts(poly, w * ss), 255, lineType=cv2.LINE_8, shift=SH)
    if ss > 1:
        img = cv2.resize(img, (w, h), interpolation=cv2.INTER_AREA)
    return img

print('size', W, H)
land = raster_polys(load('ne_10m_land')['features'], W, H)
lakes = raster_polys(load('ne_10m_lakes')['features'], W, H)
glac = raster_polys(load('ne_10m_glaciated_areas')['features'], W, H)
water_land = np.clip(land.astype(np.int16) - lakes.astype(np.int16), 0, 255).astype(np.uint8)
np.save(f'{WORK}/land.npy', water_land)
np.save(f'{WORK}/lakes.npy', lakes)
np.save(f'{WORK}/glac.npy', glac)

# rivers (anti-aliased, width by scalerank)
riv = np.zeros((H * 2, W * 2), np.uint8)
for f in load('ne_10m_rivers_lake_centerlines')['features']:
    p = f['properties']; sr = p.get('scalerank', 10)
    if p.get('featurecla', '') not in ('River', 'Lake Centerline', 'Lake Centerline (Intermittent)', 'River (Intermittent)'):
        pass
    if sr > 8: continue
    th = {0: 4, 1: 4, 2: 4, 3: 3, 4: 3, 5: 2, 6: 2, 7: 2, 8: 1}.get(sr, 1)
    inter = 'Intermittent' in p.get('featurecla', '')
    for line in lines_of(f['geometry']):
        a = np.array(line, dtype=np.float64)
        x, y = proj(a[:, 0], a[:, 1], W * 2)
        pts = np.round(np.stack([x, y], 1) * F).astype(np.int32)
        cv2.polylines(riv, [pts], False, 150 if inter else 255, thickness=th, lineType=cv2.LINE_AA, shift=SH)
riv = cv2.resize(riv, (W, H), interpolation=cv2.INTER_AREA)
np.save(f'{WORK}/rivers.npy', riv)

# country id raster (nearest) + metadata
ctry = load('ne_10m_admin_0_countries')['features']
def area(f):
    s = 0
    for poly in rings_of(f['geometry']):
        a = np.array(poly[0]); s += abs(np.sum(a[:-1, 0] * a[1:, 1] - a[1:, 0] * a[:-1, 1])) / 2
    return s
ctry = [f for f in ctry if f['properties'].get('ADM0_A3') != 'ATA']
ctry.sort(key=lambda f: -area(f))
ids = np.zeros((H, W), np.uint16)
meta = []
for i, f in enumerate(ctry, start=1):
    for poly in rings_of(f['geometry']):
        cv2.fillPoly(ids, poly_pts(poly, W), i, lineType=cv2.LINE_8, shift=SH)
    p = f['properties']
    meta.append({k: p.get(k) for k in ['NAME', 'NAME_LONG', 'FORMAL_EN', 'ADM0_A3', 'ISO_A3', 'SOVEREIGNT', 'TYPE', 'CONTINENT', 'SUBREGION', 'POP_EST', 'POP_YEAR', 'GDP_MD', 'GDP_YEAR', 'MAPCOLOR9', 'MAPCOLOR13', 'NAME_EN']})
# lakes remove id
ids[lakes > 127] = 0
np.save(f'{WORK}/ids.npy', ids)
json.dump(meta, open(f'{WORK}/meta.json', 'w'))
print('countries', len(meta), 'land frac', (water_land > 127).mean())
