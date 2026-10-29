"""Realm QC pass 14 (29 Oct 2026): names and dates from the "left for later" part of the 28 October review list.
Usage: python3 fix_qc14.py <site folder> [year,year,...]

FIX-244 1210: the Ghurid Sultanate still covered northern India. After Muhammad of Ghor's death (1206) Qutb ud-Din
        Aibak ruled it from Lahore and Delhi; east of 72.5 E it becomes the Sultanate of Delhi.
FIX-245 700: the "Uyghurs" piece lay along the southern Tarim Basin, where the oasis kingdoms (Khotan and its
        neighbours) were under the Tang protectorate of Anxi; the Uyghur Khaganate was founded in 744, in Mongolia.
FIX-246 1530-1650: the south of Champa (Panduranga, south of Cape Varella, 12.9 N) was drawn as Dai Viet; it stayed
        a Cham kingdom until it became a Nguyen vassal in the 1690s.
FIX-247 1650-1750: the restored Toungoo kingdom of Burma, ruled from Ava from 1635, was labelled "Ava".
FIX-248 1650-1750: the Nogai Horde broke up in the 1630s; its piece east of the Ural river joins the Kazakh Khanate
        (the Junior Juz).
FIX-249 1750: Afsharid rule was confined to Khorasan; west of 56 E Iran was contested by Karim Khan Zand, the
        Qajars and Azad Khan. Filed under Persia, the realm of the 1783 map.
FIX-250 1848: the Lozi floodplain was ruled by the Kololo from about 1840 to 1864.
FIX-251 1848-1880: the Oyo Empire collapsed in the 1830s; the successor kingdom was ruled from New Oyo.
FIX-252 Madagascar 1800-1900: the Merina kingdom keeps its name through 1880 (it was "Imerina" from 1871), the rest
        of the island is the other Malagasy kingdoms, not "Madagascar"; specks left on the 1900 French map join it.
FIX-253 Hadramaut: the ancient kingdom was annexed by Himyar about 300; from 1000 the name covered later polities.
        300-400: joins Himyar. 1000-1300: Hadramaut towns and tribes. 1400-1900: the Kathiri Sultanate (founded
        1395; with the Qu'aiti from the 1860s). 1783-1900: the Mahra Sultanate, which lasted to 1967, is drawn again.
FIX-254 Arabia 1871-1914: one name stood for changing rulers. 1871-1880: the Saudi and Rashidi emirates; 1900: the
        Rashidi Emirate of Jabal Shammar, which held Najd from 1891 to 1902; 1914: Ibn Saud's Emirate of Nejd and
        Hasa, with Hail still Rashidi. On 1871-1900 inner Oman and the south-eastern desert, drawn inside "Arabia",
        go back to Muscat and Oman and the Bedouin tribes, as on the 1848 map.
FIX-255 Specks: a duplicate "Kazakh Khanate (three juzes)" (1815, 1848) and a "Kazakh, Turkmen and Mongol nomads"
        speck (1400-1880) join their neighbours.

Borders, areas and labels are re-traced with ../derive-2026/era_tools.py.
Afterwards: python3 scripts/build_realm_index.py, overlays/ovsecond_build.py and scripts/build_content_pages.py."""
import collections, json, os, sys
import numpy as np
from scipy import ndimage
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'derive-2026'))
import era_tools as T

SITE = sys.argv[1]
J = lambda p: json.load(open(p, encoding='utf-8'))
ORDER = ['n', 'r', 'k', 'p', 'a', 'b', 'l', 'w', 'a3', 'x', 'c']
EMETA = J(f'{SITE}/data/eras.json')
F = {e['y']: e['f'] for e in EMETA['eras']}
G = EMETA['realms']
SEEN = {}
for f in F.values():
    for r in J(f'{SITE}/eras/{f}.json')['realms']:
        SEEN.setdefault(r['n'], r['g'])
LAT = T.LATR[:, None] * np.ones((1, T.EW))
LON = ((np.arange(T.EW) + 0.5) / T.EW * 360 - 180)[None, :] * np.ones((T.EH, 1))
ALL = np.ones((T.EH, T.EW), bool)


COLOUR = {'Toungoo Burma': '#b5838d', 'Kololo Kingdom': '#9c7b50', 'Malagasy kingdoms': '#8f9a6a', 'Kathiri Sultanate': '#b9925e', 'Hadramaut towns and tribes': '#b9925e', 'Central Arabian emirates (Saudi and Rashidi)': '#a8875a', 'Emirate of Jabal Shammar (Rashidi)': '#9f7f55'}


def gid(name, like=None):
    for i, g in enumerate(G):
        if g['n'] == name: return i
    if name in SEEN: return SEEN[name]
    c = COLOUR.get(name) or (G[like]['c'] if like is not None else '#948a70')
    G.append({'k': name.lower(), 'c': c, 't': 1, 'n': name}); SEEN[name] = len(G) - 1; return SEEN[name]


# FIX-244: the Ghurid Sultanate had the Sultanate of Delhi's colour; on the 1210 map they are neighbours
for _g in G:
    if _g['n'] == 'Ghurid Sultanate': _g['c'] = '#a39a45'


def realm_of(js, name, like=None):
    for i, r in enumerate(js['realms']):
        if r['n'] == name: return i
    js['realms'].append({'g': gid(name, like), 'n': name}); return len(js['realms']) - 1


OPS = []
def R(fix, old, new, y0, y1, realm=None, k=None):
    OPS.append((fix, 'rename', y0, y1, old, dict(new=new, realm=realm, k=k)))
def S(fix, old, new, y0, y1, mask, realm=None, k=None):
    OPS.append((fix, 'split', y0, y1, old, dict(new=new, mask=mask, realm=realm, k=k)))
def A(fix, old, y0, y1, mask=None):
    OPS.append((fix, 'absorb', y0, y1, old, dict(mask=mask)))

def box(la0, la1, lo0, lo1):
    return (LAT >= la0) & (LAT <= la1) & (LON >= lo0) & (LON <= lo1)

def F_(fix, new, y0, y1, mask):
    """fill: unclaimed land pixels (id 0) inside mask go to the existing realm-piece named new"""
    OPS.append((fix, 'fill', y0, y1, new, dict(new=new, mask=mask)))


def mask_of(year, name):
    js = J(f'{SITE}/eras/{F[year]}.json'); ids = T.read_ids(js)
    return np.isin(ids, [i for i, e in enumerate(js['ents'], 1) if e['n'] == name])
HADR = mask_of(1750, 'Hadramaut') | mask_of(1750, 'Kathiri Sultanate'); MAHRA = mask_of(1750, 'Mahra')
OMAN = mask_of(1848, 'Muscat and Oman')
BED = mask_of(1848, 'Bedouin tribes') | mask_of(1848, 'Kathiri Sultanate') | mask_of(1848, 'Mahra')   # the tribal land of the 1848 map

# FIX-244
S('FIX-244', 'Ghurid Sultanate', 'Sultanate of Delhi', 1210, 1210, LON >= 72.5)
# FIX-245
R('FIX-245', 'Uyghurs', 'Tarim Basin oasis kingdoms (Tang protectorate)', 700, 700, realm='Tang Empire')
# FIX-246
S('FIX-246', 'Đại Việt', 'Champa', 1530, 1650, box(10.9, 12.9, 107.6, 109.8))
# FIX-247
R('FIX-247', 'Ava', 'Toungoo Burma (ruled from Ava)', 1650, 1750, realm='Toungoo Burma')
# FIX-248
S('FIX-248', 'Nogai Horde', 'Kazakh Khanate', 1650, 1750, ALL)
# FIX-249
S('FIX-249', 'Afsharid Iran', 'Western Iran (Zand, Qajar and rival khans)', 1750, 1750, LON < 56.0, realm='Persia')
# FIX-250
R('FIX-250', 'Lozi', 'Kololo Kingdom', 1848, 1848, realm='Kololo Kingdom')
# FIX-251
R('FIX-251', 'Oyo', 'Oyo (New Oyo)', 1848, 1880, realm='Oyo')
# FIX-252
R('FIX-252', 'Imerina', 'Merina Kingdom', 1871, 1880, realm='Merina Kingdom')
R('FIX-252', 'Madagascar', 'Malagasy kingdoms (Sakalava and others)', 1800, 1880, realm='Malagasy kingdoms')
A('FIX-252', 'Imerina', 1900, 1900)
A('FIX-252', 'Madagascar', 1900, 1900)
# FIX-253
A('FIX-253', 'Hadramaut', 300, 400)
R('FIX-253', 'Hadramaut', 'Hadramaut towns and tribes', 1000, 1300, realm='Hadramaut towns and tribes')
R('FIX-253', 'Hadramaut', 'Kathiri Sultanate', 1400, 1750, realm='Kathiri Sultanate')
S('FIX-253', 'Bedouin tribes', 'Kathiri Sultanate', 1783, 1848, HADR, realm='Kathiri Sultanate', k=0)
S('FIX-253', 'Bedouin tribes', 'Mahra', 1783, 1815, MAHRA, realm='Mahra', k=0)
S('FIX-253', 'Bedouin tribes', 'Mahra', 1848, 1848, MAHRA & (LON < 53.0), realm='Mahra', k=0)
S('FIX-253', 'Arabia', "Kathiri and Qu'aiti sultanates", 1871, 1900, HADR, realm='Kathiri Sultanate', k=0)
S('FIX-253', 'Arabia', 'Mahra', 1871, 1900, MAHRA & (LON < 53.0), realm='Mahra', k=0)
# FIX-254
R('FIX-254', 'Arabia', 'Central Arabian emirates (Saudi and Rashidi)', 1871, 1880, realm='Central Arabian emirates (Saudi and Rashidi)')
R('FIX-254', 'Arabia', 'Emirate of Jabal Shammar (Rashidi)', 1900, 1900, realm='Emirate of Jabal Shammar (Rashidi)')
S('FIX-254', 'Arabia (Nejd)', 'Hail', 1914, 1914, (LAT > 26.0) & (LON < 44.5), realm='Hail')
R('FIX-254', 'Arabia (Nejd)', 'Emirate of Nejd and Hasa', 1914, 1914, realm='Emirate of Nejd and Hasa')
S('FIX-254', 'Central Arabian emirates (Saudi and Rashidi)', 'Bedouin tribes', 1871, 1880, BED, realm='Bedouin tribes', k=1)
S('FIX-254', 'Emirate of Jabal Shammar (Rashidi)', 'Bedouin tribes', 1900, 1900, BED, realm='Bedouin tribes', k=1)
S('FIX-254', 'Central Arabian emirates (Saudi and Rashidi)', 'Muscat and Oman', 1871, 1880, OMAN)
S('FIX-254', 'Emirate of Jabal Shammar (Rashidi)', 'Muscat and Oman', 1900, 1900, OMAN)
# FIX-255
A('FIX-255', 'Kazakh Khanate (three juzes)', 1815, 1848)
A('FIX-255', 'Kazakh, Turkmen and Mongol nomads', 1400, 1880)

NOTE = {
    'FIX-244': 'After Muhammad of Ghor died in 1206, Qutb ud-Din Aibak ruled his Indian lands from Lahore and Delhi: the Sultanate of Delhi (line approximate).',
    'FIX-245': 'The oasis kingdoms of the southern Tarim Basin were under the Tang protectorate of Anxi; the Uyghur Khaganate was founded in 744.',
    'FIX-246': 'Southern Champa (Panduranga) remained a Cham kingdom until it became a vassal of the Nguyen lords in the 1690s (line approximate).',
    'FIX-247': 'The restored Toungoo kingdom ruled Burma from Ava from 1635 to 1752.',
    'FIX-248': 'The Nogai Horde broke up in the 1630s; the steppe east of the Ural river was held by the Kazakh Junior Juz.',
    'FIX-249': 'By 1750 Afsharid rule was confined to Khorasan; western Iran was contested by Karim Khan Zand, the Qajars and Azad Khan (line approximate).',
    'FIX-250': 'The Kololo, from southern Africa, ruled the Lozi floodplain from about 1840 until the Lozi restored their kingdom in 1864.',
    'FIX-251': 'The Oyo Empire collapsed in the 1830s; a smaller successor kingdom was ruled from New Oyo.',
    'FIX-252': 'The Merina kingdom ruled central Madagascar until the French conquest of 1895-1897; the rest of the island was held by the Sakalava and other kingdoms.',
    'FIX-253': 'The ancient kingdom of Hadramaut was annexed by Himyar about 300. The Kathiri Sultanate ruled the Hadramaut from 1395, and the Mahra Sultanate the coast to its east until 1967.',
    'FIX-254': 'Central Arabia: the second Saudi state and the Rashidi emirate of Hail; the Rashidis held Najd from 1891 to 1902, when Ibn Saud took Riyadh.',
    'FIX-255': 'Small mapping specks were joined to their neighbours.',
}
NEED_IDS = {'split', 'absorb', 'clear', 'paint', 'fill'}


def ents_named(js, name):
    return [i + 1 for i, e in enumerate(js['ents']) if e.get('a') and e['n'] == name]


def fix_era(y, LAND):
    key = F[y]; p = f'{SITE}/eras/{key}.json'; js = J(p)
    log = collections.Counter(); notes = []
    todo = [op for op in OPS if op[2] <= y <= op[3] and (op[1] == 'paint' or ents_named(js, op[4]))]
    if not todo:
        return None
    ids = orig = None
    ov = J(f'{SITE}/data/ovmain.json'); rows = ov['eras'][key]
    if any(op[1] in NEED_IDS for op in todo):
        same, bad = T.check_roundtrip(js, LAND)
        assert same and all(x[1] == x[2] and x[3] == x[4] for x in bad), f'tracing does not reproduce the {key} map; stop'
        ids = T.read_ids(js); orig = ids.copy()
    for fix, kind, y0, y1, old, o in OPS:
        if not (y0 <= y <= y1): continue
        if kind == 'paint':
            hit = [i for i, e in enumerate(js['ents'], 1) if e.get('a') and e['k'] == 1 and e['n'] != o['new']]
        else:
            hit = ents_named(js, old)
        if not hit: continue
        if kind == 'rename':
            for i in hit:
                e = js['ents'][i - 1]; rn = js['realms'][e['r']]['n'] if e['r'] >= 0 else None
                like = js['realms'][e['r']]['g'] if e['r'] >= 0 else None
                target = o['realm'] or (o['new'] if rn == old or rn is None else None)
                if target: e['r'] = realm_of(js, target, like)
                for e2 in js['ents']:                      # the rest of a realm of that name follows it
                    if e2 is not e and e2['r'] >= 0 and rn == old and js['realms'][e2['r']]['n'] == old and target:
                        e2['r'] = e['r']
                e['n'] = o['new']; e['x'] = 1
                if o['k'] is not None: e['k'] = o['k']
                log[fix] += 1
        elif kind in ('split', 'paint'):
            o = dict(o, realm=o.get('realm'), k=o.get('k'))
            m = np.isin(ids, hit) & o['mask']
            if not m.any(): continue
            src = js['ents'][hit[0] - 1]
            like = js['realms'][src['r']]['g'] if src['r'] >= 0 else None
            ex = [i for i in ents_named(js, o['new']) if i not in hit] or [i for i, e in enumerate(js['ents'], 1) if e['n'] == o['new'] and i not in hit]
            if ex:
                ni = ex[0]
            else:
                js['ents'].append({'n': o['new'], 'r': realm_of(js, o['realm'] or o['new'], like), 'k': src['k'] if o['k'] is None else o['k'],
                                   'p': 1, 'a': 1, 'x': 1})
                ni = len(js['ents'])
                while len(rows) < ni: rows.append(list(rows[int(np.bincount(orig[m]).argmax()) - 1]))
            ids[m] = ni; log[fix + ' px'] += int(m.sum())
        elif kind == 'fill':
            m = (ids == 0) & LAND & o['mask']
            if not m.any(): continue
            ids[m] = hit[0]; log[fix + ' filled px'] += int(m.sum())
            notes.append(NOTE[fix]); continue
        elif kind == 'clear':
            m = np.isin(ids, hit) & (ALL if o['mask'] is None else o['mask'])
            ids[m] = 0; log[fix + ' cleared px'] += int(m.sum())
        elif kind == 'absorb':
            m = np.isin(ids, hit) & (ALL if o['mask'] is None else o['mask'])
            lab, n = ndimage.label(m)
            for c in range(1, n + 1):
                cm = lab == c
                ring = ndimage.binary_dilation(cm) & ~cm & (ids > 0) & ~np.isin(ids, hit)
                if ring.any():
                    ids[cm] = np.bincount(ids[ring]).argmax()
                else:
                    near = ndimage.binary_dilation(cm, iterations=12) & ~cm & (ids > 0) & ~np.isin(ids, hit)
                    if near.any(): ids[cm] = np.bincount(ids[near]).argmax()
                log[fix + ' joined'] += 1
        notes.append(NOTE[fix])
        if ids is not None:                                 # names later ops look up must reflect pixels now
            for i in hit:
                if not (ids == i).any(): js['ents'][i - 1]['a'] = 0
    if ids is not None:
        changed = ids != orig
        touched = set(np.unique(orig[changed]).tolist()) | set(np.unique(ids[changed]).tolist()); touched.discard(0)
        for i in touched:
            e = js['ents'][i - 1]; a, b, l = T.stats(ids, i)
            e['a'] = a
            for k, v in (('b', b), ('l', l)):
                if v is None: e.pop(k, None)
                else: e[k] = v
        js['borders'] = T.borders(ids, LAND)
        js['_png'] = T.write_ids(ids)
        assert (T.read_ids(js) == ids).all()
    open(f'{SITE}/data/ovmain.json', 'w', encoding='utf-8').write(json.dumps(ov, ensure_ascii=True, separators=(',', ':')))
    used = sorted({e['r'] for e in js['ents'] if e['r'] >= 0})
    remap = {r: k for k, r in enumerate(used)}
    js['realms'] = [js['realms'][r] for r in used]
    for e in js['ents']:
        if e['r'] >= 0: e['r'] = remap[e['r']]
    js['ents'] = [{k: e[k] for k in ORDER if k in e} for e in js['ents']]
    js['notes'] += [n for n in dict.fromkeys(notes) if n not in js['notes']]
    open(p, 'w', encoding='utf-8').write(json.dumps(js, ensure_ascii=False, separators=(',', ':')))
    return dict(log)


LAND = T.land_mask(f'{SITE}/eras', list(F.values()))
for y in sorted(y for y in F if len(sys.argv) < 3 or str(y) in sys.argv[2].split(',')):
    r = fix_era(y, LAND)
    if r: print(y, r, flush=True)
for ix in EMETA['eras']:
    js = J(f"{SITE}/eras/{ix['f']}.json")
    ix['c'] = len(js['notes'])
    ix['n'] = sum(1 for e in js['ents'] if e.get('a') and e['k'] == 0)
    ix['m'] = sum(1 for e in js['ents'] if e.get('a') and e['k'] == 1)
open(f'{SITE}/data/eras.json', 'w', encoding='utf-8').write(json.dumps(EMETA, ensure_ascii=True, separators=(',', ':')))
