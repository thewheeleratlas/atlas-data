"""Derive the 1989 map, the last year of the Cold War order, from the 1994 map.
Usage: python3 make_1989.py <site folder>     (writes <site>/eras/1989.json and updates <site>/data/*.json)

The map shows the world at the end of 1989, after the fall of the Berlin Wall (9 November) and before the changes
of 1990-1993. Changes from 1994:
  - the USSR: Russia and the fourteen other union republics are one territory, as on the 1960 map (it broke up in
    December 1991);
  - Yugoslavia (Slovenia, Croatia, Bosnia and Herzegovina, Macedonia, Serbia and Montenegro; broke up 1991-1992) and
    Czechoslovakia (split on 1 January 1993) are whole again;
  - Germany is East and West Germany (reunified 3 October 1990), split along the inner German border as the 1960 map
    draws it;
  - Yemen is North Yemen (the Yemen Arab Republic) and South Yemen (the People's Democratic Republic of Yemen),
    divided as the 1960 map's Kingdom of Yemen and Aden Protectorate (unified 22 May 1990), with Socotra, unclaimed on the
    source map, in South Yemen;
  - Eritrea is part of Ethiopia (annexed 1962; independent 1993);
  - Namibia is South West Africa, run by South Africa until independence on 21 March 1990;
  - the West Bank and the Gaza Strip, under Israeli occupation since 1967, are their own territories of Israel's
    realm, outlined as the 2026 map's Palestine;
  - small states and islands the 1994 source map leaves unclaimed are added with their 2026 outlines: Singapore,
    Bahrain, the Maldives, Mauritius, the Seychelles, the Comoros, Cape Verde, Sao Tome and Principe, the Solomon
    Islands, Vanuatu and Kiribati;
  - dependencies the 1994 source map shows as states join their governing country: Anguilla, Montserrat and the Turks
    and Caicos Islands (United Kingdom), Puerto Rico and American Samoa (United States), Saint Barthelemy and Wallis
    and Futuna (France), Niue (New Zealand, in free association).
Borders, areas and labels are re-traced with era_tools.py. The faith, culture and development layers are painted
for 1989 afterwards by the overlay rules (../overlays). Run from data-source/scripts/derive-2026/."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import era_tools as T, cold_war as C

SITE = sys.argv[1]
D = T.Derive(SITE, '1994')
j60, i60 = C.era_ids(SITE, '1960')
j26, i26 = C.era_ids(SITE, '2026')
R = lambda name: D.realm(name)
n = {}

# the USSR, Yugoslavia, Czechoslovakia
r_su = D.realm('USSR', g=C.g_of(SITE, '1960', 'USSR'))
D.rename('Russia', 'USSR', realm=r_su)
n['USSR'] = C.merge(D, 'USSR', ['Ukraine', 'Belarus', 'Moldova', 'Estonia', 'Latvia', 'Lithuania', 'Georgia', 'Armenia', 'Azerbaijan',
                                'Kazakhstan', 'Kyrgyzstan', 'Tajikistan', 'Turkmenistan', 'Uzbekistan'])
r_yu = D.realm('Yugoslavia', g=C.g_of(SITE, '1960', 'Yugoslavia'))
D.rename('FR Yugoslavia', 'Yugoslavia', realm=r_yu)
n['Yugoslavia'] = C.merge(D, 'Yugoslavia', ['Slovenia', 'Croatia', 'Bosnia and Herzegovina', 'Macedonia'])
r_cs = D.realm('Czechoslovakia', g=C.g_of(SITE, '1960', 'Czechoslovakia'))
D.rename('Czech Republic', 'Czechoslovakia', realm=r_cs)
n['Czechoslovakia'] = C.merge(D, 'Czechoslovakia', ['Slovakia'])

# East and West Germany, North and South Yemen: the 1960 lines
gdr = C.nearest_split(C.ent_mask(j60, i60, 'East Germany'), C.ent_mask(j60, i60, 'West Germany'))
n['East Germany'] = D.take('East Germany', D.realm('East Germany', g=C.g_of(SITE, '1960', 'East Germany')), gdr, ['Germany'])
D.rename('Germany', 'West Germany'); D.rename_realm('Germany', 'West Germany')
south = C.nearest_split(C.ent_mask(j60, i60, 'Aden Protectorate'), C.ent_mask(j60, i60, 'Kingdom of Yemen'))
n['South Yemen'] = D.take('South Yemen', D.realm('South Yemen', colour='#b0583a'), south, ['Yemen'])
D.rename('Yemen', 'North Yemen'); D.rename_realm('Yemen', 'North Yemen')
n['Socotra'] = C.fill(D, C.ent_mask(j26, i26, 'Yemen') & D.lon_box(52.0, 11.9, 54.7, 12.9), 'South Yemen')   # unclaimed on the source map

# Eritrea in Ethiopia; South West Africa under South Africa
D.rename('Eritrea', 'Eritrea', realm=R('Ethiopia'))
D.rename('Namibia', 'South West Africa', realm=R('South Africa'))

# the occupied territories
pal = C.ent_mask(j26, i26, 'Palestine')
gaza = pal & D.lon_box(34.0, 31.0, 34.65, 31.7)
r_il = R('Israel')
n['Gaza Strip'] = D.take('Gaza Strip (Israeli-occupied)', r_il, gaza, ['Israel'])
n['West Bank'] = D.take('West Bank (Israeli-occupied)', r_il, pal & ~gaza, ['Israel'])

# small states missing from the source map
for name26, name, frm in [('Singapore', 'Singapore', ['Malaysia']), ('Bahrain', 'Bahrain', ['Saudi Arabia', 'Qatar']), ('Maldives', 'Maldives', []),
                          ('Mauritius', 'Mauritius', []), ('Seychelles', 'Seychelles', []), ('Comoros', 'Comoros', []),
                          ('Cabo Verde', 'Cape Verde', []), ('São Tomé and Principe', 'São Tomé and Príncipe', []),
                          ('Solomon Islands', 'Solomon Islands', []), ('Vanuatu', 'Vanuatu', []), ('Kiribati', 'Kiribati', [])]:
    n[name] = C.add_from(D, C.ent_mask(j26, i26, name26), name, D.realm(name, g=C.g_of(SITE, '2026', name26)), frm)

# dependencies
for name, gov in [('Anguilla', 'United Kingdom'), ('Montserrat', 'United Kingdom'), ('Turks and Caicos Islands', 'United Kingdom'),
                  ('Puerto Rico', 'United States'), ('American Samoa', 'United States'), ('Saint Barthelemy', 'France'),
                  ('Wallis and Futuna Islands', 'France'), ('Niue', 'New Zealand')]:
    D.rename(name, name, realm=R(gov))

notes = ['Built from the 1994 map, adjusted to the end of 1989.',
         'The Berlin Wall fell on 9 November 1989; Germany was reunified on 3 October 1990.',
         'The USSR is shown whole; its fifteen union republics became independent in 1991. Yugoslavia broke up in 1991–1992 and Czechoslovakia split on 1 January 1993.',
         'North Yemen and South Yemen united on 22 May 1990. Namibia (South West Africa) became independent of South Africa on 21 March 1990. Eritrea was part of Ethiopia until 1993.',
         'The West Bank, the Gaza Strip and the Golan Heights were under Israeli occupation from 1967.']
D.drop_notes = []
out, ix = D.save(1989, '1989', 'The fall of the Berlin Wall', notes, 1994)
print('1989 written:', ', '.join(f'{k} {v:,} px' for k, v in n.items()), f"| {ix['n']} states, {ix['m']} peoples, {len(out['borders'])} border lines")
