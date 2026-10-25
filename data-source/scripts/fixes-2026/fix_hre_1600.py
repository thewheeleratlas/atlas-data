"""The German states inside the Holy Roman Empire on the 1600 map (25 Oct 2026). Usage: python3 fix_hre_1600.py <site folder>

FIX-136 1600: the map drew most of Germany, with Austria and Bohemia, as one Holy Roman Empire territory. As on the
        1650-1750 maps (fix_hre_split.py), the larger states get their own territories, with outlines from the nearest
        map that draws them, cut back to their 1600 extent where it was clearly smaller:
          - Habsburg lands: Austria, Bohemia, Silesia and Lusatia (Bohemian until 1635, so taken out of Saxony's
            1783 outline east of about 14 degrees E);
          - Bavaria: its 1800 outline without the Upper Palatinate, which was the Elector Palatine's until 1628 and goes
            with the Electoral Palatinate (the Rhenish Palatinate's 1815 outline);
          - Brandenburg: its 1715 outline cut to the Mark (without Cleves, Mark, Magdeburg, Halberstadt and Pomerania);
          - the Duchy of Pomerania: the Baltic coast between the Recknitz and the Leba, from the 1783 outlines;
          - Saxony, Württemberg, Baden, Hohenzollern, Anhalt, Brunswick, Lippe-Detmold, Waldeck, the Saxon duchies,
            Brunswick-Lüneburg, Holstein, Mecklenburg and Oldenburg: their 1783 outlines.
FIX-137 1600: Royal Hungary was listed under the wrong realm (Austronesian peoples); it is the Habsburg Monarchy.

Outlines are approximate. Borders, areas and labels are re-traced with the s6_eras.py code in ../derive-2026/era_tools.py.
Afterwards rebuild the search index (build_realm_index.py)."""
import copy, json, os, sys
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'derive-2026'))
import era_tools as T

SITE = sys.argv[1]
J = lambda p: json.load(open(p, encoding='utf-8'))
ORDER = ['n', 'r', 'k', 'p', 'a', 'b', 'l', 'w', 'a3', 'x', 'c']
meta = J(f'{SITE}/data/eras.json')
LAND = T.land_mask(f'{SITE}/eras', [e['f'] for e in meta['eras']])


def load(key):
    js = J(f'{SITE}/eras/{key}.json')
    return js, T.read_ids(js)


def mask(src, name, realm=None):
    js, ids = src
    hits = [i + 1 for i, e in enumerate(js['ents']) if e['n'] == name and e.get('a') and (realm is None or js['realms'][e['r']]['n'] == realm)]
    assert len(hits) == 1, (name, hits)
    return ids == hits[0]


def reg(name, like=None):
    """registry index for a realm name: an exact match, else the entry of `like`, else a new entry."""
    for i, r in enumerate(meta['realms']):
        if r['n'] == name: return i
    if like:
        for i, r in enumerate(meta['realms']):
            if r['n'] == like: return i
    meta['realms'].append({'k': name.lower(), 'c': '#7a6a8a', 't': 0, 'n': name})
    return len(meta['realms']) - 1


class Era:
    def __init__(self, key):
        self.key = key
        self.js, self.ids = load(key)
        same, bad = T.check_roundtrip(self.js, LAND)
        hand = {x[0] for x in bad if x[1] == x[2] and x[3] == x[4]}
        assert same and len(hand) == len(bad), f'tracing does not reproduce the {key} map; stop'
        self.hand = hand; self.orig = self.ids.copy(); self.notes = []; self.new = []; self.log = []
        self.relabelled = set()

    def realm(self, name, like=None):
        R = self.js['realms']
        for i, r in enumerate(R):
            if r['n'] == name: return i
        R.append({'g': reg(name, like), 'n': name}); return len(R) - 1

    def ent(self, name, realm=None):
        hits = [i + 1 for i, e in enumerate(self.js['ents']) if e['n'] == name and e.get('a') and (realm is None or self.js['realms'][e['r']]['n'] == realm)]
        assert len(hits) == 1, (self.key, name, hits)
        return hits[0]

    def take(self, m, frm, name, realm, like=None, into=None):
        """pixels of mask m now in entities frm go to entity `into`, or to a new entity `name` in realm `realm`."""
        sel = m & np.isin(self.ids, frm)
        n = int(sel.sum())
        if n < 3: return 0
        if into is None:
            self.js['ents'].append({'n': name, 'r': self.realm(realm, like), 'k': 0, 'p': 1, 'a': 0, 'x': 1})
            into = len(self.js['ents']); self.new.append((into, frm[0]))
        self.ids[sel] = into; self.log.append(f'{name} {n}px')
        return n

    def save(self):
        js, ids = self.js, self.ids
        changed = ids != self.orig
        touched = (set(np.unique(self.orig[changed]).tolist()) | set(np.unique(ids[changed]).tolist()) | self.relabelled) - {0}
        for i in touched:
            e = js['ents'][i - 1]; a, b, l = T.stats(ids, i)
            if e['n'] in self.hand and a and e.get('l') and i not in self.relabelled: l = e['l']
            e['a'] = a
            for k, v in (('b', b), ('l', l)):
                if v is None: e.pop(k, None)
                else: e[k] = v
        js['ents'] = [{k: e[k] for k in ORDER if k in e} for e in js['ents']]
        js['borders'] = T.borders(ids, LAND)
        js['notes'] += self.notes
        js['_png'] = T.write_ids(ids)
        try:
            import base64, oxipng
            js['_png'] = base64.b64encode(oxipng.optimize_from_memory(base64.b64decode(js['_png']), level=4)).decode('ascii')
        except ImportError:
            pass
        assert (T.read_ids(js) == ids).all()
        open(f'{SITE}/eras/{self.key}.json', 'w', encoding='utf-8').write(json.dumps(js, ensure_ascii=False, separators=(',', ':')))
        if self.new:
            p = f'{SITE}/data/ovmain.json'; d = J(p); rows = d['eras'][self.key]
            for ni, parent in self.new:
                while len(rows) < ni: rows.append(copy.deepcopy(rows[parent - 1]))
            open(p, 'w', encoding='utf-8').write(json.dumps(d, ensure_ascii=True, separators=(',', ':')))
        print(self.key, '; '.join(self.log), flush=True)



S83, S00, S15, S715 = load('1783'), load('1800'), load('1815'), load('1715')
M = {n: mask(S83, n) for n in ('Saxony', 'Württemberg', 'Baden', 'Hohenzollern', 'Anhalt', 'Brunswick', 'Lippe-Detmold', 'Waldeck',
                               'Thuringia', 'Hanover', 'Holstein', 'Mecklenburg-Schwerin', 'Mecklenburg-Strelitz', 'Oldenburg')}
M['Habsburg'] = mask(S83, 'Habsburg Monarchy', 'Habsburg Monarchy')
M['Silesia'] = mask(S83, 'Silesia')
M['Prussia83'] = mask(S83, 'Prussia', 'Prussia')
M['Bavaria'] = mask(S00, 'Bavaria')
M['Palatinate'] = mask(S15, 'Palatinate')
M['Brandenburg'] = mask(S715, 'Brandenburg')
M['Mecklenburg'] = M['Mecklenburg-Schwerin'] | M['Mecklenburg-Strelitz']
box = lambda x0, y0, x1, y1: T.geo_mask([[x0, y0], [x1, y0], [x1, y1], [x0, y1]])
UPPER_PAL = box(11.25, 48.95, 12.95, 50.05)
LUSATIA = box(14.05, 50.75, 15.4, 52.2) | box(13.55, 51.45, 15.4, 52.2)
MARK = box(11.2, 51.6, 15.7, 53.45) & ~box(11.0, 51.6, 12.3, 52.3)
POMERANIA = box(12.4, 53.3, 17.7, 54.9)

E = Era('1600')
hre = [E.ent('Holy Roman Empire', 'Holy Roman Empire')]
hab = E.realm('Habsburg Monarchy')
for i, e in enumerate(E.js['ents'], 1):   # FIX-137
    if e.get('a') and E.js['realms'][e['r']]['n'] == 'Austronesian peoples' and e['n'] == 'Royal Hungary':
        e['r'] = hab; e['x'] = 1; E.relabelled.add(i); E.log.append('Royal Hungary -> Habsburg Monarchy')
E.take(M['Habsburg'], hre, 'Austria and Bohemia', 'Habsburg Monarchy')
E.take(M['Silesia'], hre, 'Silesia', 'Habsburg Monarchy')
E.take(M['Saxony'] & LUSATIA, hre, 'Lusatia', 'Habsburg Monarchy')
E.take(M['Brandenburg'] & MARK, hre, 'Brandenburg', 'Brandenburg', like='Prussia')
E.take((M['Brandenburg'] | M['Prussia83'] | M['Mecklenburg']) & POMERANIA & ~M['Mecklenburg'] & ~MARK, hre, 'Pomerania', 'Pomerania')
E.take(M['Bavaria'] & UPPER_PAL, hre, 'Upper Palatinate', 'Electoral Palatinate', like='Palatinate')
E.take(M['Palatinate'], hre, 'Electoral Palatinate', 'Electoral Palatinate', like='Palatinate')
E.take(M['Bavaria'], hre, 'Bavaria', 'Bavaria')
E.take(M['Hanover'], hre, 'Brunswick-Lüneburg', 'Brunswick-Lüneburg', like='Hanover')
E.take(M['Holstein'], hre, 'Holstein', 'Holstein')
E.take(M['Mecklenburg'], hre, 'Mecklenburg', 'Mecklenburg', like='Mecklenburg-Schwerin')
E.take(M['Oldenburg'], hre, 'Oldenburg', 'Oldenburg')
for name in ('Saxony', 'Württemberg', 'Baden', 'Hohenzollern', 'Anhalt', 'Brunswick', 'Lippe-Detmold', 'Waldeck', 'Thuringia'):
    E.take(M[name], hre, name, name)
E.notes.append('Bavaria, Saxony, Brandenburg, Pomerania, Württemberg, the Electoral Palatinate and the other larger German states have their own territories inside the Holy Roman Empire, and Austria, Bohemia, Silesia and Lusatia are Habsburg lands; outlines are taken from the 1715, 1783, 1800 and 1815 maps and are approximate.')
E.save()

for ix in meta['eras']:
    js = J(f"{SITE}/eras/{ix['f']}.json")
    ix['c'] = len(js['notes'])
    ix['n'] = sum(1 for e in js['ents'] if e.get('a') and e['k'] == 0)
    ix['m'] = sum(1 for e in js['ents'] if e.get('a') and e['k'] == 1)
open(f'{SITE}/data/eras.json', 'w', encoding='utf-8').write(json.dumps(meta, ensure_ascii=True, separators=(',', ':')))
