"""Shared generator pieces for world-convention tasks (agent-world / selection-world conventions).
Layout switch: LAYOUT='flat' (all properties on the object) or 'static' (properties listed in STATIC under ^static)."""
import re, sys, os, json

def _negated_spans(lhs):
    """Spans of negated conditions (-( ... ) and -{ ... }) in a rule's LHS."""
    spans, k = [], 0
    while True:
        m = re.search(r'-\s*([({])', lhs[k:])
        if not m: return spans
        start = k + m.start(); open_ch = m.group(1); close_ch = ')' if open_ch == '(' else '}'
        depth, q = 0, k + m.start(1)
        while q < len(lhs):
            if lhs[q] == open_ch: depth += 1
            elif lhs[q] == close_ch:
                depth -= 1
                if depth == 0: break
            q += 1
        spans.append((start, q + 1)); k = q + 1

def literalize_handles(text):
    """Default (15 Nov 2026): every object-handle value test on a rule's LHS gets $, so a chunk keeps the handle as a constant.
    Without it chunking turns handles into variables with no inequality between them, and a chunk learned for one object can fire for
    another (Hanoi: a chunk for moving a disc onto peg P2 also matched the goal peg P3, see FINDING-chunking-overgeneral.md).
    Chunks then transfer only to the same named objects.
    Not inside a negated condition (Soar 9.6.50: "bad test type in hash_test ... cannot recover" when it builds a justification), and
    not inside a { ... } test that also holds a relational test, such as { <> <bh> <dh> } (Soar 9.6.50: segmentation fault); this
    function only adds $ to plain `object-handle <h>` tests, so it never writes the second form."""
    out = []
    for part in re.split(r'(?m)(?=^sp \{)', text):
        if not part.startswith('sp {') or '-->' not in part: out.append(part); continue
        lhs, rhs = part.split('-->', 1)
        spans = _negated_spans(lhs)
        def lit(m):
            if any(a <= m.start() < b for a, b in spans): return m.group(0)
            return f'{m.group(1)} $ {m.group(2)}'
        lhs = re.sub(r'([\^.]object-handle) (<[\w-]+>)', lit, lhs)
        out.append(lhs + '-->' + rhs)
    return ''.join(out)

DEFAULT_OUTPUT = {'command': 'perform-action', 'nameAttribute': 'name', 'arguments': ['argument1', 'argument2', 'argument3'],
                  'done': ['interrupted', 'complete', 'success'], 'success': ['success'], 'error': ['error', 'failure'],
                  'applied': 'complete'}   # the same fields as WorldSpec's OutputForm (spec_backend.py)

_EFFECT = re.compile(r'\^io\.output-link\.perform-action <pa>\)\n(\s*)\(<pa> \^name (\S+) \^status complete((?: \^argument\d+ [^ )]+)*) -\^effect-applied true\)')

def apply_output_form(text, task, form):
    """Rewrite the environment-effect rules for a declared output form and add the environment's output map
    (World-Conventions L10-018). The rules are generated in the default perform-action form; this changes only the
    command they read from the output-link, so the default output is unchanged byte for byte."""
    f = dict(DEFAULT_OUTPUT, **form)
    attrs = f['arguments']
    def sub(m):
        ind, name, args = m.group(1), m.group(2), m.group(3)
        def arg(a):
            k = int(a.group(1))
            return f"^{attrs[k - 1] if k <= len(attrs) else f'argument{k}'} "
        args = re.sub(r'\^argument(\d+) ', arg, args)
        if f.get('command'):
            return f"^io.output-link.{f['command']} <pa>)\n{ind}(<pa> ^{f['nameAttribute']} {name} ^status {f['applied']}{args} -^effect-applied true)"
        return f"^io.output-link.{name} <pa>)\n{ind}(<pa> ^status {f['applied']}{args} -^effect-applied true)"
    text, n = _EFFECT.subn(sub, text)
    assert n or 'perform-action' not in text, f'{task}: environment-effect rules not in the expected form'
    body = ([f"^command {f['command']}", f"^name-attribute {f['nameAttribute']}"] if f.get('command')
            else ['^command-is-action-handle true'])
    body += [f'^argument{k} {a}' for k, a in enumerate(attrs, 1)]
    body += [f"^done-status {' '.join(f['done'])}", f"^success-status {' '.join(f['success'])}", f"^error-status {' '.join(f['error'])}"]
    rule = (f"\n## How the environment takes actions on the output-link (World-Conventions L10-018).\n"
            f"sp {{{task}*elaborate*environment-output-map\n   (state <s> ^problem-space.name {task} ^superstate nil)\n-->\n"
            f"   (<s> ^environment-output-map <m>)\n   (<m> " + '\n        '.join(body) + ")\n}\n")
    return text + rule

def _top_conds(lhs):
    """Spans (start, end) of the top-level positive conditions of a left-hand side (negated ones skipped)."""
    out, i, depth, start, neg = [], 0, 0, None, False
    while i < len(lhs):
        c = lhs[i]
        if c in '({':
            if depth == 0: start, neg = i, (i > 0 and lhs[i-1] == '-')
            depth += 1
        elif c in ')}':
            depth -= 1
            if depth == 0 and start is not None:
                if not neg and lhs[start] == '(': out.append((start, i + 1))
                start = None
        i += 1
    return out

def drop_redundant_object_tests(text):
    """World-Conventions L3-104, as familygen's Prod.dropRedundantObjectTests: in each rule, a test
    (<w> ^objects.object <x>) is left out when <x> is also bound as an argument of a relation (<w> ^rel <r>)
    (<r> ^argumentN <x>) in the same rule. Top-level positive conditions only."""
    def fix(m):
        name, body = m.group(1), m.group(2)
        if '-->' not in body: return m.group(0)
        lhs, rhs = body.split('-->', 1)
        spans = _top_conds(lhs)
        conds = [lhs[a:b] for a, b in spans]
        idv = lambda c: (re.match(r'\((?:state\s+)?(<[^>]+>)', c) or [None, None])[1]
        worlds = {idv(c) for c in conds if re.search(r'\^objects\.object\s', c)}
        red = {}
        for w in worlds:
            vals = lambda c, pat: [v for a, vs in re.findall(pat + r'((?:\s+(?:\{[^}]*\}|<[^>]+>))+)', c)
                                   for v in re.findall(r'\{[^}]*\}|<[^>]+>', vs) if v.startswith('<')]
            rels = {v for c in conds if idv(c) == w for v in vals(c, r'\^(?!objects\b)([\w-]+)')}
            red[w] = {x for c in conds if idv(c) in rels for x in vals(c, r'\^(argument\d+)')}
        if not any(red.values()): return m.group(0)
        new = lhs
        for (a, b) in reversed(spans):
            c = lhs[a:b]; w = idv(c)
            if w not in red or not red[w]: continue
            def strip(mm):
                vs = [v for v in re.findall(r'\{[^}]*\}|<[^>]+>', mm.group(2)) if v not in red[w]]
                return (mm.group(1) + '^objects.object ' + ' '.join(vs)) if vs else ''
            c2 = re.sub(r'(\s*)\^objects\.object((?:\s+(?:\{[^}]*\}|<[^>]+>))+)', strip, c)
            if c2 == c: continue
            # the attribute removed was the first on its identifier: the next one moves up beside it
            c2 = re.sub(r'^\((<[^>]+>)\s*\n\s*\^', r'(\1 ^', c2)
            if re.fullmatch(r'\((?:state\s+)?<[^>]+>\s*\)', c2):
                # nothing left: drop the condition and the line it stood on
                ls = new.rfind('\n', 0, a); new = new[:ls if ls >= 0 else a] + new[b:]
            else:
                new = new[:a] + c2 + new[b:]
        return f'sp {{{name}\n{new}-->{rhs}}}'
    return re.sub(r'(?ms)^sp \{(\S+)\n(.*?)^\}', fix, text)

def match_hints(text):
    """Matching hints for learned rules (World-Conventions L11-009, L3-095), as WorldSpec's matchHints: production
    optimize-attribute for ^object (the objects of the initial world) and for every attribute a rule adds to the world
    <w> (relations and the like; its number of values in the initialize rule, at least 2). Read from the rules
    themselves, so every generator built on Task gets them; they change condition order only, never what matches."""
    rules = re.findall(r'(?ms)^sp \{(\S+)\n(.*?)^\}', text)
    init = next((b for n, b in rules if '*apply*initialize-' in n), '')
    m = re.search(r'\^object ((?:<[^>]+>\s*)+)', init)
    n_obj = len(re.findall(r'<[^>]+>', m.group(1))) if m else 0
    names, count = [], {}
    for n, b in rules:
        rhs = b.split('-->', 1)[1] if '-->' in b else ''
        for clause in re.findall(r'\(<w>([^()]*)\)', rhs):
            for a, vals in re.findall(r'\^([\w.-]+)((?:\s+[^\s^]+)+)', clause):
                vs = [v for v in vals.split() if v not in ('+', '-')]
                if '-' in vals.split() or not vs or a == 'objects': continue
                if a not in names: names.append(a)
                if b is init: count[a] = count.get(a, 0) + len(vs)
    if not n_obj and not names: return ''
    out = '## Matching hints for learned rules (World-Conventions L3-095, L11-009): many-valued attributes, sized from the initial world.\n'
    out += f'production optimize-attribute object {max(n_obj, 2)}\n'
    for a in names: out += f'production optimize-attribute {a} {max(count.get(a, 0), 2)}\n'
    return out + '\n'

def finish(text):
    """L3-104 and L11-009 for generators that write rules without Task (the English-world gen.py files): leave out
    redundant object tests, then put the matching hints after the leading comment lines."""
    t = drop_redundant_object_tests(text)
    import static_pass   # L7-028 candidate: static objects and shared relations
    t = static_pass.mark_static({'rules': t})[0]['rules']
    m = re.match(r'(?:#[^\n]*\n|\s*\n)*', t)
    return t[:m.end()] + match_hints(t) + t[m.end():]

class Task:
    def __init__(s, name, desc, layout='flat', static=(), strategy='iterative-deepening', derived=(), literal_handles=True):
        s.name, s.desc, s.layout, s.static, s.strategy = name, desc, layout, set(static), strategy
        s.literal_handles = literal_handles   # $ on every object-handle test (chunks keep handles as constants; see literalize_handles)
        s.derived = list(derived)   # object attributes computed by elaborations (i-support): never copied into a look-ahead world
        s.parts = []
        s.objects = []     # (handle, {attr:val}, extra_rhs_lines)
        s.desired = []     # (handle, {attr:val})
        s.init_extra = []  # extra RHS lines in the initialize operator
        # Phases and loops (World-Conventions L8-026 to L8-030): phases = list of desired lists (s.desired unused then);
        # loop_start = index of the phase the last one returns to (None: no loop); termination = a desired list (the
        # state's ^termination-desireds); repeat_count = passes to run (^repeat-count).
        s.phases, s.loop_start, s.termination, s.repeat_count = [], None, [], None
        # Output form the environment takes (World-Conventions L10-018); None = the default ^perform-action form,
        # written exactly as before. Also from the environment variable WG_OUTPUT (JSON), so every gen_*.py takes it.
        s.output = json.loads(os.environ['WG_OUTPUT']) if os.environ.get('WG_OUTPUT') else None
        # Matching hints for learned rules (World-Conventions L11-009): production optimize-attribute lines after the
        # header (match_hints). False leaves them out, to compare runs.
        s.match_hints = True
        # Static objects and shared relations (World-Conventions L7-028, candidate 26 Nov 2026; static_pass.py).
        # False leaves them out (for a library without static sharing).
        s.static_sharing = True
        # Fixed properties under ^fixed (L7-029 candidate, 26 Nov 2026) only with look-ahead: None decides from the
        # proposals (static_pass.has_lookahead), True or False says so.
        s.lookahead = None
    def add(s, text): s.parts.append(text.strip('\n') + '\n')
    # ---- attribute access
    def lhs_attr(s, attr, val, in_static=None):
        st = (attr in s.static) if in_static is None else in_static
        return f'^static.{attr} {val}' if (s.layout == 'static' and st) else f'^{attr} {val}'
    def check_mutable(s, attr):
        assert not (s.layout == 'static' and attr in s.static), f'{s.name}: rule writes static attribute {attr}'
    def obj_rhs(s, var, handle, props):
        flat = {a: v for a, v in props.items() if not (s.layout == 'static' and a in s.static)}
        stat = {a: v for a, v in props.items() if s.layout == 'static' and a in s.static}
        out = f'   ({var} ^object-handle {handle} ^anchored true ' + ' '.join(f'^{a} {v}' for a, v in flat.items())
        stv = var[:-1] + '-st>'
        if stat: out += f' ^static {stv}'
        out = out.rstrip() + ')\n'
        if stat: out += f'   ({stv} ' + ' '.join(f'^{a} {v}' for a, v in stat.items()) + ')\n'
        return out
    # ---- fixed parts
    def header(s):
        return s.desc.rstrip() + '\n'
    def init(s):
        n = s.name
        vars_ = ' '.join(f'<o-{h}>' for h, _, _ in s.objects)
        t = f'''
sp {{{n}*propose*initialize-{n}
   (state <s> ^superstate nil ^world <w> -^name)
-->
   (<s> ^operator <o> + >)
   (<o> ^name initialize-{n} ^task-operator false)
}}

sp {{{n}*apply*initialize-{n}
   (state <s> ^operator.name initialize-{n} ^world <w>)
   (<w> ^objects <objs>)
-->
   (<s> ^name {n} ^desireds <ds>)
   (<objs> ^object {vars_})
'''
        for h, props, _ in s.objects: t += s.obj_rhs(f'<o-{h}>', h, props)
        if not s.phases:
            t += s.desireds_rhs('<ds>', 'd', s.desired)
        else:
            # Phases (World-Conventions L8-026 to L8-029): a chain of desireds linked by ^next-desireds; the first is
            # the state's ^desireds; a loop closes the chain back to s.loop_start (^loop-start true).
            names = ['<ds>'] + [f'<ph{k}>' for k in range(2, len(s.phases) + 1)]
            for k, (dv, ph) in enumerate(zip(names, s.phases)):
                t += s.desireds_rhs(dv, f'p{k + 1}d', ph)
                nxt = names[k + 1] if k + 1 < len(names) else (names[s.loop_start] if s.loop_start is not None else None)
                if nxt: t += f'   ({dv} ^next-desireds {nxt})\n'
            if s.loop_start is not None: t += f'   ({names[s.loop_start]} ^loop-start true)\n'
        if s.termination:
            t += '   (<s> ^termination-desireds <tds>)\n' + s.desireds_rhs('<tds>', 'td', s.termination)
        if s.repeat_count is not None:
            t += f'   (<s> ^repeat-count {s.repeat_count})\n'
        for l in s.init_extra: t += '   ' + l + '\n'
        t += f'   (log 1 (crlf) |Initialize {n}.|)\n}}\n'
        return t
    def desireds_rhs(s, var, pre, desired):
        """RHS lines of one desireds structure (desired-count and its desired objects or relations)."""
        t = f'   ({var} ^desired-count {len(desired)} ' + ' '.join(f'^desired <{pre}{i}>' for i in range(1, len(desired)+1)) + ')\n'
        if pre == 'd': pre = 'd'
        for i, dd in enumerate(desired, 1):
            d = f'{pre}{i}'
            if dd[0] == 'rel':   # ('rel', name, handle1, handle2, ...): desired relation, canonical relation-object shape
                _, rn, *hs = dd
                t += f'   (<{d}> ^{rn} <{d}-r>)\n   (<{d}-r> ' + ' '.join(f'^argument{k} <{d}-a{k}>' for k in range(1, len(hs)+1)) + ')\n'
                for k, hh in enumerate(hs, 1): t += f'   (<{d}-a{k}> ^object-handle {hh})\n'
            else:
                h, props = dd
                t += f'   (<{d}> ^object <{d}-o>)\n   (<{d}-o> ^object-handle {h} ' + ' '.join(f'^{a} {v}' for a, v in props.items()) + ')\n'
        return t
    def space_and_flags(s):
        n = s.name
        if s.strategy == 'iterative-deepening':
            fl = '^mea-operator-selection true'   # other flags take the library defaults
        else:
            fl = '^mea-operator-selection true'
        dc = ''.join(' ^dont-copy-object-attribute ' + a for a in s.derived)
        return f'''
sp {{{n}*elaborate*problem-space
   (state <s> ^name {n})
-->
   (<s> ^problem-space <p>)
   (<p> ^name {n}{''.join(' ^copy-relation '+r for r in getattr(s,'copy_relations',[]))}{dc})
}}

sp {{{n}*elaborate*problem-space*mea-substate
   (state <s> ^impasse no-change ^attribute operator ^superstate <ss>)
   (<ss> ^problem-space.name {n} ^operator <so>)
   (<so> ^task-operator true -^pre-conditions-satisfied true)
-->
   (<s> ^problem-space <p>)
   (<p> ^name {n}{dc})
}}

{s.flags_comment_line()}sp {{{n}*elaborate*flags
   (state <s> ^superstate nil ^name {n})
-->
   (<s> ^flag-override <f>)
   (<f> {fl}{s.extra_flags if hasattr(s,'extra_flags') else ''})
}}
'''
    def flags_comment_line(s):
        # A comment the task gives for its flag settings (e.g. how a search setting was measured); without one, the
        # convention pass writes the group comment (L3-012).
        c = getattr(s, 'flags_comment', None)
        return f'## {c}\n' if c else ''
    def achievement(s):
        n = s.name
        t = ''
        STATIC_NEG = ('  -{(<w> ^objects.object <ob>)\n    (<ob> ^object-handle <h> ^static.<a> <v>)}\n' if s.layout == 'static' else '')
        t += f'''
## Achievement of object-property desireds (supplied by the task).
sp {{{n}*elaborate*state*achieved*object-property
   (state <s> ^desireds <ds> ^world <w>)
   (<ds> ^desired <d>)
   (<d> ^object <do>)
   (<do> ^object-handle <h> ^{{ <> object-handle <a> }} <v>)
   (<w> ^anchored-world true ^objects.object <ob>)
   (<ob> ^object-handle <h> ^<a> <v>)
-->
   (<ds> ^achieved <d>)
}}

sp {{{n}*elaborate*state*unachieved*object-property
   (state <s> ^desireds <ds> ^world <w>)
   (<ds> ^desired <d>)
   (<d> ^object <do>)
   (<do> ^object-handle <h> ^{{ <> object-handle <a> }} <v>)
   (<w> ^anchored-world true)
  -{{(<w> ^objects.object <ob>)
    (<ob> ^object-handle <h> ^<a> <v>)}}
{STATIC_NEG}-->
   (<ds> ^unachieved <d>)
}}
'''
        if s.layout == 'static':
            t += f'''
## Layout static: desired properties may also be held under ^static.
sp {{{n}*elaborate*state*achieved*object-property*static
   (state <s> ^desireds <ds> ^world <w>)
   (<ds> ^desired <d>)
   (<d> ^object <do>)
   (<do> ^object-handle <h> ^{{ <> object-handle <a> }} <v>)
   (<w> ^anchored-world true ^objects.object <ob>)
   (<ob> ^object-handle <h> ^static.<a> <v>)
-->
   (<ds> ^achieved <d>)
}}
'''
            s.static_achieved_warning = True
        return t
    def achievement_relation(s, nargs):
        n = s.name
        a = ' '.join(f'^argument{k}.object-handle <h{k}>' for k in range(1, nargs+1))
        return f'''
## Achievement of relation desireds ({nargs} arguments): the world has the relation between objects with these handles.
sp {{{n}*elaborate*state*achieved*relation{nargs}
   (state <s> ^desireds <ds> ^world <w>)
   (<ds> ^desired <d>)
   (<d> ^<rel> <dr>)
   (<dr> {a})
   (<w> ^anchored-world true ^<rel> <wr>)
   (<wr> {a})
-->
   (<ds> ^achieved <d>)
}}

sp {{{n}*elaborate*state*unachieved*relation{nargs}
   (state <s> ^desireds <ds> ^world <w>)
   (<ds> ^desired <d>)
   (<d> ^<rel> <dr>)
   (<dr> {a})
   (<w> ^anchored-world true)
  -{{(<w> ^<rel> <wr>)
    (<wr> {a})}}
-->
   (<ds> ^unachieved <d>)
}}
'''
    def copy_relation(s, rel):
        """Look-ahead substates copy only the relations the library names (on, above, in, ...); any other canonical relation
        needs its own copy rule, generated here (same shape as the library's relation-copy rules)."""
        return f'''
## Copy relation {rel} into look-ahead world copies (the library copies only on/above/in/holding-object/future-event).
sp {{{s.name}*elaborate*default-state-copy-relation*{rel}
   (state <s> ^deep-copy-world true
              ^world <new-world>)
   (<new-world> ^duplicate-of <old-world>
                ^objects.object <on-new> <object-new>)
   (<on-new> ^object-handle <location-handle>)
   (<object-new> ^object-handle <object-handle>)
   (<old-world> ^{rel} <relation-object>)
   (<relation-object> ^argument2 <cl-object>
                      ^argument1 <object-value>)
   (<cl-object> ^object-handle <location-handle>)
   (<object-value> ^object-handle <object-handle>)
-->
   (<new-world> ^{rel} <new-relation-object>)
   (<new-relation-object> ^duplicate-of <relation-object>
                          ^argument2 <on-new>
                          ^argument1 <object-new>)
}}
'''
    def copy_desired_relation(s, rel):
        return f'''
## Copy desired relation {rel} into look-ahead desireds (the library copies only on/in/controlled-by/above desired relations).
sp {{{s.name}*elaborate*copy-desired-relation*{rel}
   (state <s> ^name evaluate-operator
              ^desireds <desireds>)
   (<desireds> ^duplicate-of <duplicate-desireds>
               ^desired <desired>)
   (<desired> ^duplicate-of <duplicate-desired>)
   (<duplicate-desired> ^{rel} <value>)
   (<value> ^argument1.object-handle <argument1-handle>
            ^argument2.object-handle <argument2-handle>)
-->
   (<desired> ^{rel} <value1>)
   (<value1> ^argument1.object-handle <argument1-handle>
             ^argument2.object-handle <argument2-handle>)}}
'''
    def propose(s, opname, lhs, args, attrs='', pre_count=0, extra_rhs=''):
        n = s.name
        argtxt = ' '.join(f'^argument{i} {a}' for i, a in enumerate(args, 1))
        return f'''
sp {{{n}*propose*{opname}
   (state <s> ^problem-space.name {n} ^flags.mea-operator-selection true ^world <w> ^desireds <ds>)
   (<w> ^anchored-world true ^objects <objs>)
{lhs.rstrip()}
   (<ds> ^unachieved-desireds true)
-->
   (<s> ^operator <op> +)
   (<op> ^name {opname.split('*')[0]} ^task-operator true ^action-handle {opname.split('*')[0]} {argtxt} ^argument-count {len(args)} ^desireds <pre>{(' ' + attrs) if attrs else ''})
   (<pre> ^desired-count {pre_count})
}}
'''
    def text(s):
        t = s.header() + s.init() + s.space_and_flags() + '\n' + ''.join(s.parts)
        if s.termination:   # the task's achievement rules also mark the termination desireds (L8-028)
            t = t.replace('(state <s> ^desireds <ds> ^world <w>)', '(state <s> ^<< desireds termination-desireds >> <ds> ^world <w>)')
        if s.output: t = apply_output_form(t, s.name, s.output)
        if s.literal_handles: t = literalize_handles(t)
        import convpass   # 18 Nov 2026 conventions: problem-space test (L3-005), group comments (L3-012)
        t = convpass.apply(t)
        import check_derived
        _, bad = check_derived.check(t)
        assert not bad, f'{s.name}: derived object attributes not declared (Task(derived=[...])): {bad}'
        t = drop_redundant_object_tests(t)
        if s.static_sharing and s.layout == 'flat':
            import static_pass
            t = static_pass.mark_static({'rules': t}, s.lookahead)[0]['rules']
        h = s.header()
        if s.match_hints and t.startswith(h): t = h + match_hints(t) + t[len(h):]
        return t
