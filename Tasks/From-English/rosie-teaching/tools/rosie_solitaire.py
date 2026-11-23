"""Task definitions for the solitaire dialogs (Rosie teaching data), world conventions (18 Nov 2026).

peg_solitaire: "If a peg is between a clear location and a block then you can remove the peg [move the peg onto a
  garbage] plus move the block onto the clear location." Operator jump (argument1 = the jumping block, argument2 = the
  clear location), one proposal per direction with the step-1..4 static relations of the grid puzzles (A-G2). A removed
  peg loses its on relation (it is off the board); with a garbage object it is on the garbage (A-P1). The goal "the number
  of covered locations is one" is read as: a covered location, and no other covered location (a negated condition in a
  goal elaboration; A-P2).
mahjong: a pair of clear available blocks of the same colour is moved onto the garbage location.
golf_solitaire (golf, tri-peaks): free blocks go onto the clear garbage, then onto the top block when one value apart. A
  block moved onto the garbage pile gets ^position 1, so it is top while clear and is trashed (A-P3)."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rosie_gen as R, rosie_blocks as B
from rosie_tasks import _desc, _finish, clear_concept
from rosie_swap import on, rel, clear
from rosie_grid import steps, DIRS8


def _effect2(t, op, k, cond, rhs, write, extra_op=''):
    tn = t.name
    t.add(f'''
## Effect of {op}{' in direction ' + str(k) if k else ''} (look-ahead).
sp {{{tn}*apply*{op}*internal{'*dir-' + str(k) if k else ''}
   (state <s> ^operator <op> ^internal-actions true ^world <w>)
   (<op> ^task-operator true ^name {op}{extra_op} ^pre-conditions-satisfied true ^argument1.object-handle <qh> ^argument2.object-handle <lh>)
{cond}
-->
   {rhs}
}}

## Effect of a completed {op} command{' in direction ' + str(k) if k else ''} on the real world (once per command).
sp {{{tn}*apply*{op}*environment-effect{'*dir-' + str(k) if k else ''}
   :o-support
   (state <s> ^superstate nil ^world <w> ^io.output-link.perform-action <pa>)
   (<pa> ^name {op} ^status complete ^argument1 <qh> ^argument2 <lh> -^effect-applied true)
{cond}
-->
   {rhs}
   (<pa> ^effect-applied true){write}
}}
''')


def peg_solitaire(name, world, default_world, nums, garbage):
    trans = '''
- Operator jump (argument1 = the jumping block, argument2 = the clear location), statement 4; every block is a peg
  (statement 6). "between" needs the three locations in a line: step-1..8 static relations from the locations' x and y,
  in the four directions and the two diagonals, one proposal per direction (A-G2, A-P6). clear is a maintained one-argument relation (statement 5).
- The jumped peg is ''' + ('moved onto the garbage object' if garbage else 'removed: it loses its on relation and is off the board') + ''' (A-P1).
- Goal (statement 11): one covered location: a covered location and no other (A-P2). "The solution has eight steps"
  (statement 7) is checked against the plans, not used.'''
    desc = _desc(f'Peg solitaire ({name})', nums, f'{default_world} (a triangle of ten locations, nine pegs)', trans)
    objs, rels, _ = R.read_world(world)
    t = R.RosieTask(name, desc, world, lambda i, a: f"{a['category']}-{i}", maintained=['clear'], concept=clear_concept,
                    static_relations=steps(objs, rels, DIRS8))
    for k in range(1, 9):
        t.add(t.t.propose(f'jump*dir-{k}', '''   (<objs> ^object <q> <l> <c> <o> <p>)
   (<q> ^type block ^object-handle <qh>)
   (<l> ^type location ^object-handle <lh>)
   (<p> ^type block)
''' + on('<p>', '<c>', 'p') + '\n' + on('<q>', '<o>', 'q') + '\n' + rel(f'step-{k}', '<l>', '<c>', 'lc') + '\n'
            + rel(f'step-{k}', '<c>', '<o>', 'co') + '\n' + clear('<l>', 'l'), ['<q>', '<l>'], attrs=f'^direction {k}'))
        cond = f'''   (<w> ^anchored-world true ^objects <objs>)
   (<objs> ^object <q> <l> <c> <o> <p>{' <g>' if garbage else ''})
   (<q> ^object-handle <qh>)
   (<l> ^object-handle <lh>)
   (<p> ^type block){chr(10) + '   (<g> ^name garbage)' if garbage else ''}
   (<w> ^on <rp> <rq> ^below <bp> <bq> ^clear <cl>)
   (<rp> ^argument1 <p> ^argument2 <c>)
   (<bp> ^argument1 <c> ^argument2 <p>)
   (<rq> ^argument1 <q> ^argument2 <o>)
   (<bq> ^argument1 <o> ^argument2 <q>)
   (<cl> ^argument1 <l>)
''' + rel(f'step-{k}', '<l>', '<c>', 'lc') + '\n' + rel(f'step-{k}', '<c>', '<o>', 'co')
        rhs = ('''(<rp> ^argument2 <c> - <g>)
   (<bp> ^argument1 <c> - <g>)''' if garbage else '''(<w> ^on <rp> - ^below <bp> -)''') + '''
   (<rq> ^argument2 <o> - <l>)
   (<bq> ^argument1 <o> - <l>)
   (<w> ^clear <cl> - <nc1> <nc2>)
   (<nc1> ^argument1 <c>)
   (<nc2> ^argument1 <o>)'''
        _effect2(t, 'jump', k, cond, rhs, '''
   (write |Jump | <qh> | onto | <lh> (crlf))''', extra_op=f' ^direction {k}')
    t.add(f'''
## Goal: the number of covered locations is one (a covered location and no other; A-P2).
sp {{{name}*elaborate*goal*one-covered
   (state <s> ^world <w>)
   (<w> ^objects <objs> ^below <b1>)
   (<objs> ^object <t> <l1>)
   (<t> ^type task)
   (<l1> ^type location)
   (<b1> ^argument1 <l1>)
  -{{(<w> ^below <b2>)
    (<b2> ^argument1 {{ <> <l1> <l2> }})
    (<objs> ^object <l2>)
    (<l2> ^type location)}}
-->
   (<t> ^goal-met true)
}}
''')
    _finish(t, name, world, default_world)


def mahjong(name, world, default_world, nums=(4, 5, 6, 8)):
    from rosie_chess import available_concept
    trans = '''
- Operator move-pair (argument1, argument2 = the two blocks), statement 4: two different clear available blocks of the same
  colour go onto the garbage location. available (not on a location, statement 5) and clear (statement 6) are maintained
  one-argument relations; a block that a moved block was on becomes clear.
- The goal (statement 8) is expanded over the blocks of the world file: every block is on the garbage.'''
    desc = _desc(f'Mahjong ({name})', nums, f'{default_world} (seven coloured blocks in stacks; a garbage location)', trans)
    objs, rels, _ = R.read_world(world)
    def concept(n, objs, rels):
        return clear_concept(n, objs, rels) if n == 'clear' else available_concept(objs, rels)
    t = R.RosieTask(name, desc, world, lambda i, a: f"{a['category']}-{i}", maintained=['clear', 'available'], concept=concept)
    tn = t.name
    t.add(t.t.propose('move-pair', '''   (<objs> ^object <b1> <b2>)
   (<b1> ^type block ^color <c> ^object-handle <h1>)
   (<b2> ^type block ^color <c> ^object-handle { <> <h1> <h2> })
   (<w> ^available <a1> <a2> ^clear <c1> <c2>)
   (<a1> ^argument1 <b1>)
   (<a2> ^argument1 <b2>)
   (<c1> ^argument1 <b1>)
   (<c2> ^argument1 <b2>)''', ['<b1>', '<b2>']))
    # Each of the two blocks is either on another block or on nothing; one rule per combination.
    def part(i, on_block):
        if on_block:
            return (f'''   (<w> ^on <r{i}> ^below <bl{i}>)
   (<r{i}> ^argument1 <b{i}> ^argument2 <x{i}>)
   (<bl{i}> ^argument1 <x{i}> ^argument2 <b{i}>)''',
                    f'''   (<r{i}> ^argument2 <x{i}> - <g>)
   (<bl{i}> ^argument1 <x{i}> - <g>)
   (<w> ^clear <n{i}>)
   (<n{i}> ^argument1 <x{i}>)''')
        return (f'''  -{{(<w> ^on <r{i}>)
    (<r{i}> ^argument1 <b{i}>)}}''',
                f'''   (<w> ^on <r{i}> ^below <bl{i}>)
   (<r{i}> ^argument1 <b{i}> ^argument2 <g>)
   (<bl{i}> ^argument1 <g> ^argument2 <b{i}>)''')
    for o1 in (True, False):
        for o2 in (True, False):
            c1, r1 = part(1, o1); c2, r2 = part(2, o2)
            tag = ('b' if o1 else 'n') + ('b' if o2 else 'n')
            cond = f'''   (<w> ^anchored-world true ^objects <objs>)
   (<objs> ^object <b1> <b2> <g>)
   (<b1> ^object-handle <h1>)
   (<b2> ^object-handle <h2>)
   (<g> ^type location ^name garbage)
   (<w> ^available <a1> <a2> ^clear <c1> <c2>)
   (<a1> ^argument1 <b1>)
   (<a2> ^argument1 <b2>)
   (<c1> ^argument1 <b1>)
   (<c2> ^argument1 <b2>)
{c1}
{c2}'''
            rhs = f'''(<w> ^available <a1> - <a2> -)
{r1}
{r2}'''
            t.add(f'''
## Effect of move-pair (look-ahead; {tag}).
sp {{{tn}*apply*move-pair*internal*{tag}
   (state <s> ^operator <op> ^internal-actions true ^world <w>)
   (<op> ^task-operator true ^name move-pair ^pre-conditions-satisfied true ^argument1.object-handle <h1> ^argument2.object-handle <h2>)
{cond}
-->
   {rhs}
}}

## Effect of a completed move-pair command on the real world (once per command; {tag}).
sp {{{tn}*apply*move-pair*environment-effect*{tag}
   :o-support
   (state <s> ^superstate nil ^world <w> ^io.output-link.perform-action <pa>)
   (<pa> ^name move-pair ^status complete ^argument1 <h1> ^argument2 <h2> -^effect-applied true)
{cond}
-->
   {rhs}
   (<pa> ^effect-applied true)
   (write |Move | <h1> | and | <h2> | onto the garbage| (crlf))
}}
''')
    blocks = [t.h[i] for i, a in sorted(objs.items()) if a['category'] == 'block']
    t.add(f'''
## Goal: all blocks are on a garbage.
sp {{{tn}*elaborate*goal*all-on-garbage
   (state <s> ^world <w>)
   (<w> ^objects <objs>)
   (<objs> ^object <t> <g> {' '.join(f'<b-{h}>' for h in blocks)})
   (<t> ^type task)
   (<g> ^type location ^name garbage)
''' + '\n'.join(f'''   (<b-{h}> ^object-handle {h})
{on(f'<b-{h}>', '<g>', h)}''' for h in blocks) + '''
-->
   (<t> ^goal-met true)
}
''')
    _finish(t, name, world, default_world)


def _pile_position(i, objs, rels):
    """A block's position: 1 when it is on the garbage pile (on the garbage, or on a block that is), else 0 for absent (A-P3)."""
    on = dict(rels.get('on', []))
    seen = set()
    while i in on and i not in seen:
        seen.add(i); i = on[i]
        if objs[i].get('name') == 'garbage': return 1
    return 0


def golf_solitaire(name, world, default_world, title, nums=(4, 5, 6, 8, 9, 10, 15, 16)):
    trans = '''
- Operator move (argument1 = the block, argument2 = the garbage or the top block): statement 4 (a free block onto the
  clear garbage) and statements 8 and 10 (a free block onto the top block when its value is one less or one more).
- free (statement 6: clear and no position) and top (statement 9: clear and position one) are expanded in place. The
  blocks start with ^position 0, read as "absent" (A-P3); a block moved onto the garbage pile gets ^position 1, so it is
  top while clear and trashed (statement 16). A block's position is read as that of the pile it is in: 1 when it is on the
  garbage or on a block that is (so the example states, which give no position to the blocks, come out as intended).
- clear is a maintained one-argument relation (statement 5). A block can lie on two blocks (tri-peaks), so the block it
  leaves becomes clear only when no other block is on it (a negated condition in the applications; A-P4).
- The goal (statement 15) is expanded over the blocks of the world file. "The solution has nine steps" (statement 11)
  is checked against the plans, not used.'''
    desc = _desc(f'{title} ({name})', nums, f'{default_world} (nine numbered blocks in three piles; a garbage location)', trans)
    objs, rels, _ = R.read_world(world)
    t = R.RosieTask(name, desc, world, lambda i, a: f"{a['category']}-{i}", maintained=['clear'], concept=clear_concept,
                    extra_props=lambda i, a, rels: ({'position': _pile_position(i, objs, rels), 'value-plus-1': a['value'] + 1,
                                                     'value-minus-1': a['value'] - 1} if a['category'] == 'block' else {}))
    tn = t.name
    free = '''   (<b> ^type block ^position 0 ^value <v> ^object-handle <bh>)
''' + clear('<b>', 'b')
    t.add(t.t.propose('move*onto-garbage', '''   (<objs> ^object <b> <d>)
''' + free + '''
   (<d> ^type location ^name garbage ^object-handle <dh>)
''' + clear('<d>', 'd'), ['<b>', '<d>']))
    for tag in ('one-less', 'one-more'):
        # "the value of a free block is one less [more] than the value of a top block": a proposal cannot compute on its
        # left side, so each block carries its value plus one and minus one, static, set at initialization (A-P5).
        attr = 'value-plus-1' if tag == 'one-less' else 'value-minus-1'
        t.add(t.t.propose(f'move*onto-top*{tag}', f'''   (<objs> ^object <b> <d>)
   (<b> ^type block ^position 0 ^{attr} <tv> ^object-handle <bh>)
''' + clear('<b>', 'b') + '''
   (<d> ^type block ^position 1 ^value <tv> ^object-handle <dh>)
''' + clear('<d>', 'd'), ['<b>', '<d>']))
    cond_common = '''   (<w> ^anchored-world true ^objects <objs>)
   (<objs> ^object <b> <d>)
   (<b> ^object-handle <bh> ^position 0)
   (<d> ^object-handle <dh>)
   (<w> ^clear <cd>)
   (<cd> ^argument1 <d>)'''
    variants = {
        'from-block-freed': ('''
   (<w> ^on <r> ^below <bl>)
   (<r> ^argument1 <b> ^argument2 <x>)
   (<bl> ^argument1 <x> ^argument2 <b>)
  -{(<w> ^on <r2>)
    (<r2> ^argument1 { <> <b> } ^argument2 <x>)}''', '''(<r> ^argument2 <x> - <d>)
   (<bl> ^argument1 <x> - <d>)
   (<w> ^clear <cd> - <nc>)
   (<nc> ^argument1 <x>)
   (<b> ^position 0 - 1)'''),
        'from-block-still-covered': ('''
   (<w> ^on <r> ^below <bl> ^on <r2>)
   (<r> ^argument1 <b> ^argument2 <x>)
   (<bl> ^argument1 <x> ^argument2 <b>)
   (<r2> ^argument1 { <> <b> } ^argument2 <x>)''', '''(<r> ^argument2 <x> - <d>)
   (<bl> ^argument1 <x> - <d>)
   (<w> ^clear <cd> -)
   (<b> ^position 0 - 1)'''),
        'from-nothing': ('''
  -{(<w> ^on <r>)
    (<r> ^argument1 <b>)}''', '''(<w> ^on <nr> ^below <nb> ^clear <cd> -)
   (<nr> ^argument1 <b> ^argument2 <d>)
   (<nb> ^argument1 <d> ^argument2 <b>)
   (<b> ^position 0 - 1)'''),
    }
    for tag, (c, r) in variants.items():
        B._effect(t, 'move', ('<bh>', '<dh>'), cond_common + c, r, '''
   (<pa> ^effect-applied true)
   (write |Move | <bh> | onto | <dh> (crlf))''', guard_internal=tag)
    blocks = [t.h[i] for i, a in sorted(objs.items()) if a['category'] == 'block']
    t.add(f'''
## Goal: all blocks are trashed (position one).
sp {{{tn}*elaborate*goal*all-trashed
   (state <s> ^world <w>)
   (<w> ^objects <objs>)
   (<objs> ^object <t> {' '.join(f'<b-{h}>' for h in blocks)})
   (<t> ^type task)
''' + '\n'.join(f'   (<b-{h}> ^object-handle {h} ^position 1)' for h in blocks) + '''
-->
   (<t> ^goal-met true)
}
''')
    _finish(t, name, world, default_world)
