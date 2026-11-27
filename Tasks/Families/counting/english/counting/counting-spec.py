# Counting: WorldSpec description (statement numbers as in english-input.txt).
# Written from the family's human-description.md only; no Soar rules of the family were read.
from worldspec_py import *
C = obj('c', 'counter')
TASK = task(
  name='counting', title='Counting (families, from English)', folder='Families/counting/english/counting', lean_name='countingEnglish',
  statements=[
    (1, 'Count upwards from a starting number to a target number, one at a time.'),
    (2, 'This instance counts from 0 to 100.')],
  world_rels=[],
  ops=[
    dict(name='count-up', params=[], stmts=[1],
         pre=[C, has('c', 'count', 'lt', prop('c', 'target'))],
         bind=[C],
         effects=[e_update('c', 'count', plus(prop('c', 'count'), val(num(1))))],
         report=[text('Count one more')])],
  goal=ex(C, has('c', 'count', 'eq', prop('c', 'target'))), goalStmts=[1],
  assumptions=[
    dict(id='A-CT1', kind='intent', stmts=[1, 2], text='A counter object holds the current number (count, starting at 0) and the target (100).'),
    dict(id='A-CT2', kind='intent', stmts=[1], text='"one at a time": each count-up action adds 1 to the count; it is proposed only while the count is below the target, and the goal is a count equal to the target.')])
