"""The stated length of a solution sets the look-ahead depth limit (World-Conventions L16-045, 24 Nov 2026).

A task's English may state the length of its solution ("The solution has twenty-four steps."). The statement can be wrong
(Rosie missionaries-and-cannibals says five; eleven are needed), so it is used only as a lower bound on how deep
iterative deepening may search: max-evaluation-depth = max(library default 12, stated length). Below the default
nothing is written. Without this, a task whose solution is longer than 12 steps and whose moves cannot be undone
commits moves chosen at the depth limit without a success in sight (8-men-on-a-raft: 0 of 3 seeds; with the limit
24, 3 of 3 in the optimal 24 moves).

    length(path) -> the stated number of steps, or None
    block(path, task) -> rule text for the rules file ('' when no statement or not above the default)
Written 24 November 2026 by Claude, supervised by John E. Laird."""
import re

DEFAULT = 12
WORDS = {w: i for i, w in enumerate('zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen '
                                     'fifteen sixteen seventeen eighteen nineteen twenty'.split())}
WORDS.update({'thirty': 30, 'forty': 40, 'fifty': 50})
STATEMENT = re.compile(r'The solution has ([a-z-]+|\d+) steps?', re.I)

def _number(s):
    s = s.lower()
    if s.isdigit(): return int(s)
    parts = s.split('-')
    if all(p in WORDS for p in parts): return sum(WORDS[p] for p in parts)
    return None

def length(path):
    m = STATEMENT.search(open(path, encoding='utf-8').read())
    return _number(m.group(1)) if m else None

def block(path, task):
    n = length(path)
    if n is None or n <= DEFAULT: return ''
    return f'''
## Look-ahead depth limit from the stated solution length (World-Conventions L16-045): "The solution has {n} steps",
## above the library default of {DEFAULT}, so iterative deepening may search {n} steps deep.
sp {{{task}*elaborate*flags*max-evaluation-depth
   (state <s> ^superstate nil ^name {task})
-->
   (<s> ^flag-override <f>)
   (<f> ^max-evaluation-depth {n})
}}
'''
