#!/usr/bin/env bash
# Re-render the Mermaid diagrams in agentgen-pipeline-dataflow.md to PNGs in this folder.
# Requires: npm i -g @mermaid-js/mermaid-cli   (provides mmdc)
# Usage: ./render.sh   (set PUPPETEER_CONFIG=<file> to pass a puppeteer config, as CI does)
set -euo pipefail
cd "$(dirname "$0")"
names=(pipeline-1-main-path pipeline-2-english-to-lean-design pipeline-3-lean-design-to-tested-agent pipeline-4-revised-flow-soar-mcp)
tmp=$(mktemp -d); trap 'rm -rf "$tmp"' EXIT
python3 - "$tmp" "${names[@]}" <<'PY'
import re, sys
tmp, names = sys.argv[1], sys.argv[2:]
blocks = re.findall(r"```mermaid\n(.*?)```", open("agentgen-pipeline-dataflow.md").read(), re.S)
assert len(blocks) == len(names), f"{len(blocks)} diagrams in the .md but {len(names)} names in render.sh"
for n, b in zip(names, blocks):
    open(f"{tmp}/{n}.mmd", "w").write(b)
PY
for n in "${names[@]}"; do
  mmdc ${PUPPETEER_CONFIG:+-p "$PUPPETEER_CONFIG"} -i "$tmp/$n.mmd" -o "$n.png" -w 1600 -s 2 -b white
done
echo "Rendered ${#names[@]} PNGs"
