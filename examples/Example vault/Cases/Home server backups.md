---
type: case
kind: tech
status: active
counterpart: "Home server (backup tool + external drive)"
goal: "Nightly backups that restore cleanly, checked once a month"
started: 2026-11-10
closed:
tags: [case, tech]
---
# Home server backups

> [!summary] Where this stands
> **Status:** nightly job runs; the first test restore worked.
> **Next:** schedule a monthly restore check — you.
> **Waiting for:** nothing.

## ✅ Tasks
- [ ] Set a monthly reminder to test-restore one folder #computer #cal 📅 2026-12-01 🆔 cal-2b91e0
- [x] Run a first test restore #computer 📅 2026-11-15 ✅ 2026-11-14

## Scope
- [x] Photos folder
- [ ] Documents folder

## Log
### 2026-11-14
- Restored one folder from last night's [[Glossary#Snapshot|snapshot]] to a scratch location; files matched.
### 2026-11-10
- Nightly job set up. First run failed with "repository does not exist": the drive was mounted under a different name. Fixed by mounting it by its label.

## Decisions
| Date | Decision | Why | Options considered |
|---|---|---|---|
| 2026-11-10 | Back up to an external drive first, cloud later | Free, and easy to test | Drive only / cloud only / both |

### Open questions
- Which cloud storage for the off-site copy?

## Learned here
- [[External drives can mount under a different name]]: mount by label, not by position.

## Contacts and channels
- Backup tool documentation and forum.

## Sources
- Backup tool's "getting started" guide, read 2026-11-10.
