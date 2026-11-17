# Vacuum world: WorldSpec description (statement numbers as in english-input.txt).
from worldspec_py import *
VA = obj('v', 'agent')
TASK = task(
  name='vacuum-world', title='Vacuum world (vacuum-world)', folder='classic-ai/vacuum-world', lean_name='vacuumWorld',
  statements=[
    (1, 'The world has two squares, Left and Right, side by side.'),
    (2, 'A vacuum cleaner is in the Left square. Both squares are dirty.'),
    (3, 'The vacuum can move to the other square.'),
    (4, 'The vacuum can suck, which makes the square it is in clean.'),
    (5, 'Each action costs one step.'),
    (6, 'The goal is that both squares are clean, in as few steps as possible.')],
  world_rels=['at', 'dirty', 'next'],
  maintained=[dict(name='clean', var='x', stmts=[4, 6], defn=[obj('x', 'square'), none(rel('dirty', V('x')))])],
  ops=[
    dict(name='move', params=[('to', 'square')], stmts=[3],
         pre=[VA, rel('at', V('v'), V('cur')), rel('next', V('cur'), V('to'))],
         bind=[VA, rel('at', V('v'), V('old'))],
         effects=[e_change('at', [V('v'), V('old')], 2, V('to'))],
         report=[text('Move to '), handle('to')]),
    dict(name='suck', params=[('sq', 'square')], stmts=[4],
         pre=[VA, rel('at', V('v'), V('sq')), rel('dirty', V('sq'))],
         bind=[],
         effects=[e_del('dirty', V('sq')), e_add('clean', V('sq'))],
         report=[text('Suck in '), handle('sq')])],
  goal=forall('x', 'square', [rel('clean', V('x'))]), goalStmts=[6],
  assumptions=[
    dict(id='A-V1', kind='intent', stmts=[1, 3], text='"the other square": a static next relation holds between Left and Right in both directions.'),
    dict(id='A-V2', kind='intent', stmts=[4, 6], text='"clean" is "not dirty", kept as a maintained relation (it tests absence and decides the goal).'),
    dict(id='A-V3', kind='intent', stmts=[4], text='Suck is proposed only in a dirty square: sucking a clean square changes nothing, so it is never part of a shortest plan.'),
    dict(id='A-V4', kind='intent', stmts=[5, 6], text='"as few steps as possible": unit cost per action, read through the library\'s search settings, not through the rules.')])
