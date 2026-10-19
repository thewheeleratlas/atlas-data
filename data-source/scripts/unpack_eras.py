"""Write each era's ID raster back out as a plain PNG.
The deployed site stores the raster inside site/eras/<key>.json as base64 (key "_png") to save files.
Usage: python3 unpack_eras.py [site/eras] [out folder]   ->  <out>/<key>.png and <out>/<key>.json (without _png)"""
import base64, glob, json, os, sys
src = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), '..', '..', 'site', 'eras')
out = sys.argv[2] if len(sys.argv) > 2 else 'eras-unpacked'
os.makedirs(out, exist_ok=True)
n = 0
for p in sorted(glob.glob(os.path.join(src, '*.json'))):
    d = json.load(open(p, encoding='utf-8'))
    b = d.pop('_png', None)
    key = os.path.basename(p)[:-5]
    if b:
        open(os.path.join(out, key + '.png'), 'wb').write(base64.b64decode(b)); n += 1
    json.dump(d, open(os.path.join(out, key + '.json'), 'w', encoding='utf-8'), separators=(',', ':'), ensure_ascii=False)
print(f'{n} rasters written to {out}')
