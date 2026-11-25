"""Generates the Soar agent for this dialog from its instructor statements (english-input.txt); see tools/rosie_grid.py.
usage: python3 gen.py [WORLD] [--control none|all|SC-1]   (default init-8puzzlerc.world; another example state writes rules for the state checks)"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'tools'))
import rosie_grid as G
os.chdir(HERE)
CONTROL = sys.argv[sys.argv.index('--control') + 1] if '--control' in sys.argv else 'none'
ARGS = [a for i, a in enumerate(sys.argv[1:], 1) if a != '--control' and sys.argv[i - 1] != '--control']
WORLD = ARGS[0] if ARGS else 'init-8puzzlerc.world'
G.sliding('eight-puzzle', WORLD, 'init-8puzzlerc.world', 'Eight puzzle', 'color', 8, 'a 3 by 3 grid; eight coloured blocks',
          control=CONTROL)
