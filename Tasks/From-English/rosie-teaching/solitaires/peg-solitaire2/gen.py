"""Generates the Soar agent for this dialog from its instructor statements (english-input.txt); see tools/rosie_solitaire.py.
usage: python3 gen.py [WORLD]   (default init-peg.world; another example state writes rules for the state checks)"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'tools'))
import rosie_solitaire as P
os.chdir(HERE)
WORLD = sys.argv[1] if len(sys.argv) > 1 else 'init-peg.world'
P.peg_solitaire('peg-solitaire', WORLD, 'init-peg.world', (4, 5, 6, 11, 12), garbage=True)
