#!/usr/bin/env bash
set -euo pipefail

LIST_FILE="${1:-/tmp/extensions.txt}"
BIN="${OPENVSCODE_SERVER_DIR:-/opt/openvscode-server}/bin/openvscode-server"

if [[ -f "$LIST_FILE" ]]; then
  # Filter comments and empty lines
  grep -vE '^\s*(#|$)' "$LIST_FILE" | while read -r ext; do
    echo "Installing extension: $ext"
    "$BIN" --install-extension "$ext" \
      --extensions-dir /data/extensions \
      --user-data-dir /data/user-data || true
  done
fi


