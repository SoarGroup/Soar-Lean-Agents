"""Generates the Soar agent for this dialog from its instructor statements (english-input.txt); see tools/rosie_grid.py.
usage: python3 gen.py [WORLD]   (default init-tourrc.world; another example state writes rules for the state checks)"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'tools'))
import rosie_grid as G
os.chdir(HERE)
WORLD = sys.argv[1] if len(sys.argv) > 1 else 'init-tourrc.world'
G.tour('traveling-salesman', WORLD, 'init-tourrc.world', 'Traveling salesman', (5, 6, 7, 8, 11, 13), 'adjacent', True,
       'a 4 by 3 grid; the red block on one location, eleven blue blocks in a stack', '''
- Operator move-salesman ( argument1 = the red block, argument2 = the clear location),
  statement 5; adjacent (statement 8) is a static relation between locations (A-G1).
- "The solution has eleven steps" (statement 9) is checked against the plans, not used.''', op='move-salesman')
