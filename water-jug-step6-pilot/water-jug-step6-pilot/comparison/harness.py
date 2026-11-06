"""Task-level runs of Water Jug agents in Soar 9.6.5 (soar_sml).

usage: harness.py DIR LOADFILE [--cap N] [--seeds a-b] [--first]
For each seed: source the agent, then `srand SEED` (overriding the agent's own srand), run decision by
decision up to the cap, and record: whether a top-state jug reached the goal (volume 3, contents 1),
the top-level operators applied before that, whether the agent halted, and chunks learned.
--first instead uses `decide indifferent-selection --first` and srand 0 (the agent library's setting).
Prints one JSON object per run.
"""
import argparse, json, os, re
import soar_sml as sml

TOP_OP = re.compile(r'^\s*\d+:    O: \S+ \(([^)]+)\)', re.M)

def jug_state(a):
    t = a.ExecuteCommandLine('print --depth 2 s1')
    out = []
    for i in re.findall(r'\^jug (\S+)', t):
        m = re.search(r'\(' + re.escape(i) + r' ([^)]*)\)', t)
        if m:
            v = re.search(r'\^volume (\S+)', m.group(1)); c = re.search(r'\^contents (\S+)', m.group(1))
            if v and c:
                out.append((int(float(v.group(1))), int(float(c.group(1)))))
    return tuple(sorted(out, reverse=True))

def run(d, load, cap, seed=None, first=False, goal=(3, 1)):
    k = sml.Kernel.CreateKernelInCurrentThread(True, 0)
    a = k.CreateAgent('h')
    out = []
    a.RegisterForPrintEvent(sml.smlEVENT_PRINT, lambda *x: out.append(x[-1]), None)
    if first:
        a.ExecuteCommandLine('decide indifferent-selection --first'); a.ExecuteCommandLine('srand 0')
    os.chdir(d); a.ExecuteCommandLine('cd ' + d)
    a.ExecuteCommandLine('source ' + load)
    if not first:
        a.ExecuteCommandLine(f'srand {seed}')
    a.ExecuteCommandLine('watch 1')
    ops, goal_ops, halted, path = [], None, False, []
    n = 0
    for n in range(1, cap + 1):
        out.clear()
        a.RunSelf(1)
        txt = ''.join(out)
        ops += [o for o in TOP_OP.findall(txt) if o not in ('evaluate-operator', 'create-preferences')]
        js = jug_state(a)
        if js and (not path or path[-1] != js):
            path.append(js)
        if goal_ops is None and goal in js:
            goal_ops = len(ops)
        if 'halted' in txt:
            halted = True
            break
    m = re.search(r'(\d+) decisions', a.ExecuteCommandLine('stats'))
    chunks = len(re.findall(r'^\S', a.ExecuteCommandLine('print --chunks'), re.M))
    k.Shutdown()
    return dict(seed=seed, decisions=int(m.group(1)) if m else n, halted=halted,
                solved=goal_ops is not None, ops_to_goal=goal_ops, chunks=chunks,
                path=[list(map(list, p)) for p in path[:40]], ops=ops[:40])

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('dir'); p.add_argument('load')
    p.add_argument('--cap', type=int, default=300)
    p.add_argument('--seeds', default='1-20')
    p.add_argument('--first', action='store_true')
    o = p.parse_args()
    d = os.path.abspath(o.dir)
    if o.first:
        print(json.dumps(run(d, o.load, o.cap, first=True)), flush=True)
    else:
        lo, hi = map(int, o.seeds.split('-'))
        for s in range(lo, hi + 1):
            print(json.dumps(run(d, o.load, o.cap, seed=s)), flush=True)
