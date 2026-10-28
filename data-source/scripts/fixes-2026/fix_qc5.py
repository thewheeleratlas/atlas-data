"""Realm QC pass 5 (28 Oct 2026): North America after contact, the 1530-1800 maps (names). Usage: python3 fix_qc5.py <site folder> [one year]

FIX-200 Peoples shown where they arrived only later: the Plains Apache (not the Comanche, Kiowa or Arapaho) on the
        southern and central Plains before 1700-1715; the Kiowa and Plains Apache (not the Cheyenne) at the Black Hills;
        Plains bison hunters (not the Teton Lakota) west of the Missouri before 1750; the Coahuiltecan and Jumano
        peoples (not the Lipan) in Texas before 1700; the Comanche (not the Kiowa) on the southern Plains in 1750.
FIX-201 Peoples and cultures shown after they were gone: the Bahamas empty after the Lucayans were taken (1530-1600)
        and English from 1650; the Taíno of Hispaniola after 1530; the "Aztec Empire" (1530) and "Mogollon" (1530-1600)
        in north-east Mexico are the Pame and Huastec peoples; Adena and Hopewell are the Shawnee, Miami, Delaware and
        Wyandot; the Erie (destroyed 1654-56), Susquehannocks (1675-77) and Natchez (1729-31) end on time; the
        Caloosahatchee culture is the Calusa; the Thule are the Inuit.
FIX-202 Misplaced or modern names: the Narragansett and Wampanoag (was "Cusabo", in Rhode Island); the Ohio Valley
        peoples (was "Kaskaskia", in Ohio); Western Apache and Yavapai for the central-Arizona "Hopi" and Hopi for
        "Hopie"; Snohomish (was Tulalip, a reservation confederation); the Yellowknives (was Akaitcho); the Northern
        Tutchone (was Selkirk); Inuit, Labrador Inuit and Eastern James Bay Cree (were Nunavik, Nunatsiavut, Eeyou
        Istchee).
FIX-203 Misspelt names: Montaukett, Nanticoke, Klickitat, Tenino, Maidu, Kawaiisu, Salinan, Tlingit, Serrano,
        Cahuilla, Sugpiaq (Alutiiq), Piro, Tewa, Naniaba, Ojibwa, Yanktonai, Winnebago, Chitimacha.
FIX-204 Colonies: South Carolina only from 1670 (Cusabo in 1650; Carolina, England, 1700-1715); New York, not New
        Amsterdam, after 1664; Saint-Domingue French in 1700 (west of about 71.7 W) and a French colony, not a realm of
        its own; Puerto Rico (Spain), not the Danish Virgin Islands; the Leeward and French islands as colonies, not
        peoples; Nova Scotia (was "Acadian Peninsula"); Venezuela in New Granada (1750); Yucatán Maya (1530) and the Itza
        kingdom (1600) outside New Spain; Calusa and Tequesta south of 28.5 N, outside Spanish Florida (1650, 1700);
        the Kingdom of Hawaii and Russian Kodiak (1800); Inuit, not British North America, in the Arctic islands (1800).

Names, and a few splits along stated lines. Borders, areas and labels are re-traced with ../derive-2026/era_tools.py.
Afterwards: python3 scripts/build_realm_index.py and scripts/build_content_pages.py."""
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


def gid(name, like=None):
    for i, g in enumerate(G):
        if g['n'] == name: return i
    if name in SEEN: return SEEN[name]
    c = G[like]['c'] if like is not None else '#948a70'
    G.append({'k': name.lower(), 'c': c, 't': 1, 'n': name}); SEEN[name] = len(G) - 1; return SEEN[name]


def realm_of(js, name, like=None):
    for i, r in enumerate(js['realms']):
        if r['n'] == name: return i
    js['realms'].append({'g': gid(name, like), 'n': name}); return len(js['realms']) - 1


# ---- operations. Each: (fix, kind, years, name, ...). Years are inclusive [y0, y1]. A realm may list several
# names separated by "|": the first that exists on the map is used.
OPS = []
def R(fix, old, new, y0, y1, realm=None, k=None):
    OPS.append((fix, 'rename', y0, y1, old, dict(new=new, realm=realm, k=k)))
def S(fix, old, new, y0, y1, mask, realm=None, k=None):
    OPS.append((fix, 'split', y0, y1, old, dict(new=new, mask=mask, realm=realm, k=k)))
def A(fix, old, y0, y1, mask=None):
    OPS.append((fix, 'absorb', y0, y1, old, dict(mask=mask)))
def C(fix, old, y0, y1, mask=None):
    OPS.append((fix, 'clear', y0, y1, old, dict(mask=mask)))

ENG = 'Kingdom of Great Britain|Kingdom of England|Commonwealth of England'
FRA = 'France'
SPA = 'Spain|Spain (Habsburg)'
# FIX-200
for old in ('Comanche', 'Arapaho'):
    R('FIX-200', old, 'Plains Apache', 1530, 1700 if old == 'Comanche' else 1650)
R('FIX-200', 'Kiowa', 'Plains Apache', 1530, 1715)
R('FIX-200', 'Kiowa', 'Comanche', 1750, 1750)
R('FIX-200', 'Cheyenne', 'Plains Apache', 1530, 1650)
R('FIX-200', 'Cheyenne', 'Kiowa and Plains Apache', 1700, 1750)
R('FIX-200', 'Teton', 'Plains bison hunters', 1530, 1715)
R('FIX-200', 'Lipan', 'Coahuiltecan and Jumano peoples', 1530, 1650)
# FIX-201
C('FIX-201', 'Taíno and Kalinago peoples', 1530, 1600)
R('FIX-201', 'Taíno and Kalinago peoples', 'Bahamas', 1650, 1800, realm=ENG, k=0)
A('FIX-201', 'Taino', 1600, 1800)
R('FIX-201', 'Aztec Empire', 'Pame', 1530, 1530, k=1)
R('FIX-201', 'Mogollon', 'Pame and Huastec peoples', 1530, 1600)
R('FIX-201', 'Adena', 'Miami and Shawnee', 1530, 1750)
R('FIX-201', 'Hopewell', 'Shawnee and Erie peoples', 1530, 1650)
R('FIX-201', 'Hopewell', 'Shawnee, Delaware and Wyandot', 1700, 1750)
R('FIX-201', 'Erie', 'Mingo and Wyandot', 1700, 1750)
R('FIX-201', 'Susquehanna', 'Delaware and Shawnee', 1700, 1750)
R('FIX-201', 'Natchez', 'Choctaw', 1750, 1750)
R('FIX-201', 'Caloosahatchee culture', 'Calusa', 1530, 1800)
R('FIX-201', 'Thule', 'Inuit', 1530, 1800)
# FIX-202
R('FIX-202', 'Cusabo', 'Narragansett and Wampanoag', 1530, 1800)
R('FIX-202', 'Kaskaskia', 'Ohio Valley peoples', 1530, 1650)
R('FIX-202', 'Kaskaskia', 'Mingo and Wyandot', 1700, 1750)
R('FIX-202', 'Hopi', 'Western Apache and Yavapai', 1530, 1800)
R('FIX-202', 'Hopie', 'Hopi', 1530, 1800)
for old, new in (('Tulalip', 'Snohomish'), ('Akaitcho', "Yellowknives (T'atsaot'ine)"), ('Selkirk', 'Northern Tutchone'),
                 ('Nunavik', 'Inuit (Nunavimmiut)'), ('Nunatsiavut', 'Labrador Inuit'), ('Eeyou Istchee', 'Eastern James Bay Cree')):
    R('FIX-202', old, new, 1530, 1800)
# FIX-203
for old, new in (('Montana', 'Montaukett'), ('Ninticoy', 'Nanticoke'), ('Kijkitat', 'Klickitat'), ('Tenimo', 'Tenino'),
                 ('Maiou', 'Maidu'), ('Kawahsu', 'Kawaiisu'), ('Saunan', 'Salinan'), ('Tlinoit', 'Tlingit'), ('Serano', 'Serrano'),
                 ('Cahulia', 'Cahuilla'), ('Suspiaq', 'Sugpiaq (Alutiiq)'), ('Riro', 'Piro'), ('Pewa', 'Tewa'), ('Naniaho', 'Naniaba'),
                 ('Obiwa', 'Ojibwa'), ('Yankontai', 'Yanktonai'), ('Winebago', 'Winnebago'), ('Chtimacha', 'Chitimacha')):
    R('FIX-203', old, new, 1530, 1800)
# FIX-204
R('FIX-204', 'South Carolina', 'Cusabo', 1650, 1650)
R('FIX-204', 'South Carolina', 'Carolina', 1700, 1715, realm=ENG, k=0)
R('FIX-204', 'New Amsterdam', 'New York', 1700, 1800, realm=ENG)
S('FIX-204', 'Hispaniola (Spain)', 'Saint-Domingue', 1700, 1700, LON < -71.7, realm=FRA, k=0)
R('FIX-204', 'Saint-Domingue', 'Saint-Domingue', 1700, 1800, realm=FRA)
R('FIX-204', 'Virgin Islands (Danemark)', 'Puerto Rico (Spain)', 1715, 1750, realm=SPA)
for old in ('Anguilla', 'Antigua and Barbuda', 'Montserrat', 'Turks and Caicos Islands'):
    R('FIX-204', old, old, 1700, 1800, realm=ENG, k=0)
for old in ('Guadeloupe', 'Martinique'):
    R('FIX-204', old, old, 1700, 1800, realm=FRA, k=0)
R('FIX-204', 'Saint Barthelemy', 'Saint-Barthélemy', 1700, 1783, realm=FRA, k=0)
R('FIX-204', 'Saint Barthelemy', 'Saint-Barthélemy', 1784, 1800, realm='Sweden', k=0)
R('FIX-204', 'Acadian Peninsula (UK)', 'Nova Scotia', 1783, 1800, realm=ENG, k=0)
NS = 'Viceroyalty of New Spain'
S('FIX-204', NS, 'Viceroyalty of New Granada', 1750, 1750, (LAT < 13) & (LON > -75), realm=SPA)
S('FIX-204', NS, 'Maya kingdoms', 1530, 1530, (LAT > 17.5) & (LON > -91), realm='Maya kingdoms', k=0)
S('FIX-204', NS, 'Itza kingdom', 1600, 1600, (LAT >= 16) & (LAT <= 18) & (LON >= -91) & (LON <= -89), realm='Itza kingdom', k=0)
S('FIX-204', 'Florida', 'Calusa', 1650, 1700, (LAT < 28.5) & (LON < -81), realm='Calusa', k=1)
S('FIX-204', 'Florida', 'Tequesta and Ais', 1650, 1700, (LAT < 28.5) & (LON >= -81), realm='Tequesta and Ais', k=1)
R('FIX-204', 'Polynesians', 'Kingdom of Hawaii', 1800, 1800, realm='Kingdom of Hawaii', k=0)
R('FIX-204', 'Sugpiaq (Alutiiq)', 'Russian America', 1800, 1800, realm='Russian Empire', k=0)
R('FIX-204', 'British North America', 'Inuit', 1800, 1800, realm='Inuit', k=1)

NOTE = {
    'FIX-200': 'Plains peoples are shown where they lived at this date; the Comanche, Kiowa, Cheyenne and Lakota reached the southern and western Plains only in the 1700s.',
    'FIX-201': 'Peoples and archaeological cultures are shown only while they existed.',
    'FIX-202': 'Peoples are named and placed as they were at this date, not by modern reservations, treaties or regions.',
    'FIX-203': 'Names respelled.',
    'FIX-204': 'Colonies are shown as colonies, under the power that held them at this date, and only where it held them (lines approximate).',
}
NEED_IDS = {'split', 'absorb', 'clear'}


def ents_named(js, name):
    return [i + 1 for i, e in enumerate(js['ents']) if e.get('a') and e['n'] == name]


def fix_era(y, LAND):
    key = F[y]; p = f'{SITE}/eras/{key}.json'; js = J(p)
    log = collections.Counter(); notes = []
    todo = [op for op in OPS if op[2] <= y <= op[3] and ents_named(js, op[4])]
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
        hit = ents_named(js, old)
        if not hit: continue
        if kind == 'rename':
            for i in hit:
                e = js['ents'][i - 1]; rn = js['realms'][e['r']]['n'] if e['r'] >= 0 else None
                like = js['realms'][e['r']]['g'] if e['r'] >= 0 else None
                target = o['realm'] or (o['new'] if rn == old or rn is None else None)
                if target and '|' in target:
                    have = {r['n'] for r in js['realms']}
                    target = next((t for t in target.split('|') if t in have), target.split('|')[0])
                if target: e['r'] = realm_of(js, target, like)
                for e2 in js['ents']:                      # the rest of a realm of that name follows it
                    if e2 is not e and e2['r'] >= 0 and rn == old and js['realms'][e2['r']]['n'] == old and target:
                        e2['r'] = e['r']
                e['n'] = o['new']; e['x'] = 1
                if o['k'] is not None: e['k'] = o['k']
                log[fix] += 1
        elif kind == 'split':
            m = np.isin(ids, hit) & o['mask']
            if not m.any(): continue
            src = js['ents'][hit[0] - 1]
            like = js['realms'][src['r']]['g'] if src['r'] >= 0 else None
            ex = [i for i in ents_named(js, o['new']) if i not in hit]
            if ex:
                ni = ex[0]
            else:
                tr = o['realm'] or o['new']
                if '|' in tr:
                    have = {r['n'] for r in js['realms']}
                    tr = next((t for t in tr.split('|') if t in have), tr.split('|')[0])
                js['ents'].append({'n': o['new'], 'r': realm_of(js, tr, like), 'k': src['k'] if o['k'] is None else o['k'],
                                   'p': 1, 'a': 1, 'x': 1})
                ni = len(js['ents'])
                while len(rows) < ni: rows.append(list(rows[int(np.bincount(orig[m]).argmax()) - 1]))
            ids[m] = ni; log[fix + ' px'] += int(m.sum())
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
for y in sorted(y for y in F if len(sys.argv) < 3 or y == int(sys.argv[2])):
    if y < 1530 or y > 1800: continue
    r = fix_era(y, LAND)
    if r: print(y, r, flush=True)
for ix in EMETA['eras']:
    js = J(f"{SITE}/eras/{ix['f']}.json")
    ix['c'] = len(js['notes'])
    ix['n'] = sum(1 for e in js['ents'] if e.get('a') and e['k'] == 0)
    ix['m'] = sum(1 for e in js['ents'] if e.get('a') and e['k'] == 1)
open(f'{SITE}/data/eras.json', 'w', encoding='utf-8').write(json.dumps(EMETA, ensure_ascii=True, separators=(',', ':')))
