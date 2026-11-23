"""Generates the Soar agent for this dialog from its instructor statements (english-input.txt); see tools/rosie_chess.py.
usage: python3 gen.py [WORLD]   (default init-nknights2.world; another example state writes rules for the state checks)"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'tools'))
import rosie_chess as C
os.chdir(HERE)
WORLD = sys.argv[1] if len(sys.argv) > 1 else 'init-nknights2.world'
C.placement('n-knights', WORLD, 'init-nknights2.world', 'N knights', (5, 6, 7, 10, 12, 16, 17), ['jumpable'], 'a grid; eight blocks in a stack')
