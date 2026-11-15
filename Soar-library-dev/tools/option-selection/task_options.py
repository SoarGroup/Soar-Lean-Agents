"""Run the option probes on the generated tasks and write options.json for each. usage: task_options.py [outdir]
For every task: build the model graph, run probe_graph.report, check the model against the Soar agent (operator count equals the model's fewest operators),
run check_options on the generated rules, and write options.json (emit_options)."""
import os, sys, subprocess, json
sys.path[:0] = ['/home/claude/worldgen']
import graph_models as M, probe_graph as P, check_options as CO, emit_options as EO, play
out = sys.argv[1] if len(sys.argv) > 1 else '/tmp/task-options'; os.makedirs(out, exist_ok=True)
lib = os.environ.get('WLIB', '/home/claude/soar-library-dev')
TASKS = [('eight-puzzle-3', 'gen_eight.py', dict(EP_STEPS='3'), 'eight-puzzle-rules.soar', lambda w: M.eight(3, w)),
         ('eight-puzzle-2', 'gen_eight.py', dict(EP_STEPS='2'), 'eight-puzzle-rules.soar', lambda w: M.eight(2, w)),
         ('water-jug', 'gen_waterjug.py', {}, 'water-jug-rules.soar', lambda w: M.waterjug(w)),
         ('hanoi-2', 'gen_hanoi.py', dict(HANOI_DISCS='2'), 'hanoi-rules.soar', lambda w: M.hanoi(2, w)),
         ('hanoi-3', 'gen_hanoi.py', dict(HANOI_DISCS='3'), 'hanoi-rules.soar', lambda w: M.hanoi(3, w))]
rows = []
for name, gen, env, rules, model in TASKS:
    e = dict(os.environ); e.update(env); subprocess.run(['python3', gen, 'flat'], env=e, check=True, cwd='/home/claude/worldgen')
    text = open('/home/claude/worldgen/' + rules).read(); row = dict(task=name)
    for w in (False, True):
        m = model(w); rep = P.report(m['edges'], m['start'], m['goals'], h=m['h'], score=m['score'])
        row['weighted' if w else 'unit'] = dict(flags=rep['flags'], reasons=rep['reasons'], warnings=rep['warnings'], optimum=rep.get('optimum'))
    m = model(False); row['model_fewest_operators'] = P._hops(m['edges'], m['start'], m['goals'])
    cap = 1200 if name == 'hanoi-3' else 6000
    if name != 'hanoi-3':   # hanoi-3 needs a 7-move look-ahead, beyond the library's depth limit: model only
        shutil_rules = rules; r = play.play(shutil_rules, 1, cap, lib=lib); row['agent_operators'] = len(r['actions']); row['agent_done'] = r['success']
    lint = CO.check(text); row['lint_errors'] = [x for x in lint if x[1] == 'E']
    answers = {'Q1': ('no', 'the English gives no cost, duration or effort for actions', 'assumption')}
    EO.write(f'{out}/{name}.options.json', '/home/claude/worldgen/' + rules, answers, m['edges'], m['start'], m['goals'], h=m['h'], score=m['score'])
    rows.append(row); print(json.dumps(row, default=str))
json.dump(rows, open(f'{out}/summary.json', 'w'), indent=1, default=str)
