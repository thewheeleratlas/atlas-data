"""Derive the 525 BCE map, the Persian Empire of Cyrus and Cambyses, from the 550 BCE map (make_bc550.py).
Usage: python3 make_bc525.py <site folder>     (writes <site>/eras/bc525.json and updates <site>/data/*.json)

Between 550 and 525 BCE Cyrus the Great took Media (550-549), Lydia (c. 547), Bactria, Sogdia and Arachosia
(c. 545-539) and Babylon with its empire (539); in 525 his son Cambyses conquered Egypt. Cilicia stayed a
self-governing vassal under its own kings. On this map they are all the Achaemenid Empire: Lydia, Babylonia, Egypt, Persis and
Cilicia as named territories, the Median and eastern lands as the empire's main territory. Not yet Persian: the Indus lands (Gandhara, taken under Darius I c. 518), Thrace (c. 513)
and Cyrene, which only sent tribute after 525. Rome is still a kingdom. Run from data-source/scripts/derive-2026/."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import era_tools as T

D = T.Derive(sys.argv[1], 'bc550')
D.drop_notes = [n for n in D.src['notes'] if n.startswith(('Before Cyrus the Great', 'Cyrus overthrew Media'))]   # 550-only notes
r_ach = D.realm('Achaemenid Empire', g=22)        # registry entry 'Persia', as on the 500 BCE map
D.rename('Median Empire', 'Achaemenid Empire', realm=r_ach)
D.rename('Persis (Anshan)', 'Persis', realm=r_ach)
D.rename('Lydia', 'Lydia', realm=r_ach)
D.rename('Neo-Babylonian Empire', 'Babylonia', realm=r_ach)
D.rename('Egypt (26th Dynasty)', 'Egypt', realm=r_ach)
D.rename('Cilicia (Hilakku)', 'Cilicia', realm=r_ach)
# the eastern conquests join the empire's main territory (one label, not two crowded ones)
import numpy as np
D.take('Achaemenid Empire', r_ach, np.ones_like(D.LAND), ['Bactrians, Sogdians and Arachosians'])

notes = ['Built from the 550 BCE map, adjusted to 525.',
         'Cyrus the Great took Media (550–549), Lydia (c. 547), Bactria, Sogdia and Arachosia (c. 545–539) and Babylon with its empire (539); in 525 Cambyses conquered Egypt at Pelusium.',
         'Not yet Persian: the Indus lands (Gandhara, under Darius I c. 518) and Thrace (c. 513); Cyrene sent tribute but kept its own king. Cilicia was a self-governing vassal.']
out, ix = D.save(-525, 'bc525', 'Cambyses conquers Egypt', notes, -550)
ach = next(e for e in out['ents'] if e['n'] == 'Achaemenid Empire')
print(f"525 BCE written | {ix['n']} states, {ix['m']} peoples, {len(out['borders'])} border lines")
