"""Static check of the search/cost options a generated Soar task program selects.
usage: check_options.py RULES.soar [...]   exit 1 if any ERROR.  Reads the ^flag-override blocks and the task's cost vocabulary
(^step-cost, ^estimated-remaining-cost, ^state-value, ^better higher, ^progress-score). Each finding is E (will not work / wrong result)
or W (works but probably not what was intended). Rule ids refer to Option-Selection-Guide-v1.md section 4."""
import re, sys
ENUM = {'cost-metric': {'none', 'unit', 'time'}, 'optimize': {'true', 'false'}, 'iterative-step': {'operator', 'tie-impasse', 'cost'},
        'termination': {'depth', 'progress'}, 'mea-operator-selection': {'true', 'false'}}
NUM = {'heuristic-weight', 'cost-weight', 'cost-quantum', 'min-step-cost', 'aspiration', 'aspiration-step', 'progress-threshold'}
NEEDS_COST = {'optimize', 'heuristic-weight', 'cost-weight', 'cost-quantum', 'min-step-cost', 'aspiration', 'aspiration-step'}
def flags(text):
    out = {}
    for m in re.finditer(r'\(<(\w+)>\s+((?:\^[\w-]+\s+[^\s)^]+\s*)+)\)', text):
        for k, v in re.findall(r'\^([\w-]+)\s+([^\s)^]+)', m.group(2)):
            if k in ENUM or k in NUM or k in ('cost-metric', 'desired-selection'): out[k] = v
    return out
def check(text):
    f = flags(text); r = []
    def add(i, lvl, msg): r.append((i, lvl, msg))
    it = f.get('iterative-step', 'operator'); cm = f.get('cost-metric', 'unit' if it == 'cost' else 'none')  # library v2.37: iterative-step cost implies unit
    opt = f.get('optimize', 'false') == 'true'
    h = bool(re.search(r'\^estimated-remaining-cost\s+[\d.]', text)); nv = bool(re.search(r'\^better\s+higher', text)); sv = '^state-value' in text
    sc = bool(re.search(r'\^step-cost\b', text)); zero = bool(re.search(r'\^step-cost\s+0(\.0+)?[\s)]', text))
    ps = '^progress-score' in text
    for k, v in f.items():
        if k in ENUM and v not in ENUM[k]: add('O1', 'E', f'^{k} {v}: allowed values are {sorted(ENUM[k])}')
        if k in NUM and not re.fullmatch(r'-?\d+(\.\d+)?', v): add('O1', 'E', f'^{k} {v}: must be a number')
    for k in sorted(NEEDS_COST & set(f)):
        if cm == 'none': add('O2', 'E', f'^{k} needs ^cost-metric unit or time (it has no effect with none)')
    if it == 'cost' and cm == 'none': add('O2', 'E', '^iterative-step cost with ^cost-metric none: cost-cap iteration has no path cost (leave cost-metric unset, which gives unit since library v2.37, or set unit or time)')
    if cm == 'unit' and not sc: add('O3', 'W', 'cost-metric unit but no operator carries ^step-cost: every task operator costs 1 (the library default), so the cost is the number of operators')
    if cm == 'none' and (sc or h): add('O3', 'W', 'task supplies ^step-cost or ^estimated-remaining-cost but cost-metric is none: they are ignored')
    if h and cm != 'none' and not (opt or it == 'cost'): add('O4', 'W', '^estimated-remaining-cost is used only with optimize true or iterative-step cost')
    if h and f.get('heuristic-weight', '1') not in ('1', '1.0') and not h: add('O4', 'W', 'heuristic-weight without ^estimated-remaining-cost')
    if 'heuristic-weight' in f and not h: add('O4', 'W', '^heuristic-weight has no effect without ^estimated-remaining-cost')
    if h: add('O5', 'W', 'confirm ^estimated-remaining-cost never exceeds the true remaining cost (probe P2); an overestimate loses optimality')
    if it == 'cost' and not h and zero: add('O6', 'W', 'zero-cost operators with cost-cap iteration and no heuristic: may not finish (zero-cost cycle). Add ^estimated-remaining-cost or set ^min-step-cost to about a tenth of the smallest real step cost (0.01 explores the cycle ~cap/0.01 times)')
    if nv != sv: add('O7', 'E', '^state-value and ^better higher must be supplied together')
    if nv and cm == 'none': add('O7', 'W', 'net value (^better higher) needs cost-metric unit or time to subtract path cost')
    if nv and opt: add('O8', 'W', 'optimize and the cost bounds are not applied to a net value (first-success semantics; about 1 graph in 10 returned a costlier path)')
    if nv and it == 'cost': add('O8', 'W', 'iterative-step cost with net value needs an acyclic or bounded task graph')
    if f.get('termination') == 'progress':
        if not ps and not re.search(r'\^desired\b', text): add('O9', 'E', 'termination progress needs ^progress-score or desireds')
        add('O9', 'W', 'confirm the progress score is monotone along solutions (probe P4); Hanoi-like tasks fail')
    if it == 'tie-impasse' and cm != 'none' and not opt: add('O10', 'W', 'iterative-step tie-impasse uses a cost metric only with optimize true (library v2.30); without optimize the cost options are ignored')
    if cm == 'time': add('O11', 'W', 'cost-metric time: measured only on tasks without scheduled future events; with events run probe P5')
    if cm != 'none' and not opt and it != 'cost' and not nv: add('O12', 'W', 'cost-metric set, optimize false, iterative-step not cost: the result is the cheapest path at the first successful depth, not the global optimum')
    return r
if __name__ == '__main__':
    bad = 0
    for p in sys.argv[1:]:
        for i, lvl, msg in check(open(p).read()):
            print(f'{p}: {lvl} {i}: {msg}'); bad += lvl == 'E'
    sys.exit(1 if bad else 0)
