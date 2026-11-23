# Scripts, audit and safe editing

Read this before running `audit_vault.py` or `link_glossary.py`, before an audit, and before any bulk edit of notes.

## Scripts
In this skill's `scripts/` folder. They must run where the vault lives (Python 3.9+, standard library only). If the vault is on the user's computer and Claude works from elsewhere, ask once to copy them to a folder outside the vault, such as `<vaults folder>/_tools/`. Never put scripts inside a synced vault.

- `audit_vault.py <vault>`: read-only check of the whole vault. Core checks always run: broken `[[links]]` and `![[embeds]]`, orphan notes, unsafe file names, case and learning frontmatter, case sections and Log order, stalled and done-but-open cases, stale learnings, possible sensitive numbers (masked), `???` decision stubs, `.stignore`, Dashboard queries. Recall and course checks switch on when the vault has study notes or a `Courses/` folder. Options: `--stale-months 12`, `--only core`.
- `link_glossary.py <vault> [--apply]`: dry run by default. Reads `<vault>/glossary_terms.json` (or `--terms <file>`): see `assets/glossary_terms.example.json`. Links the first plain mention of each term per note, anchored on the word (`[[Glossary#Registration|Anmeldung]]`). It skips frontmatter, headings, tables, code, the glossary note itself and the sections listed in the file. Safe to re-run.

## Audit mode
Use when the user asks to check or tidy the vault, after a bulk import, or when opening an older vault.
1. Run `audit_vault.py`. It changes nothing.
2. Judge each finding before reporting: a difference may be a deliberate choice of the user. Report it as "differs from the skill" and ask whether to update the vault or leave it.
3. Report one short table (counts of FAIL / WARN / INFO, then findings grouped by area, worst first). Say what could not be checked (how it renders in Obsidian, whether the content is right).
4. Fix only after approval, with a short script that changes as little as possible; re-run the audit and report the new counts. Never rewrite the user's own words (Log entries, decisions, answers).

## Editing safely
- Back up before bulk edits: copy the affected notes to a folder outside the vault (`<vaults folder>/_backup/<Vault> pre-<what> <date>`).
- Edit with a short read-modify-write script: assert each target matches exactly once, dry-run, then apply. In a quoted heredoc write real newlines: a doubled backslash-n becomes literal text (the audit flags it).
- After renaming a note, section or property, update every reference by script, then re-run the audit.
