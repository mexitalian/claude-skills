---
name: obsidian-task-system
description: "Use when managing tasks in an Obsidian vault with the Tasks plugin, syncing tasks tagged #cal to Google Calendar, or reconciling the calendar with the vault."
---

# Obsidian task system and calendar sync

The vault is the source of truth for tasks. Tasks tagged `#cal` are mirrored to a Google Calendar on request: one task, one event. There is no plugin, no Google Cloud project and no OAuth setup. Claude reconciles the two using a small script plus a Google Calendar connector.

Cases in `obsidian-casebook` and study notes in `obsidian-learning-recall` use these conventions.

Check what is installed first: `<vault>/.obsidian/community-plugins.json`. This skill assumes the Tasks plugin (`obsidian-tasks-plugin`).

## What you need
- An Obsidian vault Claude can read and edit: in Claude Code, a local folder; in the Claude app, a folder on the computer linked through the desktop app.
- Python 3.9+ wherever the vault lives (standard library only).
- A Google Calendar connector or MCP server with tools to list calendars and to list, create and update events. For calendar sync only.

## 1. Task conventions
- Task syntax: `- [ ] text #tag ⏫ 📅 2026-11-12`. Priority ⏫ 🔼 🔽, due 📅, scheduled ⏳, done ✅, recurrence 🔁. Nested `- [ ]` lines are subtasks; plain `- ` bullets under a task are its notes.
- Context tags (GTD style) work well, for example `#calls #email #computer #errand #waiting-for #urgent`, plus topic tags. Use the vault's existing tags rather than inventing new ones.
- In project notes, put the open tasks in a `## ✅ Tasks` block right after the H1.
- An open-tasks dashboard note uses Tasks queries (`not done`, `due on or before today`, `tags include #waiting-for`). Queries must be checked inside Obsidian before anyone relies on them, because Claude cannot run them.
- Keep completed history in an archive note, not as scattered `- [x]` lines.
- When moving tasks in from another app, turn the old open checkboxes in the source notes into plain bullets so nothing is counted twice. Make a backup first.
- Unknown emoji such as ⏰ or ⏱ must sit in the description, before the tags and known fields. If they come after them, the Tasks plugin stops parsing the trailing 📅 and priority.

## 2. Calendar sync with #cal
Claude reconciles on request, and after changing any `#cal` task.
- An open task with `#cal` and `📅 YYYY-MM-DD` = one event on that date. Optional `⏰ HH:MM` and `⏱ 1h` (or `1h30m`, `45m`) in the description; without ⏰ the event is all-day.
- The Tasks-plugin id `🆔 cal-xxxxxx` on the line links task and event. The event description carries `obsidian-task: cal-xxxxxx`. Events without that marker are unmanaged: never touch them.

### The script
`scripts/cal_tasks.py` in this skill's folder. It must run on the machine where the vault lives. If the vault is on the user's own computer and Claude works from elsewhere (for example the Claude app linked to the desktop), ask once to copy the script to a folder outside the vault, such as `<vaults folder>/_tools/cal_tasks.py`. Never put it inside a vault that syncs to other devices.
- `python3 cal_tasks.py --vault "<vault path>" list` prints JSON: open `#cal` tasks with a date, done tasks, and `problems`.
- `assign` is a dry run that shows which tasks still need a 🆔. `assign --apply` appends the ids (before any `^block-ref`, keeping the file's line endings).
- The vault path is required (or set `OBSIDIAN_VAULT`). The script skips `.obsidian`, `.trash`, `.git`, `_tools` and fenced code blocks.

### Which calendar
Use the calendar recorded for this vault (see "Record the setup" below). If none is recorded, list the calendars, recommend a dedicated one (for example "Tasks"), ask once, and record the choice.

Several vaults can share one calendar. Then every managed event also carries `obsidian-vault: <VaultName>` in its description, and its title gets the vault's prefix (and colour, if the user wants one). When searching, use `obsidian-vault: <VaultName>`, and only judge events of the vault being synced: never flag or touch another vault's events.

### Steps
1. Run `list`. Fix `problems` first: assign missing ids (dry run, then apply), ask about `#cal` tasks with no 📅, and resolve duplicate ids.
2. List events on the target calendar with full-text search `obsidian-task` (or `obsidian-vault: <VaultName>`) over a wide date range.
3. Match by id.
   - **No event:** create one. Title from the task. Description: the task's notes, the `obsidian-task: <id>` line and "Managed from the Obsidian vault: change the 📅 date on the task there, not here."
   - **Reminders:** a popup at 09:00 on the day (all-day events count minutes back from midnight, so `-540`), plus one a day earlier (`1440`) for high-priority tasks. If the calendar tool rejects a negative value, tell the user and use the nearest accepted reminder instead.
   - **Date, time or duration differs:** update only those fields. **Same:** leave it alone. Never overwrite other event text unless asked.
4. An event with an id but no open `#cal` task:
   - task done → prefix the title with `✅ DONE:` and keep the event;
   - task or tag removed → report it and ask before deleting anything.
5. Report one short line per change.

## 3. Working on the vault
- Back up before bulk edits: copy the affected notes to a backup folder outside the vault, such as `<vaults folder>/_backup/<Vault> pre-<what> <date>`.
- Keep helper scripts outside every vault, so sync tools do not send them to other devices.
- Edit notes with a short read-modify-write script: assert that each target line matches exactly once, dry-run first, then apply.
- Ask before any system-level change (installing software, changing services, editing app config). Edits to vault notes that the user asked for are fine.

## 4. Privacy
Vaults often sync to phones and other devices. Do not add government IDs, tax IDs, social-insurance numbers, customer numbers or bank details to notes, and do not print existing ones in chat. Ask before copying one in. Check where a plugin stores API keys or tokens before installing it: plugin settings live in `.obsidian/plugins/<plugin>/data.json` and sync with the vault.

## 5. Record the setup
After the first sync for a vault, record its setup in a place future sessions will read: the project's `CLAUDE.md`, a note in the vault (for example `Tasks setup.md`), or Claude's memory. Record the vault path, the calendar name and ID, the vault prefix and colour if the calendar is shared, and where the script lives. Read it at the start of each sync, and update it when something changes.
