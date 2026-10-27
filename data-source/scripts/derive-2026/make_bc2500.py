"""Derive the 2500 BCE map, the age of the pyramids, from the 3000 BCE map.
Usage: python3 make_bc2500.py <site folder>     (writes <site>/eras/bc2500.json and updates <site>/data/*.json)

About 2500 BCE:
  - Egypt is in the Old Kingdom, after the Great Pyramid of Khufu (about 2560);
  - Sumer is a land of rival city-states (Ur, Uruk, Lagash, Umma, Kish) in the Early Dynastic III period, two
    centuries before Sargon of Akkad; in Syria, Ebla and Mari are great city-states; Elam is ruled from Awan;
  - the Indus Valley civilisation is in its mature phase (about 2600-1900), with Harappa and Mohenjo-daro;
  - Crete is Early Minoan, before the first palaces;
  - on the steppe the Yamnaya horizon has given way to the Catacomb culture; in central and eastern Europe the
    Corded Ware culture has replaced the Baden and Cucuteni-Trypillia cultures; the Maykop culture of the north
    Caucasus has ended;
  - in China the Longshan cultures have followed Yangshao and Dawenkou; Shijiahe follows Qujialing on the middle
    Yangtze, Baodun is on the Chengdu plain, and the Xiaoheyan culture follows Hongshan in the north-east;
  - the steppe east of the Urals is home to herders after the Botai culture.
Norte Chico (Caral), Valdivia and the other peoples are as on the 3000 map. Everything else, including the faith,
culture and development layers, is the 3000 BCE map's. Dates this early are uncertain, often by a century.
Run from data-source/scripts/derive-2026/."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import era_tools as T

D = T.Derive(sys.argv[1], 'bc3000')
G = lambda name: next(i for i, r in enumerate(D.meta['realms']) if r['n'] == name)

r_egy = D.realm('Egypt (Old Kingdom)', g=G('Egypt'))
r_syr = D.realm('Syrian city-states (Ebla, Mari)', g=G('city-states'))
r_ind = D.realm('Indus Valley Civilisation', g=G('Indus Valley Civilisation (late Harappan)'))
r_cat = D.realm('Catacomb culture', g=G('Catacomb culture'))
r_cw = D.realm('Corded Ware culture', colour='#8f8a6e', kind=1)
r_nc = D.realm('North Caucasian culture', colour='#94886a', kind=1)
r_lsh = D.realm('Longshan culture', g=G('Longshan culture'))
r_sjh = D.realm('Shijiahe culture', g=G('Shijiahe culture'))
r_bd = D.realm('Baodun culture', g=G('Baodun culture'))
r_xhy = D.realm('Xiaoheyan culture', colour='#8e8a72', kind=1)
r_sh = D.realm('Steppe herders', g=G('Steppe herders'))
r_min = D.realm('Early Minoan Crete', colour='#4f8fa8', kind=1)

D.rename('Egypt', 'Egypt (Old Kingdom)', realm=r_egy)
D.rename('city-states', 'Syrian city-states (Ebla, Mari)', realm=r_syr)
D.rename('Early Harappan culture', 'Indus Valley Civilisation', realm=r_ind)
D.js['ents'][D.ent('Indus Valley Civilisation') - 1]['k'] = 0
D.rename('Yamnaya culture', 'Catacomb culture', realm=r_cat)
D.rename('Cucuteni–Trypillia culture', 'Corded Ware culture (east)', realm=r_cw)
D.rename('Baden culture', 'Corded Ware culture', realm=r_cw)
D.rename('Maykop culture', 'North Caucasian culture', realm=r_nc)
D.rename('Late Yangshao culture', 'Longshan culture', realm=r_lsh)
D.rename('Dawenkou culture', 'Shandong Longshan culture', realm=r_lsh)
D.rename('Qujialing culture', 'Shijiahe culture', realm=r_sjh)
D.rename('Upper Yangtze Neolithic', 'Baodun culture', realm=r_bd)
D.rename('Hongshan culture', 'Xiaoheyan culture', realm=r_xhy)
D.rename('Botai and steppe herders', 'Steppe herders', realm=r_sh)
D.rename('Minoan', 'Early Minoan Crete', realm=r_min)

notes = ['Built from the 3000 BCE map, adjusted to 2500.',
         'The age of the pyramids: Egypt was in the Old Kingdom, after the Great Pyramid of Khufu (about 2560). Sumer was a land of rival city-states, two centuries before Sargon of Akkad; Ebla and Mari were great cities in Syria.',
         'The Indus Valley civilisation was in its mature phase (about 2600–1900), the age of Harappa and Mohenjo-daro.',
         'In Europe the Corded Ware culture had replaced the Baden and Cucuteni–Trypillia cultures, and on the steppe the Catacomb culture followed the Yamnaya. In China the Longshan cultures followed Yangshao and Dawenkou.',
         'Dates this early are uncertain, often by a century.']
out, ix = D.save(-2500, 'bc2500', 'The age of the pyramids', notes, -3000)
print('2500 BCE written:', f"{ix['n']} states, {ix['m']} peoples, {len(out['borders'])} border lines")
