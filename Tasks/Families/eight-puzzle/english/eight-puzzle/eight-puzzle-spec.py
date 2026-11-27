# Eight puzzle: WorldSpec description (statement numbers as in english-input.txt).
# Written from the family's human-description.md; the start and target arrangements were read from the original initialize rules.
from worldspec_py import *
BL = obj('bl', 'blank')
TILES = ['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight']
# target arrangement (rows top to bottom), from the original initialize rules
TARGET = {'top-left': 'one', 'top-middle': 'eight', 'top-right': 'seven',
          'middle-left': 'two', 'center': 'blank', 'middle-right': 'six',
          'bottom-left': 'three', 'bottom-middle': 'four', 'bottom-right': 'five'}
TASK = task(
  name='eight-puzzle', title='Eight puzzle (families, from English)', folder='Families/eight-puzzle/english/eight-puzzle', lean_name='eightPuzzleEnglish',
  statements=[
    (1, 'A 3 x 3 tray holds eight numbered tiles and one empty square.'),
    (2, 'A tile next to the empty square (left, right, above or below, not diagonally) may slide into it, leaving its own square empty.'),
    (3, 'Tiles may not be lifted out.'),
    (4, 'The goal is to slide tiles until they match the target arrangement.')],
  world_rels=['at', 'next-to'],
  ops=[
    dict(name='slide', params=[('t', 'tile'), ('to', 'square')], stmts=[2, 3],
         pre=[BL, rel('at', V('bl'), V('to')), rel('at', V('t'), V('from')), rel('next-to', V('from'), V('to'))],
         bind=[BL, rel('at', V('t'), V('old')), rel('at', V('bl'), V('bold'))],
         effects=[e_change('at', [V('t'), V('old')], 2, V('to')), e_change('at', [V('bl'), V('bold')], 2, V('old'))],
         report=[text('Slide tile '), handle('t'), text(' into '), handle('to')])],
  goal=ex(*[rel('at', H(x), H(sq)) for sq, x in TARGET.items()]), goalStmts=[4],
  repeatControl={'rel': 'at', 'types': ['tile', 'blank']},
  assumptions=[
    dict(id='A-EP1', kind='intent', stmts=[1], text='Nine square objects with names by position (top-left ... bottom-right) and a static next-to relation between squares that share a side, both ways ("not diagonally").'),
    dict(id='A-EP2', kind='intent', stmts=[1, 2], text='The empty square is marked by a blank object that is at a square like a tile, so a slide swaps the squares of a tile and the blank. Tiles are named one ... eight.'),
    dict(id='A-EP3', kind='intent', stmts=[3], text='"may not be lifted out": slide is the only operator.'),
    dict(id='A-EP4', kind='intent', stmts=[4], text='The start and target arrangements are not in the English; they were read from the original agent\'s initialize rules (JL allowed this). The goal names the square of every tile and of the blank.'),
    dict(id='A-EP5', kind='intent', stmts=[], text='Search control, not from the English (as for the other WorldSpec search tasks): a look-ahead state that returns to a situation already on its path fails; a situation is where each tile and the blank are.')])
