# webtasks tools

`worldspec_py.py`: WorldSpec in Python, a stand-in for `rosiegen` where Lean cannot be built. A port of
`SoarLean/agentgen/WorldSpec/Sem.lean`, `WorldFile.lean` and `Json.lean`, plus a printer of the Lean
description. Checked against Lean's own export for fox-goose-bean (same JSON, same 7-move shortest plan).
Commands (`TASK.py` defines `TASK`): `lean OUT.lean`, `json WORLD OUT.json`, `check WORLD`,
`explore WORLD LIMIT`, `replay WORLD RUN.json`. Run with `PYTHONPATH` set to this folder.
It is not a substitute for the Lean checks: compare its JSON with `rosiegen json` once Lean builds.
