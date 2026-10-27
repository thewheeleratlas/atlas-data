"""Faith, culture and development layers and card rows for the 1975 and 1989 maps (made by make_1989.py and
make_1975.py). Usage: python3 cold_war_layers.py <site folder> <work folder>

The work folder needs the Natural Earth layers in <work>/dl (../fetch_natural_earth.py, plus
ne_10m_populated_places_simple) and the masks from ../s1_masks.py in <work>/work (HHA_WORKDIR=<work>).

1. The overlay rules (../overlays/s8_religion.py, s10_develop.py) paint 1960, 1975, 1989 and 1994 in a scratch copy.
   Repainting 1960 and 1994 reproduces the deployed layers except where they were corrected by hand in 2026
   (fixes-2026/fix_overlay_*.py: about 250 faith and 470 culture pixels). Those corrections are carried into 1975 and
   1989 where the new year was painted the same as the corrected year: the 1994 correction first, then the 1960 one.
   The development layer is reproduced exactly and is used as painted.
2. Areas per faith and culture (data/religions.json, data/cultures.json), the largest cities (data/develop.json) and
   the per-territory main faith, main culture and development rows (data/ovmain.json, ../overlays/ovmain_build.py)
   are written for the two new years. ovmain_build.py needs the atlas's modern country grid; it is rebuilt from the
   s1_masks.py country raster, whose ids match data/world.json, and the terrain from tiles/terrain/L1.webp."""
import json, os, re, shutil, subprocess, sys, base64
import numpy as np, cv2
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); OV = os.path.join(os.path.dirname(HERE), 'overlays')
sys.path.insert(0, HERE)
import era_tools as T

SITE, WORK = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2])
NEW, NBR = ['1975', '1989'], ['1960', '1994']
TMP = os.path.join(WORK, 'cold_war'); shutil.rmtree(TMP, ignore_errors=True)
os.makedirs(f'{TMP}/eras'); os.makedirs(f'{TMP}/data')
J = lambda p: json.load(open(p, encoding='utf-8'))
meta = J(f'{SITE}/data/eras.json')
m2 = dict(meta); m2['eras'] = [e for e in meta['eras'] if e['f'] in NEW + NBR]
json.dump(m2, open(f'{TMP}/data/eras.json', 'w'))
for k in NEW + NBR:
    js = J(f'{SITE}/eras/{k}.json'); open(f'{TMP}/eras/{k}.png', 'wb').write(base64.b64decode(js.pop('_png')))
    json.dump(js, open(f'{TMP}/eras/{k}.json', 'w'), ensure_ascii=False)
env = dict(os.environ, HHA_WORKDIR=WORK, HHA_SITE=TMP)
for args in (['s8_religion.py', 'religion'], ['s8_religion.py', 'culture'], ['s10_develop.py']):
    subprocess.run([sys.executable, *args], cwd=OV, env=env, check=True, stdout=subprocess.DEVNULL)

ALIAS = json.loads(re.search(r'const ASSET_ALIAS = (\{.*?\});', open(f'{SITE}/atlas.js', encoding='utf-8').read()).group(1))
deployed = lambda d, k: f"{SITE}/{ALIAS.get(f'{d}/{k}.png', f'{d}/{k}.png')}"
def rd(path, wide):
    a = np.asarray(Image.open(path).convert('RGB')).astype(np.int32)
    return a[..., 0] + (a[..., 1] << 8) if wide else a[..., 0]
PIXKM = np.repeat(T.PIXKM, T.EW)
for d, name in (('rel', 'religions'), ('cul', 'cultures')):
    info = J(f'{SITE}/data/{name}.json'); wide = info['wide']
    D = {k: rd(deployed(d, k), wide) for k in NBR}; R = {k: rd(f'{TMP}/{d}/{k}.png', wide) for k in NEW + NBR}
    for k in NBR: print(f'{d} {k}: repainted, {int((D[k] != R[k]).sum())} pixels differ from the deployed layer (hand corrections)')
    for y in NEW:
        F = R[y]
        F = np.where((F == R['1994']) & (D['1994'] != R['1994']), D['1994'], np.where((F == R['1960']) & (D['1960'] != R['1960']), D['1960'], F))
        print(f'{d} {y}: {int((F != R[y]).sum())} corrected pixels carried over')
        if wide: out = np.zeros(F.shape + (3,), np.uint8); out[..., 2] = F & 255; out[..., 1] = F >> 8
        else: out = F.astype(np.uint8)
        cv2.imwrite(f'{SITE}/{d}/{y}.png', out, [cv2.IMWRITE_PNG_COMPRESSION, 9])
        shutil.copy(f'{SITE}/{d}/{y}.png', f'{TMP}/{d}/{y}.png')
        area = np.bincount(F.ravel(), weights=PIXKM, minlength=len(info['items']) + 1)
        info['eras'][y] = [[int(i), int(round(area[i]))] for i in np.argsort(-area) if i > 0 and area[i] > 500]
    for k in NBR: shutil.copy(deployed(d, k), f'{TMP}/{d}/{k}.png')
    shutil.copy(f'{SITE}/data/{name}.json', f'{TMP}/data/{name}.json')   # item names as deployed
    open(f'{SITE}/data/{name}.json', 'w', encoding='utf-8').write(json.dumps(info, ensure_ascii=True, separators=(',', ':')))
dev = J(f'{SITE}/data/develop.json'); dnew = J(f'{TMP}/data/develop.json')
for k in NBR:
    assert (rd(deployed('dev', k), False) == rd(f'{TMP}/dev/{k}.png', False)).all(), f'dev {k} not reproduced'
for y in NEW:
    shutil.copy(f'{TMP}/dev/{y}.png', f'{SITE}/dev/{y}.png'); dev['eras'][y] = dnew['eras'][y]
open(f'{SITE}/data/develop.json', 'w', encoding='utf-8').write(json.dumps(dev, ensure_ascii=True, separators=(',', ':')))

# card rows
OM = f'{TMP}/ovmain'; os.makedirs(f'{OM}/devidx'); os.makedirs(f'{OM}/atlas/data'); os.makedirs(f'{OM}/atlas/tiles/ids')
for f in ('ovmain_build.py', 'popw.py', 'devindex.py', 'maddison2020.csv'): shutil.copy(f'{OV}/{f}', OM)
for f in ('devindex.py', 'maddison2020.csv'): shutil.copy(f'{OV}/{f}', f'{OM}/devidx')
np.save(f'{OM}/terrain4096.npy', np.asarray(Image.open(f'{SITE}/tiles/terrain/L1.webp').convert('RGB')))
shutil.copy(f'{SITE}/data/world.json', f'{OM}/atlas/data/world.json')
cid = np.load(f'{WORK}/work/ids.npy')[::4, ::4]; ne = J(f'{WORK}/work/meta.json')
assert all(ne[c['id'] - 1]['ADM0_A3'] == c['a3'] for c in J(f'{SITE}/data/world.json')['countries']), 'country ids do not match world.json'
rgb = np.zeros(cid.shape + (3,), np.uint8); rgb[..., 0] = cid & 255; rgb[..., 1] = cid >> 8
Image.fromarray(rgb).save(f'{OM}/atlas/tiles/ids/0_0_0.png')
subprocess.run([sys.executable, 'ovmain_build.py', TMP + '/'], cwd=OM, env=dict(os.environ, HHA_ATLAS=f'{OM}/atlas/'), check=True, stdout=subprocess.DEVNULL)
rows = J(f'{TMP}/data/ovmain.json')['eras']; om = J(f'{SITE}/data/ovmain.json')
for k in NBR:
    same = sum(a == b for a, b in zip(om['eras'][k], rows[k]))
    print(f'ovmain {k}: {same} of {len(rows[k])} rows reproduced (others: GDP rounding, 2026 hand corrections)')
for y in NEW:
    assert len(rows[y]) == len(J(f'{SITE}/eras/{y}.json')['ents']); om['eras'][y] = rows[y]
open(f'{SITE}/data/ovmain.json', 'w', encoding='utf-8').write(json.dumps(om, ensure_ascii=True, separators=(',', ':')))
print('done')
