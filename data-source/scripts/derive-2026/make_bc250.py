"""Derive the 250 BCE map, the age of Ashoka and the First Punic War, from the 300 BCE map.
Usage: python3 make_bc250.py <site folder>     (writes <site>/eras/bc250.json and updates <site>/data/*.json)

Changes from 300 BCE:
  - Rome: the Roman confederation holds the peninsula south of the Arno-Rubicon line (Samnite Wars to 290,
    Pyrrhic War and Tarentum 272), and in the First Punic War (264-241) most of Sicily. Syracuse under Hiero II
    is a Roman ally; Carthage keeps Lilybaeum and Drepana in the west of the island, and Sardinia and Corsica.
  - The successor kingdoms after Ipsus (301) and Corupedium (281): Antigonid Macedon under Antigonus II holds
    Macedonia and Thessaly; the Aetolian and Achaean leagues, Sparta and Athens hold southern Greece; Thrace is
    Thracian and Celtic (Tylis); the Seleucid Empire holds Anatolia west of the Halys, Syria, Mesopotamia and Iran;
    Pergamon (from 263), Bithynia and Pontus (from 281) are their own kingdoms; the Galatians settled in central
    Anatolia (c. 275); the Ptolemies hold Coele-Syria and Phoenicia.
  - The Mauryan Empire under Ashoka (268-232), after the conquest of Kalinga (c. 261), holds the subcontinent
    north of the Tamil kingdoms of the far south.
  - China: the Zhou royal house ended in 256; Qin holds Shangdang, Luoyang and the Han valley as far as Ying.
Everything else, including the faith, culture and development layers, is the 300 BCE map's. Borders, areas and
labels are re-traced with the s6_eras.py code (era_tools.py). Run from data-source/scripts/derive-2026/."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import era_tools as T

D = T.Derive(sys.argv[1], 'bc300')
geo, box = T.geo_mask, D.lon_box
G = lambda name: next(i for i, r in enumerate(D.meta['realms']) if r['n'] == name)
n = {}

# ---- Italy and Sicily
ITALY = geo([[10.2, 43.75], [12.8, 44.1], [14.0, 43.6], [15.5, 42.6], [17.0, 41.9], [18.8, 40.6], [18.8, 39.8], [17.3, 38.9],
             [16.3, 37.85], [15.62, 37.85], [15.62, 38.3], [15.3, 38.7], [14.5, 40.0], [12.6, 41.1], [10.9, 42.4], [10.0, 43.2]])
ITALIC = ['Greek city-states', 'Etrurians', 'Sabines', 'Samnites', 'Rome', 'Hallstatt culture', 'Urnfield cultures']
r_rome = D.realm('Roman Republic')
n['italy'] = D.take('Roman Republic', r_rome, ITALY, [x for x in ITALIC if any(e['n'] == x for e in D.js['ents'])])
SYRACUSE = geo([[14.55, 36.65], [15.35, 36.6], [15.35, 37.85], [15.0, 37.85], [14.55, 37.2]])
r_syr = D.realm('Syracuse', colour='#c0874a')
n['syracuse'] = D.take('Syracuse', r_syr, SYRACUSE, ['Greek city-states', 'Carthaginian Empire'])
# the source map's 'Greek city-states' also covers Liguria; north of the Arno those lands are Ligurian
r_lig = D.realm('Ligurians', colour='#8f8a5c', kind=1)
n['liguria'] = D.take('Ligurians', r_lig, box(6.5, 43.4, 10.7, 45.2), ['Greek city-states'], kind=1)
n['sicily'] = D.take('Roman Republic', r_rome, box(12.9, 36.4, 15.7, 38.4), ['Carthaginian Empire', 'Greek city-states'])

# ---- Greece, Thrace and Anatolia
r_mac = D.realm('Macedon (Antigonid)', g=G('Empire of Alexander'))
r_grk = D.realm('Greek city-states')
EUROPE_W = box(19.0, 34.5, 26.2, 42.6)
n['macedon_from_antigonus'] = D.take('Kingdom of Kassander', None, EUROPE_W, ['Kingdom of Antigonus'])
n['greece'] = D.take('Greek leagues and city-states', r_grk, box(19.5, 34.5, 24.8, 38.9), ['Kingdom of Kassander'])
D.rename('Kingdom of Kassander', 'Macedon (Antigonid)', realm=r_mac)
r_thr = D.realm('Thracians', g=G('Thracians'))
THRACE = geo([[22.0, 44.6], [29.9, 44.6], [29.05, 41.25], [28.95, 41.0], [26.4, 40.2], [24.0, 40.6], [22.0, 41.3]])
n['thrace'] = D.take('Thracians and the Celts of Tylis', r_thr, THRACE, ['Kingdom of Lysimachus', 'Kingdom of Antigonus', 'Macedon (Antigonid)'], kind=1)
ANAT = ['Kingdom of Antigonus', 'Kingdom of Lysimachus', 'Cappadocia', 'Seleucid Kingdom']
r_per = D.realm('Pergamon', g=G('Pergamon'))
n['pergamon'] = D.take('Pergamon', r_per, geo([[26.7, 39.45], [27.6, 39.6], [28.2, 39.2], [27.9, 38.75], [26.9, 38.7], [26.65, 39.0]]), ANAT)
n['bithynia'] = D.take('Bithynia', None, geo([[29.05, 41.3], [32.4, 41.6], [32.4, 40.3], [30.6, 39.9], [29.05, 40.2]]), ANAT)
r_pon = D.realm('Pontus', colour='#7d5a9c')
n['pontus'] = D.take('Pontus', r_pon, geo([[33.6, 42.2], [41.8, 41.6], [41.6, 40.2], [37.5, 39.9], [34.8, 40.3], [33.6, 41.2]]), ANAT)
r_gal = D.realm('Galatians', g=G('Celts'), kind=1)
n['galatia'] = D.take('Galatians', r_gal, geo([[31.3, 40.4], [33.4, 40.9], [35.2, 40.3], [35.0, 38.9], [33.0, 38.8], [31.3, 39.3]]), ANAT, kind=1)
# the Ptolemies hold Coele-Syria and Phoenicia up to the Eleutherus
COELE = geo([[34.0, 31.2], [34.9, 33.0], [35.6, 34.62], [36.6, 34.62], [36.8, 33.4], [36.3, 31.9], [35.5, 31.0], [34.4, 31.0]])
n['coele_syria'] = D.take('Ptolemaic Kingdom', None, COELE, ['Kingdom of Antigonus', 'Arameans'])
# everything else the two Diadochi held passes to the Seleucids
n['seleucid'] = D.take('Seleucid Kingdom', None, box(19.0, 25.0, 60.0, 45.0), ['Kingdom of Antigonus', 'Kingdom of Lysimachus'])

# ---- India: Ashoka's empire reaches the Tamil kingdoms
INDIA_N = box(60.0, 12.9, 89.6, 37.0)
n['mauryan'] = D.take('Mauryan Empire', None, INDIA_N, ['Indian kingdoms and republics', 'Indian kingdoms'])
r_tam = D.realm('Tamil kingdoms (Cholas, Pandyas, Cheras)', g=G('Cholas'))
D.rename('Indian kingdoms and republics', 'Tamil kingdoms (Cholas, Pandyas, Cheras)', realm=r_tam)

# ---- China: the end of Zhou; Qin takes Shangdang, Luoyang and the Han valley
QIN = geo([[103.0, 36.6], [113.3, 36.6], [113.3, 34.2], [112.6, 32.6], [113.6, 30.6], [112.6, 29.6], [103.0, 29.6]])
n['qin'] = D.take('Qin', None, QIN, ['Zhou states'])
D.rename('Zhou states', 'Warring States (Zhao, Wei, Han, Chu, Yan, Qi)')
D.rename_realm('Zhou states', 'Warring States')

notes = ['Built from the 300 BCE map, adjusted to 250.',
         'Rome holds Italy south of the Arno and the Rubicon and, midway through the First Punic War (264–241), most of Sicily; Syracuse under Hiero II is a Roman ally, and Carthage keeps Lilybaeum, Drepana, Sardinia and Corsica.',
         'After Ipsus (301) and Corupedium (281): Antigonid Macedon holds Macedonia and Thessaly, the Aetolian and Achaean leagues, Sparta and Athens hold southern Greece, and the Seleucids hold Anatolia, Syria, Mesopotamia and Iran. Pergamon, Bithynia and Pontus are kingdoms of their own, the Galatians have settled in central Anatolia, and the Ptolemies hold Coele-Syria.',
         'Ashoka (268–232) rules the Mauryan Empire after conquering Kalinga (c. 261); only the Tamil kingdoms of the far south lie outside it.',
         'The Zhou royal house ended in 256; Qin holds Shangdang, Luoyang and the Han valley and will unify China in 221.']
out, ix = D.save(-250, 'bc250', 'Ashoka and the First Punic War', notes, -300)
A = {e['n']: e['a'] for e in out['ents'] if e.get('a')}
print('250 BCE written:', ', '.join(f'{k} {v:,} px' for k, v in n.items()))
print(' areas:', {k: f"{A.get(k, 0):,} km2" for k in ('Roman Republic', 'Syracuse', 'Seleucid Kingdom', 'Mauryan Empire', 'Qin', 'Macedon (Antigonid)', 'Pontus', 'Pergamon')})
print(f" {ix['n']} states, {ix['m']} peoples, {len(out['borders'])} border lines")
