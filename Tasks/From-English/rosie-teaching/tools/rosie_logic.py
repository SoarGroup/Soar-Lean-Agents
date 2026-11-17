"""Logic-puzzle dialogs (Rosie teaching data), world conventions: four-map-coloring, jigsawdoku, kakuro, kenken, kenken2,
killer-sudoku, logi-five, shuffle, sudoku, sujiko, suko, survo.

Shared readings (tools/rosie-language.md):
  - "You can write a number that is between one and N onto an empty location": operator write, argument1 = the location,
    argument2 = a number object (number-1 .. number-N, ^number k; operator arguments are objects under the conventions).
    Its effect is ^value k on the location.
  - empty ("the value of a location is absent") tests absence and decides legality: a maintained one-argument relation,
    removed by write. filled ("the value of a location is more than zero") is expanded in place.
  - "The goal is that all locations are filled": expanded over the locations of the world file.
  - Losing conditions mark the state with ^failure (look-ahead returns a failure):
      same(attr): two different locations with the same attr and the same value;
      near: a location and an object next to it (the world's near relation) with the same value;
      sums: "if the locations in a G are filled and the sum of the values of the G is not T": one group object per G of the
            world file (type group, static member relation), a derived ^sum once every member has a value, and a failure
            when the sum differs from T (a constant ^target-value, or the value of the target object named by sum-target).
  - "The solution has N steps.": checked against the plans, not used."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rosie_gen as R
from rosie_tasks import _desc, _finish

SKIP = ('Load ', 'Ok.', 'Done.', 'No.')

def auto_nums():
    lines = [l.strip() for l in open('script.txt').read().splitlines() if l.strip()]
    return [i for i, l in enumerate(lines, 1) if not l.startswith(SKIP)]

def handle(i, a):
    if a['category'] == 'location': return f"loc-{a['row']}-{a['column']}"
    return f'block-{i}'

def same_rule(name, attr=None, color=None, tag=None):
    """Two different locations [both of color] [with the same attr] and the same value."""
    tag = tag or f"same-{attr or 'any'}{'-' + color if color else ''}-value"
    c = f' ^color {color}' if color else ''
    a1 = f' ^{attr} <a>' if attr else ''
    return f'''
## Failure ({tag}): two different{' ' + color if color else ''} locations{' with the same ' + attr if attr else ''} have the same value.
sp {{{name}*elaborate*failure*{tag}
   (state <s> ^desireds <ds> ^world <w>)
   (<w> ^anchored-world true ^objects <objs>)
   (<objs> ^object <l1> <l2>)
   (<l1> ^type location{c}{a1} ^value <v> ^object-handle <h1>)
   (<l2> ^type location{c}{a1} ^value <v> ^object-handle {{ <> <h1> }})
-->
   (<s> ^failure <ds>)
}}
'''

def near_rule(name):
    return f'''
## Failure: the value of a location is the value of an object that is next to it (the near relation of the world file).
sp {{{name}*elaborate*failure*same-value-as-neighbor
   (state <s> ^desireds <ds> ^world <w>)
   (<w> ^anchored-world true ^near <r>)
   (<r> ^argument1 <l> ^argument2 <o>)
   (<l> ^type location ^value <v>)
   (<o> ^value <v>)
-->
   (<s> ^failure <ds>)
}}
'''

def logic(name, world, default_world, title, max_n, failures, groups=(), static_rel=(), world_note='', translation=''):
    """groups: list of (handle, [member ids], target) with target ('const', k) or ('obj', id); failures: rule texts."""
    objs, rels, _ = R.read_world(world)
    nums = auto_nums()
    trans = translation + '\n- Operator write (argument1 = the location, argument2 = number-k for k from 1 to %d).' % max_n
    t = R.RosieTask(name, _desc(title, nums, default_world + world_note, trans), world, handle,
                    maintained=['empty'], concept=lambda n, o, r: {i for i, a in o.items() if a['category'] == 'location' and 'value' not in a},
                    derived=('goal-met', 'sum'), copy_relations=('below',),
                    static_relations={r: rels[r] for r in static_rel})
    for k in range(1, max_n + 1):
        t.t.objects.append((f'number-{k}', {'type': 'number', 'number': k}, []))
    h = t.h
    # group objects: static member relations, sum target
    for gh, members, target in groups:
        props = {'type': 'group', 'size': len(members)}
        if target[0] == 'const': props['target-value'] = target[1]
        t.t.objects.append((gh, props, []))
        for m in members:
            v = f'<member-{gh}-{h[m]}>'
            t.t.init_extra += [f'(<w> ^member {v})', f'({v} ^argument1 <o-{gh}> ^argument2 <o-{h[m]}>)']
        if target[0] == 'obj':
            v = f'<target-{gh}>'
            t.t.init_extra += [f'(<w> ^sum-target {v})', f'({v} ^argument1 <o-{gh}> ^argument2 <o-{h[target[1]]}>)']
    if groups:
        t.t.copy_relations += ['member'] + (['sum-target'] if any(g[2][0] == 'obj' for g in groups) else [])
    t.add(t.t.propose('write', '''   (<objs> ^object <l> <n>)
   (<l> ^type location ^object-handle <lh>)
   (<n> ^type number ^number <k> ^object-handle <nh>)
   (<w> ^empty <e>)
   (<e> ^argument1 <l>)''', ['<l>', '<n>']))
    cond = '''   (<w> ^anchored-world true ^objects <objs> ^empty <e>)
   (<objs> ^object <l> <n>)
   (<l> ^object-handle <lh>)
   (<n> ^object-handle <nh> ^number <k>)
   (<e> ^argument1 <l>)'''
    t.add(f'''
## Effect of write (look-ahead): the location has the value; it is no longer empty.
sp {{{name}*apply*write*internal
   (state <s> ^operator <op> ^internal-actions true ^world <w>)
   (<op> ^task-operator true ^name write ^pre-conditions-satisfied true ^argument1.object-handle <lh> ^argument2.object-handle <nh>)
{cond}
-->
   (<l> ^value <k>)
   (<w> ^empty <e> -)
}}

## Effect of a completed write command on the real world (once per command).
sp {{{name}*apply*write*environment-effect
   :o-support
   (state <s> ^superstate nil ^world <w> ^io.output-link.perform-action <pa>)
   (<pa> ^name write ^status complete ^argument1 <lh> ^argument2 <nh> -^effect-applied true)
{cond}
-->
   (<l> ^value <k>)
   (<w> ^empty <e> -)
   (<pa> ^effect-applied true)
   (write |Write | <k> | on | <lh> (crlf))
}}
''')
    for f in failures:
        t.add(f)
    # one sum rule per group size, then the two failure tests
    for size in sorted({len(m) for _, m, _ in groups}):
        ms = range(1, size + 1)
        hs = ' '.join(f'<m{i}>' for i in ms)
        conds = '\n'.join(f'   (<r{i}> ^argument1 <g> ^argument2 <l{i}>)\n   (<l{i}> ^value <v{i}> ^object-handle '
                          + ('<h1>)' if i == 1 else '{ ' + ' '.join(f'<> <h{j}>' for j in range(1, i)) + f' <h{i}> }})')
                          for i in ms)
        t.add(f'''
## Sum of a group of {size} locations, once every member has a value (derived; not copied into look-ahead worlds).
sp {{{name}*elaborate*group*sum*{size}
   (state <s> ^world <w>)
   (<w> ^anchored-world true ^objects.object <g> ^member {' '.join(f'<r{i}>' for i in ms)})
   (<g> ^type group ^size {size})
{conds}
-->
   (<g> ^sum (+ {' '.join(f'<v{i}>' for i in ms)}))
}}
''')
    if any(g[2][0] == 'const' for g in groups):
        t.add(f'''
## Failure: the locations of a group are filled and their sum is not the group's number.
sp {{{name}*elaborate*failure*group-sum-constant
   (state <s> ^desireds <ds> ^world <w>)
   (<w> ^anchored-world true ^objects.object <g>)
   (<g> ^type group ^target-value <tv> ^sum {{ <> <tv> }})
-->
   (<s> ^failure <ds>)
}}
''')
    if any(g[2][0] == 'obj' for g in groups):
        t.add(f'''
## Failure: the locations of a group are filled and their sum is not the value of the group's target.
sp {{{name}*elaborate*failure*group-sum-target
   (state <s> ^desireds <ds> ^world <w>)
   (<w> ^anchored-world true ^objects.object <g> ^sum-target <st>)
   (<st> ^argument1 <g> ^argument2 <tg>)
   (<g> ^type group ^sum <sum>)
   (<tg> ^value {{ <> <sum> }})
-->
   (<s> ^failure <ds>)
}}
''')
    locs = [h[i] for i, a in sorted(objs.items()) if a['category'] == 'location']
    t.add(f'''
## Goal: all locations are filled (expanded over the locations of the world file; filled: value more than zero).
sp {{{name}*elaborate*goal*all-filled
   (state <s> ^world <w>)
   (<w> ^anchored-world true ^objects <objs>)
   (<objs> ^object <t> {' '.join(f'<l-{x}>' for x in locs)})
   (<t> ^type task)
''' + '\n'.join(f'   (<l-{x}> ^object-handle {x} ^value > 0)' for x in locs) + '''
-->
   (<t> ^goal-met true)
}
''')
    _finish(t, name, world, default_world)
    return t

# ------------------------------------------------------------------ group builders from the world file
def by_attr(objs, attr, color=None):
    out = {}
    for i, a in objs.items():
        if a['category'] == 'location' and (color is None or a.get('color') == color) and attr in a:
            out.setdefault(a[attr], []).append(i)
    return out

def line_sums(objs, line_attr, cell_color, clue_color, prefix):
    """Groups of the cell_color locations sharing line_attr (row or column), target: the clue_color location on that line.
    Lines with no cell_color location are not groups (A-L4)."""
    groups = []
    cells = by_attr(objs, line_attr, cell_color)
    for v, members in sorted(cells.items()):
        clues = [i for i, a in objs.items() if a['category'] == 'location' and a.get('color') == clue_color and a.get(line_attr) == v]
        if clues:
            assert len(clues) == 1, (prefix, v, clues)
            groups.append((f'{prefix}-{v}', sorted(members), ('obj', clues[0])))
    return groups

# ------------------------------------------------------------------ the twelve tasks
L4 = '\n- "a location ... a location ... the former ... the latter" are two different locations (A-L1).'

def task(folder, world):
    objs, rels, _ = R.read_world(world)
    S = lambda attr, tag=None: same_rule(NAME[folder], attr, tag=tag)
    n = NAME[folder]
    if folder == 'four-map-coloring':
        return logic(n, world, 'init-map-ncolor3rc.world', 'Map coloring with numbers', 4, [near_rule(n)],
                     static_rel=('near',), world_note=' (a 3x3 grid of locations, six filled; near relation between neighbors)',
                     translation='- "an object that is next to the location": the near relation of the world file (A-L2).')
    if folder in ('sudoku', 'jigsawdoku'):
        return logic(n, world, {'sudoku': 'init-mini-sudoku2.world', 'jigsawdoku': 'init-jigsawdoku.world'}[folder],
                     {'sudoku': 'Mini sudoku', 'jigsawdoku': 'Jigsawdoku'}[folder], 4,
                     [S('row'), S('column'), S('section')], world_note=' (a 4x4 grid in four sections, four empty)', translation=L4)
    if folder == 'logi-five':
        return logic(n, world, 'init-logi5.world', 'Logi-5', 4, [S('row'), S('column'), S('color')],
                     world_note=' (a 4x4 grid in four color regions, four empty)', translation=L4)
    if folder == 'kenken':
        groups = [(f'group-{c}', sorted(m), ('const', 10)) for c, m in by_attr(objs, 'color').items()]
        return logic(n, world, 'init-color-ken.world', 'KenKen (color groups)', 4, [S('row'), S('column')], groups=groups,
                     world_note=' (a 4x4 grid in four color groups, four empty)',
                     translation=L4 + '\n- group: locations with the same color ("If the blocks have the same color then they are in a group"); each must sum to ten when filled.')
    if folder == 'kenken2':
        groups = [(f'region-{c}', sorted(m), ('const', 10)) for c, m in by_attr(objs, 'section').items()]
        return logic(n, world, 'init-ken-ken.world', 'KenKen (sections)', 4, [S('row'), S('column')], groups=groups,
                     world_note=' (a 4x4 grid in four sections, four empty)',
                     translation=L4 + '\n- region: locations with the same section; each must sum to ten when filled.')
    if folder == 'killer-sudoku':
        groups = [(f'group-{c}', sorted(m), ('const', 10)) for c, m in by_attr(objs, 'color').items()]
        return logic(n, world, 'init-killer-sudoku.world', 'Killer sudoku', 4, [S('row'), S('column'), S('section')],
                     groups=groups, world_note=' (a 4x4 grid with sections and color groups, four empty)',
                     translation=L4 + '\n- group: locations with the same color; each must sum to ten when filled.')
    if folder == 'kakuro':
        groups = line_sums(objs, 'column', 'green', 'blue', 'file') + line_sums(objs, 'row', 'green', 'yellow', 'rank')
        return logic(n, world, 'init-kakuro.world', 'Kakuro', 9,
                     [same_rule(n, 'row', 'green', 'identical-green-same-row'), same_rule(n, 'column', 'green', 'identical-green-same-column')],
                     groups=groups, world_note=' (a 5x4 grid: green cells, blue column clues, yellow row clues, black cells)',
                     translation='- file (rank): the green locations of one column (row); the sum is over those green locations, and its target is the blue (yellow) location of that column (row): "atop" ("aside") (A-L3). A column or row with no green location is no file (rank) (A-L4).')
    if folder == 'shuffle':
        groups = line_sums(objs, 'column', 'green', 'blue', 'file') + line_sums(objs, 'row', 'green', 'blue', 'rank')
        return logic(n, world, 'init-shuffle.world', 'Shuffle', 9, [], groups=groups,
                     world_note=' (a 4x4 grid: green cells, blue clues in the first row and the last column, one black cell)',
                     translation='- file (rank): the green locations of one column (row); the sum is over those green locations, and its target is the blue location of that column (row): "beneath" ("beside") (A-L3, A-L4).')
    if folder == 'survo':
        groups = line_sums(objs, 'column', 'green', 'blue', 'file') + line_sums(objs, 'row', 'green', 'blue', 'rank')
        return logic(n, world, 'init-survo2.world', 'Survo', 12, [same_rule(n, None, 'green', 'same-value-green')], groups=groups,
                     world_note=' (a 4x5 grid: green cells, blue clues in the first row and the last column, one black cell)',
                     translation='- file (rank): the green locations of one column (row), target the blue location of that column (row) (A-L3, A-L4).')
    if folder in ('sujiko', 'suko'):
        under = {}
        for l, b in rels.get('under', []): under.setdefault(b, []).append(l)
        groups = [(f'grouping-{b}', sorted(m), ('obj', b)) for b, m in sorted(under.items())]
        fails = [same_rule(n, None, None, 'same-value-any')]
        if folder == 'suko':
            for c, k in (('blue', 10), ('red', 9), ('green', 26)):
                groups.append((f'{c}-locations', sorted(by_attr(objs, 'color', c).get(c, [])) or
                               sorted(i for i, a in objs.items() if a.get('color') == c and a['category'] == 'location'), ('const', k)))
        return logic(n, world, {'sujiko': 'init-sujiko.world', 'suko': 'init-suko.world'}[folder],
                     {'sujiko': 'Sujiko', 'suko': 'Suko'}[folder], 9, fails, groups=groups,
                     world_note=' (a 3x3 grid of locations and four clue blocks, each above the four locations around it)',
                     translation='- grouping: the locations under one block (the under relation of the world file); target: that block\'s value.' +
                     ('\n- "the blue (red, green) locations are filled and the sum of the values of them is not ten (nine, twenty-six)": a group per color with a constant target.' if folder == 'suko' else ''))
    raise KeyError(folder)

NAME = {'four-map-coloring': 'number-map-color', 'jigsawdoku': 'jigsawdoku-sudoku', 'kakuro': 'kakuro', 'kenken': 'color-ken-ken',
        'kenken2': 'ken-ken', 'killer-sudoku': 'killer-sudoku', 'logi-five': 'logi-five', 'shuffle': 'shuffle',
        'sudoku': 'mini-sudoku', 'sujiko': 'sujiko', 'suko': 'suko', 'survo': 'survo'}
