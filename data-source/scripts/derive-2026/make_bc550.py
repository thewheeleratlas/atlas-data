"""Derive the 550 BCE map, the Near East before Cyrus the Great, from the 500 BCE map.
Usage: python3 make_bc550.py <site folder>     (writes <site>/eras/bc550.json and updates <site>/data/*.json)

In 550 BCE the lands of the later Achaemenid Empire were four great powers:
  - the Median Empire (Iran, Armenia and Anatolia east of the Halys), with Persis (Anshan) under Cyrus as its
    vassal until his revolt (553-550);
  - Lydia under Croesus (Anatolia west of the Halys);
  - the Neo-Babylonian Empire under Nabonidus (Mesopotamia, Syria, the Levant and, from 552, the Tayma oasis);
  - Egypt under Amasis II of the 26th Dynasty, with Cyprus;
plus Cilicia (Hilakku), Greek Cyrene, and the peoples of Bactria, Sogdia and Arachosia beyond Media. The Indus
lands later taken by Darius go to Gandhara. Rome is still a kingdom (the Republic dates from 509). Everything
else, including the faith, culture and development layers, is the 500 BCE map's. Run from data-source/scripts/derive-2026/."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import era_tools as T

D = T.Derive(sys.argv[1], 'bc500')
G = lambda name: next(i for i, r in enumerate(D.meta['realms']) if r['n'] == name)
ACH = ['Achaemenid Empire']
geo, box = T.geo_mask, D.lon_box

r_med = D.realm('Median Empire', g=G('Mannaea and the Median tribes'))
r_bab = D.realm('Neo-Babylonian Empire', g=G('Babylonia'))
r_egy = D.realm('Egypt (26th Dynasty)', g=G('Egypt'))
r_cyr = D.realm('Cyrene', g=G('Cyrenaica'))
r_lyd = D.realm('Lydia', colour='#8e3b5a')
r_cil = D.realm('Cilicia (Hilakku)', colour='#5a8fa0')
r_bac = D.realm('Bactrians, Sogdians and Arachosians', colour='#8f9a78', kind=1)

n = {}
n['egypt'] = D.take('Egypt (26th Dynasty)', r_egy, box(24.5, 21.5, 35.6, 31.7) | box(32.0, 34.4, 34.8, 35.8), ACH)
n['cyrene'] = D.take('Cyrene', r_cyr, box(9.0, 22.0, 24.5, 33.5), ACH)
n['lydia'] = D.take('Lydia', r_lyd, geo([[25.0, 42.4], [35.9, 41.8], [34.6, 41.2], [33.6, 40.4], [33.3, 39.6], [33.6, 38.6],
                                            [33.0, 37.3], [30.5, 36.0], [25.0, 35.6]]), ACH)
n['cilicia'] = D.take('Cilicia (Hilakku)', r_cil, geo([[33.0, 35.9], [33.0, 37.3], [35.0, 37.9], [36.7, 37.4], [36.4, 36.1], [34.5, 36.3]]), ACH)
n['babylon'] = D.take('Neo-Babylonian Empire', r_bab, geo([[34.0, 36.6], [36.7, 37.4], [38.5, 37.3], [41.0, 37.4], [43.5, 36.5], [45.5, 34.5],
                                                          [47.5, 31.8], [48.6, 30.0], [47.5, 29.2], [39.0, 26.5], [34.8, 28.0], [34.2, 31.3]]), ACH)
n['persis'] = D.take('Persis (Anshan)', r_med, geo([[47.5, 31.8], [48.6, 30.0], [51.0, 26.8], [57.5, 26.0], [58.5, 28.5], [55.5, 31.5],
                                                   [51.5, 33.0], [48.5, 33.5]]), ACH)
n['gandhara'] = D.take('Gandhāra', None, box(67.8, 23.0, 78.0, 37.5), ACH)
n['bactria'] = D.take('Bactrians, Sogdians and Arachosians', r_bac, box(60.5, 23.0, 80.0, 46.0), ACH, kind=1)
D.rename('Achaemenid Empire', 'Median Empire', realm=r_med)
D.rename_realm('Achaemenid Empire', 'Achaemenid Empire (unused)')
D.rename('Roman Republic', 'Kingdom of Rome'); D.rename_realm('Roman Republic', 'Kingdom of Rome')

notes = ['Built from the 500 BCE map, adjusted to 550.',
         'Before Cyrus the Great: Media held Iran, Armenia and Anatolia east of the Halys, with Persis (Anshan) as its vassal; Lydia under Croesus held Anatolia west of the Halys; the Neo-Babylonian Empire of Nabonidus held Mesopotamia, Syria and the Levant; Egypt under Amasis II held Cyprus.',
         'Cyrus overthrew Media in 550–549 and took Lydia (c. 547) and Babylon (539); Cambyses took Egypt in 525.',
         'Rome was still ruled by kings; the Republic dates from 509.']
out, ix = D.save(-550, 'bc550', 'Before Cyrus the Great', notes, -500)
print('550 BCE written:', ', '.join(f'{k} {v:,} px' for k, v in n.items()), f"| {ix['n']} states, {ix['m']} peoples, {len(out['borders'])} border lines")
