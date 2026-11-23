# WorldSpec description generated from PDDL by Tasks/pddl/tools/pddl2ws.py (literal translation).
from worldspec_py import *
TASK = task(
  name='pddl-ferry',
  title='ferry / p01-l2-c1 (PDDL)',
  folder='pddl/pddl-ferry',
  lean_name='pddlFerry',
  statements=[(1, 'PDDL action sail'), (2, 'PDDL action board'), (3, 'PDDL action debark'), (4, 'PDDL goal of problem p01-l2-c1')],
  world_rels=['at', 'at-ferry', 'car', 'empty-ferry', 'location', 'not-eq', 'on'],
  ops=[{'name': 'sail', 'params': [('from', 'object'), ('to', 'object')], 'stmts': [1], 'pre': [{'rel': 'not-eq', 'args': [{'var': 'from'}, {'var': 'to'}]}, {'rel': 'location', 'args': [{'var': 'from'}]}, {'rel': 'location', 'args': [{'var': 'to'}]}, {'rel': 'at-ferry', 'args': [{'var': 'from'}]}], 'bind': [], 'effects': [{'del': 'at-ferry', 'args': [{'var': 'from'}]}, {'add': 'at-ferry', 'args': [{'var': 'to'}]}], 'report': [{'text': 'sail '}, {'handle': 'from'}, {'text': ' '}, {'handle': 'to'}]}, {'name': 'board', 'params': [('car', 'object'), ('loc', 'object')], 'stmts': [2], 'pre': [{'rel': 'car', 'args': [{'var': 'car'}]}, {'rel': 'location', 'args': [{'var': 'loc'}]}, {'rel': 'at', 'args': [{'var': 'car'}, {'var': 'loc'}]}, {'rel': 'at-ferry', 'args': [{'var': 'loc'}]}, {'obj': 'nferry', 'type': 'ferry'}, {'has': 'nferry', 'prop': 'empty', 'cmp': 'eq', 'rhs': {'val': {'sym': 'true'}}}], 'bind': [{'obj': 'nferry', 'type': 'ferry'}], 'effects': [{'del': 'at', 'args': [{'var': 'car'}, {'var': 'loc'}]}, {'add': 'on', 'args': [{'var': 'car'}]}, {'update': 'nferry', 'prop': 'empty', 'rhs': {'val': {'sym': 'false'}}}], 'report': [{'text': 'board '}, {'handle': 'car'}, {'text': ' '}, {'handle': 'loc'}]}, {'name': 'debark', 'params': [('car', 'object'), ('loc', 'object')], 'stmts': [3], 'pre': [{'rel': 'car', 'args': [{'var': 'car'}]}, {'rel': 'location', 'args': [{'var': 'loc'}]}, {'rel': 'on', 'args': [{'var': 'car'}]}, {'rel': 'at-ferry', 'args': [{'var': 'loc'}]}], 'bind': [{'obj': 'nferry', 'type': 'ferry'}], 'effects': [{'del': 'on', 'args': [{'var': 'car'}]}, {'add': 'at', 'args': [{'var': 'car'}, {'var': 'loc'}]}, {'update': 'nferry', 'prop': 'empty', 'rhs': {'val': {'sym': 'true'}}}], 'report': [{'text': 'debark '}, {'handle': 'car'}, {'text': ' '}, {'handle': 'loc'}]}],
  goal={'ex': [{'rel': 'at', 'args': [{'h': 'c-0'}, {'h': 'l-1'}]}]},
  goalStmts=[4],
  assumptions=[],
)
