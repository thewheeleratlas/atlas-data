"""Batch 4 (17 Oct 2026): name-only P2 fixes; no border shapes change. Usage: python3 fix_batch4.py <eras folder> <data folder>
FIX-108 1945 colonial names; FIX-109 1945 Manchuria label; FIX-110 1914 British protectorates in Arabia; FIX-111 1750 Prussia labels;
FIX-112 1900 Congo Free State sliver + Baluchistan label; FIX-113 Natural Earth abbreviations expanded; FIX-115 1200 Delhi placeholder.
Realm renames also move that year's entry in flags.json so realm-card flags keep working."""
import json, sys, os
J = lambda p: json.load(open(p)); Wr = lambda p, d: open(p, 'w').write(json.dumps(d, separators=(',', ':')))
E, D = sys.argv[1], sys.argv[2]
fl = J(f'{D}/flags.json'); reg = J(f'{D}/eras.json'); log = []
NE = {'Antigua and Barb.':'Antigua and Barbuda','Ashmore and Cartier Is.':'Ashmore and Cartier Islands','Bosnia and Herz.':'Bosnia and Herzegovina',
 'Br. Indian Ocean Ter.':'British Indian Ocean Territory','Brazilian I.':'Brazilian Island','British Virgin Is.':'British Virgin Islands','Cayman Is.':'Cayman Islands',
 'Central African Rep.':'Central African Republic','Clipperton I.':'Clipperton Island','Cook Is.':'Cook Islands','Coral Sea Is.':'Coral Sea Islands',
 'Cyprus U.N. Buffer Zone':'Cyprus UN Buffer Zone','Dem. Rep. Congo':'Democratic Republic of the Congo','Dominican Rep.':'Dominican Republic','Eq. Guinea':'Equatorial Guinea',
 'Faeroe Is.':'Faroe Islands','Falkland Is.':'Falkland Islands','Fr. Polynesia':'French Polynesia','Fr. S. Antarctic Lands':'French Southern and Antarctic Lands',
 'Heard I. and McDonald Is.':'Heard Island and McDonald Islands','Indian Ocean Ter.':'Australian Indian Ocean Territories','Marshall Is.':'Marshall Islands',
 'N. Cyprus':'Northern Cyprus','N. Mariana Is.':'Northern Mariana Islands','Pitcairn Is.':'Pitcairn Islands','S. Geo. and the Is.':'South Georgia and the South Sandwich Islands',
 'S. Sudan':'South Sudan','Solomon Is.':'Solomon Islands','Spratly Is.':'Spratly Islands','St. Kitts and Nevis':'Saint Kitts and Nevis','St. Pierre and Miquelon':'Saint Pierre and Miquelon',
 'St. Vin. and Gren.':'Saint Vincent and the Grenadines','Turks and Caicos Is.':'Turks and Caicos Islands','U.S. Minor Outlying Is.':'US Minor Outlying Islands',
 'U.S. Virgin Is.':'US Virgin Islands','W. Sahara':'Western Sahara','Wallis and Futuna Is.':'Wallis and Futuna','eSwatini':'Eswatini'}
EDITS = {  # year: [(old, new, lists, tag)]
 1945: [('Sudan','Anglo-Egyptian Sudan',('ents',),'FIX-108'), ('Guinea-Bissau (Portugal)','Portuguese Guinea',('ents',),'FIX-108'),
        ('Equatorial Guinea','Spanish Guinea',('ents','realms'),'FIX-108'), ('Somalia','Italian Somaliland (British administration)',('ents',),'FIX-108'),
        ('Republic of China','Manchuria',('ents',),'FIX-109')],
 1914: [('British Protectorate','British protectorates (Aden, Trucial States, Oman)',('ents',),'FIX-110')],
 1750: [('Prussia','East Prussia',('ents',),'FIX-111'), ('Brandenburg','Kingdom of Prussia (Brandenburg)',('ents',),'FIX-111')],
 1900: [('Belgian Congo','Congo Free State',('ents',),'FIX-112'), ('India','Baluchistan',('ents','realms'),'FIX-112')],
 1200: [('Sultanate of Delhi','Ghurid governors of Delhi',('ents','realms'),'FIX-115')],
}
def mvflag(y, old, new):
    r = fl['r']; ys = str(y)
    if old in r and ys in r[old]:
        r.setdefault(new, {})[ys] = r[old].pop(ys)
        if not r[old]: del r[old]
for f in sorted(os.listdir(E)):
    if not f.endswith('.json'): continue
    p = f'{E}/{f}'; d = J(p); y = d['y']; ch = 0
    for old, new, lists, tag in EDITS.get(y, []):
        n = 0
        for lst in lists:
            for e in d[lst]:
                if e.get('n') == old:
                    if lst == 'ents' and y == 1750 and old == 'Prussia' and e.get('a', 0) > 50000: continue
                    e['n'] = new; n += 1
                    if lst == 'realms': mvflag(y, old, new)
        assert n, (y, old); log.append(f'{tag} {y}: {old} -> {new} ({n})'); ch += n
    if y >= 1945:
        for lst in ('ents', 'realms'):
            for e in d[lst]:
                if e.get('n') in NE:
                    old = e['n']; e['n'] = NE[old]; ch += 1
                    if lst == 'realms': mvflag(y, old, NE[old])
                    log.append(f'FIX-113 {y} {lst}: {old} -> {NE[old]}')
    if ch: Wr(p, d)
for r in reg['realms']:
    if r.get('n') in NE: r['n'] = NE[r['n']]
Wr(f'{D}/eras.json', reg); Wr(f'{D}/flags.json', fl)
print('\n'.join(l for l in log if not l.startswith('FIX-113'))); print('FIX-113 renames:', sum(l.startswith('FIX-113') for l in log))
