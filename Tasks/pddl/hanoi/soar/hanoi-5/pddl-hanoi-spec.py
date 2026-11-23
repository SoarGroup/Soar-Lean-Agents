# WorldSpec description generated from PDDL by Tasks/pddl/tools/pddl2ws.py (literal translation).
from worldspec_py import *
TASK = task(
  name='pddl-hanoi',
  title='hanoi / hanoi5 (PDDL)',
  folder='pddl/pddl-hanoi',
  lean_name='pddlHanoi',
  statements=[(1, 'PDDL action move'), (2, 'PDDL goal of problem hanoi5')],
  world_rels=['clear', 'on', 'smaller'],
  ops=[{'name': 'move', 'params': [('disc', 'object'), ('from', 'object'), ('to', 'object')], 'stmts': [1], 'pre': [{'rel': 'smaller', 'args': [{'var': 'to'}, {'var': 'disc'}]}, {'rel': 'on', 'args': [{'var': 'disc'}, {'var': 'from'}]}, {'rel': 'clear', 'args': [{'var': 'disc'}]}, {'rel': 'clear', 'args': [{'var': 'to'}]}], 'bind': [], 'effects': [{'del': 'on', 'args': [{'var': 'disc'}, {'var': 'from'}]}, {'del': 'clear', 'args': [{'var': 'to'}]}, {'add': 'clear', 'args': [{'var': 'from'}]}, {'add': 'on', 'args': [{'var': 'disc'}, {'var': 'to'}]}], 'report': [{'text': 'move '}, {'handle': 'disc'}, {'text': ' '}, {'handle': 'from'}, {'text': ' '}, {'handle': 'to'}]}],
  goal={'ex': [{'rel': 'on', 'args': [{'h': 'd-5'}, {'h': 'peg3'}]}, {'rel': 'on', 'args': [{'h': 'd-4'}, {'h': 'd-5'}]}, {'rel': 'on', 'args': [{'h': 'd-3'}, {'h': 'd-4'}]}, {'rel': 'on', 'args': [{'h': 'd-2'}, {'h': 'd-3'}]}, {'rel': 'on', 'args': [{'h': 'd-1'}, {'h': 'd-2'}]}]},
  goalStmts=[2],
  assumptions=[],
)
