# Muddy children: WorldSpec description (statement numbers as in english-input.txt).
# Possible worlds are objects; what a child knows is explicit, as derived relations tested positively
# (JL, 16 Nov 2026). Each round of answers is an operator that records the answers given in the actual
# world and rules out every world where some child would have answered differently.
from worldspec_py import *
T = obj('t', 'stage')
NEXT = e_update('t', 'step', plus(prop('t', 'step'), val(num(1))))
TASK = task(
  name='muddy-children', title='Muddy children (muddy-children)', folder='classic-ai/muddy-children', lean_name='muddyChildren',
  statements=[
    (1, 'Three children are playing. Two of them, Amy and Ben, have mud on their foreheads; Cal does not.'),
    (2, "Each child can see the other children's foreheads but not his or her own."),
    (3, 'Their father says to all of them: "At least one of you has mud on your forehead."'),
    (4, 'Then he asks, again and again: "Do you know whether you have mud on your forehead?" All the children answer at the same time, truthfully, "yes" or "no".'),
    (5, 'Every child reasons perfectly and knows that the others do too, and every child hears every answer.'),
    (6, 'The goal is to find in which round each child first answers "yes", and why.')],
  world_rels=['muddy', 'clean', 'view-mate', 'actual', 'out-at', 'said-yes'],
  derived=[
    dict(name='all-clean', vars=['pw'], stmts=[3], defn=[obj('pw', 'world'), none(rel('muddy', V('c'), V('pw')))]),
    dict(name='live-at', vars=['pw', 'r'], stmts=[3, 4, 5],
         defn=[obj('pw', 'world'), obj('r', 'round'),
               none(rel('out-at', V('pw'), V('earlier')), has('earlier', 'n', 'lt', prop('r', 'n')))]),
    dict(name='knows-at', vars=['c', 'pw', 'r'], stmts=[2, 4, 5],
         defn=[obj('c', 'child'), rel('live-at', V('pw'), V('r')),
               none(rel('view-mate', V('c'), V('pw'), V('w2')), rel('live-at', V('w2'), V('r')))]),
    dict(name='answers-differ', vars=['pw', 'r'], stmts=[4, 5],
         defn=[rel('live-at', V('pw'), V('r')), rel('actual', V('wa')), obj('c', 'child'),
               rel('knows-at', V('c'), V('wa'), V('r')), none(rel('knows-at', V('c'), V('pw'), V('r')))]),
    dict(name='answers-differ-too', vars=['pw', 'r'], stmts=[4, 5],
         defn=[rel('live-at', V('pw'), V('r')), rel('actual', V('wa')), obj('c', 'child'),
               rel('knows-at', V('c'), V('pw'), V('r')), none(rel('knows-at', V('c'), V('wa'), V('r')))])],
  ops=[
    dict(name='father-speaks', params=[('t', 'stage')], stmts=[3], pre=[has('t', 'step', 'eq', val(num(0)))], bind=[],
         effects=[e_each([rel('all-clean', V('pw'))], e_add('out-at', V('pw'), H('father-round'))), NEXT],
         report=[text('Father: at least one of you has mud on your forehead')]),
    dict(name='ask', params=[('r', 'round')], stmts=[4, 5],
         pre=[T, has('t', 'step', 'eq', prop('r', 'n')), has('r', 'n', 'gt', val(num(0)))], bind=[T],
         effects=[e_each([rel('actual', V('wa')), rel('knows-at', V('c'), V('wa'), V('r'))], e_add('said-yes', V('c'), V('r'))),
                  e_each([rel('answers-differ', V('pw'), V('r'))], e_add('out-at', V('pw'), V('r'))),
                  e_each([rel('answers-differ-too', V('pw'), V('r'))], e_add('out-at', V('pw'), V('r'))), NEXT],
         report=[text('Father asks, round '), prop('r', 'n')])],
  goal=forall('x', 'child', [rel('said-yes', V('x'), V('y'))]), goalStmts=[6],
  assumptions=[
    dict(id='A-MC1', kind='intent', stmts=[1, 2], text='The eight possible patterns of mud are world objects; muddy and clean say each child\'s forehead in each world; view-mate(c, w, w2) holds when w2 differs from w only on c\'s own forehead (what c cannot see). The actual world is w-mmc.'),
    dict(id='A-MC2', kind='intent', stmts=[2, 4, 5], text='Knowledge is explicit (JL, 16 Nov 2026): knows-at(c, w, r) holds when, in world w at round r, no world c cannot tell from w is still possible. It and the other derived relations use negation only in their definitions; operators test them positively.'),
    dict(id='A-MC3', kind='intent', stmts=[3, 4, 5], text='The father\'s statement and each round are operators that rule out worlds (out-at(w, round)), on every world at once. A world is live at round r if it was not ruled out in an earlier round, so each round is judged on the worlds left before it. A stage number keeps the order; round objects carry their number.'),
    dict(id='A-MC4', kind='intent', stmts=[4], text='A round records which children answer yes in the actual world (said-yes(c, r)), and rules out every world where some child would answer differently than in the actual world (all answers are heard).'),
    dict(id='A-MC5', kind='intent', stmts=[6], text='The goal is that every child has answered yes in some round; the rounds of first yes are read from said-yes. Four rounds are provided.')])
