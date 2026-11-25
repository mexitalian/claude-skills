# Changelog

All notable changes to obsidian-vault-kit. Versions follow [semantic versioning](https://semver.org): a new major number means something you rely on changed.

## 1.3.0 (2026-11-25)
- **Changed:** `obsidian-task-system` gives every dated task `#cal` by default. Before creating an event, the sync now looks for an existing unmanaged event for the same task (target and primary calendar, same day ±1) and adopts it by appending the `obsidian-task:` marker, instead of creating a duplicate. Unclear matches are asked about.
- **New:** a fallback for assigning `🆔 cal-` ids by hand when the script can't run.

## 1.2.0 (2026-11-23)
- **New:** behaviour evals in `plugins/obsidian-vault-kit/evals/`: 13 cases for `claude plugin eval`, each run with and without the plugin. See "How it's tested" in the README for the results.
- **Fixed:** in reviews, the casebook now names a weekday only when it has computed it. The evals caught Claude labelling 4 December 2026 as a Thursday (it is a Friday).
- **Changed:** shorter skills. Coursera steps and course-file handling moved to `course-to-obsidian-vault/references/`, and script, audit and editing details to `obsidian-casebook/references/scripts-and-audit.md`. They load only when needed. The course skill is 25% shorter and the casebook 15%.
- **Changed:** skill descriptions are written in the third person, as Anthropic's authoring guidance recommends.

## 1.1.0 (2026-11-23)
- **New:** `examples/Example vault`, a small made-up vault showing cases, learnings, a glossary, `#cal` tasks, a study note and a course lesson. Open it in Obsidian to see what the skills produce.
- **New:** `audit_vault.py --today YYYY-MM-DD` audits as of a given date (used by the tests; also handy for "what will be stale next month?").
- **New:** automated tests for all three scripts and the package (`tests/`), run on every push by GitHub Actions.
- **Fixed:** the casebook's "What's needed" and "Scope" checklists no longer show up as open tasks on the Dashboard, and the audit no longer counts them as a case's next action.

## 1.0.0 (2026-11-22)
- First release: `obsidian-task-system`, `obsidian-casebook`, `obsidian-learning-recall` and `course-to-obsidian-vault`, with `cal_tasks.py`, `audit_vault.py` and `link_glossary.py`.
