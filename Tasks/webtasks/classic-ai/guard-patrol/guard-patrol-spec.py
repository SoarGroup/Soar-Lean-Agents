# Guard patrol (guard-patrol): WorldSpec description (statement numbers as in english-input.txt).
from worldspec_py import *
G = obj('g', 'agent')
TASK = task(
  name='guard-patrol', title='Guard patrol (guard-patrol)', folder='classic-ai/guard-patrol', lean_name='guardPatrol',
  statements=[
    (1, 'The world has three squares, A, B and C, in a row.'),
    (2, 'A guard robot is in square A.'),
    (3, 'The robot can move to a neighbouring square.'),
    (4, 'The robot goes to square C, then back to square A, and repeats this three times.')],
  world_rels=['at', 'next'],
  ops=[
    dict(name='move', params=[('to', 'square')], stmts=[3],
         pre=[G, rel('at', V('g'), V('cur')), rel('next', V('cur'), V('to'))],
         bind=[G, rel('at', V('g'), V('old'))],
         effects=[e_change('at', [V('g'), V('old')], 2, V('to'))],
         report=[text('Move to '), handle('to')])],
  goal=ex(G, rel('at', V('g'), H('a'))), goalStmts=[4],
  phases=[dict(name='at-c', stmts=[4], cond=ex(G, rel('at', V('g'), H('c')))), dict(name='at-a', stmts=[4], cond=ex(G, rel('at', V('g'), H('a'))))], loopStart=0, repeatCount=3,
  assumptions=[
    dict(id='A-G1', kind='intent', stmts=[1, 3], text='"neighbouring": a static next relation between A and B and between B and C, both ways.'),
    dict(id='A-G2', kind='intent', stmts=[4], text='Going to C and back to A are two phases; repeats closes the loop back to the first (L8-027); three times is ^repeat-count 3 (L8-029).')])
