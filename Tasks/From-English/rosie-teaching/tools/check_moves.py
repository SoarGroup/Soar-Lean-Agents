"""Independent check of a plan for the side-swapping, grid, chess and solitaire dialogs (18 Nov 2026): replays the actions
on the world file in Python, from the instructor's statements (not the generated rules), and reports any illegal action,
any losing state, and whether the goal holds at the end.
usage: python3 run_agent.py DIR LOADER --json | python3 check_moves.py TASK WORLD"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rosie_gen as R


class W:
    def __init__(s, path):
        s.objs, rels, _ = R.read_world(path)
        s.rels = {k: set(v) for k, v in rels.items()}
        s.on = dict(rels.get('on', []))                      # block -> what it is on
        s.h = {f"{a['category']}-{i}": i for i, a in s.objs.items()}
        s.pos = {i: a.get('position', 0) for i, a in s.objs.items() if a['category'] == 'block'}

    def cat(s, i): return s.objs[i]['category']
    def col(s, i): return s.objs[i].get('color')
    def clear(s, i): return i not in s.on.values()
    def loc(s, b): return s.on.get(b) if s.on.get(b) in s.objs and s.cat(s.on.get(b)) == 'location' else None
    def r(s, name, a, b): return (a, b) in s.rels.get(name, set())
    def adjacent(s, a, b): return s.r('near', a, b) and not s.r('diagonal-with', a, b) and not s.r('diagonal-with', b, a)
    def xy(s, i): a = s.objs[i]; return (a.get('x', a.get('column')), a.get('y', a.get('row')))
    def between(s, l, c, o):
        (lx, ly), (cx, cy), (ox, oy) = s.xy(l), s.xy(c), s.xy(o)
        return (lx - cx, ly - cy) == (cx - ox, cy - oy) and abs(lx - cx) + abs(ly - cy) == 1
    def between8(s, l, c, o):
        """c is the midpoint of l and o, one step from each in any of the eight directions (peg solitaire; A-P6)."""
        (lx, ly), (cx, cy), (ox, oy) = s.xy(l), s.xy(c), s.xy(o)
        return (lx - cx, ly - cy) == (cx - ox, cy - oy) and max(abs(lx - cx), abs(ly - cy)) == 1
    def knight(s, l, f):
        locs = [i for i in s.objs if s.cat(i) == 'location']
        return l != f and not s.r('near', l, f) and not s.r('near', f, l) and any(s.r('alongside', o, f) and s.r('diagonal-with', o, l) for o in locs)
    def available(s, b): return s.loc(b) is None and s.on.get(b) is None or (b in s.on and s.cat(s.on[b]) == 'block')
    def locations(s): return [i for i in s.objs if s.cat(i) == 'location']
    def blocks(s): return [i for i in s.objs if s.cat(i) == 'block']


def step(w, b, d, ok):
    if not ok: return False
    w.on[b] = d
    return True


def swap(kind):
    def check(w, act):
        name, b, d = act[0], w.h[act[1]], w.h[act[2]]
        if w.cat(d) != 'location' or not w.clear(d) or w.cat(b) != 'block': return False
        l1 = w.loc(b)
        others = {w.loc(o): o for o in w.blocks() if o != b}
        if kind in ('frogs', 'men'):
            right_peg = w.col(b) == 'blue'; left_peg = w.col(b) == 'red'
            jump_ok = lambda dirrel: any(w.r(dirrel, l1, l2) and w.r(dirrel, l2, d) and (kind == 'men' or w.col(o) != w.col(b))
                                         for l2, o in others.items() if l2)
            ok = (right_peg and (w.r('right-of', d, l1) or jump_ok('left-of'))) or (left_peg and (w.r('left-of', d, l1) or jump_ok('right-of')))
        else:
            ok = w.knight(d, l1)
        return step(w, b, d, ok)
    def goal(w): return all(w.col(w.loc(b)) == w.col(b) for b in w.blocks())
    return check, goal, lambda w: False


def grid(kind):
    def check(w, act):
        name, b, d = act[0], w.h[act[1]], w.h[act[2]]
        if w.cat(d) != 'location' or not w.clear(d): return False
        if name in ('push', 'push-block'):   # b is the pushed block on C; the blue pusher on O, in line with d
            c = w.loc(b)
            pushers = [q for q in w.blocks() if w.col(q) == 'blue' and w.loc(q) and w.between(d, c, w.loc(q))]
            if not pushers: return False
            q = pushers[0]; w.on[q] = c; w.on[b] = d; return True
        l1 = w.loc(b)
        if kind in ('maze', 'sokoban') and w.col(b) != 'blue': return False
        return step(w, b, d, l1 is not None and w.adjacent(d, l1))
    def goal(w):
        if kind == 'maze': return any(w.col(w.loc(b)) == 'blue' for b in w.blocks() if w.col(b) == 'blue' and w.loc(b))
        if kind == 'sokoban': return all(any(w.col(b) == c and w.loc(b) and w.col(w.loc(b)) == c for b in w.blocks()) for c in ('red', 'green'))
        attr = 'color' if kind == 'color' else 'value'
        return all(w.loc(b) and w.objs[w.loc(b)].get(attr) == w.objs[b].get(attr) for b in w.blocks())
    return check, goal, lambda w: False


def placement(rules):
    def check(w, act):
        b, d = w.h[act[1]], w.h[act[2]]
        if w.cat(d) != 'location' or not w.clear(d) or not w.clear(b) or w.loc(b) is not None: return False
        w.on[b] = d; return True
    def lost(w):
        placed = [(b, w.loc(b)) for b in w.blocks() if w.loc(b)]
        for i, (b1, l1) in enumerate(placed):
            for b2, l2 in placed[i + 1:]:
                (c1, r1), (c2, r2) = w.xy(l1), w.xy(l2)
                if 'row' in rules and r1 == r2: return True
                if 'column' in rules and c1 == c2: return True
                if 'diagonal' in rules and abs(r1 - r2) == abs(c1 - c2): return True
                if 'next-to' in rules and (w.r('near', l1, l2) or w.r('near', l2, l1)): return True
                if 'jumpable' in rules and (w.knight(l1, l2) or w.knight(l2, l1)): return True
        return False
    return check, lambda w: all(w.loc(b) for b in w.blocks()), lost


def tour(move):
    def check(w, act):
        b, d = w.h[act[1]], w.h[act[2]]
        old = w.loc(b)
        if w.col(b) != 'red' or w.cat(d) != 'location' or not w.clear(d) or old is None: return False
        if not (w.adjacent(d, old) if move == 'adjacent' else w.knight(d, old)): return False
        tops = [u for u in w.blocks() if w.col(u) == 'blue' and w.clear(u) and w.loc(u) is None]
        if len(tops) != 1: return False
        w.on[b] = d; w.on[tops[0]] = old; return True
    def goal(w):
        cov = all(not w.clear(l) for l in w.locations())
        if move != 'adjacent': return cov
        r = [w.loc(b) for b in w.blocks() if w.col(b) == 'red']
        return cov and any(w.adjacent(g, l) for l in r for g in w.locations() if w.col(g) == 'green')
    return check, goal, lambda w: False


def pegs(garbage):
    def check(w, act):
        q, l = w.h[act[1]], w.h[act[2]]
        o = w.loc(q)
        if w.cat(l) != 'location' or not w.clear(l) or o is None: return False
        cs = [c for c in w.locations() if w.between8(l, c, o) and not w.clear(c)]
        if not cs: return False
        p = [b for b in w.blocks() if w.loc(b) == cs[0]][0]
        if garbage: w.on[p] = [i for i, a in w.objs.items() if a.get('name') == 'garbage'][0]
        else: del w.on[p]
        w.on[q] = l; return True
    return check, lambda w: sum(1 for l in w.locations() if not w.clear(l)) == 1, lambda w: False


def mahjong():
    def check(w, act):
        b1, b2 = w.h[act[1]], w.h[act[2]]
        g = [i for i, a in w.objs.items() if a.get('name') == 'garbage'][0]
        for b in (b1, b2):
            if not w.clear(b) or w.on.get(b) == g: return False
        if b1 == b2 or w.col(b1) != w.col(b2): return False
        w.on[b1] = g; w.on[b2] = g; return True
    return check, lambda w: all(w.on.get(b) == [i for i, a in w.objs.items() if a.get('name') == 'garbage'][0] for b in w.blocks()), lambda w: False


def golf():
    def check(w, act):
        b, d = w.h[act[1]], w.h[act[2]]
        if not w.clear(b) or w.pos[b] != 0 or not w.clear(d): return False
        if w.cat(d) == 'location':
            if w.objs[d].get('name') != 'garbage': return False
        elif not (w.pos[d] == 1 and abs(w.objs[b]['value'] - w.objs[d]['value']) == 1): return False
        w.on[b] = d; w.pos[b] = 1; return True
    return check, lambda w: all(p == 1 for p in w.pos.values()), lambda w: False


CHECKS = {'frogs-and-toads': swap('frogs'), 'eight-men-raft': swap('men'), 'knight-swap': swap('knight'),
          'knight-side-swap': swap('knight'), 'simple-maze': grid('maze'), 'push-maze': grid('maze'),
          'sokoban': grid('sokoban'), 'eight-puzzle': grid('color'), 'five-puzzle': grid('color'),
          'iso-eight-puzzle': grid('value'), 'fifteen-puzzle': grid('value'),
          'n-queens': placement(['row', 'column', 'diagonal']), 'n-rooks': placement(['row', 'column']),
          'n-kings': placement(['next-to']), 'n-knights': placement(['jumpable']),
          'traveling-salesman': tour('adjacent'), 'knights-tour': tour('jumpable'),
          'peg-solitaire-r': pegs(False), 'peg-solitaire': pegs(True), 'mahjong': mahjong(),
          'golf-solitaire': golf(), 'tri-peaks': golf()}

if __name__ == '__main__':
    task, world = sys.argv[1], sys.argv[2]
    run = json.load(sys.stdin)
    w = W(world)
    check, goal, lost = CHECKS[task]
    verdict = None
    for n, act in enumerate(run['actions'], 1):
        if not check(w, act): verdict = f'action {n} illegal: {" ".join(act)}'; break
        if lost(w): verdict = f'losing state after action {n}'; break
    if verdict is None: verdict = 'goal holds' if goal(w) else 'goal does not hold'
    print(f"{run['outcome']}, {run['n_actions']} actions, {run['decisions']} decisions: {verdict}")
