"""Independent check of a plan produced by a Rosie-pilot agent: replays the actions on the world file in Python, using the
instructor's statements directly (not the generated rules), and reports any illegal action, any losing state and whether the
goal holds at the end.
usage: python3 run_agent.py DIR LOADER --json | python3 check_plan.py TASK WORLD     (TASK: a key of CHECKS)"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rosie_gen as R

def hanoi(objs, on, acts):
    h = {f"{a['category']}-{i}": i for i, a in objs.items()}
    clear = lambda x: x not in on.values()                                   # statement 6
    for n, (name, b, d) in enumerate(acts, 1):
        b, d = h[b], h[d]
        ok = (name == 'move' and objs[b]['category'] == 'block' and clear(b) and clear(d)
              and objs[d]['volume'] > objs[b]['volume'])                      # statements 5, 7
        if not ok: return f'action {n} illegal: {name} {b} {d}'
        on[b] = d
    greens = [i for i, a in objs.items() if a['category'] == 'location' and a.get('color') == 'green']
    return 'goal holds' if sum(clear(g) for g in greens) >= 2 else 'goal does not hold'   # statement 9

def fox(objs, on, acts):
    def handle(i):
        a = objs[i]
        return f'bank-{i}' if a['category'] == 'location' else a.get('shape', a.get('color')) + f'-{i}'
    h = {handle(i): i for i in objs}
    boat = next(i for i, a in objs.items() if a.get('shape') == 'boat')
    banks = [i for i, a in objs.items() if a['category'] == 'location']
    def lost():
        opp = [b for b in banks if on[boat] != b]                            # statement 7
        col = lambda c: [i for i, a in objs.items() if a.get('color') == c]
        return any(any(on[r] == o for r in col(x)) and any(on[y] == o for y in col('yellow')) for o in opp for x in ('red', 'green'))
    for n, (name, x, d) in enumerate(acts, 1):
        x, d = h[x], h[d]
        cur = on[boat]
        if d == cur or objs[d]['category'] != 'location': return f'action {n} illegal: destination not the opposite bank'
        if name == 'ferry-one':                                              # statement 5
            if x == boat or on[x] != cur: return f'action {n} illegal: block not on the current bank'
            on[x] = d
        elif name != 'cross': return f'action {n} unknown: {name}'          # statement 8
        on[boat] = d
        if lost(): return f'action {n} reaches a losing state'               # statements 10, 13
    dest = next(i for i in banks if objs[i].get('name') == 'destination')
    return 'goal holds' if all(on[i] == dest for i, a in objs.items() if a['category'] == 'block') else 'goal does not hold'

def blocks_world(colors):
    bottom, top_on, top_below = colors
    def check(objs, on, acts):
        h = {f"{a['category']}-{i}": i for i, a in objs.items()}
        clear = lambda x: x not in on.values()
        for n, (name, b, d) in enumerate(acts, 1):
            b, d = h[b], h[d]
            if not (name == 'move' and objs[b]['category'] == 'block' and clear(b) and clear(d) and b != d):
                return f'action {n} illegal: {name} {b} {d}'
            on[b] = d
        col = lambda i, c: objs[i]['category'] == 'block' and objs[i].get('color') == c
        ok = any(col(a, top_on) and col(on[a], bottom) and any(col(c, top_below) and on.get(c) == a for c in objs)
                 for a in on)
        return 'goal holds' if ok else 'goal does not hold'
    return check

def sorting(objs, on, acts):
    h = {f"{a['color']}-{a['category']}-{i}": i for i, a in objs.items()}
    for n, (name, b, l) in enumerate(acts, 1):
        b, l = h[b], h[l]
        if not (name == 'move' and objs[b]['category'] == 'block' and objs[l]['category'] == 'location' and on[b] != l):
            return f'action {n} illegal: {name} {b} {l}'
        on[b] = l
    ok = all(objs[on[b]]['color'] == a['color'] for b, a in objs.items() if a['category'] == 'block')
    return 'goal holds' if ok else 'goal does not hold'

def frogs(variant):
    def check(objs, on, acts):
        h = {f"{a['category']}-{i}": i for i, a in objs.items()}
        count = lambda l: sum(1 for b in on if on[b] == l)
        for n, (name, c, l) in enumerate(acts, 1):
            c, l = h[c], h[l]
            k = count(c)
            ok = name == 'move' and k >= 1 and abs(objs[c]['x'] - objs[l]['x']) == k and objs[c]['y'] == objs[l]['y']
            if variant == 'lazy':
                ok = ok and not any(on[b] == c and objs[b].get('color') == 'red' for b in on)
            if not ok: return f'action {n} illegal: {name} {c} {l}'
            for b in [b for b in on if on[b] == c]: on[b] = l
        locs = [i for i, a in objs.items() if a['category'] == 'location']
        if variant == 'red-location':
            ok = all(objs[on[b]].get('color') == 'red' for b in on)
        else:
            ok = sum(1 for l in locs if count(l) == 0) >= 3
        return 'goal holds' if ok else 'goal does not hold'
    return check


def river(kind):
    """Replay crossings: legality from the action statements, losing conditions, goal (all blocks on the destination)."""
    def check(objs, on, acts):
        def handle(i):
            a = objs[i]
            if a['category'] == 'location': return f'bank-{i}'
            return '-'.join(x for x in (a.get('shape'), a.get('last-name')) if x) + f'-{i}'
        h = {handle(i): i for i in objs}
        boat = next(i for i, a in objs.items() if a.get('shape') == 'boat')
        banks = [i for i, a in objs.items() if a['category'] == 'location']
        def lost():
            for b in banks:
                here = [i for i in on if on[i] == b and i != boat]
                if kind == 'husband':
                    for w in here:
                        if objs[w].get('shape') == 'woman':
                            hus = [m for m in objs if objs[m].get('shape') == 'man' and objs[m].get('last-name') == objs[w]['last-name']]
                            if any(on[m] != b for m in hus) and any(objs[m].get('shape') == 'man' for m in here): return True
                if kind == 'wife':
                    for m in here:
                        if objs[m].get('shape') == 'man':
                            wif = [w for w in objs if objs[w].get('shape') == 'woman' and objs[w].get('last-name') == objs[m]['last-name']]
                            if any(on[w] != b for w in wif) and any(objs[w].get('shape') == 'woman' and w not in wif for w in here): return True
                if kind == 'mac':
                    c = sum(1 for i in here if objs[i].get('shape') == 'cannibal'); m = sum(1 for i in here if objs[i].get('shape') == 'missionary')
                    if m > 0 and c > m: return True
            return False
        for n, (name, x, y) in enumerate(acts, 1):
            cur = on[boat]; dest = next(b for b in banks if b != cur)
            if name == 'ferry-one':
                x = h[x]
                if h[y] != dest or x == boat or on[x] != cur: return f'action {n} illegal: {name} {x} {y}'
                moved = [x]
            elif name in ('ferry-two', 'ferry-two-children'):
                x, y = h[x], h[y]
                ok = x != y and boat not in (x, y) and on[x] == cur and on[y] == cur
                if name == 'ferry-two-children': ok = ok and objs[x].get('shape') == 'child' and objs[y].get('shape') == 'child'
                if not ok: return f'action {n} illegal: {name} {x} {y}'
                moved = [x, y]
            else: return f'action {n} unknown: {name}'
            for i in moved + [boat]: on[i] = dest
            if lost(): return f'action {n} reaches a losing state'
        dest = next(i for i in banks if objs[i].get('name') == 'destination')
        return 'goal holds' if all(on[i] == dest for i, a in objs.items() if a['category'] == 'block') else 'goal does not hold'
    return check

def logic(task):
    """Replay writes: an empty location, a number from 1 to N, no losing condition after any write, all filled at the end."""
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    def check(objs, on, acts):
        import rosie_logic as RL
        N = {'number-map-color': 4, 'kakuro': 9, 'shuffle': 9, 'sujiko': 9, 'suko': 9, 'survo': 12}.get(task, 4)
        h = {RL.handle(i, a): i for i, a in objs.items()}
        val = {i: a['value'] for i, a in objs.items() if 'value' in a}
        locs = [i for i, a in objs.items() if a['category'] == 'location']
        A = lambda i, k: objs[i].get(k)
        def pairs(attr=None, color=None):
            L = [i for i in locs if i in val and (color is None or A(i, 'color') == color)]
            return any(val[a] == val[b] and (attr is None or A(a, attr) == A(b, attr)) for a in L for b in L if a < b)
        def sums(groups):
            for members, target in groups:
                if all(m in val for m in members) and members:
                    t = target[1] if isinstance(target, tuple) else val.get(target)   # ('k', n): a constant; else a clue object id
                    if sum(val[m] for m in members) != t: return True
            return False
        def line(attr, cell, clue):
            out = []
            for v in sorted({A(i, attr) for i in locs}):
                cells = [i for i in locs if A(i, attr) == v and A(i, 'color') == cell]
                clues = [i for i in locs if A(i, attr) == v and A(i, 'color') == clue]
                if cells and clues: out.append((cells, clues[0]))
            return out
        def by(attr, const):
            return [([i for i in locs if A(i, attr) == v], ('k', const)) for v in sorted({A(i, attr) for i in locs if A(i, attr) is not None})]
        under = {}
        for l, b in RL.R.read_world(WORLD)[1].get('under', []): under.setdefault(b, []).append(l)
        def lost():
            if task == 'number-map-color':
                return any(val.get(a) is not None and val.get(a) == val.get(b) for a, b in RELS.get('near', []))
            if task in ('mini-sudoku', 'jigsawdoku-sudoku'): return pairs('row') or pairs('column') or pairs('section')
            if task == 'logi-five': return pairs('row') or pairs('column') or pairs('color')
            if task == 'color-ken-ken': return pairs('row') or pairs('column') or sums(by('color', 10))
            if task == 'ken-ken': return pairs('row') or pairs('column') or sums(by('section', 10))
            if task == 'killer-sudoku': return pairs('row') or pairs('column') or pairs('section') or sums(by('color', 10))
            if task == 'kakuro': return pairs('row', 'green') or pairs('column', 'green') or sums(line('column', 'green', 'blue') + line('row', 'green', 'yellow'))
            if task == 'shuffle': return sums(line('column', 'green', 'blue') + line('row', 'green', 'blue'))
            if task == 'survo': return pairs(None, 'green') or sums(line('column', 'green', 'blue') + line('row', 'green', 'blue'))
            if task in ('sujiko', 'suko'):
                g = [(m, b) for b, m in under.items()]
                for b in under: val.setdefault(b, objs[b]['value'])
                extra = [([i for i in locs if A(i, 'color') == c], ('k', k)) for c, k in (('blue', 10), ('red', 9), ('green', 26))] if task == 'suko' else []
                return pairs() or sums(g + extra)
            raise KeyError(task)
        for n, (name, l, num) in enumerate(acts, 1):
            l = h[l]; k = int(num.split('-')[1])
            if name != 'write' or l in val or not 1 <= k <= N: return f'action {n} illegal: {name} {l} {num}'
            val[l] = k
            if lost(): return f'action {n} reaches a losing state'
        return 'goal holds' if all(i in val and val[i] > 0 for i in locs) else 'goal does not hold'
    return check

CHECKS = {'tower-of-hanoi': hanoi, 'goose-fox-beans': fox, 'blocks-world': blocks_world(('green', 'red', 'orange')),
          'world-blocks': blocks_world(('purple', 'blue', 'yellow')), 'sorting-puzzle': sorting,
          'stacked-frogs': frogs('three-clear'), 'king-stacked-frogs': frogs('red-location'),
          'lazy-stacked-frogs': frogs('lazy'), 'tower-of-hanoi-4': hanoi, 'tower-of-hanoi-5': hanoi,
          'family-cross': river('none'), 'jealous-husbands': river('husband'), 'jealous-wives': river('wife'),
          'missionaries-and-cannibals': river('mac')}
for _t in ('number-map-color', 'jigsawdoku-sudoku', 'kakuro', 'color-ken-ken', 'ken-ken', 'killer-sudoku', 'logi-five', 'shuffle',
           'mini-sudoku', 'sujiko', 'suko', 'survo'):
    CHECKS[_t] = logic(_t)
WORLD, RELS = None, {}

if __name__ == '__main__':
    task, world = sys.argv[1], sys.argv[2]
    objs, rels, _ = R.read_world(world)
    WORLD, RELS = world, rels
    on = dict(rels.get('on', []))
    run = json.load(sys.stdin)
    verdict = CHECKS[task](objs, on, run['actions'])
    print(f"{run['outcome']}, {run['n_actions']} actions, {run['decisions']} decisions: {verdict}")
