# WorldSpec description generated from PDDL by Tasks/pddl/tools/pddl2ws.py (literal translation).
from worldspec_py import *
TASK = task(
  name='pddl-gripper-strips',
  title='gripper-strips / strips-gripper-x-1 (PDDL)',
  folder='pddl/pddl-gripper-strips',
  lean_name='pddlGripperStrips',
  statements=[(1, 'PDDL action move'), (2, 'PDDL action pick'), (3, 'PDDL action drop'), (4, 'PDDL goal of problem strips-gripper-x-1')],
  world_rels=['at', 'at-robby', 'ball', 'carry', 'free', 'gripper', 'room'],
  ops=[{'name': 'move', 'params': [('from', 'object'), ('to', 'object')], 'stmts': [1], 'pre': [{'rel': 'room', 'args': [{'var': 'from'}]}, {'rel': 'room', 'args': [{'var': 'to'}]}, {'rel': 'at-robby', 'args': [{'var': 'from'}]}], 'bind': [], 'effects': [{'del': 'at-robby', 'args': [{'var': 'from'}]}, {'add': 'at-robby', 'args': [{'var': 'to'}]}], 'report': [{'text': 'move '}, {'handle': 'from'}, {'text': ' '}, {'handle': 'to'}]}, {'name': 'pick', 'params': [('obj', 'object'), ('room', 'object'), ('gripper', 'object')], 'stmts': [2], 'pre': [{'rel': 'ball', 'args': [{'var': 'obj'}]}, {'rel': 'room', 'args': [{'var': 'room'}]}, {'rel': 'gripper', 'args': [{'var': 'gripper'}]}, {'rel': 'at', 'args': [{'var': 'obj'}, {'var': 'room'}]}, {'rel': 'at-robby', 'args': [{'var': 'room'}]}, {'rel': 'free', 'args': [{'var': 'gripper'}]}], 'bind': [], 'effects': [{'del': 'at', 'args': [{'var': 'obj'}, {'var': 'room'}]}, {'del': 'free', 'args': [{'var': 'gripper'}]}, {'add': 'carry', 'args': [{'var': 'obj'}, {'var': 'gripper'}]}], 'report': [{'text': 'pick '}, {'handle': 'obj'}, {'text': ' '}, {'handle': 'room'}, {'text': ' '}, {'handle': 'gripper'}]}, {'name': 'drop', 'params': [('obj', 'object'), ('room', 'object'), ('gripper', 'object')], 'stmts': [3], 'pre': [{'rel': 'ball', 'args': [{'var': 'obj'}]}, {'rel': 'room', 'args': [{'var': 'room'}]}, {'rel': 'gripper', 'args': [{'var': 'gripper'}]}, {'rel': 'carry', 'args': [{'var': 'obj'}, {'var': 'gripper'}]}, {'rel': 'at-robby', 'args': [{'var': 'room'}]}], 'bind': [], 'effects': [{'del': 'carry', 'args': [{'var': 'obj'}, {'var': 'gripper'}]}, {'add': 'at', 'args': [{'var': 'obj'}, {'var': 'room'}]}, {'add': 'free', 'args': [{'var': 'gripper'}]}], 'report': [{'text': 'drop '}, {'handle': 'obj'}, {'text': ' '}, {'handle': 'room'}, {'text': ' '}, {'handle': 'gripper'}]}],
  goal={'ex': [{'rel': 'at', 'args': [{'h': 'ball4'}, {'h': 'roomb'}]}, {'rel': 'at', 'args': [{'h': 'ball3'}, {'h': 'roomb'}]}, {'rel': 'at', 'args': [{'h': 'ball2'}, {'h': 'roomb'}]}, {'rel': 'at', 'args': [{'h': 'ball1'}, {'h': 'roomb'}]}]},
  goalStmts=[4],
  assumptions=[],
)
