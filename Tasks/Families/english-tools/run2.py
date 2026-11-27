"""Generic task-level runner for the blind round trip (Soar via soar_sml).

usage: python3 run2.py DIR LOADFILE [--seeds 1-3] [--episodes 3] [--cap 3000] [--chunk never|only|always]

Environment: every command an agent puts on the output-link gets ^status complete on the
next input phase (a generic 'world that always succeeds'). Nothing else is put on the input-link.
Protocol for task results: the agent prints a line containing 'TASK-RESULT: success' or
'TASK-RESULT: failure' (then usually halts). An episode ends at halt or at the cap.
Episodes 2..K run in the same agent after init-soar (learned rules and RL values kept).
Prints one JSON object per seed.
"""
import argparse, json, os, re, time, sys
import soar_sml as S

def count(a, cmd):
    r = a.ExecuteCommandLine(cmd)
    return len([l for l in r.splitlines() if l.strip() and not l.startswith('*')])

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('dir'); ap.add_argument('load')
    ap.add_argument('--seeds', default='1-3'); ap.add_argument('--episodes', type=int, default=3)
    ap.add_argument('--cap', type=int, default=3000)
    ap.add_argument('--chunk', default=None, help='chunk setting applied after the agent is loaded (overrides its own)')
    o = ap.parse_args(); o.dir = os.path.abspath(o.dir)
    lo, hi = map(int, o.seeds.split('-'))
    k = S.Kernel.CreateKernelInNewThread(S.Kernel.kUseAnyPort) if hasattr(S.Kernel, 'kUseAnyPort') else S.Kernel.CreateKernelInNewThread(0)
    for seed in range(lo, hi + 1):
        a = k.CreateAgent(f'a{seed}'); out = []
        a.RegisterForPrintEvent(S.smlEVENT_PRINT, lambda mid, ud, ag, msg: out.append(msg), None)
        os.chdir(o.dir)
        src = a.ExecuteCommandLine('source ' + o.load)
        if o.chunk: a.ExecuteCommandLine('chunk ' + o.chunk)
        m = re.search(r'Total: (\d+) productions sourced', src)
        load_errors = len(re.findall(r'(?i)\berror\b', src)) + (0 if m else 1)
        user_rules = None
        st = a.ExecuteCommandLine('stats')
        mm = re.search(r'(\d+) productions \((\d+) default, (\d+) user, (\d+) chunks\)', st)
        if mm: default_rules, user_rules = int(mm.group(2)), int(mm.group(3))
        else: default_rules = None
        a.ExecuteCommandLine(f'srand {seed}')
        a.ExecuteCommandLine('trace 1')
        eps = []
        for ep in range(o.episodes):
            if ep: a.ExecuteCommandLine('init-soar'); a.ExecuteCommandLine('trace 1')
            out.clear(); acts=[]; t0 = time.time(); d0 = None
            st0 = a.ExecuteCommandLine('stats')
            m0 = re.search(r'(\d+) decisions', st0); d0 = int(m0.group(1)) if m0 else 0
            halted = False; steps = 0
            seen = 0
            for steps in range(1, o.cap + 1):
                a.RunSelf(1)
                n = a.GetNumberCommands()
                for i in range(n):
                    c = a.GetCommand(i)
                    if c.GetParameterValue('status') is None: acts.append(c.GetCommandName() + ':' + ','.join(str(c.GetParameterValue(k)) for k in ('name','argument1','argument2') if c.GetParameterValue(k)))
                    if c.GetParameterValue('status') is None: c.AddStatusComplete()
                if n: a.Commit(); a.ClearOutputLinkChanges()
                txt = out[-1] if out else ''
                tail = ''.join(out[seen:]); seen = len(out)
                if 'halted' in tail or a.GetRunState() == S.sml_RUNSTATE_HALTED:
                    halted = True; break
                if re.search(r'achieved - success|achieved all desireds|\S failed(?=\s|Interrupt|$)', tail) or 'TASK-RESULT' in tail:
                    break
            wall = time.time() - t0
            txt = ''.join(out)
            # top-level operators from the decision trace (depth 0: 'N: O: Oxx (name)' directly after the cycle number)
            tops = re.findall(r'(?m)^\s*\d+:    O: \S+ \(([^)]+)\)', txt)
            skip = {'initialize-agent-world','wait','goal-completed','next-desireds','clean-up-topstate'}
            topops = [t for t in tops if t not in skip and not t.startswith('initialize-')]
            st1 = a.ExecuteCommandLine('stats')
            m1 = re.search(r'(\d+) decisions', st1); d1 = int(m1.group(1)) if m1 else 0
            cpu = re.search(r'Kernel CPU Time:\s+([\d.]+)', st1)
            res = 'success' if 'TASK-RESULT: success' in txt else 'failure' if 'TASK-RESULT: failure' in txt else None
            mres = re.search(r'achieved - success|achieved all desireds|\S failed(?=\s|Interrupt|$)', txt)
            if res is None and mres: res = 'failure' if 'failed' in mres.group(0) else 'success'
            if res is None:  # the generated originals' own messages
                if 'The problem has been solved' in txt: res = 'success'
                elif re.search(r'(?i)failure state|task has failed', txt): res = 'failure'
            mm = re.search(r'(\d+) chunks\)', st1)
            g = lambda pat, t: int(re.search(pat, t).group(1)) if re.search(pat, t) else 0
            fir = g(r'(\d+) production firings', st1) - (g(r'(\d+) production firings', st0) if ep == 0 else 0)
            wmc = g(r'(\d+) wme changes', st1) - (g(r'(\d+) wme changes', st0) if ep == 0 else 0)
            wmmax = g(r'WM size: \d+ current, [\d.]+ mean, (\d+) maximum', st1)
            eps.append(dict(actions=len(acts), plan=acts[:40], top_ops=len(topops), top_plan=topops[:40], decisions=d1 - d0 if ep == 0 else d1, halted=halted, result=res, wall_s=round(wall, 3),
                            kernel_cpu_s=float(cpu.group(1)) if cpu else None,
                            chunks=int(mm.group(1)) if mm else None,
                            firings=fir, wme_changes=wmc, wm_max=wmmax,
                            runtime_errors=len(re.findall(r'(?i)\berror\b', txt)),
                            warnings=len(re.findall(r'(?i)\bwarning\b', txt))))
        rl = a.ExecuteCommandLine('print --rl')
        rl_rules = len(re.findall(r'^\S+\s+[\d.]+\s+-?[\d.eE+-]+\s*$', rl, re.M))
        print(json.dumps(dict(seed=seed, load_ok=bool(m), load_errors=load_errors, user_rules=user_rules,
                              default_rules=default_rules, rl_rules=rl_rules, episodes=eps)), flush=True)
        k.DestroyAgent(a)
    k.Shutdown()

main()
