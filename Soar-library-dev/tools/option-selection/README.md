# Option-selection tools

Tools for choosing the cost and search options of a generated task, as described in
`Soar-library-dev/docs/Option-Selection-Guide-v1.md`. Unpacked from `option-selection-v1.2.zip` (14 Nov 2026).

- `probe_graph.py`: probes P0 to P5 on a model of a task instance (state graph).
- `check_options.py`: static check of the options in a rules file (`python3 check_options.py <task>-rules.soar`).
- `emit_options.py`: writes options.json from the answers, the probes and the check.
- `graph_models.py`, `task_options.py`: example task models and the driver that runs the probes on them.
- `test_options.py`: tests of the checker (`python3 test_options.py`; 12 negative and 2 positive cases).

The cost-graph P5 driver, `p5_costgraph.py`, is in `Soar-library-dev/tools/worldgen-v18.zip`.
