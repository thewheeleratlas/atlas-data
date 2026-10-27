"""Shared helpers for the 1975 and 1989 maps (make_1975.py, make_1989.py)."""
import json, numpy as np
from scipy import ndimage
import era_tools as T

def era_ids(site, key):
    js = json.load(open(f'{site}/eras/{key}.json', encoding='utf-8'))
    return js, T.read_ids(js)

def ent_mask(js, ids, name):
    hits = [i + 1 for i, e in enumerate(js['ents']) if e['n'] == name and e.get('a')]
    assert hits, name
    return np.isin(ids, hits)

def nearest_split(a, b):
    """Every pixel goes to the nearer of masks a and b; returns the part that is nearer a."""
    da = ndimage.distance_transform_edt(~a); db = ndimage.distance_transform_edt(~b)
    return da <= db

def g_of(site, key, realm_name):
    """Registry index of a realm as an existing map uses it."""
    js = json.load(open(f'{site}/eras/{key}.json', encoding='utf-8'))
    hits = [r['g'] for r in js['realms'] if r['n'] == realm_name]
    assert hits, (key, realm_name)
    return hits[0]

def add_from(D, mask, name, realm, frm=(), kind=0):
    """A new territory on mask: unclaimed pixels, and pixels of the territories frm. Returns its pixel count."""
    frm_ids = [D.ent(n) for n in frm]
    m = mask & ((D.ids == 0) | np.isin(D.ids, frm_ids)) & D.LAND
    assert m.any(), f'{name}: nothing to add'
    D.js['ents'].append({'n': name, 'r': realm, 'k': kind, 'p': 1, 'a': 0, 'x': 1}); i = len(D.js['ents'])
    D.parent[i] = frm_ids[0] if frm_ids else 1   # ovmain rows are rebuilt after the layers are painted
    D.ids[m] = i; D.touched.update([i] + frm_ids)
    return int(m.sum())

def merge(D, into, names):
    """Territories names join territory into (their pixels; the territories are left empty)."""
    i = D.ent(into); n = 0
    for nm in names:
        j = D.ent(nm); m = D.ids == j; n += int(m.sum()); D.ids[m] = i; D.touched.update([i, j])
    return n

def set_realm(D, name, realm, new_name=None):
    return D.rename(name, new_name or name, realm=realm)

def fill(D, mask, name):
    """Unclaimed land pixels of mask join the territory name."""
    i = D.ent(name); m = mask & (D.ids == 0) & D.LAND
    assert m.any(), f'{name}: nothing to fill'
    D.ids[m] = i; D.touched.add(i); return int(m.sum())
