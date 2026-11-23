#!/usr/bin/env bash
# A fresh vault: Obsidian config and one unrelated note, no examples of the skills' conventions
set -euo pipefail
mkdir -p vault/.obsidian
printf '# Inbox\n\n- Ideas for the weekend\n' > vault/Inbox.md
printf -- '# Errands\n\n- [ ] Renew bike insurance #cal 📅 2026-12-15\n- [ ] Buy stamps 📅 2026-12-02\n' > vault/Errands.md
