"""Task definitions for the block-puzzle dialogs (Rosie teaching data). Each function writes one task's rules and loader;
the folder's gen.py names the function and the world. The statements quoted in each rules file are read from the folder's
script.txt, so the header always shows the instructor's words.

usage from a task folder:  python3 gen.py [WORLD]   (WORLD: another example state, for the state checks)"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rosie_gen as R, rosie_blocks as B

def _statements(nums):
    lines = [l.strip() for l in open('script.txt').read().splitlines() if l.strip()]
    return '\n'.join(f'##  {n:2d}. {lines[n - 1]}' for n in nums)

def _desc(title, nums, world_note, translation):
    return (f'## {title}, generated from the Rosie teaching script (english-input.txt) under the world conventions.\n##\n'
            f'## Instructor statements used (numbers as in english-input.txt):\n{_statements(nums)}\n'
            f'## World: {world_note}\n##\n## Translation (tools/rosie-language.md gives the general reading; the assumption '
            f'ledger is in README.md):\n' + '\n'.join('##   ' + l for l in translation.strip().splitlines()) + '\n')

def _finish(t, name, world, default_world):
    out = f'{name}-rules.soar' if world == default_world else f'{name}-rules-{world[:-6]}.soar'
    t.write(out)
    open(f'{name}.soar', 'w').write(R.loader(f'{name}.soar', f'{name}-rules.soar', 5))
    print('wrote', out)

def clear_concept(name, objs, rels):
    """'If a location is not below an object then it is clear', for every object (A-H1)."""
    assert name == 'clear'
    below_first = {a for a, b in rels.get('below', [])}
    return {i for i in objs if i not in below_first}

# ---------------------------------------------------------------- Tower of Hanoi (3, 4, 5 blocks)
def hanoi(name, world, default_world, nums=(4, 5, 6, 8)):
    desc = _desc(f'Tower of Hanoi ({name})', nums, default_world + ' (two green locations and a blue one; the blocks stacked '
                 'by volume on a green location)', '''
- Operator move (argument1 = the block, argument2 = the object it is moved onto).
- clear tests absence and decides legality, so it is a maintained one-argument relation (W-SPEC v6 section 3); it
  applies to blocks as well as locations (A-H1).
- larger than is expanded in place: the destination's volume is more than the block's (A-H2).
- The goal is ^goal-met true on the task object when two different green locations are clear (A-H3).''')
    t = R.RosieTask(name, desc, world, lambda i, a: f"{a['category']}-{i}", maintained=['clear'], concept=clear_concept)
    B.move_clear(t, 'move', larger=True)
    t.add(f'''
## Goal: two different green locations are clear.
sp {{{name}*elaborate*goal*two-clear-green-locations
   (state <s> ^world <w>)
   (<w> ^objects <objs> ^clear <c1> <c2>)
   (<objs> ^object <t> <l1> <l2>)
   (<t> ^type task)
   (<l1> ^type location ^color green ^object-handle <h1>)
   (<l2> ^type location ^color green ^object-handle {{ <> <h1> <h2> }})
   (<c1> ^argument1 <l1>)
   (<c2> ^argument1 <l2>)
-->
   (<t> ^goal-met true)
}}
''')
    _finish(t, name, world, default_world)

# ---------------------------------------------------------------- Blocks world (two colorings)
def blocks_world(name, world, default_world, bottom, top_on, top_below, nums=(4, 5, 7)):
    """Goal: 'a <top_on> block is on a <bottom> block and the <top_on> block is below a <top_below> block'."""
    desc = _desc(f'Blocks world ({name})', nums, default_world + ' (three locations; three colored blocks in one stack)', f'''
- Operator move (argument1 = the block, argument2 = the object it is moved onto).
- clear is a maintained one-argument relation, for blocks and locations (A-H1).
- The goal is ^goal-met true on the task object when some {top_on} block is on some {bottom} block and the same {top_on}
  block is below some {top_below} block.''')
    t = R.RosieTask(name, desc, world, lambda i, a: f"{a['category']}-{i}", maintained=['clear'], concept=clear_concept)
    B.move_clear(t, 'move', larger=False)
    t.add(f'''
## Goal: a {top_on} block is on a {bottom} block and the {top_on} block is below a {top_below} block.
sp {{{name}*elaborate*goal*stack
   (state <s> ^world <w>)
   (<w> ^objects <objs> ^on <r1> ^below <r2>)
   (<objs> ^object <t> <a> <b> <c>)
   (<t> ^type task)
   (<a> ^type block ^color {top_on})
   (<b> ^type block ^color {bottom})
   (<c> ^type block ^color {top_below})
   (<r1> ^argument1 <a> ^argument2 <b>)
   (<r2> ^argument1 <a> ^argument2 <c>)
-->
   (<t> ^goal-met true)
}}
''')
    _finish(t, name, world, default_world)

# ---------------------------------------------------------------- Sorting
def sorting(name, world, default_world, nums=(4, 6)):
    desc = _desc('Sorting', nums, default_world + ' (a red, a green and a blue location; two blocks of each color)', '''
- Operator move (argument1 = the block, argument2 = the location). Any block can move to any location other than the
  one it is on (A-S1).
- The goal ("all the red blocks are on a red location and ...") is expanded over the blocks of the world file: each block
  is on a location of its own color (A-S2). The test is positive.''')
    t = R.RosieTask(name, desc, world, lambda i, a: f"{a['color']}-{a['category']}-{i}")
    B.move_block(t, 'move')
    blocks = [(t.h[i], a['color']) for i, a in sorted(t.objs.items()) if a['category'] == 'block']
    conds = '\n'.join(f'''   (<b-{h}> ^object-handle {h})
   (<l-{h}> ^type location ^color {c})
   (<w> ^on <on-{h}>)
   (<on-{h}> ^argument1 <b-{h}> ^argument2 <l-{h}>)''' for h, c in blocks)
    objs = ' '.join(f'<b-{h}> <l-{h}>' for h, _ in blocks)
    t.add(f'''
## Goal: every block is on a location of its own color.
sp {{{name}*elaborate*goal*sorted
   (state <s> ^world <w>)
   (<w> ^objects <objs>)
   (<objs> ^object <t> {objs})
   (<t> ^type task)
{conds}
-->
   (<t> ^goal-met true)
}}
''')
    _finish(t, name, world, default_world)

# ---------------------------------------------------------------- Stacking frogs (three variants)
def _block_count(i, a, rels):
    return {'block-count': sum(1 for b, l in rels.get('on', []) if l == i)} if a['category'] == 'location' else {}

def _apart(objs):
    """apart-k(L, C): locations on the same row whose x differs by k, read so that adjacent locations are 1 apart (A-F2:
    fixed by the instructor's answer to Rosie's instance-count question)."""
    locs = [(i, a) for i, a in objs.items() if a['category'] == 'location']
    rels = {}
    for i, a in locs:
        for j, b in locs:
            if i != j and a['y'] == b['y']:
                rels.setdefault(f"apart-{abs(a['x'] - b['x'])}", []).append((i, j))
    return rels

def frogs(name, world, default_world, nums, variant):
    """variant: 'three-clear' (stacking frogs), 'red-location' (king), 'lazy' (accessible covered location; three clear)."""
    goal_clear = variant in ('three-clear', 'lazy')
    acc = variant == 'lazy'
    trans = '''
- Operator move (argument1 = the covered location C whose blocks move, argument2 = the location L they move onto). All the
  blocks on C move together onto L (A-F1).
- "the number of the locations between L and C" is read so that adjacent locations count 1 (A-F2): the reading that
  gives the instructor's answer to Rosie's question on the number of instances. It is a static relation apart-k,
  computed from the locations' x and y and declared ^copy-relation.
- "the number of the blocks that are on C" is the maintained attribute ^block-count of each location; covered (below an
  object) holds exactly when the count is at least 1, so it needs no test of its own.'''
    if acc: trans += '\n- accessible ("a location that is not below a red block") is a maintained one-argument relation. No move changes it:\n  a moving pile is never on an inaccessible location.'
    if goal_clear: trans += '\n- clear is a maintained one-argument relation. The goal is three different clear locations.'
    else: trans += '\n- The goal ("all the blocks are on a red location") is expanded over the blocks of the world file (A-F3).'
    desc = _desc(f'Stacking frogs ({name})', nums, default_world + ' (four locations in a row, one block on each)', trans)
    objs, rels, _ = R.read_world(world)
    maintained = (['clear'] if goal_clear else []) + (['accessible'] if acc else [])
    def concept(n, objs, rels):
        if n == 'clear': return clear_concept(n, objs, rels)
        if n == 'accessible':
            red = {i for i, a in objs.items() if a['category'] == 'block' and a.get('color') == 'red'}
            under_red = {l for l, b in rels.get('below', []) if b in red}
            return {i for i, a in objs.items() if a['category'] == 'location' and i not in under_red}
    desc += ('## Search settings: ^iterative-step tie-impasse, chosen by the P6 probe (probe_settings.py, 16 Nov 2026, library\n'
             '## v2.34, seeds 1-3): same 3-move plans as operator depth with fewer decisions (probe.json).\n')
    t = R.RosieTask(name, desc, world, lambda i, a: f"{a['category']}-{i}", maintained=maintained, concept=concept,
                    extra_props=_block_count, static_relations=_apart(objs), extra_flags=' ^iterative-step tie-impasse')
    nblocks = sum(1 for a in objs.values() if a['category'] == 'block')
    B.move_pile(t, 'move', k_max=nblocks, clear=goal_clear, accessible=acc)
    if goal_clear:
        t.add(f'''
## Goal: three different clear locations.
sp {{{name}*elaborate*goal*three-clear
   (state <s> ^world <w>)
   (<w> ^objects <objs> ^clear <c1> <c2> <c3>)
   (<objs> ^object <t> <l1> <l2> <l3>)
   (<t> ^type task)
   (<l1> ^type location ^object-handle <h1>)
   (<l2> ^type location ^object-handle {{ <> <h1> <h2> }})
   (<l3> ^type location ^object-handle {{ <> <h1> <> <h2> <h3> }})
   (<c1> ^argument1 <l1>)
   (<c2> ^argument1 <l2>)
   (<c3> ^argument1 <l3>)
-->
   (<t> ^goal-met true)
}}
''')
    else:
        blocks = [t.h[i] for i, a in sorted(objs.items()) if a['category'] == 'block']
        conds = '\n'.join(f'''   (<b-{h}> ^object-handle {h})
   (<l-{h}> ^type location ^color red)
   (<w> ^on <on-{h}>)
   (<on-{h}> ^argument1 <b-{h}> ^argument2 <l-{h}>)''' for h in blocks)
        t.add(f'''
## Goal: all the blocks are on a red location.
sp {{{name}*elaborate*goal*on-red-location
   (state <s> ^world <w>)
   (<w> ^objects <objs>)
   (<objs> ^object <t> {' '.join(f'<b-{h}> <l-{h}>' for h in blocks)})
   (<t> ^type task)
{conds}
-->
   (<t> ^goal-met true)
}}
''')
    _finish(t, name, world, default_world)
