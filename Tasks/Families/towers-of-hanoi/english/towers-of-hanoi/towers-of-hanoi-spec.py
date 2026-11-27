# Tower of Hanoi: WorldSpec description (statement numbers as in english-input.txt).
# Written from the family's human-description.md; only the target peg was read from the original initialize rules.
from worldspec_py import *
TASK = task(
  name='towers-of-hanoi', title='Tower of Hanoi (families, from English)', folder='Families/towers-of-hanoi/english/towers-of-hanoi', lean_name='towersOfHanoiEnglish',
  statements=[
    (1, 'There are three pegs, A, B and C, and three disks of different sizes, all on peg A, largest at the bottom.'),
    (2, 'Move one disk at a time, taking only the top disk of a peg.'),
    (3, 'A disk is placed on an empty peg or on a larger disk; a disk may never rest on a smaller one.'),
    (4, 'The goal is to move the whole stack to another peg.')],
  world_rels=['on'],
  derived=[
    dict(name='top', vars=['d', 'p'], stmts=[2],
         defn=[obj('d', 'disk'), rel('on', V('d'), V('p')), none(obj('e', 'disk'), rel('on', V('e'), V('p')), has('e', 'size', 'lt', prop('d', 'size')))]),
    dict(name='can-take', vars=['q', 'd'], stmts=[3],
         defn=[obj('q', 'peg'), obj('d', 'disk'), none(obj('f', 'disk'), rel('on', V('f'), V('q')), has('f', 'size', 'lt', prop('d', 'size')))])],
  ops=[
    dict(name='move-disk', params=[('d', 'disk'), ('to', 'peg')], stmts=[2, 3],
         pre=[rel('top', V('d'), V('from')), rel('can-take', V('to'), V('d')), distinct('from', 'to')],
         bind=[rel('on', V('d'), V('old'))],
         effects=[e_change('on', [V('d'), V('old')], 2, V('to'))],
         report=[text('Move disk '), handle('d'), text(' to peg '), handle('to')])],
  goal=forall('x', 'disk', [rel('on', V('x'), H('c'))]), goalStmts=[4],
  repeatControl={'rel': 'on', 'types': ['disk']},
  assumptions=[
    dict(id='A-TH1', kind='intent', stmts=[1], text='Each disk (small, medium, large) has a size (1, 2, 3) and an on relation to the peg it is on; the order within a peg follows from the sizes, since a disk never rests on a smaller one.'),
    dict(id='A-TH2', kind='intent', stmts=[2], text='"the top disk of a peg": the smallest disk on its peg (no smaller disk on the same peg), a derived relation top(disk, peg).'),
    dict(id='A-TH3', kind='intent', stmts=[3], text='"an empty peg or a larger disk": the target peg has no disk smaller than the moved one (its top disk, if any, is larger), a derived relation can-take(peg, disk). Negations stay in derived relations, which the operators test positively (W-CHK-009).'),
    dict(id='A-TH4', kind='intent', stmts=[4], text='"another peg": peg C, read from the original agent\'s initialize rules (the English does not name it; JL allowed reading initial states there).'),
    dict(id='A-TH5', kind='intent', stmts=[], text='Search control, not from the English (as for the other WorldSpec search tasks): a look-ahead state that returns to a situation already on its path fails; a situation is where each disk is.')])
