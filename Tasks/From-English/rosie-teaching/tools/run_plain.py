"""Run a standard-Soar Rosie agent (tools/rosie_plain.py), or check an example state.

  python3 run_plain.py DIR LOADER.soar [--seed N] [--cap N] [--json] [--extra FILE]
      Runs decision by decision; records the plan from the 'ACTION: name arg1 arg2' lines that the agent prints when
      the top state selects a task operator; stops at (s1 ^failure *), at (s1 ^success *), at halt, or at the cap.
      A failure takes precedence over a success. Output as tools/run_agent.py, so check_plan.py and check_moves.py
      read it unchanged.
  python3 run_plain.py DIR LOADER.soar --check RULES.soar
      Loads the default rules and RULES.soar (rules whose initial state is an example world), runs 2 decisions
      (initialization only) and prints whether the top state has ^success and ^failure."""
import argparse, json, os, re, sys, time
import soar_sml as S


def load(a, d, loader, rules):
    os.chdir(d)
    for line in open(loader).read().splitlines():
        line = line.strip()
        if not line or line.startswith('#'): continue
        if rules and line.startswith('source ') and line.endswith('-rules.soar'): line = 'source ' + rules
        r = a.ExecuteCommandLine(line)
        if 'rror' in r: print('LOAD:', r[-800:], file=sys.stderr)


def main():
    p = argparse.ArgumentParser()
    p.add_argument('dir'); p.add_argument('loader')
    p.add_argument('--seed', type=int, default=1); p.add_argument('--cap', type=int, default=5000)
    p.add_argument('--check'); p.add_argument('--json', action='store_true')
    p.add_argument('--extra', action='append')
    args = p.parse_args()
    k = S.Kernel.CreateKernelInNewThread(0); a = k.CreateAgent('a'); out = []
    a.RegisterForPrintEvent(S.smlEVENT_PRINT, lambda mid, ud, ag, msg: out.append(msg), None)
    load(a, args.dir, args.loader, args.check)
    for extra in args.extra or []:
        print('EXTRA:', a.ExecuteCommandLine('source ' + extra).strip().splitlines()[-1:], file=sys.stderr)
    a.ExecuteCommandLine('watch 0'); a.ExecuteCommandLine(f'srand {args.seed}')
    if args.check:
        a.RunSelf(2)
        s1 = a.ExecuteCommandLine('print s1')
        print(json.dumps({'rules': args.check, 'success': '^success' in s1, 'failure': '^failure' in s1}))
        k.Shutdown(); return
    acts, t0, outcome, seen = [], time.time(), 'cap', 0
    for step in range(args.cap):
        a.RunSelf(1)
        text = ''.join(out[seen:]); seen = len(out)
        acts += [m.split() for m in re.findall(r'ACTION: ([^\n]+)', text)]
        s1 = a.ExecuteCommandLine('print s1')
        if '^failure' in s1: outcome = 'failure'; break
        if '^success' in s1: outcome = 'success'; break
        if a.GetRunState() == S.sml_RUNSTATE_HALTED: outcome = 'halted'; break
    st = a.ExecuteCommandLine('stats')
    chunks = re.search(r'(\d+) chunks\)', st)
    res = dict(outcome=outcome, decisions=step + 1, actions=acts, n_actions=len(acts), seconds=round(time.time() - t0, 1),
               cpu=re.search(r'Kernel CPU Time:\s+([\d.]+)', st).group(1), chunks=int(chunks.group(1)) if chunks else None)
    if args.json: print(json.dumps(res))
    else:
        print(f"{outcome} at decision {step + 1}; {len(acts)} actions; {res['seconds']} s")
        for x in acts: print('  ', ' '.join(x))
    k.Shutdown()


if __name__ == '__main__':
    main()
