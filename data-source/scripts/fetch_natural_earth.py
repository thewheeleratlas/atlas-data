"""Download the public-domain Natural Earth layers the build needs into workdir/dl/.

Natural Earth is public domain (https://www.naturalearthdata.com/).
GeoJSON copies are taken from the nvkelso/natural-earth-vector repository.
"""
import os, urllib.request

LAYERS = ['ne_10m_land', 'ne_10m_lakes', 'ne_10m_glaciated_areas', 'ne_10m_rivers_lake_centerlines',
          'ne_10m_admin_0_countries', 'ne_10m_admin_1_states_provinces']
BASE = 'https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/'
root = os.environ.get('HHA_WORKDIR', os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'workdir')))
dl = os.path.join(root, 'dl'); os.makedirs(dl, exist_ok=True)
for n in LAYERS:
    p = os.path.join(dl, n + '.geojson')
    if os.path.exists(p): print('have', n); continue
    print('downloading', n); urllib.request.urlretrieve(BASE + n + '.geojson', p)
print('done ->', dl)
