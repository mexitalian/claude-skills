---
description: "Assigning calendar ids only to #cal tasks, keeping existing ids"
max_turns: 30
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill, Edit, Write, Bash]
tags: [example-vault, tasks]
---
My Obsidian vault is in the folder `vault`. Get my #cal tasks ready for calendar sync by giving every one of them its id. Don't touch the calendar itself, just the notes.
