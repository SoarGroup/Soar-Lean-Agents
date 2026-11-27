# Tools for the English-derived family agents (25 November 2026)

- `build.sh DIR`: spec -> `<task>-worldspec.json` and `.lean` (worldspec_py.py), rules (spec_backend.py, path B), loader. Set `WG` to `SoarLean/worldgen`.
- `common.py`: writes `.world` files (objects and predicate tuples).
- `run3.py`: run2.py (the family runner) plus the world-convention end test used by run_agent.py: an episode ends at `(s1 ^failure)` or at `(s1 ^success)` once no phase or loop remains. run2.py alone never sees these agents finish. `run2.py` is included because run3.py is a copy of it.
- `batch_settings3.py ROOT english OUT.jsonl`: every agent in `list-english.txt` (set `LIST=english-tools/list-english.txt CAPS=english-tools/caps-english.json`, paths relative to ROOT = Tasks/Families) under chunk never / only / always, seeds 1-3, through run3.py.
- `caps-english.json`: decision caps (the search tasks need more than the families' 3,000).

Note on names: the world-file reader treats a trailing `1` on a value as a sense marker and drops it (`d1` becomes `d`), so object names here avoid a trailing 1 (small/medium/large, one ... eight, missionary-a).
