#!/bin/bash
# build.sh DIR: spec -> worldspec.json (path B input), Lean description, rules (spec_backend.py), loader.
# Loader uses the repo-relative library path; LIB overrides it for local runs.
set -e
WG=${WG:?set WG to SoarLean/worldgen}
D=$(cd "$1" && pwd); t=$(basename "$D")
cd "$D"
w=$(ls init-*.world)
python3 "$WG/worldspec_py.py" "$t-spec.py" json "$w" "$t-worldspec.json" >/dev/null
python3 "$WG/worldspec_py.py" "$t-spec.py" lean "$t-worldspec.lean" >/dev/null
(cd "$WG" && python3 spec_backend.py "$D/$t-worldspec.json" "$D/$t-rules.soar" >/dev/null)
lib=${LIB:-../../../../../Soar/soar-library}
printf '## %s (from English): loads the Soar library and the generated rules.\npushd "%s"\nsource soar-library.soar\npopd\nsource %s-rules.soar\n' "$t" "$lib" "$t" > "$t.soar"
echo "built $t: $(grep -c '^sp {' $t-rules.soar) rules"
