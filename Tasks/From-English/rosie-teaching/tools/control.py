"""Search-control knowledge kept with a task's English statement, and selected for testing.

A task's English file (english-input.txt, task.md) may end with a section that starts with a line beginning
'Search control' (any heading level). Each item in it is one line:

    SC-<n> [<kind>]: <statement>

kind is one of: desired-order, operator-preference, evaluation, method.  The items augment the problem; they never
change it (initial state, legal moves, goal).  Generators and writers see the items only through this tool:

    select(path, spec)   -> list of (id, kind, text) for spec 'none' | 'all' | 'SC-1,SC-3'
    strip(path)          -> the file's text without the section (what a 'none' condition sees)
    text(path, spec)     -> the file's text with only the selected items

usage: python3 control.py FILE [none|all|SC-1,SC-2]   prints the text for that condition.
Written 22 November 2026 by Claude, supervised by John E. Laird.
"""
import re
import sys

KINDS = {'desired-order', 'operator-preference', 'evaluation', 'method'}
HEAD = re.compile(r'^\s*(#+\s*)?Search control\b', re.I)
ITEM = re.compile(r'^\s*(SC-\d+)\s*\[([a-z-]+)\]\s*:\s*(.+?)\s*$')


def _split(path):
    lines = open(path, encoding='utf-8').read().splitlines()
    for i, l in enumerate(lines):
        if HEAD.match(l):
            return lines[:i], lines[i:]
    return lines, []


def items(path):
    out = []
    for l in _split(path)[1]:
        m = ITEM.match(l)
        if m:
            if m.group(2) not in KINDS:
                raise ValueError(f'{path}: {m.group(1)} has unknown kind {m.group(2)}')
            out.append((m.group(1), m.group(2), m.group(3)))
    ids = [i for i, _, _ in out]
    if len(ids) != len(set(ids)):
        raise ValueError(f'{path}: duplicate control item IDs')
    return out


def select(path, spec='none'):
    spec = (spec or 'none').strip()
    allitems = items(path)
    if spec == 'none':
        return []
    if spec == 'all':
        return allitems
    want = [s.strip() for s in spec.split(',') if s.strip()]
    known = {i for i, _, _ in allitems}
    missing = [w for w in want if w not in known]
    if missing:
        raise ValueError(f'{path}: no control item {", ".join(missing)}')
    return [it for it in allitems if it[0] in want]


def strip(path):
    return '\n'.join(_split(path)[0]).rstrip() + '\n'


def text(path, spec='none'):
    chosen = select(path, spec)
    body = strip(path)
    if not chosen:
        return body
    head = _split(path)[1][0]
    return body + '\n' + head + '\n' + '\n'.join(f'  {i} [{k}]: {t}' for i, k, t in chosen) + '\n'


def tag(spec_items):
    """File-name tag for a selection: '' for none, '-sc1-sc3' for SC-1 and SC-3."""
    return ''.join('-' + i.lower().replace('-', '') for i, _, _ in spec_items)


if __name__ == '__main__':
    sys.stdout.write(text(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else 'none'))
