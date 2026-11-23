"""Generates the Soar agent for this dialog from its instructor statements (english-input.txt); see tools/rosie_grid.py.
usage: python3 gen.py [WORLD]   (default init-atour2.world; another example state writes rules for the state checks)"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'tools'))
import rosie_grid as G
os.chdir(HERE)
WORLD = sys.argv[1] if len(sys.argv) > 1 else 'init-atour2.world'
G.tour('knights-tour', WORLD, 'init-atour2.world', "Knight's tour", (4, 5, 6, 7, 8, 11, 13), 'jumpable', False,
       'a 4 by 3 grid; the red block on one location, eleven blue blocks in a stack', '''
- Operator tour-move (argument1 = the red block, argument2 = the clear location), statement 4. captured (statement 7) is
  expanded in place (the location below the red block); movable-from (statement 8) is the knight's move, a static
  relation computed from alongside, diagonal-with and near as in knight swapping (A-S3).
- "The solution has eleven steps" (statement 9) is checked against the plans, not used.''')
