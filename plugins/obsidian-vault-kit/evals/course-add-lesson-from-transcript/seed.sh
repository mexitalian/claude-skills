#!/usr/bin/env bash
# Copies the repo's example vault into the run's empty workspace as ./vault
set -euo pipefail
case_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo="$(cd "$case_dir/../../../.." && pwd)"
cp -R "$repo/examples/Example vault" ./vault
