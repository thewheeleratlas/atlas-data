"""1530 map (22 Oct 2026): the Ottomans conquered the Mamluk Sultanate in 1517. Usage: python3 fix_1530_ottoman.py <eras folder>
FIX-124: the leftover 'Mamluk Sultanate' territory on the 1530 map (mostly Barqa, i.e. Cyrenaica, with a thin margin
of the Hejaz interior) joins the Ottoman Empire as 'Barqa (Cyrenaica)'. The leftover 'Aq Qoyunlu' sliver (the
confederation ended by 1508) on the Syrian Desert edge joins it as 'Syrian Desert'. No shapes are redrawn: only which
realm the two territories belong to. The empty realm entries stay in the file so other realm numbers don't move.
Afterwards rebuild the search index (build_realm_index.py)."""
import json, sys
E = sys.argv[1]; p = f'{E}/1530.json'
d = json.load(open(p, encoding='utf-8'))
assert d['y'] == 1530
ott = [i for i, r in enumerate(d['realms']) if r['n'] == 'Ottoman Empire']; assert len(ott) == 1; ott = ott[0]
moves = {'Mamluk Sultanate': 'Barqa (Cyrenaica)', 'Aq Qoyunlu': 'Syrian Desert'}
done = []
for e in d['ents']:
    if e.get('n') in moves and e.get('r') != ott:
        old = e['n']; e['n'] = moves[old]; e['r'] = ott; done.append(old)
assert sorted(done) == sorted(moves), done
d['notes'].insert(0, 'The Ottomans conquered the Mamluk Sultanate in 1517; Egypt, Syria, the Hejaz and the Mamluk claim to Barqa (Cyrenaica) were Ottoman. Still to be redrawn: Iraq, which was Safavid until Baghdad fell in 1534.')
open(p, 'w', encoding='utf-8').write(json.dumps(d, ensure_ascii=False, separators=(',', ':')))
print('FIX-124 1530:', ', '.join(f'{o} -> {moves[o]} (Ottoman Empire)' for o in done))
