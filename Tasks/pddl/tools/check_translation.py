"""Check a translated problem: a Fast Downward plan for the PDDL must replay to the goal in the WorldSpec semantics.

usage: python3 check_translation.py DOMAIN_DIR PROBLEM   (the agent folder soar/<problem stem> must exist)
Needs unified-planning with up-fast-downward, and WORLDGEN on PYTHONPATH (worldspec_py.py).
"""
import sys
from pathlib import Path
import worldspec_py as W
sys.path.insert(0, str(Path(__file__).resolve().parent)); from pddl2ws import soar_name
from unified_planning.io import PDDLReader
from unified_planning.shortcuts import OneshotPlanner, get_environment

env = get_environment(); env.credits_stream = None; env.error_used_name = False
dd = Path(sys.argv[1]); prob = sys.argv[2]
agent = dd / 'soar' / Path(prob).stem
t = W.load_task(str(next(agent.glob('*-spec.py'))))
st = W.initial(t, next(agent.glob('init-*.world')).read_text())
p = PDDLReader().parse_problem(str(dd / 'domain.pddl'), str(dd / 'problems' / prob))
with OneshotPlanner(name='fast-downward') as planner:
    plan = planner.solve(p, timeout=120).plan
steps = [(a.action.name.lower(), [soar_name(str(x).lower()) for x in a.actual_parameters]) for a in plan.actions]
print(f'{dd.name}/{prob}: goal before {W.goal_met(t, st)}; ', end='')
for n, args in steps:
    st = W.apply_op(t, st, n, args)
print(f'FD plan of {len(steps)} actions replays; goal after {W.goal_met(t, st)}')
