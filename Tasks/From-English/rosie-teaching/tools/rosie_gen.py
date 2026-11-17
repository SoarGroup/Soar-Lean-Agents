"""Shared pieces for translating a Rosie teaching dialog into a world-convention Soar agent (pilot, 16 Nov 2026).

What is shared across tasks (see rosie-language.md for the reading of each statement form):
  - reading a .world file (objects, relations, relation sets) into world-convention objects and relation objects;
  - the task object that carries the goal (^goal-met true, a derived attribute) and the failure (state ^failure);
  - the loader file, the problem space, flags and achievement rules (from wg.py, worldgen v19);
  - writing the same rules with any example state (init, fail, final) as the initial world, for the state checks.
What each task's gen.py supplies: the operators (proposal + application), the maintained concepts and how
each action changes them, and the goal and failure elaborations, each with the statement it comes from."""
import os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import wg

def _val(v):
    """World-file values: symbols lose Rosie's trailing sense number (red1 -> red); numbers stay numbers (4.0 -> 4)."""
    try:
        f = float(v)
        return int(f) if f == int(f) else f
    except ValueError:
        return re.sub(r'1$', '', v)

def read_world(path):
    """-> objects {id: {attr: value}}, relations {name: [(id1, id2)]}, sets {name: [[ids]]}"""
    objs, rels, sets = {}, {}, {}
    for block in open(path).read().strip().split('\n\n'):
        lines = [l.split() for l in block.strip().splitlines() if l.strip()]
        if not lines: continue
        head = lines[0]
        if head[0] == 'objid':
            objs[int(head[1])] = {l[0]: _val(l[1]) for l in lines[1:]}
        elif head[0] == 'predicate':
            rels.setdefault(_val(head[1]), []).extend((int(a), int(b)) for a, b in lines[1:])
        elif head[0] == 'predicate-set':
            sets.setdefault(head[1], []).extend([int(x) for x in l] for l in lines[1:])
    return objs, rels, sets

class RosieTask:
    """name: task name; desc: header comment; world: path of the initial world file;
    handle(id, attrs) -> handle string; maintained: names of one-argument relations kept by the actions,
    computed for the initial world by concept(name, objs, rels) -> set of ids."""
    def __init__(s, name, desc, world, handle, maintained=(), concept=None, static=(), derived=('goal-met',),
                 member_sets=(), copy_relations=('below',), extra_flags='', task_props=None,
                 extra_props=None, static_relations=None):
        s.name = name
        s.objs, s.rels, s.sets = read_world(world)
        s.h = {i: handle(i, a) for i, a in s.objs.items()}
        t = s.t = wg.Task(name, desc, layout='flat', static=static, derived=list(derived))
        for i, a in sorted(s.objs.items()):
            props = {'type': a['category'], **{k: v for k, v in a.items() if k != 'category'},
                     **(extra_props(i, a, s.rels) if extra_props else {})}
            t.objects.append((s.h[i], props, []))
        t.objects.append(('task', {'type': 'task', **(task_props or {})}, []))
        for rel in ('on', 'below'):
            for k, (a, b) in enumerate(s.rels.get(rel, [])):
                v = f'<{rel}-{k}>'
                t.init_extra += [f'(<w> ^{rel} {v})', f'({v} ^argument1 <o-{s.h[a]}> ^argument2 <o-{s.h[b]}>)']
        for name_ in maintained:
            for i in sorted(concept(name_, s.objs, s.rels)):
                v = f'<{name_}-{s.h[i]}>'
                t.init_extra += [f'(<w> ^{name_} {v})', f'({v} ^argument1 <o-{s.h[i]}>)']
        for setname, objtype in member_sets:   # a predicate-set becomes objects of objtype and a static member relation
            for k, members in enumerate(s.sets.get(setname, []), 1):
                lh = f'{objtype}-{k}'
                t.objects.append((lh, {'type': objtype}, []))
                for m in members:
                    v = f'<member-{k}-{s.h[m]}>'
                    t.init_extra += [f'(<w> ^member {v})', f'({v} ^argument1 <o-{lh}> ^argument2 <o-{s.h[m]}>)']
        for rel, pairs in (static_relations or {}).items():   # static relations computed by the task from the world file
            for k, (a, b) in enumerate(pairs):
                v = f'<{rel}-{k}>'
                t.init_extra += [f'(<w> ^{rel} {v})', f'({v} ^argument1 <o-{s.h[a]}> ^argument2 <o-{s.h[b]}>)']
        t.copy_relations = list(copy_relations) + list(static_relations or {}) + list(maintained) + (['member'] if member_sets else [])
        t.extra_flags = extra_flags
        t.desired.append(('task', {'goal-met': 'true'}))
        t.add(t.achievement())

    def add(s, text): s.t.add(text)

    def text(s): return s.t.text()

    def write(s, out):
        open(out, 'w').write(s.text())

def loader(task_file, rules_file, depth_to_repo):
    """The task's .soar loader: the shared library from the repository, then the task rules."""
    lib = '/'.join(['..'] * depth_to_repo + ['Soar', 'soar-library'])
    return f'''# Loads the shared Soar library from the repository (Soar/soar-library), then the task rules.
# The path assumes this folder sits at Tasks/From-English/rosie-teaching/<category>/<task>.
# To use another library location: SOAR_LIBRARY=/path/to/soar-library python3 gen.py
pushd "{os.environ.get('SOAR_LIBRARY', lib)}"
source soar-library.soar
popd
source {rules_file}
'''
