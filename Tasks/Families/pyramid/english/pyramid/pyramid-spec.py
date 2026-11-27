# Pyramid: WorldSpec description (statement numbers as in english-input.txt).
# Written from the family's human-description.md only; no Soar rules of the family were read.
from worldspec_py import *
P = obj('p', 'problem')
TASK = task(
  name='pyramid', title='Pyramid problem (families, from English)', folder='Families/pyramid/english/pyramid', lean_name='pyramidEnglish',
  statements=[
    (1, 'A pyramid problem adds a run of consecutive numbers counting down from a base.'),
    (2, 'The base is the first term, and each term is one less than the one before.'),
    (3, 'The height says how many terms follow the first, so height h gives h + 1 terms.'),
    (4, 'This problem has base 5 and height 10 (5 + 4 + ... + (-5)).'),
    (5, 'The goal is to compute the sum.')],
  world_rels=[],
  ops=[
    dict(name='add-term', params=[], stmts=[1, 2, 3],
         pre=[P, has('p', 'remaining', 'ge', val(num(0)))],
         bind=[P],
         effects=[e_update('p', 'sum', plus(prop('p', 'sum'), prop('p', 'term'))),
                  e_update('p', 'term', plus(prop('p', 'term'), val(num(-1)))),
                  e_update('p', 'remaining', plus(prop('p', 'remaining'), val(num(-1))))],
         report=[text('Add the next term')])],
  goal=ex(P, has('p', 'remaining', 'lt', val(num(0)))), goalStmts=[3, 5],
  assumptions=[
    dict(id='A-PY1', kind='intent', stmts=[2, 4], text='A problem object holds the next term (starting at the base, 5), the running sum (starting at 0) and the number of terms still to add after the next one (remaining, starting at the height, 10).'),
    dict(id='A-PY2', kind='intent', stmts=[1, 2, 3], text='add-term adds the next term to the sum, lowers the term by 1 and lowers remaining by 1 (adding -1; WorldSpec has no subtraction, so a negative constant is added). It is proposed while remaining is 0 or more, which gives h + 1 terms.'),
    dict(id='A-PY3', kind='intent', stmts=[5], text='"compute the sum": the goal is that every term has been added (remaining below 0); the sum is then on the problem object (0 for this instance).')])
