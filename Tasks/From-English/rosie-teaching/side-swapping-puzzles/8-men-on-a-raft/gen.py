"""Generates the Soar agent for this dialog from its instructor statements (english-input.txt); see tools/rosie_swap.py.
usage: python3 gen.py [WORLD]   (default init-8men.world; another example state writes rules for the state checks)"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'tools'))
import rosie_swap as S
os.chdir(HERE)
WORLD = sys.argv[1] if len(sys.argv) > 1 else 'init-8men.world'
S.eight_men('eight-men-raft', WORLD, 'init-8men.world')
