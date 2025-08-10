#!/usr/bin/env bash
set -euo pipefail

PORT="${PORT:-3000}"
HOST="${HOST:-0.0.0.0}"

ARGS=(
  "--host" "${HOST}"
  "--port" "${PORT}"
  "--telemetry-level" "off"
  "--user-data-dir" "/data/user-data"
  "--extensions-dir" "/data/extensions"
)

if [[ -n "${CONNECTION_TOKEN:-}" ]]; then
  ARGS+=("--connection-token" "${CONNECTION_TOKEN}")
elif [[ "${DISABLE_CONNECTION_TOKEN:-false}" == "true" || "${ALLOW_NO_TOKEN:-false}" == "true" ]]; then
  ARGS+=("--without-connection-token")
fi

exec "${OPENVSCODE_SERVER_DIR}/bin/openvscode-server" "${ARGS[@]}"


