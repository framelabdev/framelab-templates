#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

docker build -f base/Dockerfile -t openvscode-base:latest .
docker build -f stacks/node.Dockerfile --build-arg BASE_IMAGE=openvscode-base:latest -t openvscode-node:latest .

echo "Built images: openvscode-base:latest, openvscode-node:latest"


