"""Derive the 1975 map, the end of the Vietnam War and of Portugal's empire, from the 1989 map (make_1989.py).
Usage: python3 make_1975.py <site folder>     (writes <site>/eras/1975.json and updates <site>/data/*.json)

The map shows the world at the end of 1975. Changes from 1989:
  - Vietnam is North and South Vietnam, divided as on the 1960 map. Saigon fell on 30 April 1975; the South was run
    by the Provisional Revolutionary Government as the Republic of South Vietnam until reunification on 2 July 1976;
  - Zimbabwe is Rhodesia (white-minority rule from the unrecognised declaration of independence of 1965 to 1979);
  - Western Sahara is Spanish Sahara (Spain withdrew in February 1976, after the Madrid Accords of November 1975);
  - the Sinai Peninsula, taken by Israel in 1967, is under Israeli occupation (returned to Egypt by 1982);
  - East Timor declared independence from Portugal on 28 November 1975 and was invaded by Indonesia on 7 December
    (annexed in 1976); it is shown on its own, outlined as the 2026 map's Timor-Leste;
  - British Honduras (Belize, independent 1981), Brunei (a British protectorate until 1984), the West Indies
    Associated States (Antigua, Saint Kitts-Nevis, Saint Lucia, Saint Vincent and Dominica, independent 1978-1983),
    the Seychelles (1976), the British Solomon Islands (1978) and the Gilbert Islands (Kiribati, 1979) are British;
    the New Hebrides (Vanuatu, 1980) were an Anglo-French condominium; Djibouti (1977) was the French Territory of
    the Afars and the Issas;
  - Burkina Faso is Upper Volta (renamed 1984) and Myanmar is Burma (renamed 1989).
Everything else is the 1989 map's. Borders, areas and labels are re-traced with era_tools.py; the faith, culture and
development layers are painted for 1975 afterwards by the overlay rules (../overlays). Run from
data-source/scripts/derive-2026/."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import era_tools as T, cold_war as C

SITE = sys.argv[1]
D = T.Derive(SITE, '1989')
j60, i60 = C.era_ids(SITE, '1960')
j26, i26 = C.era_ids(SITE, '2026')
R = lambda name: D.realm(name)
n = {}

south = C.nearest_split(C.ent_mask(j60, i60, 'South Vietnam'), C.ent_mask(j60, i60, 'North Vietnam'))
n['South Vietnam'] = D.take('South Vietnam', D.realm('South Vietnam', g=C.g_of(SITE, '1960', 'South Vietnam')), south, ['Vietnam'])
D.rename('Vietnam', 'North Vietnam', realm=D.realm('North Vietnam', g=C.g_of(SITE, '1960', 'North Vietnam')))
D.rename('Zimbabwe', 'Rhodesia', realm=D.realm('Rhodesia', g=C.g_of(SITE, '1989', 'Zimbabwe')))
D.rename('Western Sahara', 'Spanish Sahara', realm=R('Spain'))
SINAI = [[32.28, 31.42], [32.42, 30.6], [32.58, 29.95], [33.4, 28.9], [34.25, 27.6], [35.3, 27.6], [35.3, 31.42]]
n['Sinai'] = D.take('Sinai (Israeli-occupied)', R('Israel'), T.geo_mask(SINAI), ['Egypt'])
n['East Timor'] = D.take('East Timor', D.realm('East Timor', g=C.g_of(SITE, '2026', 'Timor-Leste')), C.ent_mask(j26, i26, 'Timor-Leste'), ['Indonesia'])
uk, fr = R('United Kingdom'), R('France')
for old, new, realm in [('Belize', 'British Honduras', uk), ('Brunei', 'Brunei', uk), ('Antigua and Barbuda', 'Antigua', uk),
                        ('Saint Kitts and Nevis', 'Saint Kitts-Nevis', uk), ('Saint Lucia', 'Saint Lucia', uk),
                        ('Saint Vincent and the Grenadines', 'Saint Vincent', uk), ('Dominica', 'Dominica', uk),
                        ('Seychelles', 'Seychelles', uk), ('Solomon Islands', 'British Solomon Islands', uk),
                        ('Kiribati', 'Gilbert Islands', uk), ('Djibouti', 'French Territory of the Afars and the Issas', fr)]:
    D.rename(old, new, realm=realm)
D.rename('Vanuatu', 'New Hebrides', realm=D.realm('New Hebrides', g=C.g_of(SITE, '2026', 'Vanuatu')))
D.rename('Burkina Faso', 'Upper Volta'); D.rename_realm('Burkina Faso', 'Upper Volta')
D.rename('Myanmar', 'Burma'); D.rename_realm('Myanmar', 'Burma')

notes = ['Built from the 1989 map, adjusted to the end of 1975.',
         'Saigon fell on 30 April 1975; North and South Vietnam were reunified on 2 July 1976. The Khmer Rouge took Phnom Penh on 17 April 1975, and the Lao monarchy was abolished on 2 December.',
         "Portugal's African colonies became independent in 1974–1975: Guinea-Bissau, Mozambique, Cape Verde, São Tomé and Príncipe and Angola. East Timor declared independence on 28 November 1975 and was invaded by Indonesia on 7 December.",
         'Rhodesia was ruled by its white minority under an unrecognised declaration of independence (1965–1979). South West Africa (Namibia) was held by South Africa, and Eritrea, annexed by Ethiopia in 1962, was fighting for independence.',
         'Spain agreed in November 1975 to leave Spanish Sahara, which Morocco and Mauritania divided in 1976. Israel held the Sinai, the West Bank, the Gaza Strip and the Golan Heights from 1967; the Sinai was returned to Egypt by 1982.',
         'Cyprus was divided after the Turkish invasion of 1974. The Lebanese Civil War began in April 1975.']
D.drop_notes = [x for x in D.src['notes'] if x.startswith(('The Berlin Wall', 'North Yemen and South Yemen', 'The West Bank, the Gaza'))]
out, ix = D.save(1975, '1975', 'The end of the Vietnam War', notes, 1989)
print('1975 written:', ', '.join(f'{k} {v:,} px' for k, v in n.items()), f"| {ix['n']} states, {ix['m']} peoples, {len(out['borders'])} border lines")
