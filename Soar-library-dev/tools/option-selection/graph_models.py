"""Independent state-graph models of the generated tasks, for the option probes (probe_graph.py). Each model returns
dict(edges=, start=, goals=, h=, score=, hops=) and knows nothing about the Soar rules. weighted=True gives a non-uniform step cost.
eight(steps, weighted): cost of moving tile t = t; h = (weighted) Manhattan distance, admissible; score = tiles in place.
waterjug(weighted): cost = litres moved (fill: added, empty: discarded, pour: poured); no h.
hanoi(n, weighted): cost of moving disc d = d; no h; score = discs on the goal peg."""
import collections
G = (1, 2, 3, 4, 5, 6, 7, 8, 0)
EIGHT_STARTS = {1: (1,2,3,4,5,0,7,8,6), 2: (1,2,3,4,0,5,7,8,6), 3: (1,2,3,4,8,5,7,0,6)}
def _nbrs8(b):
    z = b.index(0); r, c = divmod(z, 3)
    for dr, dc in ((0, 1), (1, 0), (0, -1), (-1, 0)):
        r2, c2 = r + dr, c + dc
        if 0 <= r2 < 3 and 0 <= c2 < 3:
            j = r2 * 3 + c2; nb = list(b); nb[z], nb[j] = nb[j], 0; yield tuple(nb), b[j]
def eight(steps=3, weighted=False):
    start = EIGHT_STARTS[steps]; edges = {}; q = collections.deque([start]); seen = {start}
    while q:
        b = q.popleft(); edges[b] = []
        for nb, tile in _nbrs8(b):
            edges[b].append((nb, tile if weighted else 1))
            if nb not in seen: seen.add(nb); q.append(nb)
    pos = {t: divmod(i, 3) for i, t in enumerate(G)}
    def man(b): return sum((t if weighted else 1) * (abs(i // 3 - pos[t][0]) + abs(i % 3 - pos[t][1])) for i, t in enumerate(b) if t)
    return dict(edges=edges, start=start, goals={G}, h={b: man(b) for b in edges}, score={b: sum(1 for i, t in enumerate(b) if t and t == G[i]) for b in edges})
def waterjug(weighted=False):
    cap = (3, 5); start = (0, 0); edges = {}; q = collections.deque([start]); seen = {start}
    while q:
        s = q.popleft(); out = []
        for j in (0, 1):
            f = list(s); f[j] = cap[j]; out.append((tuple(f), cap[j] - s[j]))
            e = list(s); e[j] = 0; out.append((tuple(e), s[j]))
            k = 1 - j; amt = min(s[j], cap[k] - s[k]); p = list(s); p[j] -= amt; p[k] += amt; out.append((tuple(p), amt))
        edges[s] = [(t, (c if weighted else 1)) for t, c in out if t != s and (c > 0 or not weighted)]
        for t, _ in edges[s]:
            if t not in seen: seen.add(t); q.append(t)
    goals = {s for s in edges if s[0] == 1}
    return dict(edges=edges, start=start, goals=goals, h=None, score=None)
def hanoi(n=2, weighted=False):
    start = tuple([0] * n); edges = {}; q = collections.deque([start]); seen = {start}
    while q:
        s = q.popleft(); edges[s] = []
        for d in range(n):
            if any(s[e] == s[d] for e in range(d)): continue   # a smaller disc is on top
            for p in range(3):
                if p != s[d] and not any(s[e] == p for e in range(d)):
                    t = list(s); t[d] = p; t = tuple(t); edges[s].append((t, d + 1 if weighted else 1))
                    if t not in seen: seen.add(t); q.append(t)
    goal = tuple([2] * n)
    return dict(edges=edges, start=start, goals={goal}, h=None, score={s: sum(1 for x in s if x == 2) for s in edges})
