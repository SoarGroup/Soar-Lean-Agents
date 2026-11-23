"""Learning setting kept with a task's English statement (World-Conventions L5-021).

The library learns from look-ahead by default (chunk only, library v2.46). A task whose agent should not learn says so
in its English file (english-input.txt, task.md) with one line, placed before any 'Search control' section:

    Learning: do not learn from look-ahead. <reason>

Without such a line the agent keeps the library default. Generators see the setting only through this tool:

    setting(path)  -> ('off', reason) or ('on', '')
    block(path)    -> the text to append to the rules file ('' when learning stays on): a comment with the reason,
                      then 'chunk never', sourced after the library so it overrides the default.

usage: python3 learning.py FILE   prints the setting.
Written 23 November 2026 by Claude, supervised by John E. Laird.
"""
import re
import sys

LINE = re.compile(r'^\s*Learning\s*:\s*(.+?)\s*$', re.I)
OFF = re.compile(r'^do not learn from look-ahead\.?\s*(.*)$', re.I)
ON = re.compile(r'^learn from look-ahead\.?\s*(.*)$', re.I)


def setting(path):
    found = None
    for l in open(path, encoding='utf-8').read().splitlines():
        m = LINE.match(l)
        if not m:
            continue
        if found is not None:
            raise ValueError(f'{path}: more than one Learning line')
        s = m.group(1)
        if OFF.match(s):
            found = ('off', OFF.match(s).group(1))
        elif ON.match(s):
            found = ('on', ON.match(s).group(1))
        else:
            raise ValueError(f'{path}: Learning line not understood: {s}')
    return found or ('on', '')


def block(path):
    mode, reason = setting(path)
    if mode == 'on':
        return ''
    return ('\n## Learning is off for this agent: the English statement says "Learning: do not learn from look-ahead"'
            ' (World-Conventions L5-021).\n'
            + (f'## Reason given: {reason}\n' if reason else '')
            + 'chunk never\n')


if __name__ == '__main__':
    print(setting(sys.argv[1]))
