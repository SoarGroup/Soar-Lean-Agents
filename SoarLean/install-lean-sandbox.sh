#!/usr/bin/env bash
# install-lean-sandbox.sh — install Lean 4.35.0 (the version agentgen and cmcsoar use) in a
# Claude cloud workspace, where release.lean-lang.org is blocked but GitHub is allowed.
# elan's own toolchain download fails there, so the toolchain is fetched from GitHub releases
# and linked into elan under the name the lean-toolchain files use.
# Usage:  bash install-lean-sandbox.sh      then  export PATH="$HOME/.elan/bin:$PATH"
# On your own computer use the standard elan installer instead.
# Written 16 November 2026 by Claude, supervised by John E. Laird; tested in a workspace that day.
set -euo pipefail

VER=4.35.0
TOOLCHAIN="leanprover/lean4:v${VER}"
DEST="$HOME/lean"

if "$HOME/.elan/bin/lean" --version 2>/dev/null | grep -q "version ${VER}"; then
  echo "Lean ${VER} already installed."; exit 0
fi

# 1. elan itself (installer script from GitHub; no default toolchain, since that download is blocked)
if [ ! -x "$HOME/.elan/bin/elan" ]; then
  curl -sSfL https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh -o /tmp/elan-init.sh
  bash /tmp/elan-init.sh -y --default-toolchain none
fi

# 2. Lean toolchain from GitHub releases (~600 MB); unpacked with Python because zstd is often missing
if [ ! -x "$DEST/lean-${VER}-linux/bin/lean" ]; then
  curl -sSfL -o /tmp/lean.tar.zst \
    "https://github.com/leanprover/lean4/releases/download/v${VER}/lean-${VER}-linux.tar.zst"
  python3 -c "import zstandard" 2>/dev/null || pip install --break-system-packages -q zstandard
  mkdir -p "$DEST"
  python3 - "$DEST" <<'EOF'
import sys, tarfile, zstandard
with open('/tmp/lean.tar.zst', 'rb') as f:
    tarfile.open(fileobj=zstandard.ZstdDecompressor().stream_reader(f), mode='r|').extractall(sys.argv[1])
EOF
  rm -f /tmp/lean.tar.zst
fi

# 3. Register it with elan and make it the default
"$HOME/.elan/bin/elan" toolchain link "$TOOLCHAIN" "$DEST/lean-${VER}-linux"
"$HOME/.elan/bin/elan" default "$TOOLCHAIN"

"$HOME/.elan/bin/lean" --version
"$HOME/.elan/bin/lake" --version
echo 'Done. Run: export PATH="$HOME/.elan/bin:$PATH"'
