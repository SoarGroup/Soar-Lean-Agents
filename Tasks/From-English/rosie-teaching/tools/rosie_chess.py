"""Task definitions for the chess-problem dialogs (Rosie teaching data), world conventions (18 Nov 2026).

Placement (n-queens, n-rooks, n-kings, n-knights): "You can move a clear available block onto a clear location."
The blocks start in a stack, not on a location. available ("not on a location") and clear are maintained one-argument
relations. A placed block (on a location) has the row and column of its location; "next to", "cross-diagonal" and
"jumpable" between blocks are static relations between the locations they are on (A-C1). The goal "all blocks are
placed" is expanded over the blocks of the world file.

Moving the bottom block of the stack tests that it is on nothing (a negated condition in a look-ahead application,
L11-003, Should): the world file has no table under the stack (A-C2)."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rosie_gen as R, rosie_blocks as B
from rosie_tasks import _desc, _finish, clear_concept
from rosie_swap import on, rel, clear, knight_moves


def available_concept(objs, rels):
    on_loc = {b for b, l in rels.get('on', []) if objs[l]['category'] == 'location'}
    return {i for i, a in objs.items() if a['category'] == 'block' and i not in on_loc}


def place(t, op='place-block'):
    tn = t.name
    t.add(t.t.propose(op, '''   (<objs> ^object <b> <d>)
   (<b> ^type block ^object-handle <bh>)
   (<d> ^type location ^object-handle <dh>)
   (<w> ^available <av>)
   (<av> ^argument1 <b>)
''' + clear('<b>', 'b') + '\n' + clear('<d>', 'd'),
        ['<b>', '<d>']))
    base = '''   (<w> ^anchored-world true ^objects <objs>)
   (<objs> ^object <b> <d>)
   (<b> ^object-handle <bh>)
   (<d> ^object-handle <dh>)
   (<w> ^clear <cd> ^available <av>)
   (<cd> ^argument1 <d>)
   (<av> ^argument1 <b>)'''
    on_block = base + '''
   (<w> ^on <r> ^below <bl>)
   (<r> ^argument1 <b> ^argument2 <old>)
   (<bl> ^argument1 <old> ^argument2 <b>)'''
    rhs_on = '''(<r> ^argument2 <old> - <d>)
   (<bl> ^argument1 <old> - <d>)
   (<w> ^clear <cd> - <nc> ^available <av> -)
   (<nc> ^argument1 <old>)'''
    on_nothing = base + '''
  -{(<w> ^on <r>)
    (<r> ^argument1 <b>)}'''
    rhs_nothing = '''(<w> ^on <nr> ^below <nb> ^clear <cd> - ^available <av> -)
   (<nr> ^argument1 <b> ^argument2 <d>)
   (<nb> ^argument1 <d> ^argument2 <b>)'''
    write = f'''
   (<pa> ^effect-applied true)
   (write |Place | <bh> | onto | <dh> (crlf))'''
    B._effect(t, op, ('<bh>', '<dh>'), on_block, rhs_on, write, guard_internal='from-block')
    B._effect(t, op, ('<bh>', '<dh>'), on_nothing, rhs_nothing, write, guard_internal='from-nothing')


def failure(t, tag, comment, lhs):
    t.add(f'''
## Failure ({tag}): {comment}
sp {{{t.name}*elaborate*failure*{tag}
   (state <s> ^problem-space.name {t.name} ^desireds <ds> ^world <w>)
   (<w> ^anchored-world true ^objects <objs>)
   (<objs> ^object <b1> <b2> <l1> <l2>)
   (<b1> ^type block ^object-handle <h1>)
   (<b2> ^type block ^object-handle {{ <> <h1> }})
{on('<b1>', '<l1>', 1)}
{on('<b2>', '<l2>', 2)}
{lhs}
-->
   (<s> ^failure <ds>)
}}
''')


def goal_all_placed(t, objs):
    blocks = [t.h[i] for i, a in sorted(objs.items()) if a['category'] == 'block']
    conds = '\n'.join(f'''   (<b-{h}> ^object-handle {h})
   (<l-{h}> ^type location)
{on(f'<b-{h}>', f'<l-{h}>', h)}''' for h in blocks)
    t.add(f'''
## Goal: all blocks are placed (on a location).
sp {{{t.name}*elaborate*goal*all-placed
   (state <s> ^world <w>)
   (<w> ^objects <objs>)
   (<objs> ^object <t> {' '.join(f'<b-{h}> <l-{h}>' for h in blocks)})
   (<t> ^type task)
{conds}
-->
   (<t> ^goal-met true)
}}
''')


def cross_diagonal(objs):
    locs = {i: a for i, a in objs.items() if a['category'] == 'location'}
    return [(i, j) for i in locs for j in locs if i != j
            and abs(locs[i]['row'] - locs[j]['row']) == abs(locs[i]['column'] - locs[j]['column'])]


def placement(name, world, default_world, title, nums, rules, note):
    """rules: subset of 'row', 'column', 'diagonal', 'next-to', 'jumpable'."""
    trans = '''
- Operator place-block (argument1 = the block, argument2 = the location), statement 5. available (statement 6) and clear
  (statement 7) are maintained one-argument relations; the blocks start in a stack (A-C2).
- A placed block has the row and column of the location it is on; the relations between blocks are static relations
  between their locations (A-C1).''' + ''.join({
        'row': '\n- Failure placed-same-row: two different placed blocks on locations with the same row.',
        'column': '\n- Failure place-same-col: two different placed blocks on locations with the same column.',
        'diagonal': '\n- Failure place-same-diag: two placed blocks are cross-diagonal: the difference of the rows equals the difference\n  of the columns (in size; A-C3), a static relation cross-diagonal.',
        'next-to': '\n- Failure: a block is next to another block (near between their locations, static).',
        'jumpable': '\n- Failure: a block is jumpable by another block: the knight\'s move, a static relation computed as in knight\n  swapping (alongside, diagonal-with, near; A-S3).'}[r] for r in rules) + '''
- The goal (all blocks are placed) is expanded over the blocks of the world file.'''
    desc = _desc(f'{title} ({name})', nums, f'{default_world} ({note})', trans)
    objs, rels, _ = R.read_world(world)
    st = {}
    if 'diagonal' in rules: st['cross-diagonal'] = cross_diagonal(objs)
    if 'next-to' in rules: st['near'] = rels.get('near', [])
    if 'jumpable' in rules: st['jumpable'] = knight_moves(rels)
    def concept(n, objs, rels):
        return clear_concept(n, objs, rels) if n == 'clear' else available_concept(objs, rels)
    t = R.RosieTask(name, desc, world, lambda i, a: f"{a['category']}-{i}", maintained=['clear', 'available'], concept=concept,
                    static_relations=st)
    place(t)
    if 'row' in rules:
        failure(t, 'placed-same-row', 'two placed blocks have the same row.', '   (<l1> ^row <r>)\n   (<l2> ^row <r>)')
    if 'column' in rules:
        failure(t, 'place-same-col', 'two placed blocks have the same column.', '   (<l1> ^column <c>)\n   (<l2> ^column <c>)')
    if 'diagonal' in rules:
        failure(t, 'place-same-diag', 'two placed blocks are cross-diagonal.', rel('cross-diagonal', '<l1>', '<l2>', 'x'))
    if 'next-to' in rules:
        failure(t, 'next-to', 'a block is next to another block.', rel('near', '<l1>', '<l2>', 'x'))
    if 'jumpable' in rules:
        failure(t, 'jumpable', 'a block is jumpable by another block.', rel('jumpable', '<l1>', '<l2>', 'x'))
    goal_all_placed(t, objs)
    _finish(t, name, world, default_world)
