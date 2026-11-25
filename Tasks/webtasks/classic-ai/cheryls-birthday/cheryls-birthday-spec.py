# Cheryl's birthday: WorldSpec description (statement numbers as in english-input.txt).
# Knowledge is explicit: derived relations say which candidate dates a speaker would or would not know,
# and operators test them positively (JL, 16 Nov 2026). Each statement is an operator that rules out,
# on every date at once, the dates where the statement would be false.
from worldspec_py import *
D, D2 = obj('d', 'date'), obj('d2', 'date')
SAME_MONTH = has('d2', 'month', 'eq', prop('d', 'month'))
SAME_DAY = has('d2', 'day', 'eq', prop('d', 'day'))
T = obj('t', 'stage')
def stage(k): return has('t', 'step', 'eq', val(num(k)))
NEXT = e_update('t', 'step', plus(prop('t', 'step'), val(num(1))))
TASK = task(
  name='cheryls-birthday', title="Cheryl's birthday (cheryls-birthday)", folder='classic-ai/cheryls-birthday', lean_name='cherylsBirthday',
  statements=[
    (1, "Albert and Bernard want to know Cheryl's birthday. Cheryl gives them ten possible dates: May 15, May 16, May 19, June 17, June 18, July 14, July 16, August 14, August 15, August 17."),
    (2, 'Cheryl tells Albert only the month and tells Bernard only the day.'),
    (3, 'Albert says: "I don\'t know when Cheryl\'s birthday is, but I know that Bernard doesn\'t know either."'),
    (4, 'Bernard says: "At first I didn\'t know when Cheryl\'s birthday is, but I know now."'),
    (5, 'Albert says: "Then I also know when Cheryl\'s birthday is."'),
    (6, 'Each statement is true, and each speaker reasons perfectly.'),
    (7, "The goal is to find Cheryl's birthday.")],
  world_rels=['out3', 'out4', 'out5', 'answer'],
  derived=[
    # before statement 3: every date is a candidate
    dict(name='albert-would-know', vars=['d'], stmts=[2, 3],
         defn=[D, none(D2, distinct('d', 'd2'), SAME_MONTH)]),
    dict(name='bernard-would-know', vars=['d'], stmts=[2, 3, 4],
         defn=[D, none(D2, distinct('d', 'd2'), SAME_DAY)]),
    dict(name='bernard-might-know', vars=['d'], stmts=[3],
         defn=[D, D2, SAME_MONTH, rel('bernard-would-know', V('d2'))]),
    # after statement 3
    dict(name='left-after-3', vars=['d'], stmts=[3], defn=[D, none(rel('out3', V('d')))]),
    dict(name='bernard-unsure-after-3', vars=['d'], stmts=[4],
         defn=[rel('left-after-3', V('d')), rel('left-after-3', V('d2')), distinct('d', 'd2'), SAME_DAY]),
    # after statement 4
    dict(name='left-after-4', vars=['d'], stmts=[4], defn=[rel('left-after-3', V('d')), none(rel('out4', V('d')))]),
    dict(name='albert-unsure-after-4', vars=['d'], stmts=[5],
         defn=[rel('left-after-4', V('d')), rel('left-after-4', V('d2')), distinct('d', 'd2'), SAME_MONTH]),
    # after statement 5
    dict(name='left-after-5', vars=['d'], stmts=[5], defn=[rel('left-after-4', V('d')), none(rel('out5', V('d')))]),
    dict(name='only-date', vars=['d'], stmts=[7], defn=[rel('left-after-5', V('d')), none(rel('left-after-5', V('d2')), distinct('d', 'd2'))])],
  ops=[
    dict(name='statement-3', monotonic=True, params=[('t', 'stage')], stmts=[3, 6], pre=[stage(1)], bind=[],
         effects=[e_each([rel('albert-would-know', V('d'))], e_add('out3', V('d'))),
                  e_each([rel('bernard-might-know', V('d'))], e_add('out3', V('d'))), NEXT],
         report=[text('Statement 3 rules out the dates in months where Albert would know, or where Bernard might know')]),
    dict(name='statement-4', monotonic=True, params=[('t', 'stage')], stmts=[4, 6], pre=[stage(2)], bind=[],
         effects=[e_each([rel('left-after-3', V('d')), rel('bernard-would-know', V('d'))], e_add('out4', V('d'))),
                  e_each([rel('bernard-unsure-after-3', V('d'))], e_add('out4', V('d'))), NEXT],
         report=[text('Statement 4 rules out the dates where Bernard would have known at first, or would still not know')]),
    dict(name='statement-5', monotonic=True, params=[('t', 'stage')], stmts=[5, 6], pre=[stage(3)], bind=[],
         effects=[e_each([rel('albert-unsure-after-4', V('d'))], e_add('out5', V('d'))), NEXT],
         report=[text('Statement 5 rules out the dates where Albert would still not know')]),
    dict(name='answer', monotonic=True, params=[('d', 'date')], stmts=[7], pre=[T, stage(4), rel('only-date', V('d'))],
         bind=[T], effects=[e_add('answer', V('d')), NEXT],
         report=[text("Cheryl's birthday is "), prop('d', 'month'), text(' '), prop('d', 'day')])],
  goal=ex(rel('answer', V('x'))), goalStmts=[7],
  assumptions=[
    dict(id='A-CB1', kind='intent', stmts=[1, 2], text='The ten dates are date objects with a month and a day. Who was told what is not stored: "Albert would know" is read over every date, as if Albert had been told that date\'s month.'),
    dict(id='A-CB2', kind='intent', stmts=[3, 4, 5, 6], text='Knowledge is explicit (JL, 16 Nov 2026): derived relations, recomputed in every world, say for which dates a speaker would or would not know; operators test them positively. Their definitions use negation ("no other date has that day"), which is allowed only there.'),
    dict(id='A-CB3', kind='intent', stmts=[3, 4, 5], text='Each statement is an operator that marks, on every date at once (an each effect), the dates where the statement would be false (out3, out4, out5). Marks are added, never removed, so each statement is judged on the dates left before it. A stage number keeps the statements in order.'),
    dict(id='A-CB4', kind='intent', stmts=[3], text='"I know that Bernard doesn\'t know": rules out every date in a month that has a date whose day is unique among all ten (Bernard might know). "I don\'t know": rules out dates in a month with one date (none here).'),
    dict(id='A-CB5', kind='intent', stmts=[4], text='"At first I didn\'t know": rules out dates with a unique day among all ten (already gone after statement 3). "I know now": rules out dates whose day is shared by another date left after statement 3.'),
    dict(id='A-CB6', kind='intent', stmts=[5, 7], text='"Then I also know": rules out dates whose month is shared by another date left after statement 4. The answer is the one date left; with more than one left, no answer is proposed.')])
