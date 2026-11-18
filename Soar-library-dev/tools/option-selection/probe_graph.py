"""Probes that decide which cost/search options a task needs, run on an explicit small instance of the task.
A task generator describes its instance as a state graph: edges = {state: [(next_state, step_cost), ...]}, start, goals (set), and optionally
h = {state: estimate} and score = {state: progress score}. Ids P1..P5 refer to Option-Selection-Guide-v1.md section 3.
usage (library): import probe_graph as P; P.report(edges, start, goals, h=None, score=None)"""
import heapq, collections
def _dist(edges, start, goals):
    d = {start: 0}; pq = [(0, start)]
    while pq:
        c, n = heapq.heappop(pq)
        if c > d[n]: continue
        for b, w in edges.get(n, []):
            if c + w < d.get(b, 1e18): d[b] = c + w; heapq.heappush(pq, (c + w, b))
    return d, min((d[g] for g in goals if g in d), default=None)
def _hops(edges, start, goals):
    q = collections.deque([(start, 0)]); seen = {start}
    while q:
        n, k = q.popleft()
        if n in goals: return k
        for b, _ in edges.get(n, []):
            if b not in seen: seen.add(b); q.append((b, k + 1))
def _cheapest_fewest(edges, start, goals):
    """cost of the cheapest path among those with the fewest operators"""
    d = {start: (0, 0)}; pq = [(0, 0, start)]
    while pq:
        k, c, n = heapq.heappop(pq)
        if (k, c) > d[n]: continue
        for b, w in edges.get(n, []):
            v = (k + 1, c + w)
            if v < d.get(b, (10**9, 1e18)): d[b] = v; heapq.heappush(pq, (v[0], v[1], b))
    return min((d[g][1] for g in goals if g in d), default=None)
def p1_discriminates(edges, start, goals):
    """P1: does cost change the answer? True if the cheapest path costs less than the cheapest of the fewest-operator paths."""
    return _cheapest_fewest(edges, start, goals) > _dist(edges, start, goals)[1] + 1e-9
def p2_admissible(edges, goals, h):
    """P2: h(s) <= true remaining cost for every state that can reach a goal. Returns the list of violating states."""
    rev = collections.defaultdict(list)
    for a, l in edges.items():
        for b, w in l: rev[b].append((a, w))
    d = {g: 0 for g in goals}; pq = [(0, g) for g in goals]
    while pq:
        c, n = heapq.heappop(pq)
        if c > d[n]: continue
        for a, w in rev[n]:
            if c + w < d.get(a, 1e18): d[a] = c + w; heapq.heappush(pq, (c + w, a))
    return [(s, h[s], d[s]) for s in h if s in d and h[s] > d[s] + 1e-9]
def p3_zero_cost_cycle(edges):
    """P3: states on a cycle of zero-cost edges (cycle search without a heuristic may not finish)."""
    z = {a: [b for b, w in l if w <= 0] for a, l in edges.items()}; bad = set()
    for s in z:
        seen = set(); st = list(z[s])
        while st:
            n = st.pop()
            if n == s: bad.add(s); break
            if n in seen: continue
            seen.add(n); st.extend(z.get(n, []))
    return sorted(bad, key=str)
def p4_progress_monotone(edges, start, goals, score):
    """P4: along some optimal-length solution the score never decreases. Returns the minimum number of score decreases on a solution path."""
    best = {start: 0}; pq = [(0, 0, start)]; cnt = 0
    while pq:
        dec, k, n = heapq.heappop(pq)
        if dec > best.get(n, 1e9): continue
        if n in goals: return dec
        for b, _ in edges.get(n, []):
            nd = dec + (score[b] < score[n])
            if nd < best.get(b, 1e9): best[b] = nd; cnt += 1; heapq.heappush(pq, (nd, cnt, b))
    return None
def report(edges, start, goals, h=None, score=None):
    """Recommend options. Returns dict(flags=..., reasons=[...], warnings=[...])."""
    flags = {}; why = []; warn = []
    opt = _dist(edges, start, goals)[1]
    if opt is None: return dict(flags={}, reasons=['no path from start to a goal'], warnings=['unsolvable instance'])
    if p1_discriminates(edges, start, goals):
        flags.update({'cost-metric': 'unit', 'optimize': 'true'}); why.append('P1: the cheapest path is not the shortest; cost matters')
        zc = p3_zero_cost_cycle(edges)
        if h is not None:
            bad = p2_admissible(edges, goals, h)
            if bad: warn.append(f'P2: h overestimates in {len(bad)} states (first: {bad[0]}); fix h or drop it'); h = None
            else: why.append('P2: h is admissible; add ^estimated-remaining-cost'); 
        if zc and h is None: warn.append(f'P3: zero-cost cycles at {zc[:3]}; avoid iterative-step cost without a heuristic, or raise ^min-step-cost to ~0.1 x smallest real step cost')
        if h is not None: flags['estimated-remaining-cost'] = 'task-supplied'
    else:
        why.append('P1: the cheapest path is also the shortest; leave cost-metric none (default depth iteration is already optimal)')
    if score is not None:
        d = p4_progress_monotone(edges, start, goals, score)
        if d == 0: why.append('P4: progress score is monotone on a solution; ^termination progress is safe')
        else: warn.append(f'P4: every solution lowers the progress score {d} times; do not use termination progress')
    return dict(flags=flags, reasons=why, warnings=warn, optimum=opt)

def p5_compare(runs, optimum):
    """P5: runs = {config name: dict(cost=, decisions=, done=)} measured by running the agent on a small instance; optimum from the task's independent checker.
    Returns dict(optimal=[names that finished with the optimum, cheapest in decisions first], suboptimal={name: cost}, unfinished=[names], choice=name or None)."""
    ok = sorted((r['decisions'], n) for n, r in runs.items() if r.get('done') and abs(r['cost'] - optimum) < 1e-9)
    return dict(optimal=[n for _, n in ok], suboptimal={n: r['cost'] for n, r in runs.items() if r.get('done') and abs(r['cost'] - optimum) >= 1e-9},
                unfinished=[n for n, r in runs.items() if not r.get('done')], choice=ok[0][1] if ok else None)
