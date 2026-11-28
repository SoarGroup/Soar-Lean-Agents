"""Type as attribute (World-Conventions L7-029, v2.49 candidate, JL 27 Nov 2026).

A world's typed objects are also held under their type: (<objs> ^block <b1> <b2> ^table <t>), besides
(<objs> ^object <b1> <b2> <t>), which the library derives from the type sets. Objects keep their ^type (JL 27 Nov 2026);
an object with no type is held under ^object only. For generators that write Soar rules directly (wg.py: Rosie, worldgen, English-world agents), the rules of
one agent are rewritten as the last step:
  * the initialize rule, and any rule that adds objects to an ^objects set, put each object under its type (read from
    the object's own ^type in the same rule; ^object when it has none);
  * a condition ^objects.object <x>, or (<objs> ^object <x>) on an ^objects value, becomes ^objects.T <x> when the rule
    tests (<x> ^type T) with a constant T, finds <x> by the constant handle of an object of type T, or finds it through
    argument K of an operator named N (^argumentK.object-handle, or an output command's ^argumentK handle) whose
    proposals give argument K the one type T; a ^type test so replaced is left out (an object under ^objects.T has type
    T). An untyped object the rule also binds as a relation argument loses its object-set test (L3-104). Otherwise the
    condition stays ^objects.object <x>: ^object holds every object, typed ones included (the library adds each typed
    object to it), so no rule needs a variable attribute, which Soar cannot index.
WorldSpec (spec_backend.py, Compile.lean) and familygen (Family/Task.lean typeAttr) write the same form from their
descriptions. Needs the library with type-attribute object sets (v2.49 candidate)."""
import re

ARGTYPE = {}   # (operator, argument) -> type, set by apply()
GROUP = re.compile(r'\((state\s+)?(<[^\s()<>]+>)(\s[^()]*)\)')
VAR = r'<[^\s()<>{}]+>'
VAL = r'(?:\{[^{}]*\}|' + VAR + r')'


def _rules(text):
    """(name, body start, body end) of each sp {...}: the body runs from after the name's line to the brace that
    closes the rule, wherever it stands (a rule may end with ')}' on its last condition or action line)."""
    out = []
    for m in re.finditer(r'(?m)^sp \{(\S+)\s*\n', text):
        depth, q, bar = 1, m.start() + 4, False
        while q < len(text):
            ch = text[q]
            if ch == '|': bar = not bar
            elif not bar:
                if ch == '{': depth += 1
                elif ch == '}':
                    depth -= 1
                    if depth == 0: break
            q += 1
        out.append((m.group(1), m.end(), q))
    return out


def _bound(v):
    """The variable a value binds: <x>, or the last variable of { <> <y> <x> }."""
    if v.startswith('{'):
        vs = re.findall(VAR, v)
        return vs[-1] if vs else None
    return v


def _types(side):
    """Variable -> constant type, from (<v> ... ^type T ...) groups."""
    out = {}
    for g in GROUP.finditer(side):
        m = re.search(r'\^type\s+(?:\$\s+)?([^\s()<>{}|$]+)(?=[\s)])', g.group(3) + ' ')
        if m: out[g.group(2)] = m.group(1)
    return out


def _handle_types(side, htype):
    """Variable -> type, for variables found by the constant handle of an initial object."""
    out = {}
    for g in GROUP.finditer(side):
        m = re.search(r'\^object-handle\s+(?:\$\s+)?([^\s()<>{}|$]+)(?=[\s)])', g.group(3) + ' ')
        if m and m.group(1) in htype: out[g.group(2)] = htype[m.group(1)]
    return out


def _initial_types(text):
    """handle -> type of the initial world's objects (from every initialize rule)."""
    out = {}
    for name, a, b in _rules(text):
        if '*apply*initialize-' not in name or '-->' not in text[a:b]: continue
        rhs = text[a:b].split('-->', 1)[1]
        for g in GROUP.finditer(rhs):
            h = re.search(r'\^object-handle\s+([^\s()<>{}|]+)(?=[\s)])', g.group(3) + ' ')
            t = re.search(r'\^type\s+([^\s()<>{}|]+)(?=[\s)])', g.group(3) + ' ')
            if h and t and not t.group(1).startswith('<'): out[h.group(1)] = t.group(1)
    return out


def _arg_types(text):
    """(operator name, argument number) -> type, from the proposals: a rule that proposes an operator named N with
    ^argumentK <x> and tests (<x> ^type T). An argument proposed with more than one type, or with none, gets none."""
    seen = {}
    for name, a, b in _rules(text):
        body = text[a:b]
        if '-->' not in body: continue
        lhs, rhs = body.split('-->', 1)
        tl = _types(lhs)
        for g in GROUP.finditer(rhs):
            m = re.search(r'\^name\s+([^\s()<>{}|]+)(?=[\s)])', g.group(3) + ' ')
            if not m: continue
            for k, x in re.findall(r'\^argument(\d+)\s+(<[^\s()<>]+>)', g.group(3)):
                seen.setdefault((m.group(1), k), set()).add(tl.get(x, '?'))
    return {key: next(iter(ts)) for key, ts in seen.items() if len(ts) == 1 and '?' not in ts}


def _operator_arg_types(lhs, argtype):
    """Variable -> type for objects a rule finds through the handle (or value) of a task operator's argument."""
    out, ops = {}, {}
    for g in GROUP.finditer(lhs):
        m = re.search(r'\^name\s+([^\s()<>{}|]+)(?=[\s)])', g.group(3) + ' ')
        if m: ops[g.group(2)] = (m.group(1), g.group(3))
    hvar = {}
    for g in GROUP.finditer(lhs):
        h = re.search(r'\^object-handle\s+(?:\$\s+)?(<[^\s()<>]+>)', g.group(3))
        if h: hvar.setdefault(h.group(1), g.group(2))
    for o, (n, body) in ops.items():
        for k, h in re.findall(r'\^argument(\d+)\.object-handle\s+(?:\$\s+)?(<[^\s()<>]+>)', body):
            if (n, k) in argtype and h in hvar: out[hvar[h]] = argtype[(n, k)]
        for k, x in re.findall(r'\^argument(\d+)\s+(<[^\s()<>]+>)', body):
            if (n, k) in argtype: out[hvar.get(x, x)] = argtype[(n, k)]   # an object, or the handle of one (a command)
    return out


def _relation_args(masked):
    """Variables bound as an argument of a relation object (a group with ^argumentN and no ^name)."""
    out = set()
    for g in GROUP.finditer(masked):
        if re.search(r'\^name\s', g.group(3)): continue
        out |= set(re.findall(r'\^argument\d+\s+(<[^\s()<>]+>)', g.group(3)))
    return out


def _rewrite(side, typ, objsets, tvar, relargs=()):
    """^objects.object v.. and (<objs> ^object v..) -> one attribute per value, named by its type. An untyped value
    that the rule also binds as a relation argument loses its object-set test (L3-104)."""
    typed = {}

    def name(v):
        x = _bound(v)
        if x and x in typ:
            typed[x] = typ[x]; return typ[x]
        if x and x in relargs and not v.startswith('{'): return None
        return tvar(x)

    def dotted(m):
        vals = re.findall(VAL, m.group(2))
        parts = [(name(v), v) for v in vals]
        return ' '.join(f'{m.group(1)}objects.{n} {v}' for n, v in parts if n is not None)
    side = re.sub(r'(\^(?:[a-z][\w-]*\.)*)objects\.object((?:\s+' + VAL + r')+)', dotted, side)

    def grp(m):
        if m.group(2) not in objsets: return m.group(0)
        def ob(mm):
            vals = re.findall(VAL, mm.group(1))
            parts = []
            for v in vals:
                t = name(v)
                if t is None: continue
                if parts and parts[-1][0] == t: parts[-1][1].append(v)
                else: parts.append((t, [v]))
            return ' '.join(f'^{t} ' + ' '.join(vs) for t, vs in parts)
        body = re.sub(r'\^object((?:\s+' + VAL + r')+)', ob, m.group(3))
        if not body.strip(): return '\x00'
        return '(' + (m.group(1) or '') + m.group(2) + body + ')'
    return GROUP.sub(grp, side), typed


def _drop_type_tests(text, typed):
    """Leave out ^type T on variables now typed by their ^objects attribute; a condition left empty goes. Applied to
    the conditions of one scope only (no negated condition inside it)."""
    def grp(m):
        v = m.group(2)
        if v not in typed or m.group(1): return m.group(0)
        body = re.sub(r'\s*\^type\s+' + re.escape(typed[v]) + r'(?=[\s)]|$)', '', m.group(3))
        if body == m.group(3): return m.group(0)
        if not body.strip(): return '\x00'
        body = re.sub(r'^\s*\n\s*', ' ', body)   # the attribute removed was the first: the next one moves up
        return '(' + v + body + ')'
    out = GROUP.sub(grp, text)
    out = re.sub(r'\n[ \t]*\x00[ \t]*(?=\n|$)', '', out)
    return out.replace('\x00', '')


def _scope(text, htype, objsets, tvar, outer):
    """One scope: the conditions outside negations, with each negated conjunction -{ ... } a scope of its own (it sees
    this scope's types) and each negated condition -( ... ) rewritten with this scope's types but giving none and
    losing no ^type test (as familygen's taScope)."""
    import wg
    spans = wg._negated_spans(text)
    masked = text
    for a, b in reversed(spans): masked = masked[:a] + ' ' * (b - a) + masked[b:]
    tt = _types(masked)
    types = {**(_operator_arg_types(masked, ARGTYPE) if not outer else {}), **_handle_types(masked, htype), **tt, **outer}
    relargs = _relation_args(masked)
    pieces, typed_all, k = [], {}, 0
    for a, b in spans + [(len(text), len(text))]:
        seg, typed = _rewrite(text[k:a], types, objsets, tvar, relargs)
        typed_all.update(typed); pieces.append(['top', seg])
        if a < b:
            sp_ = text[a:b]
            if re.match(r'-\s*\{', sp_):
                i = sp_.index('{')
                pieces.append(['neg', sp_[:i + 1] + _scope(sp_[i + 1:-1], htype, objsets, tvar, types) + '}'])
            else:
                pieces.append(['neg', _rewrite(sp_, types, objsets, tvar)[0]])
        k = b
    drop = {x: t for x, t in typed_all.items() if tt.get(x) == t and types.get(x) == t}
    return ''.join(_drop_type_tests(seg, drop) if kind == 'top' else seg for kind, seg in pieces)


def apply(text):
    """Rewrite one agent's rules (all files joined, or one file) to type-attribute object sets."""
    htype = _initial_types(text)
    global ARGTYPE
    ARGTYPE = _arg_types(text)
    out, pos = [], 0
    for name, a, b in _rules(text):
        body = text[a:b]
        if '-->' not in body: continue
        lhs, rhs = body.split('-->', 1)
        used = set(re.findall(VAR, body))
        names = {}

        def tvar(x):   # type not known: ^objects.object, which holds every object (L7-029, 27 Nov 2026)
            return 'object'
        objsets = set(re.findall(r'\^(?:[a-z][\w-]*\.)*objects\s+(' + VAR + ')', lhs + rhs))
        lhs2 = _scope(lhs, htype, objsets, tvar, {})
        import wg
        masked = lhs
        for x0, x1 in reversed(wg._negated_spans(lhs)): masked = masked[:x0] + ' ' * (x1 - x0) + masked[x1:]
        tr = {**_handle_types(masked, htype), **_types(masked), **_types(rhs)}
        rhs2, _ = _rewrite(rhs, tr, objsets, lambda x: 'object')
        out.append(text[pos:a] + lhs2 + '-->' + rhs2); pos = b
    out.append(text[pos:])
    return ''.join(out)

