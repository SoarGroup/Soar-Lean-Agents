# Instant Insanity: WorldSpec description (statement numbers as in english-input.txt).
from worldspec_py import *
def clash(side):
    return dict(name=f'same-colour-{side}', stmts=[5],
                cond=ex(obj('c1', 'cube'), obj('c2', 'cube'), distinct('c1', 'c2'),
                        rel('placed', V('c1'), V('o1')), rel('placed', V('c2'), V('o2')),
                        has('o1', side, 'eq', prop('o2', side))))
TASK = task(
  name='instant-insanity', title='Instant Insanity (instant-insanity)', folder='classic-ai/instant-insanity', lean_name='instantInsanity',
  statements=[
    (1, 'There are four cubes. Each face of a cube is red, green, blue, white or yellow.'),
    (2, 'Each cube is given by its three pairs of opposite faces: cube 1: red and green, blue and white, red and yellow; cube 2: green and blue, yellow and red, white and white; cube 3: yellow and white, green and red, blue and blue; cube 4: blue and red, white and yellow, green and green.'),
    (3, 'You stack the four cubes in a column, each turned any way you like.'),
    (4, 'The column has four sides: front, back, left and right.'),
    (5, 'The goal is that each of the four sides of the column shows four different colours.')],
  world_rels=['orient', 'prev', 'placed'],
  maintained=[dict(name='unplaced', var='x', stmts=[3], defn=[obj('x', 'cube'), none(rel('placed', V('x'), V('y')))])],
  ops=[
    dict(name='place', params=[('c', 'cube'), ('o', 'orientation')], stmts=[3, 4],
         pre=[rel('unplaced', V('c')), rel('orient', V('o'), V('c')), rel('prev', V('c'), V('q')), rel('placed', V('q'), V('r'))],
         bind=[],
         effects=[e_add('placed', V('c'), V('o')), e_del('unplaced', V('c'))],
         report=[text('Place '), handle('c'), text(' turned as '), handle('o')])],
  goal=forall('x', 'cube', [rel('placed', V('x'), V('o'))]), goalStmts=[3, 5],
  failures=[clash(s) for s in ('front', 'back', 'left', 'right')],
  assumptions=[
    dict(id='A-II1', kind='intent', stmts=[2, 3, 4], text='"turned any way you like": each cube has one orientation object per distinct assignment of colours to the four sides (front, back, left, right); the top and bottom faces do not matter. Cube 1 has 24, cubes 2 to 4 have 16 (each has a pair of equal colours).'),
    dict(id='A-II2', kind='intent', stmts=[3], text='"stack in a column": cubes are placed one at a time in the order 1, 2, 3, 4, each on the one before; cube 1 goes on the ground, which counts as placed from the start.'),
    dict(id='A-II3', kind='intent', stmts=[5], text='"four different colours" on a side: two placed cubes showing the same colour on the same side is a losing state, so a partial column that cannot be completed is cut off at once.')])
