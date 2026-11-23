"""Task definitions for the side-swapping dialogs (Rosie teaching data), world conventions (18 Nov 2026).
Each function writes one task's rules and loader; the folder's gen.py names the function and the world.

A block moves onto a location. Every legal move in these dialogs ends on a clear location, so the effect is the same
for every move statement: the block's on and below relations name the new location, the new location stops being clear
and the location the block left becomes clear. Each move statement is a separate proposal of the one operator move.
left-of, right-of and the knight's-move relations are static relations between locations, copied from the world file.
A block is "to the left/right of" something when the location it is on is (A-S1)."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rosie_gen as R, rosie_blocks as B
from rosie_tasks import _desc, _finish, clear_concept

MOVE_COND = '''   (<w> ^anchored-world true ^objects <objs>)
   (<objs> ^object <b> <d>)
   (<b> ^object-handle <bh>)
   (<d> ^object-handle <dh>)
   (<w> ^on <r> ^below <bl> ^clear <cd>)
   (<r> ^argument1 <b> ^argument2 <old>)
   (<bl> ^argument1 <old> ^argument2 <b>)
   (<cd> ^argument1 <d>)'''
MOVE_RHS = '''(<r> ^argument2 <old> - <d>)
   (<bl> ^argument1 <old> - <d>)
   (<w> ^clear <cd> - <nc>)
   (<nc> ^argument1 <old>)'''


def on(var_b, var_l, tag):
    return f'''   (<w> ^on <on-{tag}>)
   (<on-{tag}> ^argument1 {var_b} ^argument2 {var_l})'''


def rel(name, a, b, tag):
    return f'''   (<w> ^{name} <{name}-{tag}>)
   (<{name}-{tag}> ^argument1 {a} ^argument2 {b})'''


def clear(var, tag):
    return f'''   (<w> ^clear <clear-{tag}>)
   (<clear-{tag}> ^argument1 {var})'''


def propose_move(t, suffix, lhs, op='move'):
    """One move statement: lhs binds <b> (the block) and <d> (the clear location it moves onto)."""
    t.add(t.t.propose(f'{op}*{suffix}', f'''   (<objs> ^object <b> <d>)
   (<b> ^type block ^object-handle <bh>)
   (<d> ^type location ^object-handle <dh>)
{lhs}''', ['<b>', '<d>']))


def move_effect(t, op='move', verb='Move'):
    B._effect(t, op, ('<bh>', '<dh>'), MOVE_COND, MOVE_RHS, f'''
   (<pa> ^effect-applied true)
   (write |{verb} | <bh> | onto | <dh> (crlf))''')


def goal_same_color(t, name, objs):
    """'All the red blocks are on the red locations and all the blue blocks are on the blue locations', expanded over the
    blocks of the world file (A-S2)."""
    blocks = [(t.h[i], a['color']) for i, a in sorted(objs.items()) if a['category'] == 'block']
    conds = '\n'.join(f'''   (<b-{h}> ^object-handle {h})
   (<l-{h}> ^type location ^color {c})
{on(f'<b-{h}>', f'<l-{h}>', h)}''' for h, c in blocks)
    t.add(f'''
## Goal: every block is on a location of its own color.
sp {{{name}*elaborate*goal*colors-matched
   (state <s> ^world <w>)
   (<w> ^objects <objs>)
   (<objs> ^object <t> {' '.join(f'<b-{h}> <l-{h}>' for h, _ in blocks)})
   (<t> ^type task)
{conds}
-->
   (<t> ^goal-met true)
}}
''')


# ---------------------------------------------------------------- Frogs and toads
def frogs_toads(name, world, default_world, nums=(4, 5, 6, 7, 8, 10, 11, 15)):
    trans = '''
- Operator move (argument1 = the block, argument2 = the clear location it moves onto); four proposals, one per move
  statement (4, 7, 10, 11). A toad is a blue block, a frog a red block (statements 6, 8), expanded in place.
- clear is a maintained one-argument relation (statement 5). left-of and right-of are static relations between
  locations; a block is to the left/right of a location when the location it is on is (A-S1).
- The goal (statement 15) is expanded over the blocks of the world file: each block is on a location of its colour (A-S2).'''
    desc = _desc(f'Frogs and toads ({name})', nums, default_world + ' (five locations in a row; two toads, a clear location, two frogs)', trans)
    objs, rels, _ = R.read_world(world)
    t = R.RosieTask(name, desc, world, lambda i, a: f"{a['category']}-{i}", maintained=['clear'], concept=clear_concept,
                    static_relations={'left-of': rels.get('left-of', []), 'right-of': rels.get('right-of', [])})
    # 4: a clear location to the right of a toad: the toad moves onto it.
    propose_move(t, 'toad-step', '''   (<b> ^color blue)
''' + on('<b>', '<l1>', 'b') + '\n' + rel('right-of', '<d>', '<l1>', 'd') + '\n' + clear('<d>', 'd'))
    # 7: a clear location to the left of a frog: the frog moves onto it.
    propose_move(t, 'frog-step', '''   (<b> ^color red)
''' + on('<b>', '<l1>', 'b') + '\n' + rel('left-of', '<d>', '<l1>', 'd') + '\n' + clear('<d>', 'd'))
    # 10: a frog to the right of a toad, the toad to the right of a clear location: the frog moves onto it.
    propose_move(t, 'frog-jump', '''   (<b> ^color red)
   (<objs> ^object <o>)
   (<o> ^type block ^color blue)
''' + on('<b>', '<l1>', 'b') + '\n' + on('<o>', '<l2>', 'o') + '\n' + rel('right-of', '<l1>', '<l2>', 'bo') + '\n'
        + rel('right-of', '<l2>', '<d>', 'od') + '\n' + clear('<d>', 'd'))
    # 11: a toad to the left of a frog, the frog to the left of a clear location: the toad moves onto it.
    propose_move(t, 'toad-jump', '''   (<b> ^color blue)
   (<objs> ^object <o>)
   (<o> ^type block ^color red)
''' + on('<b>', '<l1>', 'b') + '\n' + on('<o>', '<l2>', 'o') + '\n' + rel('left-of', '<l1>', '<l2>', 'bo') + '\n'
        + rel('left-of', '<l2>', '<d>', 'od') + '\n' + clear('<d>', 'd'))
    move_effect(t)
    goal_same_color(t, name, objs)
    _finish(t, name, world, default_world)


# ---------------------------------------------------------------- Eight men on a raft
def eight_men(name, world, default_world, nums=(4, 5, 6, 7, 9, 10, 15)):
    trans = '''
- Operator move (argument1 = the peg, argument2 = the clear location it moves onto); four proposals, one per move
  statement (4, 7, 9, 10). Every block is a peg (statement 6). Blue pegs step right and jump right over any peg; red pegs
  step left and jump left over any peg.
- clear is a maintained one-argument relation (statement 5); left-of and right-of are static relations between locations,
  and a peg is to the left/right of a location when the location it is on is (A-S1).
- The goal (statement 15) is expanded over the blocks of the world file (A-S2). "The solution has twenty-four steps"
  (statement 11) is checked against the plans, not used.'''
    desc = _desc(f'Eight men on a raft ({name})', nums, default_world + ' (nine locations in a row; four blue pegs, a clear location, four red pegs)', trans)
    objs, rels, _ = R.read_world(world)
    t = R.RosieTask(name, desc, world, lambda i, a: f"{a['category']}-{i}", maintained=['clear'], concept=clear_concept,
                    static_relations={'left-of': rels.get('left-of', []), 'right-of': rels.get('right-of', [])})
    propose_move(t, 'blue-step', '   (<b> ^color blue)\n' + on('<b>', '<l1>', 'b') + '\n' + rel('right-of', '<d>', '<l1>', 'd') + '\n' + clear('<d>', 'd'))
    propose_move(t, 'red-step', '   (<b> ^color red)\n' + on('<b>', '<l1>', 'b') + '\n' + rel('left-of', '<d>', '<l1>', 'd') + '\n' + clear('<d>', 'd'))
    propose_move(t, 'red-jump', '''   (<b> ^color red)
   (<objs> ^object <o>)
   (<o> ^type block)
''' + on('<b>', '<l1>', 'b') + '\n' + on('<o>', '<l2>', 'o') + '\n' + rel('right-of', '<l1>', '<l2>', 'bo') + '\n'
        + rel('right-of', '<l2>', '<d>', 'od') + '\n' + clear('<d>', 'd'))
    propose_move(t, 'blue-jump', '''   (<b> ^color blue)
   (<objs> ^object <o>)
   (<o> ^type block)
''' + on('<b>', '<l1>', 'b') + '\n' + on('<o>', '<l2>', 'o') + '\n' + rel('left-of', '<l1>', '<l2>', 'bo') + '\n'
        + rel('left-of', '<l2>', '<d>', 'od') + '\n' + clear('<d>', 'd'))
    move_effect(t)
    goal_same_color(t, name, objs)
    _finish(t, name, world, default_world)


# ---------------------------------------------------------------- Knight swapping (3x3 corners, 4x4 sides)
def knight_moves(rels):
    """'If an object that is alongside a block is diagonal with a location that is not next to the block then the location
    is jumpable by the block' (statement 6), computed from the world file's alongside, diagonal-with and near relations
    between locations, with the block standing for the location it is on (A-S1): jumpable(L, F) for every location F a
    block could stand on. A static relation; whether a block stands on F is tested in the proposal (A-S3)."""
    alongside, diagonal, near = set(rels.get('alongside', [])), set(rels.get('diagonal-with', [])), set(rels.get('near', []))
    locs = {a for p in alongside | diagonal | near for a in p}
    out = []
    for f in sorted(locs):
        for l in sorted(locs):
            if l != f and (l, f) not in near and (f, l) not in near and any((o, f) in alongside and (o, l) in diagonal for o in locs):
                out.append((l, f))
    return out


def knights(name, world, default_world, nums=(4, 5, 6, 11), title='Knight swapping'):
    trans = '''
- Operator move (argument1 = the block, argument2 = the clear location it moves onto), statement 4.
- jumpable (statement 6) is a static relation jumpable(L, F) between locations, computed from the world file's alongside,
  diagonal-with and near relations with the block standing for the location F it is on (A-S1, A-S3): the knight's move.
- clear is a maintained one-argument relation (statement 5).
- The goal (statement 11) is expanded over the blocks of the world file (A-S2). "The solution has four steps" (statement 7)
  is checked against the plans, not used.'''
    desc = _desc(f'{title} ({name})', nums, default_world, trans)
    objs, rels, _ = R.read_world(world)
    t = R.RosieTask(name, desc, world, lambda i, a: f"{a['category']}-{i}", maintained=['clear'], concept=clear_concept,
                    static_relations={'jumpable': knight_moves(rels)})
    propose_move(t, 'jump', on('<b>', '<l1>', 'b') + '\n' + rel('jumpable', '<d>', '<l1>', 'd') + '\n' + clear('<d>', 'd'))
    move_effect(t)
    goal_same_color(t, name, objs)
    _finish(t, name, world, default_world)
