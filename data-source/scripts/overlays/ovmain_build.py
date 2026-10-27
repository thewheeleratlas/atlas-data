"""Per-territory main faith, main culture and development for every era -> data/ovmain.json.
Main faith/culture = largest share of the territory's estimated population, where population is approximated by
true pixel area x (development + 2)^1.5, with ice caps discounted. Hand corrections (CURATED) then override major
territories where that approximation is known to pick the wrong group. Development = per-capita index relative to its era (devidx/devindex.py): income per person from 1815, urbanisation before."""
import json, numpy as np, sys, csv
from PIL import Image
sys.path.insert(0, '.')
SITE = sys.argv[1] if len(sys.argv) > 1 else 'cand/'
from popw import row_lat, weights as popweights
sys.path.insert(0, 'devidx')
from devindex import scores as dev_scores
def rgb(p): return np.array(Image.open(SITE + p).convert('RGB')).astype(np.int64)
R = json.load(open(SITE + 'data/religions.json')); C = json.load(open(SITE + 'data/cultures.json'))
RI = R['items'] or R['faiths']; CI = C['items'] or C['faiths']
RN = {x['n']: i + 1 for i, x in enumerate(RI)}; CN = {x['n']: i + 1 for i, x in enumerate(CI)}
H = 2111
lat_e = np.array([row_lat(y) for y in range(H + 1)]); A = np.abs(np.sin(lat_e[:-1]) - np.sin(lat_e[1:]))[:, None]
T = np.load('terrain4096.npy').astype(float); br = T.mean(axis=2); sat = T.max(axis=2) - T.min(axis=2)
HAB = np.where((br > 205) & (sat < 28), 0.03, 1.0)
CURATED = [  # (territory names, first year, last year, main faith, main culture) -- sources: standard census figures / references
    (['Nigeria'], 1900, 2026, None, 'Hausa'),
    (['Dutch East Indies', 'Netherlands Indies', 'Netherlands East Indies (Republic proclaimed)', 'Indonesia'], 1700, 2026, None, 'Javanese'),
    (['Bechuanaland', 'Botswana'], 1880, 2026, None, 'Sotho-Tswana'),
    (['South Africa', 'Union of South Africa'], 1900, 2026, None, 'Nguni (Zulu, Xhosa, Swazi)'),
    (['Cape Colony'], 1871, 1900, None, 'Nguni (Zulu, Xhosa, Swazi)'),
    (['Ottoman Empire', 'Ottoman Sultanate'], 1400, 1922, None, 'Turkish'),
    (['Austria Hungary', 'Austro-Hungarian Empire'], 1867, 1918, None, 'German'),
    (['Iraq', 'Kingdom of Iraq'], 1900, 2026, 'Shia Islam', None),
    (['Kenya'], 1960, 2026, None, 'East African Bantu (Kikuyu, Sukuma, Nyamwezi)'),
    (['Chad'], 1945, 2026, None, 'Central Sudanic peoples (Sara, Fur)'),
    (['Mali'], 1945, 2026, None, 'Mande (Mandinka, Bambara, Soninke)'),
    (['Niger'], 1945, 2026, None, 'Hausa'),
    (['French West Africa'], 1895, 1958, None, 'Mande (Mandinka, Bambara, Soninke)'),
    (['Grand Duchy of Moscow', 'Tsardom of Russia', 'Russian Empire', 'Russia'], 1400, 2026, 'Eastern Orthodox Christianity', 'Russian'),
    (['Makkura'], 600, 1400, 'Oriental Orthodox Christianity', 'Nubian'),
    (['Roman Republic', 'Roman Empire'], -100, 299, None, 'Latin (Roman)'),   # the Latin West counts as several cultures, so Greek was largest
    (['Volga Bulgars'], 922, 1240, 'Sunni Islam', None),
    (['Xixia'], 1038, 1227, 'Mahayana Buddhism', 'Qiang and Tangut'),
    (['Poland'], 1000, 1300, None, 'Polish'),
    (['Ethiopia', 'Abyssinia', 'Zagwe Ethiopia'], 330, 2026, 'Oriental Orthodox Christianity', None),
    (['Peru'], 1821, 1940, None, 'Quechua'),
    (['Viceroyalty of Peru'], 1542, 1824, None, 'Quechua'),
    (['Malaya'], 1400, 1900, 'Sunni Islam', 'Malay'),
    (['Maratha', 'Maratha Confederacy'], 1674, 1818, None, 'Marathi'),
    (['Western Australia (UK)'], 1890, 1901, 'Protestant Christianity', 'Australian and New Zealander'),
    (['Germany'], 2010, 2026, 'Nonreligious majority', None),
    (["Côte d'Ivoire", 'Ivory Coast'], 1994, 2026, 'Sunni Islam', 'Akan'),    (['Dhekelia', 'Akrotiri'], 1961, 2026, 'Eastern Orthodox Christianity', 'Greek'),   # tiny UK bases: border pixels spill into N. Cyprus
]
for names, y0, y1, rf, cf in CURATED:
    assert rf is None or rf in RN, rf; assert cf is None or cf in CN, cf
idx = [e for e in json.load(open(SITE + 'data/eras.json'))['eras']]
out = {}; changes = []
for e in idx:
    f, yr = e['f'], e['y']
    js = json.load(open(SITE + f'eras/{f}.json')); n = len(js['ents']) + 1
    a = rgb(f'eras/{f}.png'); ids = a[..., 0] | (a[..., 1] << 8)
    rel = rgb(f'rel/{f}.png')[..., 0]; c = rgb(f'cul/{f}.png'); cul = c[..., 0] | (c[..., 1] << 8)
    dev = rgb(f'dev/{f}.png')[..., 0].astype(float)
    w = (A * HAB * (dev + 2) ** 1.5).ravel(); flat = ids.ravel()
    mains = []
    for arr, items in [(rel, RI), (cul, CI)]:
        k = len(items) + 1
        M = np.bincount(flat * k + arr.ravel(), weights=w, minlength=n * k).reshape(n, k); M[:, 0] = 0
        na = next((i + 1 for i, x in enumerate(items) if x['id'] == 'na'), None)
        if na:   # 'n/a' is the main value only when it covers most of the territory; otherwise the largest known group
            tot = M.sum(axis=1); mostly_na = M[:, na] > 0.5 * tot; Mk = M.copy(); Mk[:, na] = 0
            best = Mk.argmax(axis=1); best[Mk.max(axis=1) <= 0] = 0; best[mostly_na] = na
        else:
            best = M.argmax(axis=1); best[M.max(axis=1) <= 0] = 0
        mains.append(best)
    cnt = np.bincount(flat, minlength=n); dsum = np.bincount(flat, weights=dev.ravel(), minlength=n)
    davg = np.where(cnt > 0, dsum / np.maximum(cnt, 1), 0)
    dsc, dgdp = dev_scores(yr, ids, n - 1, dev, popweights(dev))
    rows = []
    for i, en in enumerate(js['ents']):
        r_, c_ = int(mains[0][i + 1]), int(mains[1][i + 1])
        for names, y0, y1, rf, cf in CURATED:
            if en['n'] in names and y0 <= yr <= y1:
                if rf and RN[rf] != r_: changes.append((f, en['n'], 'faith', RI[r_ - 1]['n'] if r_ else '-', rf)); r_ = RN[rf]
                if cf and CN[cf] != c_: changes.append((f, en['n'], 'culture', CI[c_ - 1]['n'] if c_ else '-', cf)); c_ = CN[cf]
        rows.append([r_, c_, int(dsc[i + 1]), int(dgdp[i + 1])])
    out[f] = rows
json.dump({'about': 'Per territory and era: [main faith, main culture (1-based indexes into religions.json / cultures.json items), development score 0-100 relative to its era, GDP per person in 2011 dollars (0 before 1815)]. Population-weighted estimates plus hand corrections.', 'eras': out},
          open(SITE + 'data/ovmain.json', 'w'), separators=(',', ':'))
with open('ovmain-corrections.csv', 'w', newline='', encoding='utf-8') as fh:
    wr = csv.writer(fh); wr.writerow(['Era map', 'Territory', 'Field', 'Computed', 'Corrected to']); wr.writerows(changes)
print('eras', len(out), 'corrections applied', len(changes))
