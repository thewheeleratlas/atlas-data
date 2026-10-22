"""Batch 5 (22 Oct 2026): name-only fixes; no border shapes change. Usage: python3 fix_batch5.py <eras folder> <data folder>
FIX-120 misspelt or garbled names; FIX-121 out-of-date or unclear names; FIX-122 one spelling for Kyivan Rus';
FIX-123 "Hindu kingdoms" -> "Indian kingdoms" up to 400 CE.
Each rename applies to the realm and to territories with exactly the same name on that map. A realm rename also
moves that year's entry in flags.json (when the data folder has one) so realm-card flags keep working, and a name
in the realm registry (eras.json) is renamed once no map uses the old name any more.
Afterwards rebuild the search index: python3 build_realm_index.py (website: scripts/build_realm_index.py)."""
import json, sys, os
J = lambda p: json.load(open(p, encoding='utf-8'))
Wr = lambda p, d, a=False: open(p, 'w', encoding='utf-8').write(json.dumps(d, ensure_ascii=a, separators=(',', ':')))   # eras.json is ASCII-escaped; the rest is UTF-8
E, D = sys.argv[1], sys.argv[2]
FL = f'{D}/flags.json'
fl = J(FL) if os.path.exists(FL) else None
reg = J(f'{D}/eras.json'); log = []
ALL = None   # every map year
def years(*ys): return set(ys)
EARLY_INDIA = years(-323, -300, -200, -100, -1, 100, 200, 300, 400)
RENAMES = [  # (years or ALL, old, new, tag)
 (years(-1, 100, 200), 'Satavahanihara', 'Satavahana Empire', 'FIX-120'),
 (years(-1, 100, 200), 'Boihaenum', 'Marcomanni (Boiohaemum)', 'FIX-120'),
 (years(300), 'Rome (Diocletianus)', 'Roman Empire (Diocletian)', 'FIX-120'),
 (years(300), 'Rome (Maximian)', 'Roman Empire (Maximian)', 'FIX-120'),
 (years(300), 'Rome (Constantinus)', 'Roman Empire (Constantius)', 'FIX-120'),
 (years(300), 'Rome (Galerius)', 'Roman Empire (Galerius)', 'FIX-120'),
 (years(600), 'Shaskanka', 'Gauda (Shashanka)', 'FIX-120'),
 (ALL, 'Mamluke Sultanate', 'Mamluk Sultanate', 'FIX-120'),
 (years(1783), 'Mahratta states', 'Maratha states', 'FIX-120'),
 (years(-500, -200), 'Rome', 'Roman Republic', 'FIX-121'),
 (years(-200, -100), 'Maan', "Ma'in (Minaean Kingdom)", 'FIX-121'),
 (years(-100), 'Sarmates', 'Sarmatians', 'FIX-121'),
 (years(-100), 'Saces', 'Saka', 'FIX-121'),
 (years(100, 200), 'S. Xiongnu', 'Southern Xiongnu', 'FIX-121'),
 (years(400, 500), 'Ruanruan', 'Rouran Khaganate', 'FIX-121'),
 (years(500), 'Toba Wei', 'Northern Wei', 'FIX-121'),
 (years(700), 'Tufan Empire', 'Tibetan Empire', 'FIX-121'),
 (years(800, 900), 'Idrisid Caliphate', 'Idrisid dynasty', 'FIX-121'),
 (years(1066, 1100), 'Karkhanids', 'Kara-Khanid Khanate', 'FIX-121'),
 (years(1200, 1210), 'Kara Khitai Khaganate', 'Qara Khitai (Western Liao)', 'FIX-121'),
 (ALL, 'Malaysian Islamic states', 'Malay sultanates', 'FIX-121'),
 (ALL, 'Ming Chinese Empire', 'Ming Empire', 'FIX-121'),
 (years(1600, 1700, 1715, 1750, 1783), 'Netherlands', 'Dutch Republic', 'FIX-121'),
 (years(1783), 'Poland', 'Polish–Lithuanian Commonwealth', 'FIX-121'),
 (years(1900), 'Germany', 'German Empire', 'FIX-121'),
 (years(1914), 'Russia', 'Russian Empire', 'FIX-121'),
 (years(1945), 'China', 'Republic of China', 'FIX-121'),
 (ALL, 'Kyivan Rus', "Kyivan Rus'", 'FIX-122'),
 (ALL, 'Kievan Rus', "Kyivan Rus'", 'FIX-122'),
 (EARLY_INDIA, 'Hindu kingdoms and republics', 'Indian kingdoms and republics', 'FIX-123'),
 (EARLY_INDIA, 'Hindu kingdoms', 'Indian kingdoms', 'FIX-123'),
]
def mvflag(y, old, new):
    if fl is None: return
    r = fl['r']; ys = str(y)
    if old in r and ys in r[old]:
        r.setdefault(new, {})[ys] = r[old].pop(ys)
        if not r[old]: del r[old]
used = set(); found = {i: 0 for i in range(len(RENAMES))}
for f in sorted(os.listdir(E)):
    if not f.endswith('.json'): continue
    p = f'{E}/{f}'; d = J(p); y = d['y']; ch = 0
    for i, (ys, old, new, tag) in enumerate(RENAMES):
        if ys is not None and y not in ys: continue
        n = 0
        for lst in ('realms', 'ents'):
            for e in d[lst]:
                if e.get('n') == old:
                    e['n'] = new; n += 1
                    if lst == 'realms': mvflag(y, old, new)
        if n: log.append(f'{tag} {y}: {old} -> {new} ({n})'); found[i] += n; ch += n
    for lst in ('realms', 'ents'):
        for e in d[lst]: used.add(e.get('n'))
    if ch: Wr(p, d)
missing = [RENAMES[i][1] for i, n in found.items() if not n]
assert not missing, f'not found on any map: {missing}'
for r in reg['realms']:
    for ys, old, new, tag in RENAMES:
        if r.get('n') == old and old not in used:
            r['n'] = new; log.append(f'{tag} registry: {old} -> {new}')
Wr(f'{D}/eras.json', reg, True)
if fl is not None: Wr(FL, fl)
print('\n'.join(log)); print(len(log), 'changes')
