"""Realm QC pass 4 (28 Oct 2026): Africa and the Americas before 1500 (with the modern labels on the 1450-1750 maps
of North America), and three loose ends in Central Asia and Ukraine. Usage: python3 fix_qc4.py <site folder> [one year]

FIX-186 Africa, deep time: Homo sapiens, not Homo heidelbergensis, in Africa at 123,000 BCE; the Iberomaurusian and
        Capsian cultures, not "Berber tribes", in the Maghreb (10000-5000 BCE); Saharan hunter-gatherers before
        cattle herding (10000-8000 BCE); central African forest foragers, not "Bantu", before the Bantu expansion
        (8000-4000 BCE); Madagascar unpeopled before about 500 CE, Sardinia Nuragic (1500-1250 BCE), "Hunters-gatherers"
        respelled.
FIX-187 Egypt, Nubia and the Aegean before the states: Faiyum and early Nile farmers (5000 BCE, was "Naquada I"),
        the Naqada culture (4000 BCE, was "Egypt"), the A-Group culture (4000-3000 BCE, was "Kerma"), Neolithic Crete
        (4000 BCE, was "Minoan"), and Alashiya on Cyprus (1500-1250 BCE, was "Middle Helladic Greeks").
FIX-188 North Africa: Numidia under Masinissa (200 BCE, was the kingdoms of Syphax and Gala); the Byzantine Exarchate
        of Africa (600, was the Vandals); the Aures kingdom and the Masmuda Berbers outside the Umayyad realm (700,
        was Barghawata, which formed in 744); the Marinid Sultanate (1450, 1453; the Wattasids took the throne in
        1472); "Touareg" respelled Tuareg.
FIX-189 The Nile and the Horn: Makuria (was "Makkura"); Alwa, not the Funj (1450-1492; Sennar was founded about
        1504); Cushitic peoples, not "Kushites", in the Horn (700); the Sultanate of Ifat (1300, 1400; it absorbed
        Shewa about 1285); south of 13.5 N the "Beja" territory is the Nilotic and Gumuz peoples (900-1500); east of
        25 E the "Tubu and Saharan nomads" are the Beja and Arab nomads (1279-1500); the Mbundu chiefdoms before Ndongo
        (1450-1492).
FIX-190 The Caribbean: the islands were unpeopled before about 5000 BCE (the Bahamas before about 700 CE); Archaic
        peoples (4000 BCE-1 BCE), the Saladoid peoples (100-600) and the Taíno (700-1200) before "Taíno and Kalinago";
        Archaic peoples of Cuba (was "Ciboney"); the Lucayans (was "Turks and Caicos Islands").
FIX-191 Peoples of colonial origin shown before 1500: Matawai (Kalina and Trio peoples), Garífuna (Pech), Kriol (Rama),
        Miskito (Mayangna), "Cayenne" (Kalina and Palikur), "Essequibo" (Lokono).
FIX-192 Mesoamerica: Mixtec and Zapotec kingdoms (were "empires"); Cuicuilco before Teotihuacan (323-200 BCE);
        the Aztatlán chiefdoms and Cora and Totorame peoples (were "Nayarit"); "maïze" respelled.
FIX-193 The Andes and Amazonia: the Chinchorro culture (1500 BCE) and Alto Ramírez culture (1250-500 BCE), were
        "Chinchoros"; Andean Archaic peoples before Norte Chico (5000-4000 BCE); the Las Vegas culture before Valdivia
        (5000 BCE); the El Paraíso and Manchay cultures; Chavín; Amazonian and Ecuadorian peoples for the Kichwa groups,
        who formed after the Inca and colonial periods; the Awá (Guajá); Sateré-Mawé; Guenoa-Minuanes.
FIX-194 Hawaii was settled about 1000 CE: no Polynesians before then; Hawaiian chiefdoms, not the Hawaiian Kingdom
        (1795), on the 1450-1492 maps.
FIX-195 North American archaeological cultures: Fort Ancient for Adena and Hopewell on the 1450-1500 maps; Hopewell for
        Adena (300, 400); the Poverty Point culture (1500 BCE) then Fourche Maline (to 500 CE); Fourche Maline for "Mill
        Creek" in East Texas; Dorset for Thule before 1100; Ancestral Puebloans for "Anasazi"; late Mogollon and Hohokam
        renamed; the Mississippian and Fort Ancient cultures (1000-1453) in the Mississippi and Ohio valleys, cut from
        "Eastern North American hunter-gatherers" along approximate boxes; Plains, Plateau and Beothuk respelled.
FIX-196 Norse Greenland: its own realm before 1261, Norway's to 1397, the Kalmar Union's in 1400.
FIX-197 Reservation, treaty, removal-era (Oklahoma) and Métis labels on the 1450-1750 maps: renamed for the people who
        lived there, or, where only a few map pixels, joined to the territory around them.
FIX-198 Plains and south-eastern peoples shown where they arrived only later: Lakota bands and the Cheyenne (Plains
        bison hunters), the Comanche and Kiowa (Querechos, the Plains Apache), the Westo, Yamasee and Seminole
        (Savannah River chiefdoms, Guale); "Tlinoit" and "Coqs" renamed for the peoples of their land.
FIX-199 Central Asia and Ukraine: the Tarim Basin peoples and city-states (Tocharian and Saka), not "Proto-Tibetan
        cultures" (1500 BCE-300 CE); the "Steppe nomads (Xianbei, Kangju, Wusun)" territory split into the Xianbei,
        Kangju, the Tarim city-states, the Kidarites and the Xianbei, Kumo Xi and Khitan tribes, with stray pieces
        joined to their neighbours (1 BCE-500 CE); the Chernoles culture (to about 700 BCE) followed by Scythian-era
        forest-steppe farmers and the Bastarnae.

Mostly names. The splits use approximate boxes and lines, stated above. Borders, areas and labels are re-traced with
../derive-2026/era_tools.py. Afterwards: python3 scripts/build_realm_index.py and scripts/build_content_pages.py."""
import collections, json, os, sys
import numpy as np
from scipy import ndimage
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'derive-2026'))
import era_tools as T

SITE = sys.argv[1]
J = lambda p: json.load(open(p, encoding='utf-8'))
ORDER = ['n', 'r', 'k', 'p', 'a', 'b', 'l', 'w', 'a3', 'x', 'c']
EMETA = J(f'{SITE}/data/eras.json')
F = {e['y']: e['f'] for e in EMETA['eras']}
G = EMETA['realms']
SEEN = {}
for f in F.values():
    for r in J(f'{SITE}/eras/{f}.json')['realms']:
        SEEN.setdefault(r['n'], r['g'])
LAT = T.LATR[:, None] * np.ones((1, T.EW))
LON = ((np.arange(T.EW) + 0.5) / T.EW * 360 - 180)[None, :] * np.ones((T.EH, 1))
ALL = np.ones((T.EH, T.EW), bool)


def gid(name, like=None):
    for i, g in enumerate(G):
        if g['n'] == name: return i
    if name in SEEN: return SEEN[name]
    c = G[like]['c'] if like is not None else '#948a70'
    G.append({'k': name.lower(), 'c': c, 't': 1, 'n': name}); SEEN[name] = len(G) - 1; return SEEN[name]


def realm_of(js, name, like=None):
    for i, r in enumerate(js['realms']):
        if r['n'] == name: return i
    js['realms'].append({'g': gid(name, like), 'n': name}); return len(js['realms']) - 1


# ---- operations. Each: (fix, kind, years, name, ...). Years are inclusive [y0, y1].
OPS = []
def R(fix, old, new, y0, y1, realm=None, k=None):          # rename territories called `old` (and a realm of that name)
    OPS.append((fix, 'rename', y0, y1, old, dict(new=new, realm=realm, k=k)))
def S(fix, old, new, y0, y1, mask, realm=None, k=None):     # split the part inside `mask` off as `new`
    OPS.append((fix, 'split', y0, y1, old, dict(new=new, mask=mask, realm=realm, k=k)))
def A(fix, old, y0, y1, mask=None):                         # join each piece (inside `mask`) to the neighbour it borders most
    OPS.append((fix, 'absorb', y0, y1, old, dict(mask=mask)))
def C(fix, old, y0, y1, mask=None):                         # unpeopled: no territory
    OPS.append((fix, 'clear', y0, y1, old, dict(mask=mask)))

# FIX-186
R('FIX-186', 'Homo heidelbergensis', 'Homo sapiens (early modern humans)', -123000, -123000)
R('FIX-186', 'Berber tribes', 'Iberomaurusian culture', -10000, -10000)
R('FIX-186', 'Berber tribes', 'Capsian culture', -8000, -5000)
R('FIX-186', 'Saharan pastoral nomads', 'Saharan hunter-gatherers', -10000, -8000)
R('FIX-186', 'Bantu', 'Central African forest foragers', -8000, -4000)
C('FIX-186', 'Hunters-gatherers', -10000, -2500, LAT < -10)                        # Madagascar
R('FIX-186', 'Hunters-gatherers', 'Nuragic civilization', -1500, -1250)
R('FIX-186', 'Hunters-gatherers', 'Hunter-gatherers', -123000, 2026)
# FIX-187
R('FIX-187', 'Naquada I', 'Faiyum and early Nile farmers', -5000, -5000)
R('FIX-187', 'Egypt', 'Naqada culture', -4000, -4000, k=1)
R('FIX-187', 'Kerma', 'A-Group culture', -4000, -3000)
R('FIX-187', 'Minoan', 'Neolithic Crete', -4000, -4000)
R('FIX-187', 'Middle Helladic Greeks', 'Alashiya (Cyprus)', -1500, -1250, k=0)
# FIX-188
R('FIX-188', 'Kingdom of Syphax', 'Numidia', -200, -200)
R('FIX-188', 'Kingdom of Gala', 'Numidia', -200, -200)
R('FIX-188', 'Vandals', 'Exarchate of Africa', 600, 600, realm='Eastern Roman Empire', k=0)
R('FIX-188', 'Aures', 'Kingdom of the Aurès', 700, 700, realm='Kingdom of the Aurès')
R('FIX-188', 'Barghawata', 'Masmuda Berbers', 700, 700, realm='Masmuda Berbers', k=1)
R('FIX-188', 'Wattasid Sultanate', 'Marinid Sultanate', 1450, 1453)
R('FIX-188', 'Touareg', 'Tuareg', -123000, 2026)
# FIX-189
R('FIX-189', 'Makkura', 'Makuria', -123000, 2026)
R('FIX-189', 'Funj', 'Alwa', 1450, 1492)
R('FIX-189', 'Kushites', 'Cushitic peoples', 700, 700)
R('FIX-189', 'Shoa', 'Sultanate of Ifat', 1300, 1400)
S('FIX-189', 'Beja people', 'Nilotic and Gumuz peoples', 900, 1500, LAT < 13.5)
S('FIX-189', 'Tubu and Saharan nomads', 'Beja and Arab nomads', 1279, 1500, LON >= 25)
R('FIX-189', 'Ndongo', 'Mbundu chiefdoms', 1450, 1492)
# FIX-190
TAINO = 'Taíno and Kalinago peoples'
C('FIX-190', TAINO, -10000, -5000, LAT > 12)
C('FIX-190', TAINO, -4000, 600, LAT > 23.3)                                        # the Bahamas
R('FIX-190', TAINO, 'Archaic Caribbean peoples', -10000, -1)
R('FIX-190', TAINO, 'Saladoid peoples', 100, 600)
R('FIX-190', TAINO, 'Taíno', 700, 1210)
R('FIX-190', 'Ciboney', 'Archaic peoples of Cuba', -123000, 2026)
R('FIX-190', 'Turks and Caicos Islands', 'Lucayans', 1492, 1500)
# FIX-191
for old, new in (('Matawai', 'Kalina and Trio peoples'), ('Garífuna', 'Pech'), ('Kriol', 'Rama'), ('Miskito', 'Mayangna (Sumu)'),
                 ('Cayenne', 'Kalina and Palikur peoples'), ('Essequibo', 'Lokono (Arawak)')):
    R('FIX-191', old, new, -123000, 1500)
# FIX-192
R('FIX-192', 'Mixtec Empire', 'Mixtec kingdoms', -123000, 1500)
R('FIX-192', 'Zapotec Empire', 'Zapotec kingdoms', -123000, 1500)
R('FIX-192', 'Teotihuacan', 'Cuicuilco', -323, -200)
R('FIX-192', 'Nayarit', 'Aztatlán chiefdoms', 1279, 1400)
R('FIX-192', 'Nayarit', 'Cora and Totorame peoples', 1450, 1500)
R('FIX-192', 'Mesoamerican hunter-gatherers and maïze farmers', 'Hunter-gatherers and maize farmers', -123000, 2026)
# FIX-193
R('FIX-193', 'Chinchoros', 'Chinchorro culture', -1500, -1500)
R('FIX-193', 'Chinchoros', 'Alto Ramírez culture', -1250, -500)
R('FIX-193', 'Norte Chico', 'Andean Archaic peoples', -5000, -4000)
R('FIX-193', 'Valdivia', 'Las Vegas culture', -5000, -5000)
R('FIX-193', 'El Paraiso', 'El Paraíso culture', -1500, -1500)
R('FIX-193', 'El Paraiso', 'Manchay culture', -1250, -500)
R('FIX-193', 'Chavin', 'Chavín', -123000, 2026)
R('FIX-193', 'Kichwa (Amazónico)', 'Quijos', -123000, 1500)
for old in ('Kichwa del Río Napo', 'Kichwa del Río Pastaza', 'Kichwa del Río Tigre'):
    R('FIX-193', old, 'Záparo peoples', -123000, 1500)
R('FIX-193', 'Kichwa Lamista', 'Lamas (Motilones)', -123000, 1500)
A('FIX-193', 'Kichwa Santarrosino', -123000, 1500)
A('FIX-193', 'Kichwa', -123000, 1453)
R('FIX-193', 'Awá', 'Awá (Guajá)', -123000, 2026, realm='Awá (Guajá)')
R('FIX-193', 'Sataré-Mawé', 'Sateré-Mawé', -123000, 2026)
R('FIX-193', 'Guenoa-Muinanes', 'Guenoa-Minuanes', -123000, 2026)
# FIX-194
C('FIX-194', 'Polynesians (Hawaii)', -123000, 900)
R('FIX-194', 'Kō Hawaiʻi Paeʻāina (Hawaiian Kingdom)', 'Hawaiian chiefdoms', 1450, 1492)
# FIX-195
R('FIX-195', 'Adena', 'Fort Ancient culture', 1450, 1500)
R('FIX-195', 'Hopewell', 'Fort Ancient culture', 1450, 1500)
R('FIX-195', 'Adena Culture', 'Hopewell Culture', 300, 400)
R('FIX-195', 'Poverty point culture', 'Poverty Point culture', -1500, -1000)
R('FIX-195', 'Poverty point culture', 'Fourche Maline culture', -700, 500)
R('FIX-195', 'Mill Creek Culture', 'Fourche Maline culture', -123000, 500)
R('FIX-195', 'Thule', 'Dorset culture', -123000, 1100)
R('FIX-195', 'Anasazi', 'Ancestral Puebloans', -123000, 1400)
R('FIX-195', 'Anasazi', 'Pueblos', 1450, 1500)
R('FIX-195', 'Mogollon', 'Chihuahuan desert peoples (Concho, Suma)', 1450, 1500)
R('FIX-195', 'Hohokam', "Akimel O'odham", 1450, 1500)
EAST = 'Eastern North American hunter-gatherers'
S('FIX-195', EAST, 'Fort Ancient culture', 1000, 1453, (LAT >= 37.5) & (LAT <= 41) & (LON >= -86) & (LON <= -80.5))
S('FIX-195', EAST, 'Mississippian culture', 1000, 1453, (LAT >= 30) & (LAT <= 39.5) & (LON >= -95) & (LON <= -81.5))
R('FIX-195', 'Plain bison hunters', 'Plains bison hunters', -123000, 2026)
R('FIX-195', 'Plateau fichers and hunter gatherers', 'Plateau fishers and hunter-gatherers', -123000, 2026)
R('FIX-195', 'Boethuk', 'Beothuk', -123000, 2026)
# FIX-196
R('FIX-196', 'Norse Greenland', 'Norse Greenland', 985, 1260, realm='Norse Greenland')
R('FIX-196', 'Norse Greenland', 'Norse Greenland', 1261, 1396, realm='Kingdom of Norway')
# FIX-197
MODERN = {
    'Carcross/Tagish First Nation (BC)': 'Tagish and Inland Tlingit', 'Carcross/Tagish First Nation (Yukon)': 'Tagish and Inland Tlingit',
    'Teslin Tlingit Council (BC)': 'Inland Tlingit', 'Teslin Tlingit Council (Yukon)': 'Inland Tlingit',
    'Confederated Tribes of Warm Springs': 'Sahaptin peoples (Tenino, Wasco)', "Gwitch'in Settlement Region": "Gwich'in",
    "Hul'qumi'num Treaty Group": "Hul'qumi'num peoples", 'Kelly Lake Metis Settlement Society': 'Dane-zaa (Beaver)',
    'Michif Piyii (Métis)': 'Cree', 'NWT Métis Nation': 'Denesuline (Chipewyan)', 'NunatuKavut': 'Innu and Labrador Inuit',
    'Mississaugas of the Credit First Nation': 'Neutral Nation (Attawandaron)', 'Salish & Kootenai Tribes': 'Ktunaxa (Kootenai)',
    'Salish Kootenai (Flathead)': 'Bitterroot Salish (Flathead)',
}
for old, new in MODERN.items():
    R('FIX-197', old, new, 1450, 1800)
OKLA_BIG = ['Cherokee (Oklahoma)', 'Cheyenne-Arapaho (Oklahoma)', 'Chickasaw (Oklahoma)', 'Choctaw (Oklahoma)',
            'Kiowa-Comanche-Apache (Oklahoma)', 'Muscogee (Oklahoma)', 'Osage (Oklahoma)']
for old in OKLA_BIG:
    R('FIX-197', old, 'Wichita and Caddoan peoples', 1450, 1800)
ABSORB = ['Confederated Tribes of Grand Ronde', 'Confederated Tribes of Siletz Indians', 'Confederated Villages of Lisjan',
          'Graton Rancheria', 'Hoopa (Reservation)', 'Resighini Rancheria (Yurok)', 'Mountain Métis', 'Sahtu Dene and Metis',
          'Mount Tabor Indian Community', 'Pascua Yaqui', 'San Carlos Apache', 'White Mountain Apache', 'Seminole', 'Miccosukee',
          'Seminole Tribe of Florida (Big Cypress Reservation)', 'Seminole Tribe of Florida (Brighton Reservation)',
          'Seminole Tribe of Florida (Hollywood Reservation)', 'Seminole Tribe of Florida (Immokalee Reservation)',
          'Seminole Tribe of Florida (Tampa Reservation)', 'Tigua', 'Wabanaki (Dawnland Confederacy)', 'Bella']
OKLA_SMALL = ['Eastern Shawnee (Oklahoma)', 'Iowa (Oklahoma)', 'Kaw (Oklahoma)', 'Kickapoo (Oklahoma)', 'Miami (Oklahoma)',
              'Modoc (Oklahoma)', 'Otoe-Missouri (Oklahoma)', 'Ottawa (Oklahoma)', 'Pawnee (Oklahoma)', 'Peoria (Oklahoma)',
              'Ponca (Oklahoma)', 'Potawatomi-Shawnee (Oklahoma)', 'Sac and Fox (Oklahoma)', 'Seminole (Oklahoma)',
              'Seneca-Cayuga (Oklahoma)', 'Tonkawa (Oklahoma)', 'Wichita-Caddo-Delaware (Oklahoma)', 'Wyandotte (Oklahoma)']
for old in ABSORB + OKLA_SMALL:
    A('FIX-198' if old in ('Seminole', 'Miccosukee', 'Tigua', 'Wabanaki (Dawnland Confederacy)', 'Bella') else 'FIX-197', old, 1450, 1800)
# FIX-198
for old in ('Hunkpapa', 'Itazipco', 'Mnicoujou', 'Oglala', 'Oohenumpa', 'Sicangu', 'Sihapsa', 'Cheyenne'):
    R('FIX-198', old, 'Plains bison hunters', 1450, 1500)
for old in ('Nʉmʉnʉʉ (Comanche)', 'Comanche', 'Gáuigú (Kiowa)'):
    R('FIX-198', old, 'Querechos (Plains Apache)', 1450, 1500)
R('FIX-198', 'Westo', 'Savannah River chiefdoms', 1450, 1500)
R('FIX-198', 'Yamassee', 'Guale', 1450, 1500)
R('FIX-198', 'Tlinoit', 'Northern Athabaskan peoples', 1450, 1500)
R('FIX-198', 'Coqs', 'Kalapuya and Molalla peoples', 1450, 1500)
# FIX-199
TARIM = (LON >= 73.5) & (LON <= 92) & (((LON < 85) & (LAT >= 36.8)) | ((LON >= 85) & (LAT >= 37.8))) & (LAT <= 44)
S('FIX-199', 'Proto-Tibetan cultures', 'Tarim Basin peoples (Tocharian and Saka)', -1500, -250, TARIM)
S('FIX-199', 'Proto-Tibetan cultures', 'Tarim Basin city-states', -100, 300, TARIM)
SN = 'Steppe nomads (Xianbei, Kangju, Wusun)'
S('FIX-199', SN, 'Xianbei', 100, 300, (LAT >= 44) & (LON >= 80) & (LON <= 100))
S('FIX-199', SN, 'Kangju and Sogdian city-states', 200, 300, (LON >= 55.5) & (LON < 74) & (LAT >= 35) & (LAT <= 42.5) & (LON >= 58))
S('FIX-199', SN, 'Tarim Basin city-states', 400, 500, TARIM)
S('FIX-199', SN, 'Xianbei, Kumo Xi and Khitan tribes', 400, 500, LON > 96)
S('FIX-199', SN, 'Kidarite Kingdom', 400, 400, LON < 73.5)
A('FIX-199', SN, -1, 500)
R('FIX-199', 'Chernoles culture', 'Scythian-era forest-steppe farmers', -550, -250)
R('FIX-199', 'Chernoles culture', 'Bastarnae', -200, -1)

NOTE = {
    'FIX-186': 'Peoples of the deep past are named for their time: early modern humans, the Iberomaurusian and Capsian cultures, foragers before farming and herding spread.',
    'FIX-187': 'Before the first states: the Faiyum and Naqada cultures in Egypt, the A-Group in Nubia, Neolithic Crete; Cyprus is Alashiya.',
    'FIX-188': 'North Africa is named for its rulers of the time.',
    'FIX-189': 'The Nile and the Horn of Africa are named for their peoples and states of the time.',
    'FIX-190': 'The Caribbean islands were settled from about 5000 BCE (the Bahamas from about 700 CE): Archaic peoples, then the Saladoid peoples and the Taíno.',
    'FIX-191': 'Peoples who formed in the colonial era are replaced by the peoples who lived there before 1500.',
    'FIX-192': 'Mesoamerica is named for its peoples and states of the time.',
    'FIX-193': 'Andean and Amazonian peoples are named for their time.',
    'FIX-194': 'Hawaii was settled about 1000 CE; before the Hawaiian Kingdom (1795) the islands were separate chiefdoms.',
    'FIX-195': 'North American cultures are named for their time; the Mississippi and Ohio valleys were the land of the Mississippian and Fort Ancient cultures (boxes approximate).',
    'FIX-196': 'Norse Greenland was self-governing until 1261, then Norway\'s.',
    'FIX-197': 'Modern reservation, treaty and removal-era labels are replaced by the peoples who lived there at the time.',
    'FIX-198': 'Peoples who reached this land only later are replaced by those who lived there at the time.',
    'FIX-199': 'Central Asia and the forest-steppe are named for their peoples of the time; the Tarim Basin was a land of oasis city-states (lines approximate).',
}
NEED_IDS = {'split', 'absorb', 'clear'}


def ents_named(js, name):
    return [i + 1 for i, e in enumerate(js['ents']) if e.get('a') and e['n'] == name]


def fix_era(y, LAND):
    key = F[y]; p = f'{SITE}/eras/{key}.json'; js = J(p)
    log = collections.Counter(); notes = []
    todo = [op for op in OPS if op[2] <= y <= op[3] and ents_named(js, op[4])]
    if not todo:
        return None
    ids = orig = None
    ov = J(f'{SITE}/data/ovmain.json'); rows = ov['eras'][key]
    if any(op[1] in NEED_IDS for op in todo):
        same, bad = T.check_roundtrip(js, LAND)
        assert same and all(x[1] == x[2] and x[3] == x[4] for x in bad), f'tracing does not reproduce the {key} map; stop'
        ids = T.read_ids(js); orig = ids.copy()
    for fix, kind, y0, y1, old, o in OPS:
        if not (y0 <= y <= y1): continue
        hit = ents_named(js, old)
        if not hit: continue
        if kind == 'rename':
            for i in hit:
                e = js['ents'][i - 1]; rn = js['realms'][e['r']]['n'] if e['r'] >= 0 else None
                like = js['realms'][e['r']]['g'] if e['r'] >= 0 else None
                target = o['realm'] or (o['new'] if rn == old or rn is None else None)
                if target: e['r'] = realm_of(js, target, like)
                for e2 in js['ents']:                      # the rest of a realm of that name follows it
                    if e2 is not e and e2['r'] >= 0 and rn == old and js['realms'][e2['r']]['n'] == old and target:
                        e2['r'] = e['r']
                e['n'] = o['new']; e['x'] = 1
                if o['k'] is not None: e['k'] = o['k']
                log[fix] += 1
        elif kind == 'split':
            m = np.isin(ids, hit) & o['mask']
            if not m.any(): continue
            src = js['ents'][hit[0] - 1]
            like = js['realms'][src['r']]['g'] if src['r'] >= 0 else None
            ex = [i for i in ents_named(js, o['new']) if i not in hit]
            if ex:
                ni = ex[0]
            else:
                js['ents'].append({'n': o['new'], 'r': realm_of(js, o['realm'] or o['new'], like), 'k': src['k'] if o['k'] is None else o['k'],
                                   'p': 1, 'a': 1, 'x': 1})
                ni = len(js['ents'])
                while len(rows) < ni: rows.append(list(rows[int(np.bincount(orig[m]).argmax()) - 1]))
            ids[m] = ni; log[fix + ' px'] += int(m.sum())
        elif kind == 'clear':
            m = np.isin(ids, hit) & (ALL if o['mask'] is None else o['mask'])
            ids[m] = 0; log[fix + ' cleared px'] += int(m.sum())
        elif kind == 'absorb':
            m = np.isin(ids, hit) & (ALL if o['mask'] is None else o['mask'])
            lab, n = ndimage.label(m)
            for c in range(1, n + 1):
                cm = lab == c
                ring = ndimage.binary_dilation(cm) & ~cm & (ids > 0) & ~np.isin(ids, hit)
                if ring.any():
                    ids[cm] = np.bincount(ids[ring]).argmax()
                else:
                    near = ndimage.binary_dilation(cm, iterations=12) & ~cm & (ids > 0) & ~np.isin(ids, hit)
                    if near.any(): ids[cm] = np.bincount(ids[near]).argmax()
                log[fix + ' joined'] += 1
        notes.append(NOTE[fix])
        if ids is not None:                                 # names later ops look up must reflect pixels now
            for i in hit:
                if not (ids == i).any(): js['ents'][i - 1]['a'] = 0
    if ids is not None:
        changed = ids != orig
        touched = set(np.unique(orig[changed]).tolist()) | set(np.unique(ids[changed]).tolist()); touched.discard(0)
        for i in touched:
            e = js['ents'][i - 1]; a, b, l = T.stats(ids, i)
            e['a'] = a
            for k, v in (('b', b), ('l', l)):
                if v is None: e.pop(k, None)
                else: e[k] = v
        js['borders'] = T.borders(ids, LAND)
        js['_png'] = T.write_ids(ids)
        assert (T.read_ids(js) == ids).all()
    open(f'{SITE}/data/ovmain.json', 'w', encoding='utf-8').write(json.dumps(ov, ensure_ascii=True, separators=(',', ':')))
    used = sorted({e['r'] for e in js['ents'] if e['r'] >= 0})
    remap = {r: k for k, r in enumerate(used)}
    js['realms'] = [js['realms'][r] for r in used]
    for e in js['ents']:
        if e['r'] >= 0: e['r'] = remap[e['r']]
    js['ents'] = [{k: e[k] for k in ORDER if k in e} for e in js['ents']]
    js['notes'] += [n for n in dict.fromkeys(notes) if n not in js['notes']]
    open(p, 'w', encoding='utf-8').write(json.dumps(js, ensure_ascii=False, separators=(',', ':')))
    return dict(log)


LAND = T.land_mask(f'{SITE}/eras', list(F.values()))
for y in sorted(y for y in F if len(sys.argv) < 3 or y == int(sys.argv[2])):
    if y > 1800: continue
    r = fix_era(y, LAND)
    if r: print(y, r, flush=True)
for ix in EMETA['eras']:
    js = J(f"{SITE}/eras/{ix['f']}.json")
    ix['c'] = len(js['notes'])
    ix['n'] = sum(1 for e in js['ents'] if e.get('a') and e['k'] == 0)
    ix['m'] = sum(1 for e in js['ents'] if e.get('a') and e['k'] == 1)
open(f'{SITE}/data/eras.json', 'w', encoding='utf-8').write(json.dumps(EMETA, ensure_ascii=True, separators=(',', ':')))
