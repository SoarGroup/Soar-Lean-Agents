"""Probe the search and cost settings of a generated task and recommend its ^flag-override (intake checklist, step P6).

usage:
  python3 probe_settings.py --lib LIBDIR --dir TASKDIR --load TASK.soar [--seeds 1-3] [--cap 3000]
                            [--configs default|cost|all|'it/cm/op,...'] [--checker 'python3 check.py {plan}']
                            [--edges model.json] [--out probe.json] [--options options.json]

What it does
  1. For every candidate configuration (iterative-step / cost-metric / optimize) it loads the task with an extra rule that adds a
     ^flag-override object with those flags, runs each seed to the cap, and records: solved, decisions, plan length (the world's
     ^applied-count, the number of task operators applied in the top state) and, when --checker is given, the plan cost the
     checker prints (it receives the plan, one action per line, in the file named by {plan}).
  2. It picks the configuration that (a) solves every seed, (b) has the best plan (lowest checker cost, else fewest operators,
     summed over seeds), (c) uses the fewest decisions (summed). Ties go to the library defaults. A configuration that solves
     fewer seeds never wins, even when it is faster.
  3. With --edges (a model graph, as in graph_models.py: {"edges": {state: [[next, cost], ...]}, "start": s, "goals": [...]})
     it also reports the choice profile of the model (P6): along a fewest-operator solution, how many states offer a choice.
     Many forced steps per choice favour tie-impasse; a choice at almost every step favours operator. This is advice only:
     the measured runs decide.
  4. It writes probe.json and, with --options, merges the recommendation into options.json under "measured" and "search".

The flags the task already sets itself are not overridden: those configurations are run with the task's own values and
reported as such ("fixed"). Defaults (library v2.34 to v2.41): iterative-step operator, cost-metric none, optimize false; the depth limit is
the max-evaluation-depth flag (library v2.37 on), default 12.
"""
import argparse, json, os, re, subprocess, sys, tempfile, time

DEFAULT = ('operator', 'none', 'false')
DEPTH_LIMIT = 12  # library default of ^flags.max-evaluation-depth (v2.37 on)
SETS = {
    'default': [DEFAULT, ('tie-impasse', 'none', 'false')],
    'cost':    [DEFAULT, ('operator', 'unit', 'true'), ('tie-impasse', 'unit', 'true')],
    'all':     [DEFAULT, ('tie-impasse', 'none', 'false'), ('operator', 'unit', 'true'), ('tie-impasse', 'unit', 'true')],
}
FLAGS = ('iterative-step', 'cost-metric', 'optimize')


def task_sets(taskdir, load):
    """Flags the task's own rules already set (any ^flag-override value in its files)."""
    txt = ''
    for f in os.listdir(taskdir):
        if f.endswith('.soar') and not f.startswith('_probe'):
            txt += open(os.path.join(taskdir, f), errors='ignore').read()
    return {k: m.group(1) for k in FLAGS for m in [re.search(r'\^%s\s+([\w-]+)' % k, txt)] if m}


def run_one(lib, taskdir, load, cfg, seed, cap, fixed):
    import soar_sml as S
    kv = [(k, v) for k, v in zip(FLAGS, cfg) if k not in fixed]
    k = S.Kernel.CreateKernelInNewThread(0); a = k.CreateAgent('probe'); out = []
    a.RegisterForPrintEvent(S.smlEVENT_PRINT, lambda mid, ud, ag, msg: out.append(msg), None)
    cwd = os.getcwd(); os.chdir(taskdir)
    try:
        a.ExecuteCommandLine('output agent-logs 1 off')
        if lib:
            a.ExecuteCommandLine('pushd "%s"' % lib); a.ExecuteCommandLine('source soar-library.soar'); a.ExecuteCommandLine('popd')
        src = a.ExecuteCommandLine('source ' + load)
        if kv:
            a.ExecuteCommandLine('sp {probe*flag-override (state <s> ^superstate nil) --> (<s> ^flag-override <f>) (<f> %s)}'
                                 % ' '.join('^%s %s' % p for p in kv))
        a.ExecuteCommandLine('srand %d' % seed); a.ExecuteCommandLine('watch 0')
        plan, t0, halted = [], time.time(), False
        for _ in range(cap):
            a.RunSelf(1)
            for i in range(a.GetNumberCommands()):
                c = a.GetCommand(i)
                plan.append(c.GetCommandName() + ' ' + ' '.join(
                    '%s=%s' % (c.GetChild(j).GetAttribute(), c.GetChild(j).GetValueAsString()) for j in range(c.GetNumberChildren())))
                if c.GetParameterValue('status') is None: c.AddStatusComplete()
            if a.GetNumberCommands(): a.Commit(); a.ClearOutputLinkChanges()
            if a.GetRunState() == S.sml_RUNSTATE_HALTED or 'halted' in ''.join(out[-3:]): halted = True; break
            if 'success' in a.ExecuteCommandLine('print (s1 ^success *)'): halted = True; break   # tasks that mark success and wait
        txt = ''.join(out)
        st = a.ExecuteCommandLine('stats'); dec = int(re.search(r'(\d+) decisions', st).group(1))
        w = re.search(r'\^world (\w+)', a.ExecuteCommandLine('print S1'))
        ac = re.search(r'\^applied-count (\d+)', a.ExecuteCommandLine('print ' + w.group(1))) if w else None
        ok = halted and 'TASK-RESULT: failure' not in txt and not re.search(r'(?i)failure state|task has failed', txt)
        return dict(seed=seed, solved=bool(ok), decisions=dec, operators=int(ac.group(1)) if ac else len(plan) or None,
                    plan=plan, wall_s=round(time.time() - t0, 2), load_error=bool(re.search(r'\bError\b', src)))
    finally:
        os.chdir(cwd); k.Shutdown()


def cost_of(checker, plan):
    if not checker: return None
    fd, p = tempfile.mkstemp(suffix='.plan'); os.write(fd, '\n'.join(plan).encode()); os.close(fd)
    try:
        r = subprocess.run(checker.replace('{plan}', p), shell=True, capture_output=True, text=True, timeout=120)
        m = re.search(r'cost[:= ]+([\d.]+)', r.stdout, re.I)
        return float(m.group(1)) if m else None
    finally: os.unlink(p)


def choice_profile(edges, start, goals):
    """P6: along one fewest-operator solution of the model, how many states offer more than one move."""
    from collections import deque
    prev, q = {start: None}, deque([start])
    while q:
        s = q.popleft()
        if s in goals: break
        for n, _ in edges.get(s, []):
            if n not in prev: prev[n] = s; q.append(n)
    goal = next((g for g in goals if g in prev), None)
    if goal is None: return dict(solvable=False)
    path, s = [], goal
    while s is not None: path.append(s); s = prev[s]
    path.reverse()
    choices = sum(1 for s in path[:-1] if len(edges.get(s, [])) > 1)
    steps = len(path) - 1
    advice = ('tie-impasse' if steps > DEPTH_LIMIT and choices <= DEPTH_LIMIT or (steps and choices / steps < 0.34)
              else 'operator')
    return dict(solvable=True, steps=steps, choices=choices, forced=steps - choices, advice=advice,
                reason='%d choices in %d steps; the depth limit (max-evaluation-depth) is %d and operator depth counts every step, tie-impasse only choices'
                       % (choices, steps, DEPTH_LIMIT))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--lib'); ap.add_argument('--dir', required=True); ap.add_argument('--load', required=True)
    ap.add_argument('--seeds', default='1-3'); ap.add_argument('--cap', type=int, default=3000)
    ap.add_argument('--configs', default='all'); ap.add_argument('--checker'); ap.add_argument('--edges')
    ap.add_argument('--out', default='probe.json'); ap.add_argument('--options')
    o = ap.parse_args()
    lo, hi = map(int, o.seeds.split('-')); seeds = list(range(lo, hi + 1))
    cfgs = SETS.get(o.configs) or [tuple(c.split('/')) for c in o.configs.split(',')]
    fixed = task_sets(o.dir, o.load)
    rows = []
    for cfg in cfgs:
        eff = tuple(fixed.get(k, v) for k, v in zip(FLAGS, cfg))
        if any(r['effective'] == list(eff) for r in rows): continue      # the task fixes the flags that differ
        runs = []
        for sd in seeds:
            r = run_one(o.lib, o.dir, o.load, cfg, sd, o.cap, fixed); r['cost'] = cost_of(o.checker, r['plan']); runs.append(r)
        rows.append(dict(config=list(cfg), effective=list(eff), runs=[{k: v for k, v in r.items() if k != 'plan'} for r in runs],
                         solved=sum(r['solved'] for r in runs), decisions=sum(r['decisions'] for r in runs),
                         quality=(sum(r['cost'] for r in runs) if all(r['cost'] is not None for r in runs)
                                  else sum(r['operators'] or 0 for r in runs)),
                         quality_kind='checker cost' if o.checker else 'operators'))
        print('%-32s solved %d/%d  quality %s  decisions %d' % ('/'.join(eff), rows[-1]['solved'], len(seeds),
                                                                 rows[-1]['quality'], rows[-1]['decisions']), file=sys.stderr)
    full = [r for r in rows if r['solved'] == len(seeds)]
    pool = full or rows
    best = min(pool, key=lambda r: (-r['solved'], r['quality'] if full else 0, r['decisions'], list(r['effective']) != list(DEFAULT)))
    override = {k: v for k, v in zip(FLAGS, best['effective']) if k not in fixed and v != dict(zip(FLAGS, DEFAULT))[k]}
    rep = dict(task=os.path.join(o.dir, o.load), library=o.lib, seeds=seeds, cap=o.cap, fixed_by_task=fixed, configs=rows,
               recommended=dict(effective=dict(zip(FLAGS, best['effective'])), override=override,
                                solved_all=bool(full), rule=('(<f> %s)' % ' '.join('^%s %s' % kv for kv in override.items())
                                                             if override else 'no override: library defaults')),
               warnings=([] if full else ['no configuration solved every seed; raise --cap or fix the task before choosing']))
    if o.edges:
        m = json.load(open(o.edges)); rep['choice_profile'] = choice_profile(m['edges'], m['start'], set(m['goals']))
    json.dump(rep, open(o.out, 'w'), indent=1)
    if o.options:
        opts = json.load(open(o.options)) if os.path.exists(o.options) else {}
        opts.setdefault('measured', {})['probe_settings'] = {k: rep[k] for k in ('seeds', 'cap', 'configs')}
        opts['search'] = rep['recommended']
        json.dump(opts, open(o.options, 'w'), indent=1)
    print(json.dumps(rep['recommended'], indent=1))


if __name__ == '__main__':
    main()
