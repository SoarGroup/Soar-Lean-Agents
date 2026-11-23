"""Generates the Soar agent for this dialog from its instructor statements (english-input.txt); see tools/rosie_chess.py.
usage: python3 gen.py [WORLD]   (default init-rooks.world; another example state writes rules for the state checks)"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'tools'))
import rosie_chess as C
os.chdir(HERE)
WORLD = sys.argv[1] if len(sys.argv) > 1 else 'init-rooks.world'
C.placement('n-rooks', WORLD, 'init-rooks.world', 'N rooks', (5, 6, 7, 12, 13, 16, 20), ['row', 'column'], 'a 4 by 4 grid; four blocks in a stack')
