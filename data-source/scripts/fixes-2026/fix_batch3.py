"""Batch 3 (17 Oct 2026): AP-years accuracy pass, P1 fixes. Names only; no border shapes change.
Usage: python3 fix_batch3.py <eras folder> <data folder>
- FIX-101: 'Japan (Heian period)' -> 'Kamakura shogunate' in eras 1185-1333 (shogunate founded 1185/1192).
- FIX-102: 'Manchu Empire' -> 'Qing Empire' in eras from 1644 (AP World CED term: Qing dynasty).
- FIX-103: realm 'Safavid Empire' -> 'Afsharid Iran' in eras after 1736 (Nader Shah deposed the Safavids in 1736).
- FIX-104: 1945 'Mali' -> 'French Sudan' (Mali is the 1960 name).
- FIX-105: 1945 Libya label typos: Tripolitania, Cyrenaica (British administration), Fezzan (French administration)."""
import json, sys, os
J = lambda p: json.load(open(p))
Wr = lambda p, d: open(p, 'w').write(json.dumps(d, separators=(',', ':')))
eras_dir, data_dir = sys.argv[1], sys.argv[2]
log = []
def ren(d, y, old, new, lists=('realms', 'ents'), tag=''):
    n = 0
    for lst in lists:
        for e in d[lst]:
            if e.get('n') == old: e['n'] = new; n += 1
    if n: log.append(f'{tag} {y}: {old} -> {new} ({n})')
    return n
for f in sorted(os.listdir(eras_dir)):
    if not f.endswith('.json'): continue
    p = f'{eras_dir}/{f}'; d = J(p); y = d['y']; ch = 0
    if 1185 <= y <= 1333: ch += ren(d, y, 'Japan (Heian period)', 'Kamakura shogunate', tag='FIX-101')
    if y >= 1644: ch += ren(d, y, 'Manchu Empire', 'Qing Empire', tag='FIX-102')
    if 1736 < y < 1800:
        for r in d['realms']:
            if r.get('n') == 'Safavid Empire':
                big = max((e for e in d['ents'] if e.get('r') == d['realms'].index(r)), key=lambda e: e.get('a', 0), default=None)
                if big and big['n'] != 'Safavid Empire' and big.get('a', 0) > 0:
                    log.append(f'FIX-103 {y}: realm Safavid Empire -> {big["n"]}'); r['n'] = big['n']; ch += 1
                    for e in d['ents']:
                        if e.get('n') == 'Safavid Empire' and not e.get('a'): e['n'] = big['n']
    if y == 1945:
        ch += ren(d, y, 'Mali', 'French Sudan', lists=('ents',), tag='FIX-104')
        for old, new in [('Tripolitana (UK Lybia)', 'Tripolitania (British administration)'), ('Cyraneica (UK Lybia)', 'Cyrenaica (British administration)'), ('Fezzan (Frech Lybia)', 'Fezzan (French administration)')]:
            ch += ren(d, y, old, new, lists=('ents',), tag='FIX-105')
    if ch: Wr(p, d)
g = J(f'{data_dir}/eras.json')
for r in g['realms']:
    if r.get('n') == 'Manchu Empire': r['n'] = 'Qing Empire'; log.append('FIX-102 registry: Manchu Empire -> Qing Empire')
Wr(f'{data_dir}/eras.json', g)
print('\n'.join(log))
