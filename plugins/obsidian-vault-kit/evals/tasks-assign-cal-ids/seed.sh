#!/usr/bin/env bash
# Copies the repo's example vault into the run's empty workspace as ./vault
set -euo pipefail
case_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo="$(cd "$case_dir/../../../.." && pwd)"
cp -R "$repo/examples/Example vault" ./vault
printf -- '# Errands\n\n- [ ] Renew bike insurance #cal 📅 2026-12-15\n- [ ] Buy stamps 📅 2026-12-02\n' > vault/Notes/Errands.md
