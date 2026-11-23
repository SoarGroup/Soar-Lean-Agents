"""Operators shared by the block-puzzle dialogs (Rosie teaching data), world conventions. Each builder adds a proposal and
its two applications (look-ahead and completed command) to a RosieTask, with the maintenance of the maintained concepts.

  move_clear(t, name, larger)  "You can move a clear block onto a clear object [that is larger than the block]."
                                (tower-of-hanoi, -4, -5; blocks-world, blocks-world2). Maintains clear.
  move_block(t, name)          "You can move a block onto a location." (sorting). No concept to maintain.
  move_pile(t, name, k_max, clear=True, accessible=False)
                               "If the number of the locations between a location and a [accessible] covered location is the
                                number of the blocks that are on the covered location then you can move it onto the former
                                location." (stacking frogs). Maintains clear (when the goal uses it) and the block count.
"""

def _effect(t, name, args, cond, rhs, write, guard_internal='', guard_env=''):
    tn = t.name
    a1, a2 = args
    t.add(f'''
## Effect of {name} (look-ahead).
sp {{{tn}*apply*{name}*internal{guard_internal and '*' + guard_internal}
   (state <s> ^operator <op> ^internal-actions true ^world <w>)
   (<op> ^task-operator true ^name {name} ^pre-conditions-satisfied true ^argument1.object-handle {a1} ^argument2.object-handle {a2})
{cond}
-->
   {rhs}
}}

## Effect of a completed {name} command on the real world (once per command).
sp {{{tn}*apply*{name}*environment-effect{guard_internal and '*' + guard_internal}
   :o-support
   (state <s> ^superstate nil ^world <w> ^io.output-link.perform-action <pa>)
   (<pa> ^name {name} ^status complete ^argument1 {a1} ^argument2 {a2} -^effect-applied true)
{cond}
-->
   {rhs}{write}
}}
''')

def move_clear(t, name='move', larger=False):
    """Statement: a clear block onto a clear object (that is larger than the block). clear is maintained: the destination
    stops being clear and the object the block left becomes clear (only a clear block moves, so nothing else was on it)."""
    lg = ('''
   (<b> ^volume <bv>)
   (<d> ^volume > <bv>)''' if larger else '')
    t.add(t.t.propose(name, f'''   (<objs> ^object <b> <d>)
   (<b> ^type block ^object-handle <bh>)
   (<d> ^object-handle <dh>)
   (<w> ^clear <cb> <cd>)
   (<cb> ^argument1 <b>)
   (<cd> ^argument1 <d>){lg}''', ['<b>', '<d>']))
    cond = '''   (<w> ^anchored-world true ^objects <objs>)
   (<objs> ^object <b> <d>)
   (<b> ^object-handle <bh>)
   (<d> ^object-handle <dh>)
   (<w> ^on <r> ^below <bl> ^clear <cd>)
   (<r> ^argument1 <b> ^argument2 <old>)
   (<bl> ^argument1 <old> ^argument2 <b>)
   (<cd> ^argument1 <d>)'''
    rhs = '''(<r> ^argument2 <old> - <d>)
   (<bl> ^argument1 <old> - <d>)
   (<w> ^clear <cd> - <nc>)
   (<nc> ^argument1 <old>)'''
    _effect(t, name, ('<bh>', '<dh>'), cond, rhs, '''
   (<pa> ^effect-applied true)
   (write |Move | <bh> | onto | <dh> (crlf))''')

def move_block(t, name='move'):
    """Statement: a block onto a location (any block, any location other than the one it is on)."""
    t.add(t.t.propose(name, '''   (<objs> ^object <b> <l>)
   (<b> ^type block ^object-handle <bh>)
   (<l> ^type location ^object-handle <lh>)
   (<w> ^on <r>)
   (<r> ^argument1 <b> ^argument2 { <> <l> <old> })''', ['<b>', '<l>']))
    cond = '''   (<w> ^anchored-world true ^objects <objs>)
   (<objs> ^object <b> <l>)
   (<b> ^object-handle <bh>)
   (<l> ^object-handle <lh>)
   (<w> ^on <r> ^below <bl>)
   (<r> ^argument1 <b> ^argument2 { <> <l> <old> })
   (<bl> ^argument1 <old> ^argument2 <b>)'''
    rhs = '''(<r> ^argument2 <old> - <l>)
   (<bl> ^argument1 <old> - <l>)'''
    _effect(t, name, ('<bh>', '<lh>'), cond, rhs, '''
   (<pa> ^effect-applied true)
   (write |Move | <bh> | onto | <lh> (crlf))''')

def move_pile(t, name='move', k_max=4, clear=True, accessible=False):
    """Statement: the blocks on a covered location C move together onto a location L when the number of locations between
    L and C (counted so that adjacent locations count 1, as the instructor's instance count fixes; static relation apart-k)
    is the number of blocks on C (maintained attribute ^block-count). argument1 = C, argument2 = L.
    C is covered whenever its block count is at least 1, so covered needs no test of its own."""
    acc = '''
   (<w> ^accessible <ac>)
   (<ac> ^argument1 <c>)''' if accessible else ''
    for k in range(1, k_max + 1):
        t.add(t.t.propose(f'{name}*{k}-blocks', f'''   (<objs> ^object <c> <l>)
   (<c> ^type location ^block-count {k} ^object-handle <ch>)
   (<l> ^type location ^object-handle <lh>)
   (<w> ^apart-{k} <ap>)
   (<ap> ^argument1 <l> ^argument2 <c>){acc}''', ['<c>', '<l>']))
    base = '''   (<w> ^anchored-world true ^objects <objs>)
   (<objs> ^object <c> <l>)
   (<c> ^object-handle <ch>)
   (<l> ^object-handle <lh>)'''
    # every block on C now on L (one instantiation per block, all in the same phase)
    _effect(t, name, ('<ch>', '<lh>'), base + '''
   (<w> ^on <r> ^below <bl>)
   (<r> ^argument1 <b> ^argument2 <c>)
   (<bl> ^argument1 <c> ^argument2 <b>)''', '''(<r> ^argument2 <c> - <l>)
   (<bl> ^argument1 <c> - <l>)''', '', 'blocks')
    # block counts, and clear: C is now clear; L stops being clear if it was empty
    for case, lcond, crhs in (('onto-empty', '^block-count { <m> 0 }', '\n   (<w> ^clear <cl> -)' if clear else ''),
                              ('onto-pile', '^block-count { <m> > 0 }', '')):
        ccl = '\n   (<w> ^clear <cl>)\n   (<cl> ^argument1 <l>)' if (clear and case == 'onto-empty') else ''
        add_c = '\n   (<w> ^clear <nc>)\n   (<nc> ^argument1 <c>)' if clear else ''
        _effect(t, name, ('<ch>', '<lh>'), base + f'''
   (<c> ^block-count {{ <k> > 0 }})
   (<l> {lcond}){ccl}''', f'''(<c> ^block-count <k> - 0)
   (<l> ^block-count <m> - (+ <m> <k>)){crhs}{add_c}''', '''
   (<pa> ^effect-applied true)
   (write |Move the | <k> | block(s) on | <ch> | onto | <lh> (crlf))''', 'count-' + case)

# ---------------------------------------------------------------- Search-control items (control.py; 22 Nov 2026)
def sc_no_repeat_smallest(t, name, sc_id, op='move'):
    """Search-control item (operator-preference): 'During look-ahead, do not move the smallest block twice in a row.'
    Bookkeeping: the task object records the handle of the block moved last (^sc-last-moved). It is kept in the world so
    that look-ahead copies it; no problem rule reads it. Two application rules per case (L3-052): one replaces the record,
    one adds it when there is none. In a look-ahead state (^real false) a move of the smallest block is rejected when that
    block was the last one moved. Rule names carry the item ID."""
    sid = sc_id.lower()
    def rec(case, state, op_test, extra=''):
        return f'''
sp {{{name}*{sid}*apply*{op}*last-moved*{case}{'*first' if extra == 'first' else ''}
{':o-support' + chr(10) if 'perform-action' in state else ''}   {state}
   {op_test}
   (<w> ^anchored-world true ^objects.object <t>)
   (<t> ^type task {'-^sc-last-moved' if extra == 'first' else '^sc-last-moved { <old> <> <bh> }'})
-->
   (<t> ^sc-last-moved {'<bh>' if extra == 'first' else '<old> - <bh>'})
}}'''
    internal = ('(state <s> ^problem-space.name ' + name + ' ^operator <op> ^internal-actions true ^world <w>)',
                '(<op> ^name ' + op + ' ^pre-conditions-satisfied true ^argument1.object-handle $ <bh>)')
    env = ('(state <s> ^problem-space.name ' + name + ' ^superstate nil ^world <w> ^io.output-link.perform-action <pa>)',
           '(<pa> ^name ' + op + ' ^status complete ^argument1 <bh>)')
    t.add(f'''
## {sc_id} [operator-preference]: during look-ahead, do not move the smallest block twice in a row.
## Bookkeeping: an internally applied {op} (look-ahead) or a {op} completed by the environment (the real world)
## records the block it moved on the task object (^sc-last-moved).'''
          + rec('internal', *internal) + rec('internal', *internal, 'first')
          + rec('environment', *env) + rec('environment', *env, 'first') + f'''

## Control: in look-ahead, reject moving the smallest block again right after it was moved.
sp {{{name}*{sid}*compare*{op}*smallest-twice*reject
   (state <s> ^problem-space.name {name} ^real false ^operator <o> + ^world <w>)
   (<o> ^name {op} ^argument1.object-handle $ <bh>)
   (<w> ^anchored-world true ^objects <objs>)
   (<objs> ^object <t> <b>)
   (<t> ^type task ^sc-last-moved $ <bh>)
   (<b> ^type block ^object-handle $ <bh> ^volume <bv>)
  -{{(<objs> ^object <x>)
    (<x> ^type block ^volume < <bv>)}}
-->
   (<s> ^operator <o> -)
}}
''')

def sc_largest_first(t, name, sc_id, op='move', home_test='^type location ^color blue'):
    """Search-control item (operator-preference): 'Work first on the largest block that is not yet in place: never move a
    block that is in place, and move the largest block that is not in place onto its place whenever it can.' A block is in
    place when it is the largest block and on the home location (blue, from the goal), or when it is on the next larger
    block and that block is in place. In place, the largest block not in place and its place are derived on the state
    (i-supported, never copied into look-ahead); the rules apply in the real state and in look-ahead. Rule names carry
    the item ID."""
    sid = sc_id.lower()
    ps = f'(state <s> ^problem-space.name {name} ^world <w>)'
    t.add(f'''
## {sc_id} [operator-preference]: work first on the largest block that is not yet in place.
## In place (state elaboration): the largest block on the home location.
sp {{{name}*{sid}*elaborate*in-place*largest
   {ps}
   (<w> ^anchored-world true ^objects <objs> ^on <r>)
   (<objs> ^object <b> <h>)
   (<b> ^type block ^volume <bv>)
   (<h> {home_test})
   (<r> ^argument1 <b> ^argument2 <h>)
  -{{(<objs> ^object <x>)
    (<x> ^type block ^volume > <bv>)}}
-->
   (<s> ^sc-in-place <b>)
}}

## In place: a block on the next larger block, when that block is in place.
sp {{{name}*{sid}*elaborate*in-place*next
   {ps}
   (<s> ^sc-in-place <y>)
   (<w> ^anchored-world true ^objects <objs> ^on <r>)
   (<objs> ^object <b>)
   (<b> ^type block ^volume <bv>)
   (<y> ^volume <yv>)
   (<r> ^argument1 <b> ^argument2 <y>)
  -{{(<objs> ^object <x>)
    (<x> ^type block ^volume {{ > <bv> < <yv> }})}}
-->
   (<s> ^sc-in-place <b>)
}}

## The largest block not in place, when it is the largest block: its place is the home location.
sp {{{name}*{sid}*elaborate*target*largest
   {ps}
   (<w> ^anchored-world true ^objects <objs>)
   (<objs> ^object <b> <h>)
   (<b> ^type block ^volume <bv>)
   (<h> {home_test})
  -(<s> ^sc-in-place <b>)
  -{{(<objs> ^object <x>)
    (<x> ^type block ^volume > <bv>)}}
-->
   (<s> ^sc-target <tg>)
   (<tg> ^block <b> ^place <h>)
}}

## The largest block not in place, when larger blocks are all in place: its place is the next larger block.
sp {{{name}*{sid}*elaborate*target*next
   {ps}
   (<s> ^sc-in-place <y>)
   (<w> ^anchored-world true ^objects <objs>)
   (<objs> ^object <b>)
   (<b> ^type block ^volume <bv>)
   (<y> ^volume {{ <yv> > <bv> }})
  -(<s> ^sc-in-place <b>)
  -{{(<objs> ^object <x>)
    (<x> ^type block ^volume {{ > <bv> < <yv> }})}}
  -{{(<objs> ^object <z>)
    (<z> ^type block ^volume > <bv>)
    -(<s> ^sc-in-place <z>)}}
-->
   (<s> ^sc-target <tg>)
   (<tg> ^block <b> ^place <y>)
}}

## Control: never move a block that is in place.
sp {{{name}*{sid}*compare*{op}*in-place*reject
   (state <s> ^problem-space.name {name} ^operator <o> + ^sc-in-place <b>)
   (<o> ^name {op} ^argument1.object-handle $ <bh>)
   (<b> ^object-handle $ <bh>)
-->
   (<s> ^operator <o> -)
}}

## Control: moving the largest block that is not in place onto its place is best.
sp {{{name}*{sid}*compare*{op}*largest-to-place*best
   (state <s> ^problem-space.name {name} ^operator <o> + ^sc-target <tg>)
   (<tg> ^block.object-handle $ <bh> ^place.object-handle $ <ph>)
   (<o> ^name {op} ^argument1.object-handle $ <bh> ^argument2.object-handle $ <ph>)
-->
   (<s> ^operator <o> >)
}}
''')

def sc_smallest_not_back(t, name, sc_id, op='move'):
    """Search-control item (operator-preference): 'In look-ahead, do not move the smallest block back to the location it
    was on before.' A block is on a location (its peg) when it is on that location or on a block that is on it; this is
    derived on the state (i-supported, never copied). Bookkeeping: when the smallest block moves, the task object records
    the location it left (^sc-smallest-from); kept in the world so look-ahead copies it, read by no problem rule. In a
    look-ahead state, after the evaluated operator has been applied (^tried-tied-operator), a move of the smallest block
    onto that location's stack is rejected. Rule names carry the item ID."""
    sid = sc_id.lower()
    smallest = '''  -{(<objs> ^object <x>)
    (<x> ^type block ^volume < <bv>)}'''
    def record(case, state, op_test, guard_in, guard_out, first):
        return f'''
sp {{{name}*{sid}*apply*{op}*smallest-from*{case}{'*first' if first else ''}
{':o-support' + chr(10) if case == 'environment' else ''}   {state}
   {op_test}
   (<w> ^anchored-world true ^objects <objs>)
   (<objs> ^object <t> <b>)
   (<b> ^type block ^object-handle $ <bh> ^volume <bv>)
{smallest}
   (<s> ^sc-on-location <ol>)
   (<ol> ^block <b> ^location <l>){guard_in}
   (<t> ^type task {'-^sc-smallest-from' if first else '^sc-smallest-from { <old> <> <l> }'})
-->
   (<t> ^sc-smallest-from {'<l>' if first else '<old> - <l>'}){guard_out}
}}'''
    internal = (f'(state <s> ^problem-space.name {name} ^operator <op> ^internal-actions true ^world <w>)',
                f'(<op> ^name {op} ^pre-conditions-satisfied true ^argument1.object-handle $ <bh>)', '', '')
    env = (f'(state <s> ^problem-space.name {name} ^superstate nil ^world <w> ^io.output-link.perform-action <pa>)',
           f'(<pa> ^name {op} ^status complete ^argument1 <bh>)', '\n   (<pa> -^sc-from-recorded true)',
           '\n   (<pa> ^sc-from-recorded true)')
    t.add(f'''
## {sc_id} [operator-preference]: in look-ahead, do not move the smallest block back to the location it was on before.
## A block is on a location: directly, or on a block that is on it (state elaboration, not copied).
sp {{{name}*{sid}*elaborate*on-location*direct
   (state <s> ^problem-space.name {name} ^world <w>)
   (<w> ^anchored-world true ^objects <objs> ^on <r>)
   (<objs> ^object <b> <l>)
   (<b> ^type block)
   (<l> ^type location)
   (<r> ^argument1 <b> ^argument2 <l>)
-->
   (<s> ^sc-on-location <ol>)
   (<ol> ^block <b> ^location <l>)
}}

sp {{{name}*{sid}*elaborate*on-location*stacked
   (state <s> ^problem-space.name {name} ^world <w> ^sc-on-location <ol1>)
   (<ol1> ^block <y> ^location <l>)
   (<w> ^anchored-world true ^objects <objs> ^on <r>)
   (<objs> ^object <b>)
   (<b> ^type block)
   (<r> ^argument1 <b> ^argument2 <y>)
-->
   (<s> ^sc-on-location <ol>)
   (<ol> ^block <b> ^location <l>)
}}
## Bookkeeping: when the smallest block moves (internally or in the environment), record the location it leaves.'''
          + record('internal', *internal[:2], internal[2], internal[3], False)
          + record('internal', *internal[:2], internal[2], internal[3], True)
          + record('environment', *env[:2], env[2], env[3], False)
          + record('environment', *env[:2], env[2], env[3], True) + f'''

## Control: in look-ahead, reject moving the smallest block onto the stack of the location it left last time.
sp {{{name}*{sid}*compare*{op}*smallest-back*reject*location
   (state <s> ^problem-space.name {name} ^real false ^tried-tied-operator <any> ^operator <o> + ^world <w>)
   (<o> ^name {op} ^argument1.object-handle $ <bh> ^argument2.object-handle $ <dh>)
   (<w> ^anchored-world true ^objects <objs>)
   (<objs> ^object <t> <b> <d>)
   (<b> ^type block ^object-handle $ <bh> ^volume <bv>)
{smallest}
   (<d> ^type location ^object-handle $ <dh>)
   (<t> ^type task ^sc-smallest-from <fl>)
   (<fl> ^object-handle $ <dh>)
-->
   (<s> ^operator <o> -)
}}

sp {{{name}*{sid}*compare*{op}*smallest-back*reject*block
   (state <s> ^problem-space.name {name} ^real false ^tried-tied-operator <any> ^operator <o> + ^world <w>
              ^sc-on-location <ol>)
   (<o> ^name {op} ^argument1.object-handle $ <bh> ^argument2.object-handle $ <dh>)
   (<w> ^anchored-world true ^objects <objs>)
   (<objs> ^object <t> <b> <d>)
   (<b> ^type block ^object-handle $ <bh> ^volume <bv>)
{smallest}
   (<d> ^type block ^object-handle $ <dh>)
   (<ol> ^block <d> ^location <dl>)
   (<t> ^type task ^sc-smallest-from <fl>)
   (<fl> ^object-handle $ <flh>)
   (<dl> ^object-handle $ <flh>)
-->
   (<s> ^operator <o> -)
}}
''')
