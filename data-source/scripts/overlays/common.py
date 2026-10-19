import numpy as np, json, math, os
# Paths are configurable: set HHA_WORKDIR (inputs + scratch) and HHA_SITE (output site folder).
S = os.environ.get('HHA_WORKDIR', os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'workdir')))
DL = S + '/dl'
BM = S + '/bm'
WORK = S + '/work'
OUT = os.environ.get('HHA_SITE', os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'site')))
os.makedirs(WORK, exist_ok=True)

# Miller cylindrical, cropped
LAT_N, LAT_S = 83.7, -62.0
W = 8192

def miller_y(latdeg):
    p = np.radians(latdeg)
    return 1.25 * np.log(np.tan(np.pi / 4 + 0.4 * p))

Y_N = float(miller_y(LAT_N)); Y_S = float(miller_y(LAT_S))
K = W / (2 * np.pi)                     # px per radian
H = int(round((Y_N - Y_S) * K))

def proj(lon, lat, w=W):
    k = w / (2 * np.pi)
    x = (np.radians(lon) + np.pi) * k
    y = (Y_N - miller_y(np.clip(lat, -89.5, 89.5))) * k
    return x, y

def inv_lat(ypx, w=W):
    k = w / (2 * np.pi)
    my = Y_N - ypx / k
    return np.degrees(2.5 * np.arctan(np.exp(0.8 * my)) - 0.625 * np.pi)

def rings_of(geom):
    t = geom['type']
    if t == 'Polygon': return [geom['coordinates']]
    if t == 'MultiPolygon': return geom['coordinates']
    return []

def lines_of(geom):
    t = geom['type']
    if t == 'LineString': return [geom['coordinates']]
    if t == 'MultiLineString': return geom['coordinates']
    return []

def load(name):
    return json.load(open(f'{DL}/{name}.geojson'))
