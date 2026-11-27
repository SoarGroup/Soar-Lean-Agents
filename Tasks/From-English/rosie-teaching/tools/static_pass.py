"""Static objects and shared relations from the rules themselves (World-Conventions L7-028, candidate 26 Nov 2026).

For generators that write Soar rules directly (wg.py: Rosie, worldgen, English-world agents; the same analysis as
familygen's Variant.markStatic), the rules of one agent are read and:
  * an object of the initial world is static when no rule other than the initialize rule writes or removes an
    attribute on an object of its type (a write on an object variable whose type the rule does not test counts for
    every type, so then nothing is static); the task object is never static (goal and phase marks are elaborated on it);
  * a relation of the initial world is shared when no rule other than the initialize rule adds or removes it on a world
    or changes one of its relation objects, the library does not copy it itself (on, above, in), and every argument of
    every initial tuple is a static object.
The initialize rule then gives each static object ^static true, and the problem-space rule declares each shared
relation with ^share-relation (in place of ^copy-relation); a task-specific copy rule for a shared relation is removed.
WorldSpec computes the same from its description (spec_backend.static_info, Compile.lean Task.staticInfo).
Needs the library candidate with static sharing (v2.48 candidate, 26 Nov 2026)."""
import re

LIB_COPIED = {'on', 'above', 'in'}
NOT_RELATIONS = {'objects', 'anchored-world', 'real', 'duplicate-of', 'copy-map', 'stamp', 'parent-stamp', 'local-version',
                 'versioned-tag', 'versioned-operator', 'look-ahead-steps', 'parent-steps', 'room-name', 'anchored',
                 'counted-operator', 'applied-count'}

_TOK = re.compile(r'<<|>>|<>|<=>|<=|>=|\^[^\s()<>{}]+|<[^\s<>()]+>|\|[^|]*\||[(){}]|[^\s(){}]+')


def _positive(lhs):
    """The left-hand side without its negated conditions (-( ... ) and -{ ... }): only positive tests bind or type."""
    import wg
    for a, b in reversed(wg._negated_spans(lhs)): lhs = lhs[:a] + ' ' * (b - a) + lhs[b:]
    return lhs


def rules(text):
    """(name, lhs, rhs, start, end) of each sp {...} in text; lhs without its negated conditions."""
    out = []
    for m in re.finditer(r'(?ms)^sp \{(\S+)\s*\n(.*?)^\}', text):
        body = m.group(2)
        if '-->' not in body: continue
        lhs, rhs = body.split('-->', 1)
        out.append((m.group(1), _positive(lhs), rhs, m.start(), m.end()))
    return out


def triples(block):
    """(id, attr, value) for every attribute test or action in block; dotted paths get fresh intermediate variables.
    Values are variables, constants, or None (for a { } or << >> test with no variable). A '-' after a value
    (removal) is read as part of the action, like '+'."""
    toks = _TOK.findall(block)
    out, i, fresh = [], 0, [0]
    def new():
        fresh[0] += 1; return f'<#{fresh[0]}>'
    while i < len(toks):
        if toks[i] != '(':
            i += 1; continue
        j = i + 1
        if j < len(toks) and toks[j] == 'state': j += 1
        if j >= len(toks) or not toks[j].startswith('<') or toks[j] in ('<<', '<>', '<=', '<=>'):
            i += 1; continue            # a function call such as (write ...) or (+ a b)
        ident, k = toks[j], j + 1
        attr_path = None
        while k < len(toks) and toks[k] != ')':
            t = toks[k]
            if t == '(':                # nested function value, such as (+ <a> <b>): skip to its close
                if attr_path is not None: out.append((attr_path[0], attr_path[1], None))
                d = 0
                while k < len(toks):
                    if toks[k] == '(': d += 1
                    elif toks[k] == ')':
                        d -= 1
                        if d == 0: break
                    k += 1
                k += 1; continue
            if t.startswith('^'):
                attr_path = t[1:].split('.'); k += 1
                cur = ident
                for a in attr_path[:-1]:
                    nv = new(); out.append((cur, a, nv)); cur = nv
                attr_path = (cur, attr_path[-1]); continue
            if attr_path is None: k += 1; continue
            if t == '{':
                d, vs = 0, []
                while k < len(toks):
                    if toks[k] == '{': d += 1
                    elif toks[k] == '}':
                        d -= 1
                        if d == 0: break
                    elif toks[k].startswith('<') and toks[k] not in ('<<', '<>', '<=', '<=>'): vs.append(toks[k])
                    k += 1
                out.append((attr_path[0], attr_path[1], vs[-1] if vs else None)); k += 1; continue
            if t == '<<':
                while k < len(toks) and toks[k] != '>>': k += 1
                out.append((attr_path[0], attr_path[1], None)); k += 1; continue
            if t in ('<>', '<', '<=', '>=', '<=>') and attr_path is not None and k + 1 < len(toks) and toks[k + 1] not in (')', '}'):
                out.append((attr_path[0], attr_path[1], None)); k += 2; continue   # a comparison test binds nothing
            if t in ('+', '-', '>', '=', '!', '~', '@', '&', '$') or t.startswith('-^'):
                if t.startswith('-^'):   # negated attribute test: not a binding
                    attr_path = None
                k += 1; continue
            out.append((attr_path[0], attr_path[1], t)); k += 1
        i += 1
    return out


def analyse(texts):
    """texts: the rule files of one agent. Returns (static handles, shared relations, report) or None when the
    agent has no recognizable initialize rule."""
    global _last_fixed
    _last_fixed = []
    init = None
    for f, t in texts.items():
        for r in rules(t):
            if '*apply*initialize-' in r[0] and re.search(r'\^object\b', r[2]) and 'object-handle' in r[2]:
                init = (f, r); break
        if init: break
    if not init: return None
    _, (iname, ilhs, irhs, _, _) = init
    tr = triples(irhs)
    objsets = {v for (i, a, v) in triples(ilhs) if a == 'objects' and v}
    objs = {v for (i, a, v) in tr if i in objsets and a == 'object' and v and v.startswith('<')}
    handle = {i: v for (i, a, v) in tr if a == 'object-handle' and i in objs}
    typ = {i: v for (i, a, v) in tr if a == 'type' and i in objs}
    lw = {v for (i, a, v) in triples(ilhs) if a == 'world'}
    rel_tuples = {}
    for (i, a, v) in tr:
        if i in lw and a not in NOT_RELATIONS and v and v.startswith('<'):
            args = [x for (i2, a2, x) in tr if i2 == v and re.fullmatch(r'argument\d+', a2)]
            rel_tuples.setdefault(a, []).append(args)
    htype = {handle[x]: typ[x] for x in objs if x in handle and x in typ}
    # operator argument types, from the proposals: (operator name, argument attribute) -> types
    argtype = {}
    for f, t in texts.items():
        for (name, lhs, rhs, _, _) in rules(t):
            lt, rt = triples(lhs), triples(rhs)
            ty = {}
            for (i, a, v) in lt:
                if a == 'type' and v and not v.startswith('<'): ty.setdefault(i, set()).add(v)
            for (o, a, n) in rt:
                if a != 'name' or not n or n.startswith('<'): continue
                for (o2, a2, x) in rt:
                    if o2 == o and re.fullmatch(r'argument\d+', a2):
                        argtype.setdefault((n, a2), set()).update(ty.get(x, {'?'}))
    mutable, any_untyped, written = set(), False, set()
    written_attr, desired_ids = set(), {v for (i, a, v) in tr if a == 'desired' and v}
    for f, t in texts.items():
        for (name, lhs, rhs, _, _) in rules(t):
            if name == iname: continue
            lt = triples(lhs)
            objv = {v for (i, a, v) in lt if v and (a == 'object' or re.fullmatch(r'argument\d+', a))}
            worldv = {v for (i, a, v) in lt if a == 'world' and v}
            relv = {v: a for (i, a, v) in lt if i in worldv and v and a not in NOT_RELATIONS}
            types = {}
            for (i, a, v) in lt:
                if a == 'type' and v and not v.startswith('<'): types.setdefault(i, set()).add(v)
            # an object found by a constant handle has that object's type
            for (i, a, v) in lt:
                if a == 'object-handle' and v and not v.startswith('<') and v in htype and i not in types:
                    types[i] = {htype[v]}; objv.add(i)
            # an object found by the handle of an operator's (or a command's) argument has that argument's type
            hvar = {v: i for (i, a, v) in lt if a == 'object-handle' and v and v.startswith('<')}
            names = {i: v for (i, a, v) in lt if a == 'name' and v and not v.startswith('<')}
            for (o, a, y) in lt:
                if o in names and y and re.fullmatch(r'argument\d+', a):
                    hs = [y] + [v for (i2, a2, v) in lt if i2 == y and a2 == 'object-handle']
                    for h in hs:
                        x = hvar.get(h)
                        if x and x != y and x not in types and (names[o], a) in argtype and '?' not in argtype[(names[o], a)]:
                            types[x] = set(argtype[(names[o], a)])
                            objv.add(x)
            rt = triples(rhs)
            objsv = {v for (i, a, v) in lt + rt if a == 'objects' and v}
            newobj = {v for (i, a, v) in rt if i in objsv and a == 'object' and v and v.startswith('<') and v not in objv}
            for (i, a, v) in rt:
                if i in objv and a not in ('duplicate-of',):
                    if i in types:
                        mutable |= types[i]
                        for ty in types[i]: written_attr.add((ty, a))
                    else: any_untyped = True
                if i in newobj:
                    nt = {x for (i2, a2, x) in rt if i2 == i and a2 == 'type' and x and not x.startswith('<')}
                    if not nt: any_untyped = True
                    for ty in nt: written_attr.add((ty, a)); mutable.add(ty)
                # properties a desired object tests stay flat (the library matches them by attribute)
                if a == 'desired' and v: desired_ids.add(v)
                if i in worldv and a not in NOT_RELATIONS: written.add(a)
                if i in relv: written.add(relv[i])
    if any_untyped:
        return set(), [], 'an object variable without a type test is written: nothing static'
    _last_fixed = _fixed_props(texts, tr, objs, typ, mutable, written_attr, desired_ids)
    static_vars = {x for x in objs if typ.get(x) not in mutable and typ.get(x) != 'task' and x in handle}
    static = {handle[x] for x in static_vars}
    shared = [r for r, tups in rel_tuples.items()
              if r not in written and r not in LIB_COPIED and all(all(x in static_vars for x in args) for args in tups)]
    return static, shared, f'{len(static)} static objects; shared relations: {" ".join(shared) or "none"}'


FIXED_MIN = 3                       # World-Conventions L7-022 (measured 26 Nov 2026)
LIB_FLAT = {'object-handle', 'type', 'anchored', 'static', 'fixed'}
_last_fixed = []


def _fixed_props(texts, tr, objs, typ, mutable, written_attr, desired_ids):
    """Fixed properties (World-Conventions L7-017 to L7-022, 26 Nov 2026; spec_backend.fixed_info, familygen
    Variant.markFixed): a type that has some property a rule other than the initialize rule writes, and at least
    FIXED_MIN constant-valued properties no such rule writes, keeps those under ^fixed; a property name is fixed on every
    type that has it or on none; library attributes and properties a desired object tests stay flat."""
    props = {}
    for x in objs:
        ty = typ.get(x)
        if ty is None: continue
        ps = props.setdefault(ty, {})
        for (i, a, v) in tr:
            if i == x and a not in LIB_FLAT: ps[a] = ps.get(a, True) and bool(v) and not v.startswith('<')
    dattrs = set()
    for t in texts.values():
        for r in rules(t):
            rt = triples(r[2])
            ids = desired_ids | {v for (i, a, v) in rt if a == 'desired' and v}
            dobj = {v for (i, a, v) in rt if i in ids and a == 'object' and v}
            dattrs |= {a for (i, a, v) in rt if i in dobj}
    blocked, block_all = _varattr_types(texts)
    if block_all: return []
    ok = lambda ty: ty in mutable and ty != 'task' and ty not in blocked
    isfixed = lambda ty, p: ok(ty) and (ty, p) not in written_attr and props[ty][p] and p not in dattrs
    names = []
    for ty, ps in props.items():
        for p in ps:
            if isfixed(ty, p) and p not in names: names.append(p)
    while True:
        keep = [p for p in names if all(isfixed(ty, p) for ty, ps in props.items() if p in ps)]
        keep = [p for p in keep if all(len([q for q in ps if q in keep]) >= FIXED_MIN for ty, ps in props.items() if p in ps)]
        if keep == names: return names
        names = keep


_VGROUP = re.compile(r'\((state\s+)?(<[^\s()<>]+>)(\s[^()]*)\)')
_NOT_OBJECT_ATTRS = {'operator', 'world', 'desireds', 'desired', 'achieved', 'unachieved', 'superstate', 'io',
                     'input-link', 'output-link', 'problem-space', 'objects', 'top-state', 'super-desireds', 'flags'}
_VATTR = re.compile(r'\^(<<|\{|<[^\s<>()]+>)')


def _varattr_types(texts):
    """Types whose properties a rule tests through an attribute that is not a constant: ^<a>, ^<< a b >> or ^{ ... }
    (World-Conventions L7-022): such a test does not see a property moved under ^fixed, so those types keep every
    property flat. When the tested object's type is not known, nothing is fixed, except on a desired object, or when each
    attribute variable is bound by an attribute test on a desired object (the achievement rules: the properties a
    desired object tests stay flat). Returns (blocked types, block all)."""
    blocked = set()
    for t in texts.values():
        for m in re.finditer(r'(?ms)^sp \{(\S+)\s*\n(.*?)^\}', t):
            body = m.group(2)
            if '-->' not in body or '*apply*initialize-' in m.group(1): continue
            lhs = body.split('-->', 1)[0]
            lt = triples(lhs)
            types = {}
            for (i, a, v) in lt:
                if a == 'type' and v and not v.startswith('<'): types.setdefault(i, set()).add(v)
            dids = {v for (i, a, v) in lt if a in ('desired', 'achieved', 'unachieved') and v}
            dobj = {v for (i, a, v) in lt if i in dids and a == 'object' and v}
            groups = [(g.group(2), g.group(3)) for g in _VGROUP.finditer(lhs) if not g.group(1)]
            dattr_vars = set()
            for var, b in groups:
                if var in dobj:
                    dattr_vars |= set(re.findall(r'<[^\s<>()]+>', ' '.join(re.findall(r'\^\{[^}]*\}|\^<[^\s<>()]+>', b))))
            notobj = {v for (i, a, v) in lt if v and a in _NOT_OBJECT_ATTRS}
            notobj |= {i for (i, a, v) in lt if a in ('name', 'task-operator', 'superstate', 'problem-space')}
            for var, b in groups:
                if var in dobj or var in notobj or not _VATTR.search(b): continue
                if var in types: blocked |= types[var]; continue
                avars = set(re.findall(r'<[^\s<>()]+>', ' '.join(re.findall(r'\^\{[^}]*\}|\^<[^\s<>()]+>', b))))
                if '^<<' in b or not avars or not avars <= dattr_vars: return blocked, True
    return blocked, False


_GROUP = re.compile(r'\((<[^\s()<>]+>)(\s[^()]*)\)')


def _fixed_text(t, iname, names, objtypes):
    """Rewrite one rule file: the initialize rule's object groups move fixed properties to a ^fixed group; every other
    rule's tests of a fixed property on an object variable (or through ^argumentN / ^object) become ^fixed.<p>."""
    alt = '|'.join(re.escape(n) for n in sorted(names, key=len, reverse=True))
    def init_group(m):
        var, body = m.group(1), m.group(2)
        if '^object-handle' not in body: return m.group(0)
        toks = re.findall(r'\^[^\s()]+|\|[^|]*\||[^\s()]+', body)
        flat, fx, k = [], [], 0
        while k < len(toks):
            a = toks[k]; vals = []
            k += 1
            while k < len(toks) and not toks[k].startswith('^'): vals.append(toks[k]); k += 1
            (fx if a[1:] in names else flat).append(' '.join([a] + vals))
        if not fx: return m.group(0)
        fv = var[:-1] + '-fx>'
        return f'({var} ' + ' '.join(flat + [f'^fixed {fv}']) + f')\n   ({fv} ' + ' '.join(fx) + ')'
    out, pos = [], 0
    for (name, _, _, st, en) in rules(t):
        body = t[st:en]
        if name == iname:
            a = body.index('-->')
            body = body[:a] + _GROUP.sub(init_group, body[a:])
        else:
            a = body.index('-->')
            lhs, rhs = body[:a], body[a:]
            objv = {v for (i, at, v) in triples(lhs) if v and v.startswith('<')
                    and (at == 'object' or re.fullmatch(r'argument\d+', at))}
            objv |= {i for (i, at, v) in triples(lhs) if at in ('object-handle',) or (at == 'type' and v in objtypes)}
            def grp(m):
                if m.group(1) not in objv: return m.group(0)
                return '(' + m.group(1) + re.sub(r'(-?)\^(' + alt + r')(?=[\s)])', r'\1^fixed.\2', m.group(2)) + ')'
            lhs = _GROUP.sub(grp, lhs)
            lhs = re.sub(r'([\^.](?:argument\d+|object))\.(' + alt + r')(?=[\s)])', r'\1.fixed.\2', lhs)
            body = lhs + rhs
        out.append(t[pos:st] + body); pos = en
    return ''.join(out) + t[pos:]


def _add_static(t, iname, handles):
    """^static true on each static object's group in the initialize rule."""
    for r in rules(t):
        if r[0] != iname: continue
        start, end = r[3], r[4]
        body = t[start:end]
        for h in handles:
            m = re.search(r'\((<[^>]+>)\s+\^object-handle\s+' + re.escape(h) + r'(?=[\s)])', body)
            if not m: continue
            d, q = 0, m.start()
            while q < len(body):
                if body[q] == '(': d += 1
                elif body[q] == ')':
                    d -= 1
                    if d == 0: break
                q += 1
            body = body[:q] + ' ^static true' + body[q:]
        return t[:start] + body + t[end:]
    return t


def has_lookahead(texts):
    """Look-ahead is possible unless every task operator is applied without a tie: all task-operator proposals are
    monotonic (the library applies those first), or every proposed task operator gets an indifferent preference
    (^operator <o> =, with or without a value, as RL templates and the families' indifferent rule give) from a rule
    that tests the operator by a constant name or by no name at all (a ^name <> exclusion covers nothing)."""
    rs = [r for t in texts.values() for r in rules(t)]
    props = [r for r in rs if '^task-operator true' in r[2] and re.search(r'\^operator <[^>]+> \+', r[2])]
    if not props: return True
    if all('^monotonic true' in r[2] for r in props): return False
    names = set()
    for r in props:
        names |= {v for (i, a, v) in triples(r[2]) if a == 'name' and v and not v.startswith('<')}
    covered, every = set(), False
    for (name, lhs, rhs, _, _) in rs:
        for o in re.findall(r'\^operator (<[^>]+>) =(?=[\s)])', rhs) + re.findall(r'\^operator (<[^>]+>) = -?[\d.]+', rhs):
            lt = triples(lhs)
            ns = {v for (i, a, v) in lt if i == o and a == 'name'}
            if re.search(re.escape(o) + r'[^()]*\^name <>', lhs): continue
            if not ns: every = True
            covered |= {v for v in ns if v and not v.startswith('<')}
    return not (every or names <= covered)


def mark_static(texts, lookahead=None):
    """Apply the marks to an agent's rule files (dict file -> text). Returns (new texts, report)."""
    res = analyse(texts)
    if not res: return texts, 'no initialize rule recognized'
    static, shared, rep = res
    if lookahead is None: lookahead = has_lookahead(texts)
    names = list(_last_fixed) if lookahead else []
    if names:
        iname0 = next(r[0] for t in texts.values() for r in rules(t) if '*apply*initialize-' in r[0] and 'object-handle' in r[2])
        objtypes = set()
        for t in texts.values():
            for r in rules(t):
                if r[0] == iname0: objtypes |= {v for (i, a, v) in triples(r[2]) if a == 'type' and v}
        texts = {f: _fixed_text(t, iname0, names, objtypes) for f, t in texts.items()}
        rep += f'; fixed properties: {" ".join(names)}'
    if not static: return texts, rep
    out = {}
    iname = next(r[0] for t in texts.values() for r in rules(t) if '*apply*initialize-' in r[0] and 'object-handle' in r[2])
    declared = False
    for f, t in texts.items():
        t = _add_static(t, iname, sorted(static, key=lambda h: -len(h)))
        for r in shared:
            # a task-specific copy rule for the relation goes; the declaration changes
            t = re.sub(r'(?ms)\n(?:##[^\n]*\n)*sp \{\S+\*elaborate\*default-state-copy-relation\*' + re.escape(r) + r'\s*\n.*?^\}\n', '\n', t)
            t, n = re.subn(r'\^copy-relation\s+' + re.escape(r) + r'(?=[\s)])', '^share-relation ' + r, t)
            if n: declared = True
        out[f] = t
    if shared and not declared:
        # no ^copy-relation to replace: add the declarations to the task's problem-space rule
        for f, t in out.items():
            m = re.search(r'(?ms)^sp \{\S+\*elaborate\*problem-space\s*\n.*?\(<p> \^name ([^\s)]+)', t)
            if m:
                k = m.end()
                out[f] = t[:k] + ''.join(f' ^share-relation {r}' for r in shared) + t[k:]
                break
    return out, rep
