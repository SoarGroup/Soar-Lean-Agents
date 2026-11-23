"""Parse every domain/problem pair under Tasks/pddl; plan the smallest problems.

Usage: python3 check_pddl.py <Tasks/pddl> [n_to_solve_per_domain]
"""
import sys, re, signal
from pathlib import Path
from unified_planning.io import PDDLReader
from unified_planning.shortcuts import OneshotPlanner, get_environment

get_environment().credits_stream = None
get_environment().error_used_name = False
root = Path(sys.argv[1]); nsolve = int(sys.argv[2]) if len(sys.argv) > 2 else 2

def key(p):
    m = re.findall(r"\d+", p.name)
    return [int(x) for x in m] if m else [0]

report = []
for d in sorted(x for x in root.iterdir() if x.is_dir()):
    probs = sorted((d / "problems").glob("*.pddl"), key=key)
    parsed, failed, solved = 0, [], []
    for i, p in enumerate(probs):
        try:
            prob = PDDLReader().parse_problem(str(d / "domain.pddl"), str(p))
            parsed += 1
        except Exception as e:
            failed.append(f"{p.name}: {str(e)[:120]}")
            continue
        if i < nsolve:
            try:
                with OneshotPlanner(name="fast-downward") as planner:
                    r = planner.solve(prob, timeout=60)
                plan = r.plan
                solved.append(f"{p.name}: {r.status.name}, {len(plan.actions) if plan else '-'} actions")
            except Exception as e:
                solved.append(f"{p.name}: planner error {str(e)[:100]}")
    report.append((d.name, len(probs), parsed, failed, solved))

for name, n, parsed, failed, solved in report:
    print(f"{name}: {parsed}/{n} parsed")
    for f in failed[:3]:
        print(f"   PARSE FAIL {f}")
    for s in solved:
        print(f"   {s}")
