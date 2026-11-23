"""convpass.py: a final pass over generated Soar rules that applies conventions decided on 18 Nov 2026
(World-Conventions-v6 / Soar-Conventions, level-based IDs):

  L3-005  every rule tests, in its first condition, the name of its state or of the problem space the state
          belongs to; rules that fire in every state holding a world (world and desired elaborations, internal
          operator applications) included. Exceptions: rules that create a state's name or problem space
          (initialization; the problem-space elaborations, including the one for an operator no-change substate).
  L3-012  each rule, or each group of rules for the same operator or purpose, is preceded by an English
          #-comment.
  L3-039 / L3-083  agents that learn with RL do not put an indifferent preference in their proposals.

Usage (inside a generator):   text = convpass.apply(text, rl=False)
         or on files:          python3 convpass.py [--rl] FILE.soar ...   (rewrites the files in place)
         on agent folders:     python3 convpass.py --agent DIR             (all .soar files of one agent together)
The pass is idempotent: running it twice changes nothing more.
"""
import re
import sys
import os

RULE = re.compile(r'(?m)^[ \t]*sp\s*\{')


def split_rules(text):
    """[(prefix_text, rule_text)]; rule_text runs from 'sp {' to its closing brace. A trailing piece has rule None."""
    out, i = [], 0
    while True:
        m = RULE.search(text, i)
        if not m:
            out.append((text[i:], None))
            return out
        j, depth = m.end(), 1
        while depth and j < len(text):
            c = text[j]
            if c == '|':
                k = j + 1
                while k < len(text) and text[k] != '|':
                    k += 1
                j = k
            elif c == '{':
                depth += 1
            elif c == '}':
                depth -= 1
            j += 1
        out.append((text[i:m.start()], text[m.start():j]))
        i = j


def rule_name(r):
    return r.split('{', 1)[1].split()[0]


def first_state_cond(r):
    return re.search(r'\(state\s+(<[\w-]+>)([^)]*)\)', r)


def op_names_proposed(r):
    """Operator names a proposal rule creates: (<o> ^name X ...) for every <o> with ^operator <o> + on the RHS."""
    lhs, _, rhs = r.partition('-->')
    names = set()
    for v in re.findall(r'\^operator\s+(<[\w-]+>)\s*\+', rhs):
        for m in re.finditer(r'\(' + re.escape(v) + r'\s[^)]*?\^name\s+([^\s)]+)', rhs):
            names.add(m.group(1))
    return names


def op_names_applied(r):
    lhs = r.partition('-->')[0]
    m = re.search(r'\^operator\.name\s+(<<[^>]*>>|[^\s)]+)', lhs)
    if m:
        return set(m.group(1).strip('<> ').split()) if m.group(1).startswith('<<') else {m.group(1)}
    st = first_state_cond(r)
    if not st:
        return set()
    m = re.search(r'\^operator\s+(<[\w-]+>)(?!\s*\+)', st.group(2))
    if not m:
        return set()
    v = m.group(1)
    m2 = re.search(r'\(' + re.escape(v) + r'\s[^)]*?\^name\s+(\{[^}]*\}|<<[^>]*>>|[^\s)]+)', lhs)
    if not m2:
        return set()
    t = m2.group(1)
    found = re.findall(r'<<([^>]*)>>', t)
    if found:
        return set(found[0].split())
    return {t} if not t.startswith('<') else set()


def ps_of(cond_text):
    m = re.search(r'\^problem-space\.name\s+(\{[^}]*\}|<<[^>]*>>|[^\s)]+)', cond_text)
    if not m:
        return None
    t = m.group(1)
    d = re.search(r'<<([^>]*)>>', t)
    if d:
        return set(d.group(1).split())
    if t.startswith('<') or t.startswith('{'):
        return None
    return {t}


def exempt(r):
    n = rule_name(r)
    st = first_state_cond(r)
    if not st:
        return True
    c = st.group(2)
    if re.search(r'\^name\s', c) or '^problem-space.name' in c:
        return True
    if '*initialize-' in n or '^impasse' in c or ('*elaborate*problem-space' in n) or re.search(r'\^operator\.name\s+initialize-', c):
        return True
    if re.fullmatch(r'\s*\^superstate(\.[\w-]+)?\s+<[\w-]+>\s*', c):
        return True   # passes structure from a superstate into substates of any problem space (e.g. ancestor worlds)
    if ':template' in r.split('(state', 1)[0]:
        return False
    return False


def add_ps(r, ps):
    st = first_state_cond(r)
    test = ps.pop() if len(ps) == 1 else '<< ' + ' '.join(sorted(ps)) + ' >>'
    return r[:st.end(1)] + f' ^problem-space.name {test}' + r[st.end(1):]


def describe(r):
    """A one-line English description of a rule from its structure (name fields, state, operator, changes)."""
    n = rule_name(r)
    f = n.split('*')
    task, func = f[0], (f[1] if len(f) > 1 else '')
    what = ' '.join(f[2:]).replace('-', ' ') if len(f) > 2 else ''
    st = first_state_cond(r)
    ps = ps_of(st.group(2)) if st else None
    where = f' in problem space {"/".join(sorted(ps))}' if ps else ''
    lhs, _, rhs = r.partition('-->')
    if func == 'propose':
        ops = sorted(op_names_proposed(r)) or [f[2] if len(f) > 2 else '?']
        return f'## Propose {" and ".join(ops)}{where} when its conditions below hold' + (f' ({" ".join(f[3:]).replace("-", " ")})' if len(f) > 3 else '') + '.'
    if func == 'apply':
        ops = sorted(op_names_applied(r)) or [f[2] if len(f) > 2 else '?']
        changes = sorted(set(re.findall(r'\^([\w|-]+)\s+<[\w-]+>\s+-', rhs)) | set(re.findall(r'\^([\w|-]+)\s+[^\s)]+\s+-\s', rhs)))
        detail = ' '.join(f[3:]).replace('-', ' ')
        txt = f'## Apply {" / ".join(ops)}{where}' + (f' ({detail})' if detail else '')
        if changes:
            txt += ': changes ' + ', '.join('^' + c for c in changes)
        return txt + '.'
    if func == 'elaborate':
        made = sorted(set(re.findall(r'\^([\w|.-]+)\s', rhs)) - {'name'})[:4]
        return f'## Elaborate {what}{where}' + (': adds ' + ', '.join('^' + m for m in made) if made else '') + '.'
    if func in ('compare', 'select'):
        pref = '>' if re.search(r'\^operator\s+<[\w-]+>\s*>\s*[)\n]', rhs) else '<' if re.search(r'\^operator\s+<[\w-]+>\s*<\s*[)\n]', rhs) else ''
        kind = {'>': 'best', '<': 'worst'}.get(pref, 'preference')
        return f'## Search control{where}: {what} ({kind}).'
    if func == 'rl':
        return f'## RL rule template for {what}{where}: one numeric-indifferent value per state-operator pair.'
    return f'## {func.capitalize()} {what}{where}.'.replace('  ', ' ')


def has_comment(prefix):
    return bool(re.search(r'#[^\n]*\n[ \t]*\Z', prefix))


def group_key(r):
    f = rule_name(r).split('*')
    return f[2] if len(f) > 2 else rule_name(r)


def apply_files(texts, rl=False):
    """texts: {fname: text} for one agent (all its rule files). Returns {fname: new_text}, notes."""
    rules = [(fn, r) for fn, t in texts.items() for _, r in split_rules(t) if r]
    # problem space of each operator, from its proposals
    op_ps = {}
    task_ps = set()
    for fn, r in rules:
        st = first_state_cond(r)
        if not st:
            continue
        if '*elaborate*problem-space' in rule_name(r) and '^impasse' not in st.group(2):
            m = re.search(r'\(<[\w-]+>\s+\^name\s+([^\s)]+)', r.partition('-->')[2])
            if m:
                task_ps.add(m.group(1))
        p = ps_of(st.group(2))
        if p and rule_name(r).split('*')[1:2] == ['propose']:
            for o in op_names_proposed(r):
                op_ps.setdefault(o, set()).update(p)
    notes = []
    out = {}
    for fn, t in texts.items():
        parts = split_rules(t)
        new, prev = [], None
        for pre, r in parts:
            if r is None:
                new.append(pre)
                continue
            n = rule_name(r)
            func = n.split('*')[1] if '*' in n else ''
            if not exempt(r):
                ps = None
                if func == 'apply':
                    ops = op_names_applied(r)
                    s = set()
                    for o in ops:
                        s |= op_ps.get(o, set())
                    if not s:
                        allps = set().union(*op_ps.values()) if op_ps else set()
                        for o in ops:
                            s |= {p for p in allps if o.endswith('-' + p)}
                    if not s and re.search(r'\^(world|desireds)\b', r.partition('-->')[0]) and task_ps:
                        s = set(task_ps)
                    ps = s or None
                elif func in ('elaborate', 'compare', 'select', 'rl') or func not in ('propose',):
                    lhs = r.partition('-->')[0]
                    if re.search(r'\^(world|desireds|superstate\.ancestor-world)\b', lhs) and task_ps:
                        ps = set(task_ps)
                    elif re.search(r'\^operator\s+<[\w-]+>\s*\+', lhs):
                        s = set()
                        for o in re.findall(r'\^name\s+([\w-]+)', lhs):
                            s |= op_ps.get(o, set())
                        ps = s or (set(task_ps) if task_ps else None)
                if not ps and '^superstate nil' in first_state_cond(r).group(2) and task_ps:
                    ps = set(task_ps)
                if ps:
                    r = add_ps(r, set(ps))
                else:
                    notes.append(f'{fn}: {n}: no problem space found')
            if rl and func == 'propose':
                r = re.sub(r'(\^operator\s+<[\w-]+>\s*\+)\s*=(?=[\s)])', r'\1', r)
            g = group_key(r)
            if not has_comment(pre) and g != prev:
                ind = re.match(r'[ \t]*', pre.split('\n')[-1]).group(0)
                head = pre[:len(pre) - len(pre.split('\n')[-1])]
                pre = head + ind + describe(r) + '\n' + ind
            prev = g
            new.append(pre + r)
        out[fn] = ''.join(new)
    return out, notes


def apply(text, rl=False):
    return apply_files({'_': text}, rl)[0]['_']


if __name__ == '__main__':
    args = sys.argv[1:]
    rl = '--rl' in args
    args = [a for a in args if a != '--rl']
    if args and args[0] == '--agent':
        for d in args[1:]:
            fs = {}
            for root, _, files in os.walk(d):
                for f in files:
                    if f.endswith('.soar'):
                        fs[os.path.join(root, f)] = open(os.path.join(root, f)).read()
            res, notes = apply_files(fs, rl or any(x == 'rl' or x.startswith('hrl') for x in os.path.basename(d.rstrip('/')).split('-')))
            for p, t in res.items():
                if t != fs[p]:
                    open(p, 'w').write(t)
            for n in notes:
                print('NOTE', n)
    else:
        fs = {p: open(p).read() for p in args}
        res, notes = apply_files(fs, rl)
        for p, t in res.items():
            if t != fs[p]:
                open(p, 'w').write(t)
        for n in notes:
            print('NOTE', n)
