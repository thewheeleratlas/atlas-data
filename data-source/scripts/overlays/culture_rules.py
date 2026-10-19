"""Majority-culture rules for the Culture layer.

Same rule format as religion_rules.py: (first year, last year, culture id, where), applied in order, later rules override.
A "culture" here is the ethnic / ethno-linguistic identity of most of the people living in an area (as on a Crusader Kings
culture map), not the ruler's.  Cultures are grouped into families (language families or broad heritages).
Before c. 500 BCE, and outside the well-documented regions before c. 1000 CE, the picture is broad-brush.
"""
import colorsys

# family id, display name, base hue (deg), saturation
FAMS = [
    ('prehistoric', 'Prehistoric peoples', 35, 0.18),
    ('latin', 'Latin (Romance)', 46, 0.62),
    ('germanic', 'Germanic', 218, 0.50),
    ('celtic', 'Celtic', 140, 0.42),
    ('hellenic', 'Hellenic', 198, 0.55),
    ('slavic', 'Slavic', 285, 0.38),
    ('baltic', 'Baltic', 78, 0.42),
    ('uralic', 'Uralic (Finno-Ugric)', 176, 0.40),
    ('paleo_eu', 'Paleo-European and early Indo-European', 28, 0.30),
    ('caucasian', 'Caucasian and Armenian', 4, 0.45),
    ('ane', 'Ancient Near Eastern', 48, 0.38),
    ('semitic', 'Semitic', 104, 0.42),
    ('afroasiatic', 'Berber, Egyptian and Cushitic', 38, 0.50),
    ('iranian', 'Iranian', 160, 0.45),
    ('turkic', 'Turkic', 10, 0.58),
    ('mongolic', 'Mongolic and Tungusic', 36, 0.55),
    ('arctic', 'Arctic and Paleo-Siberian', 205, 0.25),
    ('indo_aryan', 'Indo-Aryan', 26, 0.66),
    ('dravidian', 'Dravidian', 338, 0.48),
    ('sinitic', 'Chinese (Sinitic)', 354, 0.62),
    ('tibeto_burman', 'Tibeto-Burman', 296, 0.42),
    ('tai', 'Tai-Kadai', 68, 0.55),
    ('austroasiatic', 'Austroasiatic', 128, 0.45),
    ('austronesian', 'Austronesian', 184, 0.50),
    ('japonic', 'Japanese and Korean', 322, 0.50),
    ('w_african', 'West African (Niger-Congo)', 28, 0.45),
    ('bantu', 'Bantu', 14, 0.45),
    ('nilo', 'Nilo-Saharan', 52, 0.40),
    ('khoisan', 'Khoisan', 42, 0.30),
    ('n_american', 'North American peoples', 32, 0.40),
    ('mesoamerican', 'Mesoamerican', 12, 0.55),
    ('andean', 'Andean', 300, 0.38),
    ('s_american', 'Lowland South American', 112, 0.40),
    ('creole', 'Creole and African diaspora', 330, 0.30),
    ('oceanian', 'Oceanian and Australian', 18, 0.45),
]
FAMILIES = [[f, n] for f, n, _, _ in FAMS]
FAMILIES.append(['na', 'Unknown or uncertain'])
_FAMH = {f: (h, s) for f, n, h, s in FAMS}

# id, name, family, Wikipedia title, one-line note
C = [
    # prehistory
    ('foragers', 'Hunter-gatherers', 'prehistoric', 'Hunter-gatherer', 'Mobile foraging bands: the way of life of all humans before farming, and of many peoples long after.'),
    ('neolithic', 'Neolithic farmers', 'prehistoric', 'Neolithic Revolution', 'The first farming peoples, spreading from the Fertile Crescent into Europe and beyond from c. 9000 BCE.'),
    ('saharan', 'Green Sahara herders', 'prehistoric', 'African humid period', 'Cattle herders of the "Green Sahara" (c. 7000-3000 BCE), painted on the rocks of Tassili and Acacus.'),
    # Paleo-European / early IE
    ('old_euro', 'Old European farmers', 'paleo_eu', 'Old Europe (archaeology)', 'The Neolithic and Copper Age farming cultures of Europe before the Indo-European languages arrived.'),
    ('pie', 'Proto-Indo-Europeans', 'paleo_eu', 'Proto-Indo-Europeans', 'Herders of the Pontic-Caspian steppe (Yamnaya culture), whose language is the ancestor of most European and Indian tongues.'),
    ('bronze_ie', 'Bronze Age Indo-Europeans', 'paleo_eu', 'Corded Ware culture', 'The Corded Ware, Bell Beaker and Urnfield peoples of Bronze Age Europe, ancestors of the Celts, Germans, Balts and Slavs.'),
    ('basque', 'Basque', 'paleo_eu', 'Basques', 'The only surviving pre-Indo-European people of western Europe, in the western Pyrenees.'),
    ('iberian', 'Iberians', 'paleo_eu', 'Iberians', 'The pre-Roman peoples of eastern and southern Spain, with their own script.'),
    ('etruscan', 'Etruscans', 'paleo_eu', 'Etruscan civilization', 'The non-Indo-European city-builders of Tuscany who taught Rome much of its religion and engineering.'),
    ('italic', 'Italic peoples', 'paleo_eu', 'Italic peoples', 'Samnites, Umbrians, Oscans and the other Italic-speaking peoples of the peninsula before Roman unification.'),
    ('nuragic', 'Nuragic Sardinians', 'paleo_eu', 'Nuragic civilization', 'The tower-builders of Bronze and Iron Age Sardinia.'),
    ('minoan', 'Minoans', 'paleo_eu', 'Minoan civilization', 'The palace civilisation of Bronze Age Crete (Knossos), before the Greeks.'),
    ('thracian', 'Thracians', 'paleo_eu', 'Thracians', 'The Indo-European people of the eastern Balkans, famed horsemen and goldsmiths.'),
    ('dacian', 'Dacians', 'paleo_eu', 'Dacians', 'The Thracian-related people of the Carpathians, conquered by Trajan in 106.'),
    ('illyrian', 'Illyrians', 'paleo_eu', 'Illyrians', 'The peoples of the western Balkans before the Slavs; the Albanians are probably their descendants.'),
    ('albanian', 'Albanian', 'paleo_eu', 'Albanians', 'Speakers of Albanian, an independent branch of Indo-European, in the western Balkans.'),
    ('tocharian', 'Tocharians', 'paleo_eu', 'Tocharians', 'The Indo-European oasis people of the northern Tarim Basin (Kucha, Turfan), known from Buddhist manuscripts.'),
    ('pannonian', 'Pannonians', 'paleo_eu', 'Pannonians', 'The Illyrian-related peoples of the middle Danube, Romanised under the Empire.'),
    # Latin
    ('latin', 'Latin (Roman)', 'latin', 'Ancient Rome', 'The Latin-speaking Romans; Latin became the everyday language of Italy and the western provinces.'),
    ('gallo_roman', 'Gallo-Roman', 'latin', 'Gallo-Roman culture', 'The Latin-speaking population of Roman Gaul, ancestors of the French and Occitans.'),
    ('hispano_roman', 'Hispano-Roman', 'latin', 'Hispania', 'The Latin-speaking population of Roman and Visigothic Spain.'),
    ('romano_african', 'Romano-African', 'latin', 'Africa (Roman province)', 'The Latin-speaking townspeople of Roman North Africa, home of St Augustine.'),
    ('italian', 'Italian', 'latin', 'Italians', 'Speakers of the Italian dialects that grew from Latin after the fall of Rome.'),
    ('french', 'French', 'latin', 'French people', 'The people of northern France (langue d\'oil), and from the 19th century of all France.'),
    ('occitan', 'Occitan', 'latin', 'Occitans', 'The langue d\'oc of southern France (Provence, Languedoc, Gascony, Auvergne) - the language of the troubadours.'),
    ('castilian', 'Castilian (Spanish)', 'latin', 'Spaniards', 'The Castilians of the Reconquista and the Spanish nation that grew from them.'),
    ('catalan', 'Catalan', 'latin', 'Catalans', 'The people of Catalonia, Valencia and the Balearic Islands.'),
    ('galician', 'Galician-Portuguese', 'latin', 'Galician-Portuguese', 'The Romance people of north-west Iberia, from whom Galicians and Portuguese both descend.'),
    ('portuguese', 'Portuguese', 'latin', 'Portuguese people', 'The people of Portugal, from the 12th-century kingdom.'),
    ('andalusi', 'Andalusi', 'latin', 'Al-Andalus', 'The mixed Arabic- and Romance-speaking (Mozarabic) population of Muslim Iberia.'),
    ('romanian', 'Romanian (Vlach)', 'latin', 'Romanians', 'The Romance-speaking people of the lower Danube and Carpathians.'),
    ('romansh', 'Romansh', 'latin', 'Romansh people', 'The Rhaeto-Romance people of the Swiss Alps (Graubunden).'),
    ('mexican', 'Mexican', 'latin', 'Mexicans', 'The Spanish-speaking mestizo and criollo population of Mexico (and of New Spain before it).'),
    ('central_am', 'Central American (Ladino)', 'latin', 'Ladino people', 'The Spanish-speaking mestizo population of Central America.'),
    ('hisp_carib', 'Hispanic Caribbean', 'latin', 'Criollo people', 'The Spanish-speaking creole population of Cuba, Santo Domingo and Puerto Rico.'),
    ('colombian', 'Colombian and Venezuelan', 'latin', 'Colombians', 'The Spanish-speaking mestizo, pardo and criollo population of New Granada and Venezuela.'),
    ('peruvian', 'Peruvian and Ecuadorian (Mestizo)', 'latin', 'Mestizo', 'The Spanish-speaking mestizo and criollo population of the Andean coast and cities.'),
    ('chilean', 'Chilean', 'latin', 'Chileans', 'The Spanish-speaking mestizo population of central Chile.'),
    ('argentine', 'Argentine and Uruguayan', 'latin', 'Argentines', 'The Spanish-speaking people of the River Plate, swelled by Italian and Spanish immigration after 1870.'),
    ('paraguayan', 'Paraguayan', 'latin', 'Paraguayans', 'The bilingual Guarani-Spanish mestizo nation of Paraguay.'),
    ('bolivian', 'Bolivian (Mestizo)', 'latin', 'Bolivians', 'The Spanish-speaking mestizo population of lowland and southern Bolivia.'),
    ('brazilian', 'Brazilian', 'latin', 'Brazilians', 'The Portuguese-speaking population of Brazil, mixing Portuguese, African and Indigenous roots.'),
    ('quebecois', 'French Canadian', 'latin', 'French Canadians', 'The French-speaking people of Quebec and Acadia.'),
    # Germanic
    ('germanic', 'Germanic tribes', 'germanic', 'Germanic peoples', 'The early Germanic peoples of northern Europe: Goths, Vandals, Franks, Saxons, Alemanni and more.'),
    ('norse', 'Norse', 'germanic', 'Norsemen', 'The Scandinavians of the Viking Age.'),
    ('anglo_saxon', 'Anglo-Saxon', 'germanic', 'Anglo-Saxons', 'The Angles, Saxons and Jutes who settled England from the 5th century.'),
    ('english', 'English', 'germanic', 'English people', 'The people of England after the Norman Conquest.'),
    ('scots', 'Lowland Scots', 'germanic', 'Scottish people', 'The Scots-speaking people of the Scottish Lowlands.'),
    ('german', 'German', 'germanic', 'Germans', 'The German-speaking peoples of central Europe.'),
    ('dutch', 'Dutch and Flemish', 'germanic', 'Dutch people', 'The Low Franconian-speaking people of the Netherlands and Flanders.'),
    ('frisian', 'Frisian', 'germanic', 'Frisians', 'The people of the North Sea coast of the Netherlands.'),
    ('danish', 'Danish', 'germanic', 'Danes', 'The people of Denmark and Scania.'),
    ('swedish', 'Swedish', 'germanic', 'Swedes', 'The people of Sweden.'),
    ('norwegian', 'Norwegian', 'germanic', 'Norwegians', 'The people of Norway.'),
    ('icelandic', 'Icelandic', 'germanic', 'Icelanders', 'Descendants of the Norse settlers of Iceland (from 874).'),
    ('anglo_american', 'American (Anglo-American)', 'germanic', 'White Anglo-Saxon Protestants', 'The English-speaking settler society of British North America and the United States.'),
    ('anglo_canadian', 'English Canadian', 'germanic', 'English Canadians', 'The English-speaking population of Canada, founded by Loyalists, Scots and Irish settlers.'),
    ('anglo_aus', 'Australian and New Zealander', 'germanic', 'Anglo-Celtic Australians', 'The settler society of Australia and New Zealand.'),
    ('afrikaner', 'Afrikaans-speaking (Boer and Cape Coloured)', 'germanic', 'Afrikaners', 'The Afrikaans-speaking population of the Cape: Boer settlers and the Cape Coloured community.'),
    # Celtic
    ('celtic', 'Celts', 'celtic', 'Celts', 'The Iron Age Celtic peoples (Hallstatt and La Tene cultures) of central and western Europe.'),
    ('gaulish', 'Gauls', 'celtic', 'Gauls', 'The Celtic peoples of Gaul conquered by Caesar.'),
    ('celtiberian', 'Celtiberians and Lusitanians', 'celtic', 'Celtiberians', 'The Celtic and Celtic-related peoples of central and western Iberia.'),
    ('briton', 'Britons', 'celtic', 'Celtic Britons', 'The Brythonic Celts of Britain.'),
    ('welsh', 'Welsh', 'celtic', 'Welsh people', 'The Britons of Wales.'),
    ('cornish', 'Cornish', 'celtic', 'Cornish people', 'The Britons of Cornwall.'),
    ('breton', 'Breton', 'celtic', 'Bretons', 'The Britons who settled Armorica (Brittany) in the 5th-6th centuries.'),
    ('irish', 'Irish', 'celtic', 'Irish people', 'The Gaels of Ireland.'),
    ('gaels', 'Scottish Gaels', 'celtic', 'Scottish Gaels', 'The Gaelic-speaking people of the Scottish Highlands and Islands.'),
    ('pictish', 'Picts', 'celtic', 'Picts', 'The people of northern and eastern Scotland until the 9th century.'),
    # Hellenic
    ('greek', 'Greek', 'hellenic', 'Greeks', 'The Greek-speaking people, from Mycenae and the polis to Byzantium and modern Greece.'),
    # Slavic
    ('slavic', 'Early Slavs', 'slavic', 'Early Slavs', 'The Slavic peoples of the great migrations (6th-9th centuries).'),
    ('wendish', 'Wends (Polabian Slavs)', 'slavic', 'Polabian Slavs', 'The Slavs between the Elbe and the Oder, Germanised from the 12th century.'),
    ('rus', 'Rus (East Slavic)', 'slavic', 'East Slavs', 'The East Slavs of Kievan Rus, ancestors of Russians, Ukrainians and Belarusians.'),
    ('russian', 'Russian', 'slavic', 'Russians', 'The Russian people, from Muscovy to the steppes, the Urals and Siberia.'),
    ('ruthenian', 'Ruthenian', 'slavic', 'Ruthenians', 'The East Slavs of the Polish-Lithuanian Commonwealth, ancestors of Ukrainians and Belarusians.'),
    ('ukrainian', 'Ukrainian', 'slavic', 'Ukrainians', 'The Ukrainian people.'),
    ('belarusian', 'Belarusian', 'slavic', 'Belarusians', 'The Belarusian people.'),
    ('polish', 'Polish', 'slavic', 'Poles', 'The Polish people.'),
    ('czech', 'Czech', 'slavic', 'Czechs', 'The Czechs of Bohemia and Moravia.'),
    ('slovak', 'Slovak', 'slavic', 'Slovaks', 'The Slovaks of the northern Carpathians.'),
    ('slovene', 'Slovene', 'slavic', 'Slovenes', 'The Slovenes (Carantanians) of the eastern Alps.'),
    ('croatian', 'Croatian', 'slavic', 'Croats', 'The Croats of Croatia and western Bosnia.'),
    ('serbian', 'Serbian', 'slavic', 'Serbs', 'The Serbs of Serbia, Montenegro and eastern Bosnia.'),
    ('bosniak', 'Bosniak', 'slavic', 'Bosniaks', 'The Muslim South Slavs of Bosnia.'),
    ('bulgarian', 'Bulgarian and Macedonian', 'slavic', 'Bulgarians', 'The South Slavs of the eastern Balkans, who absorbed the Turkic Bulgars.'),
    # Baltic
    ('baltic', 'Balts', 'baltic', 'Balts', 'The Baltic-speaking peoples between the Vistula and the Dvina.'),
    ('prussian', 'Old Prussians', 'baltic', 'Old Prussians', 'The Baltic people of Prussia, conquered by the Teutonic Order in the 13th century.'),
    ('lithuanian', 'Lithuanian', 'baltic', 'Lithuanians', 'The Lithuanian people.'),
    ('latvian', 'Latvian', 'baltic', 'Latvians', 'The Latvians (Curonians, Latgalians, Semigallians).'),
    # Uralic
    ('finnic', 'Finnic peoples', 'uralic', 'Finnic peoples', 'The Finnic peoples of the eastern Baltic and northern Russia.'),
    ('finnish', 'Finnish', 'uralic', 'Finns', 'The Finns.'),
    ('estonian', 'Estonian', 'uralic', 'Estonians', 'The Estonians.'),
    ('karelian', 'Karelian', 'uralic', 'Karelians', 'The Karelians, between Finland and Russia.'),
    ('sami', 'Sami', 'uralic', 'Sami people', 'The reindeer-herding people of Lapland.'),
    ('volga_finn', 'Volga Finns and Permians', 'uralic', 'Volga Finns', 'Mordvins, Mari, Udmurts and Komi of the Volga and Urals.'),
    ('magyar', 'Hungarian (Magyar)', 'uralic', 'Hungarians', 'The Magyars, who crossed the Carpathians in 895.'),
    ('ugric_samoyed', 'Khanty, Mansi and Samoyeds', 'uralic', 'Samoyedic peoples', 'The Ugric and Samoyedic reindeer herders of western Siberia (Nenets, Khanty, Mansi, Selkup).'),
    # Caucasian
    ('armenian', 'Armenian', 'caucasian', 'Armenians', 'The Armenian people of the Armenian Highlands.'),
    ('georgian', 'Georgian', 'caucasian', 'Georgians', 'The Kartvelian people of Georgia.'),
    ('circassian', 'Circassian', 'caucasian', 'Circassians', 'The Adyghe of the north-western Caucasus.'),
    ('vainakh', 'Vainakh (Chechen and Ingush)', 'caucasian', 'Vainakh peoples', 'The Chechens and Ingush.'),
    ('dagestani', 'Dagestani peoples', 'caucasian', 'Peoples of Dagestan', 'Avars, Dargins, Lezgins and the many peoples of Dagestan.'),
    ('cauc_albanian', 'Caucasian Albanians', 'caucasian', 'Caucasian Albania', 'The ancient people of what is now Azerbaijan.'),
    ('hurrian', 'Hurrians and Urartians', 'caucasian', 'Hurrians', 'The Hurrians of Mitanni and their Urartian relatives around Lake Van.'),
    # Ancient Near East
    ('sumerian', 'Sumerian', 'ane', 'Sumer', 'The inventors of writing and the city-state, in southern Mesopotamia.'),
    ('elamite', 'Elamite', 'ane', 'Elam', 'The people of Elam in south-western Iran, rivals of Sumer and Babylon.'),
    ('hattic', 'Hattians', 'ane', 'Hattians', 'The original people of central Anatolia, before the Hittites.'),
    ('anatolian', 'Hittites and Luwians', 'ane', 'Anatolian peoples', 'The Indo-European Hittites, Luwians and their successors (Lycians, Lydians) of Anatolia.'),
    ('phrygian', 'Phrygians', 'ane', 'Phrygians', 'The people of King Midas in central Anatolia.'),
    ('egyptian', 'Egyptian (Coptic)', 'afroasiatic', 'Copts', 'The people of the Nile valley from the Pharaohs to the Copts.'),
    # Semitic
    ('akkadian', 'Akkadian (Babylonian and Assyrian)', 'semitic', 'Akkadian Empire', 'The Semitic people of Mesopotamia: Akkad, Babylon and Assyria.'),
    ('amorite', 'Amorites', 'semitic', 'Amorites', 'The Semitic people of Bronze Age Syria.'),
    ('canaanite', 'Canaanite and Phoenician', 'semitic', 'Canaanites', 'The Canaanites and Phoenicians of the Levant coast and the Punic colonies (Carthage).'),
    ('punic', 'Punic (Carthaginian)', 'semitic', 'Punic people', 'The Phoenician people of Carthage and its colonies.'),
    ('aramaic', 'Aramaean and Syriac', 'semitic', 'Arameans', 'The Aramaic-speaking people of Syria and Mesopotamia, from the Aramaean kingdoms to the Syriac Christians.'),
    ('jewish', 'Jewish (Hebrew)', 'semitic', 'Jews', 'The Israelites and the Jewish people.'),
    ('arab', 'Arab', 'semitic', 'Arabs', 'The Arabs of Arabia and the lands they Arabised after the 7th century.'),
    ('south_arabian', 'South Arabian (Sabaean and Himyarite)', 'semitic', 'Old South Arabian', 'The incense kingdoms of Yemen: Saba, Qataban, Hadramawt and Himyar.'),
    ('maltese', 'Maltese', 'semitic', 'Maltese people', 'The Maltese, whose language grew from Siculo-Arabic.'),
    ('habesha', 'Habesha (Amhara and Tigray)', 'semitic', 'Habesha peoples', 'The Semitic-speaking Christian highlanders of Ethiopia and Eritrea, heirs of Aksum.'),
    # Afroasiatic
    ('berber', 'Berber (Amazigh)', 'afroasiatic', 'Berbers', 'The indigenous people of North Africa and the Sahara.'),
    ('tuareg', 'Tuareg', 'afroasiatic', 'Tuareg people', 'The Berber camel-nomads of the central Sahara.'),
    ('beja', 'Beja', 'afroasiatic', 'Beja people', 'The Cushitic nomads of the Red Sea hills.'),
    ('cushitic', 'Cushitic peoples', 'afroasiatic', 'Cushitic peoples', 'The Cushitic-speaking peoples of the Horn of Africa (Agaw, Sidama and others).'),
    ('somali', 'Somali', 'afroasiatic', 'Somalis', 'The Somali people.'),
    ('oromo', 'Oromo', 'afroasiatic', 'Oromo people', 'The Oromo, who spread across southern Ethiopia in the 16th century.'),
    ('afar', 'Afar', 'afroasiatic', 'Afar people', 'The Afar of the Danakil.'),
    ('hausa', 'Hausa', 'afroasiatic', 'Hausa people', 'The Hausa city-states of northern Nigeria and their people.'),
    # Iranian
    ('iranian', 'Early Iranians', 'iranian', 'Iranian peoples', 'The early Iranian-speaking peoples of the Iranian plateau and Central Asia.'),
    ('median', 'Medes', 'iranian', 'Medes', 'The Medes of north-western Iran.'),
    ('persian', 'Persian', 'iranian', 'Persians', 'The Persians, from Cyrus the Great to modern Iran.'),
    ('parthian', 'Parthian', 'iranian', 'Parthians', 'The Parni / Parthians of north-eastern Iran.'),
    ('scythian', 'Scythians and Saka', 'iranian', 'Scythians', 'The Iranian horse nomads of the Eurasian steppe.'),
    ('sarmatian', 'Sarmatians and Alans', 'iranian', 'Sarmatians', 'The Iranian nomads who followed the Scythians on the steppe; the Alans of the Caucasus.'),
    ('ossetian', 'Ossetian (Alan)', 'iranian', 'Ossetians', 'The Ossetians, heirs of the Alans, in the central Caucasus.'),
    ('sogdian', 'Sogdian', 'iranian', 'Sogdians', 'The merchant people of Samarkand and Bukhara, traders of the Silk Road.'),
    ('bactrian', 'Bactrian', 'iranian', 'Bactria', 'The people of Bactria (northern Afghanistan).'),
    ('khwarezmian', 'Khwarezmian', 'iranian', 'Khwarazm', 'The people of the Amu Darya delta.'),
    ('tajik', 'Tajik', 'iranian', 'Tajiks', 'The Persian-speaking people of Central Asia and Afghanistan.'),
    ('kurdish', 'Kurdish', 'iranian', 'Kurds', 'The Kurds of the Zagros and Taurus mountains.'),
    ('lur', 'Lur and Bakhtiari', 'iranian', 'Lurs', 'The Lurs and Bakhtiari of the Zagros.'),
    ('pashtun', 'Pashtun', 'iranian', 'Pashtuns', 'The Pashtuns of southern and eastern Afghanistan and north-west Pakistan.'),
    ('baloch', 'Baloch', 'iranian', 'Baloch people', 'The Baloch of the deserts between Iran and the Indus.'),
    ('azeri_iranian', 'Azari (Old Azeri)', 'iranian', 'Old Azeri language', 'The Iranian-speaking people of Azerbaijan before the Turkic settlement.'),
    # Turkic
    ('xiongnu', 'Xiongnu', 'turkic', 'Xiongnu', 'The nomad confederation of the Mongolian steppe that fought Han China.'),
    ('hunnic', 'Huns', 'turkic', 'Huns', 'The steppe nomads who burst into Europe in 370 under leaders like Attila.'),
    ('gokturk', 'Gokturks and early Turks', 'turkic', 'Gokturks', 'The first Turkic khaganate (552) and the Turkic tribes of the steppe.'),
    ('avar', 'Pannonian Avars', 'turkic', 'Pannonian Avars', 'The steppe nomads who ruled the Carpathian Basin (568-796).'),
    ('bulgar', 'Bulgars', 'turkic', 'Bulgars', 'The Turkic Bulgars of the Volga and the Danube.'),
    ('khazar', 'Khazar', 'turkic', 'Khazars', 'The Khazar khaganate of the Volga and Caspian steppe.'),
    ('uyghur', 'Uyghur', 'turkic', 'Uyghurs', 'The Uyghurs: khaganate in Mongolia (744-840), then the oasis people of the Tarim Basin.'),
    ('kipchak', 'Kipchaks and Cumans', 'turkic', 'Cumans', 'The Kipchak-Cuman nomads of the western steppe (11th-13th centuries).'),
    ('oghuz', 'Oghuz Turks', 'turkic', 'Oghuz Turks', 'The Oghuz tribes of the Aral steppe, from whom the Seljuks and Ottomans came.'),
    ('turkish', 'Turkish', 'turkic', 'Turkish people', 'The Turks of Anatolia and Rumelia.'),
    ('azerbaijani', 'Azerbaijani', 'turkic', 'Azerbaijanis', 'The Turkic people of Azerbaijan and north-west Iran.'),
    ('turkmen', 'Turkmen', 'turkic', 'Turkmens', 'The Turkmen of the Karakum.'),
    ('tatar', 'Tatar', 'turkic', 'Tatars', 'The Volga, Crimean and Siberian Tatars, heirs of the Golden Horde.'),
    ('nogai', 'Nogai and Crimean Tatars', 'turkic', 'Nogais', 'The Nogai Horde and Crimean Tatars of the Pontic and Caspian steppe.'),
    ('bashkir', 'Bashkir', 'turkic', 'Bashkirs', 'The Bashkirs of the southern Urals.'),
    ('chuvash', 'Chuvash', 'turkic', 'Chuvash people', 'The Chuvash, last speakers of the Bulgar branch of Turkic.'),
    ('kazakh', 'Kazakh', 'turkic', 'Kazakhs', 'The Kazakh nomads of the great steppe (from the 15th century).'),
    ('kyrgyz', 'Kyrgyz', 'turkic', 'Kyrgyz people', 'The Kyrgyz, from the Yenisei to the Tian Shan.'),
    ('uzbek', 'Uzbek', 'turkic', 'Uzbeks', 'The Uzbeks of Transoxiana (from c. 1500).'),
    ('chagatai', 'Chagatai Turks', 'turkic', 'Chagatai language', 'The Turkic people of Transoxiana and Ferghana before the Uzbeks.'),
    ('yakut', 'Yakut (Sakha)', 'turkic', 'Yakuts', 'The Sakha horse- and cattle-breeders of the Lena valley.'),
    ('tuvan', 'Tuvan and Altai', 'turkic', 'Tuvans', 'The Turkic peoples of the Sayan and Altai mountains.'),
    # Mongolic / Tungusic
    ('xianbei', 'Xianbei and Rouran', 'mongolic', 'Xianbei', 'The proto-Mongolic peoples who followed the Xiongnu on the steppe.'),
    ('khitan', 'Khitan', 'mongolic', 'Khitan people', 'The Khitans of the Liao dynasty (916-1125).'),
    ('mongol', 'Mongol', 'mongolic', 'Mongols', 'The Mongols.'),
    ('oirat', 'Oirat and Kalmyk', 'mongolic', 'Oirats', 'The western Mongols: Dzungars and the Kalmyks of the Volga.'),
    ('buryat', 'Buryat', 'mongolic', 'Buryats', 'The Buryat Mongols around Lake Baikal.'),
    ('jurchen', 'Jurchen and Manchu', 'mongolic', 'Manchu people', 'The Tungusic Mohe, Jurchen and Manchu peoples of Manchuria.'),
    ('evenki', 'Evenki and Tungusic peoples', 'mongolic', 'Evenks', 'The Evenki, Evens and other Tungusic reindeer people of eastern Siberia.'),
    # Arctic / Paleo-Siberian
    ('paleo_siberian', 'Chukchi, Koryak and Paleo-Siberians', 'arctic', 'Paleosiberian languages', 'The Chukchi, Koryaks, Itelmens, Yukaghirs and Nivkhs of far north-east Asia.'),
    ('inuit', 'Inuit and Yupik', 'arctic', 'Inuit', 'The Arctic peoples from Alaska to Greenland.'),
    ('ainu', 'Ainu', 'japonic', 'Ainu people', 'The indigenous people of Hokkaido, Sakhalin and the Kurils.'),
    # Indo-Aryan
    ('vedic', 'Vedic Indo-Aryans', 'indo_aryan', 'Indo-Aryan peoples', 'The Indo-Aryan tribes of the Rigveda, in the Punjab and Ganges plain.'),
    ('indo_aryan', 'Indo-Aryan (Prakrit)', 'indo_aryan', 'Indo-Aryan peoples', 'The Indo-Aryan-speaking peoples of northern India in the Maurya, Kushan and Gupta eras.'),
    ('hindustani', 'Hindustani', 'indo_aryan', 'Hindustani people', 'The Hindi-Urdu speaking people of the Ganges plain and central India.'),
    ('rajasthani', 'Rajasthani', 'indo_aryan', 'Rajasthani people', 'The people of Rajasthan (Rajputana).'),
    ('punjabi', 'Punjabi', 'indo_aryan', 'Punjabis', 'The people of the Punjab.'),
    ('sindhi', 'Sindhi', 'indo_aryan', 'Sindhis', 'The people of Sindh on the lower Indus.'),
    ('gujarati', 'Gujarati', 'indo_aryan', 'Gujarati people', 'The people of Gujarat.'),
    ('marathi', 'Marathi', 'indo_aryan', 'Marathi people', 'The people of Maharashtra and the Deccan.'),
    ('bengali', 'Bengali', 'indo_aryan', 'Bengalis', 'The people of Bengal.'),
    ('odia', 'Odia', 'indo_aryan', 'Odia people', 'The people of Odisha (Kalinga).'),
    ('assamese', 'Assamese', 'indo_aryan', 'Assamese people', 'The people of the Brahmaputra valley.'),
    ('nepali', 'Nepali (Khas)', 'indo_aryan', 'Nepalis', 'The people of Nepal.'),
    ('kashmiri', 'Kashmiri and Dardic', 'indo_aryan', 'Dardic peoples', 'The Kashmiris and the Dardic peoples of the Hindu Kush and Karakoram.'),
    ('sinhalese', 'Sinhalese', 'indo_aryan', 'Sinhalese people', 'The Sinhalese of Sri Lanka.'),
    ('gandharan', 'Gandharan', 'indo_aryan', 'Gandhara', 'The people of Gandhara (Peshawar valley and Swat).'),
    # Dravidian
    ('harappan', 'Harappan (Indus Valley)', 'dravidian', 'Indus Valley Civilisation', 'The people of the Indus cities (c. 3300-1800 BCE); their language is unknown, perhaps Dravidian.'),
    ('dravidian', 'Dravidian peoples', 'dravidian', 'Dravidian peoples', 'The Dravidian-speaking peoples of southern India.'),
    ('tamil', 'Tamil', 'dravidian', 'Tamils', 'The Tamils of the far south of India and northern Sri Lanka.'),
    ('telugu', 'Telugu', 'dravidian', 'Telugu people', 'The Telugu people of Andhra.'),
    ('kannada', 'Kannada', 'dravidian', 'Kannadigas', 'The Kannada people of Karnataka.'),
    ('malayali', 'Malayali', 'dravidian', 'Malayali', 'The people of Kerala.'),
    ('gond', 'Gond and Adivasi peoples', 'dravidian', 'Adivasi', 'The tribal (Adivasi) peoples of the central Indian forests: Gonds, Mundas, Santals and others.'),
    # Sinitic
    ('huaxia', 'Huaxia (early Chinese)', 'sinitic', 'Huaxia', 'The early Chinese of the Yellow River (Shang and Zhou).'),
    ('han', 'Han Chinese', 'sinitic', 'Han Chinese', 'The Han Chinese, named after the Han dynasty (206 BCE-220 CE).'),
    # Tibeto-Burman
    ('tibetan', 'Tibetan', 'tibeto_burman', 'Tibetan people', 'The Tibetans.'),
    ('burmese', 'Burmese (Bamar)', 'tibeto_burman', 'Bamar people', 'The Bamar of the Irrawaddy valley.'),
    ('pyu', 'Pyu', 'tibeto_burman', 'Pyu city-states', 'The Pyu city-states of upper Burma (c. 200 BCE-1050 CE).'),
    ('yi_bai', 'Yi and Bai (Nanzhao)', 'tibeto_burman', 'Nanzhao', 'The peoples of Yunnan: Bai, Yi and the kingdoms of Nanzhao and Dali.'),
    ('hill_tb', 'Naga, Kachin, Chin and hill peoples', 'tibeto_burman', 'Kachin people', 'The Tibeto-Burman hill peoples between India, Burma and China.'),
    ('karen', 'Karen', 'tibeto_burman', 'Karen people', 'The Karen of eastern Burma.'),
    ('qiang', 'Qiang and Tangut', 'tibeto_burman', 'Western Xia', 'The Qiang and Tanguts of the Gansu corridor (Western Xia, 1038-1227).'),
    # Tai
    ('baiyue', 'Baiyue', 'tai', 'Baiyue', 'The "Hundred Yue" peoples of southern China before Han settlement.'),
    ('zhuang', 'Zhuang', 'tai', 'Zhuang people', 'The Zhuang of Guangxi, the largest minority of China.'),
    ('thai', 'Thai (Siamese)', 'tai', 'Thai people', 'The Siamese of the Chao Phraya basin.'),
    ('lao', 'Lao', 'tai', 'Lao people', 'The Lao of the Mekong valley and Isan.'),
    ('shan', 'Shan and Tai Yuan', 'tai', 'Shan people', 'The Shan and northern Thai (Lanna) Tai peoples.'),
    ('miao', 'Miao (Hmong) and Yao', 'tai', 'Miao people', 'The Hmong-Mien hill peoples of Guizhou and the south-west.'),
    # Austroasiatic
    ('viet', 'Vietnamese (Kinh)', 'austroasiatic', 'Vietnamese people', 'The Vietnamese of the Red River delta and, after the Nam tien, of the whole coast.'),
    ('khmer', 'Khmer', 'austroasiatic', 'Khmer people', 'The Khmer of Cambodia and the Mekong.'),
    ('mon', 'Mon', 'austroasiatic', 'Mon people', 'The Mon of lower Burma and Dvaravati Thailand.'),
    ('munda', 'Munda and Khasi', 'austroasiatic', 'Munda people', 'The Austroasiatic peoples of eastern India.'),
    # Austronesian
    ('formosan', 'Taiwanese indigenous', 'austronesian', 'Taiwanese indigenous peoples', 'The Austronesian peoples of Taiwan, homeland of the Austronesian expansion.'),
    ('malay', 'Malay', 'austronesian', 'Malays', 'The Malays of the peninsula, Sumatra and the Borneo coasts.'),
    ('javanese', 'Javanese', 'austronesian', 'Javanese people', 'The Javanese of central and eastern Java.'),
    ('sundanese', 'Sundanese', 'austronesian', 'Sundanese people', 'The Sundanese of western Java.'),
    ('balinese', 'Balinese', 'austronesian', 'Balinese people', 'The Hindu Balinese.'),
    ('acehnese', 'Acehnese', 'austronesian', 'Acehnese people', 'The people of Aceh.'),
    ('batak', 'Batak and Minangkabau', 'austronesian', 'Batak people', 'The Batak of the Toba highlands and the Minangkabau of west Sumatra.'),
    ('bugis', 'Bugis and Makassar', 'austronesian', 'Bugis', 'The seafaring Bugis and Makassarese of south Sulawesi.'),
    ('dayak', 'Dayak and Borneo peoples', 'austronesian', 'Dayak people', 'The inland peoples of Borneo.'),
    ('e_indonesian', 'Eastern Indonesian peoples', 'austronesian', 'Lesser Sunda Islands', 'The peoples of Sulawesi, the Moluccas and the Lesser Sundas.'),
    ('tagalog', 'Tagalog and Luzon peoples', 'austronesian', 'Tagalog people', 'The Tagalog, Ilocano, Kapampangan and other peoples of Luzon.'),
    ('visayan', 'Visayan', 'austronesian', 'Visayans', 'The Visayans of the central Philippines.'),
    ('moro', 'Moro', 'austronesian', 'Moro people', 'The Muslim peoples of Mindanao and Sulu.'),
    ('cham', 'Cham', 'austronesian', 'Cham people', 'The Cham of Champa on the central Vietnamese coast.'),
    ('malagasy', 'Malagasy', 'austronesian', 'Malagasy people', 'The people of Madagascar, of Austronesian and Bantu descent.'),
    ('polynesian', 'Polynesian', 'austronesian', 'Polynesians', 'The Polynesian navigators of the Pacific: Hawaiians, Tongans, Samoans, Tahitians and others.'),
    ('maori', 'Maori', 'austronesian', 'Maori people', 'The Polynesian people of New Zealand (from c. 1300).'),
    ('melanesian', 'Melanesian', 'austronesian', 'Melanesians', 'The peoples of the Melanesian islands (Fiji, Vanuatu, Solomons, New Caledonia).'),
    # Japanese / Korean
    ('jomon', 'Jomon', 'japonic', 'Jomon period', 'The hunter-fisher potters of prehistoric Japan.'),
    ('japanese', 'Japanese', 'japonic', 'Japanese people', 'The Japanese (Yamato) people.'),
    ('ryukyuan', 'Ryukyuan', 'japonic', 'Ryukyuan people', 'The people of the Ryukyu Islands (Okinawa).'),
    ('korean', 'Korean', 'japonic', 'Koreans', 'The Korean people.'),
    ('emishi', 'Emishi', 'japonic', 'Emishi', 'The people of northern Honshu outside Yamato rule until the 9th century.'),
    # West Africa
    ('w_african', 'West African peoples', 'w_african', 'Niger-Congo languages', 'The farming peoples of the West African savanna and forest.'),
    ('mande', 'Mande (Mandinka, Bambara, Soninke)', 'w_african', 'Mandé peoples', 'The Mande peoples of the empires of Ghana and Mali.'),
    ('wolof', 'Wolof and Serer', 'w_african', 'Wolof people', 'The Wolof and Serer of Senegambia.'),
    ('fula', 'Fula (Fulani)', 'w_african', 'Fula people', 'The Fula pastoralists and their imamates of Futa Toro, Futa Jallon, Macina and Adamawa.'),
    ('mossi', 'Mossi and Gur peoples', 'w_african', 'Mossi people', 'The Mossi kingdoms and the Gur-speaking peoples of the Volta basin.'),
    ('akan', 'Akan', 'w_african', 'Akan people', 'The Akan (Asante, Fante) of the forest gold country.'),
    ('gbe', 'Ewe and Fon (Gbe)', 'w_african', 'Gbe peoples', 'The Ewe, Fon and Aja of the "Slave Coast" (Dahomey).'),
    ('yoruba', 'Yoruba', 'w_african', 'Yoruba people', 'The Yoruba of Ife and Oyo.'),
    ('edo', 'Edo (Benin)', 'w_african', 'Edo people', 'The Edo people of the Kingdom of Benin.'),
    ('igbo', 'Igbo', 'w_african', 'Igbo people', 'The Igbo of south-eastern Nigeria.'),
    ('cross_river', 'Ibibio, Efik and Ijaw', 'w_african', 'Ibibio people', 'The peoples of the Niger delta and Cross River.'),
    ('middle_belt', 'Middle Belt peoples (Nupe, Tiv, Jukun)', 'w_african', 'Middle Belt', 'The many peoples of central Nigeria.'),
    ('kru', 'Kru, Mende and Atlantic coast peoples', 'w_african', 'Kru people', 'The peoples of the Upper Guinea coast (Sierra Leone, Liberia, Ivory Coast).'),
    ('ubangian', 'Ubangian peoples (Zande, Banda, Gbaya)', 'w_african', 'Ubangian languages', 'The peoples of the Central African savanna.'),
    # Bantu
    ('bantu', 'Bantu peoples', 'bantu', 'Bantu peoples', 'The Bantu-speaking farmers who spread from Cameroon across central, eastern and southern Africa.'),
    ('kongo', 'Kongo', 'bantu', 'Kongo people', 'The Bakongo of the Kingdom of Kongo.'),
    ('mbundu', 'Mbundu and Ovimbundu', 'bantu', 'Ovimbundu', 'The peoples of the Ndongo kingdom and the Angolan plateau.'),
    ('luba_lunda', 'Luba and Lunda', 'bantu', 'Luba people', 'The Luba and Lunda empires of the southern savanna.'),
    ('congo_bantu', 'Congo Basin peoples (Mongo, Kuba)', 'bantu', 'Mongo people', 'The forest peoples of the central Congo basin.'),
    ('fang', 'Fang and Gabon peoples', 'bantu', 'Fang people', 'The Fang and other peoples of Gabon, Equatorial Guinea and south Cameroon.'),
    ('great_lakes', 'Great Lakes Bantu (Ganda, Rwanda, Rundi)', 'bantu', 'Great Lakes Bantu', 'The kingdoms of Buganda, Bunyoro, Rwanda and Burundi.'),
    ('e_bantu', 'East African Bantu (Kikuyu, Sukuma, Nyamwezi)', 'bantu', 'Kikuyu people', 'The Bantu farmers of the Kenyan and Tanzanian interior.'),
    ('swahili', 'Swahili', 'bantu', 'Swahili people', 'The Muslim merchant towns of the east African coast (Kilwa, Mombasa, Zanzibar).'),
    ('shona', 'Shona', 'bantu', 'Shona people', 'The Shona of Great Zimbabwe and Mutapa.'),
    ('nguni', 'Nguni (Zulu, Xhosa, Swazi)', 'bantu', 'Nguni people', 'The Nguni peoples of south-east Africa, including the Zulu and Xhosa.'),
    ('sotho', 'Sotho-Tswana', 'bantu', 'Sotho-Tswana peoples', 'The Sotho and Tswana of the highveld.'),
    ('maravi', 'Maravi and Makua (Chewa, Yao)', 'bantu', 'Chewa people', 'The peoples of Malawi and northern Mozambique.'),
    ('bemba', 'Bemba and Zambian peoples', 'bantu', 'Bemba people', 'The Bemba, Tonga and Lozi of Zambia.'),
    ('herero', 'Herero and Ovambo', 'bantu', 'Ovambo people', 'The Bantu peoples of Namibia.'),
    ('tsonga', 'Tsonga and Mozambique peoples', 'bantu', 'Tsonga people', 'The Tsonga, Sena and Ndau of southern Mozambique.'),
    ('pygmy', 'Central African foragers (Batwa)', 'bantu', 'African Pygmies', 'The forest hunter-gatherers of the Congo basin.'),
    # Nilo-Saharan
    ('nubian', 'Nubian', 'nilo', 'Nubians', 'The Nubians of the middle Nile: Kerma, Kush, Makuria and Alodia.'),
    ('kanuri', 'Kanuri', 'nilo', 'Kanuri people', 'The Kanuri of Kanem-Bornu around Lake Chad.'),
    ('songhai', 'Songhai and Zarma', 'nilo', 'Songhai people', 'The Songhai of Gao and the Niger bend.'),
    ('nilotic', 'Nilotic peoples (Dinka, Nuer, Luo, Maasai)', 'nilo', 'Nilotic peoples', 'The cattle peoples of the upper Nile and the Rift Valley.'),
    ('sudanic', 'Central Sudanic peoples (Sara, Fur)', 'nilo', 'Central Sudanic languages', 'The Fur of Darfur, the Sara of southern Chad and their neighbours.'),
    ('toubou', 'Toubou', 'nilo', 'Toubou people', 'The Toubou of Tibesti.'),
    ('sudanese_arab', 'Sudanese Arab', 'semitic', 'Sudanese Arabs', 'The Arabic-speaking peoples of the Sudan (Ja\'alin, Baggara, Shaigiya and others).'),
    ('chadian_arab', 'Chadian Arab (Baggara)', 'semitic', 'Baggara Arabs', 'The Arab cattle nomads of the Sahel belt.'),
    ('moor', 'Moors (Hassaniya Arabs)', 'semitic', 'Moors', 'The Arab-Berber Bidhan of the western Sahara.'),
    # Khoisan
    ('khoisan', 'Khoisan (Khoikhoi and San)', 'khoisan', 'Khoisan', 'The original herders and hunter-gatherers of southern Africa.'),
    # North America
    ('dene', 'Dene (Athabaskan)', 'n_american', 'Dene', 'The Athabaskan-speaking peoples of the subarctic forests.'),
    ('apache', 'Apache and Navajo', 'n_american', 'Southern Athabaskan languages', 'The southern Athabaskans who moved into the Southwest c. 1400-1500.'),
    ('algonquian', 'Algonquian peoples', 'n_american', 'Algonquian peoples', 'The Algonquian peoples of the north-east, Great Lakes and northern plains (Cree, Ojibwe, Lenape, Powhatan, Blackfoot).'),
    ('iroquoian', 'Iroquoian peoples', 'n_american', 'Iroquoian peoples', 'The Haudenosaunee (Iroquois), Huron and Cherokee.'),
    ('siouan', 'Siouan peoples', 'n_american', 'Siouan-speaking peoples', 'The Lakota, Dakota, Osage, Crow and other Siouan peoples of the Plains.'),
    ('muskogean', 'Muskogean peoples', 'n_american', 'Muskogean languages', 'The Creek, Choctaw, Chickasaw and Seminole of the south-east.'),
    ('mississippian', 'Mississippian mound-builders', 'n_american', 'Mississippian culture', 'The maize-farming chiefdoms of the Mississippi valley (Cahokia, c. 800-1600).'),
    ('caddoan', 'Caddoan peoples', 'n_american', 'Caddoan languages', 'The Caddo, Wichita and Pawnee.'),
    ('pueblo', 'Pueblo and Southwest peoples', 'n_american', 'Puebloans', 'The Ancestral Puebloans, Hohokam and Pueblo peoples of the desert Southwest.'),
    ('numic', 'Great Basin peoples (Shoshone, Ute, Comanche)', 'n_american', 'Numic languages', 'The Uto-Aztecan peoples of the Great Basin and southern Plains.'),
    ('californian', 'California peoples', 'n_american', 'Indigenous peoples of California', 'The many peoples of California.'),
    ('nw_coast', 'Pacific Northwest peoples', 'n_american', 'Indigenous peoples of the Pacific Northwest Coast', 'The salmon and cedar cultures of the north-west coast (Tlingit, Haida, Kwakwakawakw, Salish).'),
    ('plateau', 'Plateau peoples', 'n_american', 'Plateau Indians', 'The Nez Perce and other peoples of the Columbia plateau.'),
    ('aridoamerican', 'Chichimec and Aridoamerican peoples', 'n_american', 'Aridoamerica', 'The peoples of northern Mexico (Chichimecs, Yaqui, Tarahumara).'),
    ('african_american', 'African American', 'creole', 'African Americans', 'Descendants of enslaved Africans in the United States; a majority in South Carolina, Mississippi and Louisiana for long periods.'),
    # Mesoamerica
    ('olmec', 'Olmec', 'mesoamerican', 'Olmecs', 'The first great Mesoamerican civilisation (c. 1500-400 BCE) on the Gulf coast.'),
    ('maya', 'Maya', 'mesoamerican', 'Maya peoples', 'The Maya of Yucatan, Chiapas and Guatemala.'),
    ('otomanguean', 'Zapotec, Mixtec and Otomi', 'mesoamerican', 'Oto-Manguean languages', 'The Oto-Manguean peoples of Oaxaca and central Mexico (Monte Alban, Teotihuacan\'s neighbours).'),
    ('nahua', 'Nahua (Aztec)', 'mesoamerican', 'Nahuas', 'The Nahuatl-speaking peoples of central Mexico: Toltecs, Mexica (Aztecs) and Tlaxcalans.'),
    ('purepecha', 'Purepecha (Tarascan)', 'mesoamerican', 'Purépecha', 'The Tarascan state of Michoacan, never conquered by the Aztecs.'),
    ('lenca', 'Lenca, Pipil and isthmus peoples', 'mesoamerican', 'Lenca people', 'The peoples of Honduras, El Salvador and Nicaragua.'),
    # Andes
    ('chavin', 'Chavin and early Andeans', 'andean', 'Chavín culture', 'The early Andean civilisations (Chavin, Paracas, Nazca).'),
    ('quechua', 'Quechua', 'andean', 'Quechua people', 'The Quechua-speaking people of the Andes, spread by the Inca empire.'),
    ('aymara', 'Aymara', 'andean', 'Aymara people', 'The Aymara of the Titicaca basin, heirs of Tiwanaku.'),
    ('mochica', 'Moche and Chimu', 'andean', 'Chimú culture', 'The north-coast civilisations of Peru (Moche c. 100-800, Chimu c. 900-1470).'),
    ('muisca', 'Muisca and Chibchan peoples', 'andean', 'Muisca', 'The Muisca of the Bogota highlands, source of the El Dorado legend.'),
    ('mapuche', 'Mapuche', 'andean', 'Mapuche', 'The Mapuche of southern Chile, unconquered until the 1880s.'),
    ('diaguita', 'Diaguita and Andean Argentines', 'andean', 'Diaguita', 'The peoples of north-west Argentina.'),
    # Lowland South America
    ('tupi', 'Tupi-Guarani', 's_american', 'Tupi people', 'The Tupi and Guarani peoples of the Brazilian coast and the Parana.'),
    ('arawak', 'Arawak and Taino', 's_american', 'Arawak peoples', 'The Arawak peoples of the Amazon and the Caribbean (Taino).'),
    ('carib', 'Carib peoples', 's_american', 'Kalina people', 'The Carib peoples of the Guianas and the Lesser Antilles.'),
    ('ge', 'Ge and Brazilian highland peoples', 's_american', 'Gê peoples', 'The Ge-speaking peoples of the Brazilian plateau.'),
    ('amazonian', 'Amazonian peoples', 's_american', 'Indigenous peoples in Brazil', 'The many peoples of the Amazon rainforest.'),
    ('chaco', 'Chaco peoples', 's_american', 'Gran Chaco', 'The Wichi, Qom and other peoples of the Gran Chaco.'),
    ('patagonian', 'Tehuelche and Patagonian peoples', 's_american', 'Tehuelche people', 'The Tehuelche, Selknam and other peoples of Patagonia and the Pampas.'),
    ('afro_carib', 'Afro-Caribbean', 'creole', 'Afro-Caribbean people', 'Descendants of enslaved Africans in the Caribbean and the Guianas (Haitians, Jamaicans and others).'),
    # Oceania
    ('aboriginal', 'Aboriginal Australian', 'oceanian', 'Aboriginal Australians', 'The peoples of Australia, with over 60,000 years of continuous culture.'),
    ('papuan', 'Papuan peoples', 'oceanian', 'Papuan people', 'The peoples of New Guinea.'),
    ('indo_fijian', 'Indo-Fijian', 'indo_aryan', 'Indo-Fijians', 'Descendants of Indian indentured labourers in Fiji, the majority from the 1940s to the 1980s.'),
    ('hawaii_japanese', 'Japanese Hawaiian', 'japonic', 'Japanese in Hawaii', 'Japanese plantation migrants, the largest group in Hawaii c. 1900-1950.'),
]

# colours: hue/sat from the family, lightness and small hue shifts cycle through the family's members
_L = [0.50, 0.37, 0.63, 0.44, 0.57, 0.31, 0.69, 0.47, 0.40, 0.60]
_DH = [0, 9, -9, 16, -16, 4, -4, 12, -12, 20]
_seen = {}
FAITHS = []
for cid, n, fam, w, d in C:
    k = _seen.get(fam, 0); _seen[fam] = k + 1
    h, s = _FAMH[fam]
    r, g, b = colorsys.hls_to_rgb(((h + _DH[k % 10]) % 360) / 360, _L[k % 10], min(0.85, s + (0.08 if k % 3 == 1 else 0)))
    FAITHS.append(dict(id=cid, n=n, fam=fam, c='#%02x%02x%02x' % (round(r * 255), round(g * 255), round(b * 255)), w=w, d=d))
FAITHS.append(dict(id='na', n='n/a (unknown or uncertain)', fam='na', c='#6f6c66', d="No category is shown here: the population is unknown, too mixed or too disputed to name one group, or the land was uninhabited. Every n/a area is listed in the atlas's n/a register."))
_ids = [f['id'] for f in FAITHS]
assert len(set(_ids)) == len(_ids), 'duplicate culture id'

RULES = []
def R(y0, y1, cul, **where): RULES.append((y0, y1, cul, where))
E = 99999
B = -999999

from religion_rules import (ARABIA, MAGHREB, ANDES, STEPPE_RUS, STEPPE_UKR, RUS_W, RUS_C, RUS_N, RUS_VOLGA, RUS_URAL, RUS_SSIB, RUS_FE,
                            MEX_N, MEX_CORE, JAVA, SUMATRA_S, MUSLIM_PHL)

# ------------------------------------------------------------------ shared areas
SCOTLAND = [[-7.9, 54.62], [-5.2, 54.75], [-3.05, 54.95], [-2.6, 55.15], [-2.05, 55.62], [-1.75, 55.82], [-0.5, 61.5], [-9, 61.5], [-9, 54.62]]
HIGHLANDS = [[-8.5, 55.25], [-5.1, 55.75], [-4.65, 56.08], [-3.85, 56.4], [-3.05, 56.85], [-2.75, 57.2], [-3.35, 57.55], [-4.15, 57.62], [-3.85, 58.25],
             [-3.25, 58.62], [-3.4, 58.9], [-8.5, 58.9]]
NORTHERN_ISLES = [-3.5, 58.6, -0.5, 61.0]
WALES = [-5.5, 51.3, -2.65, 53.45]
CORNWALL = [-6.5, 49.8, -4.25, 50.95]
N_IRELAND = [-8.2, 53.95, -5.3, 55.35]
OCCITAN = ['Pyrénées-Atlantiques', 'Landes', 'Gironde', 'Lot-et-Garonne', 'Gers', 'Hautes-Pyrénées', 'Haute-Garonne', 'Ariège', 'Tarn-et-Garonne', 'Tarn',
           'Aude', 'Hérault', 'Gard', 'Lozère', 'Aveyron', 'Lot', 'Dordogne', 'Corrèze', 'Haute-Vienne', 'Creuse', 'Cantal', 'Puy-de-Dôme', 'Haute-Loire',
           'Ardèche', 'Drôme', 'Vaucluse', 'Bouches-du-Rhône', 'Var', 'Alpes-Maritimes', 'Alpes-de-Haute-Provence', 'Hautes-Alpes', 'Charente']
BRETON = ['Finistère', 'Morbihan', "Côtes-d'Armor"]
ALSACE = ['Bas-Rhin', 'Haute-Rhin', 'Moselle']
CORSICA = ['Haute-Corse', 'Corse-du-Sud']
ETRURIA = ['Firenze', 'Pisa', 'Lucca', 'Livorno', 'Siena', 'Arezzo', 'Grosseto', 'Pistoia', 'Prato', 'Massa-Carrara', 'Viterbo', 'Perugia', 'Terni']
MAGNA_GRAECIA = ['Reggio Calabria', 'Crotene', 'Catanzaro', 'Vibo Valentia', 'Cosenza', 'Taranto', 'Napoli', 'Siracusa', 'Catania', 'Messina', 'Ragusa',
                 'Agrigento', 'Caltanissetta', 'Enna']
SARDINIA = ['Carbonia-Iglesias', 'Sassari', 'Nuoro', 'Olbia-Tempio', 'Oristrano', 'Medio Campidano', 'Cagliari', 'Ogliastra']
BASQUE_C = ['Gipuzkoa', 'Bizkaia']
CATALONIA = ['Barcelona', 'Gerona', 'Lérida', 'Tarragona']
VALENCIA_C = ['Castellón', 'Valencia', 'Alicante']
GALICIA = ['La Coruña', 'Lugo', 'Orense', 'Pontevedra']
CASTILE_OLD = ['Burgos', 'Cantabria', 'Asturias', 'León', 'Palencia', 'Valladolid', 'Soria', 'La Rioja', 'Zamora', 'Salamanca', 'Segovia', 'Ávila', 'Álava']
CASTILE_NEW = ['Madrid', 'Toledo', 'Guadalajara', 'Cuenca', 'Zaragoza', 'Huesca', 'Teruel', 'Navarra']
CASTILE_SOUTH = ['Sevilla', 'Córdoba', 'Jaén', 'Cádiz', 'Huelva', 'Murcia', 'Cáceres', 'Badajoz', 'Ciudad Real', 'Albacete']
GRANADA = ['Granada', 'Málaga', 'Almería']
IBERIA_IB = ['Barcelona', 'Gerona', 'Lérida', 'Tarragona', 'Castellón', 'Valencia', 'Alicante', 'Murcia', 'Almería', 'Granada', 'Málaga', 'Jaén', 'Córdoba',
             'Sevilla', 'Cádiz', 'Huelva', 'Baleares', 'Zaragoza', 'Huesca', 'Teruel', 'Albacete']
DE_WEST = ['Bayern', 'Baden-Württemberg', 'Rheinland-Pfalz', 'Saarland', 'Hessen', 'Nordrhein-Westfalen', 'Niedersachsen', 'Bremen', 'Hamburg',
           'Schleswig-Holstein', 'Thüringen', 'Sachsen-Anhalt']
DE_EAST = ['Brandenburg', 'Berlin', 'Mecklenburg-Vorpommern', 'Sachsen']
CH_FR = ['Genève', 'Vaud', 'Neuchâtel', 'Jura', 'Valais', 'Fribourg']
FLANDERS = ['West Flanders', 'East Flanders', 'Antwerp', 'Limburg', 'Flemish Brabant']
WALLONIA = ['Hainaut', 'Namur', 'Luxembourg', 'Liege', 'Walloon Brabant']
PL_GER = ['West Pomeranian', 'Lubusz', 'Lower Silesian', 'Warmian-Masurian']
SUDETEN = ['Karlovarský', 'Ústecký', 'Liberecký']
AT_EAST = ['Niederösterreich', 'Wien', 'Burgenland', 'Steiermark']
TRANSYLV_HU = ['Bihor', 'Satu Mare', 'Salaj', 'Cluj', 'Mures', 'Harghita', 'Covasna', 'Arad', 'Timis', 'Maramures', 'Bistrita-Nasaud', 'Alba', 'Sibiu',
               'Brasov', 'Hunedoara', 'Caras-Severin']
SZEKELY = ['Harghita', 'Covasna']
VOJVODINA = ['Severno-Backi', 'Zapadno-Backi', 'Južno-Backi', 'Severno-Banatski', 'Srednje-Banatski', 'Južno-Banatski', 'Sremski']
BG_TURK = ['Kardzhali', 'Razgrad', 'Targovishte', 'Shumen', 'Silistra', 'Dobrich']
BIH_CRO = ['West Herzegovina', 'Herzegovina-Neretva', 'West Bosnia', 'Posavina']
BIH_BOSNIAK = ['Sarajevo', 'Zenica-Doboj', 'Tuzla', 'Una-Sana', 'Bosnian Podrinje', 'Central Bosnia']
GR_MAC = ['Kentriki Makedonia', 'Dytiki Makedonia']
TR_HATTI = ['Çorum', 'Yozgat', 'Kinkkale', 'Ankara', 'Kirsehir', 'Çankiri']
TR_AEGEAN = ['Izmir', 'Aydin', 'Mugla', 'Çanakkale', 'Balikesir', 'Manisa']
TR_LYDIA = ['Izmir', 'Manisa', 'Aydin', 'Mugla', 'Antalya', 'Denizli', 'Usak', 'Burdur', 'Isparta']
TR_PHRYGIA = ['Ankara', 'Eskisehir', 'Afyonkarahisar', 'Kütahya', 'Konya', 'Bilecik', 'Usak', 'Kinkkale', 'Kirsehir', 'Aksaray', 'Çankiri']
TR_PONTUS = ['Trabzon', 'Rize', 'Giresun', 'Ordu', 'Samsun', 'Sinop', 'Artvin', 'Gümüshane', 'Bayburt']
TR_CENTRAL = ['Konya', 'Aksaray', 'Karaman', 'Nigde', 'Nevsehir', 'Kirsehir', 'Ankara', 'Kayseri', 'Sivas', 'Tokat', 'Amasya', 'Yozgat', 'Çorum',
              'Malatya', 'Kinkkale', 'Eskisehir', 'Afyonkarahisar', 'Isparta', 'Burdur', 'Çankiri', 'Kastamonu', 'K. Maras', 'Gaziantep', 'Erzincan',
              'Elazig', 'Erzurum']
TR_WEST = ['Kütahya', 'Denizli', 'Usak', 'Manisa', 'Aydin', 'Mugla', 'Izmir', 'Antalya', 'Mersin', 'Adana', 'Osmaniye', 'Hatay', 'Bolu', 'Düzce',
           'Karabük', 'Bartın', 'Zinguldak', 'Bilecik', 'Balikesir', 'Çanakkale', 'Bursa', 'Sakarya', 'Kocaeli', 'Yalova']
TR_THRACE = ['Edirne', 'Kirklareli', 'Tekirdag', 'Istanbul']
ARMENIA_W = ['Van', 'Mus', 'Bitlis', 'Erzurum', 'Kars', 'Agri', 'Iğdir', 'Erzincan', 'Bingöl', 'Tunceli', 'Elazig', 'Ardahan', 'Bayburt']
TR_KURD = ['Van', 'Mus', 'Bitlis', 'Agri', 'Bingöl', 'Tunceli', 'Hakkari', 'Sirnak', 'Siirt', 'Batman', 'Diyarbakir', 'Mardin', 'Adiyaman']
TR_SYRIAC = ['Mardin', 'Batman', 'Diyarbakir', 'Sanliurfa', 'Adiyaman']
IRQ_KURD = ['Dihok', 'Arbil', 'As-Sulaymaniyah']
IRQ_SOUTH = ['Al-Basrah', 'Maysan', 'Dhi-Qar', 'Al-Muthannia', 'Al-Qādisiyyah', 'An-Najaf', "Karbala'", 'Babil', 'Wasit']
SYRIA_W = ['Damascus', 'Rif Dimashq', 'Homs (Hims)', 'Hamah', 'Tartus', 'Lattakia', 'Idlib', 'Aleppo', 'Dar`a', 'Quneitra', "As Suwayda'"]
SYRIA_E = ['Dayr Az Zawr', 'Hasaka (Al Haksa)', 'Ar Raqqah']
ELAM = ['Khuzestan', 'Ilam', 'Lorestan', 'Kohgiluyeh and Buyer Ahmad', 'Fars', 'Bushehr', 'Chahar Mahall and Bakhtiari']
MEDIA = ['Hamadan', 'Kermanshah', 'Kordestan', 'Zanjan', 'Qazvin', 'Markazi', 'Tehran', 'Alborz', 'Qom', 'Lorestan']
PARTHIA = ['North Khorasan', 'Razavi Khorasan', 'South Khorasan', 'Golestan', 'Semnan']
IR_AZER = ['East Azarbaijan', 'Ardebil', 'Zanjan']
IR_KURD = ['Kordestan', 'Kermanshah', 'Ilam']
IR_LUR = ['Lorestan', 'Kohgiluyeh and Buyer Ahmad', 'Chahar Mahall and Bakhtiari']
AF_BACTRIA = ['Balkh', 'Jawzjan', 'Samangan', 'Kunduz', 'Takhar', 'Baghlan', 'Faryab', 'Sari Pul', 'Badakhshan']
AF_HERAT = ['Hirat', 'Farah', 'Nimroz', 'Badghis', 'Ghor']
AF_ARACHOSIA = ['Kandahar', 'Hilmand', 'Zabul', 'Uruzgan']
AF_KABUL = ['Kabul', 'Parwan', 'Kapisa', 'Logar', 'Wardak', 'Laghman', 'Nangarhar', 'Kunar', 'Nuristan', 'Paktya', 'Khost', 'Ghazni', 'Paktika']
AF_PASHTUN = ['Kandahar', 'Hilmand', 'Zabul', 'Uruzgan', 'Laghman', 'Nangarhar', 'Kunar', 'Paktya', 'Khost', 'Paktika', 'Logar', 'Wardak', 'Ghazni', 'Farah', 'Nimroz']
AF_TAJIK = ['Kabul', 'Parwan', 'Kapisa', 'Badakhshan', 'Takhar', 'Baghlan', 'Balkh', 'Samangan', 'Kunduz', 'Hirat', 'Badghis', 'Ghor']
AF_UZBEK = ['Faryab', 'Jawzjan', 'Sari Pul']
UZ_SOGD = ['Samarkand', 'Bukhoro', 'Navoi', 'Kashkadarya', 'Jizzakh', 'Sirdaryo', 'Tashkent', 'Ferghana', 'Namangan', 'Andijon']
UZ_KHWAREZM = ['Khorezm', 'Karakalpakstan']
UZ_FERGHANA = ['Ferghana', 'Namangan', 'Andijon', 'Tashkent', 'Sirdaryo', 'Jizzakh']
UZ_TAJIK = ['Samarkand', 'Bukhoro', 'Navoi', 'Kashkadarya', 'Surkhandarya']
KAZ_NORTH = ['North Kazakhstan', 'Qostanay', 'Aqmola', 'Astana', 'Pavlodar', 'Qaraghandy', 'East Kazakhstan']
IND_HINDUSTANI = ['Uttar Pradesh', 'Bihar', 'Madhya Pradesh', 'Delhi', 'Haryana', 'Uttarakhand', 'Himachal Pradesh']
IND_SOUTH = ['Tamil Nadu', 'Kerala', 'Karnataka', 'Andhra Pradesh', 'Telangana', 'Puducherry', 'Goa', 'Maharashtra']
IND_NE_HILLS = ['Nagaland', 'Manipur', 'Mizoram', 'Arunachal Pradesh', 'Meghalaya']
LK_TAMIL = ['Yāpanaya', 'Kilinŏchchi', 'Mulativ', 'Mannārama', 'Vavuniyāva', 'Trikuṇāmalaya', 'Maḍakalapuva']
CN_CORE = ['Henan', 'Shanxi', 'Shaanxi', 'Hebei', 'Shandong', 'Beijing', 'Tianjin']
CN_MID = ['Anhui', 'Jiangsu', 'Hubei', 'Shanghai']
CN_SOUTH1 = ['Zhejiang', 'Jiangxi', 'Hunan', 'Sichuan', 'Chongqing']
VN_HIGHLANDS = ['Kon Tum', 'Gia Lai', 'Đắk Lắk', 'Đắk Nông']
TH_ISAN = ['Nakhon Ratchasima', 'Chaiyaphum', 'Khon Kaen', 'Udon Thani', 'Nong Khai', 'Bueng Kan', 'Loei', 'Nong Bua Lam Phu', 'Sakon Nakhon',
           'Nakhon Phanom', 'Mukdahan', 'Kalasin', 'Maha Sarakham', 'Roi Et', 'Yasothon', 'Amnat Charoen', 'Ubon Ratchathani']
TH_KHMER = ['Surin', 'Buri Ram', 'Si Sa Ket']
TH_MALAY = ['Pattani', 'Yala', 'Narathiwat', 'Satun']
MM_LOWER = ['Mon', 'Bago', 'Yangon', 'Ayeyarwady', 'Tanintharyi', 'Kayin']
MM_UPPER = ['Mandalay', 'Magway', 'Sagaing']
MY_PEN = ['Perlis', 'Kedah', 'Kelantan', 'Perak', 'Pulau Pinang', 'Selangor', 'Negeri Sembilan', 'Melaka', 'Johor', 'Pahang', 'Terengganu', 'Kuala Lumpur', 'Putrajaya']
ID_MALAY = ['Riau', 'Kepulauan Riau', 'Jambi', 'Sumatera Selatan', 'Bangka-Belitung', 'Bengkulu', 'Lampung']
ID_EAST = ['Sulawesi Tengah', 'Sulawesi Tenggara', 'Sulawesi Utara', 'Gorontalo', 'Maluku', 'Maluku Utara', 'Nusa Tenggara Timur', 'Nusa Tenggara Barat']
KALIMANTAN = ['Kalimantan Barat', 'Kalimantan Tengah', 'Kalimantan Timur', 'Kalimantan Selatan']
# West Africa
ML_MANDE = ['Kayes', 'Koulikoro', 'Bamako', 'Ségou', 'Sikasso']
GN_MANDE = ['Kankan', 'Siguiri', 'Kouroussa', 'Mandiana', 'Kérouané', 'Faranah', 'Dabola', 'Dinguiraye', 'Kissidougou']
GN_FUTA = ['Labé', 'Pita', 'Mamou', 'Dalaba', 'Lélouma', 'Tougué', 'Koubia', 'Mali', 'Gaoual', 'Télimélé']
GN_COAST = ['Conakry', 'Boke', 'Boffa', 'Dubréka', 'Coyah', 'Forécariah', 'Kindia', 'Fria', 'Nzérékoré', 'Lola', 'Macenta', 'Guéckédou', 'Yomou', 'Beyla']
SN_WOLOF = ['Dakar', 'Thiès', 'Louga', 'Diourbel', 'Kaolack', 'Fatick', 'Kaffrine']
SN_MANDE = ['Tambacounda', 'Kédougou', 'Kolda', 'Sédhiou', 'Ziguinchor']
GH_AKAN = ['Ashanti', 'Brong Ahafo', 'Eastern', 'Central', 'Western', 'Greater Accra']
GH_GUR = ['Upper East', 'Upper West', 'Northern']
CI_AKAN = ['Sud-Comoé', 'Comoe', "N'zi-Comoé", 'Lacs', 'Vallée du Bandama', 'Lagunes', 'Agnéby', 'Zanzan']
CI_KRU = ['Cavally', 'Bas-Sassandra', 'Dix-Huit Montagnes', 'Haut-Sassandra', 'Fromager', 'Sud-Bandama', 'Marahoué']
CI_NORTH = ['Savanes', 'Denguélé', 'Worodougou', 'Bafing']
BJ_SOUTH = ['Mono', 'Kouffo', 'Atlantique', 'Littoral', 'Ouémé', 'Zou', 'Collines']
BJ_NORTH = ['Atakora', 'Donga', 'Borgou', 'Alibori']
NG_YORUBA = ['Oyo', 'Osun', 'Ogun', 'Ondo', 'Ekiti', 'Lagos', 'Kwara']
NG_IGBO = ['Anambra', 'Imo', 'Abia', 'Enugu', 'Ebonyi']
NG_DELTA = ['Rivers', 'Bayelsa', 'Akwa Ibom', 'Cross River']
NG_EDO = ['Edo', 'Delta']
NG_MIDDLE = ['Niger', 'Federal Capital Territory', 'Nassarawa', 'Plateau', 'Benue', 'Taraba', 'Kogi', 'Adamawa', 'Gombe']
NG_HAUSA = ['Kano', 'Katsina', 'Jigawa', 'Zamfara', 'Sokoto', 'Kebbi', 'Kaduna', 'Bauchi']
NE_HAUSA = ['Maradi', 'Zinder', 'Tahoua']
NE_SONGHAI = ['Tillabéri', 'Niamey', 'Dosso']
TD_SOUTH = ['Logone Occidental', 'Logone Oriental', 'Mandoul', 'Moyen-Chari', 'Tandjilé', 'Mayo-Kebbi Est', 'Mayo-Kebbi Ouest']
TD_KANEM = ['Lac', 'Kanem', 'Barh El Gazel']
TD_ARAB = ['Batha', 'Chari-Baguirmi', 'Salamat', 'Hadjer-Lamis', 'Guéra', "Ville de N'Djamena"]
TD_WADAI = ['Ouaddaï', 'Wadi Fira', 'Sila']
TD_TOUBOU = ['Tibesti', 'Borkou', 'Ennedi']
SD_DARFUR = ['North Darfur', 'Western Darfur', 'Central Darfur', 'Southern Darfur', 'Eastern Darfur']
SD_CENTRAL = ['Khartoum', 'Gezira', 'White Nile', 'Sennar', 'Blue Nile']
ET_HABESHA = ['Tigray', 'Amhara']
ER_HIGH = ['Maekel', 'Debub', 'Anseba']
# East and southern Africa
KE_BANTU = ['Central', 'Eastern', 'Western', 'Nairobi', 'Coast']
CD_KONGO = ['Bas-Congo', 'Kinshasa City']
CD_LUBA = ['Katanga', 'Kasaï-Oriental', 'Kasaï-Occidental']
CD_BASIN = ['Équateur', 'Bandundu', 'Maniema', 'Orientale']
AO_KONGO = ['Zaire', 'Uíge', 'Cabinda']
AO_MBUNDU = ['Luanda', 'Bengo', 'Cuanza Norte', 'Malanje', 'Cuanza Sul', 'Huambo', 'Bié', 'Benguela', 'Huíla']
AO_LUNDA = ['Lunda Norte', 'Lunda Sul', 'Moxico']
CG_KONGO = ['Pool', 'Brazzaville', 'Bouenza', 'Niari', 'Kouilou', 'Pointe Noire', 'Lékoumou']
ZA_NGUNI = ['KwaZulu-Natal', 'Eastern Cape', 'Mpumalanga']
ZA_SOTHO = ['Free State', 'Gauteng', 'North West', 'Limpopo']
NA_NORTH = ['Omusati', 'Ohangwena', 'Oshana', 'Oshikoto', 'Kavango', 'Caprivi', 'Kunene', 'Otjozondjupa']
MZ_SOUTH = ['Maputo', 'Gaza', 'Inhambane', 'Sofala']
MZ_NORTH = ['Niassa', 'Tete', 'Nampula', 'Cabo Delgado', 'Zambezia']
UG_NORTH = [-180, 1.75, 180, 5]
# Americas
US_NE = ['Maine', 'New Hampshire', 'Vermont', 'Massachusetts', 'Rhode Island', 'Connecticut', 'New Jersey', 'Delaware', 'Maryland']
US_LAKES = ['Michigan', 'Wisconsin', 'Illinois', 'Indiana', 'Ohio']
US_PLAINS = ['North Dakota', 'South Dakota', 'Iowa', 'Minnesota', 'Missouri']
US_SE = ['Georgia', 'Alabama', 'Mississippi', 'Florida', 'South Carolina', 'Tennessee', 'Kentucky']
US_BASIN = ['Nevada', 'Utah']
CO_ANDES = ['Cundinamarca', 'Boyacá', 'Santander', 'Bogota', 'Norte de Santander', 'Antioquia', 'Caldas', 'Risaralda', 'Quindío', 'Tolima', 'Huila',
            'Valle del Cauca', 'Cauca', 'Nariño']
CO_COAST = ['Atlántico', 'Bolívar', 'Magdalena', 'Cesar', 'Sucre', 'Córdoba']
CO_LLANOS = ['Meta', 'Casanare', 'Arauca', 'Vichada']
CO_AMAZON = ['Amazonas', 'Vaupés', 'Guainía', 'Guaviare', 'Caquetá', 'Putumayo']
PE_NCOAST = ['La Libertad', 'Lambayeque', 'Piura', 'Tumbes']
PE_HIGH = ['Junín', 'Pasco', 'Huánuco', 'Áncash', 'Huancavelica', 'Ayacucho', 'Apurímac', 'Cusco', 'Arequipa', 'Cajamarca']
PE_LOW = ['Loreto', 'Ucayali', 'Madre de Dios', 'San Martín', 'Amazonas']
EC_HIGH = ['Carchi', 'Imbabura', 'Pichincha', 'Cotopaxi', 'Tungurahua', 'Chimborazo', 'Bolivar', 'Cañar', 'Azuay', 'Loja', 'Santo Domingo de los Tsáchilas']
EC_COAST = ['Guayas', 'Manabi', 'El Oro', 'Los Rios', 'Esmeraldas', 'Santa Elena']
EC_AMAZON = ['Sucumbios', 'Orellana', 'Pastaza', 'Morona Santiago', 'Zamora Chinchipe', 'Napo']
BO_ALTI = ['La Paz', 'Oruro', 'Potosí']
BO_VALLEY = ['Cochabamba', 'Chuquisaca']
BO_LOW = ['Santa Cruz', 'El Beni', 'Pando']
AR_NW = ['Salta', 'Jujuy', 'Tucumán', 'Catamarca', 'La Rioja', 'Santiago del Estero', 'San Juan', 'Mendoza']
AR_LITORAL = ['Corrientes', 'Entre Ríos', 'Misiones']
AR_PATAGONIA = ['Neuquén', 'Río Negro', 'Chubut', 'Santa Cruz', 'Tierra del Fuego']
AR_PAMPA = ['Buenos Aires', 'La Pampa', 'San Luis', 'Córdoba', 'Santa Fe', 'Ciudad de Buenos Aires']
CL_CENTRAL = ['Región Metropolitana de Santiago', 'Valparaíso', "Libertador General Bernardo O'Higgins", 'Maule', 'Coquimbo', 'Ñuble', 'Bío-Bío']
CL_SOUTH = ['La Araucanía', 'Los Ríos', 'Los Lagos']
CL_NORTH = ['Arica y Parinacota', 'Tarapacá', 'Antofagasta']
CL_PATAG = ['Aisén del General Carlos Ibáñez del Campo', 'Magallanes y Antártica Chilena']
PY_CHACO = ['Boquerón', 'Presidente Hayes', 'Alto Paraguay']
BR_COAST = ['Rio de Janeiro', 'São Paulo', 'Espírito Santo', 'Bahia', 'Sergipe', 'Alagoas', 'Pernambuco', 'Paraíba', 'Rio Grande do Norte']
BR_1700 = ['Minas Gerais', 'Ceará', 'Piauí', 'Maranhão', 'Paraná', 'Santa Catarina']
BR_1783 = ['Goiás', 'Mato Grosso', 'Mato Grosso do Sul', 'Rio Grande do Sul', 'Distrito Federal', 'Tocantins']
BR_TUPI = BR_COAST + ['Ceará', 'Piauí', 'Maranhão', 'Paraná', 'Santa Catarina', 'Rio Grande do Sul']
BR_GE = ['Minas Gerais', 'Goiás', 'Tocantins', 'Distrito Federal', 'Mato Grosso', 'Mato Grosso do Sul']
BR_AMAZON = ['Amazonas', 'Acre', 'Rondônia', 'Roraima', 'Amapá', 'Pará']
VE_CORE = ['Distrito Capital', 'Miranda', 'Aragua', 'Carabobo', 'Falcón', 'Lara', 'Yaracuy', 'Zulia', 'Mérida', 'Táchira', 'Trujillo', 'Sucre',
           'Nueva Esparta', 'Vargas']
VE_ANDES = ['Mérida', 'Táchira', 'Trujillo']
GT_LADINO = ['Jutiapa', 'Chiquimula', 'Santa Rosa', 'Jalapa', 'Zacapa', 'El Progreso', 'Escuintla', 'Guatemala', 'Izabal']
MX_MAYA = ['Yucatán', 'Campeche', 'Quintana Roo', 'Chiapas', 'Tabasco']
MX_NAHUA = ['México', 'Distrito Federal', 'Puebla', 'Tlaxcala', 'Morelos', 'Hidalgo', 'Veracruz', 'Guerrero']
MX_WEST = ['Jalisco', 'Nayarit', 'Colima', 'Zacatecas', 'Aguascalientes', 'San Luis Potosí', 'Guanajuato', 'Querétaro']

# ================================================================== 0. base and prehistory
R(B, E, 'foragers')
R(-3000, E, 'evenki', a0=['RUS'], clip=[88, 45, 190, 82])
R(-3000, E, 'ugric_samoyed', a0=['RUS'], clip=[55, 55, 88, 82])
R(-3000, E, 'ugric_samoyed', a1={'RUS': ['Nenets', 'Yamal-Nenets']})
R(-3000, E, 'ugric_samoyed', a1={'RUS': ['Krasnoyarsk']}, clip=[80, 68, 115, 82])
R(-3000, E, 'paleo_siberian', a1={'RUS': ['Chukchi Autonomous Okrug', 'Kamchatka']})
R(-3000, E, 'paleo_siberian', a1={'RUS': ['Maga Buryatdan', 'Sakha (Yakutia)']}, clip=[150, 60, 190, 72])
R(-3000, E, 'paleo_siberian', a0=['RUS'], clip=[-180, 55, -165, 75])
R(-9500, -3501, 'neolithic', box=[[34, 30, 48.5, 38.5], [30, 36, 34, 41]])                      # Fertile Crescent, central Anatolia
R(-7000, -3001, 'saharan', box=[-12, 16, 33, 30])
R(-6500, -2801, 'old_euro', a0=['GRC', 'BGR', 'MKD', 'SRB', 'ROU', 'MDA', 'HUN', 'BIH', 'HRV', 'SVN', 'ALB', 'MNE', 'KOS'])
R(-6500, -2801, 'old_euro', a0=['TUR'], clip=[25, 36, 31, 42.5])
R(-5500, -2801, 'old_euro', a0=['DEU', 'CZE', 'SVK', 'AUT', 'POL', 'FRA', 'BEL', 'NLD', 'CHE', 'UKR', 'ITA', 'ESP', 'PRT', 'LUX', 'MLT'])
R(-5500, -2801, 'old_euro', a0=['UKR'], cut=[[28.5, 44, 41, 48.6]])
R(-4000, -2801, 'old_euro', a0=['GBR', 'IRL', 'IMN', 'DNK'])
R(-4000, -2801, 'old_euro', a0=['SWE', 'NOR'], clip=[4, 55, 20, 60.5])
R(-4500, -2501, 'pie', a1={'UKR': STEPPE_UKR, 'RUS': STEPPE_RUS + ['Kalmyk']}, a0=['KAZ'], clip=[28.5, 44, 56, 52.5])
R(-2800, -1001, 'bronze_ie', a0=['DEU', 'POL', 'CZE', 'SVK', 'AUT', 'CHE', 'NLD', 'BEL', 'LUX', 'DNK', 'HUN', 'BLR', 'LTU', 'LVA', 'GBR', 'IRL', 'IMN', 'FRA'])
R(-2800, -1001, 'bronze_ie', a0=['SWE', 'NOR'], clip=[4, 55, 20, 61])
R(-2800, -1001, 'bronze_ie', a0=['UKR'], a1={'RUS': RUS_W + RUS_C})
R(-2500, -801, 'iranian', a1={'UKR': STEPPE_UKR, 'RUS': STEPPE_RUS + ['Kalmyk', 'Bashkortostan', 'Chelyabinsk', 'Kurgan']}, a0=['KAZ', 'TKM', 'UZB', 'TJK'])
R(-3000, -1601, 'old_euro', a0=['GRC'])
R(-3000, -1451, 'minoan', a1={'GRC': ['Kriti']})
R(-1800, -239, 'nuragic', a1={'ITA': SARDINIA})
R(-3000, E, 'basque', a1={'ESP': BASQUE_C})
R(-3000, 1599, 'basque', a1={'ESP': ['Álava']})
R(-3000, E, 'basque', a1={'ESP': ['Navarra']}, clip=[-2.5, 42.75, -0.7, 43.4])
R(-3000, E, 'basque', a1={'FRA': ['Pyrénées-Atlantiques']}, clip=[-1.8, 42.9, -0.85, 43.6])

# ================================================================== 1. Mediterranean antiquity
R(-2000, E, 'greek', a0=['GRC'])
R(-1450, E, 'greek', a1={'GRC': ['Kriti']})
R(-1000, -301, 'thracian', a1={'GRC': ['Anatoliki Makedonia kai Thraki']})
R(-1100, E, 'greek', a0=['CYP'])
R(-1000, -1, 'italic', a0=['ITA', 'SMR', 'VAT'], a1x={'ITA': SARDINIA})
R(-900, -101, 'etruscan', a1={'ITA': ETRURIA + ['Roma']}, clip=[9.5, 41.95, 13, 44.3])
R(-800, -1, 'latin', a1={'ITA': ['Roma', 'Latina']})
R(-750, -201, 'greek', a1={'ITA': MAGNA_GRAECIA})
R(-750, -241, 'punic', a1={'ITA': ['Trapani', 'Palermo']})
R(-400, -191, 'celtic', a0=['ITA'], clip=[7.3, 44.35, 12.2, 46.4])
R(-200, 599, 'latin', a0=['ITA', 'SMR', 'VAT'])
R(-800, -218, 'punic', a0=['MLT'])
R(-217, 869, 'latin', a0=['MLT'])
R(870, E, 'maltese', a0=['MLT'])
R(600, E, 'italian', a0=['ITA', 'SMR', 'VAT'])
R(-1000, -101, 'iberian', a1={'ESP': IBERIA_IB})
R(-800, -101, 'celtiberian', a1={'ESP': GALICIA + CASTILE_OLD + ['Madrid', 'Toledo', 'Guadalajara', 'Cuenca', 'Cáceres', 'Badajoz', 'Ciudad Real']}, a0=['PRT'])
R(-800, -201, 'punic', a1={'ESP': ['Cádiz', 'Málaga', 'Baleares']})
R(-100, 749, 'hispano_roman', a0=['ESP', 'PRT', 'AND', 'GIB'], a1x={'ESP': BASQUE_C})
R(-1000, -301, 'thracian', a0=['BGR', 'MKD'], a1={'TUR': TR_THRACE[:3], 'SRB': ['Nišavski', 'Pirotski', 'Zajecarski', 'Borski', 'Jablanicki', 'Pcinjski', 'Toplicki']})
R(-300, 599, 'thracian', a0=['BGR'], a1={'TUR': TR_THRACE[:3]})
R(-300, 599, 'greek', a0=['MKD'], clip=[20.4, 40.8, 23.1, 41.6])
R(-1000, 599, 'illyrian', a0=['ALB', 'MNE', 'BIH', 'HRV', 'KOS'], a1={'MKD': ['Ohrid', 'Struga', 'Debar', 'Tetovo', 'Gostivar', 'Kičevo']})
R(-1000, 599, 'illyrian', a0=['SRB'], cut=[[21.7, 42, 23.1, 44.3]])
R(-1000, 270, 'dacian', a0=['ROU', 'MDA'])
R(-1000, 399, 'pannonian', a0=['HUN', 'SVN'], clip=[13.5, 45.4, 19.2, 48.2])
R(-900, -601, 'hurrian', a1={'TUR': ['Van', 'Agri', 'Iğdir', 'Bitlis', 'Hakkari']}, a0=['ARM'])
R(-3000, -1201, 'hurrian', a1={'TUR': ['Mardin', 'Sanliurfa', 'Diyarbakir', 'Batman', 'Siirt', 'Adiyaman', 'Malatya', 'Elazig'], 'SYR': SYRIA_E})
R(-2600, -1801, 'hattic', a1={'TUR': TR_HATTI})
R(-2000, -1201, 'anatolian', a0=['TUR'], a1x={'TUR': ['Van', 'Agri', 'Iğdir', 'Bitlis', 'Hakkari', 'Kars', 'Ardahan', 'Mardin', 'Sanliurfa',
                                                        'Diyarbakir', 'Batman', 'Siirt', 'Sirnak', 'Adiyaman', 'Malatya', 'Elazig']})
R(-1200, -547, 'anatolian', a1={'TUR': TR_LYDIA + ['Mersin', 'Adana', 'Osmaniye', 'Hatay', 'K. Maras', 'Gaziantep', 'Malatya', 'Karaman', 'Nigde']})
R(-1200, -301, 'phrygian', a1={'TUR': TR_PHRYGIA + ['Kayseri', 'Nevsehir', 'Yozgat', 'Çorum', 'Sivas', 'Tokat', 'Amasya']})
R(-1000, E, 'greek', a1={'TUR': ['Izmir', 'Çanakkale']})
R(-1000, 1299, 'greek', a1={'TUR': TR_AEGEAN})
R(-600, 1599, 'greek', a1={'TUR': ['Sinop', 'Samsun', 'Trabzon', 'Giresun', 'Ordu', 'Rize']})
R(-660, 1499, 'greek', a1={'TUR': ['Istanbul', 'Kocaeli', 'Yalova', 'Bursa', 'Tekirdag', 'Sakarya']})
R(-100, 1099, 'greek', a0=['TUR'], a1x={'TUR': ARMENIA_W + TR_KURD + ['Sanliurfa', 'Hatay', 'Kilis', 'Gaziantep', 'Malatya']})
R(-100, 599, 'greek', a1={'TUR': TR_THRACE})
R(600, 1499, 'greek', a1={'TUR': TR_THRACE})
R(-630, 640, 'greek', a0=['LBY'], clip=[19.5, 31.8, 25.5, 33.5])
R(-300, 999, 'greek', a0=['EGY'], clip=[29.6, 30.9, 30.2, 31.4])     # Alexandria
R(-500, 1475, 'greek', a1={'RUS': ['Crimea', 'Sevastopol']}, clip=[32.5, 44.3, 36.7, 44.85])

# ================================================================== 2. Celts, Germans and the West
R(-800, -51, 'gaulish', a0=['FRA', 'BEL', 'LUX', 'CHE'], a1={'DEU': ['Rheinland-Pfalz', 'Saarland']})
R(-800, -101, 'celtic', a0=['AUT', 'CZE'], a1={'DEU': ['Baden-Württemberg', 'Bayern', 'Hessen', 'Thüringen']})
R(-400, -101, 'celtic', a0=['SVK', 'HUN', 'SVN'], cut=[[19.2, 45, 23, 49]])
R(-400, -51, 'celtic', a0=['SRB'], clip=[19, 44.4, 21, 45.3])
R(-800, 449, 'briton', a0=['GBR'])
R(-800, E, 'irish', a0=['IRL', 'IMN'])
R(-800, 1609, 'irish', a0=['GBR'], clip=N_IRELAND)
R(-300, 899, 'pictish', a0=['GBR'], clipoly=SCOTLAND, cut=[[-7.9, 54.6, -3.6, 56.25]])
R(500, 899, 'irish', a0=['GBR'], clip=[-7.9, 55.3, -5.0, 57.0])                             # Dal Riata
R(-300, 1099, 'briton', a0=['GBR'], clipoly=SCOTLAND, clip=[-5.2, 54.6, -3.6, 56.25])       # Strathclyde
R(650, 1099, 'anglo_saxon', a0=['GBR'], clipoly=SCOTLAND, clip=[-3.6, 55.0, -1.5, 56.1])         # Lothian (Northumbria)
R(-50, 449, 'gallo_roman', a0=['FRA', 'BEL', 'LUX'], a1={'DEU': ['Rheinland-Pfalz', 'Saarland'], 'CHE': CH_FR})
R(450, E, 'french', a0=['FRA', 'MCO'])
R(450, E, 'french', a1={'BEL': WALLONIA, 'CHE': CH_FR})
R(450, 1879, 'occitan', a1={'FRA': OCCITAN})
R(450, E, 'breton', a1={'FRA': BRETON})
R(450, 1918, 'german', a1={'FRA': ALSACE}, clip=[6.0, 47.4, 8.3, 49.3])
R(600, 1879, 'italian', a1={'FRA': CORSICA})
R(900, E, 'catalan', a1={'FRA': ['Pyrénées-Orientales']})
R(-3000, E, 'basque', a1={'FRA': ['Pyrénées-Atlantiques']}, clip=[-1.8, 42.9, -0.85, 43.6])
# Germanic peoples
R(-1000, 499, 'germanic', a0=['DNK'], a1={'DEU': ['Schleswig-Holstein', 'Niedersachsen', 'Hamburg', 'Bremen', 'Mecklenburg-Vorpommern', 'Brandenburg',
                                                   'Berlin', 'Sachsen-Anhalt']})
R(-1000, 499, 'germanic', a0=['SWE', 'NOR'], clip=[4, 55, 20, 64])
R(-500, 499, 'germanic', a0=['NLD'], a1={'DEU': ['Nordrhein-Westfalen', 'Sachsen', 'Thüringen']})
R(-100, 499, 'germanic', a1={'DEU': ['Hessen', 'Bayern', 'Baden-Württemberg']}, cut=[[6, 47, 13.9, 48.7]])
R(-50, 449, 'gallo_roman', a1={'DEU': ['Rheinland-Pfalz', 'Saarland']})
R(-500, 499, 'germanic', a0=['POL'], clip=[14, 50, 20, 55])
R(1, 549, 'germanic', a0=['CZE', 'SVK'])
R(150, 375, 'germanic', a0=['UKR', 'MDA', 'ROU'], clip=[24, 45.3, 34, 51])                 # Goths
R(271, 567, 'germanic', a0=['ROU'], clip=[20.3, 45, 27.5, 48.2])                            # Gepids
R(470, 567, 'germanic', a0=['HUN'], cut=[[19.2, 45, 23, 49]])
R(450, 1099, 'anglo_saxon', a0=['GBR'], clip=[-0.5, 50.5, 2, 53.6])
R(550, 1099, 'anglo_saxon', a0=['GBR'], clip=[-2.5, 50.5, 2, 55.9])
R(700, 1099, 'anglo_saxon', a0=['GBR'], cut=[WALES, CORNWALL, N_IRELAND], clip=[-6, 49.8, 2, 55.9])
R(1100, E, 'english', a0=['GBR'], cut=[WALES, CORNWALL, N_IRELAND], clip=[-6, 49.8, 2, 55.9])
R(450, 1699, 'cornish', a0=['GBR'], clip=CORNWALL)
R(-800, E, 'welsh', a0=['GBR'], clip=WALES)
R(-800, 449, 'briton', a0=['GBR'], clip=WALES)
R(1610, E, 'scots', a0=['GBR'], clip=N_IRELAND)
R(900, E, 'gaels', a0=['GBR'], clipoly=SCOTLAND)
R(1100, E, 'scots', a0=['GBR'], clipoly=SCOTLAND, cut=[[-9, 56.15, 0, 61.5]])                 # Lothian and the Borders
R(1100, E, 'scots', a0=['GBR'], clip=[-3.5, 56.15, -1.5, 57.75])                            # Fife to Aberdeen and Moray coast
R(1400, E, 'scots', a0=['GBR'], clipoly=SCOTLAND, clip=[-5.3, 54.6, -1.5, 56.3])
R(900, 1799, 'gaels', a0=['GBR'], clipoly=HIGHLANDS)
R(1800, E, 'scots', a0=['GBR'], clipoly=HIGHLANDS, clip=[-4.5, 56.0, -1.5, 58.0])
R(1800, E, 'gaels', a0=['GBR'], clip=[-8.5, 56.5, -5.0, 58.6])
R(800, 1468, 'norse', a0=['GBR'], clip=NORTHERN_ISLES)
R(1469, E, 'scots', a0=['GBR'], clip=NORTHERN_ISLES)
R(800, 1299, 'norse', a0=['GBR'], clip=[-8.5, 56.4, -5.6, 58.6])                           # Hebrides (Kingdom of the Isles)
R(900, 1199, 'norse', a0=['IRL'], clip=[-6.5, 53.2, -6.0, 53.5])
# Low Countries, Germany, Alps
R(-300, 799, 'frisian', a1={'NLD': ['Friesland', 'Groningen', 'Noord-Holland', 'Flevoland']})
R(500, E, 'dutch', a0=['NLD'], a1={'BEL': FLANDERS + ['Brussels']})
R(800, E, 'frisian', a1={'NLD': ['Friesland']})
R(1880, E, 'french', a1={'BEL': ['Brussels']})
R(-50, 449, 'gallo_roman', a1={'BEL': FLANDERS}, a0=['NLD'], clip=[2.5, 50.6, 6.2, 51.4])
R(450, E, 'german', a1={'DEU': ['Bayern', 'Baden-Württemberg', 'Rheinland-Pfalz', 'Saarland', 'Hessen', 'Nordrhein-Westfalen', 'Niedersachsen',
                                 'Bremen', 'Hamburg', 'Schleswig-Holstein', 'Sachsen-Anhalt', 'Thüringen']}, a0=['LUX', 'LIE'])
R(450, E, 'german', a0=['CHE'], a1x={'CHE': CH_FR + ['Ticino', 'Graubünden']})
R(450, 1879, 'romansh', a1={'CHE': ['Graubünden']})
R(1880, E, 'german', a1={'CHE': ['Graubünden']})
R(600, E, 'italian', a1={'CHE': ['Ticino']})
R(-200, 449, 'latin', a1={'CHE': ['Ticino', 'Graubünden']})
R(600, 1199, 'wendish', a1={'DEU': DE_EAST + ['Sachsen-Anhalt']}, clip=[11.3, 50.2, 15.1, 54.8])
R(600, 1099, 'wendish', a1={'DEU': ['Schleswig-Holstein']}, clip=[10.3, 53.4, 11.5, 54.5])
R(500, E, 'german', a1={'DEU': ['Schleswig-Holstein']}, clip=[8, 53, 11.5, 54.4])
R(500, 1099, 'norse', a1={'DEU': ['Schleswig-Holstein']}, clip=[8, 54.4, 11.5, 55.1])
R(1100, 1864, 'danish', a1={'DEU': ['Schleswig-Holstein']}, clip=[8, 54.4, 11.5, 55.1])
R(1100, E, 'german', a1={'DEU': ['Schleswig-Holstein']}, clip=[8, 53, 11.5, 54.4])
R(1865, E, 'german', a1={'DEU': ['Schleswig-Holstein']})
R(1200, E, 'german', a1={'DEU': DE_EAST})
R(1200, E, 'german', a1={'DEU': ['Sachsen-Anhalt']})
R(1200, E, 'wendish', a1={'DEU': ['Sachsen', 'Brandenburg']}, clip=[13.6, 51.1, 14.8, 51.8])   # Sorbs of Lusatia
R(1600, E, 'german', a1={'DEU': ['Sachsen', 'Brandenburg']}, clip=[13.6, 51.1, 14.8, 51.8])
R(-800, -16, 'celtic', a0=['AUT'])
R(-15, 549, 'latin', a0=['AUT'], clip=[9.5, 46.4, 16.9, 48.3])
R(550, E, 'german', a1={'AUT': ['Tirol', 'Vorarlberg', 'Salzburg', 'Oberösterreich']})
R(600, E, 'german', a1={'ITA': ['Bozen']})
R(600, 899, 'slavic', a1={'AUT': AT_EAST})
R(600, 1199, 'slovene', a1={'AUT': ['Kärnten']})
R(900, E, 'german', a1={'AUT': AT_EAST})
R(1200, E, 'german', a1={'AUT': ['Kärnten']})
# Scandinavia and Iceland
R(500, 1099, 'norse', a0=['DNK', 'FRO'])
R(500, 1099, 'norse', a0=['SWE'], clip=[10, 55, 20, 63.5])
R(500, 1099, 'norse', a0=['NOR'], clip=[4, 57.5, 31.5, 69.5])
R(874, 1099, 'norse', a0=['ISL'])
R(1100, E, 'icelandic', a0=['ISL'])
R(1100, E, 'danish', a0=['DNK', 'FRO'])
R(1100, E, 'swedish', a0=['SWE'], clip=[10, 55, 20, 63.5])
R(1100, 1699, 'danish', a1={'SWE': ['Skåne', 'Blekinge', 'Halland']})
R(1100, E, 'norwegian', a0=['NOR'], clip=[4, 57.5, 31.5, 69.5])
R(-1000, 1799, 'sami', a0=['NOR', 'SWE', 'FIN'], clip=[12, 63.5, 32, 72])
R(-1000, 1799, 'sami', a1={'RUS': ['Murmansk']})
R(1700, E, 'swedish', a0=['SWE'])
R(1800, E, 'norwegian', a0=['NOR'])
R(1800, E, 'finnish', a1={'FIN': ['Lapland']})
R(1800, E, 'sami', a0=['NOR'], clip=[21, 68.5, 29, 70.5])           # inner Finnmark

# ================================================================== 3. Eastern Europe, Baltic, Russia
R(-1000, 499, 'baltic', a0=['LTU', 'LVA'], a1={'BLR': ['Grodno', 'Vitebsk', 'Minsk'], 'POL': ['Podlachian', 'Warmian-Masurian'], 'RUS': ['Kaliningrad', 'Pskov', 'Smolensk']})
R(-1000, 499, 'baltic', a0=['BLR'], a1={'RUS': ['Bryansk', 'Kaluga', 'Orel', 'Tula', 'Kursk', 'Lipetsk', 'Moskovskaya', 'Moskva']})
R(-500, 499, 'slavic', a1={'UKR': ['Volyn', 'Rivne', 'Zhytomyr', 'Kiev', 'Kiev City', 'Chernihiv', "L'viv", "Ternopil'", "Khmel'nyts'kyy", 'Vinnytsya', "Ivano-Frankivs'k", 'Chernivtsi', 'Cherkasy', 'Poltava', 'Sumy', 'Transcarpathia']})
R(-300, 499, 'germanic', a0=['POL'], a1x={'POL': ['Podlachian', 'Warmian-Masurian']})
R(-1000, 1299, 'prussian', a1={'POL': ['Warmian-Masurian'], 'RUS': ['Kaliningrad']})
R(500, 1199, 'baltic', a0=['LTU', 'LVA'])
R(1200, E, 'lithuanian', a0=['LTU'])
R(1200, E, 'latvian', a0=['LVA'])
R(-1000, 1199, 'finnic', a0=['EST', 'FIN'], a1={'RUS': ['Leningrad', 'City of St. Petersburg', 'Novgorod', 'Vologda', "Arkhangel'sk", 'Karelia']})
R(1100, E, 'finnish', a0=['FIN'], cut=[[12, 66.5, 32, 72]])
R(1200, E, 'estonian', a0=['EST'])
R(800, 1937, 'karelian', a1={'RUS': ['Karelia']})
R(1938, E, 'russian', a1={'RUS': ['Karelia']})
R(-1000, 1879, 'volga_finn', a1={'RUS': ['Mordovia', 'Mariy-El', 'Udmurt', 'Komi', "Perm'", 'Kirov', 'Penza', 'Tambov', "Ryazan'", 'Nizhegorod', 'Vladimir',
                                          'Ivanovo', 'Kostroma', "Yaroslavl'", 'Moskva', 'Moskovskaya', 'Ul\'yanovsk', 'Samara']})
R(-1000, 899, 'finnic', a1={'RUS': ["Tver'", 'Pskov']})
R(500, 899, 'slavic', a0=['POL', 'SVK', 'BLR', 'UKR'])
R(550, 899, 'slavic', a0=['CZE'])
R(600, 899, 'slavic', a0=['ROU', 'MDA'])
R(800, 894, 'slavic', a0=['HUN'])
R(600, 1299, 'rus', a0=['UKR', 'BLR'], a1={'RUS': RUS_W + ['Bryansk', 'Kursk', 'Orel', 'Kaluga', 'Tula', 'Lipetsk']})
R(900, 1299, 'rus', a1={'RUS': RUS_C + ["Tver'"]})
R(-1000, 899, 'baltic', a1={'RUS': ['Smolensk', 'Kaluga', 'Bryansk']}, clip=[30, 52, 37, 56.5])
R(1300, E, 'russian', a1={'RUS': RUS_W + RUS_C + ['Bryansk', 'Kursk', 'Orel', 'Kaluga', 'Tula', "Tver'", 'Lipetsk']})
R(1400, E, 'russian', a1={'RUS': ["Arkhangel'sk", 'Vologda', 'Kirov']})
R(1600, E, 'russian', a1={'RUS': ['Penza', 'Tambov', 'Voronezh', 'Belgorod', "Ul'yanovsk", "Perm'"]})
R(1700, E, 'russian', a1={'RUS': ['Sverdlovsk', "Tyumen'", 'Samara']})
R(1783, E, 'russian', a1={'RUS': ['Saratov', 'Orenburg', 'Chelyabinsk', 'Kurgan', "Astrakhan'", 'Volgograd']})
R(1800, E, 'russian', a1={'RUS': ['Rostov', "Stavropol'"]})
R(1880, E, 'russian', a1={'RUS': ['Mordovia']})
R(1920, E, 'russian', a1={'RUS': ['Bashkortostan']})
R(1938, E, 'russian', a1={'RUS': ['Udmurt']})
R(1945, E, 'russian', a1={'RUS': ['Mariy-El', 'Komi']})
R(1300, 1799, 'ruthenian', a0=['UKR', 'BLR'])
R(1800, E, 'ukrainian', a0=['UKR'])
R(1800, E, 'belarusian', a0=['BLR'])
R(900, E, 'polish', a0=['POL'])
R(1250, 1944, 'german', a1={'POL': ['West Pomeranian', 'Lubusz']})
R(1300, 1944, 'german', a1={'POL': ['Lower Silesian', 'Warmian-Masurian'], 'RUS': ['Kaliningrad']})
R(1300, 1944, 'german', a1={'POL': ['Pomeranian']}, clip=[14, 53.5, 17.6, 55])
R(1945, E, 'russian', a1={'RUS': ['Kaliningrad']})
R(900, E, 'czech', a0=['CZE'])
R(1300, 1944, 'german', a1={'CZE': SUDETEN})
R(-500, -1, 'celtic', a0=['CZE'])
R(900, E, 'slovak', a0=['SVK'])
R(1000, E, 'magyar', a0=['SVK'], clip=[17.4, 47.7, 22.6, 48.32])
R(-400, -101, 'celtic', a0=['SVK'])
R(370, 469, 'hunnic', a0=['HUN'], cut=[[19.2, 45, 23, 49]])
R(568, 799, 'avar', a0=['HUN'])
R(895, E, 'magyar', a0=['HUN'])
R(1000, 1699, 'magyar', a1={'ROU': TRANSYLV_HU})
R(1000, E, 'magyar', a1={'ROU': SZEKELY})
R(1000, 1599, 'magyar', a1={'SRB': VOJVODINA})
R(1000, E, 'magyar', a1={'SRB': ['Severno-Backi']})
R(1700, E, 'serbian', a1={'SRB': VOJVODINA[1:]})
R(900, E, 'romanian', a0=['ROU'], a1x={'ROU': TRANSYLV_HU + ['Constanta', 'Tulcea']})
R(1700, E, 'romanian', a1={'ROU': [n for n in TRANSYLV_HU if n not in SZEKELY]})
R(1300, E, 'romanian', a0=['MDA'])
R(600, 1399, 'bulgarian', a1={'ROU': ['Constanta', 'Tulcea']})
R(1400, 1877, 'nogai', a1={'ROU': ['Constanta', 'Tulcea']})
R(1878, E, 'romanian', a1={'ROU': ['Constanta', 'Tulcea']})
R(1400, 1806, 'nogai', a1={'MDA': ['Taraclia', 'Comrat', 'Cahul', 'Basarabeasca', 'Cantemir', 'Leova']})
R(600, E, 'bulgarian', a0=['BGR', 'MKD'])
R(1400, 1877, 'turkish', a1={'BGR': BG_TURK})
R(1400, E, 'turkish', a1={'BGR': ['Kardzhali']})
R(600, E, 'serbian', a0=['SRB', 'MNE'], a1x={'SRB': VOJVODINA})
R(600, E, 'serbian', a0=['BIH'])
R(600, E, 'croatian', a0=['HRV'], a1={'BIH': BIH_CRO})
R(1600, E, 'bosniak', a1={'BIH': BIH_BOSNIAK})
R(600, 1799, 'serbian', a0=['KOS'])
R(1800, E, 'albanian', a0=['KOS'])
R(600, E, 'albanian', a0=['ALB'])
R(1800, E, 'albanian', a0=['MKD'], clip=[20.4, 41.4, 21.05, 42.4])
R(600, E, 'slovene', a0=['SVN'])
R(700, 1912, 'bulgarian', a1={'GRC': GR_MAC}, clip=[20.9, 40.45, 23.9, 41.3])
R(1400, 1922, 'turkish', a1={'GRC': ['Anatoliki Makedonia kai Thraki']})
R(1974, E, 'turkish', a0=['CYP'], clip=[32.6, 35.17, 34.7, 35.75])
# The Pontic-Caspian steppe
STEPPE = dict(a1={'UKR': STEPPE_UKR + ['Kirovohrad', 'Kharkiv'], 'RUS': STEPPE_RUS + ['Kalmyk', 'Voronezh', 'Belgorod']}, a0=['MDA'],
              cut=[[24, 47.3, 30.3, 49]])
R(-800, -301, 'scythian', **STEPPE)
R(-300, 369, 'sarmatian', **STEPPE)
R(370, 469, 'hunnic', **STEPPE)
R(470, 649, 'bulgar', **STEPPE)
R(650, 899, 'khazar', **STEPPE)
R(900, 1049, 'oghuz', **STEPPE)
R(1050, 1239, 'kipchak', **STEPPE)
R(1240, 1782, 'nogai', **STEPPE)
R(1240, 1912, 'nogai', a1={'RUS': ['Crimea', 'Sevastopol']})
R(1914, E, 'russian', a1={'RUS': ['Crimea', 'Sevastopol']})
R(1650, 1799, 'ruthenian', a1={'UKR': ['Kharkiv', 'Kirovohrad', "Dnipropetrovs'k"]})
R(1600, E, 'russian', a1={'RUS': ['Voronezh', 'Belgorod']})
R(1783, E, 'ukrainian', a1={'UKR': STEPPE_UKR})
R(1650, E, 'oirat', a1={'RUS': ['Kalmyk']})
R(1800, 1937, 'ukrainian', a1={'RUS': ['Krasnodar']}, clip=[36.5, 45.1, 41, 47])
R(1938, E, 'russian', a1={'RUS': ['Krasnodar']})
R(700, 1239, 'bulgar', a1={'RUS': ['Tatarstan', 'Chuvash', "Ul'yanovsk", 'Samara']})
R(1240, E, 'tatar', a1={'RUS': ['Tatarstan']})
R(1240, E, 'chuvash', a1={'RUS': ['Chuvash']})
R(900, 1919, 'bashkir', a1={'RUS': ['Bashkortostan']})
R(900, 1782, 'bashkir', a1={'RUS': ['Orenburg', 'Chelyabinsk', 'Kurgan']})
# Caucasus
R(-1000, E, 'circassian', a1={'RUS': ['Adygey', 'Karachay-Cherkess', 'Kabardin-Balkar']})
R(-1000, 1863, 'circassian', a1={'RUS': ['Krasnodar']}, clip=[36.5, 43.3, 41, 45.15])
R(1864, E, 'russian', a1={'RUS': ['Krasnodar']}, clip=[36.5, 43.3, 41, 45.15])
R(1914, E, 'russian', a1={'RUS': ['Adygey']})
R(-1000, E, 'vainakh', a1={'RUS': ['Chechnya', 'Ingush']})
R(-1000, E, 'dagestani', a1={'RUS': ['Dagestan']})
R(100, 1239, 'sarmatian', a1={'RUS': ['North Ossetia']})
R(1240, E, 'ossetian', a1={'RUS': ['North Ossetia']})
R(1240, 1799, 'nogai', a1={'RUS': ["Stavropol'"]})
R(-1000, E, 'georgian', a0=['GEO'])
R(-600, E, 'armenian', a0=['ARM'])
R(-300, 899, 'cauc_albanian', a0=['AZE'])
R(900, 1099, 'azeri_iranian', a0=['AZE'])
R(1100, E, 'azerbaijani', a0=['AZE'])

# ================================================================== 4. Near East, Iran, Central Asia
R(-5000, -2001, 'sumerian', a1={'IRQ': IRQ_SOUTH}, clip=[43.5, 29, 48.6, 33])
R(-2800, -540, 'akkadian', a0=['IRQ', 'KWT'], a1x={'IRQ': IRQ_KURD + ['Al-Anbar']})
R(-2000, -540, 'akkadian', a1={'IRQ': IRQ_SOUTH})
R(-2000, -540, 'akkadian', a1={'IRQ': ['Al-Anbar']}, clip=[40, 32.5, 44.5, 35])
R(-2800, -540, 'hurrian', a1={'IRQ': IRQ_KURD})
R(-539, 899, 'aramaic', a0=['IRQ', 'KWT'])
R(-1000, E, 'arab', a1={'IRQ': ['Al-Anbar', 'Al-Muthannia']}, clip=[38, 29, 43.3, 34.4])
R(700, E, 'arab', a1={'IRQ': ['Al-Basrah', 'An-Najaf', 'Al-Muthannia', 'Al-Qādisiyyah']}, a0=['KWT'])
R(900, E, 'arab', a0=['IRQ'], a1x={'IRQ': IRQ_KURD + ['Ninawa', "At-Ta'mim"]})
R(1000, E, 'arab', a1={'IRQ': ['Ninawa']})
R(900, E, 'kurdish', a1={'IRQ': IRQ_KURD + ["At-Ta'mim"]})
R(-3000, -1201, 'canaanite', a0=['LBN', 'ISR', 'PSX', 'JOR'], a1={'SYR': SYRIA_W})
R(-2500, -1201, 'amorite', a1={'SYR': ['Aleppo', 'Idlib', 'Hamah', 'Homs (Hims)', 'Damascus', 'Rif Dimashq', 'Dar`a', "As Suwayda'"] + SYRIA_E})
R(-1200, 999, 'aramaic', a1={'SYR': SYRIA_W + SYRIA_E}, a0=['JOR'], clip=[35, 30.5, 42.5, 37.4])
R(-1200, -1, 'canaanite', a0=['LBN'], a1={'SYR': ['Tartus', 'Lattakia']})
R(1, 999, 'aramaic', a0=['LBN'])
R(-1200, 135, 'jewish', a0=['ISR', 'PSX'], cut=[[34.2, 31.2, 34.65, 31.9]])
R(136, 999, 'aramaic', a0=['ISR', 'PSX'])
R(-300, 999, 'arab', a0=['JOR'], clip=[34.9, 29, 39.5, 31.6])                   # Nabataeans
R(1000, E, 'arab', a0=['SYR', 'LBN', 'ISR', 'PSX', 'JOR'])
R(1945, E, 'kurdish', a1={'SYR': ['Hasaka (Al Haksa)']}, clip=[39.5, 36.4, 42.4, 37.4])
R(1960, E, 'jewish', a0=['ISR'])
R(-2000, E, 'arab', a0=ARABIA)
R(-1200, 599, 'south_arabian', a0=['YEM'], cut=[[50, 15, 54, 19]])
R(-4000, -540, 'elamite', a1={'IRN': ELAM})
R(-1500, -801, 'iranian', a0=['IRN', 'AFG'], a1x={'IRN': ELAM})
R(-800, -551, 'median', a1={'IRN': MEDIA + ['Esfahan', 'East Azarbaijan', 'West Azarbaijan', 'Ardebil', 'Gilan', 'Mazandaran']})
R(-800, -551, 'iranian', a1={'IRN': PARTHIA + ['Kerman', 'Yazd', 'Sistan and Baluchestan', 'Hormozgan', 'Semnan']})
R(-700, E, 'persian', a1={'IRN': ['Fars', 'Bushehr', 'Kohgiluyeh and Buyer Ahmad']})
R(-550, E, 'persian', a0=['IRN'], a1x={'IRN': ['Fars', 'Bushehr', 'Kohgiluyeh and Buyer Ahmad']})
R(-250, 224, 'parthian', a1={'IRN': PARTHIA, 'TKM': ['Ahal', 'Mary']})
R(-300, 1099, 'azeri_iranian', a1={'IRN': IR_AZER + ['West Azarbaijan']})
R(1100, E, 'azerbaijani', a1={'IRN': IR_AZER})
R(1100, E, 'azerbaijani', a1={'IRN': ['West Azarbaijan']}, clip=[44, 37.4, 46, 40])
R(600, E, 'kurdish', a1={'IRN': IR_KURD})
R(600, E, 'kurdish', a1={'IRN': ['West Azarbaijan']}, clip=[44, 35.5, 46.5, 37.4])
R(1000, E, 'lur', a1={'IRN': IR_LUR})
R(1000, E, 'baloch', a1={'IRN': ['Sistan and Baluchestan']}, clip=[57, 25, 64, 30.2])
R(1600, E, 'arab', a1={'IRN': ['Khuzestan']}, clip=[47.5, 29.8, 49.6, 32.2])
R(1500, E, 'turkmen', a1={'IRN': ['Golestan']}, clip=[53.8, 37.1, 56.5, 38.2])
# Anatolia: Armenians, Kurds, Turks
R(-600, 1399, 'armenian', a1={'TUR': ARMENIA_W})
R(1080, 1374, 'armenian', a1={'TUR': ['Adana', 'Mersin', 'Osmaniye']})
R(400, 999, 'aramaic', a1={'TUR': TR_SYRIAC})
R(900, E, 'kurdish', a1={'TUR': ['Hakkari', 'Sirnak', 'Siirt']})
R(1000, E, 'kurdish', a1={'TUR': ['Mardin', 'Batman', 'Diyarbakir']})
R(1400, E, 'kurdish', a1={'TUR': TR_KURD})
R(1600, E, 'kurdish', a1={'TUR': ['Sanliurfa']}, clip=[38.5, 36.6, 41.5, 38])
R(1200, E, 'turkish', a1={'TUR': TR_CENTRAL})
R(1300, E, 'turkish', a1={'TUR': TR_WEST + ['Kayseri', 'Nigde', 'Nevsehir', 'Karaman', 'Aksaray', 'Kastamonu', 'Sinop', 'Samsun', 'Amasya', 'Tokat',
                                            'Adiyaman', 'Kilis', 'Gaziantep', 'Hatay', 'Malatya']})
R(1300, E, 'turkish', a1={'TUR': ['Izmir', 'Çanakkale']}, clip=[26.5, 37.5, 30, 40.5])
R(1400, E, 'turkish', a1={'TUR': ['Erzurum', 'Erzincan', 'Kars', 'Ardahan', 'Bayburt', 'Gümüshane', 'Elazig', 'Malatya', 'Adana', 'Mersin', 'Osmaniye']})
R(1500, E, 'turkish', a1={'TUR': TR_THRACE + ['Bursa', 'Kocaeli', 'Sakarya', 'Yalova']})
R(1600, E, 'turkish', a1={'TUR': TR_PONTUS + ['Izmir', 'Çanakkale']})
R(1920, E, 'azerbaijani', a1={'TUR': ['Iğdir']})
R(1920, E, 'turkish', a1={'TUR': ['Hatay', 'Sanliurfa']}, clip=[35.8, 36.0, 37.0, 37.0])
# Central Asia
R(-800, 449, 'scythian', a0=['KAZ', 'KGZ'])
R(-800, -251, 'scythian', a1={'TKM': ['Balkan', 'Tashauz']})
R(-1500, -551, 'iranian', a0=['UZB', 'TJK', 'TKM'])
R(-550, 899, 'sogdian', a1={'UZB': UZ_SOGD, 'TJK': ['Leninabad']})
R(-550, 899, 'bactrian', a1={'UZB': ['Surkhandarya'], 'TJK': ['Khatlon', 'Dushanbe', 'Tadzhikistan Territories'], 'AFG': AF_BACTRIA})
R(-550, 1199, 'khwarezmian', a1={'UZB': UZ_KHWAREZM, 'TKM': ['Tashauz']})
R(-550, E, 'iranian', a1={'TJK': ['Gorno-Badakhshan']})
R(-250, 224, 'parthian', a1={'TKM': ['Ahal', 'Mary']})
R(225, 1099, 'persian', a1={'TKM': ['Ahal', 'Mary', 'Chardzhou']})
R(-250, 899, 'scythian', a1={'TKM': ['Balkan']})
R(900, 1099, 'oghuz', a1={'TKM': ['Balkan', 'Tashauz']})
R(1100, E, 'turkmen', a0=['TKM'])
R(900, E, 'tajik', a1={'UZB': UZ_TAJIK, 'TJK': ['Leninabad', 'Khatlon', 'Dushanbe', 'Tadzhikistan Territories']})
R(1000, 1499, 'chagatai', a1={'UZB': UZ_FERGHANA})
R(1200, 1499, 'chagatai', a1={'UZB': UZ_KHWAREZM, 'TKM': ['Tashauz']})
R(1500, E, 'uzbek', a0=['UZB'])
R(1500, E, 'uzbek', a1={'TKM': ['Tashauz']}, clip=[59.5, 41.2, 61.5, 42.5])
R(1500, E, 'tajik', a1={'UZB': ['Samarkand', 'Bukhoro']}, clip=[64.2, 39.6, 67.2, 40.0])
R(1500, E, 'uzbek', a1={'TJK': ['Leninabad']}, clip=[68.5, 40.0, 71, 41.0])
R(1500, E, 'uzbek', a1={'KGZ': ['Osh', 'Jalal-Abad']}, clip=[71.5, 40.3, 73.4, 41.2])
R(450, 551, 'hunnic', a0=['KAZ'])
R(552, 899, 'gokturk', a0=['KAZ', 'KGZ'])
R(900, 1049, 'oghuz', a0=['KAZ'], clip=[46, 40, 70, 50])
R(900, 1049, 'kipchak', a0=['KAZ'], clip=[46, 50, 90, 56])
R(900, 1499, 'chagatai', a1={'KAZ': ['Almaty', 'Almaty City', 'Zhambyl']}, a0=['KGZ'])
R(1050, 1499, 'kipchak', a0=['KAZ'], a1x={'KAZ': ['Almaty', 'Almaty City', 'Zhambyl']})
R(1500, E, 'kazakh', a0=['KAZ'])
R(1500, E, 'kyrgyz', a0=['KGZ'])
R(1938, 2000, 'russian', a1={'KAZ': KAZ_NORTH})
R(2010, E, 'russian', a1={'KAZ': ['North Kazakhstan']})
# Afghanistan and Pakistan
R(-550, E, 'persian', a1={'AFG': AF_HERAT})
R(-550, 999, 'iranian', a1={'AFG': AF_ARACHOSIA + ['Bamyan', 'Ghazni', 'Paktika']})
R(-500, 999, 'gandharan', a1={'AFG': ['Kabul', 'Parwan', 'Kapisa', 'Logar', 'Wardak', 'Laghman', 'Nangarhar', 'Kunar', 'Nuristan', 'Paktya', 'Khost'],
                               'PAK': ['K.P.', 'F.A.T.A.', 'F.C.T.']})
R(900, E, 'tajik', a1={'AFG': AF_TAJIK + AF_BACTRIA})
R(1000, E, 'pashtun', a1={'AFG': AF_PASHTUN, 'PAK': ['K.P.', 'F.A.T.A.']})
R(1300, E, 'mongol', a1={'AFG': ['Bamyan']})
R(1500, E, 'uzbek', a1={'AFG': AF_UZBEK})
R(1000, E, 'pashtun', a1={'PAK': ['Baluchistan']}, clip=[66.5, 29.8, 70.5, 32.5])
R(-1000, 999, 'iranian', a1={'PAK': ['Baluchistan']}, cut=[[66.5, 29.8, 70.5, 32.5]])
R(1000, E, 'baloch', a1={'PAK': ['Baluchistan']}, cut=[[66.5, 29.8, 70.5, 32.5]])

# ================================================================== 5. South Asia
R(-5000, -3301, 'neolithic', a1={'PAK': ['Baluchistan']}, clip=[66.5, 27, 69, 30.5])          # Mehrgarh
R(-3000, E, 'dravidian', a1={'IND': IND_SOUTH + ['Gujarat', 'Rajasthan', 'Madhya Pradesh', 'Chhattisgarh', 'Odisha', 'Jharkhand']})
R(-3000, -501, 'munda', a1={'IND': ['Jharkhand', 'Odisha', 'Chhattisgarh', 'West Bengal', 'Bihar', 'Assam', 'Meghalaya']}, a0=['BGD'])
R(-3300, -1801, 'harappan', a1={'PAK': ['Sind', 'Punjab', 'F.C.T.'], 'IND': ['Gujarat', 'Haryana', 'Punjab', 'Chandigarh', 'Delhi']})
R(-3300, -1801, 'harappan', a1={'IND': ['Rajasthan', 'Uttar Pradesh']}, clip=[69, 26, 78, 31])
R(-1700, -501, 'vedic', a1={'PAK': ['Punjab', 'K.P.', 'F.C.T.'], 'IND': ['Punjab', 'Haryana', 'Delhi', 'Chandigarh', 'Himachal Pradesh']})
R(-1100, -501, 'vedic', a1={'IND': ['Uttar Pradesh', 'Uttarakhand']})
R(-800, -501, 'vedic', a1={'IND': ['Bihar', 'Rajasthan', 'Madhya Pradesh']})
R(-500, 999, 'indo_aryan', a1={'IND': ['Punjab', 'Haryana', 'Delhi', 'Chandigarh', 'Himachal Pradesh', 'Uttar Pradesh', 'Uttarakhand', 'Bihar',
                                       'Rajasthan', 'Madhya Pradesh', 'Gujarat', 'West Bengal', 'Maharashtra', 'Jammu and Kashmir'],
                                'PAK': ['Punjab', 'Sind', 'F.C.T.', 'Azad Kashmir']}, a0=['BGD', 'NPL'])
R(-300, 999, 'indo_aryan', a1={'IND': ['Odisha', 'Assam', 'Goa']})
R(-500, E, 'gond', a1={'IND': ['Chhattisgarh', 'Jharkhand']})
R(1300, E, 'hindustani', a1={'IND': ['Chhattisgarh']})
R(1880, E, 'hindustani', a1={'IND': ['Jharkhand']})
R(1000, E, 'hindustani', a1={'IND': IND_HINDUSTANI})
R(1000, E, 'rajasthani', a1={'IND': ['Rajasthan']})
R(1000, E, 'punjabi', a1={'IND': ['Punjab', 'Chandigarh'], 'PAK': ['Punjab', 'F.C.T.']})
R(700, E, 'sindhi', a1={'PAK': ['Sind']})
R(1000, E, 'gujarati', a1={'IND': ['Gujarat', 'Dadra and Nagar Haveli and Daman and Diu']})
R(-300, E, 'marathi', a1={'IND': ['Maharashtra', 'Goa']})
R(1000, E, 'bengali', a1={'IND': ['West Bengal']}, a0=['BGD'])
R(1960, E, 'bengali', a1={'IND': ['Tripura']})
R(1000, E, 'odia', a1={'IND': ['Odisha']})
R(500, E, 'assamese', a1={'IND': ['Assam']})
R(-1000, E, 'hill_tb', a1={'IND': IND_NE_HILLS + ['Tripura']})
R(-1000, E, 'munda', a1={'IND': ['Meghalaya']})
R(1000, E, 'nepali', a0=['NPL'])
R(-1000, E, 'tibetan', a1={'IND': ['Ladakh', 'Sikkim']})
R(1900, E, 'nepali', a1={'IND': ['Sikkim']})
R(-500, E, 'kashmiri', a1={'IND': ['Jammu and Kashmir'], 'PAK': ['Northern Areas', 'Azad Kashmir']})
R(-500, E, 'punjabi', a1={'IND': ['Jammu and Kashmir']}, clip=[73.5, 32.2, 76.5, 33.1])        # Jammu (Dogra)
R(-300, 899, 'tamil', a1={'IND': ['Tamil Nadu', 'Puducherry', 'Kerala']})
R(900, E, 'tamil', a1={'IND': ['Tamil Nadu', 'Puducherry']})
R(900, E, 'malayali', a1={'IND': ['Kerala']})
R(-300, E, 'kannada', a1={'IND': ['Karnataka']})
R(-300, E, 'telugu', a1={'IND': ['Andhra Pradesh', 'Telangana']})
R(-500, E, 'sinhalese', a0=['LKA', 'MDV'])
R(1200, E, 'tamil', a1={'LKA': LK_TAMIL})

# ================================================================== 6. China, Mongolia, Korea, Japan
R(-5000, E, 'baiyue', a1={'CHN': ['Zhejiang', 'Jiangxi', 'Hunan', 'Fujian', 'Guangdong', 'Guangxi', 'Hainan', 'Jiangsu', 'Shanghai', 'Anhui', 'Hubei']},
  a0=['HKG', 'MAC'])
R(-1000, E, 'qiang', a1={'CHN': ['Sichuan', 'Chongqing', 'Gansu', 'Ningxia', 'Qinghai']})
R(-5000, -221, 'huaxia', a1={'CHN': CN_CORE})
R(-1000, -221, 'huaxia', a1={'CHN': CN_MID})
R(-300, -221, 'huaxia', a1={'CHN': CN_SOUTH1})
R(-220, E, 'han', a1={'CHN': CN_CORE + CN_MID + CN_SOUTH1})
R(-120, E, 'han', a1={'CHN': ['Gansu', 'Ningxia']})
R(1038, 1227, 'qiang', a1={'CHN': ['Ningxia']})
R(500, E, 'han', a1={'CHN': ['Fujian']})
R(800, E, 'han', a1={'CHN': ['Guangdong'], }, a0=['HKG', 'MAC'])
R(1000, E, 'han', a1={'CHN': ['Guangxi', 'Hainan']})
R(-500, E, 'zhuang', a1={'CHN': ['Guangxi']}, clip=[104, 21, 108.6, 26.5])
R(-500, 1699, 'yi_bai', a1={'CHN': ['Yunnan']})
R(1700, E, 'han', a1={'CHN': ['Yunnan']})
R(-500, 1799, 'miao', a1={'CHN': ['Guizhou']})
R(1800, E, 'han', a1={'CHN': ['Guizhou']})
R(-1000, E, 'tibetan', a1={'CHN': ['Xizang', 'Qinghai']}, a0=['BTN'])
R(-1000, E, 'tibetan', a1={'CHN': ['Sichuan']}, clip=[97, 26, 102.4, 35])
R(-1000, E, 'tibetan', a1={'CHN': ['Gansu']}, clip=[100.5, 33, 104, 35.5])
R(1945, E, 'han', a1={'CHN': ['Qinghai']}, clip=[100.6, 35.3, 103.1, 37.5])
# Xinjiang
R(-1000, 899, 'scythian', a1={'CHN': ['Xinjiang']}, clip=[73, 34, 82.5, 42.6])
R(-1000, 839, 'tocharian', a1={'CHN': ['Xinjiang']}, clip=[82.5, 38.5, 97, 42.6])
R(840, 1099, 'tocharian', a1={'CHN': ['Xinjiang']}, clip=[82.5, 38.5, 86, 42.6])
R(-1000, 839, 'scythian', a1={'CHN': ['Xinjiang']}, clip=[82.5, 34, 97, 38.5])
R(840, E, 'uyghur', a1={'CHN': ['Xinjiang']}, clip=[86, 34, 97, 42.6])
R(950, E, 'uyghur', a1={'CHN': ['Xinjiang']}, clip=[73, 34, 82.5, 42.6])
R(1100, E, 'uyghur', a1={'CHN': ['Xinjiang']}, clip=[73, 34, 97, 42.6])
R(-500, 551, 'scythian', a1={'CHN': ['Xinjiang']}, clip=[73, 42.6, 97, 50])
R(552, 839, 'gokturk', a1={'CHN': ['Xinjiang']}, clip=[73, 42.6, 97, 50])
R(840, 1209, 'uyghur', a1={'CHN': ['Xinjiang']}, clip=[73, 42.6, 97, 50])
R(1210, 1629, 'mongol', a1={'CHN': ['Xinjiang']}, clip=[73, 42.6, 97, 50])
R(1630, 1759, 'oirat', a1={'CHN': ['Xinjiang']}, clip=[73, 42.6, 97, 50])
R(1760, 1959, 'kazakh', a1={'CHN': ['Xinjiang']}, clip=[73, 42.6, 97, 50])
R(1960, E, 'han', a1={'CHN': ['Xinjiang']}, clip=[73, 42.6, 97, 50])
R(1960, E, 'han', a1={'CHN': ['Xinjiang']}, clip=[86.5, 43.3, 88.5, 44.6])       # Urumqi
# Mongolia, Inner Mongolia, Manchuria
STEPPE_E = dict(a0=['MNG'], a1={'CHN': ['Inner Mongol'], 'RUS': ['Buryat', 'Chita']})
R(-1500, -301, 'scythian', a0=['MNG'], clip=[87, 41, 100, 53])
R(-1500, -301, 'xianbei', a0=['MNG'], a1={'CHN': ['Inner Mongol']}, clip=[100, 37, 127, 53])
R(-300, 150, 'xiongnu', **STEPPE_E)
R(151, 551, 'xianbei', **STEPPE_E)
R(552, 743, 'gokturk', **STEPPE_E)
R(744, 839, 'uyghur', **STEPPE_E)
R(840, 919, 'kyrgyz', a0=['MNG'])
R(840, 919, 'xianbei', a1={'CHN': ['Inner Mongol'], 'RUS': ['Buryat', 'Chita']})
R(920, 1124, 'mongol', **STEPPE_E)
R(920, 1124, 'khitan', a1={'CHN': ['Inner Mongol', 'Liaoning']}, a0=['MNG'], clip=[110, 37, 124, 50])
R(1125, E, 'mongol', a0=['MNG'], a1={'CHN': ['Inner Mongol']})
R(1400, E, 'oirat', a0=['MNG'], clip=[87, 45, 94.5, 51])
R(1860, E, 'kazakh', a0=['MNG'], clip=[87, 47.5, 91.5, 49.3])
R(1200, 1899, 'buryat', a1={'RUS': ['Buryat', 'Chita']})
R(1800, E, 'russian', a1={'RUS': ['Chita']})
R(1900, E, 'russian', a1={'RUS': ['Buryat']})
R(1914, E, 'han', a1={'CHN': ['Inner Mongol']})
R(-1000, 1879, 'jurchen', a1={'CHN': ['Jilin', 'Heilongjiang', 'Liaoning'], 'RUS': ['Amur', "Primor'ye", 'Yevrey', 'Khabarovsk']}, clip=[100, 38, 145, 53.5])
R(-300, E, 'han', a1={'CHN': ['Liaoning']}, clip=[118, 38, 124.5, 41.6])
R(-37, 667, 'korean', a1={'CHN': ['Jilin', 'Liaoning']}, clip=[121.5, 40, 130, 43.6])
R(400, 919, 'khitan', a1={'CHN': ['Liaoning', 'Inner Mongol']}, clip=[117, 40.5, 122.5, 45])
R(1700, E, 'han', a1={'CHN': ['Liaoning']})
R(1880, E, 'han', a1={'CHN': ['Jilin', 'Heilongjiang']})
R(-1000, E, 'korean', a0=['KOR', 'PRK'])
R(-10000, -301, 'jomon', a0=['JPN'])
R(-300, E, 'japanese', a0=['JPN'], clip=[129, 30, 142.5, 38.4])
R(-300, 799, 'emishi', a0=['JPN'], clip=[138.5, 38.4, 142.5, 41.6])
R(800, E, 'japanese', a0=['JPN'], clip=[129, 30, 142.5, 41.6])
R(-300, 1870, 'ainu', a1={'JPN': ['Hokkaidō']})
R(1871, E, 'japanese', a1={'JPN': ['Hokkaidō']}, clip=[139, 41.3, 141.6, 43.4])
R(1880, E, 'japanese', a1={'JPN': ['Hokkaidō']})
R(-300, E, 'ryukyuan', a1={'JPN': ['Okinawa']})
R(-300, 1904, 'ainu', a1={'RUS': ['Sakhalin']}, clip=[141, 45.5, 145, 49.5])
R(-300, 1899, 'paleo_siberian', a1={'RUS': ['Sakhalin']}, clip=[141, 49.5, 145, 54.5])
R(1900, E, 'russian', a1={'RUS': ['Sakhalin']}, clip=[141, 50, 145, 54.5])
R(1905, 1945, 'japanese', a1={'RUS': ['Sakhalin']}, clip=[141, 45.5, 145, 50])
R(1946, E, 'russian', a1={'RUS': ['Sakhalin']})
R(1900, E, 'russian', a1={'RUS': ['Amur', "Primor'ye", 'Yevrey', 'Khabarovsk']})
R(-4000, 1682, 'formosan', a0=['TWN'])
R(1683, E, 'han', a0=['TWN'], clip=[119, 21, 121.0, 26])
R(1783, E, 'han', a0=['TWN'])
R(1783, 1938, 'formosan', a0=['TWN'], clip=[120.9, 21.8, 122.1, 24.6])

# ================================================================== 7. Southeast Asia and the Austronesian world
R(-1000, E, 'viet', a0=['VNM'], clip=[102, 16.8, 110, 24])
R(-1000, E, 'shan', a0=['VNM'], clip=[102, 20.3, 104.6, 23.5])
R(-1000, E, 'zhuang', a0=['VNM'], clip=[105, 21.5, 107.5, 23.4])
R(200, 1470, 'cham', a0=['VNM'], clip=[106.5, 10.8, 110, 16.8])
R(1471, 1699, 'cham', a0=['VNM'], clip=[106.5, 10.8, 110, 13.5])
R(1471, E, 'viet', a0=['VNM'], clip=[102, 13.5, 110, 16.8])
R(1700, E, 'viet', a0=['VNM'], clip=[102, 10.8, 110, 13.5])
R(-500, 1814, 'khmer', a0=['VNM'], clip=[102, 8, 107.2, 11.6])
R(1815, E, 'viet', a0=['VNM'], clip=[102, 8, 110, 11.6])
R(-500, 1945, 'cham', a1={'VNM': VN_HIGHLANDS})
R(-500, E, 'khmer', a0=['KHM'])
R(-500, 1299, 'khmer', a0=['LAO'])
R(1300, E, 'lao', a0=['LAO'])
R(-200, 1299, 'mon', a0=['THA'], clip=[98, 12, 102, 17.6])
R(-500, 1299, 'malay', a0=['THA'], clip=[97, 5.5, 102, 12])
R(800, 1499, 'khmer', a1={'THA': TH_ISAN + TH_KHMER + ['Sa Kaeo', 'Prachin Buri', 'Chanthaburi', 'Trat']})
R(-500, E, 'khmer', a1={'THA': TH_KHMER})
R(1200, E, 'shan', a0=['THA'], clip=[97, 17.6, 101.4, 20.5])
R(1300, E, 'thai', a0=['THA'], clip=[97, 6, 106, 17.6], a1x={'THA': TH_ISAN + TH_KHMER + TH_MALAY})
R(1500, E, 'lao', a1={'THA': TH_ISAN})
R(-500, E, 'malay', a1={'THA': TH_MALAY})
R(1900, E, 'thai', a1={'THA': ['Satun']})
R(-200, 849, 'pyu', a1={'MMR': MM_UPPER})
R(850, E, 'burmese', a1={'MMR': MM_UPPER + ['Rakhine']})
R(-300, 1799, 'mon', a1={'MMR': MM_LOWER})
R(1800, E, 'burmese', a1={'MMR': ['Bago', 'Yangon', 'Ayeyarwady', 'Tanintharyi']})
R(1880, E, 'burmese', a1={'MMR': ['Mon']})
R(-500, E, 'karen', a1={'MMR': ['Kayin', 'Kayah']})
R(1200, E, 'shan', a1={'MMR': ['Shan']})
R(-500, 1199, 'hill_tb', a1={'MMR': ['Shan']})
R(-500, E, 'hill_tb', a1={'MMR': ['Kachin', 'Chin']})
R(-1000, E, 'malay', a1={'MYS': MY_PEN}, a0=['BRN', 'SGP'])
R(1880, E, 'han', a0=['SGP'])
R(1880, E, 'han', a1={'MYS': ['Pulau Pinang']})
R(1900, 1960, 'han', a1={'MYS': ['Selangor', 'Kuala Lumpur', 'Perak']})
R(-1000, E, 'dayak', a1={'MYS': ['Sabah', 'Sarawak', 'Labuan'], 'IDN': KALIMANTAN})
R(1400, E, 'malay', a1={'IDN': ['Kalimantan Selatan']})
R(1600, E, 'malay', a1={'IDN': ['Kalimantan Barat']}, clip=[108, -3.5, 110.5, 2])
R(-1500, E, 'javanese', a1={'IDN': ['Jawa Tengah', 'Yogyakarta', 'Jawa Timur']})
R(-1500, E, 'sundanese', a1={'IDN': ['Jawa Barat', 'Banten', 'Jakarta Raya']})
R(-1500, E, 'balinese', a1={'IDN': ['Bali']})
R(-1500, E, 'malay', a1={'IDN': ID_MALAY})
R(-1500, E, 'batak', a1={'IDN': ['Sumatera Utara', 'Sumatera Barat']})
R(-1500, E, 'acehnese', a1={'IDN': ['Aceh']})
R(-1500, E, 'bugis', a1={'IDN': ['Sulawesi Selatan', 'Sulawesi Barat']})
R(-1500, E, 'e_indonesian', a1={'IDN': ID_EAST}, a0=['TLS'])
R(-3000, E, 'papuan', a0=['PNG'], a1={'IDN': ['Papua', 'Papua Barat']})
R(-1500, E, 'melanesian', a0=['PNG'], clip=[[149.5, -6.6, 160, 0], [146, -3, 148, -1.8]])
R(-2000, E, 'tagalog', a0=['PHL'], clip=[116, 12.4, 127, 21.5])
R(-2000, E, 'visayan', a0=['PHL'], clip=[116, 4, 127, 12.4])
R(1400, E, 'moro', a1={'PHL': MUSLIM_PHL + ['Cotabato', 'Sultan Kudarat', 'Lanao del Norte', 'Zamboanga Sibugay', 'Zamboanga del Sur']})
R(1960, E, 'visayan', a1={'PHL': ['Cotabato', 'Sultan Kudarat', 'Lanao del Norte', 'Zamboanga Sibugay', 'Zamboanga del Sur']})
R(500, E, 'malagasy', a0=['MDG'])
R(-1000, E, 'melanesian', a0=['SLB', 'VUT', 'NCL', 'FJI'])
R(-1000, E, 'polynesian', a0=['TON', 'WSM', 'PYF', 'COK', 'TUV', 'NIU', 'ASM', 'WLF'])
R(1000, 1899, 'polynesian', a1={'USA': ['Hawaii']})
R(1900, 1945, 'hawaii_japanese', a1={'USA': ['Hawaii']})
R(1960, E, 'anglo_american', a1={'USA': ['Hawaii']})
R(1300, 1870, 'maori', a0=['NZL'])
R(1871, E, 'anglo_aus', a0=['NZL'])
R(-50000, E, 'aboriginal', a0=['AUS'])
R(1848, E, 'anglo_aus', a1={'AUS': ['New South Wales', 'Victoria', 'Tasmania', 'Australian Capital Territory']})
R(1848, E, 'anglo_aus', a1={'AUS': ['South Australia']}, clip=[129, -38, 141, -30])
R(1871, E, 'anglo_aus', a1={'AUS': ['Queensland']}, clip=[138, -29.2, 154, -15])
R(1878, E, 'anglo_aus', a1={'AUS': ['Western Australia']}, clip=[114, -35.5, 119.5, -28.5])
R(1900, E, 'anglo_aus', a1={'AUS': ['Queensland', 'South Australia']})
R(1900, E, 'anglo_aus', a1={'AUS': ['Western Australia']}, clip=[112, -36, 124, -25])
R(1914, E, 'anglo_aus', a0=['AUS'])
R(1914, E, 'aboriginal', a1={'AUS': ['Northern Territory']}, clip=[129, -20, 138, -10.9])

# ================================================================== 8. Siberia and the Arctic
R(500, 1699, 'kyrgyz', a1={'RUS': ['Khakass', 'Tuva']})
R(-500, E, 'tuvan', a1={'RUS': ['Tuva', 'Gorno-Altay']})
R(1700, 1899, 'tuvan', a1={'RUS': ['Khakass']})
R(1900, E, 'russian', a1={'RUS': ['Khakass']})
R(1920, E, 'russian', a1={'RUS': ['Gorno-Altay']})
R(1300, E, 'yakut', a1={'RUS': ['Sakha (Yakutia)']}, clip=[105, 56, 135, 66.5])
R(1300, 1699, 'tatar', a1={'RUS': ["Tyumen'", 'Omsk']}, clip=[60, 54, 76, 59])
R(1800, E, 'russian', a1={'RUS': RUS_SSIB + ['Irkutsk', 'Krasnoyarsk']}, clip=[55, 45, 120, 58.5])
R(1880, E, 'russian', a1={'RUS': RUS_SSIB + ['Irkutsk', 'Krasnoyarsk']}, clip=[55, 45, 120, 61])
R(1914, E, 'russian', a1={'RUS': ['Kamchatka']}, clip=[155, 50, 164, 56.5])
R(1914, E, 'russian', a1={'RUS': ['Murmansk']})
R(1945, E, 'russian', a1={'RUS': ['Khanty-Mansiy', 'Nenets', 'Maga Buryatdan', 'Irkutsk', 'Krasnoyarsk', 'Kamchatka']})
R(1960, E, 'russian', a1={'RUS': ['Chukchi Autonomous Okrug']})
R(1960, 1994, 'russian', a1={'RUS': ['Sakha (Yakutia)']}, clip=[105, 56, 135, 66.5])
R(1994, E, 'russian', a1={'RUS': ['Yamal-Nenets']})

# ================================================================== 9. Africa
# North Africa and the Sahara
R(-5000, E, 'egyptian', a0=['EGY'])
R(-3000, E, 'berber', a0=MAGHREB + ['LBY'], clip=[-18, 17, 25, 38])
R(-3000, E, 'berber', a0=['MLI', 'NER', 'TCD'], clip=[-12, 17, 16, 27])
R(-1000, E, 'berber', a0=['EGY'], clip=[24.5, 28.8, 26.5, 29.5])                       # Siwa
R(-3000, E, 'toubou', a1={'TCD': TD_TOUBOU, 'NER': ['Agadez']}, clip=[11.5, 15.5, 25, 24])
R(500, E, 'tuareg', a1={'MLI': ['Kidal', 'Timbuktu', 'Gao'], 'NER': ['Agadez'], 'DZA': ['Tamanghasset', 'Illizi'], 'LBY': ['Ghat']}, clip=[-6, 16.5, 12, 27])
R(-3500, E, 'nubian', a1={'SDN': ['Northern', 'River Nile']})
R(-3500, -1, 'nubian', a1={'EGY': ['Aswan']}, clip=[31, 22, 34, 24.2])
R(-800, -147, 'punic', a0=['TUN'], clip=[8.5, 34.5, 11.5, 37.5])
R(-800, -147, 'punic', a0=['LBY'], clip=[11.5, 32.2, 15.5, 33.3])
R(-146, 699, 'romano_african', a0=['TUN'], clip=[8.5, 34.5, 11.5, 37.5])
R(1, 699, 'romano_african', a0=['DZA'], clip=[5.5, 35.7, 8.7, 37.1])
R(1100, E, 'arab', a0=['EGY'], cut=[[24.5, 28.8, 26.5, 29.5]])
R(1100, E, 'arab', a0=['LBY'], clip=[9, 26, 25.5, 34])
R(1100, E, 'arab', a0=['TUN'])
R(1300, E, 'arab', a0=['DZA'], clip=[-2.3, 32, 9, 37.2])
R(1300, E, 'berber', a1={'DZA': ['Tizi Ouzou', 'Béjaïa', 'Bouira', 'Batna', 'Khenchela', 'Ghardaïa']})
R(1500, E, 'arab', a1={'DZA': ['Adrar', 'Béchar', 'Tindouf', 'Ouargla', 'El Oued', 'Biskra', 'Djelfa', 'Laghouat', 'El Bayadh', 'Naâma']})
R(1600, E, 'arab', a1={'MAR': ['Gharb - Chrarda - Béni Hssen', 'Rabat - Salé - Zemmour - Zaer', 'Chaouia - Ouardigha', 'Grand Casablanca',
                                'Doukkala - Abda', 'Tanger - Tétouan', 'Fès - Boulemane']})
R(1500, E, 'moor', a1={'MAR': ['Guelmim - Es-Semara', 'Laâyoune - Boujdour - Sakia El Hamra', 'Oued el Dahab']}, a0=['SAH', 'MRT'])
R(1500, E, 'moor', a1={'MLI': ['Timbuktu']}, clip=[-12, 19, -3.5, 25])
R(-1000, E, 'fula', a1={'MRT': ['Gorgol', 'Guidimaka']})
R(1500, E, 'arab', a1={'LBY': ['Murzuq', 'Sabha', 'Wadi al Hayaa', "Ash Shati'", 'Al Jufrah', 'Al Kufrah']})
# West Africa
R(-3000, E, 'w_african', box=[-18, 4, 16, 17], cut=[[8.5, 4, 16, 7.5]])
R(-3000, E, 'w_african', a0=['NER', 'TCD', 'MLI', 'MRT', 'SEN'], clip=[-18, 4, 16, 17])
R(300, E, 'mande', a1={'MLI': ML_MANDE, 'GIN': GN_MANDE, 'SEN': SN_MANDE}, a0=['GMB'])
R(300, E, 'mande', a1={'MRT': ['Hodh ech Chargui', 'Hodh el Gharbi', 'Assaba']}, clip=[-13, 14.5, -5, 17.2])
R(500, E, 'wolof', a1={'SEN': SN_WOLOF})
R(1000, E, 'fula', a1={'SEN': ['Matam', 'Saint-Louis']}, clip=[-15.5, 14.8, -11.3, 16.8])
R(1700, E, 'fula', a1={'GIN': GN_FUTA})
R(1400, E, 'fula', a1={'MLI': ['Mopti']})
R(1815, E, 'fula', a1={'NGA': ['Adamawa', 'Gombe'], 'CMR': ['Adamaoua', 'Nord']})
R(800, E, 'songhai', a1={'MLI': ['Gao', 'Timbuktu'], 'NER': NE_SONGHAI}, clip=[-5, 11, 4.5, 17.2])
R(800, E, 'songhai', a1={'NER': NE_SONGHAI})
R(500, E, 'mossi', a0=['BFA'], a1={'GHA': GH_GUR, 'TGO': ['Savanes', 'Kara'], 'BEN': BJ_NORTH, 'CIV': ['Savanes']})
R(300, E, 'mande', a1={'CIV': ['Denguélé', 'Worodougou', 'Bafing']})
R(500, E, 'akan', a1={'GHA': GH_AKAN, 'CIV': CI_AKAN})
R(500, E, 'gbe', a1={'GHA': ['Volta'], 'TGO': ['Maritime', 'Plateaux', 'Centre'], 'BEN': BJ_SOUTH})
R(500, E, 'yoruba', a1={'NGA': NG_YORUBA, 'BEN': ['Plateau']})
R(500, E, 'edo', a1={'NGA': NG_EDO})
R(500, E, 'igbo', a1={'NGA': NG_IGBO})
R(500, E, 'cross_river', a1={'NGA': NG_DELTA})
R(500, E, 'middle_belt', a1={'NGA': NG_MIDDLE})
R(900, E, 'hausa', a1={'NGA': NG_HAUSA, 'NER': NE_HAUSA})
R(800, E, 'kanuri', a1={'NGA': ['Borno', 'Yobe'], 'NER': ['Diffa'], 'TCD': TD_KANEM})
R(500, E, 'kru', a0=['LBR', 'SLE', 'GNB'], a1={'CIV': CI_KRU, 'GIN': GN_COAST})
R(-1000, E, 'hausa', a1={'CMR': ['Extrême-Nord']})
# Sahel east, Sudan, Horn
R(-3000, E, 'sudanic', a1={'TCD': TD_SOUTH + TD_WADAI + TD_ARAB, 'SDN': SD_DARFUR + ['South Kordufan', 'North Kordufan']})
R(1600, E, 'chadian_arab', a1={'TCD': TD_ARAB})
R(1700, E, 'sudanese_arab', a1={'SDN': ['Southern Darfur', 'Eastern Darfur', 'North Kordufan']})
R(-3000, E, 'nilotic', a0=['SDS'], a1={'ETH': ['Gambela Peoples']})
R(-500, E, 'ubangian', a1={'SDS': ['Western Equatoria']}, a0=['CAF'])
R(-500, E, 'ubangian', a1={'COD': ['Orientale']}, clip=[22, 2.6, 31, 5.5])
R(500, E, 'ubangian', a1={'CMR': ['Adamaoua', 'Nord', 'Est']})
R(-3000, E, 'beja', a1={'SDN': ['Red Sea', 'Kassala', 'Gedarif'], 'ERI': ['Gash Barka', 'Semenawi Keyih Bahri']}, a0=['SDN'], clip=[33.5, 14, 38.7, 22.5])
R(-1500, 1399, 'nubian', a1={'SDN': SD_CENTRAL})
R(1400, E, 'sudanese_arab', a1={'SDN': ['River Nile', 'Khartoum', 'Gezira', 'White Nile']})
R(1400, E, 'sudanic', a1={'SDN': ['Sennar', 'Blue Nile']})
R(1700, E, 'sudanese_arab', a1={'SDN': ['Sennar', 'Gedarif']})
R(-3000, E, 'cushitic', a0=['ETH', 'ERI', 'DJI', 'SOM', 'SOL'])
R(-3000, E, 'cushitic', a0=['KEN', 'TZA'], clip=[33.5, -6, 42, 5])
R(-800, E, 'habesha', a1={'ETH': ['Tigray'], 'ERI': ER_HIGH})
R(900, E, 'habesha', a1={'ETH': ['Amhara']}, clip=[36, 11, 40.5, 15])
R(1300, E, 'habesha', a1={'ETH': ['Amhara', 'Addis Ababa']})
R(1550, E, 'oromo', a1={'ETH': ['Oromiya', 'Dire Dawa']})
R(-500, E, 'somali', a0=['SOM', 'SOL'], a1={'ETH': ['Somali'], 'KEN': ['North-Eastern'], 'DJI': ['Ali Sabieh', 'Djibouti', 'Arta']})
R(-500, E, 'afar', a1={'ETH': ['Afar'], 'ERI': ['Debubawi Keyih Bahri'], 'DJI': ['Tadjourah', 'Obock', 'Dikhil']})
R(-500, E, 'sudanic', a1={'ETH': ['Benshangul-Gumaz']})
# Bantu expansion and the south
R(-3000, E, 'khoisan', box=[[10, -35, 42, -3], [27, -10, 39.5, 1]])
R(-3000, -501, 'pygmy', a0=['COD', 'COG', 'GAB', 'CAF', 'CMR', 'GNQ'], clip=[8.5, -6, 31, 5])
R(-3000, E, 'bantu', a0=['CMR'], clip=[8.5, 2, 13.5, 7.5])
R(-1000, E, 'bantu', a0=['GAB', 'GNQ', 'COG', 'CMR'], clip=[8.5, -5.5, 19, 4.5])
R(-500, E, 'bantu', a0=['COD', 'AGO', 'COG', 'CAF'], clip=[11.5, -10, 31, 3.5])
R(1, E, 'bantu', a0=['UGA', 'RWA', 'BDI', 'TZA', 'COD', 'AGO', 'ZMB', 'MWI'], a1={'KEN': KE_BANTU})
R(300, E, 'bantu', a0=['ZWE', 'MOZ', 'ZMB', 'MWI', 'AGO', 'NAM'], clip=[11, -26.5, 41, -8])
R(500, E, 'bantu', a1={'ZAF': ZA_NGUNI + ['Limpopo', 'Gauteng', 'North West', 'Free State']}, a0=['SWZ', 'LSO', 'BWA'], clip=[22, -34, 33, -22],
  cut=[[22, -34.5, 26.2, -32.2]])
R(1000, E, 'kongo', a1={'COD': CD_KONGO, 'AGO': AO_KONGO, 'COG': CG_KONGO})
R(1000, E, 'luba_lunda', a1={'COD': CD_LUBA, 'AGO': AO_LUNDA, 'ZMB': ['North-Western']})
R(1000, E, 'congo_bantu', a1={'COD': CD_BASIN}, cut=[[22, 2.6, 31, 5.5]])
R(1000, E, 'great_lakes', a1={'COD': ['Nord-Kivu', 'Sud-Kivu'], 'TZA': ['Kagera']}, a0=['RWA', 'BDI'])
R(1000, E, 'great_lakes', a0=['UGA'], cut=UG_NORTH)
R(1000, E, 'nilotic', a0=['UGA'], clip=UG_NORTH)
R(1000, E, 'mbundu', a1={'AGO': AO_MBUNDU})
R(1000, E, 'fang', a0=['GAB', 'GNQ'], a1={'CMR': ['Sud', 'Centre', 'Littoral', 'Sud-Ouest']})
R(1000, E, 'e_bantu', a1={'KEN': KE_BANTU}, a1x={'TZA': ['Kagera']}, cut=[[38.7, -11, 42, -4.4]])
R(1, E, 'nilotic', a1={'KEN': ['Rift Valley']})
R(1500, E, 'nilotic', a1={'KEN': ['Nyanza']})
R(1700, E, 'nilotic', a1={'TZA': ['Arusha', 'Manyara']})
R(900, E, 'swahili', a1={'TZA': ['Zanzibar South and Central', 'Kaskazini-Unguja', 'Zanzibar West', 'Kusini-Pemba', 'Kaskazini-Pemba', 'Dar-Es-Salaam']},
  a0=['COM'])
R(900, E, 'swahili', a0=['KEN', 'TZA', 'SOM'], clip=[[39.0, -10.6, 40.6, -4.6], [39.3, -4.6, 41.3, -1.5]])
R(1000, E, 'shona', a0=['ZWE'], a1={'MOZ': ['Manica']})
R(1840, E, 'nguni', a1={'ZWE': ['Matabeleland North', 'Matabeleland South', 'Bulawayo']})
R(1000, E, 'nguni', a1={'ZAF': ZA_NGUNI}, a0=['SWZ'], cut=[[22, -34.5, 26.2, -32.2]])
R(1000, E, 'sotho', a1={'ZAF': ZA_SOTHO}, a0=['LSO'])
R(1500, E, 'sotho', a1={'BWA': ['Central', 'Kgatleng', 'South-East', 'Southern', 'Kweneng', 'Gaborone', 'Lobatse', 'Francistown', 'Selebi-Phikwe', 'Sowa',
                                'Jwaneng', 'North-East']})
R(1000, E, 'maravi', a0=['MWI'], a1={'MOZ': MZ_NORTH, 'ZMB': ['Eastern']})
R(1000, E, 'tsonga', a1={'MOZ': MZ_SOUTH})
R(1000, E, 'bemba', a0=['ZMB'], a1x={'ZMB': ['Eastern', 'North-Western']})
R(1000, E, 'herero', a1={'NAM': NA_NORTH, 'AGO': ['Cunene', 'Namibe']})
R(1715, E, 'afrikaner', a1={'ZAF': ['Western Cape']})
R(1880, E, 'afrikaner', a1={'ZAF': ['Northern Cape']})
R(1500, 1799, 'kongo', a0=['AGO'], clip=[12.2, -8.6, 16.2, -5.5])

# ================================================================== 10. North America
NA = dict(cont='North America')
R(-3000, E, 'algonquian', a1={'USA': US_NE + US_LAKES + ['Virginia']}, a0=['CAN'], cut=[[-150, 55, -50, 85]])
R(-3000, E, 'algonquian', a1={'USA': ['Minnesota', 'Montana']}, clip=[-116, 46, -89, 49.5])
R(-3000, E, 'dene', a1={'CAN': ['Yukon', 'Northwest Territories', 'British Columbia', 'Alberta', 'Saskatchewan']}, clip=[-141, 54.5, -102, 69])
R(-3000, E, 'dene', a1={'USA': ['Alaska']}, clip=[-157.5, 57, -141, 67.5])
R(-3000, E, 'algonquian', a1={'CAN': ['Saskatchewan', 'Manitoba', 'Ontario', 'Québec', 'Newfoundland and Labrador']}, clip=[-110, 49, -55, 60.5])
R(-3000, E, 'iroquoian', a1={'USA': ['New York', 'Pennsylvania']})
R(-3000, E, 'iroquoian', a1={'CAN': ['Ontario']}, clip=[-82.6, 41.6, -75.5, 45.3])
R(-3000, 1599, 'iroquoian', a1={'CAN': ['Québec']}, clip=[-74.5, 45.3, -70.5, 47])
R(-3000, E, 'iroquoian', a0=['USA'], clip=[-85.6, 34.3, -81.6, 36.7])                       # Cherokee
R(-3000, E, 'siouan', a1={'USA': US_PLAINS + ['Nebraska', 'Kansas', 'Wyoming']}, clip=[-108, 36.9, -89, 49.5])
R(-3000, E, 'muskogean', a1={'USA': US_SE + ['Louisiana', 'Arkansas']}, cut=[[-85.6, 34.3, -81.6, 36.7]])
R(-3000, E, 'algonquian', a1={'USA': ['Kentucky', 'Tennessee']}, clip=[-89.6, 36.6, -81.9, 39.2])
R(-3000, E, 'aridoamerican', a1={'USA': ['Texas']}, clip=[-106.7, 25.8, -97, 31.5])
R(1500, E, 'apache', a1={'USA': ['Texas', 'New Mexico', 'Oklahoma']}, clip=[-104.5, 31.5, -100, 37])
R(-3000, E, 'caddoan', a1={'USA': ['Texas', 'Oklahoma', 'Arkansas', 'Louisiana', 'Kansas', 'Nebraska']}, clip=[-100, 29.5, -92.4, 42.5],
  cut=[[-94.6, 35.5, -89, 37]])
R(-3000, E, 'numic', a1={'USA': US_BASIN + ['Colorado', 'Idaho', 'Wyoming', 'Oregon', 'California', 'Arizona']}, clip=[-121, 35, -105, 45])
R(-3000, E, 'californian', a1={'USA': ['California']}, cut=[[-118, 33, -114, 37.5]])
R(-3000, E, 'nw_coast', a1={'USA': ['Washington', 'Oregon']}, clip=[-125, 42, -121.2, 49.1])
R(-3000, E, 'nw_coast', a1={'CAN': ['British Columbia']}, clip=[-133.5, 48.2, -122.6, 55.5])
R(-3000, E, 'nw_coast', a1={'USA': ['Alaska']}, clip=[-141, 54.5, -129.9, 60.5])
R(-3000, E, 'plateau', a1={'USA': ['Washington', 'Oregon', 'Idaho', 'Montana']}, clip=[-121.2, 44, -112, 49.1])
R(-3000, E, 'plateau', a1={'CAN': ['British Columbia']}, clip=[-122.6, 48.9, -114, 54.5])
R(-3000, E, 'pueblo', a1={'USA': ['Arizona', 'New Mexico', 'Utah', 'Colorado']}, clip=[-115, 31.3, -103, 37.5])
R(-3000, E, 'inuit', a0=['GRL'])
R(-3000, E, 'inuit', a1={'CAN': ['Nunavut']})
R(-3000, E, 'inuit', a1={'CAN': ['Northwest Territories']}, clip=[-141, 67.5, -100, 80])
R(-3000, E, 'inuit', a1={'CAN': ['Québec']}, clip=[-80, 58.3, -60, 63])
R(-3000, E, 'inuit', a1={'CAN': ['Newfoundland and Labrador']}, clip=[-65, 55.3, -55, 61])
R(-3000, E, 'inuit', a1={'USA': ['Alaska']}, clip=[-170, 67.5, -140, 72])
R(-3000, E, 'inuit', a1={'USA': ['Alaska']}, clip=[-180, 51, -157.5, 67.5])
R(-3000, E, 'inuit', a1={'USA': ['Alaska']}, clip=[170, 51, 180, 56])
R(1500, E, 'apache', a1={'USA': ['Arizona', 'New Mexico']}, cut=[[-107.6, 32.5, -105.6, 36.8], [-112.5, 31.3, -109.5, 33.5], [-111.5, 35.5, -109.6, 36.5]])
R(1700, E, 'numic', a1={'USA': ['Texas', 'Oklahoma', 'Kansas', 'Colorado', 'New Mexico']}, clip=[-104.5, 30, -98.3, 40])     # Comancheria
R(-3000, E, 'aridoamerican', a1={'MEX': MEX_N + ['Zacatecas', 'San Luis Potosí', 'Aguascalientes']})
R(800, 1599, 'mississippian', a1={'USA': ['Illinois', 'Missouri', 'Arkansas', 'Tennessee', 'Kentucky', 'Mississippi', 'Alabama', 'Georgia', 'Louisiana',
                                           'Oklahoma']}, clip=[-95.5, 30.8, -83, 39.6])
# European and African North America
R(1650, E, 'anglo_american', a1={'USA': ['Massachusetts', 'Connecticut', 'Rhode Island', 'Virginia', 'Maryland', 'New Hampshire']}, cut=[[-83.7, 36, -79.5, 40]])
R(1700, E, 'anglo_american', a1={'USA': ['New York', 'New Jersey', 'Pennsylvania', 'Delaware', 'Maryland', 'North Carolina', 'South Carolina', 'Maine',
                                          'Virginia']}, cut=[[-90, 34, -79.5, 43]])
R(1783, E, 'anglo_american', a1={'USA': ['New York', 'Pennsylvania', 'Virginia', 'West Virginia', 'North Carolina', 'South Carolina', 'Georgia', 'Vermont',
                                          'Maine']})
R(1800, E, 'anglo_american', a1={'USA': ['Kentucky', 'Tennessee']})
R(1815, E, 'anglo_american', a1={'USA': ['Ohio', 'Indiana', 'Mississippi', 'Alabama']}, cut=[[-88.2, 30.2, -84.8, 35], [-86.5, 39.8, -84.8, 41.8]])
R(1848, E, 'anglo_american', a1={'USA': ['Ohio', 'Indiana', 'Illinois', 'Michigan', 'Wisconsin', 'Iowa', 'Missouri', 'Arkansas', 'Alabama', 'Mississippi',
                                          'Florida', 'Texas', 'Georgia', 'Tennessee', 'Kentucky']}, cut=[[-100.5, 25.8, -96.3, 30.5]])
R(1848, E, 'anglo_american', a1={'USA': ['Utah']}, clip=[-112.6, 39.3, -111.2, 42.1])
R(1871, E, 'anglo_american', a1={'USA': ['Utah', 'Minnesota', 'Kansas', 'Nebraska', 'California', 'Oregon', 'Washington', 'Nevada', 'Colorado', 'Texas']})
R(1880, E, 'anglo_american', a1={'USA': ['North Dakota', 'South Dakota', 'Montana', 'Idaho', 'Wyoming']})
R(1900, E, 'anglo_american', a1x={'USA': ['Alaska', 'Hawaii']}, cut=[[-109.1, 31.3, -103, 37.1]])
R(1945, E, 'anglo_american', a1={'USA': ['Alaska']}, clip=[-157.5, 55, -130, 65])
R(1715, 1920, 'african_american', a1={'USA': ['South Carolina']})
R(1848, 1930, 'african_american', a1={'USA': ['Mississippi']})
R(1715, 1814, 'french', a1={'USA': ['Louisiana']}, clip=[-93.8, 29, -89, 31.2])
R(1815, 1899, 'african_american', a1={'USA': ['Louisiana']})
R(1650, E, 'mexican', a1={'USA': ['New Mexico']}, clip=[-107.6, 32.5, -105.6, 36.8])
R(1750, E, 'mexican', a1={'USA': ['Texas']}, clip=[-100.5, 25.8, -97.3, 29.3])
R(1650, E, 'quebecois', a1={'CAN': ['Québec']}, clip=[-75, 45, -64, 49.3])
R(1900, E, 'quebecois', a1={'CAN': ['Québec']}, clip=[-80, 45, -60, 52])
R(1650, 1754, 'quebecois', a1={'CAN': ['Nova Scotia', 'New Brunswick', 'Prince Edward Island']})
R(1945, E, 'quebecois', a1={'CAN': ['New Brunswick']}, clip=[-68.5, 46.8, -64, 48.1])
R(1783, E, 'anglo_canadian', a1={'CAN': ['Nova Scotia', 'New Brunswick', 'Prince Edward Island']}, cut=[[-68.5, 46.8, -64, 48.1]])
R(1715, E, 'anglo_canadian', a1={'CAN': ['Newfoundland and Labrador']}, clip=[-56, 46.5, -52.5, 49.5])
R(1815, E, 'anglo_canadian', a1={'CAN': ['Newfoundland and Labrador']}, clip=[-60, 46.5, -52.5, 52])
R(1815, E, 'anglo_canadian', a1={'CAN': ['Ontario']}, clip=[-83.2, 41.6, -74.3, 45.5])
R(1900, E, 'anglo_canadian', a1={'CAN': ['Ontario', 'Manitoba', 'Saskatchewan', 'Alberta', 'British Columbia']}, clip=[-140, 41, -74, 55])
R(1900, E, 'anglo_canadian', a1={'CAN': ['Yukon']})
R(1960, E, 'anglo_canadian', a1={'CAN': ['Newfoundland and Labrador', 'Alberta', 'British Columbia']}, clip=[-140, 41, -55, 55.3])

# ================================================================== 11. Mesoamerica and the Caribbean
R(-3000, E, 'maya', a1={'MEX': MX_MAYA}, a0=['GTM', 'BLZ'])
R(-1500, -400, 'olmec', a1={'MEX': ['Veracruz', 'Tabasco']}, clip=[-96.5, 17, -93.3, 19])
R(-3000, E, 'otomanguean', a1={'MEX': ['Oaxaca', 'Querétaro', 'Guanajuato'] + MX_NAHUA})
R(-3000, E, 'nahua', a1={'MEX': ['Jalisco', 'Nayarit', 'Colima', 'Michoacán']})
R(600, E, 'nahua', a1={'MEX': MX_NAHUA})
R(600, E, 'otomanguean', a1={'MEX': ['Hidalgo', 'Querétaro']}, clip=[-100.5, 20, -98.6, 21.5])
R(1000, E, 'purepecha', a1={'MEX': ['Michoacán']})
R(-3000, E, 'lenca', a0=['SLV', 'HND', 'NIC'])
R(-500, 900, 'maya', a0=['HND'], clip=[-89.5, 14.2, -88, 15.8])
R(-3000, E, 'muisca', a0=['CRI', 'PAN'])
R(-3000, E, 'muisca', a0=['HND', 'NIC'], clip=[-85.5, 10.5, -82, 16.1])
R(1700, E, 'mexican', a1={'MEX': MEX_N + ['Zacatecas', 'Aguascalientes', 'Jalisco', 'Guanajuato', 'San Luis Potosí', 'Querétaro', 'Nayarit', 'Colima']})
R(1871, E, 'mexican', a1={'MEX': ['Distrito Federal', 'México', 'Morelos']})
R(1900, E, 'mexican', a1={'MEX': ['Puebla', 'Tlaxcala', 'Hidalgo', 'Veracruz', 'Michoacán', 'Tabasco']})
R(1945, E, 'mexican', a1={'MEX': ['Guerrero', 'Campeche', 'Quintana Roo', 'Yucatán']})
R(1960, E, 'mexican', a1={'MEX': ['Oaxaca', 'Chiapas']}, cut=[[-93.2, 16.2, -91.5, 17.4], [-97.5, 16.4, -95.5, 17.6]])
R(1800, E, 'central_am', a1={'GTM': GT_LADINO})
R(1960, E, 'central_am', a1={'GTM': ['Petén']})
R(1715, E, 'central_am', a0=['SLV'])
R(1783, E, 'central_am', a0=['HND', 'NIC'], clip=[-90, 10.7, -85.5, 16.1])
R(1945, E, 'central_am', a0=['HND', 'NIC'])
R(1700, E, 'central_am', a0=['CRI'])
R(1800, E, 'central_am', a0=['PAN'], clip=[-83.1, 7, -78.9, 9.7])
R(1815, 1994, 'afro_carib', a0=['BLZ'])
R(2000, E, 'central_am', a0=['BLZ'])
R(-500, 1529, 'arawak', a0=['CUB', 'DOM', 'HTI', 'PRI', 'JAM', 'BHS', 'TTO'])
R(1000, 1649, 'carib', a0=['ATG', 'KNA', 'DMA', 'LCA', 'VCT', 'GRD', 'BRB', 'GLP', 'MTQ', 'TTO'])
R(1600, E, 'hisp_carib', a0=['CUB', 'DOM', 'PRI'])
R(1650, E, 'afro_carib', a0=['ATG', 'KNA', 'DMA', 'LCA', 'VCT', 'GRD', 'BRB', 'GLP', 'MTQ'])
R(1700, E, 'afro_carib', a0=['HTI', 'JAM'])
R(1715, E, 'afro_carib', a0=['BHS'])
R(1800, E, 'afro_carib', a0=['TTO'])

# ================================================================== 12. South America
R(-3000, E, 'amazonian', cont='South America')
R(-1000, E, 'tupi', a1={'BRA': BR_TUPI}, a0=['PRY', 'URY'])
R(-1000, E, 'tupi', a1={'ARG': AR_LITORAL})
R(-1000, E, 'ge', a1={'BRA': BR_GE})
R(-1000, E, 'carib', a0=['GUY', 'SUR', 'GUF'], a1={'VEN': ['Bolívar', 'Anzoátegui', 'Monagas', 'Sucre', 'Nueva Esparta', 'Miranda', 'Distrito Capital',
                                                          'Vargas', 'Aragua', 'Carabobo'], 'BRA': ['Roraima', 'Amapá'], 'COL': CO_COAST})
R(-1000, E, 'arawak', a1={'VEN': ['Zulia', 'Falcón', 'Lara', 'Yaracuy', 'Delta Amacuro', 'Apure', 'Guárico', 'Cojedes', 'Barinas', 'Portuguesa'],
                          'COL': CO_LLANOS + ['La Guajira']})
R(-1000, E, 'muisca', a1={'COL': CO_ANDES, 'VEN': VE_ANDES}, a0=['PAN'], clip=[-79, 0, -60, 12])
R(-1000, E, 'mapuche', a1={'CHL': CL_CENTRAL + CL_SOUTH, 'ARG': ['Neuquén']})
R(-1000, E, 'patagonian', a1={'CHL': CL_PATAG, 'ARG': AR_PATAGONIA + AR_PAMPA}, a0=['URY'])
R(-1000, E, 'chaco', a1={'ARG': ['Chaco', 'Formosa'], 'PRY': PY_CHACO, 'BOL': ['Tarija']}, clip=[-66, -27.5, -57, -19])
R(-1000, E, 'diaguita', a1={'ARG': AR_NW, 'CHL': ['Atacama', 'Coquimbo']})
R(-1500, 499, 'chavin', a0=['PER'], a1x={'PER': PE_LOW})
R(100, 1470, 'mochica', a1={'PER': PE_NCOAST})
R(-500, E, 'aymara', a1={'PER': ['Puno', 'Tacna', 'Moquegua'], 'BOL': BO_ALTI + BO_VALLEY, 'CHL': CL_NORTH})
R(500, E, 'quechua', a1={'PER': PE_HIGH + ['Lima', 'Ica', 'Callao']})
R(1470, E, 'quechua', a1={'PER': ['La Libertad', 'Lambayeque', 'Piura', 'Tumbes', 'Cajamarca']})
R(1480, E, 'quechua', a1={'ECU': EC_HIGH + EC_COAST})
R(1500, E, 'quechua', a1={'BOL': BO_VALLEY + ['Potosí']})
R(1600, E, 'peruvian', a1={'PER': ['Lima', 'Lima Province', 'Callao', 'Ica']})
R(1700, E, 'peruvian', a1={'PER': PE_NCOAST + ['Arequipa', 'Moquegua', 'Tacna']}, a0=['ECU'], a1x={'ECU': EC_HIGH + EC_AMAZON})
R(1900, E, 'peruvian', a1={'ECU': EC_HIGH})
R(1960, E, 'peruvian', a1={'PER': ['Junín', 'Pasco', 'Huánuco', 'Áncash', 'Cajamarca', 'Lima Province', 'San Martín', 'Ucayali', 'Loreto', 'Madre de Dios']})
R(1880, E, 'chilean', a1={'CHL': CL_NORTH})
R(1650, E, 'colombian', a1={'COL': ['Cundinamarca', 'Boyacá', 'Santander', 'Bogota', 'Antioquia', 'Tolima', 'Huila', 'Valle del Cauca', 'Cauca', 'Caldas']})
R(1700, E, 'colombian', a1={'COL': CO_COAST + CO_ANDES, 'VEN': VE_CORE})
R(1800, E, 'colombian', a0=['COL', 'VEN'], a1x={'COL': CO_AMAZON + CO_LLANOS + ['La Guajira'], 'VEN': ['Bolívar', 'Amazonas', 'Delta Amacuro']})
R(1945, E, 'colombian', a1={'COL': CO_LLANOS, 'VEN': ['Bolívar']})
R(1960, E, 'colombian', a1={'COL': ['Caquetá', 'Putumayo', 'Guaviare']})
R(1800, E, 'afro_carib', a1={'COL': ['Chocó']})
R(1650, E, 'chilean', a1={'CHL': CL_CENTRAL[:5]})
R(1800, E, 'chilean', a1={'CHL': CL_CENTRAL + ['Atacama']})
R(1880, E, 'chilean', a1={'CHL': ['Los Lagos', 'Los Ríos']})
R(1900, E, 'chilean', a1={'CHL': ['La Araucanía'] + CL_PATAG})
R(1650, E, 'argentine', a1={'ARG': ['Ciudad de Buenos Aires', 'Santa Fe', 'Córdoba', 'Tucumán', 'Mendoza', 'San Juan', 'Salta', 'Santiago del Estero']})
R(1650, E, 'argentine', a1={'ARG': ['Buenos Aires']}, clip=[-61, -35.6, -57, -33])
R(1700, E, 'argentine', a1={'ARG': AR_NW + AR_LITORAL})
R(1783, E, 'argentine', a0=['URY'])
R(1880, E, 'argentine', a1={'ARG': ['Buenos Aires', 'La Pampa', 'San Luis', 'Córdoba']})
R(1900, E, 'argentine', a1={'ARG': AR_PATAGONIA})
R(1945, E, 'argentine', a1={'ARG': ['Chaco', 'Formosa']})
R(1650, E, 'paraguayan', a0=['PRY'], a1x={'PRY': PY_CHACO})
R(1960, E, 'paraguayan', a1={'PRY': PY_CHACO})
R(1783, E, 'bolivian', a1={'BOL': ['Santa Cruz', 'Tarija']})
R(1945, E, 'bolivian', a1={'BOL': ['El Beni', 'Pando']})
R(1600, E, 'brazilian', a1={'BRA': BR_COAST})
R(1700, E, 'brazilian', a1={'BRA': BR_1700})
R(1700, E, 'brazilian', a1={'BRA': ['Pará']}, clip=[-50, -3, -46, 0])
R(1783, E, 'brazilian', a1={'BRA': BR_1783})
R(1900, E, 'brazilian', a0=['BRA'])
R(1783, E, 'afro_carib', a0=['GUY', 'SUR', 'GUF'], clip=[-62, 4.5, -51.5, 9])
R(1945, E, 'hindustani', a0=['GUY'], clip=[-62, 4.5, -56, 9])
R(1960, E, 'hindustani', a0=['SUR'], clip=[-57.2, 5.2, -54, 6.1])

# ================================================================== 13. Iberia after 711 (appended last so it overrides the generic rules)
R(750, 1084, 'andalusi', a0=['ESP', 'PRT', 'GIB'], clip=[-10, 35.8, 4.5, 41.0], cut=[[-1.2, 41.0, 4.5, 43], [-10, 40.3, -7.9, 42]])
R(750, 1117, 'andalusi', a1={'ESP': ['Zaragoza', 'Huesca', 'Teruel', 'Lérida']}, clip=[-2.0, 40.0, 1.0, 42.2])
R(1085, 1211, 'andalusi', a0=['ESP', 'PRT', 'GIB'], clip=[-10, 35.8, 4.5, 39.8], cut=[[-10, 38.3, -7.5, 39.8]])
R(1212, 1249, 'andalusi', a1={'ESP': GRANADA + ['Sevilla', 'Cádiz', 'Huelva', 'Murcia', 'Valencia', 'Alicante', 'Jaén']}, a0=['PRT'], clip=[-10, 35.8, 4.5, 39.6],
  cut=[[-10, 37.6, -7.5, 39.6]])
R(1250, 1491, 'andalusi', a1={'ESP': GRANADA})
R(750, E, 'castilian', a1={'ESP': ['Asturias', 'Cantabria', 'León', 'Burgos', 'Palencia', 'Álava', 'La Rioja']}, clip=[-7.1, 42.0, -1.6, 43.8])
R(800, E, 'castilian', a1={'ESP': CASTILE_OLD})
R(1085, E, 'castilian', a1={'ESP': CASTILE_NEW})
R(1250, E, 'castilian', a1={'ESP': CASTILE_SOUTH})
R(1492, E, 'castilian', a1={'ESP': GRANADA})
R(1500, E, 'castilian', a1={'ESP': ['Santa Cruz de Tenerife', 'Las Palmas'], })
R(-1000, 1499, 'berber', a1={'ESP': ['Santa Cruz de Tenerife', 'Las Palmas']})
R(-3000, 1599, 'basque', a1={'ESP': ['Álava']})
R(-3000, E, 'basque', a1={'ESP': BASQUE_C})
R(-3000, 1499, 'basque', a1={'ESP': ['Navarra']}, clip=[-2.5, 42.6, -0.7, 43.4])
R(800, E, 'catalan', a1={'ESP': CATALONIA})
R(1238, E, 'catalan', a1={'ESP': ['Castellón', 'Valencia', 'Alicante']}, clip=[-0.9, 37.8, 0.6, 40.8])
R(1229, E, 'catalan', a1={'ESP': ['Baleares']}, a0=['AND'])
R(800, E, 'galician', a1={'ESP': GALICIA})
R(800, 1139, 'galician', a0=['PRT'], clip=[-10, 40.3, -6, 42.2])
R(1140, E, 'portuguese', a0=['PRT'], clip=[-10, 40.0, -6, 42.2])
R(1147, E, 'portuguese', a0=['PRT'], clip=[-10, 38.3, -6, 42.2])
R(1250, E, 'portuguese', a0=['PRT'])

# late overrides
R(1945, 1960, 'indo_fijian', a0=['FJI'])


# ------------------------------------------------------------------ gap pass (15 Oct 2026): places that fell through to the
# world default ("Hunter-gatherers"). gap=True rules only repaint pixels still holding that default. 'na' = unknown or uncertain.
def G(y0, y1, cul, note, **where): R(y0, y1, cul, gap=True, note=note, **where)
CY = dict(a0=['CYP'])
G(B, 1960, '@like', 'Cyprus enclaves follow the rest of the island', a0=['CYN', 'CNM', 'ESB', 'WSB'], like=CY)
G(1961, E, 'turkish', 'Northern Cyprus: Turkish Cypriot since 1974', a0=['CYN'])
G(1961, E, 'na', 'Cyprus UN buffer zone: demilitarised, almost no residents', a0=['CNM'])
G(1961, E, '@like', 'British bases on Cyprus follow the Republic', a0=['ESB', 'WSB'], like=CY)
G(B, E, '@like', 'Åland follows Sweden (Swedish-speaking)', a0=['ALD'], like=dict(a0=['SWE']))
G(B, E, '@like', 'Andorra follows Catalonia', a0=['AND'], like=dict(a1={'ESP': ['Lérida']}))
G(B, E, '@like', 'Liechtenstein follows Vorarlberg', a0=['LIE'], like=dict(a1={'AUT': ['Vorarlberg']}))
G(B, E, '@like', 'Monaco follows Alpes-Maritimes', a0=['MCO'], like=dict(a1={'FRA': ['Alpes-Maritimes']}))
G(B, 1830, '@like', 'Jersey follows Normandy', a0=['JEY'], like=dict(a1={'FRA': ['Manche']}))
G(1831, E, 'english', 'Jersey: English-speaking majority since the 1800s', a0=['JEY'])
G(B, E, '@like', 'Hong Kong follows Guangdong', a0=['HKG', 'MAC'], like=dict(a1={'CHN': ['Guangdong']}))
G(B, E, '@like', 'Baikonur follows Qyzylorda', a0=['KAB'], like=dict(a1={'KAZ': ['Qyzylorda']}))
G(B, E, '@like', 'Kosovo follows Serbia', a0=['KOS'], like=dict(a0=['SRB']))
G(B, E, '@like', 'Guantanamo Bay follows Cuba', a0=['USG'], like=dict(a1={'CUB': ['Guantánamo']}))
G(B, E, 'na', 'Siachen Glacier: uninhabited glacier', a0=['KAS'])
G(B, E, 'na', 'Bir Tawil: uninhabited desert', a0=['BRT'])
G(B, E, 'na', 'Antarctic and sub-Antarctic islands: no permanent population', a0=['ATF', 'HMD', 'SGS', 'ATA'])
G(B, E, 'na', 'Christmas, Cocos and Chagos islands: very small, mixed or military populations', a0=['IOA', 'IOT'])
# Caribbean small islands
LA = ['ATG', 'BRB', 'DMA', 'LCA', 'VCT', 'GRD', 'KNA', 'AIA', 'MSR', 'MAF', 'BLM', 'VIR', 'VGB', 'ABW', 'CUW', 'TCA', 'CYM']
G(-800, 1492, 'arawak', 'Lesser Antilles and Dutch islands before 1492: Arawakan (Taino, Igneri, Caquetio, Lucayan) peoples', a0=LA)
G(1493, 1649, 'na', 'Caribbean islands after contact: native peoples dying out, few settlers yet', a0=LA + ['BHS', 'HTI', 'TTO'])
G(1650, E, 'afro_carib', 'Caribbean islands: Afro-Caribbean majority', a0=[c for c in LA if c != 'BLM'])
G(1650, E, 'french', 'Saint-Barthelemy: French-descended majority', a0=['BLM'])
G(1493, 1650, 'hisp_carib', 'Cuba, Hispaniola, Puerto Rico and Jamaica under early Spanish rule', a0=['CUB', 'DOM', 'PRI', 'JAM'])
G(1650, 1783, 'na', 'Bahamas and Trinidad: small, mixed populations', a0=['BHS', 'TTO'])
G(B, 1600, 'na', 'Saint Pierre and Miquelon: no settled population', a0=['SPM'])
G(1601, E, 'french', 'Saint Pierre and Miquelon: French', a0=['SPM'])
G(1900, E, 'na', 'Cabo Verde, Sao Tome and Seychelles: Creole peoples (no category on this map)', a0=['CPV', 'STP', 'SYC'])
G(1900, E, 'hindustani', 'Mauritius: Indo-Mauritian (mostly Bhojpuri-descended) majority', a0=['MUS'])
G(1700, E, 'english', 'Saint Helena: English-speaking', a0=['SHN'])
G(1914, 1945, 'japanese', 'Northern Marianas under Japan: Japanese settlers outnumbered Chamorros', a0=['MNP'])
G(B, E, 'na', 'Micronesia (Chamorro, Palauan, Chuukese, I-Kiribati): no Micronesian category on this map', a0=['GUM', 'MNP', 'PLW', 'FSM', 'KIR', 'MHL', 'NRU'])
# uninhabited before first settlement
G(B, 1210, 'na', 'New Zealand before Maori settlement (c. 1250-1300; earlier dates disputed): probably uninhabited', a0=['NZL'])
G(1211, 1279, 'maori', 'New Zealand: first Maori settlement', a0=['NZL'])
G(B, 860, 'na', 'Iceland before Norse settlement (c. 870): uninhabited', a0=['ISL'])
G(B, 400, 'na', 'Madagascar before Austronesian and Bantu settlement: few or no people', a0=['MDG'])
G(B, 1910, 'na', 'Svalbard: uninhabited until mining settlements', a1={'NOR': ['Svalbard']})
# Europe and western Asia
G(-800, -1, 'na', 'Pannonian Basin before Rome: Celtic, Scythian and Dacian peoples mixed', a0=['HUN', 'SVK', 'SVN', 'SRB', 'MKD', 'POL'])
G(1, 399, 'sarmatian', 'Great Hungarian Plain: Sarmatian Iazyges', a0=['HUN'])
G(400, 453, 'hunnic', 'Great Hungarian Plain: Hunnic heartland', a0=['HUN'])
G(454, 800, 'na', 'Pannonian Basin: Gepids, Lombards and Avars in turn', a0=['HUN', 'SVN', 'SRB', 'MKD', 'ROU'])
G(1, 400, 'gallo_roman', 'Roman Switzerland: Romanised Helvetii', a0=['CHE', 'LIE'])
G(-800, -323, 'cauc_albanian', 'Eastern Transcaucasia: Caucasian Albanian peoples', a0=['AZE'])
G(-800, -1, 'na', 'Transjordan: Edomites, Moabites and Nabataeans', a0=['JOR'])
G(1, 1000, 'na', 'Central Asian steppe and desert: shifting Iranian and Turkic peoples', a0=['TKM', 'KGZ'])
G(1000, 1279, 'na', 'Moldavia: Vlachs, Slavs, Pechenegs and Cumans', a0=['MDA'])
G(900, 1100, 'kipchak', 'Central Kazakh steppe: Kimek and Kipchak tribes', a1={'KAZ': ['East Kazakhstan', 'Qaraghandy']})
G(1100, 1450, 'greek', 'Chaldia (Gumushane): Greek, Empire of Trebizond', a1={'TUR': ['Gümüshane']})
G(1100, 1530, 'georgian', 'Artvin: Georgian (Tao-Klarjeti) until Ottoman conquest', a1={'TUR': ['Artvin']})
G(1100, 1530, 'armenian', 'Igdir: Armenian', a1={'TUR': ['Iğdir']})
G(1100, 1530, 'na', 'Sanliurfa (Edessa): Arab, Kurdish, Armenian and Syriac, too mixed to name', a1={'TUR': ['Sanliurfa']})
G(1000, 1200, 'andalusi', 'Gharb al-Andalus and Sharq al-Andalus under Muslim rule', a1={'PRT': ['Santarém', 'Évora', 'Castelo Branco', 'Leiria', 'Portalegre', 'Coimbra', 'Setúbal', 'Lisboa', 'Beja'], 'ESP': ['Cáceres', 'Castellón', 'Baleares', 'Valencia']})
# Russia and Siberia
G(1000, 1350, 'finnic', 'Zavolochye (Arkhangelsk): Finnic peoples ("Chud") and early Russian settlers', a1={'RUS': ["Arkhangel'sk"]})
G(1000, E, 'volga_finn', 'Komi, Udmurt and Mari lands: Permian and Volga Finnic peoples', a1={'RUS': ['Komi', 'Udmurt', 'Mariy-El']})
G(1000, 1860, 'sami', 'Kola Peninsula: Sami', a1={'RUS': ['Murmansk']})
G(1861, E, 'russian', 'Kola Peninsula: Russian majority', a1={'RUS': ['Murmansk']})
G(1000, 1700, 'tuvan', 'Altai and the Kuznetsk basin: Altai, Teleut and Shor Turks', a1={'RUS': ['Altay', 'Kemerovo']})
G(1000, 1700, 'tatar', 'Baraba and Irtysh: Siberian Tatars', a1={'RUS': ['Novosibirsk', 'Omsk']})
# North America: named peoples on the border map first, then whole states
_ALG = ['Arapaho', 'Delaware', 'Secotan', 'Roanoke', 'Croatan', 'Hatteras', 'Chowanoke', 'Pamlico (Pomouik)', 'WiYaPeMiAk (Weapemeoc-Yeopim)',
        'Yeopim', 'Poteskeet', 'Perquimans', 'Mattamuskeet', 'Moratok']
_SIO = ['Catawba', 'Eno', 'Occaneechi', 'Shakori', 'Sissipahaw', 'Keyauwee', 'Sugaree', 'Waccamaw (Woccon)', 'Cape Fear', 'Tutelo', 'Moneton']
G(1000, 1850, 'algonquian', 'Named Algonquian peoples (Carolina Algonquians, Lenape, Arapaho)', ent=_ALG)
G(1000, 1850, 'siouan', 'Named Siouan peoples of the Carolinas and Virginia', ent=_SIO)
G(1000, 1850, 'iroquoian', 'Tuscarora, Neusiok and Coree', ent=['Skaruhreh/Tuscarora (North Carolina)', 'Neusiok', 'Coree'])
G(1000, 1850, 'numic', 'Comanche', ent=['Nʉmʉnʉʉ (Comanche)'])
G(1000, 1850, 'apache', 'Jicarilla Apache', ent=['Jicarilla Apache'])
G(1000, 1850, 'pueblo', 'Hopi and Tigua (Pueblo peoples)', ent=['Hopi', 'Tigua'])
G(1000, 1850, 'californian', 'California peoples', a1={'USA': ['California']})
G(1000, 1850, 'caddoan', 'Oklahoma: Caddoan peoples (Wichita, Caddo)', a1={'USA': ['Oklahoma']})
G(1600, 1850, 'siouan', 'Missouri: Siouan peoples (Osage, Missouria)', a1={'USA': ['Missouri']})
G(1000, 1850, 'na', 'Texas, Colorado, Montana, North Carolina and West Virginia: several unrelated peoples, too mixed to name one', a1={'USA': ['Texas', 'Colorado', 'Montana', 'North Carolina', 'West Virginia']})
# East Asia
G(1600, 1800, 'formosan', 'Taiwan outside Dutch and Qing settlement: Taiwanese indigenous peoples', a0=['TWN'])
G(1869, 1880, 'japanese', 'Hokkaido after Japanese settlement', a1={'JPN': ['Hokkaidō']})
G(1066, 1150, 'greek', 'Anatolia after Manzikert: Greek-speaking majority under Seljuk rule', a0=['TUR'])
G(1151, 1279, 'na', 'Anatolia under the Seljuks of Rum: Greek, Armenian and Turkish, too mixed to name', a0=['TUR'])
G(1650, 1700, 'na', 'Western Hispaniola: buccaneers and early French settlers, few people', a0=['HTI'])
