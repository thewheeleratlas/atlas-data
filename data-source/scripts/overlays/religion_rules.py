"""Majority-faith rules for the Religion layer.

Each rule: (first year, last year, faith id, where).  Rules are applied in order for every era map whose year
falls in the range; a later rule overrides an earlier one.  `where` uses the same keys as era_edits.py:
a0 (countries), a1 / a1x (provinces), cont, box, poly (OR together), clip / clipoly (AND), cut (minus),
ent / realm (limit to named era entities / realms).  Only land claimed in that era's border map is painted.

The map shows the faith of the majority of the population (as in Crusader Kings' county faiths), not the ruler's.
Where no faith clearly dominated, the larger one is shown.  Before c. 1000 CE most of this is broad-brush.
"""
FAMILIES = [
    ['christian', 'Christianity'], ['islam', 'Islam'], ['jewish', 'Judaism'], ['indian', 'Indian religions'],
    ['eastasian', 'East Asian religions'], ['iranian', 'Iranian religions'], ['ancient', 'Ancient Near East & Mediterranean'],
    ['europagan', 'European paganism'], ['steppe', 'Steppe & Siberian'], ['americas', 'Religions of the Americas'],
    ['africa', 'African religions'], ['oceania', 'Oceania'], ['folk', 'Folk religion and nonreligion'], ['na', 'Unknown or uncertain'],
]
FAITHS = [
    dict(id='catholic', n='Catholic Christianity', fam='christian', c='#d6ac34', w='Catholic Church',
         d='Latin Christianity of the western Roman Church, led by the Pope. Before the Great Schism of 1054 this marks the Latin-speaking West.'),
    dict(id='orthodox', n='Eastern Orthodox Christianity', fam='christian', c='#8b3d8f', w='Eastern Orthodox Church',
         d='Greek-rite Christianity of Byzantium and its daughter churches (Bulgaria, Serbia, Rus, Georgia, Romania). Before 1054 this marks the Greek-speaking East.'),
    dict(id='protestant', n='Protestant Christianity', fam='christian', c='#3f6fb8', w='Protestantism',
         d='Churches of the Reformation (Lutheran, Reformed/Calvinist, Anglican and their offshoots), from 1517. Bohemia c. 1420–1620 is shown here for the Hussite (Utraquist) movement that anticipated it.'),
    dict(id='lds', n='Latter-day Saints (Mormon)', fam='christian', c='#5b8f9e', w='The Church of Jesus Christ of Latter-day Saints',
         d='The Restorationist church founded by Joseph Smith (1830); the Mormon exodus under Brigham Young settled the Great Basin from 1847, and Utah has had a Latter-day Saint majority ever since.'),
    dict(id='oriental', n='Oriental Orthodox Christianity', fam='christian', c='#c25a3c', w='Oriental Orthodox Churches',
         d='The churches that rejected the Council of Chalcedon (451): Coptic, Ethiopian, Armenian and Syriac Orthodox.'),
    dict(id='nestorian', n='Church of the East', fam='christian', c='#8e6c3a', w='Church of the East',
         d='The Syriac "Nestorian" church of the Persian Empire, which spread along the Silk Road to Central Asia, India and China.'),
    dict(id='sunni', n='Sunni Islam', fam='islam', c='#3e8b46', w='Sunni Islam',
         d='The majority branch of Islam, founded on the Quran and the Sunna of the Prophet Muhammad (d. 632).'),
    dict(id='shia', n='Shia Islam', fam='islam', c='#1e5e48', w='Shia Islam',
         d='The branch of Islam that follows the line of Ali and the Imams; includes Twelvers (Iran, Iraq, Azerbaijan, Lebanon), Zaydis (Yemen) and Alawites.'),
    dict(id='ibadi', n='Ibadi Islam', fam='islam', c='#86b35c', w='Ibadi Islam',
         d='The surviving branch of the early Kharijite movement, dominant in Oman and once in parts of the Maghreb.'),
    dict(id='judaism', n='Judaism', fam='jewish', c='#5fb3dd', w='Judaism',
         d='The religion of the Israelites and the Jewish people. Shown as a majority faith in ancient Israel and Judah, Himyar (c. 380–525) and modern Israel.'),
    dict(id='hindu', n='Hinduism', fam='indian', c='#e2762c', w='Hinduism',
         d='The family of Indian traditions grown from Vedic religion (Shaiva, Vaishnava, Shakta). In Southeast Asia before c. 1300 it also marks the Hindu-Buddhist court religions of Funan, Champa, Angkor and Java.'),
    dict(id='vedic', n='Vedic religion', fam='indian', c='#c99449', w='Historical Vedic religion',
         d='The religion of the Vedas brought by Indo-Aryan speakers to the Punjab and Ganges plain (c. 1500–500 BCE), ancestor of Hinduism.'),
    dict(id='harappan', n='Harappan religion', fam='indian', c='#a8714a', w='Indus Valley Civilisation',
         d='The little-understood religion of the Indus Valley cities (c. 3300–1800 BCE): ritual bathing, fertility figures and seals with animal and "proto-Shiva" motifs.'),
    dict(id='theravada', n='Theravada Buddhism', fam='indian', c='#efd57c', w='Theravada',
         d='The "Way of the Elders", the Pali-canon Buddhism of Sri Lanka, Burma, Thailand, Laos and Cambodia.'),
    dict(id='mahayana', n='Mahayana Buddhism', fam='indian', c='#e9b98a', w='Mahayana',
         d='The "Great Vehicle" Buddhism of Gandhara, Central Asia, Srivijaya, the Palas and Korea; in China and Vietnam it blended into the Chinese tradition.'),
    dict(id='vajrayana', n='Tibetan Buddhism', fam='indian', c='#b98ad2', w='Tibetan Buddhism',
         d='Vajrayana Buddhism of Tibet, Bhutan and Ladakh, adopted by the Mongols (1570s) and Kalmyks.'),
    dict(id='sikh', n='Sikhism', fam='indian', c='#2a95b8', w='Sikhism',
         d='Founded by Guru Nanak (1469–1539) in the Punjab; the majority faith of Indian Punjab since 1966.'),
    dict(id='east_asian', n='Chinese traditional religion', fam='eastasian', c='#bc3a33', w='Chinese folk religion',
         d='The Chinese blend of ancestor veneration, Confucianism, Taoism and Mahayana Buddhism, shared with Vietnam and (after 1392) Neo-Confucian Korea.'),
    dict(id='shinto', n='Shinto and Japanese Buddhism', fam='eastasian', c='#e2848b', w='Shinto',
         d='Worship of the kami, blended with Buddhism from the 6th century into the Japanese tradition.'),
    dict(id='zoroastrian', n='Zoroastrianism', fam='iranian', c='#d4664a', w='Zoroastrianism',
         d='The faith of the prophet Zarathustra and Ahura Mazda; state religion of the Achaemenid, Parthian and Sasanian empires.'),
    dict(id='manichaean', n='Manichaeism', fam='iranian', c='#7d6aa9', w='Manichaeism',
         d='The dualist faith of the prophet Mani (d. 274); state religion of the Uyghur Khaganate (763–840).'),
    dict(id='iranian', n='Early Indo-Iranian religion', fam='iranian', c='#b8885a', w='Proto-Indo-Iranian religion',
         d='The pre-Zoroastrian religion of the Iranian peoples, shared roots with the Vedic gods.'),
    dict(id='egyptian', n='Ancient Egyptian religion', fam='ancient', c='#cfb16a', w='Ancient Egyptian religion',
         d='The religion of Pharaonic Egypt and Kush: Ra, Osiris, Isis, Amun and the divine king. It faded under Christianity after c. 350 CE.'),
    dict(id='mesopotamian', n='Mesopotamian religion', fam='ancient', c='#a5805a', w='Ancient Mesopotamian religion',
         d='The temple religion of Sumer, Akkad, Babylon, Assyria and Elam: Anu, Enlil, Inanna/Ishtar, Marduk, Ashur.'),
    dict(id='canaanite', n='Canaanite and Punic religion', fam='ancient', c='#94704f', w='Ancient Canaanite religion',
         d='The religion of the Canaanites, Phoenicians, Aramaeans and Carthaginians: El, Baal, Astarte, Melqart, Tanit.'),
    dict(id='anatolian', n='Anatolian religion', fam='ancient', c='#a99070', w='Hittite mythology and religion',
         d='The Hittite, Luwian, Phrygian and Lydian religions of Asia Minor ("the thousand gods of Hatti", Cybele).'),
    dict(id='arabian', n='Arabian polytheism', fam='ancient', c='#c99e6c', w='Pre-Islamic Arabia',
         d='The gods of pre-Islamic Arabia (Hubal, al-Lat, al-Uzza, Manat) and the South Arabian kingdoms (Almaqah).'),
    dict(id='hellenic', n='Greek and Roman religion', fam='ancient', c='#6d9fc6', w='Religion in ancient Rome',
         d='The Olympian gods of Greece and Rome and the syncretic cults of the Hellenistic and Roman world, until Christianity replaced them (4th century CE).'),
    dict(id='old_european', n='Bronze Age European religion', fam='europagan', c='#8d8f78', w='Prehistoric religion',
         d='The little-known religions of Neolithic and Bronze Age Europe: megaliths, sun discs and sky gods.'),
    dict(id='celtic', n='Celtic religion', fam='europagan', c='#5d9a6b', w='Ancient Celtic religion',
         d='The druidic religion of the Gauls, Britons and Irish: Lugus, Taranis, Brigid and sacred groves.'),
    dict(id='iberian', n='Iberian and Celtiberian religion', fam='europagan', c='#82995a', w='Iberians',
         d='The pre-Roman religions of the Iberian peninsula.'),
    dict(id='germanic', n='Germanic and Norse paganism', fam='europagan', c='#6c80a8', w='Germanic paganism',
         d='The religion of the Germanic peoples and the Vikings: Odin/Woden, Thor, Freyr and the sacred groves of Uppsala.'),
    dict(id='slavic', n='Slavic paganism', fam='europagan', c='#93a75c', w='Slavic paganism',
         d='The religion of the early Slavs: Perun, Veles, Svarog and Mokosh.'),
    dict(id='baltic', n='Baltic paganism', fam='europagan', c='#6f9d8d', w='Baltic religion',
         d='The religion of the Prussians, Latvians and Lithuanians (Perkūnas, Dievas). Lithuania was the last pagan state in Europe (to 1387).'),
    dict(id='thracian', n='Thracian and Dacian religion', fam='europagan', c='#9c7ea3', w='Thracian religion',
         d='The religion of the Thracians and Dacians: the horseman hero, Zalmoxis and Orphic cults.'),
    dict(id='tengri', n='Tengrism and steppe religion', fam='steppe', c='#4fb1a9', w='Tengrism',
         d='The sky-god and ancestor religion of the steppe nomads (Scythians, Xiongnu, Turks, Mongols), with shamans and sacred mountains.'),
    dict(id='shamanism', n='Siberian and Uralic shamanism', fam='steppe', c='#8d9cab', w='Siberian shamanism',
         d='The shamanic religions of the forest and tundra peoples of northern Eurasia (Finno-Ugric, Samoyed, Tungusic, Paleo-Siberian).'),
    dict(id='bon', n='Bon and Tibetan folk religion', fam='steppe', c='#a27db3', w='Bon',
         d='The religion of Tibet and Zhangzhung before Buddhism.'),
    dict(id='mesoamerican', n='Mesoamerican religion', fam='americas', c='#c46a3a', w='Mesoamerican religion',
         d='The religion of the Olmec, Maya, Zapotec, Toltec and Aztec: the calendar, sacred ball game, pyramids and gods such as Quetzalcoatl and Tlaloc.'),
    dict(id='andean', n='Andean religion', fam='americas', c='#a06c90', w='Inca mythology',
         d='The religion of the Andes from Chavin to the Inca: Viracocha, Inti the sun, Pachamama and the huacas.'),
    dict(id='native_na', n='Native North American religions', fam='americas', c='#91815f', w='Native American religions',
         d='The many religions of the peoples of North America, from the Mississippian mound-builders to the Plains and Arctic.'),
    dict(id='south_am', n='Native South American religions', fam='americas', c='#6f9150', w='Indigenous peoples of South America',
         d='The religions of the Amazon, Orinoco, Chaco and Patagonia peoples, centred on shamans and forest spirits.'),
    dict(id='african', n='African traditional religions', fam='africa', c='#a5744a', w='Traditional African religions',
         d='The many religions of sub-Saharan Africa: a creator god, ancestors, nature spirits and divination (Yoruba, Akan, Kongo, Zulu and others).'),
    dict(id='berber', n='Berber religion', fam='africa', c='#b78e5a', w='Traditional Berber religion',
         d='The pre-Christian, pre-Islamic religion of the Berbers of North Africa and the Sahara.'),
    dict(id='aboriginal', n='Aboriginal Australian religion', fam='oceania', c='#b0653f', w='Australian Aboriginal religion and mythology',
         d='The Dreaming: ancestral beings, songlines and the sacred land of Aboriginal Australia.'),
    dict(id='oceanian', n='Austronesian and Oceanian religions', fam='oceania', c='#4e9c8e', w='Polynesian mythology',
         d='The religions of Polynesia, Melanesia, Taiwan and island Southeast Asia: ancestors, mana and tapu.'),
    dict(id='animism', n='Animism and folk religion', fam='folk', c='#9a9484', w='Animism',
         d='Local religions built around nature spirits and ancestors, shown wherever no organised faith dominated (including all of prehistory).'),
    dict(id='none', n='Nonreligious majority', fam='folk', c='#b9b3a6', w='Irreligion',
         d='Places where most people now report no religion: the Czech Republic, Estonia and eastern Germany after decades of secularisation and communist rule.'),
    dict(id='na', n='n/a (unknown or uncertain)', fam='na', c='#6f6c66',
         d="No category is shown here: the population is unknown, too mixed or too disputed to name one group, or the land was uninhabited. Every n/a area is listed in the atlas's n/a register."),
]

RULES = []
def R(y0, y1, faith, **where): RULES.append((y0, y1, faith, where))
E = 99999          # open-ended
B = -999999        # from the beginning

# ------------------------------------------------------------------ helpers
ARABIA = ['SAU', 'YEM', 'OMN', 'ARE', 'QAT', 'KWT', 'BHR']
MAGHREB = ['MAR', 'DZA', 'TUN', 'LBY', 'SAH', 'MRT']
ANDES = [[-81.3, -2.5], [-79.5, 1.6], [-77.3, 1.4], [-77.2, -2.3], [-76.4, -6], [-75.4, -9.5], [-73.2, -12.2], [-70.4, -13.4], [-68.3, -15],
         [-67.2, -16.8], [-66.2, -19.3], [-64.8, -22.6], [-65.4, -28.5], [-68.8, -31], [-71.6, -31], [-71.3, -27], [-70.3, -18.3], [-76.2, -13.6],
         [-79.6, -8], [-81.4, -5]]
N_IND = ['Punjab', 'Haryana', 'Delhi', 'Chandigarh', 'Himachal Pradesh', 'Uttarakhand', 'Uttar Pradesh']
STEPPE_RUS = ['Kalmyk', "Astrakhan'", 'Volgograd', 'Rostov', 'Orenburg', 'Saratov', 'Krasnodar', "Stavropol'", 'Crimea', 'Sevastopol']
STEPPE_UKR = ['Kherson', 'Zaporizhzhya', 'Mykolayiv', 'Odessa', "Dnipropetrovs'k", "Donets'k", "Luhans'k"]
RUS_W = ['Smolensk', 'Bryansk', 'Pskov', 'Novgorod', 'Leningrad', 'City of St. Petersburg']
RUS_C = ['Moskva', 'Moskovskaya', 'Vladimir', 'Ivanovo', 'Kostroma', "Yaroslavl'", "Tver'", 'Kaluga', 'Tula', "Ryazan'", 'Orel', 'Kursk',
         'Nizhegorod', 'Lipetsk', 'Vologda']
RUS_N = ["Arkhangel'sk", 'Karelia', 'Komi', 'Murmansk', 'Nenets', 'Kirov', "Perm'"]
RUS_VOLGA = ['Mordovia', 'Chuvash', 'Mariy-El', 'Udmurt', 'Penza', "Ul'yanovsk", 'Samara', 'Tambov', 'Voronezh', 'Belgorod']
RUS_URAL = ['Sverdlovsk', 'Chelyabinsk', 'Kurgan', "Tyumen'"]
RUS_SSIB = ['Omsk', 'Novosibirsk', 'Tomsk', 'Kemerovo', 'Altay', 'Khakass']
RUS_FE = ['Amur', "Primor'ye", 'Khabarovsk', 'Yevrey', 'Sakhalin']
MEX_N = ['Baja California', 'Baja California Sur', 'Sonora', 'Chihuahua', 'Coahuila', 'Nuevo León', 'Tamaulipas', 'Durango', 'Sinaloa']
MEX_CORE = ['México', 'Distrito Federal', 'Puebla', 'Tlaxcala', 'Morelos', 'Hidalgo', 'Veracruz', 'Oaxaca', 'Michoacán', 'Guerrero',
            'Querétaro', 'Guanajuato']
JAVA = ['Jawa Barat', 'Banten', 'Jakarta Raya', 'Jawa Tengah', 'Yogyakarta', 'Jawa Timur']
SUMATRA_S = ['Sumatera Selatan', 'Jambi', 'Riau', 'Kepulauan Riau', 'Bangka-Belitung', 'Sumatera Barat', 'Bengkulu', 'Lampung']
MUSLIM_PHL = ['Sulu', 'Tawi-Tawi', 'Basilan', 'Maguindanao', 'Lanao del Sur']
YEMEN_ZAYDI = ["Sa`dah", 'Amran', 'Hajjah', 'Al Jawf', "Sana'a", 'Amanat Al Asimah', 'Dhamar', 'Al Mahwit', 'Raymah']
IRAQ_SHIA = ['Al-Basrah', 'Maysan', 'Dhi-Qar', 'An-Najaf', "Karbala'", 'Al-Qādisiyyah', 'Babil', 'Wasit', 'Al-Muthannia']
DE_PROT_1530 = ['Sachsen', 'Thüringen', 'Sachsen-Anhalt', 'Hessen', 'Hamburg', 'Bremen', 'Niedersachsen']
DE_PROT_1600 = DE_PROT_1530 + ['Brandenburg', 'Berlin', 'Mecklenburg-Vorpommern', 'Schleswig-Holstein']
CH_PROT = ['Zürich', 'Bern', 'Basel-Stadt', 'Basel-Landschaft', 'Schaffhausen']
CH_PROT2 = CH_PROT + ['Vaud', 'Genève', 'Neuchâtel', 'Appenzell Ausserrhoden', 'Glarus', 'Thurgau', 'Graubünden']
HU_EAST = ['Hajdú-Bihar', 'Debrecen', 'Szabolcs-Szatmár-Bereg', 'Nyíregyháza', 'Békés', 'Békéscsaba', 'Jász-Nagykun-Szolnok', 'Szolnok',
           'Borsod-Abaúj-Zemplén', 'Miskolc']
PL_GERMAN = ['Lower Silesian', 'Lubusz', 'West Pomeranian', 'Pomeranian', 'Warmian-Masurian']

# ================================================================== 0. base: animism everywhere
R(B, E, 'animism')
R(-3000, E, 'shamanism', a0=['RUS'], clip=[55, 45, 190, 82])
R(-3000, E, 'shamanism', a0=['RUS'], clip=[-180, 55, -165, 75])
R(-3000, E, 'african', cont='Africa', cut=[[-18, 17, 38, 38]])
R(-3000, E, 'native_na', cont='North America')
R(-3000, E, 'south_am', cont='South America')
R(-3000, E, 'aboriginal', a0=['AUS'])
R(-3000, E, 'oceanian', a0=['PNG', 'NZL', 'FJI', 'SLB', 'VUT', 'NCL', 'WSM', 'TON', 'PYF', 'TWN', 'PHL', 'IDN', 'TLS'], cut=[[95, -11, 120, 7]])
R(-3000, E, 'oceanian', a1={'USA': ['Hawaii']})
R(500, E, 'oceanian', a0=['MDG'])
R(-3000, E, 'african', a0=['SDN', 'TCD'], clip=[14, 17, 31, 21])

# ================================================================== 1. Europe (ancient and pagan)
R(-4500, -801, 'old_european', cont='Europe', cut=[[45, 40, 190, 85], [-180, 40, -160, 85]])
R(-2000, -1451, 'old_european', a1={'GRC': ['Kriti']})       # Minoan (kept generic)
R(-1600, 349, 'hellenic', a0=['GRC', 'CYP'])
R(-1000, 349, 'hellenic', a1={'TUR': ['Izmir', 'Aydin', 'Mugla', 'Çanakkale', 'Manisa', 'Balikesir']})
R(-800, 349, 'hellenic', a0=['ITA', 'SMR', 'VAT', 'MLT'])
R(-800, 449, 'celtic', a0=['GBR', 'IRL', 'IMN'])
R(-800, -51, 'celtic', a0=['FRA', 'BEL', 'LUX', 'CHE', 'AUT', 'CZE'], a1={'DEU': ['Baden-Württemberg', 'Bayern', 'Rheinland-Pfalz', 'Saarland', 'Hessen']})
R(-800, -201, 'iberian', a0=['ESP', 'PRT'])
R(-800, -201, 'canaanite', a1={'ESP': ['Cádiz', 'Málaga', 'Almería', 'Murcia', 'Baleares']})
R(-1000, E, 'germanic', a0=['DNK', 'SWE', 'NOR'])
R(-1000, -101, 'germanic', a1={'DEU': ['Schleswig-Holstein', 'Niedersachsen', 'Hamburg', 'Bremen', 'Mecklenburg-Vorpommern', 'Brandenburg', 'Berlin', 'Sachsen-Anhalt']})
R(-100, 699, 'germanic', a0=['DEU', 'NLD'])
R(-100, 499, 'germanic', a1={'POL': ['West Pomeranian', 'Lubusz', 'Lower Silesian', 'Greater Poland', 'Pomeranian', 'Kuyavian-Pomeranian']})
R(-50, 549, 'germanic', a0=['CZE'])
R(-1000, 299, 'thracian', a0=['BGR', 'MKD'])
R(-1000, 599, 'thracian', a0=['ROU', 'MDA'])
R(-800, 1099, 'slavic', a0=['POL', 'BLR', 'UKR', 'SVK'], a1={'RUS': RUS_W + RUS_C})
R(550, 899, 'slavic', a0=['CZE'])
R(-1000, 1386, 'baltic', a0=['LTU'], a1={'POL': ['Warmian-Masurian', 'Podlachian'], 'RUS': ['Kaliningrad'], 'BLR': ['Grodno', 'Vitebsk']})
R(-1000, 1278, 'baltic', a0=['LVA'])
R(-1000, E, 'shamanism', a0=['FIN', 'EST'], a1={'RUS': RUS_N + RUS_VOLGA + RUS_URAL + ['Bashkortostan', 'Tatarstan']})
# steppe north of the Black Sea and Caspian
R(-1000, 1349, 'tengri', a1={'UKR': STEPPE_UKR, 'RUS': STEPPE_RUS}, a0=['KAZ'])
R(-1000, 1349, 'tengri', a0=['MDA'], clip=[26, 44, 31, 46.5])
# Rome spreads Greco-Roman religion (Gaul, Spain, Britain, Danube, Africa)
R(-120, 349, 'hellenic', a0=['FRA'], clip=[-5, 41, 9, 44.8])
R(-50, 349, 'hellenic', a0=['FRA', 'BEL', 'LUX', 'CHE', 'AUT', 'SVN', 'HRV', 'BIH', 'SRB', 'MNE', 'ALB', 'MKD'])
R(-200, 349, 'hellenic', a0=['ESP', 'PRT'])
R(50, 399, 'hellenic', a0=['GBR'], clip=[-6, 49, 2, 55])
R(1, 399, 'hellenic', a1={'DEU': ['Rheinland-Pfalz', 'Saarland']}, a0=['HUN'], clip=[5, 44, 19.2, 51])
R(106, 274, 'hellenic', a0=['ROU'], clip=[21, 43.5, 26, 47.5])
R(50, 349, 'hellenic', a0=['BGR'])

# ================================================================== 2. Near East, Mediterranean Africa, Iran (ancient)
R(-4000, 349, 'egyptian', a0=['EGY'])
R(-1500, 349, 'egyptian', a1={'SDN': ['Northern', 'River Nile']})
R(-4500, -1, 'mesopotamian', a0=['IRQ', 'KWT'], a1={'SYR': ['Dayr Az Zawr', 'Hasaka (Al Haksa)', 'Ar Raqqah'], 'TUR': ['Mardin', 'Sanliurfa', 'Batman', 'Siirt', 'Diyarbakir']})
R(-3000, -551, 'iranian', a0=['IRN', 'AFG', 'TKM', 'TJK', 'UZB'])
R(-1000, 99, 'iranian', a1={'CHN': ['Xinjiang']}, clip=[73, 34, 97, 42.6])
R(-3000, -540, 'mesopotamian', a1={'IRN': ['Khuzestan', 'Ilam', 'Lorestan', 'Kohgiluyeh and Buyer Ahmad', 'Fars', 'Bushehr', 'Chahar Mahall and Bakhtiari']})
R(-3000, -301, 'canaanite', a0=['LBN', 'ISR', 'PSX', 'JOR'], a1={'SYR': ['Damascus', 'Rif Dimashq', 'Homs (Hims)', 'Hamah', 'Tartus', 'Lattakia', 'Idlib', 'Aleppo', "Dar`a", 'Quneitra', "As Suwayda'"]})
R(-300, 349, 'hellenic', a0=['LBN', 'ISR', 'PSX', 'JOR'], a1={'SYR': ['Damascus', 'Rif Dimashq', 'Homs (Hims)', 'Hamah', 'Tartus', 'Lattakia', 'Idlib', 'Aleppo', "Dar`a", 'Quneitra', "As Suwayda'"]})
R(-1000, -723, 'judaism', a0=['ISR', 'PSX'])
R(-722, -587, 'judaism', a1={'ISR': ['Jerusalem', 'HaDarom'], 'PSX': ['West Bank']})
R(-538, -141, 'judaism', a1={'ISR': ['Jerusalem', 'HaMerkaz'], 'PSX': ['West Bank']})
R(-140, 134, 'judaism', a1={'ISR': ['Jerusalem', 'HaMerkaz', 'HaZafon', 'Haifa', 'HaDarom'], 'PSX': ['West Bank']})
R(-3000, 349, 'anatolian', a0=['TUR'], cut=[[25, 36, 29.5, 40.5]])
R(-200, 349, 'hellenic', a0=['TUR'], cut=[[38, 36.5, 45, 42]])
R(-550, 899, 'zoroastrian', a0=['IRN', 'TKM', 'TJK', 'UZB'], a1={'AFG': ['Hirat', 'Farah', 'Nimroz', 'Hilmand', 'Kandahar', 'Badghis', 'Faryab', 'Jawzjan', 'Balkh', 'Ghor', 'Uruzgan', 'Zabul']})
R(-550, 300, 'zoroastrian', a0=['ARM', 'AZE'], a1={'TUR': ['Van', 'Agri', 'Iğdir', 'Kars', 'Erzurum', 'Mus', 'Bitlis', 'Hakkari']})
R(-540, 299, 'zoroastrian', a1={'IRN': ['Khuzestan', 'Ilam', 'Lorestan', 'Kohgiluyeh and Buyer Ahmad', 'Fars', 'Bushehr', 'Chahar Mahall and Bakhtiari']})
R(1, 399, 'mesopotamian', a0=['IRQ', 'KWT'])
R(400, 899, 'nestorian', a0=['IRQ', 'KWT'])
R(-1500, 629, 'arabian', a0=ARABIA)
R(-1500, -1, 'arabian', a0=['JOR'], clip=[36.2, 29, 40, 33])
R(380, 525, 'judaism', a0=['YEM'], cut=[[48, 12, 54, 19]])
R(-3000, 699, 'berber', a0=MAGHREB + ['EGY'], clip=[-18, 15, 25.5, 38])
R(-3000, 1049, 'berber', a0=['NER', 'MLI', 'TCD', 'MRT', 'DZA', 'LBY'], clip=[-17, 16, 25, 27])
R(-800, -147, 'canaanite', a0=['TUN'])
R(-800, -147, 'canaanite', a0=['LBY'], clip=[10, 30.5, 15.5, 34])
R(-146, 349, 'hellenic', a0=['TUN'])
R(-146, 349, 'hellenic', a0=['LBY'], clip=[10, 30.5, 15.5, 34])
R(-100, 349, 'hellenic', a0=['LBY'], clip=[19.5, 30.5, 25.5, 33.5])
R(-40, 349, 'hellenic', a0=['DZA', 'MAR'], clip=[-9, 33.8, 9, 37.5])

# ================================================================== 3. Christianity in the Roman world (from c. 350)
WEST_ROME = ['ITA', 'SMR', 'VAT', 'MLT', 'FRA', 'BEL', 'LUX', 'CHE', 'ESP', 'PRT', 'AUT', 'SVN', 'HRV']
EAST_ROME = ['GRC', 'CYP', 'TUR', 'BGR', 'MKD', 'ALB', 'MNE', 'SRB', 'KOS', 'BIH', 'SYR', 'LBN', 'ISR', 'PSX', 'JOR']
R(350, E, 'catholic', a0=WEST_ROME)
R(350, 699, 'catholic', a0=['TUN'])
R(350, 699, 'catholic', a0=['LBY'], clip=[10, 30.5, 15.5, 34])
R(350, 699, 'catholic', a0=['DZA', 'MAR'], clip=[-9, 33.8, 9, 37.5])
R(400, E, 'catholic', a0=['GBR'], clip=[-6, 49, 2, 55])
R(450, E, 'catholic', a0=['IRL', 'IMN'])
R(550, E, 'catholic', a0=['GBR'])
R(450, 649, 'germanic', a0=['GBR'], clip=[-2.6, 50.4, 2, 56])        # Anglo-Saxon England before conversion
R(350, E, 'orthodox', a0=EAST_ROME)
R(350, 450, 'orthodox', a0=['EGY'])
R(350, 699, 'orthodox', a0=['LBY'], clip=[19.5, 30.5, 25.5, 33.5])
R(330, E, 'orthodox', a0=['GEO'])
R(301, E, 'oriental', a0=['ARM'])
R(301, 1399, 'oriental', a1={'TUR': ['Van', 'Agri', 'Iğdir', 'Kars', 'Erzurum', 'Mus', 'Bitlis', 'Hakkari', 'Bingöl', 'Erzincan', 'Tunceli', 'Elazig']})
R(400, 899, 'oriental', a0=['AZE'])                                  # Caucasian Albania
R(451, 1099, 'oriental', a0=['EGY'])
R(451, 999, 'oriental', a1={'SYR': ['Aleppo', 'Idlib', 'Ar Raqqah', 'Hasaka (Al Haksa)', 'Dayr Az Zawr'], 'TUR': ['Mardin', 'Sanliurfa', 'Batman', 'Diyarbakir', 'Adiyaman']})
R(550, 1399, 'oriental', a1={'SDN': ['Northern', 'River Nile']})
R(550, 1503, 'oriental', a1={'SDN': ['Khartoum', 'Gezira', 'Sennar', 'Blue Nile', 'White Nile']})
R(330, E, 'oriental', a1={'ETH': ['Tigray', 'Amhara', 'Addis Ababa']}, a0=['ERI'])
# Slavs in the Balkans before conversion
R(600, 863, 'slavic', a0=['SRB', 'BIH', 'MKD', 'MNE', 'KOS'], a1={'BGR': ['Vidin', 'Montana', 'Vratsa', 'Pleven', 'Lovech', 'Veliko Tarnovo', 'Ruse', 'Razgrad', 'Silistra', 'Shumen', 'Targovishte', 'Gabrovo', 'Dobrich', 'Varna']})
R(600, 799, 'slavic', a0=['HRV', 'SVN'], clip=[13, 44.5, 20, 47])
R(600, 899, 'slavic', a0=['ROU'])
R(568, 799, 'tengri', a0=['HUN'])           # Avars
R(895, 999, 'tengri', a0=['HUN'])           # Magyars
R(1000, E, 'catholic', a0=['HUN'])
R(864, E, 'orthodox', a0=['BGR', 'MKD'])
R(870, E, 'orthodox', a0=['SRB', 'MNE', 'ROU', 'MDA', 'KOS'])
R(870, 1599, 'catholic', a0=['BIH'])
R(800, E, 'catholic', a0=['HRV', 'SVN'])
# Germany, the Low Countries and Scandinavia
R(600, E, 'catholic', a1={'DEU': ['Baden-Württemberg', 'Bayern', 'Rheinland-Pfalz', 'Saarland']}, a0=['NLD'], clip=[-1, 47, 16, 51.6])
R(750, E, 'catholic', a1={'DEU': ['Hessen', 'Thüringen', 'Nordrhein-Westfalen']})
R(800, E, 'catholic', a0=['NLD'], a1={'DEU': ['Niedersachsen', 'Bremen', 'Hamburg', 'Schleswig-Holstein', 'Sachsen-Anhalt']})
R(700, 1149, 'slavic', a1={'DEU': ['Brandenburg', 'Berlin', 'Mecklenburg-Vorpommern', 'Sachsen']})
R(1150, E, 'catholic', a1={'DEU': ['Brandenburg', 'Berlin', 'Mecklenburg-Vorpommern', 'Sachsen']})
R(900, E, 'catholic', a0=['CZE', 'SVK'])
R(1000, E, 'catholic', a0=['POL', 'DNK', 'ISL'])
R(1066, E, 'catholic', a0=['NOR'])
R(1100, E, 'catholic', a0=['SWE'])
R(1200, E, 'catholic', a0=['FIN'], clip=[19, 59.5, 26, 62.5])
R(1279, E, 'catholic', a0=['FIN', 'EST', 'LVA'])
R(1300, E, 'catholic', a1={'POL': ['Warmian-Masurian'], 'RUS': ['Kaliningrad']})
R(1387, E, 'catholic', a0=['LTU'], a1={'POL': ['Podlachian']})
R(1279, E, 'orthodox', a1={'RUS': ['Karelia']}, a0=['FIN'], clip=[27.5, 60.5, 33, 66])
# Rus
R(1000, E, 'orthodox', a0=['UKR', 'BLR'], a1={'RUS': RUS_W})
R(1000, 1349, 'tengri', a1={'UKR': STEPPE_UKR})
R(1066, E, 'orthodox', a1={'RUS': RUS_C})
R(1400, E, 'orthodox', a1={'RUS': RUS_N})
R(1600, E, 'orthodox', a1={'RUS': RUS_VOLGA})
R(1700, E, 'orthodox', a1={'RUS': RUS_URAL})
R(1800, E, 'orthodox', a1={'RUS': RUS_SSIB + ['Irkutsk', 'Krasnoyarsk', 'Saratov', 'Orenburg', 'Volgograd', 'Rostov', 'Krasnodar', "Stavropol'", "Astrakhan'"]}, clip=[30, 40, 120, 61])
R(1900, E, 'orthodox', a1={'RUS': RUS_FE})
R(1900, E, 'orthodox', a1={'RUS': ['Sakha (Yakutia)']})
R(1914, E, 'orthodox', a0=['RUS'], clip=[55, 45, 190, 61])         # Trans-Siberian settlement
R(1945, E, 'orthodox', a0=['RUS'], clip=[55, 45, 190, 82])         # Soviet industrial Siberia
R(922, E, 'sunni', a1={'RUS': ['Tatarstan']})
R(1300, E, 'sunni', a1={'RUS': ['Bashkortostan']})
R(1350, 1799, 'sunni', a1={'RUS': ["Astrakhan'", 'Kalmyk', 'Volgograd', 'Orenburg', 'Saratov', 'Krasnodar', "Stavropol'", 'Rostov']})
R(1650, E, 'vajrayana', a1={'RUS': ['Kalmyk']})
R(1350, 1782, 'sunni', a1={'UKR': STEPPE_UKR})
R(1783, E, 'orthodox', a1={'UKR': STEPPE_UKR})
R(1350, 1848, 'sunni', a1={'RUS': ['Crimea', 'Sevastopol']})
R(1871, E, 'orthodox', a1={'RUS': ['Crimea', 'Sevastopol']})
# North Caucasus
R(900, 1199, 'orthodox', a1={'RUS': ['North Ossetia', 'Karachay-Cherkess', 'Kabardin-Balkar']})
R(1000, E, 'sunni', a1={'RUS': ['Dagestan']})
R(1700, E, 'sunni', a1={'RUS': ['Chechnya', 'Ingush', 'Kabardin-Balkar', 'Karachay-Cherkess', 'Adygey']})
R(1700, E, 'orthodox', a1={'RUS': ['North Ossetia']})

# ================================================================== 4. Islam
R(630, E, 'sunni', a0=ARABIA)
R(630, E, 'sunni', a0=['JOR'], clip=[36.4, 29, 40, 33])
R(750, E, 'ibadi', a1={'OMN': ['Ad Dakhliyah', 'Al Batnah North', 'Al Batnah South', 'Al Buraymi', 'Al Dhahira', 'Ash Sharqiyah North', 'Ash Sharqiyah South', 'Muscat', 'Al Wusta', 'Musandam']})
R(897, E, 'shia', a1={'YEM': YEMEN_ZAYDI})
R(900, E, 'shia', a0=['BHR'])
R(700, E, 'sunni', a0=['DZA', 'MAR', 'TUN', 'LBY', 'SAH', 'MRT'], clip=[-18, 15, 25.5, 38])
R(770, 950, 'ibadi', a0=['DZA'], clip=[-1, 30, 7, 36.6])
R(770, 1100, 'ibadi', a0=['LBY'], clip=[10, 30, 14.5, 32.6])
R(900, E, 'sunni', a0=['IRQ', 'KWT', 'IRN', 'AZE', 'TKM', 'UZB', 'TJK'])
R(1000, E, 'sunni', a0=['SYR', 'LBN', 'ISR', 'PSX', 'JOR'])
R(1100, E, 'sunni', a0=['EGY'])
R(1000, E, 'shia', a1={'LBN': ['South Lebanon', 'An Nabatiyah', 'Beqaa']})
R(1200, E, 'catholic', a1={'LBN': ['Mount Lebanon']})          # Maronites
R(1200, E, 'shia', a1={'SYR': ['Lattakia', 'Tartus']})             # Alawites
R(950, 1249, 'sunni', a0=['ESP', 'PRT'], clip=[-10, 35.8, 4, 41.0], cut=[[-1.2, 41.0, 4, 43], [-10, 40.3, -7.9, 42]])
R(1100, 1249, 'catholic', a0=['ESP', 'PRT'], clip=[-10, 39.8, 4, 42])
R(1150, 1249, 'catholic', a0=['PRT'], clip=[-10, 38.3, -7.5, 39.8])
R(1250, 1491, 'sunni', a1={'ESP': ['Granada', 'Málaga', 'Almería']})
R(950, 1149, 'sunni', a1={'ITA': ['Palermo', 'Trapani', 'Agrigento', 'Caltanissetta', 'Enna']}, a0=['MLT'])
# Anatolia and the Balkans under the Turks
R(1279, E, 'sunni', a1={'TUR': ['Konya', 'Aksaray', 'Karaman', 'Nigde', 'Nevsehir', 'Kirsehir', 'Ankara', 'Kayseri', 'Sivas', 'Tokat', 'Amasya', 'Yozgat', 'Çorum',
                                'Malatya', 'Kinkkale', 'Eskisehir', 'Afyonkarahisar', 'Kütahya', 'Isparta', 'Burdur', 'Denizli', 'Usak', 'Çankiri', 'Kastamonu',
                                'Karabük', 'Bolu', 'Düzce', 'K. Maras', 'Gaziantep', 'Adiyaman', 'Elazig', 'Erzincan', 'Tunceli', 'Bingöl', 'Diyarbakir',
                                'Sanliurfa', 'Mardin', 'Batman', 'Siirt', 'Sirnak', 'Kilis', 'Osmaniye', 'Adana', 'Hatay', 'Mersin', 'Antalya']})
R(1400, E, 'sunni', a0=['TUR'], cut=[[25.5, 40.2, 29.9, 42.2], [37.5, 40.4, 41.6, 41.4]])
R(1600, E, 'sunni', a1={'TUR': ['Trabzon', 'Rize', 'Giresun', 'Ordu']})
R(1920, E, 'sunni', a0=['TUR'])
R(1600, E, 'sunni', a0=['BIH'], cut=[[16.9, 42.4, 18.6, 43.6]])
R(1700, E, 'sunni', a1={'ALB': ['Tiranë', 'Durrës', 'Elbasan', 'Berat', 'Fier', 'Dibër', 'Kukës', 'Vlorë']})
R(1800, E, 'sunni', a0=['KOS'])
R(1994, E, 'sunni', a0=['CYP'], clip=[32.6, 35.17, 34.7, 35.75])
# Caucasus, Iran, Iraq
R(1600, E, 'shia', a0=['IRN', 'AZE'], a1={'IRQ': IRAQ_SHIA})
R(1600, E, 'sunni', a1={'IRN': ['Sistan and Baluchestan', 'Kordestan', 'Golestan']})
R(1600, 1799, 'sunni', a1={'IRQ': IRAQ_SHIA})
R(1960, E, 'shia', a1={'IRQ': ['Baghdad']})
# Central Asia
R(850, E, 'sunni', a0=['UZB', 'TJK', 'TKM'])
R(-550, 849, 'zoroastrian', a0=['UZB', 'TJK'])
R(100, 699, 'mahayana', a1={'AFG': ['Balkh', 'Kunduz', 'Takhar', 'Baghlan', 'Samangan', 'Bamyan', 'Kabul', 'Parwan', 'Kapisa', 'Logar', 'Wardak',
                                   'Laghman', 'Nangarhar', 'Kunar', 'Nuristan'],
                            'PAK': ['K.P.', 'F.A.T.A.', 'F.C.T.', 'Northern Areas'], 'UZB': ['Surkhandarya'], 'TJK': ['Khatlon']})
R(-200, 99, 'mahayana', a1={'PAK': ['K.P.', 'F.C.T.']})
R(700, 999, 'hindu', a1={'AFG': ['Kabul', 'Parwan', 'Kapisa', 'Logar', 'Wardak', 'Laghman', 'Nangarhar', 'Kunar', 'Nuristan', 'Paktya', 'Khost', 'Ghazni'],
                         'PAK': ['K.P.', 'F.A.T.A.', 'F.C.T.']})
R(900, E, 'sunni', a0=['AFG'], a1={'PAK': ['Baluchistan']})
R(900, 999, 'hindu', a1={'AFG': ['Kabul', 'Parwan', 'Kapisa', 'Logar', 'Wardak', 'Laghman', 'Nangarhar', 'Kunar', 'Nuristan', 'Paktya', 'Khost', 'Ghazni']})
R(1600, E, 'shia', a1={'AFG': ['Bamyan']})
# steppe and Mongolia
R(-1500, E, 'tengri', a0=['MNG', 'KAZ', 'KGZ'], a1={'CHN': ['Inner Mongol'], 'RUS': ['Tuva', 'Buryat', 'Chita', 'Gorno-Altay']})
R(-1500, E, 'tengri', a1={'CHN': ['Xinjiang']}, clip=[73, 42.6, 97, 50])
R(763, 840, 'manichaean', a1={'MNG': ['Arhangay', 'Övörhangay', 'Bulgan', 'Orhon', 'Töv', 'Ulaanbaatar', 'Selenge', 'Darhan-Uul', 'Hövsgöl', 'Bayanhongor']})
R(1000, E, 'sunni', a0=['KGZ'])
R(1350, E, 'sunni', a1={'KAZ': ['West Kazakhstan', 'Atyrau', 'Mangghystau', 'Aqtöbe', 'Qyzylorda', 'South Kazakhstan']})
R(1500, E, 'sunni', a0=['KAZ', 'KGZ'])
R(1930, 1994, 'orthodox', a1={'KAZ': ['North Kazakhstan', 'Qostanay', 'Aqmola', 'Astana', 'Pavlodar', 'Qaraghandy', 'East Kazakhstan']})
R(1580, E, 'vajrayana', a0=['MNG'], a1={'CHN': ['Inner Mongol']})
R(1750, E, 'vajrayana', a1={'RUS': ['Tuva', 'Buryat']})
R(1620, 1759, 'vajrayana', a1={'CHN': ['Xinjiang']}, clip=[73, 42.6, 97, 50])
R(1760, E, 'sunni', a1={'CHN': ['Xinjiang']}, clip=[73, 42.6, 97, 50])
R(100, 1499, 'mahayana', a1={'CHN': ['Xinjiang']}, clip=[73, 34, 97, 42.6])
R(1000, E, 'sunni', a1={'CHN': ['Xinjiang']}, clip=[73, 34, 80.5, 42.6])
R(1066, E, 'sunni', a1={'CHN': ['Xinjiang']}, clip=[73, 34, 86, 39.2])
R(1500, E, 'sunni', a1={'CHN': ['Xinjiang']}, clip=[73, 34, 97, 42.6])
R(1914, E, 'east_asian', a1={'CHN': ['Inner Mongol']})

# ================================================================== 5. South Asia
R(-3300, -1801, 'harappan', a1={'PAK': ['Sind', 'Punjab'], 'IND': ['Gujarat', 'Haryana', 'Punjab', 'Chandigarh']})
R(-1700, -501, 'vedic', a1={'PAK': ['Punjab', 'K.P.', 'F.C.T.'], 'IND': ['Punjab', 'Haryana', 'Delhi', 'Chandigarh', 'Himachal Pradesh']})
R(-1100, -501, 'vedic', a1={'IND': ['Uttar Pradesh', 'Uttarakhand']})
R(-800, -501, 'vedic', a1={'IND': ['Bihar', 'Rajasthan', 'Madhya Pradesh']})
R(-500, E, 'hindu', a0=['IND', 'NPL', 'BGD'], a1={'PAK': ['Punjab', 'Sind', 'F.C.T.', 'K.P.']})
R(-500, 99, 'hindu', a1={'AFG': ['Kabul', 'Parwan', 'Kapisa', 'Logar', 'Wardak', 'Laghman', 'Nangarhar', 'Kunar', 'Nuristan']})
R(-250, E, 'theravada', a0=['LKA'])
R(1200, E, 'hindu', a1={'LKA': ['Yāpanaya', 'Kilinŏchchi', 'Mulativ', 'Mannārama', 'Vavuniyāva']})
R(750, 1150, 'mahayana', a0=['BGD'], a1={'IND': ['West Bengal', 'Bihar']})
R(1000, E, 'sunni', a1={'PAK': ['Sind', 'Baluchistan', 'K.P.', 'F.A.T.A.']})
R(1500, E, 'sunni', a1={'PAK': ['Punjab', 'F.C.T.', 'Azad Kashmir']})
R(1400, E, 'sunni', a1={'IND': ['Jammu and Kashmir']}, clip=[73.4, 33.25, 75.8, 35])
R(1600, E, 'sunni', a0=['BGD'])
R(800, 1599, 'vajrayana', a1={'PAK': ['Northern Areas']})
R(1600, E, 'shia', a1={'PAK': ['Northern Areas']})
R(-500, 1399, 'hindu', a1={'PAK': ['Azad Kashmir']})
R(1400, E, 'sunni', a1={'PAK': ['Azad Kashmir']})
R(1150, E, 'sunni', a0=['MDV'])
R(1994, E, 'sikh', a1={'IND': ['Punjab']})
R(1960, E, 'protestant', a1={'IND': ['Nagaland', 'Mizoram', 'Meghalaya']})
R(-1000, 799, 'bon', a1={'CHN': ['Xizang', 'Qinghai']}, a0=['BTN'])
R(800, E, 'vajrayana', a1={'CHN': ['Xizang', 'Qinghai'], 'IND': ['Ladakh', 'Sikkim', 'Arunachal Pradesh']}, a0=['BTN'])
R(800, E, 'vajrayana', a1={'CHN': ['Sichuan']}, clip=[97, 26, 102.4, 35])

# ================================================================== 6. China, Korea, Japan
R(-2000, E, 'east_asian', a1={'CHN': ['Henan', 'Shanxi', 'Shaanxi', 'Hebei', 'Shandong', 'Beijing', 'Tianjin']})
R(-1000, E, 'east_asian', a1={'CHN': ['Anhui', 'Jiangsu', 'Hubei', 'Shanghai', 'Gansu', 'Ningxia', 'Sichuan', 'Chongqing']})
R(-300, E, 'east_asian', a1={'CHN': ['Zhejiang', 'Jiangxi', 'Hunan', 'Liaoning']})
R(-110, E, 'east_asian', a1={'CHN': ['Fujian', 'Guangdong', 'Guangxi', 'Hainan']})
R(1400, E, 'east_asian', a1={'CHN': ['Guizhou', 'Yunnan']})
R(750, 1253, 'mahayana', a1={'CHN': ['Yunnan']})
R(800, E, 'vajrayana', a1={'CHN': ['Sichuan']}, clip=[97, 26, 102.4, 35])
R(B, 1879, 'shamanism', a1={'CHN': ['Jilin', 'Heilongjiang'], 'RUS': RUS_FE})
R(1880, E, 'east_asian', a1={'CHN': ['Jilin', 'Heilongjiang']})
R(1683, E, 'east_asian', a0=['TWN'], clip=[119, 21, 121.0, 26])
R(1783, E, 'east_asian', a0=['TWN'])
R(-3000, 1682, 'oceanian', a0=['TWN'])
R(372, 1391, 'mahayana', a0=['KOR', 'PRK'])
R(1392, E, 'east_asian', a0=['KOR', 'PRK'])
R(-300, E, 'shinto', a0=['JPN'], clip=[122, 24, 146, 41.4])
R(1880, E, 'shinto', a0=['JPN'])

# ================================================================== 7. Southeast Asia
R(-110, E, 'east_asian', a0=['VNM'], clip=[102, 16.8, 110, 24])
R(1471, E, 'east_asian', a0=['VNM'], clip=[102, 13.5, 110, 24])
R(1700, E, 'east_asian', a0=['VNM'], clip=[102, 10.8, 110, 24])
R(1783, E, 'east_asian', a0=['VNM'])
R(200, 1470, 'hindu', a0=['VNM'], clip=[106.5, 10.8, 110, 16.8])
R(1471, 1699, 'hindu', a0=['VNM'], clip=[106.5, 10.8, 110, 13.5])
R(100, 699, 'hindu', a0=['VNM', 'KHM'], clip=[103, 8, 107.2, 12.5])
R(600, 1299, 'hindu', a0=['KHM'])
R(800, 1299, 'hindu', a1={'THA': ['Nakhon Ratchasima', 'Buri Ram', 'Surin', 'Si Sa Ket', 'Ubon Ratchathani', 'Amnat Charoen', 'Yasothon', 'Roi Et',
                                  'Maha Sarakham', 'Khon Kaen', 'Chaiyaphum', 'Kalasin', 'Sa Kaeo', 'Prachin Buri']})
R(800, 1299, 'hindu', a0=['LAO'], clip=[104, 13.5, 108, 16.5])
R(600, 1299, 'theravada', a0=['THA'], clip=[98, 12, 102, 17.6])
R(1300, E, 'theravada', a0=['THA', 'LAO', 'KHM'])
R(1300, 1782, 'theravada', a0=['VNM'], clip=[104, 8, 107, 10.8])
R(300, E, 'theravada', a1={'MMR': ['Mon', 'Bago', 'Yangon', 'Ayeyarwady', 'Magway', 'Mandalay', 'Rakhine', 'Sagaing']})
R(1050, E, 'theravada', a0=['MMR'])
R(1300, E, 'animism', a1={'MMR': ['Kachin', 'Chin']})
R(1960, E, 'protestant', a1={'MMR': ['Kachin', 'Chin']})
R(400, 1449, 'hindu', a0=['MYS'], cut=[[108, 0, 120, 8]])
R(400, 1449, 'hindu', a1={'THA': ['Pattani', 'Yala', 'Narathiwat', 'Satun', 'Songkhla']})
R(1450, E, 'sunni', a0=['MYS'], cut=[[108, 0, 120, 8]])
R(1450, E, 'sunni', a1={'THA': ['Pattani', 'Yala', 'Narathiwat']})
R(1400, E, 'sunni', a0=['BRN'])
R(400, 1529, 'hindu', a1={'IDN': JAVA})
R(400, E, 'hindu', a1={'IDN': ['Bali']})
R(1530, E, 'sunni', a1={'IDN': ['Jawa Barat', 'Banten', 'Jakarta Raya', 'Jawa Tengah', 'Yogyakarta']})
R(1600, E, 'sunni', a1={'IDN': ['Jawa Timur', 'Nusa Tenggara Barat']})
R(650, 1499, 'mahayana', a1={'IDN': SUMATRA_S})
R(1300, E, 'sunni', a1={'IDN': ['Aceh']})
R(1500, E, 'sunni', a1={'IDN': ['Riau', 'Kepulauan Riau', 'Jambi', 'Sumatera Selatan', 'Bangka-Belitung', 'Maluku Utara']})
R(1600, E, 'sunni', a1={'IDN': ['Sumatera Barat', 'Bengkulu', 'Lampung', 'Sumatera Utara', 'Kalimantan Selatan', 'Gorontalo']})
R(1650, E, 'sunni', a1={'IDN': ['Sulawesi Selatan', 'Sulawesi Barat']})
R(1650, E, 'protestant', a1={'IDN': ['Maluku']})
R(1880, E, 'protestant', a1={'IDN': ['Sulawesi Utara']})
R(1914, E, 'sunni', a1={'IDN': ['Sulawesi Tengah', 'Sulawesi Tenggara', 'Kalimantan Barat', 'Kalimantan Timur', 'Kalimantan Tengah']})
R(1914, E, 'catholic', a1={'IDN': ['Nusa Tenggara Timur']})
R(1994, E, 'protestant', a1={'IDN': ['Papua', 'Papua Barat']})
R(1994, E, 'catholic', a0=['TLS'])
R(1450, E, 'sunni', a1={'PHL': MUSLIM_PHL})
R(1600, E, 'catholic', a0=['PHL'], clip=[116, 9.3, 127, 21.5])
R(1945, E, 'catholic', a0=['PHL'])
R(1450, E, 'sunni', a1={'PHL': MUSLIM_PHL})

# ================================================================== 8. Africa
# Islam in Africa
R(1050, E, 'sunni', a0=['MRT', 'SAH', 'DZA', 'LBY', 'MAR', 'TUN'])
R(1050, E, 'sunni', a0=['MLI', 'NER'], clip=[-12, 16.3, 16, 25])
R(1100, E, 'sunni', a1={'TCD': ['Kanem', 'Lac', 'Barh El Gazel', 'Hadjer-Lamis', 'Borkou', 'Ennedi', 'Tibesti'], 'NGA': ['Borno', 'Yobe']})
R(1400, E, 'sunni', a1={'SDN': ['Northern', 'River Nile']})
R(1200, E, 'sunni', a0=['SDN'], clip=[33.5, 17, 38.7, 22.5])     # Beja of the Red Sea hills
R(1504, E, 'sunni', a1={'SDN': ['Khartoum', 'Gezira', 'Sennar', 'Blue Nile', 'White Nile', 'Kassala', 'Gedarif', 'Red Sea', 'North Kordufan']})
R(1600, E, 'sunni', a1={'SDN': ['North Darfur', 'Western Darfur', 'Central Darfur', 'Southern Darfur', 'Eastern Darfur', 'South Kordufan'],
                       'TCD': ['Ouaddaï', 'Wadi Fira', 'Batha', 'Guéra', 'Salamat', 'Sila', 'Chari-Baguirmi', 'Ville de N\'Djamena']})
R(1700, E, 'sunni', a1={'NGA': ['Kano', 'Katsina', 'Zamfara', 'Sokoto', 'Kebbi', 'Jigawa', 'Bauchi', 'Gombe']})
R(1815, E, 'sunni', a1={'NGA': ['Kaduna', 'Niger', 'Kwara', 'Adamawa', 'Federal Capital Territory', 'Nassarawa'], 'CMR': ['Nord', 'Extrême-Nord', 'Adamaoua']})
R(1880, E, 'sunni', a1={'NGA': ['Oyo', 'Osun']})
R(1783, E, 'sunni', a1={'SEN': ['Matam', 'Saint-Louis']}, a0=['GIN'], clip=[-14.5, 10, -10.5, 17])
R(1880, E, 'sunni', a0=['SEN', 'GMB'], cut=[[-17, 12.0, -13.5, 13.3]])
R(1815, E, 'sunni', a1={'MLI': ['Mopti', 'Ségou']}, a0=['NER'])
R(1914, E, 'sunni', a0=['MLI', 'NER', 'GIN', 'MRT'])
R(1960, E, 'sunni', a0=['SLE'], a1={'CIV': ['Savanes', 'Denguélé', 'Worodougou', 'Bafing', 'Zanzan']})
R(1994, E, 'sunni', a0=['BFA'])
R(900, E, 'sunni', a0=['SOM', 'DJI'], a1={'ETH': ['Somali', 'Afar', 'Harari People', 'Dire Dawa'], 'KEN': ['North-Eastern']})
R(900, E, 'sunni', a0=['ERI'], clip=[36.4, 12.3, 43.5, 18.1], cut=[[37.8, 14.4, 39.4, 16.2]])
R(1800, E, 'sunni', a1={'ETH': ['Oromiya']})
R(1000, E, 'sunni', box=[[39.0, -10.6, 41.0, -4.5], [39.4, -4.7, 41.8, -1.6]], a1={'TZA': ['Zanzibar South and Central', 'Zanzibar West', 'Kaskazini-Pemba',
                                                                                     'Kaskazini-Unguja', 'Kusini-Pemba']})
R(1100, E, 'sunni', box=[39.5, -17, 41.0, -10.4], a0=['COM'])
R(1500, E, 'sunni', a0=['MOZ'], clip=[37, -17, 41, -10.4])
# Christianity in Africa (colonial and modern majorities)
R(1500, 1799, 'catholic', a0=['AGO', 'COD'], clip=[12.2, -8.6, 16.2, -4.6])     # Kingdom of Kongo
R(1783, E, 'protestant', a1={'ZAF': ['Western Cape']})
R(1848, E, 'protestant', a1={'ZAF': ['Eastern Cape', 'Northern Cape', 'Free State']})
R(1900, E, 'protestant', a1={'ZAF': ['KwaZulu-Natal', 'Gauteng', 'North West']})
R(1945, E, 'protestant', a0=['ZAF', 'SWZ', 'NAM'])
R(1914, E, 'catholic', a0=['LSO'])
R(1880, E, 'protestant', a1={'MDG': ['Analamanga', 'Vakinankaratra', "Amoron'i Mania", 'Haute Matsiatra', 'Itasy', 'Bongolava']})
R(1960, E, 'protestant', a0=['MDG'])
R(1914, E, 'catholic', a0=['UGA'], clip=[29.5, -1.5, 34, 2.2])
R(1945, E, 'catholic', a0=['UGA', 'RWA', 'BDI', 'COD', 'COG', 'GAB', 'AGO'])
R(1960, E, 'catholic', a0=['CAF'], a1={'CMR': ['Centre', 'Sud', 'Littoral', 'Est', 'Ouest']})
R(1960, E, 'protestant', a1={'CMR': ['Nord-Ouest', 'Sud-Ouest']})
R(1945, E, 'protestant', a0=['MWI'])
R(1994, E, 'protestant', a0=['LBR'])
R(1945, E, 'protestant', a1={'GHA': ['Central', 'Eastern', 'Greater Accra', 'Western', 'Ashanti', 'Volta', 'Brong Ahafo']})
R(1945, E, 'catholic', a1={'NGA': ['Anambra', 'Imo', 'Abia', 'Enugu', 'Ebonyi']})
R(1945, E, 'protestant', a1={'NGA': ['Rivers', 'Bayelsa', 'Delta', 'Edo', 'Akwa Ibom', 'Cross River', 'Lagos', 'Ogun', 'Ondo', 'Ekiti']})
R(1994, E, 'protestant', a1={'NGA': ['Plateau', 'Benue', 'Taraba', 'Kogi']})
R(1960, E, 'protestant', a0=['ZMB', 'ZWE', 'BWA'])
R(1960, E, 'protestant', a1={'KEN': ['Central', 'Nairobi', 'Nyanza', 'Western', 'Rift Valley', 'Eastern']})
R(1960, E, 'catholic', a0=['TZA'], cut=[[38.8, -11, 42, -4.4]])
R(1994, E, 'catholic', a0=['MOZ'], clip=[30, -27, 37, -14])
R(1994, E, 'catholic', a0=['SDS'])
R(1994, E, 'catholic', a1={'TCD': ['Logone Occidental', 'Logone Oriental', 'Mandoul', 'Moyen-Chari', 'Tandjilé', 'Mayo-Kebbi Est', 'Mayo-Kebbi Ouest']})
R(1994, E, 'protestant', a1={'ETH': ['Southern Nations, Nationalities and Peoples', 'Gambela Peoples']})
R(1945, E, 'catholic', a0=['CPV', 'STP', 'GNQ'])

# ================================================================== 9. The Americas
R(-1500, 1529, 'mesoamerican', a1={'MEX': [n for n in ['Aguascalientes', 'Campeche', 'Chiapas', 'Colima', 'Distrito Federal', 'Guanajuato', 'Guerrero', 'Hidalgo',
                                                        'Jalisco', 'Michoacán', 'Morelos', 'México', 'Nayarit', 'Oaxaca', 'Puebla', 'Querétaro', 'Quintana Roo',
                                                        'San Luis Potosí', 'Tabasco', 'Tlaxcala', 'Veracruz', 'Yucatán', 'Zacatecas']]},
  a0=['GTM', 'BLZ', 'SLV'])
R(-1500, 1599, 'mesoamerican', a0=['HND'], clip=[-90, 13, -87, 16.5])
R(1530, 1599, 'mesoamerican', a1={'MEX': ['Campeche', 'Chiapas', 'Quintana Roo', 'Yucatán', 'Tabasco', 'Jalisco', 'Nayarit', 'Zacatecas', 'Aguascalientes',
                                          'San Luis Potosí', 'Colima']}, a0=['GTM', 'BLZ'])
R(-3000, 1572, 'andean', poly=ANDES)
# Latin American Catholicism
R(1530, E, 'catholic', a1={'MEX': MEX_CORE}, a0=['CUB', 'DOM', 'HTI', 'PRI', 'JAM'])
R(1600, E, 'catholic', a0=['MEX', 'GTM', 'SLV', 'HND', 'NIC', 'CRI', 'PAN', 'BLZ'], cut=[[-118, 26, -96, 33]])
R(1600, E, 'catholic', poly=ANDES)
R(1600, E, 'catholic', a1={'COL': ['Antioquia', 'Atlántico', 'Bogota', 'Bolívar', 'Boyacá', 'Caldas', 'Cauca', 'Cesar', 'Cundinamarca', 'Córdoba', 'Huila',
                                   'La Guajira', 'Magdalena', 'Nariño', 'Norte de Santander', 'Quindío', 'Risaralda', 'Santander', 'Sucre', 'Tolima',
                                   'Valle del Cauca'],
                           'VEN': ['Distrito Capital', 'Miranda', 'Aragua', 'Carabobo', 'Falcón', 'Lara', 'Yaracuy', 'Zulia', 'Mérida', 'Táchira', 'Trujillo',
                                   'Sucre', 'Nueva Esparta', 'Vargas'],
                           'ARG': ['Buenos Aires', 'Ciudad de Buenos Aires', 'Santa Fe', 'Córdoba', 'Tucumán', 'Salta', 'Jujuy', 'Santiago del Estero',
                                   'Catamarca', 'La Rioja', 'Mendoza', 'San Juan'],
                           'CHL': ['Región Metropolitana de Santiago', 'Valparaíso', "Libertador General Bernardo O'Higgins", 'Maule', 'Coquimbo', 'Ñuble', 'Bío-Bío'],
                           'BRA': ['Pernambuco', 'Paraíba', 'Rio Grande do Norte', 'Alagoas', 'Sergipe', 'Bahia', 'Espírito Santo', 'Rio de Janeiro', 'São Paulo']})
R(1600, E, 'catholic', a0=['ECU'], clip=[-81.5, -5.5, -77.5, 1.6])
R(1650, E, 'catholic', a0=['PRY'])
R(1700, E, 'catholic', a0=['URY'])
R(1700, E, 'catholic', a1={'BRA': ['Minas Gerais', 'Ceará', 'Piauí', 'Maranhão', 'Paraná', 'Santa Catarina'],
                           'ARG': ['Corrientes', 'Entre Ríos', 'Misiones', 'San Luis'],
                           'VEN': ['Anzoátegui', 'Monagas', 'Guárico', 'Cojedes', 'Portuguesa', 'Barinas']})
R(1700, E, 'catholic', a1={'MEX': ['Chihuahua', 'Coahuila', 'Nuevo León', 'Sonora', 'Durango', 'Sinaloa']})
R(1783, E, 'catholic', a0=['MEX'], a1={'BRA': ['Goiás', 'Mato Grosso', 'Mato Grosso do Sul', 'Rio Grande do Sul', 'Distrito Federal', 'Tocantins'],
                                       'CHL': ['La Araucanía'], 'BOL': ['Santa Cruz', 'Chuquisaca', 'Tarija', 'Cochabamba']})
R(1800, E, 'catholic', a0=['COL', 'VEN'], cut=[[-75, -5, -60, 3.8]])
R(1900, E, 'catholic', a0=['ARG', 'CHL', 'BRA', 'BOL', 'PRY', 'URY'])
R(1945, E, 'catholic', a0=['PER', 'ECU', 'COL', 'VEN', 'BOL'])
R(1783, E, 'protestant', a0=['GUY', 'SUR'], clip=[-62, 4.5, -53.8, 9])
R(1900, E, 'protestant', a0=['GUY', 'SUR'])
R(1783, E, 'catholic', box=[-54.6, 2, -51.5, 5.9])
R(1650, E, 'catholic', a1={'USA': ['New Mexico']}, clip=[-109, 32, -103, 37.2])
R(1715, 1836, 'catholic', a1={'USA': ['Texas']}, clip=[-100.5, 27, -94, 30.5])
R(1715, E, 'catholic', a1={'USA': ['Louisiana']})
R(1783, 1870, 'catholic', a1={'USA': ['California']}, clip=[-123.5, 32, -117, 38.5])
R(1650, 1699, 'catholic', a1={'USA': ['Florida', 'Georgia']}, clip=[-85, 25, -80, 31.5])
R(1700, 1762, 'catholic', a1={'USA': ['Florida']}, clip=[-85, 25, -80, 31.5])
# English, Dutch, French North America
R(1650, E, 'protestant', a1={'USA': ['Massachusetts', 'Connecticut', 'Rhode Island', 'Virginia', 'Maryland', 'New Hampshire']}, cut=[[-83.7, 36, -79.5, 40]])
R(1650, E, 'protestant', a0=['BRB', 'BMU'])
R(1700, E, 'protestant', a1={'USA': ['New York', 'New Jersey', 'Pennsylvania', 'Delaware', 'Maryland', 'North Carolina', 'South Carolina', 'Maine', 'Virginia']},
  cut=[[-90, 34, -79.5, 43]])
R(1700, E, 'protestant', a0=['JAM'])
R(1715, E, 'protestant', a0=['BHS'])
R(1783, E, 'protestant', a1={'USA': ['New York', 'Pennsylvania', 'Virginia', 'West Virginia', 'North Carolina', 'South Carolina', 'Georgia', 'Vermont', 'Maine']})
R(1800, E, 'protestant', a1={'USA': ['Kentucky', 'Tennessee']})
R(1815, E, 'protestant', a1={'USA': ['Ohio', 'Indiana', 'Mississippi', 'Alabama']}, cut=[[-88.2, 30.2, -84.8, 35], [-86.5, 39.8, -84.8, 41.8]])
R(1848, E, 'protestant', a1={'USA': ['Ohio', 'Indiana', 'Illinois', 'Michigan', 'Wisconsin', 'Iowa', 'Missouri', 'Arkansas', 'Alabama', 'Mississippi',
                                    'Florida', 'Texas', 'Georgia', 'Tennessee', 'Kentucky']}, cut=[[-100.5, 25.8, -96.3, 30.5]])
R(1871, E, 'protestant', a1={'USA': ['Minnesota', 'Kansas', 'Nebraska', 'California', 'Oregon', 'Washington', 'Nevada', 'Colorado', 'Utah', 'Texas']})
R(1880, E, 'protestant', a1={'USA': ['North Dakota', 'South Dakota', 'Montana', 'Idaho', 'Wyoming']})
R(1900, E, 'protestant', a0=['USA'], cut=[[-109.1, 31.3, -103, 37.1]])
R(1900, E, 'catholic', a1={'USA': ['Louisiana']})
R(1914, E, 'protestant', a1={'USA': ['Alaska', 'Hawaii']})
R(1848, 1899, 'protestant', a1={'USA': ['Hawaii']})
R(1650, E, 'catholic', a1={'CAN': ['Québec']}, clip=[-75, 45, -64, 49.3])
R(1650, 1754, 'catholic', a1={'CAN': ['Nova Scotia', 'New Brunswick', 'Prince Edward Island']})
R(1783, E, 'protestant', a1={'CAN': ['Nova Scotia', 'New Brunswick', 'Prince Edward Island']})
R(1715, E, 'protestant', a1={'CAN': ['Newfoundland and Labrador']}, clip=[-56, 46.5, -52.5, 49.5])
R(1815, E, 'protestant', a1={'CAN': ['Ontario']}, clip=[-83.2, 41.6, -74.3, 45.5])
R(1900, E, 'protestant', a1={'CAN': ['Ontario', 'Manitoba', 'Saskatchewan', 'Alberta', 'British Columbia']}, clip=[-140, 41, -74, 55])
R(1945, E, 'protestant', a0=['CAN'])                                   # Inuit and northern First Nations largely Anglican by mid-century
R(1900, E, 'catholic', a1={'CAN': ['Québec']}, clip=[-80, 45, -60, 52])
R(1945, E, 'catholic', a1={'CAN': ['New Brunswick']}, clip=[-68.5, 46.8, -64, 48.1])
R(1800, E, 'protestant', a0=['GRL'])
# Utah: Latter-day Saints from 1847
R(1848, E, 'lds', a1={'USA': ['Utah']}, clip=[-112.6, 39.3, -111.2, 42.1])
R(1871, E, 'lds', a1={'USA': ['Utah']})

# ================================================================== 10. Reformation and modern Europe
R(1420, 1620, 'protestant', a0=['CZE'], clip=[12, 48.5, 16.5, 51.1])
R(1530, E, 'protestant', a1={'DEU': DE_PROT_1530, 'CHE': CH_PROT, 'POL': ['Warmian-Masurian'], 'RUS': ['Kaliningrad']}, a0=['SWE', 'FIN', 'EST', 'LVA'])
R(1600, E, 'protestant', a1={'DEU': DE_PROT_1600, 'CHE': CH_PROT2, 'POL': PL_GERMAN, 'HUN': HU_EAST}, a0=['DNK', 'NOR', 'ISL', 'GBR'])
R(1600, E, 'protestant', a1={'DEU': ['Baden-Württemberg']}, clip=[8.6, 47.9, 10.6, 49.8])
R(1600, E, 'protestant', a1={'DEU': ['Rheinland-Pfalz']}, clip=[7.3, 48.9, 8.6, 49.7])
R(1650, E, 'protestant', a0=['NLD'], a1x={'NLD': ['Noord-Brabant', 'Limburg']})
R(1600, 1649, 'catholic', a0=['GBR'], clip=[-8.3, 53.9, -5.3, 55.4])
R(1600, 1649, 'protestant', a0=['AUT'], clip=[12.5, 46.5, 17.2, 49.1])
R(1650, E, 'catholic', a0=['LVA'], clip=[26.2, 55.6, 28.3, 57.2])
R(1960, E, 'catholic', a1={'POL': PL_GERMAN})
R(1960, E, 'orthodox', a1={'RUS': ['Kaliningrad']})
R(1945, E, 'catholic', a1={'HUN': ['Borsod-Abaúj-Zemplén', 'Miskolc', 'Jász-Nagykun-Szolnok', 'Szolnok', 'Békés', 'Békéscsaba']})
R(1960, E, 'judaism', a0=['ISR'])
R(1994, E, 'none', a0=['CZE', 'EST'], a1={'DEU': ['Brandenburg', 'Berlin', 'Mecklenburg-Vorpommern', 'Sachsen', 'Sachsen-Anhalt', 'Thüringen']})

# ================================================================== 11. Oceania
R(1848, E, 'protestant', a1={'AUS': ['New South Wales', 'Victoria', 'Tasmania', 'Australian Capital Territory']})
R(1848, E, 'protestant', a1={'AUS': ['South Australia']}, clip=[129, -38, 141, -30])
R(1871, E, 'protestant', a1={'AUS': ['Queensland']}, clip=[138, -29.2, 154, -15])
R(1900, E, 'protestant', a1={'AUS': ['Queensland', 'South Australia']}, a0=['NZL'])
R(1878, E, 'protestant', a1={'AUS': ['Western Australia']}, clip=[114, -35.5, 119.5, -28.5])
R(1900, E, 'protestant', a1={'AUS': ['Western Australia']}, clip=[112, -36, 124, -25])
R(1914, E, 'protestant', a0=['AUS'])
R(1848, E, 'protestant', a0=['NZL', 'TON', 'WSM', 'PYF'])
R(1878, E, 'protestant', a0=['FJI'])
R(1914, E, 'catholic', a0=['NCL'])
R(1945, E, 'protestant', a0=['SLB', 'VUT'])
R(1960, E, 'protestant', a0=['PNG'])


# ------------------------------------------------------------------ QC fixes (launch-readiness pass, 14 Oct 2026)
R(900, E, 'sunni', a0=['SOL'])                                                     # Somaliland was missed by the Somali rule above
R(1890, E, 'oriental', a1={'ETH': ['Oromiya']}, clip=[38.3, 8.6, 39.9, 10.3])      # Shewa core around Addis Ababa: Orthodox
R(1994, E, 'catholic', a0=['CIV'], clip=[-8.7, 4.3, -2.4, 7.9])                   # southern Côte d'Ivoire: Christian plurality
R(1994, E, 'sunni', a1={'CIV': ['Savanes', 'Denguélé', 'Worodougou', 'Bafing', 'Zanzan']})


# ------------------------------------------------------------------ gap pass (15 Oct 2026): places that fell through to the
# world default ("animism"). gap=True rules only repaint pixels still holding that default. 'na' = unknown or uncertain.
def G(y0, y1, faith, note, **where): R(y0, y1, faith, gap=True, note=note, **where)
CY = dict(a0=['CYP'])
G(B, 1960, '@like', 'Cyprus enclaves follow the rest of the island', a0=['CYN', 'CNM', 'ESB', 'WSB'], like=CY)
G(1961, E, 'sunni', 'Northern Cyprus: Turkish Cypriot, Sunni since 1974', a0=['CYN'])
G(1961, E, 'na', 'Cyprus UN buffer zone: demilitarised, almost no residents', a0=['CNM'])
G(1961, E, '@like', 'British bases on Cyprus follow the Republic', a0=['ESB', 'WSB'], like=CY)
G(B, E, '@like', 'Åland follows Sweden (Swedish-speaking)', a0=['ALD'], like=dict(a0=['SWE']))
G(B, E, '@like', 'Andorra follows Catalonia', a0=['AND'], like=dict(a1={'ESP': ['Lérida']}))
G(B, E, '@like', 'Liechtenstein follows Vorarlberg', a0=['LIE'], like=dict(a1={'AUT': ['Vorarlberg']}))
G(B, E, '@like', 'Monaco follows Alpes-Maritimes', a0=['MCO'], like=dict(a1={'FRA': ['Alpes-Maritimes']}))
G(B, 1530, '@like', 'Jersey follows Normandy', a0=['JEY'], like=dict(a1={'FRA': ['Manche']}))
G(1531, E, 'protestant', 'Jersey: Protestant since the Reformation', a0=['JEY'])
G(B, E, '@like', 'Hong Kong follows Guangdong', a0=['HKG', 'MAC'], like=dict(a1={'CHN': ['Guangdong']}))
G(B, 1815, '@like', 'Singapore follows Johor', a0=['SGP'], like=dict(a1={'MYS': ['Johor']}))
G(1816, E, 'mahayana', 'Singapore: Chinese majority since the 1800s; Buddhism the largest faith', a0=['SGP'])
G(B, E, '@like', 'Baikonur follows Qyzylorda', a0=['KAB'], like=dict(a1={'KAZ': ['Qyzylorda']}))
G(B, E, '@like', 'Kosovo follows Serbia', a0=['KOS'], like=dict(a0=['SRB']))
G(B, E, '@like', 'Guantanamo Bay follows Cuba', a0=['USG'], like=dict(a1={'CUB': ['Guantánamo']}))
G(B, E, 'na', 'Siachen Glacier: uninhabited glacier', a0=['KAS'])
G(B, E, 'na', 'Bir Tawil: uninhabited desert', a0=['BRT'])
G(B, E, 'na', 'Antarctic and sub-Antarctic islands: no permanent population', a0=['ATF', 'HMD', 'SGS', 'ATA'])
G(B, E, 'na', 'Christmas, Cocos and Chagos islands: very small, mixed or military populations', a0=['IOA', 'IOT'])
G(1000, 1530, 'catholic', 'Faroe Islands: Catholic until the Reformation', a0=['FRO'])
G(1531, E, 'protestant', 'Faroe Islands: Lutheran', a0=['FRO'])
G(B, 1830, 'oceanian', 'Samoa, Niue, Wallis and Futuna before missions', a0=['ASM', 'NIU', 'WLF', 'COK'])
G(1831, E, 'protestant', 'American Samoa, Niue and the Cook Islands: Congregational and other Protestant churches', a0=['ASM', 'NIU', 'COK'])
G(1831, E, 'catholic', 'Wallis and Futuna: Catholic', a0=['WLF'])
G(1900, E, 'catholic', 'Guam, Palau, Micronesia, Kiribati: Catholic plurality', a0=['GUM', 'PLW', 'FSM', 'KIR'])
G(1914, 1945, 'shinto', 'Northern Marianas under Japan: Japanese settlers outnumbered Chamorros', a0=['MNP'])
G(1946, E, 'catholic', 'Northern Marianas: Catholic', a0=['MNP'])
G(1938, 1945, 'na', 'Kiribati 1938: Catholic and Protestant roughly equal', a0=['KIR'])
G(1900, E, 'hindu', 'Mauritius: Hindu plurality', a0=['MUS'])
G(1900, E, 'catholic', 'Seychelles: Catholic', a0=['SYC'])
G(1700, E, 'protestant', 'Saint Helena: Anglican', a0=['SHN'])
G(1960, E, 'sunni', 'Sabah: Muslim majority', a1={'MYS': ['Sabah']})
G(1960, E, 'protestant', 'Sarawak: Christian plurality (mostly Protestant churches; Catholic share also large)', a1={'MYS': ['Sarawak']})
G(-800, 700, 'germanic', 'Netherlands: Germanic paganism before conversion', a0=['NLD'])
G(-800, -1, 'germanic', 'Thuringia and Saxony: Jastorf-culture Germanic peoples', a1={'DEU': ['Thüringen', 'Sachsen']})
G(-800, -1, 'na', 'Lower Rhine: Celtic-Germanic borderland, too uncertain to name', a1={'DEU': ['Nordrhein-Westfalen']})
G(-800, -101, 'na', 'Western Balkans: Illyrian religion (no category on this map)', a0=['ALB', 'BIH', 'HRV', 'MNE', 'SRB', 'SVN'])
G(-800, 800, 'na', 'Pannonian Basin: Celtic, Sarmatian, Hunnic and Avar religions, too mixed to name', a0=['HUN'])
G(-800, 300, 'na', 'Pre-Christian Georgia: local religion with Iranian influence (no category on this map)', a0=['GEO'])
G(-800, 800, 'na', 'Eastern Afghanistan: Buddhist, Hindu and local cults, too mixed to name', a0=['AFG'])
G(-800, 300, 'na', 'Syrian Jazira: mixed Semitic cults, early Christianity', a0=['SYR'])
