"""Generates the Soar agent for this dialog from its instructor statements (english-input.txt); see tools/rosie_tasks.py.
usage: python3 gen.py [WORLD]   (default init-blocksworld2.world; another example state writes rules for the state checks)"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'tools'))
import rosie_tasks as T
os.chdir(HERE)
WORLD = sys.argv[1] if len(sys.argv) > 1 else 'init-blocksworld2.world'
T.blocks_world('world-blocks', WORLD, 'init-blocksworld2.world', bottom='purple', top_on='blue', top_below='yellow', nums=(4, 5, 7))
