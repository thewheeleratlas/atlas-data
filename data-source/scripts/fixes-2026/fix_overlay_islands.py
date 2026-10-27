"""Culture and religion layers: small island states (27 Oct 2026). Usage: python3 fix_overlay_islands.py <site folder>

FIX-160 The 1975 and 1989 maps (made after fix_overlay_overseas.py) had the world default's coastal fringe, hunter-gatherers
        and animism, on small island territories, as the other modern maps had before FIX-143. The same rule is applied
        to them: island territories (under 3,000 pixels, no land border) whose fringe is under half the island take the
        island's main other culture or faith there.
FIX-161 The Maldives, one map pixel, fell outside the outline the culture and religion rules paint, so they showed the world
        default (hunter-gatherers, animism) on the 1975, 1989 and 2026 maps. They are Maldivian (Dhivehi), a new culture,
        and Sunni Muslim (since the 12th century).
FIX-162 Cape Verde, Sao Tome and Principe and the Seychelles were n/a for culture because the atlas had no Creole category
        for them. They are Cape Verdean and Sao Tomean Creole and Seychellois Creole (new cultures), and Catholic where the
        coastal fringe still showed animism.
FIX-163 Micronesia (Kiribati, Guam, Palau and the Federated States of Micronesia) was n/a for culture for want of a
        Micronesian category; it is Micronesian (new culture). The Northern Mariana Islands, Chamorro, Carolinian and
        Filipino with no majority, stay n/a. Kiribati's faith stays n/a on the 1938 map (Catholic and Protestant roughly
        equal), and is Catholic where the fringe showed animism on the later maps.

The four new cultures are added after 'n/a' in data/cultures.json (and in ../overlays/culture_rules.py, whose rules now
paint them), so every existing index is unchanged. Areas in data/cultures.json and data/religions.json are adjusted by
the pixels changed, and the main culture or faith of each repainted territory (data/ovmain.json) is recomputed by area."""
import json, os, sys
import numpy as np
from PIL import Image
from scipy import ndimage
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'derive-2026')); sys.path.insert(0, os.path.join(HERE, '..', 'overlays'))
import era_tools as T
import culture_rules

SITE = sys.argv[1]
J = lambda p: json.load(open(p, encoding='utf-8'))
meta = J(f'{SITE}/data/eras.json')['eras']
CUL, REL = J(f'{SITE}/data/cultures.json'), J(f'{SITE}/data/religions.json')
assert CUL['items'][-1]['id'] == 'na' or CUL['items'][-1]['id'] == 'micronesian'
have = {it['id'] for it in CUL['items']}
for f in culture_rules.FAITHS[[x['id'] for x in culture_rules.FAITHS].index('na') + 1:]:
    if f['id'] not in have: CUL['items'].append({k: f[k] for k in ('id', 'n', 'fam', 'c', 'd', 'w') if k in f})
CUL['faiths'] = CUL['items']
CID = {it['id']: i + 1 for i, it in enumerate(CUL['items'])}
RID = {it['id']: i + 1 for i, it in enumerate(REL['items'])}
assert [x['id'] for x in CUL['items']] == [x['id'] for x in culture_rules.FAITHS], 'cultures.json and culture_rules.py differ'
KM = T.PIXKM
KEEP_DEFAULT = {'Taiwan', 'Formosa', 'Republic of China (Taiwan)', 'Kuril Islands', 'French Southern and Antarctic Lands',
                'Heard Island and McDonald Islands', 'South Georgia and the South Sandwich Islands'}
FRINGE = {'cul': ['foragers'], 'rel': ['animism']}
# territory names -> (fix, culture: replace these with that, faith: replace these with that)
TARGETS = [
    (('Maldives',), 'FIX-161', (None, 'maldivian'), (None, 'sunni')),
    (('Cape Verde', 'Cabo Verde', 'São Tomé and Príncipe', 'São Tomé and Principe'), 'FIX-162', (['na', 'foragers'], 'luso_creole'), (['animism'], 'catholic')),
    (('Seychelles',), 'FIX-162', (['na', 'foragers'], 'seychellois'), (['animism'], 'catholic')),
    (('Gilbert and Ellice Islands',), 'FIX-163', (['na', 'foragers'], 'micronesian'), (['animism'], 'na')),
    (('Gilbert Islands', 'Kiribati', 'Guam', 'Palau', 'Micronesia'), 'FIX-163', (['na', 'foragers'], 'micronesian'), (['animism'], 'catholic')),
]


def read(layer, key):
    p = f'{SITE}/{layer}/{key}.png'
    if not os.path.exists(p): return None
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
        for v in vals: pal += [int(v) & 255, int(v) >> 8, 0]
        im.putpalette(pal + [0] * (768 - len(pal)))
        im.save(p, optimize=True)
    try:
        import oxipng
        oxipng.optimize(p, level=4)
    except ImportError:
        pass


def fringe(L, ids, js, dflt):
    """FIX-143's rule: the default's coastal fringe on small island territories takes the island's main other value."""
    cnt = np.bincount(ids.ravel(), minlength=len(js['ents']) + 1)
    coast = ndimage.binary_dilation(ids == 0, structure=np.ones((3, 3)))
    objs = ndimage.find_objects(ids); out = []
    for ent in np.unique(ids[(L == dflt) & coast]):
        if ent == 0 or js['ents'][ent - 1].get('k') or cnt[ent] >= 3000 or js['ents'][ent - 1]['n'] in KEEP_DEFAULT: continue
        o = objs[ent - 1]
        bx = (slice(max(0, o[0].start - 1), o[0].stop + 1), slice(max(0, o[1].start - 1), o[1].stop + 1))
        sub_ids, sub_L = ids[bx], L[bx]
        m = sub_ids == ent
        ring = ndimage.binary_dilation(m, structure=np.ones((3, 3))) & ~m
        if (sub_ids[ring] != 0).any(): continue
        v, c = np.unique(sub_L[m], return_counts=True)
        keep = (v != dflt) & (v > 0)
        if not keep.any() or c[v == dflt].sum() * 2 >= m.sum(): continue
        sel = m & (sub_L == dflt) & coast[bx]
        sub_L[sel] = int(v[keep][np.argmax(c[keep])]); out.append((js['ents'][ent - 1]['n'], int(sel.sum())))
    return out


def main():
    log, ovm = [], J(f'{SITE}/data/ovmain.json')
    for e in meta:
        y, key = e['y'], e['f']
        js = J(f'{SITE}/eras/{key}.json')
        tg = [(i + 1, t) for i, x in enumerate(js['ents']) if x.get('a') for t in TARGETS if x['n'] in t[0]]
        if not tg and y not in (1975, 1989): continue
        ids = T.read_ids(js)
        for layer, ID, DATA, col in (('cul', CID, CUL, 1), ('rel', RID, REL, 0)):
            L = read(layer, key)
            if L is None: continue
            old = L.copy()
            if y in (1975, 1989):
                for name, n in fringe(L, ids, js, ID[FRINGE[layer][0]]): log.append(('FIX-160', name, y, layer, n))
            for ent, (names, fix, cul, rel) in tg:
                labels, new = cul if layer == 'cul' else rel
                m = ids == ent
                bad = m & (L > 0) if labels is None else m & np.isin(L, [ID[x] for x in labels])
                if bad.any(): L[bad] = ID[new]; log.append((fix, js['ents'][ent - 1]['n'], y, layer, int(bad.sum())))
            ch = L != old
            if not ch.any(): continue
            areas = {i: a for i, a in DATA['eras'][key]}
            for o, n, r in zip(old[ch], L[ch], np.nonzero(ch)[0]):
                areas[int(o)] = areas.get(int(o), 0) - KM[r]; areas[int(n)] = areas.get(int(n), 0) + KM[r]
            DATA['eras'][key] = [[i, int(round(a))] for i, a in sorted(areas.items(), key=lambda t: -t[1]) if round(a) > 0]
            rows = ovm['eras'][key]
            for ent in np.unique(ids[ch]):
                if ent == 0: continue
                m = ids == ent
                if (ch & m).sum() * 2 < m.sum() and (m & (L == rows[ent - 1][col])).any(): continue   # a small part of a larger territory
                v, c = np.unique(L[m & (L > 0)], return_counts=True)
                if len(v): rows[ent - 1][col] = int(v[np.argmax(c)])
            write(layer, key, L)
    for path, D in ((f'{SITE}/data/cultures.json', CUL), (f'{SITE}/data/religions.json', REL)):
        json.dump(D, open(path, 'w', encoding='utf-8'), ensure_ascii=True, separators=(',', ':'))
    json.dump(ovm, open(f'{SITE}/data/ovmain.json', 'w', encoding='utf-8'), ensure_ascii=True, separators=(',', ':'))
    for row in log: print(*row)


if __name__ == '__main__':
    main()
