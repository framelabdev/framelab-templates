Param(
  [string]$OpenVSCodeVersion = "1.93.0"
)

$ErrorActionPreference = "Stop"
Set-Location -Path $PSScriptRoot

docker build -f base/Dockerfile --build-arg OPENVSCODE_VERSION=$OpenVSCodeVersion -t openvscode-base:latest .
docker build -f stacks/node.Dockerfile --build-arg BASE_IMAGE=openvscode-base:latest -t openvscode-node:latest .

Write-Host "Built images: openvscode-base:latest, openvscode-node:latest"


