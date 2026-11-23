---
name: obsidian-learning-recall
description: "Turns notes into low-stress study notes in an Obsidian vault: a one-minute summary first, a diagram, short chunks, check-yourself questions, Spaced Repetition cards, confidence ratings and review dates computed by Bases, with each section labelled by the learning method it uses. Use when the user wants to study, remember or review something (a lesson, a book chapter, an article, a glossary, rules they keep forgetting), or to add recall to an existing vault."
---

# Learning and recall in an Obsidian vault

Makes material stick with as little effort and stress as possible. Works for any source: an online-course lesson (see `course-to-obsidian-vault`, which uses this skill), a book chapter, an article, a talk, or the Learning notes and glossary of a casebook (`obsidian-casebook`).

**The guiding rule: small, repeatable, low pressure.** Only the one-minute summary is required reading; everything else is optional depth. Gauge progress without adding avoidable cognitive load.

The vault is the source of truth: if the user changed a structure and it works for them, keep it, and offer to update the skill rather than reverting their vault.

## Plugins
Core Obsidian plugins plus **Bases** are assumed. Community plugins: **Spaced Repetition** (`obsidian-spaced-repetition`, by st3v3nmw) for cards, and **Tasks** (`obsidian-tasks-plugin`) for actions. Installing or enabling them is the user's step (or ask before doing it). Do not add other plugins unasked.

## Vault pieces
Templates for all of these are in this skill's `assets/` folder:
```
Start Here.md              the study loop, low-load rules, the rating table, where things live
Review Queue.base          notes due for review today (computed)
Study Notes.base           all study notes with their computed next review
Didactic Methods/          index + 12 method notes; section labels link here
Concepts.base              concept notes, with when first seen and confidence
Templates/Study note.md  Templates/Concept.md
Review/Review Log.md       optional: a line per review session
```
Add property types to `.obsidian/types.json` under `types` (merge, never overwrite): `"confidence": "number"`, `"last_reviewed": "date"`. If Obsidian is running it may not pick this up: tell the user to set the type from the property menu if the date picker is missing.

## Study note
Frontmatter (all keys, even when empty). There is NO stored next review date: it is computed.
```yaml
---
title: "Chapter 3 Pricing"
type: study               # course lessons use type: lesson (see course-to-obsidian-vault)
status: captured          # pending | stub | captured
confidence:               # 1 to 4, set by the user
last_reviewed:            # YYYY-MM-DD, set by the user
source: ""
tags: [study, flashcards]
---
```
The `flashcards` tag in the frontmatter is what the Spaced Repetition plugin looks for. Never add an inline `#flashcards` tag as well.

Sections, in order. Each section ENDS with a method label line such as `> *Didactic Methods: [[Pretesting]]*`: a plain italic quote with NO `<small>` or other HTML around it (HTML breaks the links).

| Section | Content | Label |
|---|---|---|
| `## Before you read` (or `watch`) | `> [!question]` callout: 1-2 pre-questions, then a "My answer:" line | Pretesting |
| `## Start here (1 minute)` | `> [!tip] The whole thing`: one-sentence takeaway, 3-5 bullets, "Do this next"; then an italic "Come back to this when ..." line | Advance organizer · Progressive disclosure |
| `## Picture it` | one small Mermaid `flowchart TD` (never `LR`: wide diagrams render too small), plain quoted labels, validated before saving | Dual coding |
| `## The idea` | 3-5 short `###` chunks; link concepts inline | Chunking |
| `## In my life` | 2-3 questions tying the material to the user's own life, work and numbers | Elaboration |
| `## Check yourself` | up to 5 `<details><summary>Question</summary>Answer</details>` toggles; intro line: answer first, then mark 🟢 knew it / 🟡 shaky / 🔴 missed | Active recall · Confidence calibration |
| `## Cards` | up to 5 single-line `Question :: Answer` pairs | Spaced repetition · Active recall |
| `## Teach it back` | `> [!example]` empty callout: explain it in 3 sentences without looking | Teach-back |
| `## Actions` | `- [ ]` tasks. Always include `- [ ] Rate this 1, 2 or 3 in confidence and set last_reviewed to today` | Implementation intentions |
| `## Concepts used` | `[[Concept]]` links | Concept linking |
| `## Source` | where it came from (link, page range, timestamp); "Review log:" line | none |

Rules:
- At most 5 check questions and 5 cards per note.
- Theory lives in study notes, to-dos in checkboxes, choices in a Decisions note.
- **Content fidelity:** capture ideas, figures and examples accurately, in your own words. Paraphrase and condense; never copy the source wholesale or reproduce copyrighted text beyond brief quotes. Where the source contradicts itself, keep both figures and add an "In my life" prompt for the user to check, rather than silently resolving it.
- **Health and psychology material:** "In my life" prompts only ask what the user notices; never assume or write that they have a condition. Where material gives diagnostic criteria, say the note is a summary, not a way to diagnose anyone.
- **Stub notes** (welcome videos, admin items, anything the user says does not matter): `status: stub`, no `flashcards` tag, a `> [!info] Stub on purpose` callout (one to three sentences), the pretest section with its label, and Source.
- Things the user must do themselves (posting, buying, signing up) go in Actions, never done for them. Their answers, ratings and decisions are theirs: never fill them in.

## Concept notes
Ideas reused across several notes, or definitions worth a single home, go in `Concepts/` (template: `assets/Concept.md`): `type: concept`, `first_seen`, `confidence`; body: one plain sentence of what it is, `## Why it matters for me`, `## Example`, `## Seen in` (links to the notes that use it), `## Not to be confused with`. They are the study-side sibling of the casebook's Learning notes (`obsidian-casebook`), which record how a system works instead. Search `Concepts/` before creating one; add the new note to `Seen in` instead of making a near-duplicate. `assets/Concepts.base` lists them.

## Computed review dates
The user enters two values per review: `confidence` (1-4) and `last_reviewed` (today). Bases computes the due date; nothing is stored, so nothing goes stale.

| Rating | Meaning | Next review |
|---|---|---|
| 1 | Shaky, missed most | last_reviewed + 1 day |
| 2 | Mostly there | + 3 days |
| 3 | Solid | + 7 days |
| 4 | Locked in: still solid on a repeat review | + 21 days |

A formula cannot count how many times something was reviewed, so the growing interval is a rating the user chooses: 3 the first time it feels solid, 4 only on a later review where it still came without help. Say this in Start Here; do not promise automatic growth. (Automatic counting would need a button plugin such as QuickAdd or Meta Bind, or the Spaced Repetition plugin at card level: offer, do not install.)

`assets/Review Queue.base` shows notes with both values whose computed date is today or earlier; `assets/Study Notes.base` lists all study notes with the computed "Next review" column. Keep the 1/3/7/21 ladder identical in both bases, Start Here and the two method notes (Confidence calibration, Spaced repetition) when changing anything.

## The study loop
Start Here shows it as a Mermaid diagram: pre-questions (2 min) → read or watch → study note built → Start-here box (1 min) → check yourself (answer first, then open the toggle) → rate confidence → pick one action → review on the due date. About 25 minutes per item.

Traffic-light marking in toggles is deliberately manual. For card review, the user assigns a hotkey to "Spaced Repetition: Review flashcards in this note". Tasks records a completion date only when a box is ticked through the plugin (clicking it in the rendered view); mention this once.

## Didactic Methods
Copy `assets/Didactic Methods/` into the vault (the index plus 12 method notes). The section labels link to them. Index message: active recall and spaced repetition matter most; the rest make them easier. If the vault already has a Didactic Methods folder, reuse it.

If you rename a section, a method note or a property, it is a vault-wide change: replace it in every study note, the template, Start Here and the methods index with one script, grep for the old name, then re-run the audit.

## Adding recall to existing notes
For a casebook glossary or Learning notes the user keeps forgetting, do not convert them into study notes. Add a `## Cards` section with up to 5 `Question :: Answer` lines, add `flashcards` to their frontmatter tags, and let the Spaced Repetition plugin schedule them.

## Verify after every batch
- Validate every Mermaid diagram before saving.
- Run the audit from `obsidian-casebook` (`scripts/audit_vault.py <vault>`): its recall checks switch on automatically and cover the section order, the 10 method labels, the toggle and card limits, the frontmatter tag, confidence and last_reviewed values, no stored next review, the bases and `types.json`. Fix every FAIL before reporting.
- After the first batch, ask the user how links, bases and toggles render (Live Preview vs Reading view) before building more.
- Report in one or two sentences what was built and what is pending, then pause for feedback.

## Pitfalls
- Do not store `next_review`: a stored date goes stale and needs hand entry.
- Ratings 1-3 alone cannot reach 21 days: rating 4 carries the long step.
- In Python run through a quoted heredoc, write real newlines; a doubled backslash-n becomes literal text in the note (the audit flags it).
- Do not wrap method labels in HTML.
