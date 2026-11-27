# Missionaries and cannibals: WorldSpec description (statement numbers as in english-input.txt).
# Written from the family's human-description.md only; no Soar rules of the family were read.
from worldspec_py import *
BT = obj('bt', 'boat')
def at(x, y): return rel('at', V(x), V(y))
def group(g, role, bank): return [obj(g, 'group'), has(g, 'role', 'eq', val(sym(role))), rel('side', V(g), V(bank))]
# (operator name, missionaries, cannibals, report)
MIXES = [('cross-one-missionary', 1, 0, 'One missionary rows'), ('cross-two-missionaries', 2, 0, 'Two missionaries row'),
         ('cross-one-cannibal', 0, 1, 'One cannibal rows'), ('cross-two-cannibals', 0, 2, 'Two cannibals row'),
         ('cross-missionary-and-cannibal', 1, 1, 'A missionary and a cannibal row')]
LESS = {1: 'one-less', 2: 'two-less'}
def crossing(name, m, c, say):
    pre, bind, eff = [BT, at('bt', 'from'), rel('other', V('from'), V('to'))], [BT, at('bt', 'bold')], []
    for role, k, g in (('missionary', m, 'm'), ('cannibal', c, 'c')):
        if not k: continue
        # the group of this role on the starting bank loses k people, the one on the other bank gains k
        pre += group(g + 'f', role, 'from') + group(g + 't', role, 'to') + [
                at(g + 'f', g + 'n'), rel(LESS[k], V(g + 'n'), V(g + 'n1')), at(g + 't', g + 'k'), rel(LESS[k], V(g + 'k1'), V(g + 'k'))]
        # effects may use only parameters and bound variables, so the groups and numbers are bound again here
        bind += group(g + 'f', role, 'bold') + group(g + 't', role, 'to') + [
                 at(g + 'f', g + 'old'), rel(LESS[k], V(g + 'old'), V(g + 'new')), at(g + 't', g + 'told'), rel(LESS[k], V(g + 'tnew'), V(g + 'told'))]
        eff += [e_change('at', [V(g + 'f'), V(g + 'old')], 2, V(g + 'new')), e_change('at', [V(g + 't'), V(g + 'told')], 2, V(g + 'tnew'))]
    eff.append(e_change('at', [V('bt'), V('bold')], 2, V('to')))
    return dict(name=name, params=[('to', 'bank')], stmts=[2], pre=pre, bind=bind, effects=eff,
                report=[text(say + ' the boat to the '), handle('to'), text(' bank')])
TASK = task(
  name='missionaries-cannibals', title='Missionaries and cannibals (families, from English)', folder='Families/missionaries-cannibals/english/missionaries-cannibals', lean_name='missionariesCannibalsEnglish',
  statements=[
    (1, 'Three missionaries and three cannibals stand on the left bank of a river with a rowing boat.'),
    (2, 'The boat carries one or two people and never crosses empty.'),
    (3, 'If, on either bank, the cannibals ever outnumber the missionaries who are there, the missionaries are eaten.'),
    (4, 'A bank with no missionaries is safe.'),
    (5, 'The goal is to get all six people to the right bank.')],
  world_rels=['at', 'other', 'side', 'one-less', 'two-less'],
  ops=[crossing(*x) for x in MIXES],
  goal=ex(obj('g', 'group'), rel('side', V('g'), H('right')), has('g', 'role', 'eq', val(sym('missionary'))), at('g', 'n'), has('n', 'value', 'eq', val(num(3))),
          obj('h', 'group'), rel('side', V('h'), H('right')), has('h', 'role', 'eq', val(sym('cannibal'))), at('h', 'k'), has('k', 'value', 'eq', val(num(3)))), goalStmts=[5],
  failures=[dict(name='missionaries-eaten', stmts=[3, 4],
                 cond=ex(*group('g', 'missionary', 'k'), *group('h', 'cannibal', 'k'), at('g', 'n'), at('h', 'c'),
                         has('n', 'value', 'gt', val(num(0))), has('c', 'value', 'gt', prop('n', 'value'))))],
  repeatControl={'rel': 'at', 'types': ['group', 'boat']},
  assumptions=[
    dict(id='A-MC1', kind='intent', stmts=[1], text='The three missionaries are interchangeable, and so are the three cannibals, so the state is how many of each are on each bank. Four group objects (the missionaries and the cannibals on the left and on the right bank, side relation to their bank) are at a number object (zero to three, with a value). The boat is at a bank; the two banks have a static other relation both ways.'),
    dict(id='A-MC2', kind='intent', stmts=[2], text='"carries one or two people and never crosses empty": five crossing operators, one for each mix of one or two people (one or two missionaries, one or two cannibals, one of each). A crossing moves the boat to the other bank and moves the people from the group on the boat\'s bank to the group of the same role on the other bank.'),
    dict(id='A-MC3', kind='intent', stmts=[2], text='WorldSpec has no subtraction, so the counts are number objects linked by static one-less(n, n - 1) and two-less(n, n - 2) relations; a crossing is legal only when the starting group has enough people (the relation exists for its number).'),
    dict(id='A-MC4', kind='intent', stmts=[3, 4], text='"cannibals outnumber the missionaries", with no missionaries safe: a losing state is a bank whose missionaries number more than zero and fewer than its cannibals. "ever": wherever it arises, in the real world or in look-ahead.'),
    dict(id='A-MC5', kind='intent', stmts=[5], text='The goal is three missionaries and three cannibals on the right bank.'),
    dict(id='A-MC6', kind='intent', stmts=[], text='Search control, not from the English (as for the other WorldSpec river crossings): a look-ahead state that returns to a situation already on its path fails; a situation is the number in each group and where the boat is.'),
    dict(id='A-MC7', kind='intent', stmts=[3], text='Representation choice (25 Nov 2026): a first version with six person objects stated the losing states with negated conditions (exactly one or two missionaries on a bank); its learned rules dropped the negations and rejected every crossing at the start, and without learning its look-ahead did not finish in 100,000 decisions. Counting the groups needs no negation.')])
