#!/usr/bin/env python3
"""Rewrite world-convention task rules to the ^static layout (World-Conventions L7-017 to L7-022).

usage: staticize.py SRC_DIR DST_DIR INIT_FILE [RULE_FILE ...]

The static set is computed, not declared (L7-022): every attribute that the initialization gives a world
object, minus ^object-handle and ^anchored, minus every attribute that any rule other than the
initialization writes. Then:
  * the initialization puts the static attributes of each object under a new ^static identifier;
  * every condition on a world object that tests a static attribute tests ^static.<attr> instead;
  * a rule that writes a static attribute is an error (L7-018).
World-object variables in a rule are those bound as the value of ^object under a world's ^objects
(or ^objects.object), the values of --world-link state attributes, and the values of the roles of
index structures declared with --index ATTR:ROLE[+ROLE] (e.g. cell-info:cell, cand-info:cand+tuple).
Writes count only when their target is a world-object variable, so index elaborations do not make
an object attribute mutable.
All other files in SRC_DIR are copied unchanged. A report of the static set is printed.
"""
import sys, os, re, shutil, argparse

TOK = re.compile(r'"[^"]*"|\|[^|]*\||<<|>>|<=>|<>|<=|>=|-->|[(){}]|\^[^\s(){}]+|[^\s(){}]+')


def skip_str(text, i):
    """Index just past the |...| string that starts at text[i] (backslash escapes allowed)."""
    j = i + 1
    while text[j] != '|':
        j += 2 if text[j] == '\\' else 1
    return j + 1


def rules(text):
    """Yield (start, end) spans of sp {...} blocks."""
    for m in re.finditer(r'\bsp\s*\{', text):
        i, depth = m.end(), 1
        while depth:
            c = text[i]
            if c == '#':
                i = text.index('\n', i)
                continue
            if c == '|':
                i = skip_str(text, i)
                continue
            elif c == '{':
                depth += 1
            elif c == '}':
                depth -= 1
            i += 1
        yield m.start(), i


def split_rule(body):
    k = body.index('-->')
    return body[:k], body[k:]


def clauses(lhs):
    """Yield (start, end, id) for each innermost (id ^attr ...) clause in the LHS text."""
    out = []
    stack = []
    i = 0
    while i < len(lhs):
        c = lhs[i]
        if c == '#':
            j = lhs.find('\n', i)
            i = len(lhs) if j < 0 else j
            continue
        if c == '|':
            i = skip_str(lhs, i)
            continue
        if c == '(':
            stack.append(i)
        elif c == ')' and stack:
            s = stack.pop()
            inner = lhs[s + 1:i]
            if '(' not in inner:
                m = re.match(r'\s*(?:state\s+)?(<[^>\s]+>)', inner)
                if m:
                    out.append((s, i + 1, m.group(1)))
        i += 1
    return out


def attr_tests(clause_text):
    """Yield (pos, attr) of each ^attr token (first segment of dotted attrs) in a clause."""
    for m in re.finditer(r'\^([A-Za-z0-9_\-*]+)', clause_text):
        yield m.start(), m.group(1)


def rhs_clauses(rhs):
    """Yield (id, text) of each top-level (id ...) action in an RHS (strings removed)."""
    rhs = re.sub(r'\|(?:\\.|[^|\\])*\|', '', rhs)
    depth, start = 0, None
    for i, c in enumerate(rhs):
        if c == '(':
            if depth == 0: start = i
            depth += 1
        elif c == ')':
            depth -= 1
            if depth == 0:
                m = re.match(r'\(\s*(<[^>\s]+>)', rhs[start:i + 1])
                if m: yield m.group(1), rhs[start:i + 1]


def world_vars(lhs, index):
    """Variables bound to world objects in this LHS."""
    W = set()
    objs = set()
    for m in re.finditer(r'\^objects\s+(<[^>\s]+>)', lhs):
        objs.add(m.group(1))
    for m in re.finditer(r'\^objects\.object\s+(?:\{\s*)?(<[^>\s]+>)', lhs):
        W.add(m.group(1))
    for s, e, idv in clauses(lhs):
        txt = lhs[s:e]
        if idv in objs:
            for m in re.finditer(r'\^object\s+(?:\{\s*)?(<[^>\s]+>)', txt):
                W.add(m.group(1))
            # several values: ^object <a> ^object <b> handled above; also "^object <a> <b>"
    # index structures: (<s> ^cell-info <ci>) (<ci> ^cell <c> ^cand <x>)
    idx = {}
    for m in re.finditer(r'\^([\w-]+)\s+(?:\{\s*)?(<[^>\s]+>)', lhs):
        if m.group(1) in index:
            idx[m.group(2)] = m.group(1)
    for m in re.finditer(r'\^([\w-]+)\.([\w-]+)\s+(?:\{\s*)?(<[^>\s]+>)', lhs):
        if m.group(1) in index and m.group(2) in index[m.group(1)]:
            W.add(m.group(3))
    for s, e, idv in clauses(lhs):
        if idv in idx:
            roles = index[idx[idv]]
            for m in re.finditer(r'\^([\w-]+)\s+(?:\{\s*)?(<[^>\s]+>)', lhs[s:e]):
                if m.group(1) in roles:
                    W.add(m.group(2))
    for m in re.finditer(r'\^puzzle\s+(<[^>\s]+>)', lhs):
        W.add(m.group(1))
    return W


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('src'); ap.add_argument('dst'); ap.add_argument('init'); ap.add_argument('files', nargs='*')
    ap.add_argument('--index', default='cell-info:cell+cand,cand-info:cand+tuple,tuple-info:tuple+cand')
    ap.add_argument('--world-link', default='puzzle', help='state attributes whose value is a world object')
    o = ap.parse_args()
    index = {}
    for p in o.index.split(','):
        a, r = p.split(':'); index[a] = set(r.split('+'))
    src = {f: open(os.path.join(o.src, f), encoding='utf8').read() for f in [o.init] + o.files}

    # ---- objects created by the initialization
    init = src[o.init]
    obj_attrs = set()
    for s, e in rules(init):
        lhs, rhs = split_rule(init[s:e])
        for m in re.finditer(r'\((<[^>\s]+>)((?:[^()])*?\^object-handle(?:[^()])*?)\)', rhs):
            if re.search(r'\^anchored\s', m.group(2)):
                obj_attrs |= set(re.findall(r'\^([\w-]+)', m.group(2)))
    obj_attrs -= {'object-handle', 'anchored'}

    # ---- attributes written by any other rule (any RHS outside the initialization's object clauses)
    written = set()
    for f, text in src.items():
        for s, e in rules(text):
            lhs, rhs = split_rule(text[s:e])
            if f == o.init and '^object-handle' in rhs:
                continue
            rhs = re.sub(r'\|(?:\\.|[^|\\])*\|', '', rhs)
            W = world_vars(lhs, index)
            for v, t in rhs_clauses(rhs):
                if v in W:
                    written |= set(re.findall(r'\^([\w-]+)', t))
    static = sorted(obj_attrs - written)
    mutable = sorted(obj_attrs & written)
    print('static:', ' '.join(static))
    print('mutable:', ' '.join(mutable))
    S = set(static)

    os.makedirs(o.dst, exist_ok=True)
    for f in os.listdir(o.src):
        p = os.path.join(o.src, f)
        if os.path.isfile(p) and f not in src:
            shutil.copy2(p, os.path.join(o.dst, f))

    changed = 0
    for f, text in src.items():
        out, last = [], 0
        for s, e in rules(text):
            body = text[s:e]
            k = body.index('-->')
            lhs, rhs = body[:k], body[k:]
            if f == o.init and '^object-handle' in rhs:
                def mv(m):
                    v, inner = m.group(1), m.group(2)
                    keep, stat = [], []
                    for am in re.finditer(r'\^([\w-]+)\s+([^\s^()]+)', inner):
                        (stat if am.group(1) in S else keep).append(f'^{am.group(1)} {am.group(2)}')
                    if not stat or not re.search(r'\^anchored\s', inner):
                        return m.group(0)
                    sv = v[:-1] + '-st>'
                    pad = '\n        '
                    return f'({v} ' + pad.join(keep + [f'^static {sv}']) + f')\n   ({sv} ' + pad.join(stat) + ')'
                rhs = re.sub(r'\((<[^>\s]+>)((?:[^()])*?\^object-handle(?:[^()])*?)\)', mv, rhs)
            else:
                W = world_vars(lhs, index)
                for v, t in rhs_clauses(rhs):
                    if v in W:
                        for a in re.findall(r'\^([\w-]+)', t):
                            assert a not in S, f'{f}: a rule writes static attribute {a} (L7-018)'
                edits = []
                for cs, ce, idv in clauses(lhs):
                    if idv not in W:
                        continue
                    for pos, a in attr_tests(lhs[cs:ce]):
                        if a in S:
                            edits.append(cs + pos)
                for p in sorted(edits, reverse=True):
                    lhs = lhs[:p] + '^static.' + lhs[p + 1:]
                changed += len(edits)
            out.append(text[last:s]); out.append(lhs + rhs); last = e
        out.append(text[last:])
        open(os.path.join(o.dst, f), 'w', encoding='utf8').write(''.join(out))
    print('condition tests rewritten:', changed)


if __name__ == '__main__':
    main()
