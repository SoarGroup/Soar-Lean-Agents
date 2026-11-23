"""Convert PDDL problems to Soar agents (path B) and run them, checking each plan against the PDDL.

usage: python3 run_pddl.py DOMAIN_DIR PROBLEM [PROBLEM ...] [--seeds 1,2,3] [--cap N] [--chunk never]

For each problem: pddl2ws.py -> <task>-spec.py and the world file; worldspec_py.py json -> <task>-worldspec.json;
spec_backend.py -> <task>-rules.soar; then Soar (soar_sml of a 9.6.50 kernel; the library uses $) runs the agent
decision by decision, marking each perform-action complete, with `chunk <mode>` set after loading. Every action
is recorded with all its arguments, and the plan is checked by an independent PDDL validator (unified-planning's
sequential plan validator on the original domain and problem files).
Environment: WORLDGEN (folder with worldspec_py.py, spec_backend.py, convpass.py), PYTHONPATH with soar_sml.
"""
import argparse, json, os, re, subprocess, sys, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
WG = Path(os.environ.get('WORLDGEN', '/home/claude/worldgen'))


def build(dom_dir, prob):
    dom = dom_dir / 'domain.pddl'; pf = dom_dir / 'problems' / prob
    agent = dom_dir / 'soar' / Path(prob).stem
    r = subprocess.run([sys.executable, str(HERE / 'pddl2ws.py'), str(dom), str(pf), str(agent)], capture_output=True, text=True)
    if r.returncode != 0: return None, r.stdout.strip()
    spec = next(agent.glob('*-spec.py')); task = spec.name[:-len('-spec.py')]
    world = next(agent.glob('init-*.world'))
    env = dict(os.environ, PYTHONPATH=str(WG))
    j = agent / f'{task}-worldspec.json'
    r1 = subprocess.run([sys.executable, str(WG / 'worldspec_py.py'), str(spec), 'json', str(world), str(j)], capture_output=True, text=True, env=env)
    if r1.returncode != 0: return None, 'json: ' + (r1.stderr or r1.stdout)[-400:]
    r2 = subprocess.run([sys.executable, str(WG / 'spec_backend.py'), str(j), str(agent / f'{task}-rules.soar')], capture_output=True, text=True, env=env)
    if r2.returncode != 0: return None, 'rules: ' + (r2.stderr or r2.stdout)[-400:]
    nrules = len(re.findall(r'(?m)^sp \{', (agent / f'{task}-rules.soar').read_text()))
    return dict(agent=agent, task=task, loader=agent / f'{task}.soar', nrules=nrules), 'ok'


def run(agent, loader, seed, cap, chunk, extra=None):
    import soar_sml as S
    k = S.Kernel.CreateKernelInNewThread(0); a = k.CreateAgent('a')
    cwd = os.getcwd(); os.chdir(agent)
    text = Path(loader).read_text()
    lib = re.search(r'pushd "([^"]+)"', text).group(1)
    for c in [f'pushd "{lib}"', 'source soar-library.soar', 'popd', 'source ' + re.search(r'(?m)^source (\S+-rules\.soar)', text).group(1)]:
        r = a.ExecuteCommandLine(c)
        if 'rror' in r and 'source' in c: raise SystemExit('LOAD FAILED: ' + r[-600:])
    for e in extra or []:
        r = a.ExecuteCommandLine(f'source {e}')
        if 'rror' in r: raise SystemExit('EXTRA FAILED: ' + r[-400:])
    a.ExecuteCommandLine(f'chunk {chunk}')
    chunk_state = a.ExecuteCommandLine('chunk ?').strip().splitlines()[:3]
    a.ExecuteCommandLine('watch 0'); a.ExecuteCommandLine(f'srand {seed}')
    acts, t0, outcome = [], time.time(), 'cap'
    for step in range(cap):
        a.RunSelf(1)
        for i in range(a.GetNumberCommands()):
            c = a.GetCommand(i)
            if c.GetCommandName() == 'perform-action' and c.GetParameterValue('status') is None:
                args, n = [], 1
                while c.GetParameterValue(f'argument{n}') is not None:
                    args.append(c.GetParameterValue(f'argument{n}')); n += 1
                acts.append([c.GetParameterValue('name')] + args)
                c.AddStatusComplete()
        a.Commit(); a.ClearOutputLinkChanges()
        if re.search(r'\^failure', a.ExecuteCommandLine('print s1')): outcome = 'failure'; break
        if 'success' in a.ExecuteCommandLine('print (s1 ^success *)'): outcome = 'success'; break
    st = a.ExecuteCommandLine('stats')
    chunks = len(re.findall(r'(?m)^chunk', a.ExecuteCommandLine('print --chunks')))
    k.Shutdown(); os.chdir(cwd)
    return dict(seed=seed, outcome=outcome, decisions=step + 1, n_actions=len(acts), actions=acts,
                seconds=round(time.time() - t0, 1), cpu=float(re.search(r'Kernel CPU Time:\s+([\d.]+)', st).group(1)),
                chunks_learned=chunks, chunk_setting=chunk_state)


def validate(dom, prob, acts):
    from unified_planning.io import PDDLReader
    from unified_planning.shortcuts import get_environment, PlanValidator
    from unified_planning.plans import SequentialPlan, ActionInstance
    env = get_environment(); env.credits_stream = None; env.error_used_name = False
    p = PDDLReader().parse_problem(str(dom), str(prob))
    sys.path.insert(0, str(HERE)); from pddl2ws import soar_name
    objs = {soar_name(o.name.lower()): o for o in p.all_objects}
    acts_by = {x.name.lower(): x for x in p.actions}
    plan = SequentialPlan([ActionInstance(acts_by[a[0]], [objs[x.lower()] for x in a[1:]]) for a in acts])
    with PlanValidator(problem_kind=p.kind, plan_kind=plan.kind) as v:
        r = v.validate(p, plan)
    return r.status.name


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('domain_dir'); ap.add_argument('problems', nargs='+')
    ap.add_argument('--seeds', default='1,2,3'); ap.add_argument('--cap', type=int, default=20000)
    ap.add_argument('--chunk', default='never')
    ap.add_argument('--extra', action='append', help='an extra Soar file sourced after the task rules (experiments only)')
    args = ap.parse_args()
    dd = Path(args.domain_dir).resolve()
    out = []
    for prob in args.problems:
        info, msg = build(dd, prob)
        if info is None:
            print(json.dumps(dict(problem=prob, status='not converted', reason=msg))); out.append(dict(problem=prob, status='not converted', reason=msg)); continue
        for seed in [int(s) for s in args.seeds.split(',')]:
            res = run(info['agent'], info['loader'], seed, args.cap, args.chunk, [str(Path(e).resolve()) for e in args.extra or []])
            res['extra'] = args.extra or []
            res['valid'] = validate(dd / 'domain.pddl', dd / 'problems' / prob, res['actions']) if res['outcome'] == 'success' else '-'
            res.update(problem=prob, rules=info['nrules'], chunk=args.chunk)
            (info['agent'] / (f'run-seed{seed}' + ('-extra' if args.extra else '') + '.json')).write_text(json.dumps(res, indent=1))
            print(json.dumps({k: res[k] for k in ('problem', 'seed', 'outcome', 'decisions', 'n_actions', 'valid', 'cpu', 'chunks_learned', 'rules')}), flush=True)
            out.append(res)
    return out


if __name__ == '__main__':
    main()
