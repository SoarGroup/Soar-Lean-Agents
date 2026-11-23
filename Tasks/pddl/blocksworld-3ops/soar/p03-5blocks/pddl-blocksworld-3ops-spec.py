# WorldSpec description generated from PDDL by Tasks/pddl/tools/pddl2ws.py (literal translation).
from worldspec_py import *
TASK = task(
  name='pddl-blocksworld-3ops',
  title='blocksworld-3ops / bw3-5blocks (PDDL)',
  folder='pddl/pddl-blocksworld-3ops',
  lean_name='pddlBlocksworld3ops',
  statements=[(1, 'PDDL action move-b-to-b'), (2, 'PDDL action move-b-to-t'), (3, 'PDDL action move-t-to-b'), (4, 'PDDL goal of problem bw3-5blocks')],
  world_rels=['clear', 'on', 'on-table'],
  ops=[{'name': 'move-b-to-b', 'params': [('bm', 'object'), ('bf', 'object'), ('bt', 'object')], 'stmts': [1], 'pre': [{'rel': 'clear', 'args': [{'var': 'bm'}]}, {'rel': 'clear', 'args': [{'var': 'bt'}]}, {'rel': 'on', 'args': [{'var': 'bm'}, {'var': 'bf'}]}, {'distinct': ['bm', 'bt']}], 'bind': [], 'effects': [{'del': 'clear', 'args': [{'var': 'bt'}]}, {'del': 'on', 'args': [{'var': 'bm'}, {'var': 'bf'}]}, {'add': 'on', 'args': [{'var': 'bm'}, {'var': 'bt'}]}, {'add': 'clear', 'args': [{'var': 'bf'}]}], 'report': [{'text': 'move-b-to-b '}, {'handle': 'bm'}, {'text': ' '}, {'handle': 'bf'}, {'text': ' '}, {'handle': 'bt'}]}, {'name': 'move-b-to-t', 'params': [('bm', 'object'), ('bf', 'object')], 'stmts': [2], 'pre': [{'rel': 'clear', 'args': [{'var': 'bm'}]}, {'rel': 'on', 'args': [{'var': 'bm'}, {'var': 'bf'}]}], 'bind': [], 'effects': [{'del': 'on', 'args': [{'var': 'bm'}, {'var': 'bf'}]}, {'add': 'on-table', 'args': [{'var': 'bm'}]}, {'add': 'clear', 'args': [{'var': 'bf'}]}], 'report': [{'text': 'move-b-to-t '}, {'handle': 'bm'}, {'text': ' '}, {'handle': 'bf'}]}, {'name': 'move-t-to-b', 'params': [('bm', 'object'), ('bt', 'object')], 'stmts': [3], 'pre': [{'rel': 'clear', 'args': [{'var': 'bm'}]}, {'rel': 'clear', 'args': [{'var': 'bt'}]}, {'rel': 'on-table', 'args': [{'var': 'bm'}]}], 'bind': [], 'effects': [{'del': 'clear', 'args': [{'var': 'bt'}]}, {'del': 'on-table', 'args': [{'var': 'bm'}]}, {'add': 'on', 'args': [{'var': 'bm'}, {'var': 'bt'}]}], 'report': [{'text': 'move-t-to-b '}, {'handle': 'bm'}, {'text': ' '}, {'handle': 'bt'}]}],
  goal={'ex': [{'rel': 'on', 'args': [{'h': 'e'}, {'h': 'a'}]}, {'rel': 'on', 'args': [{'h': 'a'}, {'h': 'c'}]}, {'rel': 'on', 'args': [{'h': 'c'}, {'h': 'b'}]}, {'rel': 'on', 'args': [{'h': 'b'}, {'h': 'd'}]}]},
  goalStmts=[4],
  assumptions=[],
)
