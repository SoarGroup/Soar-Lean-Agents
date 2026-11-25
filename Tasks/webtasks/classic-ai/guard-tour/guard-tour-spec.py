# Guard tour (guard-tour): WorldSpec description (statement numbers as in english-input.txt).
from worldspec_py import *
G = obj('g', 'agent')
TASK = task(
  name='guard-tour', title='Guard tour (guard-tour)', folder='classic-ai/guard-tour', lean_name='guardTour',
  statements=[
    (1, 'The world has three squares, A, B and C, in a row.'),
    (2, 'A guard robot is in square A.'),
    (3, 'The robot can move to a neighbouring square.'),
    (4, 'First the robot goes to square C, then back to square A, and finally to square B.')],
  world_rels=['at', 'next'],
  ops=[
    dict(name='move', params=[('to', 'square')], stmts=[3],
         pre=[G, rel('at', V('g'), V('cur')), rel('next', V('cur'), V('to'))],
         bind=[G, rel('at', V('g'), V('old'))],
         effects=[e_change('at', [V('g'), V('old')], 2, V('to'))],
         report=[text('Move to '), handle('to')])],
  goal=ex(G, rel('at', V('g'), H('b'))), goalStmts=[4],
  phases=[dict(name='at-c', stmts=[4], cond=ex(G, rel('at', V('g'), H('c')))), dict(name='at-a', stmts=[4], cond=ex(G, rel('at', V('g'), H('a')))), dict(name='at-b', stmts=[4], cond=ex(G, rel('at', V('g'), H('b'))))],
  assumptions=[
    dict(id='A-G1', kind='intent', stmts=[1, 3], text='"neighbouring": a static next relation between A and B and between B and C, both ways.'),
    dict(id='A-G2', kind='intent', stmts=[4], text='The three stages are phases in order (L8-026); the goal field holds the last phase (used by the semantics checks).')])
