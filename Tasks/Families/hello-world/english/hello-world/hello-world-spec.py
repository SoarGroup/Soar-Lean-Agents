# Hello World: WorldSpec description (statement numbers as in english-input.txt).
# Written from the family's human-description.md only; no Soar rules of the family were read.
from worldspec_py import *
P = obj('p', 'page')
TASK = task(
  name='hello-world', title='Hello World (families, from English)', folder='Families/hello-world/english/hello-world', lean_name='helloWorldEnglish',
  statements=[
    (1, 'Write the words "Hello World" once, then stop.')],
  world_rels=[],
  ops=[
    dict(name='write-hello-world', params=[], stmts=[1],
         pre=[P, has('p', 'written', 'eq', val(sym('nothing')))],
         bind=[P],
         effects=[e_update('p', 'written', val(sym('hello-world')))],
         report=[text('Hello World')])],
  goal=ex(P, has('p', 'written', 'eq', val(sym('hello-world')))), goalStmts=[1],
  assumptions=[
    dict(id='A-HW1', kind='intent', stmts=[1], text='Writing is an action of the agent (a perform-action command); its report prints "Hello World".'),
    dict(id='A-HW2', kind='intent', stmts=[1], text='"once, then stop": a page object records what is written on it (nothing at the start); the operator needs a page with nothing written, and the goal is a page with the words, so the agent writes once and the task ends. (A test that the page lacks the property is a negation, which the compiled conditions may not contain, W-CHK-009.)')])
