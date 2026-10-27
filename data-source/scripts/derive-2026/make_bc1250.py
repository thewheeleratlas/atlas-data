"""Derive the 1250 BCE map, the height of the Late Bronze Age, from the 1500 BCE map.
Usage: python3 make_bc1250.py <site folder>     (writes <site>/eras/bc1250.json and updates <site>/data/*.json)

About 1250 BCE, in the reign of Ramesses II (about 1279-1213) and some 25 years after the battle of Kadesh (about 1274):
  - New Kingdom Egypt holds Nubia to beyond the Fourth Cataract (Kerma fell about 1500) and southern Canaan; the
    Egyptian-Hittite treaty of about 1259 left the line south of Kadesh, between Amurru (Hittite) and Upi (Egyptian);
  - the Hittite Empire holds central Anatolia, the former Arzawa lands in the west (taken by Mursili II about 1320) and
    northern Syria (Ugarit, Amurru, Carchemish);
  - Assyria under Shalmaneser I has annexed Hanigalbat, the last of Mitanni (by about 1260): the Middle Assyrian Empire;
  - Kassite Babylonia and Middle Elamite Elam continue;
  - Crete is Mycenaean (Knossos from about 1450);
  - in Europe the Urnfield cultures are spreading from the Danube (from about 1300), and the El Argar culture of
    south-east Spain has ended (about 1550).
Shang China (Anyang, the time of Wu Ding), the Vedic Aryans, the Andronovo culture and the Olmec are as on the 1500 map.
Everything else, including the faith, culture and development layers, is the 1500 BCE map's.
Dates in this period are uncertain, often by decades. Run from data-source/scripts/derive-2026/."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import era_tools as T

D = T.Derive(sys.argv[1], 'bc1500')
G = lambda name: next(i for i, r in enumerate(D.meta['realms']) if r['n'] == name)
box = D.lon_box

r_egy = D.realm('New Kingdom of Egypt')
r_hit = D.realm('Hittite Empire', g=G('Hittite Kingdom'))
r_ass = D.realm('Middle Assyrian Empire', g=G('Assyria'))
r_myc = D.realm('Mycenaean Greece')
r_urn = D.realm('Urnfield cultures', g=G('Urnfield cultures'))
r_ibe = D.realm('Iberian Bronze Age peoples', g=G('Iberian Bronze Age peoples (El Argar)'))

n = {}
# northern Syria to the Hittites (the treaty line lies south of Kadesh, about 34.3 N)
n['north syria'] = D.take('Northern Syria (Hittite vassals)', r_hit, box(34.0, 34.3, 42.0, 37.8), ['Canaanite city-states'])
D.rename('Canaanite city-states', 'Canaan (Egyptian)', realm=r_egy)
D.rename('Hittite Kingdom', 'Hittite Empire', realm=r_hit)
D.rename('Arzawa', 'Arzawa lands (Hittite)', realm=r_hit)
D.rename('Mitanni', 'Middle Assyrian Empire', realm=r_ass)
D.rename('Kerma (Kingdom of Kush)', 'Nubia (Egyptian Kush)', realm=r_egy)
D.rename('Minoan Crete', 'Crete (Mycenaean)', realm=r_myc)
D.rename('Tumulus culture', 'Urnfield cultures', realm=r_urn)
D.rename('Iberian Bronze Age peoples (El Argar)', 'Iberian Bronze Age peoples', realm=r_ibe)
# realms left without territory are dropped when the map is saved

notes = ['Built from the 1500 BCE map, adjusted to 1250.',
         'The reign of Ramesses II (about 1279–1213): Egypt held Nubia beyond the Fourth Cataract and southern Canaan; after the battle of Kadesh (about 1274) and the treaty of about 1259, the line with the Hittites ran south of Kadesh.',
         'The Hittite Empire held central Anatolia, the former Arzawa lands in the west and northern Syria; Assyria under Shalmaneser I had annexed Hanigalbat, the last of Mitanni.',
         'Crete was Mycenaean from about 1450. In Europe the Urnfield cultures were spreading from the Danube.',
         'Within about seventy years this world broke apart in the Late Bronze Age collapse. Dates this early are uncertain, often by decades.']
out, ix = D.save(-1250, 'bc1250', 'The Late Bronze Age: Ramesses II and the Hittites', notes, -1500)
print('1250 BCE written:', ', '.join(f'{k} {v:,} px' for k, v in n.items()), f"| {ix['n']} states, {ix['m']} peoples, {len(out['borders'])} border lines")
