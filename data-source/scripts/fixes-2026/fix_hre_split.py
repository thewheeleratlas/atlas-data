"""The German states inside the Holy Roman Empire, 1650-1750 (25 Oct 2026). Usage: python3 fix_hre_split.py <site folder>

FIX-132 1650, 1700, 1715, 1750: these maps drew most of Germany as one territory, the Holy Roman Empire, so Bavaria,
        Saxony, Württemberg and the other princely states had no card of their own. The larger states now have their
        own territories inside the Empire, with outlines taken from the nearest map that draws them:
          - Bavaria (the Electorate with the Upper Palatinate): its 1800 outline;
          - the Electoral Palatinate: the Rhenish Palatinate's 1815 outline (approximate: it leaves out the lands east
            of the Rhine around Heidelberg);
          - Saxony, Württemberg, Baden, Hohenzollern, Anhalt, Brunswick, Lippe-Detmold, Waldeck, Schaumburg-Lippe, the
            Saxon duchies (Thuringia), Hanover (Brunswick-Lüneburg before 1692), Holstein, Mecklenburg and Oldenburg:
            their 1783 outlines;
          - on the 1650 and 1700 maps, Brandenburg (its 1715 outline, part of the Brandenburg-Prussian realm), and the
            Habsburg hereditary lands (Austria and Bohemia) and Silesia (their 1783 outlines), which were drawn inside
            the Empire's territory.
        The many smaller states (Hesse, the ecclesiastical electorates, the Franconian and Swabian states, the imperial
        cities) stay in the Holy Roman Empire territory.
FIX-133 1650: Royal Hungary and a Habsburg territory were listed under the wrong realm (Austronesian peoples); they
        are the Habsburg Monarchy.
FIX-134 1783: Silesia was drawn as "Slavic tribes"; it was Prussian from 1742. The large territory labelled Bavaria
        also covered Franconia, Swabia, Hesse and the Rhineland; Bavaria keeps its 1800 outline with the Palatinate
        (both ruled by Charles Theodore from 1777), and the rest is the Holy Roman Empire's smaller states.
FIX-135 1800: Mecklenburg-Strelitz and Hanover were listed under the Kingdom of Great Britain; they are their own
        realms (Hanover's elector was the British king, but the electorate was a separate state).

Borders, areas and labels are re-traced with the s6_eras.py code in ../derive-2026/era_tools.py. Afterwards rebuild
the search index (build_realm_index.py)."""
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


S83, S00, S15, S715 = load('1783'), load('1800'), load('1815'), load('1715')
M = {n: mask(S83, n) for n in ('Saxony', 'Württemberg', 'Baden', 'Hohenzollern', 'Anhalt', 'Brunswick', 'Lippe-Detmold', 'Waldeck',
                               'Schaumburg-Lippe', 'Thuringia', 'Hanover', 'Holstein', 'Mecklenburg-Schwerin', 'Mecklenburg-Strelitz', 'Oldenburg')}
M['Habsburg'] = mask(S83, 'Habsburg Monarchy', 'Habsburg Monarchy')
M['Silesia'] = mask(S83, 'Slavic tribes')
M['Bavaria'] = mask(S00, 'Bavaria')
M['Palatinate'] = mask(S15, 'Palatinate')
M['Brandenburg'] = mask(S715, 'Brandenburg')
M['Mecklenburg'] = M['Mecklenburg-Schwerin'] | M['Mecklenburg-Strelitz']


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


STATES = [('Bavaria', 'Bavaria', None), ('Palatinate', 'Electoral Palatinate', 'Palatinate'), ('Saxony', 'Saxony', None),
          ('Württemberg', 'Württemberg', None), ('Baden', 'Baden', None), ('Hohenzollern', 'Hohenzollern', None),
          ('Anhalt', 'Anhalt', None), ('Brunswick', 'Brunswick', None), ('Lippe-Detmold', 'Lippe-Detmold', None),
          ('Waldeck', 'Waldeck', None), ('Schaumburg-Lippe', 'Schaumburg-Lippe', None), ('Thuringia', 'Thuringia', None)]

for key in ('1650', '1700', '1715', '1750'):
    E = Era(key)
    hre = [E.ent('Holy Roman Empire', 'Holy Roman Empire')]
    if key == '1650':   # FIX-133
        hab = E.realm('Habsburg Monarchy')
        for i, e in enumerate(E.js['ents'], 1):
            if e.get('a') and E.js['realms'][e['r']]['n'] == 'Austronesian peoples' and e['n'] in ('Royal Hungary', 'Habsburg Monarchy'):
                e['r'] = hab; e['x'] = 1; E.relabelled.add(i); E.log.append(f"{e['n']} -> Habsburg Monarchy")
    if key in ('1650', '1700'):
        E.take(M['Habsburg'], hre, 'Austria and Bohemia', 'Habsburg Monarchy')
        E.take(M['Silesia'], hre, 'Silesia', 'Habsburg Monarchy')
        E.take(M['Brandenburg'], hre, 'Brandenburg', 'Prussia')
        hn = 'Brunswick-Lüneburg' if key == '1650' else 'Hanover'
        E.take(M['Hanover'], hre, hn, hn, like='Hanover')
        E.take(M['Holstein'], hre, 'Holstein', 'Holstein')
        mn = 'Mecklenburg' if key == '1650' else 'Mecklenburg-Schwerin'
        E.take(M['Mecklenburg'], hre, mn, mn, like='Mecklenburg-Schwerin')
        E.take(M['Oldenburg'], hre, 'Oldenburg', 'Oldenburg')
    else:
        E.take(M['Hanover'], hre, 'Hanover', None, into=E.ent('Hanover'))
        E.take(M['Oldenburg'], hre, 'Oldenburg', None, into=E.ent('Oldenburg'))
        E.take(M['Habsburg'], hre, 'Habsburg Monarchy', None, into=E.ent('Habsburg Monarchy', 'Habsburg Monarchy'))
    for mk, name, like in STATES:
        E.take(M[mk], hre, name, name, like=like)
    E.notes.append('Bavaria, Saxony, Württemberg, the Electoral Palatinate and the other larger German states have their own territories inside the Holy Roman Empire, with outlines taken from the 1715, 1783, 1800 and 1815 maps; the smaller states stay in the Empire.')
    E.save()

# FIX-134 1783
E = Era('1783')
sil = E.ent('Slavic tribes'); e = E.js['ents'][sil - 1]
e.update({'n': 'Silesia', 'r': E.realm('Prussia'), 'k': 0, 'x': 1}); E.relabelled.add(sil); E.log.append('Slavic tribes -> Silesia (Prussia)')
bav = E.ent('Bavaria', 'Bavaria')
E.take(~(M['Bavaria'] | M['Palatinate']), [bav], 'Holy Roman Empire', 'Holy Roman Empire')
E.notes.append('Silesia was drawn as "Slavic tribes"; it was Prussian from 1742. Bavaria (with the Palatinate) has its own outline; the rest of southern and western Germany is the Holy Roman Empire\'s smaller states.')
E.save()

# FIX-135 1800
E = Era('1800')
for name in ('Mecklenburg-Strelitz', 'Hanover'):
    i = E.ent(name); E.js['ents'][i - 1]['r'] = E.realm(name); E.relabelled.add(i); E.log.append(f'{name} -> own realm')
E.save()

for ix in meta['eras']:
    js = J(f"{SITE}/eras/{ix['f']}.json")
    ix['c'] = len(js['notes'])
    ix['n'] = sum(1 for e in js['ents'] if e.get('a') and e['k'] == 0)
    ix['m'] = sum(1 for e in js['ents'] if e.get('a') and e['k'] == 1)
open(f'{SITE}/data/eras.json', 'w', encoding='utf-8').write(json.dumps(meta, ensure_ascii=True, separators=(',', ':')))
