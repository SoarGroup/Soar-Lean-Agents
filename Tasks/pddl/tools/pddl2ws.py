"""PDDL (STRIPS subset) to a WorldSpec description, a Rosie world file and a loader (23 November 2026).

usage: python3 pddl2ws.py DOMAIN.pddl PROBLEM.pddl OUTDIR [--task NAME]

Writes into OUTDIR:
  <task>-spec.py        the WorldSpec description (constructors of worldspec_py.py), TASK
  init-<problem>.world  the initial world (objects with categories; relation tuples)
  <task>.soar           loader: the shared library, then <task>-rules.soar
Rules and JSON are then made by the usual path B tools (see run_pddl.py, which does all of it).

Translation (literal; no information added):
  object of PDDL type T            -> object with category T ('object' when the domain is untyped)
  predicate p(x1..xn), n >= 1      -> relation p with arguments argument1..argumentn (unary type predicates included)
  action parameters ?x - T         -> operator parameters (x, T); the action name is the operator name
  precondition atom                -> rel atom; (not (= ?x ?y)) -> distinct x y
  effect (not atom) / atom         -> e_del / e_add, deletes before adds (PDDL applies deletes first)
  goal (and atoms)                 -> ex(...) of rel atoms with handles for the objects
  constants                        -> handles

Refused, with the reason printed (each is a question for the conventions or WorldSpec, not decided here):
  nullary predicates not listed in PROPOSITIONS; a parameter type with subtypes; other negative preconditions; or, imply, exists, forall,
  when; a deleted atom that is not a precondition (PDDL deletes it if present; a WorldSpec del needs it present);
  a goal that is not a conjunction of positive ground atoms; numeric fluents.
"""
import re, sys, os
from pathlib import Path

# ------------------------------------------------------------------ propositions (nullary predicates)
# Decided by John Laird, 23 Nov 2026 (World-Conventions L7-027, L3-104): a proposition is a property of an object in the world,
# (<objs> ^object <o>) (<o> ^object-handle hand ^empty true|false). Any property that is tested for true
# also carries false (no negated conditions in rule tests), so every proposition is initialized to true or
# false and maintained by operators (update effects). The object and property for each proposition are
# given per domain here (reviewed by John, 23 Nov 2026).
PROPOSITIONS = {
    'handempty': ('hand', 'hand', 'empty'),                       # blocksworld-4ops
    'empty-ferry': ('ferry', 'ferry', 'empty'),                   # ferry
    'arm-empty': ('arm', 'arm', 'empty'),                         # grid
    'movie-rewound': ('movie', 'movie', 'rewound'),               # movie
    'counter-at-zero': ('counter', 'counter', 'at-zero'),
    'counter-at-two-hours': ('counter', 'counter', 'at-two-hours'),
    'counter-at-other-than-two-hours': ('counter', 'counter', 'at-other-than-two-hours'),
    'have-chips': ('viewer', 'viewer', 'have-chips'),
    'have-dip': ('viewer', 'viewer', 'have-dip'),
    'have-pop': ('viewer', 'viewer', 'have-pop'),
    'have-cheese': ('viewer', 'viewer', 'have-cheese'),
    'have-crackers': ('viewer', 'viewer', 'have-crackers'),
}
TRUE, FALSE = {'val': {'sym': 'true'}}, {'val': {'sym': 'false'}}
def pvar(handle): return 'n' + re.sub(r'[^a-z0-9]', '', handle)

# ------------------------------------------------------------------ s-expressions
def tokens(text):
    text = re.sub(r';[^\n]*', ' ', text)
    return re.findall(r'\(|\)|[^\s()]+', text.lower())

def parse(text):
    toks = tokens(text); pos = 0
    def rd():
        nonlocal pos
        t = toks[pos]; pos += 1
        if t == '(':
            out = []
            while toks[pos] != ')': out.append(rd())
            pos += 1
            return out
        return t
    return rd()

def typed_list(xs):
    """[a b - t c - u d] -> [(a,t),(b,t),(c,u),(d,'object')]"""
    out, pend, i = [], [], 0
    while i < len(xs):
        if xs[i] == '-':
            t = xs[i + 1]
            if isinstance(t, list): raise Refuse('either-types')
            out += [(p, t) for p in pend]; pend = []; i += 2
        else:
            pend.append(xs[i]); i += 1
    return out + [(p, 'object') for p in pend]

class Refuse(Exception): pass

def section(form, key):
    for x in form[2:]:
        if isinstance(x, list) and x and x[0] == key: return x
    return None

# ------------------------------------------------------------------ domain
def read_domain(path):
    f = parse(open(path).read())
    assert f[0] == 'define' and f[1][0] == 'domain'
    d = {'name': f[1][1]}
    req = section(f, ':requirements'); d['requirements'] = req[1:] if req else []
    ty = section(f, ':types'); d['types'] = typed_list(ty[1:]) if ty else []
    co = section(f, ':constants'); d['constants'] = typed_list(co[1:]) if co else []
    pr = section(f, ':predicates')
    d['predicates'] = {p[0]: typed_list(p[1:]) for p in (pr[1:] if pr else [])}
    if section(f, ':functions'): raise Refuse('numeric fluents (:functions)')
    d['actions'] = []
    for x in f[2:]:
        if isinstance(x, list) and x[0] == ':action':
            a = {'name': x[1]}
            for k in range(2, len(x), 2): a[x[k]] = x[k + 1]
            d['actions'].append(a)
    return d

def subtypes(d):
    return {sup for _, sup in d['types'] if sup != 'object'} | ({'object'} if d['types'] else set())

def conj(form):
    if form == [] or form is None: return []
    if form[0] == 'and': return [y for x in form[1:] for y in conj(x)]
    return [form]

# ------------------------------------------------------------------ names
RESERVED = {'s', 'w', 'objs', 'ds', 'op', 'pre', 'pa', 'task', 'dr'}
def var_name(v):
    x = re.sub(r'[^a-z0-9]', '', v.lstrip('?'))
    if not x or x in RESERVED or (x[0] in 're' and x[1:].isdigit()) or x[0].isdigit(): x = 'v' + x
    return x

# ------------------------------------------------------------------ translation
SOAR_ID = re.compile(r'^[a-z][0-9]+$')
def soar_name(x):
    """A name of one letter and digits (d1) reads as a Soar identifier, so it gets a hyphen (d-1)."""
    return x[0] + '-' + x[1:] if SOAR_ID.match(x) else x

def translate(dom_path, prob_path, task_name=None):
    d = read_domain(dom_path)
    gaps = []
    for p, args in d['predicates'].items():
        if not args and p not in PROPOSITIONS: gaps.append(f'nullary predicate ({p}) with no object and property in PROPOSITIONS')
    props = {p: PROPOSITIONS[p] for p, args in d['predicates'].items() if not args and p in PROPOSITIONS}
    def pobj(p):
        h, ty, _ = props[p]
        return {'obj': pvar(h), 'type': ty}
    def phas(p, value):
        h, _, q = props[p]
        return {'has': pvar(h), 'prop': q, 'cmp': 'eq', 'rhs': value}
    supers = {t for _, t in d['types']}            # types that have subtypes
    pf = parse(open(prob_path).read())
    pname = pf[1][1]
    objs = typed_list((section(pf, ':objects') or [None])[1:]) + d['constants']
    init = conj(['and'] + (section(pf, ':init') or [None, ])[1:])
    goal = conj(section(pf, ':goal')[1])
    ops, stmts = [], []
    for k, a in enumerate(d['actions'], 1):
        params = typed_list(a.get(':parameters', []))
        vmap = {p: var_name(p) for p, _ in params}
        if len(set(vmap.values())) != len(vmap): gaps.append(f'{a["name"]}: parameter names collide after renaming')
        for p, t in params:
            if t in supers and any(sup == t for _, sup in d['types']):
                gaps.append(f'{a["name"]}: parameter {p} has type {t}, which has subtypes')
        def arg(x):
            return {'var': vmap[x]} if x.startswith('?') else {'h': soar_name(x)}
        pre = []
        for lit in conj(a.get(':precondition')):
            if lit[0] == 'not' and isinstance(lit[1], list) and lit[1][0] == '=':
                pre.append({'distinct': [vmap[lit[1][1]], vmap[lit[1][2]]]})
            elif lit[0] in props:
                pre += [pobj(lit[0]), phas(lit[0], TRUE)]
            elif lit[0] == 'not' and isinstance(lit[1], list) and lit[1][0] in props:
                pre += [pobj(lit[1][0]), phas(lit[1][0], FALSE)]
            elif lit[0] in ('not', 'or', 'imply', 'exists', 'forall', 'when', '='):
                gaps.append(f'{a["name"]}: precondition construct {lit[0]}')
            else:
                pre.append({'rel': lit[0], 'args': [arg(x) for x in lit[1:]]})
        pos_pre = {(l[0], tuple(l[1:])) for l in conj(a.get(':precondition')) if l[0] not in ('not', 'or', 'imply', 'exists', 'forall', 'when', '=')}
        dels, adds, bind, upd = [], [], [], []
        for lit in conj(a.get(':effect')):
            pl = lit[0] if lit[0] in props else (lit[1][0] if lit[0] == 'not' and isinstance(lit[1], list) and lit[1][0] in props else None)
            if pl:
                h, _, q = props[pl]
                if pobj(pl) not in bind: bind.append(pobj(pl))
                upd.append({'update': pvar(h), 'prop': q, 'rhs': FALSE if lit[0] == 'not' else TRUE})
                continue
            if lit[0] == 'not':
                at = lit[1]
                if (at[0], tuple(at[1:])) not in pos_pre:
                    gaps.append(f'{a["name"]}: deletes ({" ".join(at)}), which is not a precondition')
                dels.append({'del': at[0], 'args': [arg(x) for x in at[1:]]})
            elif lit[0] in ('forall', 'when', 'increase', 'decrease', 'assign'):
                gaps.append(f'{a["name"]}: effect construct {lit[0]}')
            else:
                adds.append({'add': lit[0], 'args': [arg(x) for x in lit[1:]]})
        report = [{'text': a['name'] + ' '}] + sum([[{'handle': vmap[p]}, {'text': ' '}] for p, _ in params], [])[:-1]
        stmts.append((k, f'PDDL action {a["name"]}'))
        ops.append(dict(name=a['name'], params=[(vmap[p], t) for p, t in params], stmts=[k],
                        pre=pre, bind=bind, effects=dels + adds + upd, report=report))
    gatoms = []
    for lit in goal:
        if lit[0] in props:
            gatoms += [x for x in (pobj(lit[0]), phas(lit[0], TRUE)) if x not in gatoms]
            continue
        if lit[0] in ('not', 'or', 'imply', 'exists', 'forall', 'when'):
            gaps.append(f'goal construct {lit[0]}')
        else:
            gatoms.append({'rel': lit[0], 'args': [{'h': soar_name(x)} for x in lit[1:]]})
    stmts.append((len(stmts) + 1, f'PDDL goal of problem {pname}'))
    name = task_name or ('pddl-' + re.sub(r'[^a-z0-9]+', '-', d['name']).strip('-'))
    t = dict(name=name, title=f'{d["name"]} / {pname} (PDDL)', folder=f'pddl/{name}', lean_name=re.sub(r'-(.)', lambda m: m.group(1).upper(), name),
             statements=stmts, world_rels=sorted(d['predicates']), ops=ops,
             goal={'ex': gatoms}, goalStmts=[len(stmts)], assumptions=[])
    pobjs = {}
    for p, (h, ty, q) in props.items():
        pobjs.setdefault(h, (ty, {}))[1][q] = 'true' if [p] in init else 'false'
    world = world_text(objs, [x for x in init if x[0] not in props], pobjs)
    return t, world, pname, gaps, d

def world_text(objs, init, pobjs={}):
    ids = {o: k for k, (o, _) in enumerate(objs, 1)}
    # The Rosie world-file reader drops one trailing '1' from every name (a word-sense marker), so each name,
    # category and predicate is written with a '1' appended and reads back unchanged.
    blocks = [f'objid {ids[o]}\ncategory {t}1\nname {soar_name(o)}1' for o, t in objs]
    for k, (h, (ty, ps)) in enumerate(pobjs.items(), len(objs) + 1):
        blocks.append(f'objid {k}\ncategory {ty}1\nname {h}1\n' + '\n'.join(f'{q} {v}' for q, v in ps.items()))
    rels = {}
    for at in init:
        if at[0] == '=': continue
        rels.setdefault(at[0], []).append(' '.join(str(ids[x]) for x in at[1:]))
    blocks += [f'predicate {r}1\n' + '\n'.join(ts) for r, ts in sorted(rels.items()) if all(ts)]
    return '\n\n'.join(blocks) + '\n'

def spec_source(t):
    def r(x): return repr(x)
    lines = ['# WorldSpec description generated from PDDL by Tasks/pddl/tools/pddl2ws.py (literal translation).',
             'from worldspec_py import *', 'TASK = task(']
    for k in ('name', 'title', 'folder', 'lean_name', 'statements', 'world_rels', 'ops', 'goal', 'goalStmts', 'assumptions'):
        lines.append(f'  {k}={r(t[k])},')
    lines.append(')')
    return '\n'.join(lines) + '\n'

LOADER = '''# Loads the shared Soar library from the repository (Soar/soar-library), then the task rules.
# The path assumes this folder sits at Tasks/pddl/<domain>/soar/<problem>.
pushd "../../../../../Soar/soar-library"
source soar-library.soar
popd
source {rules}
'''

def main():
    dom, prob, out = sys.argv[1:4]
    tname = sys.argv[sys.argv.index('--task') + 1] if '--task' in sys.argv else None
    t, world, pname, gaps, d = translate(dom, prob, tname)
    if gaps:
        print('REFUSED: ' + '; '.join(sorted(set(gaps))))
        sys.exit(2)
    o = Path(out); o.mkdir(parents=True, exist_ok=True)
    (o / f'{t["name"]}-spec.py').write_text(spec_source(t))
    (o / f'init-{pname}.world').write_text(world)
    (o / f'{t["name"]}.soar').write_text(LOADER.format(rules=f'{t["name"]}-rules.soar'))
    print(f'OK {t["name"]} {pname}: {len(t["ops"])} operators, {len(t["world_rels"])} relations')

if __name__ == '__main__':
    try: main()
    except Refuse as e:
        print('REFUSED: ' + str(e)); sys.exit(2)
