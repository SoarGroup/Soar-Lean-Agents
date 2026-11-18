"""Write options.json for a task package. usage (from a task generator):
  import emit_options; emit_options.write('options.json', rules_file, answers, edges, start, goals, h=None, score=None, measured=None)
answers: {'Q1': ('yes', 'English sentence or person', 'stated'|'assumption'), ...}.  Raises if check_options finds an error or if the flags in the
rules file differ from the flags the probes recommend for a question the answers settle (cost-metric, optimize)."""
import json, probe_graph, check_options
def write(path, rules_file, answers, edges, start, goals, h=None, score=None, measured=None):
    text = open(rules_file).read(); flags = check_options.flags(text)
    rec = probe_graph.report(edges, start, goals, h=h, score=score)
    lint = check_options.check(text); errs = [x for x in lint if x[1] == 'E']
    if errs: raise SystemExit('check_options errors: %s' % errs)
    for k in ('cost-metric', 'optimize'):
        if k in rec['flags'] and flags.get(k) != rec['flags'][k]:
            rec.setdefault('warnings', []).append(f'rules set ^{k} {flags.get(k)} but the probes recommend {rec["flags"][k]}')
        if k not in rec['flags'] and flags.get(k, 'none' if k == 'cost-metric' else 'false') not in ('none', 'false'):
            rec.setdefault('warnings', []).append(f'rules set ^{k} {flags[k]} but probe P1 says cost does not change the answer')
    out = dict(answers={q: dict(answer=a[0], basis=a[1], kind=a[2]) for q, a in answers.items()}, flags=flags,
               probes=dict(recommended=rec['flags'], reasons=rec['reasons'], warnings=rec['warnings'], optimum=rec.get('optimum')),
               lint=[dict(id=i, level=l, message=m) for i, l, m in lint], measured=measured or {})
    json.dump(out, open(path, 'w'), indent=1); return out
