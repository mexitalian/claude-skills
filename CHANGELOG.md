# Changelog

All notable changes to obsidian-vault-kit. Versions follow [semantic versioning](https://semver.org): a new major number means something you rely on changed.

## 1.1.0 (2026-11-23)
- **New:** `examples/Example vault`, a small made-up vault showing cases, learnings, a glossary, `#cal` tasks, a study note and a course lesson. Open it in Obsidian to see what the skills produce.
- **New:** `audit_vault.py --today YYYY-MM-DD` audits as of a given date (used by the tests; also handy for "what will be stale next month?").
- **New:** automated tests for all three scripts and the package (`tests/`), run on every push by GitHub Actions.
- **Fixed:** the casebook's "What's needed" and "Scope" checklists no longer show up as open tasks on the Dashboard, and the audit no longer counts them as a case's next action.

## 1.0.0 (2026-11-22)
- First release: `obsidian-task-system`, `obsidian-casebook`, `obsidian-learning-recall` and `course-to-obsidian-vault`, with `cal_tasks.py`, `audit_vault.py` and `link_glossary.py`.
