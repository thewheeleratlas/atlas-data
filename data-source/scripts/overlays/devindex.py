"""Per-capita development index for the territory cards ("Development" row).

From 1815: income per person. Each pixel takes the GDP per capita of the modern country it lies in (Maddison Project
Database 2020, Bolt & van Zanden, CC BY 4.0, via Our World in Data), interpolated to the era's year; gaps are filled
from Maddison's regional series. A territory's value is the population-weighted geometric mean over its pixels.
Before 1815: Maddison is too sparse, so the index uses urbanisation instead: the population-weighted mean of the
development (urban) layer, so empty desert and forest no longer dilute the score.
Either way the score is relative to its own era: 0 = the 5th and 100 = the 95th percentile of territories,
weighted by population, so "Very high" means among the most developed places of that time.
"""
import csv, json, math, collections, os
import numpy as np
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
SP = os.environ.get('HHA_ATLAS', './atlas/')   # an atlas site folder with data/world.json and tiles/ids/0_0_0.png
GDP_FROM = 1815

S = collections.defaultdict(dict)
for r in csv.DictReader(open(f'{HERE}/maddison2020.csv')):
    if r['GDP per capita']: S[r['Entity']][int(r['Year'])] = float(r['GDP per capita'])
SER = {k: (np.array(sorted(v)), np.log(np.array([v[y] for y in sorted(v)]))) for k, v in S.items()}

WORLD = json.load(open(SP + 'data/world.json'))['countries']
ALIAS = {'Dem. Rep. Congo': 'Democratic Republic of Congo', "Côte d'Ivoire": "Cote d'Ivoire", 'S. Sudan': 'Sudan', 'Eritrea': 'Ethiopia',
         'Somaliland': None, 'Kosovo': 'Serbia', 'eSwatini': 'Eswatini', 'N. Cyprus': 'Cyprus', 'Macao': 'Hong Kong', 'W. Sahara': 'Morocco',
         'Timor-Leste': 'Indonesia', 'Brunei': 'Malaysia', 'Bosnia and Herz.': 'Bosnia and Herzegovina', 'Czech Rep.': 'Czechia',
         'Central African Rep.': 'Central African Republic', 'Dominican Rep.': 'Dominican Republic', 'Eq. Guinea': 'Equatorial Guinea',
         'Macedonia': 'North Macedonia', 'United States of America': 'United States', 'Cabo Verde': 'Cape Verde', 'Guyana': 'Venezuela',
         'Suriname': 'Venezuela', 'Belize': 'Guatemala', 'Bahamas': 'Jamaica', 'Bhutan': 'Nepal', 'Maldives': 'Sri Lanka',
         'Siachen Glacier': 'India', 'Baikonur': 'Kazakhstan', 'Cyprus U.N. Buffer Zone': 'Cyprus', 'Dhekelia': 'Cyprus', 'Akrotiri': 'Cyprus',
         'Greenland': 'Denmark', 'Falkland Is.': 'United Kingdom'}
FSU = {'Russia', 'Ukraine', 'Belarus', 'Moldova', 'Estonia', 'Latvia', 'Lithuania', 'Armenia', 'Georgia', 'Azerbaijan',
       'Kazakhstan', 'Uzbekistan', 'Turkmenistan', 'Kyrgyzstan', 'Tajikistan', 'Baikonur'}
BALKAN = {'Albania', 'Bosnia and Herz.', 'Serbia', 'Croatia', 'Slovenia', 'Montenegro', 'Macedonia', 'North Macedonia', 'Kosovo'}
def region(c):
    n, sub = c['name'], c['sub']
    if n in FSU: return 'Former USSR'
    if n in BALKAN or sub == 'Eastern Europe': return 'Eastern Europe'
    if sub in ('Western Europe', 'Northern Europe', 'Southern Europe'): return 'Western Europe'
    if sub in ('Northern America', 'Australia and New Zealand'): return 'Western Offshoots'
    if sub in ('South America', 'Central America', 'Caribbean'): return 'Latin America'
    if sub in ('Western Asia', 'Northern Africa') or n == 'Iran': return 'Middle East'
    if sub == 'Eastern Asia': return 'East Asia'
    if sub in ('Southern Asia', 'South-Eastern Asia', 'Melanesia', 'Micronesia', 'Polynesia'): return 'South and South-East Asia'
    if 'Africa' in sub: return 'Sub-Sahara Africa'
    return 'World'
def interp(name, y):
    ys, lv = SER[name]
    if y <= ys[0]: return lv[0]
    if y >= ys[-1]: return lv[-1]
    return float(np.interp(y, ys, lv))
def country_log_gdp(c, y):
    n = c['name']
    ent = ALIAS.get(n, n) if n in ALIAS else (n if n in SER else (c['long'] if c['long'] in SER else None))
    if ent is None or ent not in SER:
        sov = c.get('sov'); ent = ALIAS.get(sov, sov) if sov and (ALIAS.get(sov, sov) in SER) else None
    reg = region(c)
    if ent is None: return interp(reg, y)
    ys, lv = SER[ent]
    if y >= ys[0] or reg not in SER: return interp(ent, y)
    # before the country's own series starts: follow its region, keeping the country's relative position
    return interp(reg, y) + (lv[0] - interp(reg, ys[0]))
_cid = None
def country_grid():
    global _cid
    if _cid is None:
        a = np.array(Image.open(SP + 'tiles/ids/0_0_0.png').convert('RGB')).astype(np.int64)
        cid = a[..., 0] | (a[..., 1] << 8)
        _cid = np.array(Image.fromarray(cid.astype(np.int32)).resize((4096, 2111), Image.NEAREST)).astype(np.int64)
    return _cid
def pixel_log_gdp(y):
    cid = country_grid(); n = cid.max() + 1
    tab = np.full(n, np.nan)
    for c in WORLD:
        if c['id'] < n: tab[c['id']] = country_log_gdp(c, y)
    g = tab[cid]
    return g    # nan where no modern country
def wpct(v, w, q):
    o = np.argsort(v); v, w = v[o], w[o]; c = np.cumsum(w); c /= c[-1]
    return float(np.interp(q, c, v))
def scores(year, ids, nent, dev, wpop):
    """Return (score 0-100 per territory index 1..nent, gdp per capita or 0)."""
    flat = ids.ravel(); w = wpop.ravel()
    if year >= GDP_FROM:
        g = pixel_log_gdp(year).ravel(); ok = ~np.isnan(g) & (flat > 0)
        sw = np.bincount(flat[ok], weights=w[ok], minlength=nent + 1)
        sg = np.bincount(flat[ok], weights=(w * np.nan_to_num(g))[ok], minlength=nent + 1)
        val = np.where(sw > 0, sg / np.maximum(sw, 1e-30), np.nan)
    else:
        ok = flat > 0
        sw = np.bincount(flat[ok], weights=w[ok], minlength=nent + 1)
        sd = np.bincount(flat[ok], weights=(w * dev.ravel())[ok], minlength=nent + 1)
        val = np.where(sw > 0, sd / np.maximum(sw, 1e-30), np.nan)
    good = ~np.isnan(val); good[0] = False
    lo, hi = wpct(val[good], sw[good], 0.05), wpct(val[good], sw[good], 0.95)
    sc = np.clip((val - lo) / max(hi - lo, 1e-9) * 100, 0, 100)
    sc = np.where(good, np.round(sc), 0).astype(int)
    gdp = np.where(good, np.round(np.exp(val), -1), 0).astype(int) if year >= GDP_FROM else np.zeros(nent + 1, int)
    return sc, gdp
