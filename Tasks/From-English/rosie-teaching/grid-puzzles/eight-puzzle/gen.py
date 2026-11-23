"""Generates the Soar agent for this dialog from its instructor statements (english-input.txt); see tools/rosie_grid.py.
usage: python3 gen.py [WORLD]   (default init-8puzzlerc.world; another example state writes rules for the state checks)"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'tools'))
import rosie_grid as G
os.chdir(HERE)
WORLD = sys.argv[1] if len(sys.argv) > 1 else 'init-8puzzlerc.world'
G.sliding('eight-puzzle', WORLD, 'init-8puzzlerc.world', 'Eight puzzle', 'color', 8, 'a 3 by 3 grid; eight coloured blocks')
