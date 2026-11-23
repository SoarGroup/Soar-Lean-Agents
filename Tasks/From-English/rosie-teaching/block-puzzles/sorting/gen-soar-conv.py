"""Generates the standard-Soar agent (Soar-Conventions.xlsx, not the world conventions) for this dialog from its instructor
statements (english-input.txt); see tools/rosie_plain.py. Output: soar-conv/.
usage: python3 gen-soar-conv.py [WORLD]   (default 'init-sorting.world'; another example state writes rules for the state checks)"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'tools'))
import rosie_plain as P
os.chdir(HERE)
WORLD = sys.argv[1] if len(sys.argv) > 1 else 'init-sorting.world'
P.sorting('sorting-puzzle', WORLD, 'init-sorting.world', nums=(4, 6))
