"""River-crossing dialogs (Rosie teaching data), world conventions: family-crossing, jealous-husbands, jealous-wives,
missionaries-and-cannibals. (fox-goose-bean, the pilot, has its own gen.py with the same readings.)

Shared readings (tools/rosie-language.md):
  - "the boat and a block on the current bank onto the opposite bank" (ferry-one): argument1 = the block (not the boat),
    argument2 = the opposite bank; the boat and the block move.
  - "a block that is on the current bank and another block that is on the current bank and the boat onto the opposite
    bank" (ferry-two): argument1, argument2 = the two blocks (an unordered pair: the block with the lower ^index is
    argument1); the destination is the opposite bank.
  - current (below a boat) is expanded in place; opposite (not below a boat) is a maintained one-argument relation.
  - "all the blocks are on a destination bank": expanded over the blocks of the world file.
Counted shapes (missionaries and cannibals): ^<shape>-count on each bank, kept by the moves."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import re
import rosie_gen as R, control as C, aggregate as A
from rosie_tasks import _desc, _finish

def handle(i, a):
    if a['category'] == 'location': return f'bank-{i}'
    return '-'.join(x for x in (a.get('shape'), a.get('last-name')) if x) + f'-{i}'

def opposite(name, objs, rels):
    boats = {i for i, a in objs.items() if a.get('shape') == 'boat'}
    under_boat = {a for a, b in rels.get('below', []) if b in boats}
    return {i for i, a in objs.items() if a['category'] == 'location' and i not in under_boat}

def river(name, world, default_world, nums, title, translation, actions, failures=(), counted=(), extra_note='',
          control='none', control_table=()):
    """actions: list of (opname, kind, filter): kind 'one' (boat + one block) or 'two' (boat + two blocks);
    filter: a shape the block(s) must have, or None. failures: list of rule texts (format with {n} = task name).
    counted: shapes counted on each bank (^<shape>-count)."""
    objs, rels, _ = R.read_world(world)
    if counted: assert all(a.get('shape') in counted or a.get('shape') == 'boat' for a in objs.values() if a['category'] == 'block')
    # Interchangeable blocks (World-Conventions L7-027): when every block but the boat belongs to a kind of identical
    # blocks, the world keeps counts per bank and kind and the operators move kinds (tools/aggregate.py).
    groups = A.interchangeable(objs, rels)
    riders = [i for i, a in objs.items() if a['category'] == 'block' and a.get('shape') != 'boat']
    if groups and all(any(i in g['members'] for g in groups.values()) for i in riders):
        return _river_counts(name, world, default_world, nums, title, translation, actions, failures, groups,
                             extra_note, control, control_table, objs, rels)
    def extra(i, a, rels):
        p = {}
        if a['category'] == 'block' and a.get('shape') != 'boat': p['index'] = i
        if a['category'] == 'block': p['label-key'] = f'pos-{i}'
        if a['category'] == 'location':
            for sh in counted:
                p[f'{sh}-count'] = sum(1 for b, l in rels.get('on', []) if l == i and objs[b].get('shape') == sh)
        return p
    translation += '''
- Search control added at JL's direction (16 Nov 2026), not from the English: in look-ahead, a move whose result is a
  situation already on the current look-ahead path is rejected. A situation is the bank of every block; each operator
  carries the label of the situation it produces (^result), the task object the label of the current one (^situation),
  and the look-ahead application records both on the history object (^visited). Real moves (JL, 16 Nov 2026, as in
  mc-world): a real move back to a situation already visited is worst (the top state records ^real-visited).'''
    if counted:
        translation += '''
- Search control added (24 Nov 2026, To-do row 48), not from the English: blocks of a counted shape differ only in
  their shape (the losing condition counts them), so they are interchangeable. Of the blocks of one shape on the bank
  the boat leaves, a crossing moves those with the lowest ^index; any other choice is rejected. This keeps one crossing
  per combination of shapes (5 instead of 21 here) and drops the permutations of the same situation.'''
    t = R.RosieTask(name, _desc(title, nums, default_world + extra_note, translation), world, handle,
                    maintained=['opposite'], concept=opposite, extra_props=extra, derived=('goal-met', 'situation'))
    t.t.objects.append(('history', {'type': 'history'}, []))
    for opname, kind, flt in actions:
        f1 = f' ^shape {flt}' if flt else ''
        if kind == 'one':
            t.add(t.t.propose(opname, f'''   (<objs> ^object <boat> <x> <cur> <opp>)
   (<boat> ^type block ^shape boat ^object-handle <bh>)
   (<x> ^type block{f1} ^object-handle {{ <> <bh> <xh> }})
   (<cur> ^type location)
   (<opp> ^type location ^object-handle <oh>)
   (<w> ^below <bb> ^on <xo> ^opposite <op-r>)
   (<bb> ^argument1 <cur> ^argument2 <boat>)
   (<xo> ^argument1 <x> ^argument2 <cur>)
   (<op-r> ^argument1 <opp>)''', ['<x>', '<opp>'], attrs='^from <cur> ^to <opp>'))
        else:
            t.add(t.t.propose(opname, f'''   (<objs> ^object <boat> <x> <y> <cur>)
   (<boat> ^type block ^shape boat)
   (<x> ^type block{f1} ^index <xi> ^object-handle <xh>)
   (<y> ^type block{f1} ^index > <xi> ^object-handle <yh>)
   (<cur> ^type location)
   (<objs> ^object <opp>)
   (<w> ^below <bb> ^on <xo> <yo> ^opposite <op-r>)
   (<op-r> ^argument1 <opp>)
   (<bb> ^argument1 <cur> ^argument2 <boat>)
   (<xo> ^argument1 <x> ^argument2 <cur>)
   (<yo> ^argument1 <y> ^argument2 <cur>)''', ['<x>', '<y>'], attrs='^from <cur> ^to <opp>'))
        _effects(t, opname, kind, counted)
    for f in failures:
        t.add(f.format(n=name))
    _repeat_control(t, [i for i, a in sorted(objs.items()) if a['category'] == 'block'])
    if counted: _symmetry_control(t)
    blocks = [t.h[i] for i, a in sorted(objs.items()) if a['category'] == 'block']
    conds = '\n'.join(f'''   (<b-{h}> ^object-handle {h})
   (<w> ^on <on-{h}>)
   (<on-{h}> ^argument1 <b-{h}> ^argument2 <dest>)''' for h in blocks)
    t.add(f'''
## Goal: all the blocks are on a destination bank (expanded over the blocks of the world file).
sp {{{name}*elaborate*goal*all-crossed
   (state <s> ^world <w>)
   (<w> ^anchored-world true ^objects <objs>)
   (<objs> ^object <t> <dest> {' '.join(f'<b-{h}>' for h in blocks)})
   (<t> ^type task)
   (<dest> ^type location ^name destination)
{conds}
-->
   (<t> ^goal-met true)
}}
''')
    tag = C.translate(t, name, control, control_table)
    _finish(t, name, world, default_world, tag)

_REPEAT_TAIL = '''
## In look-ahead, reject an operator whose result is a situation already on the path.
sp {{{n}*reject*operator*repeated-situation
   (state <s> ^internal-actions true ^operator <op> + ^world <w>)
   (<w> ^objects.object <hist>)
   (<hist> ^type history ^visited <l>)
   (<op> ^task-operator true ^result <l>)
-->
   (<s> ^operator <op> -)
}}

## ---- Search control on real moves (added, not taught; JL 16 Nov 2026, as in Tasks/From-English/mc-world): ----
## a real move back to a situation already visited is worst. It is chosen only when nothing else is left, so the agent
## prefers progress but is never trapped by its own history. The record is on the top state, not in the world, so it is
## not copied into look-ahead worlds.
## The real application records the situation it leaves (not the one it produces: recording that would make the selected
## operator itself worst, and Soar would replace it before its command completes).
sp {{{n}*apply*operator*record-real-move
   (state <s> ^superstate nil ^operator <op> ^world <w>)
   (<op> ^task-operator true)
   (<w> ^objects.object <t>)
   (<t> ^type task ^situation <sit>)
-->
   (<s> ^real-visited <sit>)
}}

sp {{{n}*compare*operator*real-repeated-situation
   (state <s> ^superstate nil ^operator <op> + ^real-visited <l>)
   (<op> ^task-operator true ^result <l>)
-->
   (<s> ^operator <op> <)
}}

## The look-ahead application records the situation it leaves and the one it produces.
sp {{{n}*apply*operator*record-path
   (state <s> ^operator <op> ^internal-actions true ^world <w>)
   (<op> ^task-operator true ^result <r>)
   (<w> ^objects <objs>)
   (<objs> ^object <hist> <t>)
   (<hist> ^type history)
   (<t> ^type task ^situation <sit>)
-->
   (<hist> ^visited <r> <sit>)
}}
'''

def _river_counts(name, world, default_world, nums, title, translation, actions, failures, groups, extra_note,
                  control, control_table, objs, rels):
    """River crossing over counts (World-Conventions L7-027): each bank has ^<kind>-count for every kind of
    interchangeable block; the boat stays an individual block (on/below its bank). ferry-one moves the boat and one
    block of a kind (argument1 = the kind object, argument2 = the opposite bank); a two-block action moves two blocks of
    kinds k1 <= k2 (argument1, argument2 = the kind objects; the same kind twice needs two on the bank). Each operator
    carries ^move-<kind> for every kind."""
    kinds = sorted(groups)
    translation += f'''
- Interchangeable blocks (World-Conventions L7-027; tools/aggregate.py): the {', '.join(kinds)} blocks are identical
  within each kind and the statements never single one out, so only how many are on each bank matters. Each bank has
  {', '.join('^' + k + '-count' for k in kinds)}; each kind is an object (^type kind, ^total). The operators move kinds:
  ferry-one argument1 = a kind, argument2 = the opposite bank; a two-block crossing has argument1 and argument2 = two
  kinds (in name order; the same kind twice when two of it are on the bank). The boat stays an individual block. An
  environment that moves individual blocks binds a kind to any block of that kind on the bank (the output names the
  kind).'''
    t = R.RosieTask(name, _desc(title, nums, default_world + extra_note, translation), world, handle,
                    maintained=['opposite'], concept=opposite, derived=('goal-met', 'situation'), aggregate=groups)
    t.t.objects.append(('history', {'type': 'history'}, []))
    places = sorted(i for i, a in objs.items() if a['category'] == 'location')
    banks = [t.h[i] for i in places]
    for opname, kind, flt in actions:
        ks = [k for k in kinds if not flt or groups[k]['attrs'].get('shape') == flt]
        combos = [(k,) for k in ks] if kind == 'one' else [(a, b) for x, a in enumerate(ks) for b in ks[x:]]
        for combo in combos:
            need = {k: combo.count(k) for k in combo}
            moves = ' '.join(f'^move-{k} {need.get(k, 0)}' for k in kinds)
            kv = {k: f'<k-{k}>' for k in need}
            lines = [f"   (<objs> ^object <boat> <cur> <opp> {' '.join(kv.values())})",
                     '   (<boat> ^type block ^shape boat)',
                     f"   (<cur> ^type location {' '.join(f'^{k}-count >= {m}' for k, m in need.items())})",
                     '   (<opp> ^type location)']
            lines += [f'   ({v} ^type kind ^object-handle {k})' for k, v in kv.items()]
            lines += ['   (<w> ^below <bb> ^opposite <op-r>)',
                      '   (<bb> ^argument1 <cur> ^argument2 <boat>)',
                      '   (<op-r> ^argument1 <opp>)']
            args = [kv[combo[0]], '<opp>'] if kind == 'one' else [kv[combo[0]], kv[combo[1]]]
            t.add(t.t.propose(f'{opname}*{"-".join(combo)}', '\n'.join(lines), args,
                              attrs=f'^from <cur> ^to <opp> {moves}'))
            _count_env_effect(t, opname, kind, combo)
        _count_internal_effects(t, opname, kinds)
    for f in failures:
        t.add(f.format(n=name))
    _count_repeat_control(t, kinds, banks)
    totals = ' '.join(f'^{k}-count {len(groups[k]["members"])}' for k in kinds)
    t.add(f'''
## Goal: all the blocks are on a destination bank: every block of each kind ({totals}) and the boat.
sp {{{name}*elaborate*goal*all-crossed
   (state <s> ^world <w>)
   (<w> ^anchored-world true ^objects <objs> ^on <rb>)
   (<objs> ^object <t> <dest> <boat>)
   (<t> ^type task)
   (<boat> ^type block ^shape boat)
   (<dest> ^type location ^name destination {totals})
   (<rb> ^argument1 <boat> ^argument2 <dest>)
-->
   (<t> ^goal-met true)
}}
''')
    tag = C.translate(t, name, control, control_table)
    _finish(t, name, world, default_world, tag)

_BOAT_COND = '''   (<w> ^anchored-world true ^objects <objs>)
   (<objs> ^object <boat> <d>)
   (<boat> ^type block ^shape boat)
   (<w> ^on <rb> ^below <bb> ^opposite <od>)
   (<rb> ^argument1 <boat> ^argument2 <old>)
   (<bb> ^argument1 <old> ^argument2 <boat>)
   (<od> ^argument1 <d>)'''
_BOAT_RHS = '''(<rb> ^argument2 <old> - <d>)
   (<bb> ^argument1 <old> - <d>)
   (<w> ^opposite <od> - <no>)
   (<no> ^argument1 <old>)'''

def _count_internal_effects(t, opname, kinds):
    """Look-ahead effects: the boat crosses; each kind's counts change by the operator's ^move-<kind>."""
    n = t.name
    t.add(f'''
## Effect of {opname} (look-ahead): the boat crosses to the opposite bank.
sp {{{n}*apply*{opname}*internal*boat
   (state <s> ^operator <op> ^internal-actions true ^world <w>)
   (<op> ^task-operator true ^name {opname} ^pre-conditions-satisfied true ^from.object-handle <oldh>)
{_BOAT_COND}
   (<old> ^object-handle <oldh>)
-->
   {_BOAT_RHS}
}}
''')
    for k in kinds:
        t.add(f'''
## Effect of {opname} (look-ahead): the {k} count of each bank changes by the number of {k} blocks moved.
sp {{{n}*apply*{opname}*internal*count*{k}
   (state <s> ^operator <op> ^internal-actions true ^world <w>)
   (<op> ^task-operator true ^name {opname} ^pre-conditions-satisfied true ^from.object-handle <oldh>
         ^to.object-handle <dh> ^move-{k} {{ > 0 <m> }})
   (<w> ^anchored-world true ^objects <objs>)
   (<objs> ^object <old> <d>)
   (<old> ^object-handle <oldh> ^{k}-count <o>)
   (<d> ^object-handle <dh> ^{k}-count <c>)
-->
   (<old> ^{k}-count <o> - (- <o> <m>))
   (<d> ^{k}-count <c> - (+ <c> <m>))
}}
''')

def _count_env_effect(t, opname, kind, combo):
    """Effect of a completed command on the real world (once per command), for one combination of kinds."""
    n = t.name
    need = {k: combo.count(k) for k in combo}
    trig = f'^argument1 {combo[0]} ^argument2 <dh>' if kind == 'one' else f'^argument1 {combo[0]} ^argument2 {combo[1]}'
    cond = _BOAT_COND + ('\n   (<d> ^object-handle <dh>)' if kind == 'one' else '')
    c, r = '', ''
    for k, m in need.items():
        c += f'\n   (<old> ^{k}-count <o-{k}>)\n   (<d> ^{k}-count <n-{k}>)'
        r += f'\n   (<old> ^{k}-count <o-{k}> - (- <o-{k}> {m}))\n   (<d> ^{k}-count <n-{k}> - (+ <n-{k}> {m}))'
    t.add(f'''
sp {{{n}*apply*{opname}*environment-effect*{"-".join(combo)}
   :o-support
   (state <s> ^superstate nil ^world <w> ^io.output-link.perform-action <pa>)
   (<pa> ^name {opname} ^status complete {trig} -^effect-applied true)
{cond}{c}
-->
   {_BOAT_RHS}{r}
   (<pa> ^effect-applied true)
   (write |{opname}: {" and ".join(combo)} with the boat from | <old> | to | <d> (crlf))
}}
''')

def _count_repeat_control(t, kinds, banks):
    """Repeated-situation search control over counts: a situation is the count of every kind on every bank and the
    bank of the boat (as _repeat_control, which labels a situation by the bank of every block)."""
    n = t.name
    cells = [(b, k) for b in banks for k in kinds]
    rules = '''
## ---- Search control (added, not taught): avoid returning to a situation on the current look-ahead path. ----
## A situation is the count of every kind on every bank and the bank of the boat.
'''
    for b, k in cells:
        rules += f'''
## The {k} count of {b} after a proposed operator.
sp {{{n}*elaborate*operator*after*{b}*{k}*from
   (state <s> ^operator <op> + ^world <w>)
   (<op> ^task-operator true ^from <bank> ^move-{k} <m>)
   (<bank> ^object-handle {b} ^{k}-count <c>)
-->
   (<op> ^after-{b}-{k} (- <c> <m>))
}}

sp {{{n}*elaborate*operator*after*{b}*{k}*to
   (state <s> ^operator <op> + ^world <w>)
   (<op> ^task-operator true ^to <bank> ^move-{k} <m>)
   (<bank> ^object-handle {b} ^{k}-count <c>)
-->
   (<op> ^after-{b}-{k} (+ <c> <m>))
}}
'''
    labs = ' |,| '.join([f'<{b}-{k}>' for b, k in cells] + ['<boat-bank>'])
    afters = ' '.join(f'^after-{b}-{k} <{b}-{k}>' for b, k in cells)
    bank_lines = '\n'.join(f'   (<bank-{b}> ^object-handle {b} ' + ' '.join(f'^{k}-count <{b}-{k}>' for k in kinds) + ')'
                           for b in banks)
    rules += f'''
## The label of the situation the operator produces.
sp {{{n}*elaborate*operator*result
   (state <s> ^operator <op> + ^world <w>)
   (<op> ^task-operator true ^to.object-handle <boat-bank> {afters})
-->
   (<op> ^result (concat {labs}))
}}

## The label of the current situation (derived; not copied into look-ahead worlds).
sp {{{n}*elaborate*situation
   (state <s> ^world <w>)
   (<w> ^anchored-world true ^objects <objs> ^on <rb>)
   (<objs> ^object <t> <boat> {' '.join(f'<bank-{b}>' for b in banks)})
   (<t> ^type task)
   (<boat> ^type block ^shape boat)
   (<rb> ^argument1 <boat> ^argument2 <bb>)
   (<bb> ^object-handle <boat-bank>)
{bank_lines}
-->
   (<t> ^situation (concat {labs}))
}}
'''
    t.add(rules + _REPEAT_TAIL.format(n=n))

def _effects(t, opname, kind, counted):
    """The boat moves from its bank <old> to the opposite bank <d>; each moved block moves too; opposite moves from <d> to
    <old>; counted shapes change by the moved blocks."""
    n = t.name
    # destination: argument2 for 'one'; for 'two' it is the opposite bank (bound through the opposite relation)
    if kind == 'one':
        trig_i = '^argument1.object-handle <xh> ^argument2.object-handle <dh> ^from.object-handle <oldh>'
        trig_e = '^argument1 <xh> ^argument2 <dh>'
        moved = ['x']
    else:
        trig_i = '^argument1.object-handle <xh> ^argument2.object-handle <yh> ^from.object-handle <oldh>'
        trig_e = '^argument1 <xh> ^argument2 <yh>'
        moved = ['x', 'y']
    cond = '''   (<w> ^anchored-world true ^objects <objs>)
   (<objs> ^object <boat> <d>)
   (<boat> ^type block ^shape boat)
   (<w> ^on <rb> ^below <bb> ^opposite <od>)
   (<rb> ^argument1 <boat> ^argument2 <old>)
   (<bb> ^argument1 <old> ^argument2 <boat>)
   (<old> ^object-handle <oldh>)
   (<od> ^argument1 <d>)''' + ('\n   (<d> ^object-handle <dh>)' if kind == 'one' else '')
    rhs = '''(<rb> ^argument2 <old> - <d>)
   (<bb> ^argument1 <old> - <d>)
   (<w> ^opposite <od> - <no>)
   (<no> ^argument1 <old>)'''
    for m in moved:
        cond += f'''
   (<objs> ^object <{m}>)
   (<{m}> ^object-handle <{m}h>)
   (<w> ^on <r{m}> ^below <b{m}>)
   (<r{m}> ^argument1 <{m}> ^argument2 <old>)
   (<b{m}> ^argument1 <old> ^argument2 <{m}>)'''
        rhs += f'''
   (<r{m}> ^argument2 <old> - <d>)
   (<b{m}> ^argument1 <old> - <d>)'''
    variants = [('', '', '')]
    if counted:
        # one variant per combination of the moved blocks' counted shapes (a block of another shape changes no count)
        import itertools
        variants = []
        for combo in itertools.product(list(counted), repeat=len(moved)):   # every moved block has a counted shape (asserted)
            c, r = '', ''
            delta = {}
            for m, sh in zip(moved, combo):
                if sh: c += f'\n   (<{m}> ^shape {sh})'; delta[sh] = delta.get(sh, 0) + 1
            for sh, k in delta.items():
                c += f'\n   (<old> ^{sh}-count <o-{sh}>)\n   (<d> ^{sh}-count <n-{sh}>)'
                r += f'\n   (<old> ^{sh}-count <o-{sh}> - (- <o-{sh}> {k}))\n   (<d> ^{sh}-count <n-{sh}> - (+ <n-{sh}> {k}))'
            variants.append(('*' + '-'.join(s or 'other' for s in combo), c, r))
    for tag, c, r in variants:
        t.add(f'''
## Effect of {opname} (look-ahead){tag and ': moved shapes ' + tag[1:]}.
sp {{{n}*apply*{opname}*internal{tag}
   (state <s> ^operator <op> ^internal-actions true ^world <w>)
   (<op> ^task-operator true ^name {opname} ^pre-conditions-satisfied true {trig_i})
{cond}{c}
-->
   {rhs}{r}
}}

sp {{{n}*apply*{opname}*environment-effect{tag}
   :o-support
   (state <s> ^superstate nil ^world <w> ^io.output-link.perform-action <pa>)
   (<pa> ^name {opname} ^status complete {trig_e} -^effect-applied true)
{cond}{c}
-->
   {rhs}{r}
   (<pa> ^effect-applied true)
   (write |{opname}: | <xh> {'| and | <yh> ' if kind == 'two' else ''}| with the boat from | <old> | to | <d> (crlf))
}}
''')

TRANS_COMMON = '''
- Operators: ferry-one ("the boat and a block on the current bank onto the opposite bank"; argument1 = the block,
  argument2 = the opposite bank) and ferry-two ("a block ... and another block ... and the boat"; argument1 and
  argument2 = the two blocks, the lower ^index first; the destination is the opposite bank). Each operator records the
  bank it leaves (^from), so its look-ahead application fires once.
- current is expanded in place (a bank below the boat); opposite is a maintained one-argument relation.
- The goal ("all the blocks are on a destination bank") is expanded over the blocks of the world file (the boat is a
  block).'''

def family(world, default_world='init-familycross.world'):
    river('family-cross', world, default_world, (4, 5, 6, 7, 8, 9, 13), 'Family crossing',
          TRANS_COMMON.replace('ferry-two ("a block ... and another block ... and the boat"',
                               'ferry-two-children (statement 4, not named in the dialog: "a child ... and another child ... and the boat"') +
          '\n- No losing condition is taught. "The solution has nine steps." is checked against the plans, not used.',
          actions=[('ferry-two-children', 'two', 'child'), ('ferry-one', 'one', None)],
          extra_note=' (two banks; two adults, two children and the boat on the first bank)')

JEALOUS = {
 'husband': '''
## Failure: a woman is on a bank, her husband (the man with her last-name) is not on the bank, and a man is on the bank.
## "not on the bank" is read as "on the other bank" (A-R3), so the test is positive.
sp {{{n}*elaborate*failure*woman-without-husband
   (state <s> ^desireds <ds> ^world <w>)
   (<w> ^anchored-world true ^objects <objs> ^on <rw> <rh> <rm>)
   (<objs> ^object <wo> <hu> <ma> <bank>)
   (<bank> ^type location)
   (<wo> ^type block ^shape woman ^last-name <ln>)
   (<hu> ^type block ^shape man ^last-name <ln>)
   (<ma> ^type block ^shape man)
   (<rw> ^argument1 <wo> ^argument2 <bank>)
   (<rh> ^argument1 <hu> ^argument2 {{ <> <bank> }})
   (<rm> ^argument1 <ma> ^argument2 <bank>)
-->
   (<s> ^failure <ds>)
}}
''',
 'wife': '''
## Failure: a man is on a bank, his wife (the woman with his last-name) is not on the bank, and another woman is on the bank.
## "not on the bank" is read as "on the other bank" (A-R3), so the test is positive.
sp {{{n}*elaborate*failure*man-without-wife
   (state <s> ^desireds <ds> ^world <w>)
   (<w> ^anchored-world true ^objects <objs> ^on <rm> <rw> <ro>)
   (<objs> ^object <ma> <wi> <wo> <bank>)
   (<bank> ^type location)
   (<ma> ^type block ^shape man ^last-name <ln>)
   (<wi> ^type block ^shape woman ^last-name <ln>)
   (<wo> ^type block ^shape woman)
   (<rm> ^argument1 <ma> ^argument2 <bank>)
   (<rw> ^argument1 <wi> ^argument2 {{ <> <bank> }})
   (<ro> ^argument1 <wo> ^argument2 <bank>)
-->
   (<s> ^failure <ds>)
}}
'''}

def jealous(kind, world, default_world='init-husbands.world'):
    name = 'jealous-husbands' if kind == 'husband' else 'jealous-wives'
    river(name, world, default_world, (4, 5, 6, 7, 8, 9, 10, 12, 14, 18), name.replace('-', ' ').capitalize(),
          TRANS_COMMON + f'''
- The losing condition marks the state with ^failure; {kind} (same last-name) is expanded in place.
- "The solution has five steps." does not match this world (three couples need 11 crossings; five fits the two-couple
  world init-husbands2): reported, not used.''',
          actions=[('ferry-one', 'one', None), ('ferry-two', 'two', None)], failures=[JEALOUS[kind]],
          extra_note=' (two banks; three couples (woman and man with the same last-name) and the boat on the first bank)')

MAC_FAIL = '''
## Failure: the number of cannibals on a bank is more than the number of missionaries on the bank, read with the usual
## exception that a bank with no missionaries is safe (A-M1; the literal reading makes the puzzle unsolvable).
sp {{{n}*elaborate*failure*cannibals-outnumber-missionaries
   (state <s> ^desireds <ds> ^world <w>)
   (<w> ^anchored-world true ^objects.object <bank>)
   (<bank> ^type location ^cannibal-count <c> ^missionary-count {{ > 0 < <c> }})
-->
   (<s> ^failure <ds>)
}}
'''

def sc_two_to_destination_first(t, name, sc_id):
    """Evaluation item: 'During look-ahead, first try crossings that carry two blocks to the destination bank, and try
    last crossings that carry two blocks back from it.' A one-step measure of progress toward the goal (all blocks on the
    destination bank, statement 17), used only to order the evaluations (World-Conventions L15-026)."""
    t.add(f'''
## ---- Search control {sc_id} [evaluation] (added, not taught; World-Conventions L15-026): evaluate first a crossing that
## carries two blocks to the destination bank, and last one that carries two back. Only the order of evaluation changes.
sp {{{name}*elaborate*operator*evaluate-first*two-to-destination
   (state <s> ^operator <op> +)
   (<op> ^task-operator true ^name ferry-two ^to <d>)
   (<d> ^name destination)
-->
   (<op> ^evaluate-first true)
}}

sp {{{name}*elaborate*operator*evaluate-last*two-from-destination
   (state <s> ^operator <op> +)
   (<op> ^task-operator true ^name ferry-two ^from <d>)
   (<d> ^name destination)
-->
   (<op> ^evaluate-last true)
}}
''')


# Search-control items (tools/control.py) missionaries-and-cannibals can translate: statement pattern -> rule writer.
CONTROL_MAC = [
    (re.compile(r'^during look-ahead, first try crossings that carry two blocks to the destination bank, and try last '
                r'crossings that carry two blocks back from it\.?$', re.I), sc_two_to_destination_first),
]


def mac(world, default_world='init-mac.world', control='none'):
    river('missionaries-and-cannibals', world, default_world, (4, 5, 6, 7, 8, 9, 10, 12, 17), 'Missionaries and cannibals',
          TRANS_COMMON + '''
- "the number of cannibals (missionaries) on a bank" is a maintained attribute ^cannibal-count (^missionary-count) of
  each bank, changed by every crossing.
- The losing condition is read with the usual exception (A-M1): a bank with cannibals and no missionaries is safe.
- "The solution has five steps." does not match this world (11 crossings): reported, not used.''',
          actions=[('ferry-one', 'one', None), ('ferry-two', 'two', None)], failures=[MAC_FAIL],
          counted=('missionary', 'cannibal'),
          extra_note=' (two banks; three missionaries, three cannibals and the boat on the first bank)',
          control=control, control_table=CONTROL_MAC)


def _symmetry_control(t):
    """Interchangeable blocks (counted shapes): only the lowest-indexed blocks of a shape on the bank left may move
    (search control, not from the English; To-do row 48)."""
    n = t.name
    t.add(f'''
## ---- Search control (added, not taught): blocks of a counted shape are interchangeable. ----
## A crossing that moves a block while a block of the same shape with a lower ^index stays on the bank it leaves is
## rejected, so one crossing remains for each combination of shapes.
sp {{{n}*reject*operator*interchangeable-block
   (state <s> ^operator <op> + ^world <w>)
   (<op> ^task-operator true ^<< argument1 argument2 >> <b> ^from <cur>)
   (<b> ^type block ^shape {{ <> boat <sh> }} ^index <bi>)
   (<w> ^objects.object <c> ^on <r>)
   (<c> ^type block ^shape <sh> ^index < <bi>)
   (<r> ^argument1 <c> ^argument2 <cur>)
  -(<op> ^argument1 <c>)
  -(<op> ^argument2 <c>)
-->
   (<s> ^operator <op> -)
}}
''')


def _repeat_control(t, blocks):
    """Look-ahead path repeated-state avoidance (search control, not from the English; decided by JL 16 Nov 2026)."""
    n = t.name
    keys = [f'pos-{i}' for i in blocks]
    t.add(f'''
## ---- Search control (added, not taught): avoid returning to a situation on the current look-ahead path. ----
## Where each block would be after a proposed operator: a moved block (an argument, or the boat) on the destination bank.
sp {{{n}*elaborate*operator*after*moved-block
   (state <s> ^operator <op> + ^world <w>)
   (<op> ^task-operator true ^<< argument1 argument2 >> <b> ^to <dest>)
   (<b> ^type block ^label-key <k>)
   (<dest> ^object-handle <dh>)
-->
   (<op> ^<k> <dh>)
}}

sp {{{n}*elaborate*operator*after*boat
   (state <s> ^operator <op> + ^world <w>)
   (<w> ^objects.object <b>)
   (<op> ^task-operator true ^to <dest>)
   (<b> ^type block ^shape boat ^label-key <k>)
   (<dest> ^object-handle <dh>)
-->
   (<op> ^<k> <dh>)
}}

## A block that does not move stays on its bank.
sp {{{n}*elaborate*operator*after*unmoved-block
   (state <s> ^operator <op> + ^world <w>)
   (<op> ^task-operator true ^argument1 <a1> ^argument2 <a2> ^to <dest>)
   (<w> ^objects <objs> ^on <r>)
   (<objs> ^object {{ <> <a1> <> <a2> <b> }})
   (<b> ^type block ^shape {{ <> boat }} ^label-key <k>)
   (<r> ^argument1 <b> ^argument2 <bank>)
   (<bank> ^object-handle <bh>)
-->
   (<op> ^<k> <bh>)
}}

## The label of the situation the operator produces.
sp {{{n}*elaborate*operator*result
   (state <s> ^operator <op> + ^world <w>)
   (<op> ^task-operator true {' '.join(f'^{k} <{k}>' for k in keys)})
-->
   (<op> ^result (concat {' |,| '.join(f'<{k}>' for k in keys)}))
}}

## The label of the current situation (derived; not copied into look-ahead worlds).
sp {{{n}*elaborate*situation
   (state <s> ^world <w>)
   (<w> ^anchored-world true ^objects <objs> ^on {' '.join(f'<r{i}>' for i in blocks)})
   (<objs> ^object <t> {' '.join(f'<b{i}>' for i in blocks)})
   (<t> ^type task)
''' + '\n'.join(f'''   (<b{i}> ^label-key {k})
   (<r{i}> ^argument1 <b{i}> ^argument2 <bank{i}>)
   (<bank{i}> ^object-handle <h{i}>)''' for i, k in zip(blocks, keys)) + f'''
-->
   (<t> ^situation (concat {' |,| '.join(f'<h{i}>' for i in blocks)}))
}}

## In look-ahead, reject an operator whose result is a situation already on the path.
sp {{{n}*reject*operator*repeated-situation
   (state <s> ^internal-actions true ^operator <op> + ^world <w>)
   (<w> ^objects.object <hist>)
   (<hist> ^type history ^visited <l>)
   (<op> ^task-operator true ^result <l>)
-->
   (<s> ^operator <op> -)
}}

## ---- Search control on real moves (added, not taught; JL 16 Nov 2026, as in Tasks/From-English/mc-world): ----
## a real move back to a situation already visited is worst. It is chosen only when nothing else is left, so the agent
## prefers progress but is never trapped by its own history. The record is on the top state, not in the world, so it is
## not copied into look-ahead worlds.
## The real application records the situation it leaves (not the one it produces: recording that would make the selected
## operator itself worst, and Soar would replace it before its command completes).
sp {{{n}*apply*operator*record-real-move
   (state <s> ^superstate nil ^operator <op> ^world <w>)
   (<op> ^task-operator true)
   (<w> ^objects.object <t>)
   (<t> ^type task ^situation <sit>)
-->
   (<s> ^real-visited <sit>)
}}

sp {{{n}*compare*operator*real-repeated-situation
   (state <s> ^superstate nil ^operator <op> + ^real-visited <l>)
   (<op> ^task-operator true ^result <l>)
-->
   (<s> ^operator <op> <)
}}

## The look-ahead application records the situation it leaves and the one it produces.
sp {{{n}*apply*operator*record-path
   (state <s> ^operator <op> ^internal-actions true ^world <w>)
   (<op> ^task-operator true ^result <r>)
   (<w> ^objects <objs>)
   (<objs> ^object <hist> <t>)
   (<hist> ^type history)
   (<t> ^type task ^situation <sit>)
-->
   (<hist> ^visited <r> <sit>)
}}
''')
