# Obsidian vault kit for Claude

Four Claude skills for running the slow, many-step parts of life in an [Obsidian](https://obsidian.md) vault: tasks and deadlines, bureaucracy and tech problems that drag on for weeks, and things you are trying to learn. Claude does the bookkeeping; the vault stays yours, in plain Markdown.

| Skill | Use it for |
|---|---|
| **obsidian-task-system** | Tasks-plugin conventions, plus syncing tasks tagged `#cal` to Google Calendar with no plugin, no Google Cloud project and no OAuth setup. |
| **obsidian-casebook** | Ongoing **cases**: an address registration, a tax return, an insurance claim, a home-server setup, a project. Each case has a one-glance "where this stands", next actions, a dated log, decisions, and **learnings**: notes on how the system actually works, recorded with their source and the date they were checked. Also a glossary, a vault audit, and a privacy check that flags bank and card numbers. |
| **obsidian-learning-recall** | Low-stress study notes for anything you want to remember: a one-minute summary first, a diagram, check-yourself questions, Spaced Repetition cards, and review dates computed by Bases from a 1-4 confidence rating. Each section is labelled with the learning method it uses, and 12 short method notes explain why. |
| **course-to-obsidian-vault** | Capturing an online course (Skool, Coursera or similar) lesson by lesson into study notes, tracking progress per week, and handling course files with their usage terms. Builds on the two skills above. |

They work alone or together. A case's deadline becomes a `#cal` task on your calendar, and a learning you keep forgetting can get recall cards.

## Example: a casebook case
```markdown
# Register new address

> [!summary] Where this stands
> **Status:** appointment done, waiting for the confirmation by post.
> **Next:** chase the office if nothing arrives by 4 December — you.
> **Waiting for:** confirmation letter since 20 November.

## ✅ Tasks
- [ ] Chase the office about the confirmation #waiting-for 📅 2026-12-04

## Log
### 2026-11-20
- Appointment went fine; they said the confirmation comes by post within two weeks.
```
Tell Claude what happened ("the letter came, they want one more form") and it updates the log, tasks and status, then suggests any general rule worth keeping as a learning note.

## Install

### Claude Code
```bash
claude plugin marketplace add mexitalian/claude-skills
claude plugin install obsidian-vault-kit@mexitalian
```

### Claude app (claude.ai, desktop)
Download the skill zips from [Releases](../../releases) and upload each under **Settings → Capabilities → Skills**. `course-to-obsidian-vault` needs `obsidian-learning-recall` and `obsidian-casebook` installed as well.

## Requirements
- An Obsidian vault Claude can reach: a local folder in Claude Code, or a folder on your computer linked through the Claude desktop app.
- Python 3.9+ on the machine where the vault lives, for the bundled scripts (standard library only).
- Obsidian core plugins with **Bases**; community plugins **Tasks** and, for recall, **Spaced Repetition**.
- For calendar sync: a Google Calendar connector (Claude app) or a Google Calendar MCP server (Claude Code).
- For course capture: a browser Claude can use, signed in by you.

## Scripts
| Script | What it does |
|---|---|
| `obsidian-task-system/scripts/cal_tasks.py` | Lists `#cal` tasks as JSON and assigns the ids that link tasks to events. |
| `obsidian-casebook/scripts/audit_vault.py` | Read-only vault check: broken links and heading anchors, orphan notes, case and learning structure, stale learnings, possible bank or card numbers (masked), and recall and course checks when relevant. |
| `obsidian-casebook/scripts/link_glossary.py` | Links the first mention of each glossary term in a note to its glossary entry. Dry run by default. |

None of them changes anything unless you pass `--apply`. Keep them outside your vault (for example `~/Vaults/_tools/`) so sync tools don't copy them to your phone.

## Privacy
The casebook is designed for real-life admin, so it tells Claude never to write ID, tax, passport, bank or card numbers into notes, and to record *where to find* a reference number instead of the number itself. The audit flags anything that slips through.

## Licence
MIT. See [LICENSE](LICENSE).
