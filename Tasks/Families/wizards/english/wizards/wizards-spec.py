# Three wizards: WorldSpec description (statement numbers as in english-input.txt).
# Written from the family's human-description.md only; no Soar rules of the family were read.
# Possible worlds are objects and knowledge is explicit, as derived relations tested positively (the scheme of
# webtasks/classic-ai/muddy-children, JL 16 Nov 2026). Each turn is an operator that records the asked wizard's
# answer in the actual world and rules out every world where he would have answered differently.
from worldspec_py import *
T = obj('t', 'stage')
NEXT = e_update('t', 'step', plus(prop('t', 'step'), val(num(1))))
TASK = task(
  name='wizards', title='Three wizards (families, from English)', folder='Families/wizards/english/wizards', lean_name='wizardsEnglish',
  statements=[
    (1, 'Three wizards, A, B and C, sit where each can see the others but not himself.'),
    (2, 'Each has a spot on his forehead that is either white or black.'),
    (3, 'They are told that at least one spot is white.'),
    (4, 'They are asked in turn, A, then B, then C, whether they know the colour of their own spot.'),
    (5, 'Each can reason about what the others would have concluded from what they see and from the answers so far.'),
    (6, 'In this instance B and C have white spots and A has a black spot.'),
    (7, 'The goal is that a wizard correctly states the colour of his own spot.')],
  world_rels=['spot', 'view-mate', 'actual', 'asks', 'out-at', 'says'],
  derived=[
    dict(name='all-black', vars=['pw'], stmts=[3], defn=[obj('pw', 'world'), none(rel('spot', V('c'), V('pw'), H('white')))]),
    dict(name='live-at', vars=['pw', 'r'], stmts=[3, 4, 5],
         defn=[obj('pw', 'world'), obj('r', 'turn'),
               none(rel('out-at', V('pw'), V('earlier')), has('earlier', 'n', 'lt', prop('r', 'n')))]),
    dict(name='knows-at', vars=['c', 'pw', 'r'], stmts=[1, 4, 5],
         defn=[obj('c', 'wizard'), rel('live-at', V('pw'), V('r')),
               none(rel('view-mate', V('c'), V('pw'), V('w2')), rel('live-at', V('w2'), V('r')))]),
    dict(name='answer-differs', vars=['pw', 'r'], stmts=[4, 5],
         defn=[rel('live-at', V('pw'), V('r')), rel('asks', V('r'), V('c')), rel('actual', V('wa')),
               rel('knows-at', V('c'), V('wa'), V('r')), none(rel('knows-at', V('c'), V('pw'), V('r')))]),
    dict(name='answer-differs-too', vars=['pw', 'r'], stmts=[4, 5],
         defn=[rel('live-at', V('pw'), V('r')), rel('asks', V('r'), V('c')), rel('actual', V('wa')),
               rel('knows-at', V('c'), V('pw'), V('r')), none(rel('knows-at', V('c'), V('wa'), V('r')))])],
  ops=[
    dict(name='tell', monotonic=True, params=[('t', 'stage')], stmts=[3], pre=[has('t', 'step', 'eq', val(num(0)))], bind=[],
         effects=[e_each([rel('all-black', V('pw'))], e_add('out-at', V('pw'), H('told'))), NEXT],
         report=[text('Told: at least one spot is white')]),
    dict(name='ask', monotonic=True, params=[('r', 'turn')], stmts=[4, 5, 7],
         pre=[T, has('t', 'step', 'eq', prop('r', 'n')), has('r', 'n', 'gt', val(num(0)))], bind=[T],
         effects=[e_each([rel('actual', V('wa')), rel('asks', V('r'), V('c')), rel('knows-at', V('c'), V('wa'), V('r')),
                          rel('spot', V('c'), V('wa'), V('col'))], e_add('says', V('c'), V('col'))),
                  e_each([rel('answer-differs', V('pw'), V('r'))], e_add('out-at', V('pw'), V('r'))),
                  e_each([rel('answer-differs-too', V('pw'), V('r'))], e_add('out-at', V('pw'), V('r'))), NEXT],
         report=[text('Ask, turn '), prop('r', 'n')])],
  goal=ex(rel('says', V('c'), V('col'))), goalStmts=[7],
  assumptions=[
    dict(id='A-WZ1', kind='intent', stmts=[1, 2], text='The eight possible patterns of spots are world objects (w-bww: A black, B white, C white); spot(c, w, colour) gives each wizard\'s colour in each world; view-mate(c, w, w2) holds when w2 differs from w only in c\'s own spot (what c cannot see). The actual world is w-bww.'),
    dict(id='A-WZ2', kind='intent', stmts=[6], text='"B and C start marked, A unmarked" in the description is read as B and C white and A black (marked = the colour the announcement is about).'),
    dict(id='A-WZ3', kind='intent', stmts=[1, 4, 5], text='Knowledge is explicit: knows-at(c, w, r) holds when, in world w at turn r, no world c cannot tell from w is still possible. Derived relations use negation only in their definitions; operators test them positively.'),
    dict(id='A-WZ4', kind='intent', stmts=[3, 4, 5], text='The announcement and each turn are operators that rule out worlds (out-at(w, turn)). A world is live at turn r if it was not ruled out at an earlier turn. A stage number keeps the order; turn objects carry their number and asks(turn, wizard) says who is asked (A, B, C in that order).'),
    dict(id='A-WZ5', kind='intent', stmts=[4, 5, 7], text='A turn records the asked wizard\'s answer in the actual world: if he knows, he states his colour (says(c, colour), the colour of his spot in the actual world, so it is correct). Every world where he would have answered differently is ruled out, since all hear the answer.'),
    dict(id='A-WZ6', kind='intent', stmts=[7], text='The goal is that some wizard has stated his colour. With A black, B and C white, A and B do not know and C states white at the third turn.')])
