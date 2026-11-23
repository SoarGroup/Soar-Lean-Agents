"""Rosie teaching dialogs translated to standard Soar (Soar-Conventions.xlsx), not the world conventions (19 Nov 2026).

What changes against the world-convention agents (rosie_gen.py and the family modules):
  - state: (<s> ^object <x>) with (<x> ^name <handle> ^type block|location ...); binary relations are attributes of the
    first object, pointing at the second ((<b> ^on <l>)); no ^world, no relation objects, no ^objects.object;
  - concepts whose test needs a negation (clear) are maintained object attributes (^clear true), set at initialization
    and changed by the operators (L3-031): a negated test matches half-built look-ahead copies and gives false results;
  - the goal is a ^desired structure on the top state (L3-024), recognized by a rule that adds (<s> ^success <d>);
    a losing state adds (<s> ^failure <d>) (L3-025); the top state halts on success (the run stops there too);
  - operators are proposed exactly when their preconditions hold (L3-038), with their arguments as named attributes;
    the application changes the state directly, in the top state and in look-ahead copies alike;
  - search: the classic default selection space (rosie-teaching/default/selection, the same rules as the Families
    soar-conv programs), with ^default-state-copy, ^default-operator-copy and ^two-level-attributes object;
  - a monitoring rule prints 'ACTION: <name> <arg1> <arg2>' when the top state selects a task operator, which is how
    run_plain.py records the plan (there is no output-link).
Handles are those of the world-convention agents, so tools/check_plan.py and check_moves.py replay the plans unchanged."""
import os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rosie_gen as R


def statements(nums):
    lines = [l.strip() for l in open('script.txt').read().splitlines() if l.strip()]
    return '\n'.join(f'#  {n:2d}. {lines[n - 1]}' for n in nums)


class Plain:
    """name: task (state) name; world: initial world file; handle(id, attrs) -> handle."""
    def __init__(s, name, title, world, nums, world_note, translation, handle=lambda i, a: f"{a['category']}-{i}"):
        s.name, s.title = name, title
        s.objs, s.rels, s.sets = R.read_world(world)
        s.h = {i: handle(i, a) for i, a in s.objs.items()}
        s.header = (f'# {title} ({name}): standard Soar conventions (Soar-Conventions.xlsx), generated from the Rosie teaching\n'
                    f'# script (english-input.txt) by tools/rosie_plain.py.\n#\n# Instructor statements used (numbers as in '
                    f'english-input.txt):\n{statements(nums)}\n# World: {world} ({world_note})\n#\n# Translation:\n'
                    + '\n'.join('#   ' + l for l in translation.strip().splitlines()) + '\n')
        s.extra_attrs = {}        # id -> list of (attr, value) added to the object at initialization
        s.static = []             # (id1, attr, id2): static binary relations as attributes
        s.desired = []            # lines of the ^desired structure: (attr, value) on <d>, or raw text
        s.rules = []
        s.dont_copy = []

    # ------------------------------------------------------------------ pieces
    def add(s, text): s.rules.append(text.strip('\n'))

    def init_rules(s):
        n = s.name
        lines = [f'   (<s> ^name {n} ^desired <d>)']
        for i, a in sorted(s.objs.items()):
            attrs = [f'^name {s.h[i]}', f"^type {a['category']}"] + [f'^{k} {v}' for k, v in a.items() if k != 'category']
            attrs += [f'^{k} {v}' for k, v in s.extra_attrs.get(i, [])]
            lines.append(f'   (<s> ^object <x{i}>)')
            lines.append(f"   (<x{i}> {' '.join(attrs)})")
        for a, b in s.rels.get('on', []):
            lines.append(f'   (<x{a}> ^on <x{b}>)')
        for a, att, b in s.static:
            lines.append(f'   (<x{a}> ^{att} <x{b}>)')
        for d in s.desired:
            lines.append(d if d.startswith('   (') else f'   (<d> {d})')
        body = '\n'.join(lines)
        return f'''
# Propose initialize-{n} in the top state before it has a name.
sp {{{n}*propose*initialize-{n}
   (state <s> ^superstate nil)
  -(<s> ^name)
-->
   (<s> ^operator <o> +)
   (<o> ^name initialize-{n})
}}

# Apply initialize-{n}: the objects and relations of the world file, and the desired state.
sp {{{n}*apply*initialize-{n}
   (state <s> ^operator <o>)
   (<o> ^name initialize-{n})
-->
{body}
}}

# Elaborate the problem space: the look-ahead copies the objects (two levels) and the operators.
sp {{{n}*elaborate*problem-space
   (state <s> ^name {n})
-->
   (<s> ^problem-space <p>)
   (<p> ^name {n} ^default-state-copy yes ^default-operator-copy yes ^two-level-attributes object)
}}

# Halt when the top state reaches the desired state.
sp {{{n}*halt*success
   (state <s> ^superstate nil ^name {n} ^desired <d> ^success <d>)
-->
   (write (crlf) |The problem has been solved.|)
   (halt)
}}

# Halt when the top state is a losing state.
sp {{{n}*halt*failure
   (state <s> ^superstate nil ^name {n} ^desired <d> ^failure <d>)
-->
   (write (crlf) |The task has failed.|)
   (halt)
}}'''

    def monitor(s, op, a1, a2):
        n = s.name
        return f'''
# Monitor: print the task operator selected in the top state (the plan).
sp {{{n}*monitor*{op}
   (state <s> ^superstate nil ^name {n} ^operator <o>)
   (<o> ^name {op} ^{a1}.name <h1> ^{a2}.name <h2>)
-->
   (write (crlf) |ACTION: {op} | <h1> | | <h2>)
}}'''

    def write(s, out=None):
        out = out or f'{s.name}-rules.soar'
        open(out, 'w').write(s.header + s.init_rules() + '\n\n' + '\n\n'.join(s.rules) + '\n')
        return out

    def loader(s, rules_file, depth):
        up = '/'.join(['..'] * depth)
        return (f'# Loads the classic default selection rules (rosie-teaching/default), then the task rules.\n'
                f'pushd {up}/default\nsource selection.soar\npopd\nsource {rules_file}\n')


def finish(p, world, default_world):
    """Writes soar-conv/<name>-rules.soar (or -rules-<world>.soar for an example state) and the loader."""
    os.makedirs('soar-conv', exist_ok=True)
    base = f'{p.name}-rules.soar' if world == default_world else f'{p.name}-rules-{os.path.basename(world)[:-6]}.soar'
    p.write(os.path.join('soar-conv', base))
    open(os.path.join('soar-conv', f'{p.name}.soar'), 'w').write(p.loader(f'{p.name}-rules.soar', 3))
    print('wrote soar-conv/' + base)


# ====================================================================== shared rules for the block puzzles
def init_clear(p):
    """clear ("If a location is not below an object then it is clear"; blocks as well, A-H1) is a maintained object
    attribute (^clear true): set at initialization for every object with nothing on it, and changed by the operators
    (L3-031: a derived elaboration would need a negation, which matches half-built look-ahead copies)."""
    on_targets = {b for a, b in p.rels.get('on', [])}
    for i in p.objs:
        if i not in on_targets: p.extra_attrs.setdefault(i, []).append(('clear', 'true'))


def move_clear(p, larger=False):
    """'You can move a clear block onto a clear object [that is larger than the block]'."""
    n = p.name
    lg = '\n   (<b> ^volume <vb>)\n   (<dest> ^volume > <vb>)' if larger else ''
    init_clear(p)
    p.add(f'''
# Propose move: a clear block onto a clear object{' that is larger than the block (volume, statement on larger)' if larger else ''}.
sp {{{n}*propose*move
   (state <s> ^name {n} ^object <b> {{ <dest> <> <b> }})
   (<b> ^type block ^clear true)
   (<dest> ^clear true){lg}
-->
   (<s> ^operator <o> +)
   (<o> ^name move ^block <b> ^destination <dest>)
}}

# Apply move: the block is on the destination instead of what it was on; what it was on is clear, the destination is not.
sp {{{n}*apply*move
   (state <s> ^name {n} ^operator <o>)
   (<o> ^name move ^block <b> ^destination <dest>)
   (<b> ^on <old>)
   (<dest> ^clear true)
-->
   (<b> ^on <old> - <dest>)
   (<old> ^clear true)
   (<dest> ^clear true -)
}}''')
    p.add(p.monitor('move', 'block', 'destination'))


# ---------------------------------------------------------------- Tower of Hanoi
def hanoi(name, world, default_world, nums):
    p = Plain(name, 'Tower of Hanoi', world, nums, 'two green locations and a blue one; the blocks stacked by volume', '''
- Operator move (^block, ^destination). clear is an i-supported state attribute, for blocks and locations (A-H1).
- larger than: the destination's volume is more than the block's (A-H2).
- Desired: (<d> ^clear-locations 2 ^location-color green): two different green locations are clear (A-H3).''')
    p.desired = ['^clear-locations 2 ^location-color green']
    move_clear(p, larger=True)
    p.add(f'''
# Desired state: two different clear locations of the desired color.
sp {{{name}*elaborate*goal*two-clear-locations
   (state <s> ^name {name} ^desired <d> ^object <l1> {{ <l2> <> <l1> }})
   (<d> ^clear-locations 2 ^location-color <c>)
   (<l1> ^type location ^color <c> ^clear true)
   (<l2> ^type location ^color <c> ^clear true)
-->
   (<s> ^success <d>)
}}''')
    finish(p, world, default_world)


# ---------------------------------------------------------------- Blocks world
def blocks_world(name, world, default_world, bottom, top_on, top_below, nums):
    p = Plain(name, 'Blocks world', world, nums, 'three locations; three colored blocks in one stack', f'''
- Operator move (^block, ^destination). clear is an i-supported state attribute, for blocks and locations (A-H1).
- "X is below Y" is read as Y is on X (the world files' below relation is the inverse of on).
- Desired: (<d> ^top-color {top_on} ^bottom-color {bottom} ^cover-color {top_below}): a {top_on} block is on a {bottom} block and
  a {top_below} block is on that {top_on} block.''')
    p.desired = [f'^top-color {top_on} ^bottom-color {bottom} ^cover-color {top_below}']
    move_clear(p)
    p.add(f'''
# Desired state: a block of the top color on a block of the bottom color, with a block of the cover color on it.
sp {{{name}*elaborate*goal*stack
   (state <s> ^name {name} ^desired <d> ^object <a> <b> <c>)
   (<d> ^top-color <tc> ^bottom-color <bc> ^cover-color <cc>)
   (<a> ^type block ^color <tc> ^on <b>)
   (<b> ^type block ^color <bc>)
   (<c> ^type block ^color <cc> ^on <a>)
-->
   (<s> ^success <d>)
}}''')
    finish(p, world, default_world)


# ---------------------------------------------------------------- Sorting
def sorting(name, world, default_world, nums):
    p = Plain(name, 'Sorting', world, nums, 'a red, a green and a blue location; two blocks of each color', """
- Operator move (^block, ^destination): any block onto any location other than the one it is on (A-S1).
- Desired: "all the red blocks are on a red location and ..." is expanded over the blocks of the world file (A-S2): one
  ^block-on entry (^block-name, ^location-color) per block. The goal holds when no entry lacks a matching block and
  location; a half-built look-ahead copy can only fail this test, never pass it.""",
              handle=lambda i, a: f"{a['color']}-{a['category']}-{i}")
    for i, a in sorted(p.objs.items()):
        if a['category'] == 'block':
            p.desired += [f'   (<d> ^block-on <e{i}>)', f"   (<e{i}> ^block-name {p.h[i]} ^location-color {a['color']})"]
    p.add(f"""
# Propose move: a block onto a location other than the one it is on.
sp {{{name}*propose*move
   (state <s> ^name {name} ^object <b> <l>)
   (<b> ^type block ^on <> <l>)
   (<l> ^type location)
-->
   (<s> ^operator <o> +)
   (<o> ^name move ^block <b> ^destination <l>)
}}

# Apply move: the block is on the destination instead of what it was on.
sp {{{name}*apply*move
   (state <s> ^name {name} ^operator <o>)
   (<o> ^name move ^block <b> ^destination <dest>)
   (<b> ^on <old>)
-->
   (<b> ^on <old> - <dest>)
}}""")
    p.add(p.monitor('move', 'block', 'destination'))
    p.add(block_on_goal(p))
    finish(p, world, default_world)


def block_on_goal(p):
    return f"""
# Desired state: every ^block-on entry holds (the named block is on a location of the named color).
sp {{{p.name}*elaborate*goal*blocks-on
   (state <s> ^name {p.name} ^desired <d>)
   (<d> ^block-on <any>)
  -{{(<d> ^block-on <e>)
    (<e> ^block-name <bn> ^location-color <lc>)
   -{{(<s> ^object <b> <l>)
     (<b> ^name <bn> ^on <l>)
     (<l> ^type location ^color <lc>)}}}}
-->
   (<s> ^success <d>)
}}"""


# ---------------------------------------------------------------- Stacking frogs
def frogs(name, world, default_world, nums, variant):
    """variant: 'three-clear' (stacking frogs), 'red-location' (king), 'lazy' (accessible covered location; three clear)."""
    goal_clear, acc = variant in ('three-clear', 'lazy'), variant == 'lazy'
    trans = """
- Operator move (^from = the covered location C, ^to = the location L): all the blocks on C move together onto L (A-F1).
- "the number of the locations between L and C" counts adjacent locations as 1 (A-F2); it is a static attribute
  (<l> ^apart-k <c>) set at initialization from the locations' x and y.
- "the number of the blocks that are on C" is the attribute ^block-count of each location, set at initialization and
  changed by move (Soar cannot count matches in a condition). C is covered exactly when its count is at least 1."""
    if acc: trans += """
- accessible ("a location that is not below a red block") is the object attribute ^accessible true, set at
  initialization. No move changes it: a moving pile never lands on an inaccessible location, and the red block's pile
  never moves."""
    if goal_clear: trans += """
- clear is the maintained object attribute ^clear true (L3-031). Desired: (<d> ^clear-locations 3)."""
    else: trans += """
- Desired: "all the blocks are on a red location" is expanded over the blocks of the world file (A-F3), as ^block-on
  entries (^block-name, ^location-color red)."""
    p = Plain(name, 'Stacking frogs', world, nums, 'four locations in a row, one block on each', trans)
    locs = [(i, a) for i, a in p.objs.items() if a['category'] == 'location']
    red = {i for i, a in p.objs.items() if a['category'] == 'block' and a.get('color') == 'red'}
    for i, a in locs:
        cnt = sum(1 for b, l in p.rels.get('on', []) if l == i)
        p.extra_attrs[i] = [('block-count', cnt)]
        if goal_clear and cnt == 0: p.extra_attrs[i].append(('clear', 'true'))
        if acc and not any(l == i and b in red for b, l in p.rels.get('on', [])): p.extra_attrs[i].append(('accessible', 'true'))
        for j, b in locs:
            if i != j and a['y'] == b['y']:
                p.static.append((i, f"apart-{abs(a['x'] - b['x'])}", j))
    nblocks = sum(1 for a in p.objs.values() if a['category'] == 'block')
    if goal_clear: p.desired = ['^clear-locations 3']
    else:
        for i, a in sorted(p.objs.items()):
            if a['category'] == 'block':
                p.desired += [f'   (<d> ^block-on <e{i}>)', f'   (<e{i}> ^block-name {p.h[i]} ^location-color red)']
    accc = ' ^accessible true' if acc else ''
    for k in range(1, nblocks + 1):
        p.add(f"""
# Propose move with {k} block(s) on the covered location: the destination is {k} location(s) away.
sp {{{name}*propose*move*{k}
   (state <s> ^name {name} ^object <c> <l>)
   (<c> ^type location ^block-count {k}{accc})
   (<l> ^type location ^apart-{k} <c>)
-->
   (<s> ^operator <o> +)
   (<o> ^name move ^from <c> ^to <l>)
}}""")
    clr_c = '\n   (<c> ^clear true)' if goal_clear else ''
    p.add(f"""
# Apply move: every block on the covered location is now on the destination.
sp {{{name}*apply*move*blocks
   (state <s> ^name {name} ^operator <o> ^object <b>)
   (<o> ^name move ^from <c> ^to <l>)
   (<b> ^type block ^on <c>)
-->
   (<b> ^on <c> - <l>)
}}

# Apply move: the destination's count grows by the covered location's count, which becomes 0.
sp {{{name}*apply*move*counts
   (state <s> ^name {name} ^operator <o>)
   (<o> ^name move ^from <c> ^to <l>)
   (<c> ^block-count {{ <k> > 0 }})
   (<l> ^block-count <m>)
-->
   (<c> ^block-count <k> - 0){clr_c}
   (<l> ^block-count <m> - (+ <m> <k>))
}}""")
    if goal_clear:
        p.add(f"""
# Apply move: a clear destination is no longer clear.
sp {{{name}*apply*move*destination-not-clear
   (state <s> ^name {name} ^operator <o>)
   (<o> ^name move ^to <l>)
   (<l> ^clear true)
-->
   (<l> ^clear true -)
}}""")
    p.add(p.monitor('move', 'from', 'to'))
    if goal_clear:
        p.add(f"""
# Desired state: three different clear locations.
sp {{{name}*elaborate*goal*three-clear
   (state <s> ^name {name} ^desired <d> ^object <l1> {{ <l2> <> <l1> }} {{ <l3> <> <l1> <> <l2> }})
   (<d> ^clear-locations 3)
   (<l1> ^type location ^clear true)
   (<l2> ^type location ^clear true)
   (<l3> ^type location ^clear true)
-->
   (<s> ^success <d>)
}}""")
    else:
        p.add(block_on_goal(p))
    finish(p, world, default_world)
