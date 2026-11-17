"""WorldSpec in Python: a stand-in for `rosiegen` where Lean cannot be built (16 November 2026).

One task description, written once in Python with the constructors below, gives:
  * the Lean source of the description (agentgen/WorldSpec/Tasks/<Name>.lean), printed from the same data;
  * the path B input (worldspec-1 JSON, the format of WorldSpec/Json.lean) for spec_backend.py;
  * the checks rosiegen makes: example states (goal, losing conditions, maintained relations),
    replay of a run, and breadth-first search for a shortest plan.

The semantics is a line-by-line port of agentgen/WorldSpec/Sem.lean and the world-file reader of
WorldSpec/WorldFile.lean. It is NOT a substitute for the Lean check: once Lean builds, run
`rosiegen json` on the printed Lean file and compare its JSON with the one written here
(`compare_json`), and prove `wellFormed = []` as in WorldSpec/Proofs.lean.

usage:
  python3 worldspec_py.py TASKS.py lean OUT.lean
  python3 worldspec_py.py TASKS.py json WORLD OUT.json
  python3 worldspec_py.py TASKS.py check WORLD
  python3 worldspec_py.py TASKS.py explore WORLD LIMIT
  python3 worldspec_py.py TASKS.py replay WORLD RUN.json
TASKS.py defines TASK (a dict built with the constructors here).
"""
import itertools, json, re, sys

# ---------------------------------------------------------------- constructors (JSON shapes of Json.lean)
def sym(s): return {'sym': s}
def num(i): return {'int': i}
def V(x): return {'var': x}
def H(h): return {'h': h}
def val(x): return {'val': x}
def plus(a, b): return {'plus': [a, b]}
def prop(y, q): return {'prop': [y, q]}
def obj(x, t=None): return {'obj': x, 'type': t}
def has(x, p, cmp, rhs): return {'has': x, 'prop': p, 'cmp': cmp, 'rhs': rhs}
def rel(r, *args): return {'rel': r, 'args': list(args)}
def distinct(x, y): return {'distinct': [x, y]}
def lacks(x, p): return {'lacks': [x, p]}
def none(*atoms): return {'none': list(atoms)}
def ex(*atoms): return {'ex': list(atoms)}
def forall(var, type, body, outer=(), filter=()): return {'all': {'outer': list(outer), 'var': var, 'type': type, 'filter': list(filter), 'body': list(body)}}
def e_set(x, p, rhs): return {'set': x, 'prop': p, 'rhs': rhs}
def e_update(x, p, rhs): return {'update': x, 'prop': p, 'rhs': rhs}
def e_each(atoms, eff): return {'each': list(atoms), 'eff': eff}
def e_add(r, *args): return {'add': r, 'args': list(args)}
def e_del(r, *args): return {'del': r, 'args': list(args)}
def e_change(r, args, pos, to): return {'change': r, 'args': list(args), 'pos': pos, 'to': to}
def text(s): return {'text': s}
def handle(x): return {'handle': x}

# ---------------------------------------------------------------- world file (WorldFile.lean)
def strip_sense(s): return s[:-1] if s.endswith('1') else s

def parse_val(s):
    t = s[:-2] if s.endswith('.0') else s
    try: return num(int(t))
    except ValueError: return sym(strip_sense(s))

def parse_world(textv):
    objs, rels = [], {}
    for b in textv.replace('\r', '').split('\n\n'):
        lines = [l.split() for l in b.split('\n') if l.split()]
        if not lines: continue
        if lines[0][0] == 'objid':
            objs.append({'id': int(lines[0][1]), 'attrs': [(l[0], parse_val(l[1])) for l in lines[1:] if len(l) == 2]})
        elif lines[0][0] == 'predicate':
            name = strip_sense(lines[0][1])
            rels.setdefault(name, []).extend([[int(x) for x in l] for l in lines[1:]])
    return objs, rels

def wsym(o, a):
    for k, v in o['attrs']:
        if k == a: return vstr(v)
    return ''

def vstr(v):
    if 'sym' in v: return v['sym']
    if 'int' in v: return str(v['int'])
    return 'true' if v['bool'] else 'false'

# ---------------------------------------------------------------- semantics (Sem.lean)
class State:
    def __init__(s, objs, rels): s.objs, s.rels = objs, rels
    def obj(s, h): return next((o for o in s.objs if o['handle'] == h), None)
    def prop(s, h, p):
        o = s.obj(h)
        if o is None: return None
        if p == 'type': return sym(o['type'])
        return next((v for k, v in o['props'] if k == p), None)
    def key(s):
        os_ = sorted(o['handle'] + ':' + ','.join(sorted(f'{k}={vstr(v)}' for k, v in o['props'])) for o in s.objs)
        rs = sorted(f"{r}({','.join(hs)})" for r, hs in s.rels)
        return ';'.join(os_) + '|' + ';'.join(rs)

def lookup(b, x):
    for k, v in b:
        if k == x: return v
    return None

def cands(st, x, b):
    return [b] if lookup(b, x) is not None else [[(x, o['handle'])] + b for o in st.objs]

def cmpval(c, a, b):
    if c == 'eq': return a == b
    if c == 'ne': return a != b
    if 'int' in a and 'int' in b:
        a, b = a['int'], b['int']
        return {'lt': a < b, 'le': a <= b, 'gt': a > b, 'ge': a >= b}[c]
    return False

def arg_match(b, pairs):
    for a, v in pairs:
        if 'h' in a:
            if a['h'] != v: return None
        else:
            w = lookup(b, a['var'])
            if w is None: b = [(a['var'], v)] + b
            elif w != v: return None
    return b

def rhs_val(pre, b, r):
    if 'val' in r: return r['val']
    if 'plus' in r:
        a, c = (rhs_val(pre, b, x) for x in r['plus'])
        return num(a['int'] + c['int']) if a and c and 'int' in a and 'int' in c else None
    return pre.prop(lookup(b, r['prop'][0]), r['prop'][1])

def rhs_vals(st, b, r):
    if 'val' in r: return [(b, r['val'])]
    if 'plus' in r:
        out = []
        for b1, v1 in rhs_vals(st, b, r['plus'][0]):
            for b2, v2 in rhs_vals(st, b1, r['plus'][1]):
                if 'int' in v1 and 'int' in v2: out.append((b2, num(v1['int'] + v2['int'])))
        return out
    y, q = r['prop']
    out = []
    for b2 in cands(st, y, b):
        pv = st.prop(lookup(b2, y), q)
        if pv is not None: out.append((b2, pv))
    return out

def step(st, b, a):
    if 'obj' in a:
        out = []
        for b2 in cands(st, a['obj'], b):
            o = st.obj(lookup(b2, a['obj']))
            if o is not None and (a['type'] is None or o['type'] == a['type']): out.append(b2)
        return out
    if 'has' in a:
        out = []
        for b2 in cands(st, a['has'], b):
            for b3, v in rhs_vals(st, b2, a['rhs']):
                u = st.prop(lookup(b3, a['has']), a['prop'])
                if u is not None and cmpval(a['cmp'], u, v): out.append(b3)
        return out
    if 'rel' in a:
        out = []
        for n, t in st.rels:
            if n == a['rel'] and len(t) == len(a['args']):
                m = arg_match(b, list(zip(a['args'], t)))
                if m is not None: out.append(m)
        return out
    if 'distinct' in a:
        x, y = a['distinct']
        return [b3 for b2 in cands(st, x, b) for b3 in cands(st, y, b2) if lookup(b3, x) != lookup(b3, y)]
    if 'lacks' in a:
        x, p = a['lacks']
        return [b2 for b2 in cands(st, x, b) if st.prop(lookup(b2, x), p) is None]
    if 'none' in a:
        return [b] if not solve(st, b, a['none']) else []
    raise ValueError(a)

def solve(st, b, atoms):
    if not atoms: return [b]
    return [b3 for b2 in step(st, b, atoms[0]) for b3 in solve(st, b2, atoms[1:])]

def holds_in(st, b, atoms): return bool(solve(st, b, atoms))

def cond_holds(st, c):
    if 'ex' in c: return holds_in(st, [], c['ex'])
    fa = c['all']
    return any(all(not holds_in(st, [(fa['var'], o['handle'])] + b, fa['filter']) or holds_in(st, [(fa['var'], o['handle'])] + b, fa['body'])
                   for o in st.objs if o['type'] == fa['type'])
               for b in solve(st, [], fa['outer']))

def with_sums(sums, st):
    if not sums: return st
    objs = []
    for o in st.objs:
        o = dict(o, props=list(o['props']))
        for s in sums:
            if o['type'] != s['ownerType']: continue
            ms = [t[1] for n, t in st.rels if n == s['rel'] and t[0] == o['handle'] and len(t) > 1]
            vs = [st.prop(m, s['prop']) for m in ms]
            if not ms or any(v is None for v in vs): continue
            o['props'].append((s['attr'], num(sum(v.get('int', 0) for v in vs))))
        objs.append(o)
    return State(objs, st.rels)

def with_derived(ds, st):
    for d in ds:
        tuples = []
        for b in solve(st, [], d['defn']):
            tup = [lookup(b, x) for x in d['vars']]
            if None not in tup and tup not in tuples: tuples.append(tup)
        st = State(st.objs, st.rels + [(d['name'], tup) for tup in tuples])
    return st

def view(t, st): return with_derived(t.get('derived', []), with_sums(t['sums'], st))

def failed(t, st): return [f['name'] for f in t['failures'] if cond_holds(view(t, st), f['cond'])]
def goal_met(t, st): return cond_holds(view(t, st), t['goal'])

def members(m, st):
    return [o['handle'] for o in st.objs if o['type'] != 'task' and holds_in(st, [(m['var'], o['handle'])], m['defn'])]

def maintained_errors(t, st):
    errs = []
    for m in t['maintained']:
        held = [a[0] for n, a in st.rels if n == m['name']]
        want = members(m, st)
        errs += [f"{m['name']} missing for {x}" for x in want if x not in held]
        errs += [f"{m['name']} held but false for {x}" for x in held if x not in want]
    return errs

def arg_h(b, a):
    if 'h' in a: return a['h']
    v = lookup(b, a['var'])
    if v is None: raise ValueError(f"unbound variable {a['var']}")
    return v

def remove_first(r, hs, rels):
    for i, (n, t) in enumerate(rels):
        if n == r and t == hs: return rels[:i] + rels[i + 1:]
    return None

def apply_eff(pre, b, st, e):
    if 'set' in e:
        h = arg_h(b, V(e['set']))
        v = rhs_val(pre, b, e['rhs'])
        if v is None: raise ValueError(f"no value for {e['set']}.{e['prop']}")
        if pre.prop(h, e['prop']) is not None: raise ValueError(f"set: {h} already has {e['prop']}")
        objs = [o if o['handle'] != h else dict(o, props=[(k, x) for k, x in o['props'] if k != e['prop']] + [(e['prop'], v)]) for o in st.objs]
        return State(objs, st.rels)
    if 'update' in e:
        h = arg_h(b, V(e['update']))
        v = rhs_val(pre, b, e['rhs'])
        if v is None: raise ValueError(f"no value for {e['update']}.{e['prop']}")
        if pre.prop(h, e['prop']) is None: raise ValueError(f"update: {h} has no {e['prop']}")
        objs = [o if o['handle'] != h else dict(o, props=[(k, x) for k, x in o['props'] if k != e['prop']] + [(e['prop'], v)]) for o in st.objs]
        return State(objs, st.rels)
    if 'add' in e: return State(st.objs, st.rels + [(e['add'], [arg_h(b, a) for a in e['args']])])
    if 'del' in e:
        hs = [arg_h(b, a) for a in e['args']]
        rs = remove_first(e['del'], hs, st.rels)
        if rs is None: raise ValueError(f"del: no {e['del']}{hs}")
        return State(st.objs, rs)
    if 'each' in e:
        out = st
        for b2 in solve(pre, b, e['each']): out = apply_eff(pre, b2, out, e['eff'])
        return out
    hs = [arg_h(b, a) for a in e['args']]
    th = arg_h(b, e['to'])
    rs = remove_first(e['change'], hs, st.rels)
    if rs is None: raise ValueError(f"change: no {e['change']}{hs}")
    nh = list(hs); nh[e['pos'] - 1] = th
    return State(st.objs, rs + [(e['change'], nh)])

def legal(t, st, op, args):
    if len(args) != len(op['params']): return None
    for (x, ty), h in zip(op['params'], args):
        o = st.obj(h)
        if o is None or (ty is not None and o['type'] != ty): return None
    sol = solve(view(t, st), [(x, h) for (x, _), h in zip(op['params'], args)][::-1], op['pre'])
    return sol[0] if sol else None

def apply_op(t, st, name, args):
    op = next((o for o in t['ops'] if o['name'] == name), None)
    if op is None: raise ValueError(f'unknown operator {name}')
    b = legal(t, st, op, args)
    if b is None: raise ValueError(f'{name} {args} is not legal')
    pre = view(t, st)
    sol = solve(pre, b, op['bind'])
    if not sol: raise ValueError(f'{name} {args}: bind has no match')
    out = st
    for e in op['effects']: out = apply_eff(pre, sol[0], out, e)
    return out

def legal_moves(t, st):
    out = []
    for op in t['ops']:
        for args in itertools.product([o['handle'] for o in st.objs], repeat=len(op['params'])):
            if legal(t, st, op, list(args)) is not None: out.append((op['name'], list(args)))
    return out

def initial(t, world_text):
    wobjs, wrels = parse_world(world_text)
    hmap = {o['id']: t['handle'](o) for o in wobjs}
    objs = [{'handle': t['handle'](o), 'type': next((vstr(v) for k, v in o['attrs'] if k == 'category'), 'object'),
             'props': [(k, v) for k, v in o['attrs'] if k != 'category']} for o in wobjs]
    objs += [{'handle': 'task', 'type': 'task', 'props': []}]
    rels = [(r, [hmap.get(i, f'unknown-{i}') for i in tup]) for r in t['world_rels'] for tup in wrels.get(r, [])]
    st0 = State(objs, rels)
    maint = [(m['name'], [x]) for m in t['maintained'] for x in members(m, st0)]
    return State(objs, rels + maint)

def explore(t, s0, limit):
    seen, frontier, errs, depth = {s0.key()}, [(s0, [])], [], 0
    if goal_met(t, s0) and not failed(t, s0): return 0, [], 1, []
    while frontier and len(seen) < limit:
        depth += 1
        nxt = []
        for st, path in frontier:
            for op, args in legal_moves(t, st):
                try: st2 = apply_op(t, st, op, args)
                except ValueError as e: errs.append(f'{op} {args}: {e}'); continue
                me = maintained_errors(t, st2)
                if me: errs.append(f'after {op} {args}: {me}')
                k = st2.key()
                if k in seen: continue
                seen.add(k)
                if not failed(t, st2):
                    if goal_met(t, st2): return depth, path + [[op] + args], len(seen), errs
                    nxt.append((st2, path + [[op] + args]))
        frontier = nxt
    return None, None, len(seen), errs

def step_cost(t, st, name, args):
    op = next(o for o in t['ops'] if o['name'] == name)
    if op.get('stepCost') is None: return 1
    b = legal(t, st, op, args)
    v = rhs_val(st, b, op['stepCost'])
    return v['int']

def cheapest(t, s0, limit):
    import heapq
    if goal_met(t, s0) and not failed(t, s0): return 0, []
    best, n, heap = {s0.key(): 0}, 0, [(0, 0, s0, [])]
    while heap and n < limit:
        c, _, st, path = heapq.heappop(heap)
        if c > best.get(st.key(), c): continue
        if goal_met(t, st) and not failed(t, st): return c, path
        for op, args in legal_moves(t, st):
            st2 = apply_op(t, st, op, args)
            if failed(t, st2): continue
            c2, k = c + step_cost(t, st, op, args), st2.key()
            if c2 < best.get(k, 1 << 60):
                best[k] = c2; n += 1
                heapq.heappush(heap, (c2, n, st2, path + [[op] + args]))
    return None, None

def replay(t, s0, acts):
    st = s0
    for n, a in enumerate(acts, 1):
        try: st = apply_op(t, st, a[0], [x for x in a[1:] if x is not None])
        except ValueError as e: return f'action {n} illegal: {e}'
        me = maintained_errors(t, st)
        if me: return f'action {n} breaks a maintained relation: {me}'
        f = failed(t, st)
        if f: return f'action {n} reaches a losing state ({f})'
    return 'goal holds' if goal_met(t, st) else 'goal does not hold'

# ---------------------------------------------------------------- path B JSON (Json.lean)
def to_json(t, st):
    return {
        'format': 'worldspec-1', 'name': t['name'], 'title': t['title'],
        'statements': [[k, s] for k, s in t['statements']],
        'assumptions': [{'id': a['id'], 'kind': a['kind'], 'text': a['text'], 'stmts': a['stmts']} for a in t['assumptions']],
        'flags': [[f, x] for f, x in t['flags']],
        'objects': [{'handle': o['handle'], 'type': o['type'], 'props': [[k, v] for k, v in o['props']]} for o in st.objs],
        'relations': [[r, hs] for r, hs in st.rels],
        'maintained': [{'name': m['name'], 'var': m['var'], 'defn': m['defn'], 'stmts': m['stmts']} for m in t['maintained']],
        'sums': t['sums'], 'ops': [{k: (x if k != 'params' else [[p, ty] for p, ty in x]) for k, x in o.items() if not (k == 'stepCost' and x is None)} for o in t['ops']],
        'goal': t['goal'], 'goalStmts': t['goalStmts'], 'failures': t['failures'],
        **({'derived': [{'name': d['name'], 'vars': d['vars'], 'defn': d['defn'], 'stmts': d['stmts']} for d in t['derived']]} if t.get('derived') else {}),
        **({'repeatControl': t['repeatControl']} if t.get('repeatControl') else {})}

def compare_json(a, b):
    """Compare a rosiegen json export with ours (key order and number formatting aside)."""
    return json.loads(json.dumps(a, sort_keys=True)) == json.loads(json.dumps(b, sort_keys=True))

# ---------------------------------------------------------------- Lean printer (Types.lean syntax)
def ls(s): return json.dumps(s, ensure_ascii=False)
def l_val(v):
    if 'sym' in v: return f'(.sym {ls(v["sym"])})'
    if 'int' in v: return f'(.int {v["int"]})' if v['int'] >= 0 else f'(.int ({v["int"]}))'
    return f'(.bool {"true" if v["bool"] else "false"})'
def l_arg(a): return f'.var {ls(a["var"])}' if 'var' in a else f'.h {ls(a["h"])}'
def l_rhs(r):
    if 'val' in r: return f'(.val {l_val(r["val"])})'
    if 'plus' in r: return f'(.plus {l_rhs(r["plus"][0])} {l_rhs(r["plus"][1])})'
    return f'(.prop {ls(r["prop"][0])} {ls(r["prop"][1])})'
def l_atom(a):
    if 'obj' in a: return f'.obj {ls(a["obj"])} ' + ('none' if a['type'] is None else f'(some {ls(a["type"])})')
    if 'has' in a: return f'.has {ls(a["has"])} {ls(a["prop"])} .{a["cmp"]} {l_rhs(a["rhs"])}'
    if 'rel' in a: return f'.rel {ls(a["rel"])} [' + ', '.join(l_arg(x) for x in a['args']) + ']'
    if 'distinct' in a: return f'.distinct {ls(a["distinct"][0])} {ls(a["distinct"][1])}'
    if 'lacks' in a: return f'.lacks {ls(a["lacks"][0])} {ls(a["lacks"][1])}'
    return '.none [' + ', '.join(l_atom(x) for x in a['none']) + ']'
def l_atoms(xs, ind='      '): return '[' + (',\n' + ind + ' ').join(l_atom(a) for a in xs) + ']'
def l_cond(c, ind='    '):
    if 'ex' in c: return '.ex ' + l_atoms(c['ex'], ind)
    fa = c['all']
    return (f'.all {{ outer := {l_atoms(fa["outer"], ind)}, var := {ls(fa["var"])}, type := {ls(fa["type"])}, '
            f'filter := {l_atoms(fa["filter"], ind)}, body := {l_atoms(fa["body"], ind)} }}')
def l_eff(e):
    if 'set' in e: return f'.set {ls(e["set"])} {ls(e["prop"])} {l_rhs(e["rhs"])}'
    if 'update' in e: return f'.update {ls(e["update"])} {ls(e["prop"])} {l_rhs(e["rhs"])}'
    if 'each' in e: return f'.each {l_atoms(e["each"], "        ")} ({l_eff(e["eff"])})'
    if 'add' in e: return f'.add {ls(e["add"])} [' + ', '.join(l_arg(x) for x in e['args']) + ']'
    if 'del' in e: return f'.del {ls(e["del"])} [' + ', '.join(l_arg(x) for x in e['args']) + ']'
    return f'.change {ls(e["change"])} [' + ', '.join(l_arg(x) for x in e['args']) + f'] {e["pos"]} ({l_arg(e["to"])})'
def l_say(p):
    if 'text' in p: return f'.text {ls(p["text"])}'
    if 'handle' in p: return f'.handle {ls(p["handle"])}'
    return f'.prop {ls(p["prop"][0])} {ls(p["prop"][1])}'
def l_nats(xs): return '[' + ', '.join(map(str, xs)) + ']'

def to_lean(t):
    L = ['import WorldSpec.Sem', 'import WorldSpec.WorldFile',
         f'/-! {t["title"]} (Tasks/webtasks/{t["folder"]}), from the numbered English statements.',
         '    Printed by worldgen/worldspec_py.py from the same data that wrote the path B JSON. -/',
         'namespace WorldSpec.Tasks', 'open WorldSpec', '',
         f'def {t["lean_name"]} : Task where',
         f'  name := {ls(t["name"])}', f'  title := {ls(t["title"])}',
         '  statements := [\n    ' + ',\n    '.join(f'({k}, {ls(s)})' for k, s in t['statements']) + ']',
         f'  world := {{ handle := fun o => o.sym {ls(t["handle_attr"])}, rels := [' + ', '.join(ls(r) for r in t['world_rels']) + '] }']
    if t['maintained']:
        L.append('  maintained := [\n    ' + ',\n    '.join(
            f'{{ name := {ls(m["name"])}, var := {ls(m["var"])}, stmts := {l_nats(m["stmts"])},\n      defn := {l_atoms(m["defn"])} }}' for m in t['maintained']) + ']')
    if t.get('derived'):
        L.append('  derived := [\n    ' + ',\n    '.join(
            f'{{ name := {ls(d["name"])}, vars := [' + ', '.join(ls(x) for x in d['vars']) + f'], stmts := {l_nats(d["stmts"])},\n      defn := {l_atoms(d["defn"])} }}' for d in t['derived']) + ']')
    ops = []
    for o in t['ops']:
        ps = ', '.join(f'({ls(x)}, ' + ('none' if ty is None else f'some {ls(ty)}') + ')' for x, ty in o['params'])
        ops.append(f'{{ name := {ls(o["name"])}, params := [{ps}], stmts := {l_nats(o["stmts"])}\n'
                   f'      pre := {l_atoms(o["pre"])}\n'
                   f'      bind := {l_atoms(o["bind"])}\n'
                   f'      effects := [' + ', '.join(l_eff(e) for e in o['effects']) + ']\n'
                   f'      report := [' + ', '.join(l_say(p) for p in o['report']) + ']' +
                   (f'\n      stepCost := some {l_rhs(o["stepCost"])}' if o.get('stepCost') is not None else '') + ' }')
    L.append('  ops := [\n    ' + ',\n    '.join(ops) + ']')
    L.append('  goal := ' + l_cond(t['goal']))
    L.append(f'  goalStmts := {l_nats(t["goalStmts"])}')
    if t['failures']:
        L.append('  failures := [\n    ' + ',\n    '.join(
            f'{{ name := {ls(f["name"])}, stmts := {l_nats(f["stmts"])},\n      cond := {l_cond(f["cond"], "      ")} }}' for f in t['failures']) + ']')
    L.append('  assumptions := [\n    ' + ',\n    '.join(
        f'{{ id := {ls(a["id"])}, kind := .{a["kind"]}, stmts := {l_nats(a["stmts"])}, text := {ls(a["text"])} }}' for a in t['assumptions']) + ']')
    if t['flags']: L.append('  flags := [' + ', '.join(f'({ls(f)}, {ls(x)})' for f, x in t['flags']) + ']')
    if t.get('repeatControl'):
        rc = t['repeatControl']
        L.append(f'  repeatControl := some {{ rel := {ls(rc["rel"])}, types := [' + ', '.join(ls(x) for x in rc['types']) + '] }')
    L += ['', 'end WorldSpec.Tasks', '']
    return '\n'.join(L)

# ---------------------------------------------------------------- task defaults and CLI
def task(**kw):
    t = dict(maintained=[], derived=[], sums=[], failures=[], flags=[], assumptions=[], handle_attr='name')
    t.update(kw)
    ha = t['handle_attr']
    t['handle'] = lambda o, ha=ha: wsym(o, ha)
    return t

def load_task(path):
    ns = {}
    exec(compile(open(path).read(), path, 'exec'), ns)
    return ns['TASK']

def main(argv):
    t = load_task(argv[1]); cmd = argv[2]
    if cmd == 'lean':
        open(argv[3], 'w', newline='\n').write(to_lean(t)); print('wrote', argv[3]); return
    st = initial(t, open(argv[3]).read())
    if cmd == 'json':
        open(argv[4], 'w', newline='\n').write(json.dumps(to_json(t, st), indent=2) + '\n'); print('wrote', argv[4])
    elif cmd == 'check':
        print(json.dumps({'goal-met': goal_met(t, st), 'failure': failed(t, st), 'maintained-errors': maintained_errors(t, st)}))
    elif cmd == 'explore':
        d, plan, n, errs = explore(t, st, int(argv[4]))
        print(f"shortest plan: {str(d) + ' actions' if d is not None else 'none found'}; {n} states; {len(errs)} errors")
        for e in errs[:10]: print('  ', e)
        if plan: print('  plan:', ' | '.join(' '.join(a) for a in plan))
    elif cmd == 'cheapest':
        c, plan = cheapest(t, st, int(argv[4]))
        print(f'cheapest plan: cost {c}, {len(plan) if plan else 0} actions')
        if plan: print('  plan:', ' | '.join(' '.join(a) for a in plan))
    elif cmd == 'replay':
        run = json.load(open(argv[4]))
        print(f"{run.get('outcome', '?')}, {len(run['actions'])} actions: {replay(t, st, run['actions'])}")

if __name__ == '__main__':
    main(sys.argv)
