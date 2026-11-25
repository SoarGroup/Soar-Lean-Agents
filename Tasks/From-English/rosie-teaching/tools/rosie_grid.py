"""Task definitions for the grid-puzzle dialogs (Rosie teaching data), world conventions (18 Nov 2026).

adjacent ("next to an object but not diagonal with it") is a static relation between locations, computed from the
world file's near and diagonal-with relations; a block is adjacent to a location when the location it is on is (A-G1).
clear is a maintained one-argument relation. A push ("a covered location between a clear location and an occupied
location") needs the three locations in a line: a static relation per direction (step-1 .. step-4, argument1 the
neighbour of argument2 in that direction), computed from the locations' coordinates (A-G2)."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import re
import rosie_gen as R, rosie_blocks as B, control as C
from rosie_tasks import _desc, _finish, clear_concept
from rosie_swap import on, rel, clear, propose_move, move_effect


def adjacent(rels):
    near, diag = set(rels.get('near', [])), set(rels.get('diagonal-with', []))
    return sorted(p for p in near if p not in diag and (p[1], p[0]) not in diag)


def coords(a):
    return (a.get('x', a.get('column')), a.get('y', a.get('row')))


DIRS4 = [(1, 0), (-1, 0), (0, 1), (0, -1)]
DIRS8 = DIRS4 + [(1, 1), (-1, -1), (1, -1), (-1, 1)]


def steps(objs, rels, dirs=DIRS4):
    """step-k(A, B): location A is location B's neighbour in direction k (dirs[k-1] in x, y), from the locations'
    coordinates (A-G2)."""
    locs = {i: coords(a) for i, a in objs.items() if a['category'] == 'location'}
    out = {f'step-{k}': [] for k in range(1, len(dirs) + 1)}
    for a, (ax, ay) in locs.items():
        for b, (bx, by) in locs.items():
            if (ax - bx, ay - by) in dirs:
                out[f'step-{dirs.index((ax - bx, ay - by)) + 1}'].append((a, b))
    return {k: v for k, v in out.items() if v}


def step_move(t, op, verb, block_test):
    """'If a [blue] block is adjacent to a clear location then you can move the block onto the location.'"""
    propose_move(t, 'adjacent-clear', block_test + on('<b>', '<l1>', 'b') + '\n' + rel('adjacent', '<d>', '<l1>', 'd') + '\n' + clear('<d>', 'd'), op=op)
    move_effect(t, op, verb)


def push(t, pusher_test, name='push'):
    """'If a covered location C is between a clear location L and an occupied location O then you can move a block on C
    onto L plus move the block on O onto C.' One proposal per direction (A-G2). argument1 = the pushed block,
    argument2 = L; the pusher and C are found again by the applications (the pusher is the block on O, the neighbour of C
    opposite L)."""
    tn = t.name
    for k in range(1, 5):
        t.add(t.t.propose(f'{name}*dir-{k}', f'''   (<objs> ^object <p> <l> <c> <o> <q>)
   (<p> ^type block ^object-handle <ph>)
   (<l> ^type location ^object-handle <lh>)
   (<q> ^type block)
{pusher_test}
''' + on('<p>', '<c>', 'p') + '\n' + on('<q>', '<o>', 'q') + '\n' + rel(f'step-{k}', '<l>', '<c>', 'lc') + '\n'
            + rel(f'step-{k}', '<c>', '<o>', 'co') + '\n' + clear('<l>', 'l'), ['<p>', '<l>'], attrs=f'^direction {k}'))
    for k in range(1, 5):
        cond = f'''   (<w> ^anchored-world true ^objects <objs>)
   (<objs> ^object <p> <l> <c> <o> <q>)
   (<p> ^object-handle <ph>)
   (<l> ^object-handle <lh>)
   (<q> ^type block)
{pusher_test}
   (<w> ^on <rp> <rq> ^below <bp> <bq> ^clear <cl>)
   (<rp> ^argument1 <p> ^argument2 <c>)
   (<bp> ^argument1 <c> ^argument2 <p>)
   (<rq> ^argument1 <q> ^argument2 <o>)
   (<bq> ^argument1 <o> ^argument2 <q>)
   (<cl> ^argument1 <l>)
''' + rel(f'step-{k}', '<l>', '<c>', 'lc') + '\n' + rel(f'step-{k}', '<c>', '<o>', 'co')
        rhs = '''(<rp> ^argument2 <c> - <l>)
   (<bp> ^argument1 <c> - <l>)
   (<rq> ^argument2 <o> - <c>)
   (<bq> ^argument1 <o> - <c>)
   (<w> ^clear <cl> - <nc>)
   (<nc> ^argument1 <o>)'''
        t.add(f'''
## Effect of {name} in direction {k} (look-ahead): the pushed block moves onto the clear location and the pusher onto
## the location the pushed block left.
sp {{{tn}*apply*{name}*internal*dir-{k}
   (state <s> ^operator <op> ^internal-actions true ^world <w>)
   (<op> ^task-operator true ^name {name} ^direction {k} ^pre-conditions-satisfied true ^argument1.object-handle <ph> ^argument2.object-handle <lh>)
{cond}
-->
   {rhs}
}}

## Effect of a completed {name} command in direction {k} on the real world (once per command).
sp {{{tn}*apply*{name}*environment-effect*dir-{k}
   :o-support
   (state <s> ^superstate nil ^world <w> ^io.output-link.perform-action <pa>)
   (<pa> ^name {name} ^status complete ^argument1 <ph> ^argument2 <lh> -^effect-applied true)
{cond}
-->
   {rhs}
   (<pa> ^effect-applied true)
   (write |Push | <ph> | onto | <lh> (crlf))
}}
''')


def goal_block_on(t, name, pairs, rule):
    """pairs: [(block colour, location colour)]: some block of the first colour is on a location of the second, for each pair."""
    conds = '\n'.join(f'''   (<b{k}> ^type block ^color {bc})
   (<l{k}> ^type location ^color {lc})
{on(f'<b{k}>', f'<l{k}>', k)}''' for k, (bc, lc) in enumerate(pairs))
    t.add(f'''
## Goal: {', '.join(f'a {bc} block is on a {lc} location' for bc, lc in pairs)}.
sp {{{name}*elaborate*goal*{rule}
   (state <s> ^world <w>)
   (<w> ^objects <objs>)
   (<objs> ^object <t> {' '.join(f'<b{k}> <l{k}>' for k in range(len(pairs)))})
   (<t> ^type task)
{conds}
-->
   (<t> ^goal-met true)
}}
''')


def goal_all_matched(t, name, objs, attr):
    """'There are N matched locations' with 'a location is matched if its <attr> is the <attr> of the block on it',
    expanded over the blocks of the world file: every block is on the location with its value (A-G3)."""
    blocks = [(t.h[i], a[attr]) for i, a in sorted(objs.items()) if a['category'] == 'block']
    conds = '\n'.join(f'''   (<b-{h}> ^object-handle {h})
   (<l-{h}> ^type location ^{attr} {v})
{on(f'<b-{h}>', f'<l-{h}>', h)}''' for h, v in blocks)
    t.add(f'''
## Goal: every location is matched (its {attr} is the {attr} of the block on it).
sp {{{name}*elaborate*goal*all-matched
   (state <s> ^world <w>)
   (<w> ^objects <objs>)
   (<objs> ^object <t> {' '.join(f'<b-{h}> <l-{h}>' for h, _ in blocks)})
   (<t> ^type task)
{conds}
-->
   (<t> ^goal-met true)
}}
''')


def _task(name, world, title, nums, note, trans, default_world, extra_static=None):
    desc = _desc(f'{title} ({name})', nums, f'{default_world} ({note})', trans)
    objs, rels, _ = R.read_world(world)
    st = {'adjacent': adjacent(rels)}
    st.update(extra_static(objs, rels) if extra_static else {})
    t = R.RosieTask(name, desc, world, lambda i, a: f"{a['category']}-{i}", maintained=['clear'], concept=clear_concept,
                    static_relations=st)
    return t, objs


SLIDE_TRANS = '''
- Operator slide-block (argument1 = the block, argument2 = the clear location), statement 5; adjacent (statement 7) is a
  static relation between locations, a block being adjacent to what its location is adjacent to (A-G1); clear is a
  maintained one-argument relation (statement 6).
- The goal is expanded over the blocks of the world file: every block is on the location with its {attr} (A-G3).'''


def sc_own_attr_first(t, name, sc_id, attr='color'):
    """Evaluation item: 'During look-ahead, first try moving a block onto a location of its own color, and try last
    moving a block off a location of its own color.' A one-step measure of progress (a location becomes or stops being
    matched, statement 11), used only to order the evaluations (World-Conventions L15-026)."""
    t.add(f'''
## ---- Search control {sc_id} [evaluation] (added, not taught; World-Conventions L15-026): evaluate first a slide onto a
## location of the block's own {attr}, and last a slide off one. Only the order of evaluation changes, not the evaluations.
sp {{{name}*elaborate*operator*evaluate-first*onto-own-{attr}
   (state <s> ^operator <op> +)
   (<op> ^task-operator true ^name slide-block ^argument1 <b> ^argument2 <d>)
   (<b> ^{attr} <v>)
   (<d> ^{attr} <v>)
-->
   (<op> ^evaluate-first true)
}}

sp {{{name}*elaborate*operator*evaluate-last*off-own-{attr}
   (state <s> ^operator <op> + ^world <w>)
   (<op> ^task-operator true ^name slide-block ^argument1 <b>)
   (<b> ^{attr} <v>)
   (<w> ^on <r>)
   (<r> ^argument1 <b> ^argument2 <l>)
   (<l> ^{attr} <v>)
-->
   (<op> ^evaluate-last true)
}}
''')


# Search-control items (tools/control.py) the sliding puzzles can translate: statement pattern -> rule writer.
CONTROL_SLIDING = [
    (re.compile(r'^during look-ahead, first try moving a block onto a location of its own colou?r, and try last moving a '
                r'block off a location of its own colou?r\.?$', re.I),
     lambda t, name, sc_id: sc_own_attr_first(t, name, sc_id, 'color')),
]


def sliding(name, world, default_world, title, attr, n, note, control='none'):
    t, objs = _task(name, world, title, (5, 6, 7, 9, 11), note, SLIDE_TRANS.format(attr=attr), default_world)
    step_move(t, 'slide-block', 'Slide', '')
    goal_all_matched(t, name, objs, attr)
    tag = C.translate(t, name, control, CONTROL_SLIDING)
    _finish(t, name, world, default_world, tag)


def maze(name, world, default_world, push_too=False, nums=(4, 5, 6, 7, 14)):
    trans = '''
- Operator block-step (argument1 = the blue block, argument2 = the clear location), statement 5; adjacent (statement 7)
  is a static relation between locations (A-G1); clear is a maintained one-argument relation (statement 6). The black
  blocks are walls only in that they stand on locations, which are then not clear.''' + ('''
- Statement 8 (push): operator push (argument1 = the block on the covered location, argument2 = the clear location),
  one proposal per direction, with step-1..4 static relations for "between" (A-G2). Occupied (statement 10) is expanded
  in place: the location below a blue block.''' if push_too else '') + '''
- The goal: a blue block is on a blue location.'''
    t, objs = _task(name, world, 'Pushing maze' if push_too else 'Simple maze', nums, 'a grid of locations; the blue block, black blocks',
                    trans, default_world, extra_static=steps if push_too else None)
    step_move(t, 'block-step', 'Step', '   (<b> ^color blue)\n')
    if push_too:
        push(t, '   (<q> ^color blue)')
    goal_block_on(t, name, [('blue', 'blue')], 'blue-matched')
    _finish(t, name, world, default_world)


def sokoban(name, world, default_world, nums=(5, 6, 7, 9, 10, 13)):
    trans = '''
- Operator move-block (argument1 = the blue block, argument2 = the clear location), statement 5; operator push-block
  (argument1 = the block on the covered location, argument2 = the clear location), statement 9, one proposal per
  direction with step-1..4 static relations for "between" (A-G2); the blue block is the pusher.
- adjacent (statement 7) is a static relation between locations (A-G1); clear is maintained (statement 6); covered
  (statement 10) is expanded in place (a location some block is on).
- The goal: a red block on a red location and a green block on a green location. "The solution has eight steps"
  (statement 11) is checked against the plans, not used.'''
    t, objs = _task(name, world, 'Sokoban', nums, 'a grid of locations; the blue block (the pusher), a red and a green block',
                    trans, default_world, extra_static=steps)
    step_move(t, 'move-block', 'Move', '   (<b> ^color blue)\n')
    push(t, '   (<q> ^color blue)', name='push-block')
    goal_block_on(t, name, [('red', 'red'), ('green', 'green')], 'red-green-matched')
    _finish(t, name, world, default_world)


# ---------------------------------------------------------------- Traveling salesman, knight's tour
def tour(name, world, default_world, title, nums, move_rel, goal_green, note, trans_move, op='tour-move'):
    """'... you can move the red block onto the clear location and move a clear available blue block onto the location
    that was below the red block.' Operator tour-move (argument1 = the red block, argument2 = the clear location). The
    clear available blue block is the top of the stack of blue blocks: there is only one, so the applications find it
    (A-G4). available and clear are maintained one-argument relations. The stack's bottom block is on nothing; moving it
    tests that (a negated condition in a look-ahead application, L11-003, Should; A-C2)."""
    from rosie_chess import available_concept
    trans = trans_move + '''
- available (not on a location) and clear are maintained one-argument relations; the blue blocks start in a stack, and the
  clear available blue block is its top, found by the applications (A-G4).
- covered (below an object) is expanded in place; the goal is expanded over the locations of the world file''' + (
        ''' and adds a red block on a location adjacent to a green location.''' if goal_green else '.')
    desc = _desc(f'{title} ({name})', nums, f'{default_world} ({note})', trans)
    objs, rels, _ = R.read_world(world)
    st = {'adjacent': adjacent(rels)} if move_rel == 'adjacent' else {}
    if move_rel == 'jumpable':
        from rosie_swap import knight_moves
        st['jumpable'] = knight_moves(rels)
    def concept(n, objs, rels):
        return clear_concept(n, objs, rels) if n == 'clear' else available_concept(objs, rels)
    t = R.RosieTask(name, desc, world, lambda i, a: f"{a['category']}-{i}", maintained=['clear', 'available'], concept=concept,
                    static_relations=st)
    tn = t.name
    t.add(t.t.propose(op, '''   (<objs> ^object <b> <d>)
   (<b> ^type block ^color red ^object-handle <bh>)
   (<d> ^type location ^object-handle <dh>)
''' + on('<b>', '<l1>', 'b') + '\n' + rel(move_rel, '<d>', '<l1>', 'd') + '\n' + clear('<d>', 'd'), ['<b>', '<d>']))
    base = '''   (<w> ^anchored-world true ^objects <objs>)
   (<objs> ^object <b> <d> <u>)
   (<b> ^object-handle <bh>)
   (<d> ^object-handle <dh>)
   (<u> ^type block ^color blue)
   (<w> ^on <r> ^below <bl> ^clear <cd> <cu> ^available <au>)
   (<r> ^argument1 <b> ^argument2 <old>)
   (<bl> ^argument1 <old> ^argument2 <b>)
   (<cd> ^argument1 <d>)
   (<cu> ^argument1 <u>)
   (<au> ^argument1 <u>)'''
    from_block = base + '''
   (<w> ^on <ru> ^below <bu>)
   (<ru> ^argument1 <u> ^argument2 <x>)
   (<bu> ^argument1 <x> ^argument2 <u>)'''
    rhs_block = '''(<r> ^argument2 <old> - <d>)
   (<bl> ^argument1 <old> - <d>)
   (<ru> ^argument2 <x> - <old>)
   (<bu> ^argument1 <x> - <old>)
   (<w> ^clear <cd> - <nx> ^available <au> -)
   (<nx> ^argument1 <x>)'''
    from_nothing = base + '''
  -{(<w> ^on <ru>)
    (<ru> ^argument1 <u>)}'''
    rhs_nothing = '''(<r> ^argument2 <old> - <d>)
   (<bl> ^argument1 <old> - <d>)
   (<w> ^on <nr> ^below <nb> ^clear <cd> - ^available <au> -)
   (<nr> ^argument1 <u> ^argument2 <old>)
   (<nb> ^argument1 <old> ^argument2 <u>)'''
    write = '''
   (<pa> ^effect-applied true)
   (write |Move | <bh> | onto | <dh> |, leaving a blue block behind| (crlf))'''
    B._effect(t, op, ('<bh>', '<dh>'), from_block, rhs_block, write, guard_internal='blue-from-block')
    B._effect(t, op, ('<bh>', '<dh>'), from_nothing, rhs_nothing, write, guard_internal='blue-from-nothing')
    locs = [t.h[i] for i, a in sorted(objs.items()) if a['category'] == 'location']
    conds = '\n'.join(f'''   (<l-{h}> ^object-handle {h})
   (<w> ^below <bw-{h}>)
   (<bw-{h}> ^argument1 <l-{h}>)''' for h in locs)
    green = '''
   (<rb> ^type block ^color red)
   (<g> ^type location ^color green)
''' + on('<rb>', '<rl>', 'rb') + '\n' + rel('adjacent', '<g>', '<rl>', 'g') if goal_green else ''
    t.add(f'''
## Goal: all locations are covered{' and a red block is adjacent to a green location' if goal_green else ''}.
sp {{{tn}*elaborate*goal*covered
   (state <s> ^world <w>)
   (<w> ^objects <objs>)
   (<objs> ^object <t> {' '.join(f'<l-{h}>' for h in locs)}{' <rb> <g>' if goal_green else ''})
   (<t> ^type task)
{conds}{green}
-->
   (<t> ^goal-met true)
}}
''')
    _finish(t, name, world, default_world)
