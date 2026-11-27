# Water jug: WorldSpec description (statement numbers as in english-input.txt).
# Written from the family's human-description.md only; no Soar rules of the family were read.
from worldspec_py import *
def p(x, q): return prop(x, q)
def add(x, q, rhs): return e_update(x, q, rhs)
TASK = task(
  name='water-jug', title='Water jug (families, from English)', folder='Families/water-jug/english/water-jug', lean_name='waterJugEnglish',
  statements=[
    (1, 'You have two unmarked jugs, one holding 3 gallons and one holding 5 gallons, both empty, and an unlimited supply of water.'),
    (2, 'In one step you may fill a jug completely or empty a jug completely.'),
    (3, 'In one step you may pour from one jug into the other until the receiving jug is full or the pouring jug is empty.'),
    (4, 'The goal is to end with exactly 1 gallon in the 3-gallon jug.')],
  world_rels=[],
  ops=[
    dict(name='fill', params=[('j', 'jug')], stmts=[1, 2],
         pre=[has('j', 'room', 'gt', val(num(0)))], bind=[],
         effects=[add('j', 'amount', p('j', 'capacity')), add('j', 'room', val(num(0)))],
         report=[text('Fill the '), handle('j'), text(' jug')]),
    dict(name='empty', params=[('j', 'jug')], stmts=[2],
         pre=[has('j', 'amount', 'gt', val(num(0)))], bind=[],
         effects=[add('j', 'amount', val(num(0))), add('j', 'room', p('j', 'capacity'))],
         report=[text('Empty the '), handle('j'), text(' jug')]),
    # the pouring jug empties: all of a fits into b
    dict(name='pour-all', params=[('a', 'jug'), ('b', 'jug')], stmts=[3],
         pre=[distinct('a', 'b'), has('a', 'amount', 'gt', val(num(0))), has('a', 'amount', 'le', p('b', 'room'))], bind=[],
         effects=[add('b', 'amount', plus(p('b', 'amount'), p('a', 'amount'))), add('b', 'room', minus(p('b', 'room'), p('a', 'amount'))),
                  add('a', 'amount', val(num(0))), add('a', 'room', p('a', 'capacity'))],
         report=[text('Pour the '), handle('a'), text(' jug into the '), handle('b'), text(' jug until it is empty')]),
    # the receiving jug fills: a has more than the room in b
    dict(name='pour-until-full', params=[('a', 'jug'), ('b', 'jug')], stmts=[3],
         pre=[distinct('a', 'b'), has('b', 'room', 'gt', val(num(0))), has('a', 'amount', 'gt', p('b', 'room'))], bind=[],
         effects=[add('a', 'amount', minus(p('a', 'amount'), p('b', 'room'))), add('a', 'room', plus(p('a', 'room'), p('b', 'room'))),
                  add('b', 'amount', p('b', 'capacity')), add('b', 'room', val(num(0)))],
         report=[text('Pour the '), handle('a'), text(' jug into the '), handle('b'), text(' jug until it is full')])],
  goal=ex(obj('j', 'jug'), has('j', 'capacity', 'eq', val(num(3))), has('j', 'amount', 'eq', val(num(1)))), goalStmts=[4],
  assumptions=[
    dict(id='A-WJ1', kind='intent', stmts=[1], text='Two jug objects, three-gallon and five-gallon, with a capacity and the amount of water in them (both 0 at the start). The supply of water is not an object: fill needs nothing.'),
    dict(id='A-WJ2', kind='intent', stmts=[2, 3], text='Pouring needs the amount that fits in the receiving jug, room = capacity - amount, in a condition, where arithmetic cannot be compiled; so each jug keeps room as a property beside its amount, and every operator updates both (with minus, added to WorldSpec 26 Nov 2026; the first version kept negated copies of the amounts, since WorldSpec then had only addition).'),
    dict(id='A-WJ3', kind='intent', stmts=[3], text='"until the receiving jug is full or the pouring jug is empty": two operators. pour-all when the pouring jug\'s amount fits in the room of the other (the pouring jug ends empty); pour-until-full when it is more than the room (the receiving jug ends full and the rest stays behind).'),
    dict(id='A-WJ4', kind='intent', stmts=[2], text='Filling a full jug or emptying an empty one changes nothing, so fill needs room in the jug and empty needs water in it.'),
    dict(id='A-WJ5', kind='intent', stmts=[], text='No repeated-situation control: it compares relations, and the amounts are numbers on the jugs. The look-ahead\'s depth limit bounds the search.')])
