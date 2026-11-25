"""Phases, loops, termination and repeat count stated in a task's English (World-Conventions L8-026 to L8-030).

A task's English file (english-input.txt) may add, after the teaching script, goals and an order among them:

    Goal <name>: <a goal statement the task's generator can read>.
    Phases: first <goal>, then <goal>, ..., finally <goal>.
    Repeat: from <goal>[, <N> times][, until <goal>].

<goal> is a goal name: the task's own goal (its "The name of the goal is ..." statement, or 'goal') or one declared
with a Goal line. Phases are pursued in order (L8-026). A Repeat line closes the sequence back to the named phase
(L8-027); "<N> times" is the number of passes (^repeat-count, L8-029); "until <goal>" ends the loop when that goal
holds (^termination-desireds, L8-028). Without a Repeat line the task ends when the last phase is achieved; a Repeat
line with neither a count nor an until-goal loops for ever (L8-030).

    read(path) -> {'goals': {name: text}, 'phases': [names], 'loop_from': name|None, 'repeat': N|None,
                   'until': name|None}, or None when the file states no phases
    apply(task, seq, main_goal) -> sets the wg.Task's phases, loop start, termination and repeat count. Each goal is the
                   attribute ^<name>-met on the task object (the task's own goal stays ^goal-met); the task's generator
                   writes the rule that sets it.
Written 24 November 2026 by Claude, supervised by John E. Laird."""
import re

NUM = {w: i for i, w in enumerate('zero one two three four five six seven eight nine ten eleven twelve'.split())}
GOAL = re.compile(r'^\s*Goal\s+([\w-]+)\s*:\s*(.+?)\s*$', re.I)
PHASES = re.compile(r'^\s*Phases\s*:\s*(.+?)\.?\s*$', re.I)
REPEAT = re.compile(r'^\s*Repeat\s*:\s*(.+?)\.?\s*$', re.I)
MAIN = re.compile(r'The name of the goal is ([\w-]+)', re.I)


def _count(s):
    s = s.lower()
    return int(s) if s.isdigit() else NUM.get(s)


def read(path):
    text = open(path, encoding='utf-8').read()
    goals, phases, loop_from, repeat, until = {}, [], None, None, None
    for line in text.splitlines():
        if m := GOAL.match(line):
            goals[m.group(1)] = m.group(2).rstrip('.')
        elif m := PHASES.match(line):
            parts = re.split(r',\s*', m.group(1))
            phases = [re.sub(r'^(first|then|finally|and then)\s+', '', p.strip(), flags=re.I) for p in parts if p.strip()]
        elif m := REPEAT.match(line):
            for part in re.split(r',\s*', m.group(1)):
                part = part.strip()
                if mm := re.match(r'from\s+([\w-]+)$', part, re.I): loop_from = mm.group(1)
                elif mm := re.match(r'(\w+)\s+times?$', part, re.I): repeat = _count(mm.group(1))
                elif mm := re.match(r'until\s+([\w-]+)$', part, re.I): until = mm.group(1)
                else: raise ValueError(f'{path}: cannot read Repeat part "{part}"')
            if loop_from is None and phases: loop_from = phases[0]
    if not phases:
        return None
    m = MAIN.search(text)
    return dict(goals=goals, phases=phases, loop_from=loop_from, repeat=repeat, until=until,
                main=m.group(1) if m else 'goal')


def attr(seq, name):
    """The task-object attribute that holds a goal."""
    return 'goal-met' if name == seq['main'] else f'{name}-met'


def apply(task, seq):
    """Set the wg.Task's phases from a sequence read by read()."""
    known = set(seq['goals']) | {seq['main']}
    for g in seq['phases'] + [x for x in (seq['loop_from'], seq['until']) if x]:
        if g not in known: raise ValueError(f'unknown goal {g} (declare it with a Goal line)')
    task.phases = [[('task', {attr(seq, g): 'true'})] for g in seq['phases']]
    if seq['loop_from'] is not None or seq['repeat'] is not None or seq['until'] is not None:
        task.loop_start = seq['phases'].index(seq['loop_from'] or seq['phases'][0])
    if seq['until']: task.termination = [('task', {attr(seq, seq['until']): 'true'})]
    if seq['repeat'] is not None: task.repeat_count = seq['repeat']
    for g in known:
        a = attr(seq, g)
        if a not in task.derived: task.derived.append(a)
