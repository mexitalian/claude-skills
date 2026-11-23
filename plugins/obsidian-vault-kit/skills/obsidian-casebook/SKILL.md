---
name: obsidian-casebook
description: "Track ongoing processes in an Obsidian vault and keep what you learn about how systems work: bureaucracy and life admin (offices, applications, taxes, insurance), tech setups and fixes, or any ongoing project. Use when the user wants to start, update, review or close a case, log what happened, record how something actually works, check what is waiting or due, or audit such a vault."
---

# Casebook: progress and learnings in an Obsidian vault

A **case** is anything that runs over weeks with steps, waiting and surprises: registering an address, a tax return, an insurance claim, a benefit or permit application, setting up a home server, a migration at work, a side project. A **learning** is what the case taught about how the system really works, kept in its own note so the next case (or the next person) starts smarter.

The vault is the source of truth. The user also edits it directly and keeps what works: if the vault differs from this skill, check whether it is an improvement before changing anything, and never revert their changes to match the skill.

## Related skills
- `obsidian-task-system`: task syntax, and the `#cal` sync that puts deadlines on Google Calendar. Case tasks follow it.
- `obsidian-learning-recall`: add recall (cards, computed reviews) to notes worth memorising, such as a glossary of official terms.
- `course-to-obsidian-vault`: builds on this skill's knowledge notes, glossary and audit for online courses.

## Working rules
- **The user does the official acts.** Submitting forms, signing, paying, calling, sending emails to an office, booking appointments: Claude drafts, prepares and checks, the user acts (or explicitly approves each send). Put these in the case's tasks as theirs to do.
- **Decisions are theirs.** Never fill in a choice or its reason. Prepare a decision row with `???` and the options.
- **Facts keep their basis.** What the user experienced, what an official source says, and what someone reported are different things. Record which one it is (see Learning notes) and never upgrade a guess to a fact.
- **Ask before system changes** (installing plugins, changing app config, sync settings). Edits to notes the user asked for are fine.
- Ask one round of questions at a time, and only what changes the result. Otherwise start and say what you assumed.

## Privacy (read before writing anything)
Case vaults collect sensitive identifiers fast, and vaults often sync to phones and other devices.
- Never write into notes: government ID, passport, tax ID or social-insurance numbers, bank or card numbers, passwords, PINs, login codes, or health details. Do not print existing ones in chat either.
- For reference numbers needed to follow up (a file reference, a customer or case number), ask the user. Default: record **where to find it** ("on the letter of 12.11.2026") or only the last 4 characters.
- Keep scans and photos of documents out of synced vaults unless the user decides otherwise; link to where they are kept instead.
- Run the audit's privacy check after bulk imports (it flags things that look like IBANs, card numbers or long ID numbers, without printing them).

## Vault layout
Cases can live in their own vault or in a folder of an existing one. Defaults (keep the vault's own names if it already has them):
```
<vault>/
  Dashboard.md                 open actions, waiting-for, due soon, embeds Cases.base and Learnings.base
  Cases/<Case name>.md         one note per case (or Cases/<Case name>/<Case name>.md if it needs files)
  Learnings/<Topic>.md         how a system works, one note per rule or topic
  Glossary.md                  official or technical terms, one ### heading per term or group
  Cases.base  Learnings.base
  Templates/Case.md  Templates/Learning.md
  _archive/                    closed cases, if the user wants them out of the way (optional)
```
Templates for every file are in this skill's `assets/` folder: copy them, then adjust names to the vault. Never use `? : * " < > |` in file or folder names (Android and Windows sync cannot store them). Add `.obsidian/types.json` entries for date properties (`started`, `last_verified`: `"date"`), merging with what is there.

If the vault is synced with Syncthing, add `.DS_Store`, `.obsidian/workspace.json`, `.obsidian/workspace-mobile.json` and `.trash` to `.stignore`.

## Case note
Frontmatter (all keys, even when empty):
```yaml
---
type: case
kind: bureaucracy        # bureaucracy | tech | project
status: active           # active | waiting | blocked | done | dropped
counterpart: ""          # who you deal with: an office, a company, a tool, a team
goal: ""                 # what "done" looks like, in one line
started: 2026-11-22
closed:
tags: [case, bureaucracy]
---
```
Sections, in this order:

| Section | Content |
|---|---|
| `> [!summary] Where this stands` | Right after the H1. Three lines: status in plain words; the next action and who has it; what you are waiting for and since when. Rewrite it on every update; it is the only part that must be read. |
| `## ✅ Tasks` | Open tasks in `obsidian-task-system` syntax. Deadlines get `📅` and, if they belong on the calendar, `#cal`. Waiting on someone: `#waiting-for` with `📅` set to the day to chase them. |
| `## What's needed` | Checklist of documents and requirements, by name only (never their numbers). Tick when ready. The Dashboard ignores these boxes; anything that needs doing goes in Tasks. |
| `## Log` | Newest first. One `### YYYY-MM-DD` heading per day, then bullets: what happened, the channel (letter, email, phone, visit, portal, terminal), who said what, the outcome. Only what the user reports or a document shows. |
| `## Decisions` | Table: Date, Decision, Why, Options considered. Then `### Open questions` for choices not made yet. |
| `## Learned here` | Links to the Learning notes this case produced or used, one line each on what it was. |
| `## Contacts and channels` | Institutions and official channels only: office, address, opening hours, public phone or email, portal URL. No private contact details of individual staff unless the user wants them. |
| `## Sources` | Official pages, letters (by date and sender), docs, threads, with the date read. |

Tech cases use the same note; in the Log, record what was tried, the exact error, and what fixed it. Projects can rename "What's needed" to "Scope" if the user prefers.

## Learning note (how a system works)
One note per rule or topic that will matter again ("Registering a new address", "Finanzamt answers by post, not email", "Syncthing folder IDs are case-sensitive").
```yaml
---
type: learning
area: ""                 # the system: an office, a law, a tool, an organisation
kind: bureaucracy        # bureaucracy | tech | project
basis: experience        # official | experience | reported | assumption
last_verified: 2026-11-22
tags: [learning, bureaucracy]
---
```
Body: one plain sentence stating the rule; `## How it actually works`; `## Gotchas`; `## Evidence` (each claim with its basis and date: official page link, "Case [[X]], 12.11.2026: they said ...", or who reported it); `## Seen in` (links to cases); `## Not to be confused with`.

- **basis**: `official` = an official source says so (link it); `experience` = it happened to the user; `reported` = someone else said so, or Claude found it in a web search; `assumption` = not checked yet. When sources disagree, keep both with their dates and say which wins in practice, rather than silently resolving it.
- **last_verified**: the date the rule was last confirmed. Rules, fees and forms change: the audit flags learnings older than 12 months (adjustable) for a re-check.
- Search `Learnings/` before creating one; extend an existing note and add the case to its `Seen in` instead of making a near-duplicate.
- Study vaults keep ideas in concept notes instead (`type: concept` in `Concepts/`, see `obsidian-learning-recall`). The audit and glossary linking treat both kinds the same way.

## Glossary
`Glossary.md` holds terms the user keeps meeting (official words such as "Anmeldebestätigung" or "Steuerbescheid", or technical terms), each as a `###` heading with a one-line plain meaning, the literal translation if useful, and where it shows up. The script `scripts/link_glossary.py` links the first plain mention of each term in other notes to its heading (see "Scripts").

## Dashboard
`assets/Dashboard.md` has Tasks queries for open actions, waiting-for (with chase dates), and due in the next two weeks, each excluding `Templates` and the "What's needed" and "Scope" checklists (their boxes are documents to gather, not actions), then embeds `Cases.base` (grouped by status) and `Learnings.base` (oldest `last_verified` first). Tasks queries must be checked inside Obsidian before anyone relies on them: Claude cannot run them.

## Workflows

### Start a case
Ask (one round): the case name, kind, counterpart, goal, and any deadline. Create the note from the template, fill "Where this stands", add the first tasks and the "What's needed" list. Search `Learnings/` for related notes and link them under "Learned here": earlier cases often already know the gotchas. If a deadline should be on the calendar, tag it `#cal` and offer to run the `obsidian-task-system` sync.

### Update a case
When the user reports what happened (or shares a letter, an email, an error):
1. Add a dated Log entry in their words, condensed. For a document, record its date, sender and what it asks for, never its identifiers.
2. Update tasks: tick what is done (completion date `✅ YYYY-MM-DD`), add the new next actions and chase dates.
3. Update `status` and rewrite "Where this stands".
4. **Learning sweep**: if the update shows how the system works (a rule, a timing, a trap), propose it as a new or extended Learning note with its basis. Ask before creating it; show the draft.
5. If a decision came up, add it to Decisions (or Open questions with `???`).
6. Reply with one or two lines: what changed and the next action.

### Review ("where am I with everything?")
Read `Cases.base` and the open tasks. Report per active case: next action, what is waiting and for how long, deadlines in the next two weeks. Flag waiting-for items past their chase date and cases with no open task (stalled). Keep it to what needs attention; do not recap the rest.

### Close a case
Set `status: done` (or `dropped`) and `closed`, write the outcome in "Where this stands", make sure no open tasks remain (move or cancel them with the user), run a final learning sweep, and optionally move the note to `_archive/`. Links keep working if it is moved through Obsidian or with every `[[link]]` updated by script.

### Research for a case
When the user asks how something works, look it up (official sources first), answer, and offer to record it as a Learning with `basis: official` (or `reported` for non-official sources) and the date read. Do not write research into the case Log as if it happened.

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
