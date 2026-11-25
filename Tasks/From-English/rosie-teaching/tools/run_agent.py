"""Run a Rosie-pilot agent (world conventions) against the stub environment, or check an example state.

  python3 run_agent.py DIR LOADER.soar [--seed N] [--cap N] [--rules RULES.soar]
      Runs decision by decision; every new perform-action is marked complete (env-complete mode of the test set);
      stops at a failure on the top state, at (s1 ^success *), or at the cap; a failure takes precedence over a success. Prints the actions, decisions and outcome.
      --rules sources RULES.soar in place of the loader's task rules (used for the state checks).
  python3 run_agent.py DIR LOADER.soar --check RULES.soar
      Loads the library and RULES.soar (rules whose initial world is an example state), runs 3 decisions
      (initialization only, no task operator applied), and prints goal-met and failure as found in that world.
Needs the soar_sml module of a Soar 9.6.6 or 9.6.50 build (the library uses $)."""
import argparse, json, os, re, sys, time
import soar_sml as S

def load(a, d, loader, rules):
    os.chdir(d)
    text = open(loader).read()
    lib = re.search(r'pushd "([^"]+)"', text).group(1)
    for c in [f'pushd "{lib}"', 'source soar-library.soar', 'popd', 'source ' + (rules or re.search(r'(?m)^source (\S+-rules\.soar)', text).group(1))]:
        r = a.ExecuteCommandLine(c)
        if 'rror' in r and 'source' in c: print('LOAD:', r[-800:])

def main():
    p = argparse.ArgumentParser()
    p.add_argument('dir'); p.add_argument('loader')
    p.add_argument('--seed', type=int, default=1); p.add_argument('--cap', type=int, default=5000)
    p.add_argument('--rules'); p.add_argument('--check'); p.add_argument('--json', action='store_true')
    p.add_argument('--watch', default='0')
    p.add_argument('--extra', action='append', help='an extra Soar file sourced after the task (experiments); repeatable')
    p.add_argument('--flags', help="extra ^flag-override values, e.g. '^iterative-step tie-impasse'")
    args = p.parse_args()
    k = S.Kernel.CreateKernelInNewThread(0); a = k.CreateAgent('a'); out = []
    a.RegisterForPrintEvent(S.smlEVENT_PRINT, lambda mid, ud, ag, msg: out.append(msg), None)
    load(a, args.dir, args.loader, args.check or args.rules)
    for extra in args.extra or []:
        print('EXTRA:', a.ExecuteCommandLine('source ' + extra).strip().splitlines()[-1:], file=sys.stderr)
    if args.flags:
        a.ExecuteCommandLine('sp {run*flag-override (state <s> ^superstate nil) --> (<s> ^flag-override <f>) (<f> %s)}' % args.flags)
    a.ExecuteCommandLine('watch ' + args.watch); a.ExecuteCommandLine(f'srand {args.seed}')
    if args.check:
        a.RunSelf(3)
        goal = bool(re.search(r'goal-met true', a.ExecuteCommandLine('print (* ^type task)')))
        fail = bool(re.search(r'\^failure', a.ExecuteCommandLine('print s1')))
        print(json.dumps({'rules': args.check, 'goal-met': goal, 'failure': fail}))
        k.Shutdown(); return
    acts, t0, outcome = [], time.time(), 'cap'
    for step in range(args.cap):
        a.RunSelf(1)
        for i in range(a.GetNumberCommands()):
            c = a.GetCommand(i)
            if c.GetCommandName() == 'perform-action' and c.GetParameterValue('status') is None:
                acts.append([c.GetParameterValue('name'), c.GetParameterValue('argument1'), c.GetParameterValue('argument2')])
                c.AddStatusComplete()
            elif c.GetParameterValue('status') is None:   # a declared output form (World-Conventions L10-018)
                ps = [(c.GetChild(q).GetAttribute(), c.GetChild(q).GetValueAsString()) for q in range(c.GetNumberChildren())]
                acts.append([c.GetCommandName()] + [v for _, v in ps])
                c.AddStatusComplete()
        a.Commit(); a.ClearOutputLinkChanges()
        # A losing condition takes precedence over the goal (John, 2026-11-16): a top state with both reports failure.
        if re.search(r'\^failure', a.ExecuteCommandLine('print s1')): outcome = 'failure'; break
        if 'success' in a.ExecuteCommandLine('print (s1 ^success *)'):
            # With phases or a loop (World-Conventions L8-026 to L8-029) a phase's success is not the end: the run ends
            # when the library's top-goal halt rule reports the task done.
            s1 = a.ExecuteCommandLine('print --depth 2 s1')
            if not re.search(r'\^next-desireds|\^repeat-count|\^termination-desireds', s1) or \
               re.search(r'achieved - success|achieved all desireds|completed its repeat count|achieved termination desireds', ''.join(out)):
                outcome = 'success'; break
    st = a.ExecuteCommandLine('stats')
    res = dict(outcome=outcome, decisions=step + 1, actions=acts, n_actions=len(acts), seconds=round(time.time() - t0, 1),
               cpu=re.search(r'Kernel CPU Time:\s+([\d.]+)', st).group(1))
    if args.json: print(json.dumps(res))
    else:
        print(f"{outcome} at decision {step + 1}; {len(acts)} actions; {res['seconds']} s")
        for x in acts: print('  ', ' '.join(x))
        tail = ''.join(out).strip().splitlines()
        print('\n'.join(l for l in tail if l.startswith(('Move', 'Ferry', 'Cross', 'Place', 'Opponent', 'Lost', 'TASK')))[-3000:])
    k.Shutdown()

if __name__ == '__main__':
    main()
