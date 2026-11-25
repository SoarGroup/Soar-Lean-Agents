"""The environment's output form stated in a task's English (World-Conventions L10-018).

A task whose environment does not take the default ^perform-action command says so in its English file, one line
after the teaching script:

    Output: command <name>; name attribute <attr>; arguments <a1> <a2> <a3>; done <s> <s>; success <s>; error <s> <s>; applied <s>.

Every part is optional and defaults to the library's map (command perform-action, name attribute name, arguments
argument1 argument2 argument3, done interrupted complete success, success success, error error failure, applied complete).
"command action" makes the action name itself the command (^<action> on the output-link, no name attribute).
The generators write the environment-effect rules and the environment's output map for that form
(worldgen/wg.py apply_output_form; WorldSpec Task.output).

    read(path) -> a dict with WorldSpec's OutputForm fields (command, nameAttribute, arguments, done, success, error,
                  applied), or None when the file has no Output line
Written 24 November 2026 by Claude, supervised by John E. Laird."""
import re

LINE = re.compile(r'^\s*Output\s*:\s*(.+?)\.?\s*$', re.I)
KEYS = {'command': 'command', 'name attribute': 'nameAttribute', 'arguments': 'arguments', 'done': 'done',
        'success': 'success', 'error': 'error', 'applied': 'applied'}
LISTS = ('arguments', 'done', 'success', 'error')


def read(path):
    for line in open(path, encoding='utf-8').read().splitlines():
        m = LINE.match(line)
        if not m: continue
        form = {}
        for part in m.group(1).split(';'):
            part = part.strip()
            if not part: continue
            key = next((k for k in sorted(KEYS, key=len, reverse=True) if part.lower().startswith(k + ' ')), None)
            if key is None: raise ValueError(f'{path}: cannot read Output part "{part}"')
            val = part[len(key):].strip()
            f = KEYS[key]
            if f in LISTS: form[f] = val.split()
            elif f == 'command': form[f] = None if val.lower() == 'action' else val
            else: form[f] = val
        return form
    return None
