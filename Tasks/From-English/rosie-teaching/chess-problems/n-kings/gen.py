"""Generates the Soar agent for this dialog from its instructor statements (english-input.txt); see tools/rosie_chess.py.
usage: python3 gen.py [WORLD]   (default init-nkings.world; another example state writes rules for the state checks)"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'tools'))
import rosie_chess as C
os.chdir(HERE)
WORLD = sys.argv[1] if len(sys.argv) > 1 else 'init-nkings.world'
C.placement('n-kings', WORLD, 'init-nkings.world', 'N kings', (5, 6, 7, 10, 15, 16), ['next-to'], 'a grid; four blocks in a stack')
