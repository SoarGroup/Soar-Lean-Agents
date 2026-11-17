# Tower of London: WorldSpec description (statement numbers as in english-input.txt).
from worldspec_py import *
TASK = task(
  name='tower-of-london', title='Tower of London (tower-of-london)', folder='classic-ai/tower-of-london', lean_name='towerOfLondon',
  statements=[
    (1, 'There are three pegs. The first peg holds up to three balls, the second up to two, the third one.'),
    (2, 'There are three balls: red, green and blue.'),
    (3, 'At the start the first peg holds red at the bottom and green on top of it, the second peg holds blue, and the third peg is empty.'),
    (4, 'You can move the top ball of a peg onto another peg that is not full.'),
    (5, 'The goal is that the first peg holds blue at the bottom and red on top of it, and the second peg holds green.'),
    (6, 'Reach the goal in as few moves as possible.')],
  world_rels=['over', 'of', 'at'],
  maintained=[dict(name='empty', var='x', stmts=[1, 4],
                   defn=[obj('x'), has('x', 'kind', 'eq', val(sym('space'))), none(rel('at', V('b'), V('x')))])],
  ops=[
    dict(name='move', params=[('b', 'ball'), ('t', 'slot')], stmts=[4],
         pre=[rel('at', V('b'), V('src')), rel('over', V('c'), V('src')), rel('empty', V('c')),
              rel('empty', V('t')), rel('over', V('t'), V('u')), rel('at', V('o'), V('u')),
              rel('of', V('src'), V('p1')), rel('of', V('t'), V('p2')), distinct('p1', 'p2')],
         bind=[rel('at', V('b'), V('old'))],
         effects=[e_change('at', [V('b'), V('old')], 2, V('t')), e_del('empty', V('t')), e_add('empty', V('old'))],
         report=[text('Move '), handle('b'), text(' to '), handle('t')])],
  goal=ex(rel('at', H('blue-ball'), H('a-low')), rel('at', H('red-ball'), H('a-mid')), rel('at', H('green-ball'), H('b-low'))),
  goalStmts=[5],
  assumptions=[
    dict(id='A-TL1', kind='intent', stmts=[1], text='"holds up to n balls": a peg has n slots, stacked by an over relation from a floor; a ball is at a slot.'),
    dict(id='A-TL2', kind='intent', stmts=[4], text='"the top ball": a ball whose slot has an empty space over it. Each peg has a cap space over its top slot that is always empty and never a target, so the top slot needs no special case.'),
    dict(id='A-TL3', kind='intent', stmts=[4], text='"onto a peg that is not full": into the peg\'s lowest empty slot, i.e. an empty slot over a slot or floor that something is at. Each floor holds a fixed base object, which no action moves.'),
    dict(id='A-TL4', kind='intent', stmts=[4], text='"another peg": the target slot is of a different peg than the ball\'s slot.'),
    dict(id='A-TL5', kind='intent', stmts=[6], text='"as few moves as possible": unit cost per move, read through the library\'s search settings, not through the rules.')])
