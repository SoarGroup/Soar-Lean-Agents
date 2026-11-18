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
