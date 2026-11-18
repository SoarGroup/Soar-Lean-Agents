"""Shared generator pieces for world-convention tasks (agent-world / selection-world conventions).
Layout switch: LAYOUT='flat' (all properties on the object) or 'static' (properties listed in STATIC under ^static)."""
import re, sys

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

class Task:
    def __init__(s, name, desc, layout='flat', static=(), strategy='iterative-deepening', derived=(), literal_handles=True):
        s.name, s.desc, s.layout, s.static, s.strategy = name, desc, layout, set(static), strategy
        s.literal_handles = literal_handles   # $ on every object-handle test (chunks keep handles as constants; see literalize_handles)
        s.derived = list(derived)   # object attributes computed by elaborations (i-support): never copied into a look-ahead world
        s.parts = []
        s.objects = []     # (handle, {attr:val}, extra_rhs_lines)
        s.desired = []     # (handle, {attr:val})
        s.init_extra = []  # extra RHS lines in the initialize operator
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
        t += f'   (<ds> ^desired-count {len(s.desired)} ' + ' '.join(f'^desired <d{i}>' for i in range(1, len(s.desired)+1)) + ')\n'
        for i, dd in enumerate(s.desired, 1):
            if dd[0] == 'rel':   # ('rel', name, handle1, handle2, ...): desired relation, canonical relation-object shape
                _, rn, *hs = dd
                t += f'   (<d{i}> ^{rn} <d{i}-r>)\n   (<d{i}-r> ' + ' '.join(f'^argument{k} <d{i}-a{k}>' for k in range(1, len(hs)+1)) + ')\n'
                for k, hh in enumerate(hs, 1): t += f'   (<d{i}-a{k}> ^object-handle {hh})\n'
            else:
                h, props = dd
                t += f'   (<d{i}> ^object <d{i}-o>)\n   (<d{i}-o> ^object-handle {h} ' + ' '.join(f'^{a} {v}' for a, v in props.items()) + ')\n'
        for l in s.init_extra: t += '   ' + l + '\n'
        t += f'   (log 1 (crlf) |Initialize {n}.|)\n}}\n'
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

sp {{{n}*elaborate*flags
   (state <s> ^superstate nil ^name {n})
-->
   (<s> ^flag-override <f>)
   (<f> {fl}{s.extra_flags if hasattr(s,'extra_flags') else ''})
}}
'''
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
   (<ds> ^unachieved <any-unachieved>)
-->
   (<s> ^operator <op> +)
   (<op> ^name {opname.split('*')[0]} ^task-operator true ^action-handle {opname.split('*')[0]} {argtxt} ^argument-count {len(args)} ^desireds <pre>{(' ' + attrs) if attrs else ''})
   (<pre> ^desired-count {pre_count})
}}
'''
    def text(s):
        t = s.header() + s.init() + s.space_and_flags() + '\n' + ''.join(s.parts)
        if s.literal_handles: t = literalize_handles(t)
        import check_derived
        _, bad = check_derived.check(t)
        assert not bad, f'{s.name}: derived object attributes not declared (Task(derived=[...])): {bad}'
        return t
