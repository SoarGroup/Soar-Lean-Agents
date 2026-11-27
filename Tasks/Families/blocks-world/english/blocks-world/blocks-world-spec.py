# Blocks world: WorldSpec description (statement numbers as in english-input.txt).
# Written from the family's human-description.md only; no Soar rules of the family were read.
from worldspec_py import *
TASK = task(
  name='blocks-world', title='Blocks world (families, from English)', folder='Families/blocks-world/english/blocks-world', lean_name='blocksWorldEnglish',
  statements=[
    (1, 'Lettered blocks sit on a table, some stacked on others.'),
    (2, 'You may move one block at a time, and only a block with nothing on top of it.'),
    (3, 'A block can go onto the table or onto another block that has nothing on top of it.'),
    (4, 'Blocks A and B start on the table and block C is on block A.'),
    (5, 'The goal is A on B, B on C and C on the table.')],
  world_rels=['on'],
  derived=[dict(name='clear', vars=['b'], stmts=[2, 3], defn=[obj('b', 'block'), none(rel('on', V('x'), V('b')))])],
  ops=[
    dict(name='move-to-table', params=[('b', 'block')], stmts=[2, 3],
         pre=[rel('clear', V('b')), rel('on', V('b'), V('from')), obj('from', 'block')],
         bind=[rel('on', V('b'), V('old'))],
         effects=[e_change('on', [V('b'), V('old')], 2, H('table'))],
         report=[text('Move block '), handle('b'), text(' to the table')]),
    dict(name='move-to-block', params=[('b', 'block'), ('to', 'block')], stmts=[2, 3],
         pre=[rel('clear', V('b')), rel('clear', V('to')), distinct('b', 'to'), rel('on', V('b'), V('from')), distinct('from', 'to')],
         bind=[rel('on', V('b'), V('old'))],
         effects=[e_change('on', [V('b'), V('old')], 2, V('to'))],
         report=[text('Move block '), handle('b'), text(' onto block '), handle('to')])],
  goal=ex(rel('on', H('a'), H('b')), rel('on', H('b'), H('c')), rel('on', H('c'), H('table'))), goalStmts=[5],
  repeatControl={'rel': 'on', 'types': ['block']},
  assumptions=[
    dict(id='A-BW1', kind='intent', stmts=[1, 4], text='One on relation from each block to what it sits on, a block or the table (a single table object).'),
    dict(id='A-BW2', kind='intent', stmts=[2, 3], text='"nothing on top of it": no block is on it, a derived relation clear(block) tested positively (W-CHK-009). Two operators: move-to-table for a block that is on a block, and move-to-block onto a different clear block.'),
    dict(id='A-BW3', kind='intent', stmts=[], text='Search control, not from the English (as for the other WorldSpec search tasks): a look-ahead state that returns to a situation already on its path fails; a situation is where each block is.')])
