#!/usr/bin/env bash
# A fresh vault: Obsidian config and one unrelated note, no examples of the skills' conventions
set -euo pipefail
mkdir -p vault/.obsidian
printf '# Inbox\n\n- Ideas for the weekend\n' > vault/Inbox.md
