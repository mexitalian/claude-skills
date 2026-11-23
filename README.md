# Obsidian vault kit for Claude

[![Test](https://github.com/mexitalian/claude-skills/actions/workflows/test.yml/badge.svg)](https://github.com/mexitalian/claude-skills/actions/workflows/test.yml) [![Licence: MIT](https://img.shields.io/badge/licence-MIT-blue.svg)](LICENSE)

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

### Try the example vault
[`examples/Example vault`](examples/Example%20vault) is a small, made-up vault with two cases (a bureaucracy errand and a home-server fix), their learnings, a glossary, `#cal` tasks, a study note and a course lesson. Download the repo, choose **Open folder as vault** in Obsidian, and install the Tasks and Spaced Repetition plugins to see the Dashboard and cards work.

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

## Limitations
- **Claude is the sync engine.** Nothing runs in the background: the calendar is updated, and the audit run, when you ask Claude to do it.
- **Tasks queries and Bases views can't be run by Claude.** They are written to the plugins' documented syntax and checked by the audit's rules, but the first time you set up a vault, open the Dashboard and Review Queue in Obsidian to confirm they render.
- **Review intervals are a simple ladder** (1, 3, 7 or 21 days from your 1-4 rating), not an adaptive algorithm. The Spaced Repetition plugin schedules the cards themselves.
- **Course capture depends on each platform's pages**, which change. The Skool and Coursera steps were accurate in November 2026.
- **The privacy check is a safety net, not a guarantee.** It spots IBANs, card numbers and 11-digit numbers; it can't recognise every kind of ID.
- **The Syncthing and other sync setups are not included**; any sync tool works, as long as it skips `.obsidian/workspace*.json`.

## How it's tested
- **Scripts:** [`tests/`](tests) holds about 45 automated tests for the three scripts, covering Windows line endings, block references, code blocks, the privacy check (which must never print the number it found), stale learnings and broken links. They also check that a vault built only from the skills' templates passes the audit, and that the [example vault](examples/Example%20vault) stays clean. [GitHub Actions](.github/workflows/test.yml) runs them on Python 3.9 and 3.12 on every push, together with `claude plugin validate`.
- **Skills:** written and tried with Claude Opus. Behaviour evals (does Claude pick the right skill, and follow it?) are planned; see the [changelog](CHANGELOG.md) for progress.

Run the tests yourself:
```bash
pip install pytest
python -m pytest -q tests
```

## Feedback
Found a bug, or a step that confused Claude? [Open an issue](https://github.com/mexitalian/claude-skills/issues) with what you asked and what happened.

## Privacy
The casebook is designed for real-life admin, so it tells Claude never to write ID, tax, passport, bank or card numbers into notes, and to record *where to find* a reference number instead of the number itself. The audit flags anything that slips through.

## Licence
MIT. See [LICENSE](LICENSE).
