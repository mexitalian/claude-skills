---
name: course-to-obsidian-vault
description: "Build, extend or audit an Obsidian study vault alongside an online course (Skool, Coursera or similar): capture lessons from the course pages, transcripts or the user's notes into study notes with recall, track progress per week, and keep course files with their usage terms. Use when the user starts a course vault, wants the next lessons added, or wants a course vault checked."
---

# Course to Obsidian vault

While the user takes an online course, build and grow an Obsidian vault from the lessons and their own learnings. Three jobs: start a new course vault, add lessons to an existing one, or audit one.

This skill is the course-capture layer. It builds on two others; read them before the first lesson of a session:
- `obsidian-learning-recall`: the study-note shape (here `type: lesson`), method labels, cards, computed reviews, Start Here and the Didactic Methods folder.
- `obsidian-casebook`: glossary linking, privacy, safe editing, and the audit script.
Optional: `obsidian-task-system` for the Tasks dashboard and calendar sync; a sync skill if the vault should reach a phone; a local transcription tool or skill for video-only lessons.

**The guiding rule: small, repeatable, low pressure.** The vault the user actually uses is the source of truth: if they changed something and it works, keep it and offer to update the skill, never revert their vault.

## Working with the user
- Ask questions in one round, and only what changes the result.
- Ask before any system change (new folders outside the vault, sync, plugin installs).
- Do not build ahead: build the lessons asked for, then pause so the user can try the vault.
- The user signs in to the course platform themselves, in the browser they choose. Never type passwords or credentials. If the browser tools disconnect, stop retrying and ask them to reconnect.
- Things the user must do themselves (posting in a community, downloading or installing resources, buying something) go in Actions, never done for them. Their answers, ratings and decisions are theirs.

## 1. Starting a new course: ask first (one round)
1. **Vault location**: one shared study vault with each course under `Courses/<Course>/` (recommended when the user takes several courses), or a vault per course. Check what exists first and extend it.
2. **Capture source**: lesson text or transcripts on the page if the platform has them (check first), else the user's own audio of the video transcribed locally, else notes they paste or dictate.
3. **Recall level**: full from day one (recommended) or minimal.
4. **Where to start**: usually the top of week 1. Intro items the user does not care about become stubs.
5. **Sync to a phone**: yes or no.
6. **Browser**: which one the user will sign in with.

## 2. Vault structure
```
<Vault>/
  Start Here.md  Dashboard.md          from obsidian-learning-recall (+ Tasks queries)
  Review Queue.base  Study Notes.base  Concepts.base
  Courses/<Course>/<Course>.md                     course map: modules table (what it covers, platform progress with the date read, vault status)
  Courses/<Course>/<Week N - Title>/<Week N - Title>.md   week page: #, Section, Lesson, Note, Watched on platform, Vault status
  Courses/<Course>/<Week N - Title>/W1-04 Lesson title.md  one note per lesson
  Concepts/              concept notes (shape in obsidian-learning-recall)
  Resources/             Resources.md index + course files worth keeping
  Didactic Methods/      from obsidian-learning-recall
  Doing/Actions.md  Doing/Decisions.md (with an "Open questions" section)  Doing/<working notes>
  Review/Review Log.md
  Templates/Lesson.md  Templates/Concept.md
```
- File names: `W<week>-<NN> <Lesson title>.md`, so notes sort in course order. Never use `? : * " < > |` in names: drop them from titles.
- Tags: `tags: [<course-slug>, <kind>]` on every course note. In a shared vault, vault-level notes carry a general tag (for example `study`); templates carry the placeholder `course-slug`.
- Navigation line in each lesson: `[[Week page|Week 1]] · [[prev|← prev]] | [[next|next →]]`. The last lesson's next link points at the course map. If the next note is not built yet, write plain text `next → (W1-09 not built yet)`, not a link (a link to a missing note fails the audit), and turn it into a link later. Templates must not link to notes that do not exist.
- Pending lessons have no note yet: their week-page row has an empty Note cell and status `pending`.
- Templates for the lesson note, week page and course map are in this skill's `assets/` folder; the others come from `obsidian-learning-recall`.

## 3. Lesson note
A study note from `obsidian-learning-recall` with `type: lesson` and these extra keys (all present, even when empty):
```yaml
---
title: "W1-04 Pricing strategies"
type: lesson
course: "<Course>"
week: 1
order: 4
group: "<section name on the platform>"
video_minutes: 16.1          # empty for readings
status: captured             # pending | stub | captured
platform_watched: false      # what the platform shows as done
confidence:
last_reviewed:
source: "<lesson URL>"
tags: [<course-slug>, lesson, week-1, flashcards]
---
```
Sections, labels, limits, stubs and content-fidelity rules are as in `obsidian-learning-recall`. The "Before you read" heading may say "Before you watch". `Study Notes.base` can group by `week` for a course.

**Decision stubs.** When a lesson says to record a decision and the user asks for it to be prepared, add a row to `Doing/Decisions.md`: today's date, the decision with `???` for their choice (name the options), `???` for the reason, and a `[[lesson]]` link. Leave the lesson's action unticked for them. Choices not made yet go under "Open questions".

## 4. Capturing from a course platform
General flow (proven on Skool):
1. Open the classroom in the user's browser after they sign in. Read the module list and progress percentages; record the date read in the course map.
2. Open each lesson page and read its text. Many platforms show the lesson's written notes as page text. Videos usually sit in a cross-origin player: do not try to work around that, and do not depend on captions. Note the video length.
3. Get lesson URLs from the sidebar links, then navigate to each. Sections may need expanding. Element references can go stale after a page change: find them again.
4. Build lesson notes from the text. Lessons not asked for yet stay `pending` with their week-page row filled in.
5. **Video-only lesson** (a length, maybe a resource, no text): tell the user and offer: leave it pending, they paste notes or a transcript, or they point to their own audio of it for local transcription. Build the note from the transcript, say so in Source, and use "captured (from audio)" in the week page.
6. **Resource-only lesson** (spreadsheet, ZIP, template): a short note on what the resource is and what to do with it; handle the file as in section 5.
7. After every batch, update the week page (watched, vault status) and the course map (progress percentage and date). Re-read the platform's progress at the end: it changes as the user watches.

### Coursera
1. **Sign-in**: without a session, course URLs redirect to the public page (module titles only). The user signs in and must be enrolled (auditing is fine).
2. **Outline**: open `/learn/<slug>/home/module/N`, wait about 7 seconds (earlier reads return "Loading..."), then read the page text: sections, item types and durations, practice assignments and quiz due dates. Record them in the course map with the date read.
3. **Lesson pages**: videos are `/learn/<slug>/lecture/<id>/<slug>`, readings `/supplement/<id>/<slug>`. Get the ids from the sidebar entries ("Video, <title>, Not submitted, N min"; "Not submitted" means not done). Only the open section's links show. Opening a reading page can tick it as done on Coursera: open readings only when the user asks, and say that a tick may come from the visit.
4. **Video text**: open the Transcript panel beside the video (it stays open on the next lecture); the page text then includes the full transcript, so no audio transcription is needed. Reading the whole page also gives the sidebar progress for the week page.
5. **Long readings**: when a reading links to a long source and the user supplies the file, copy it into `Resources/` with the lesson id in the name, read the whole text (not an automated summary), and rewrite the note from it. Add page ranges for the key parts under Source, and check every figure against the text.
6. **Capture**: videos and readings become lesson notes, `W<module>-<NN>` in course order. Practice assignments, ungraded items and graded quizzes stay on Coursera: list them on the week page under "On Coursera only (not captured here)", and say when a quiz is overdue or due soon.
7. **Finish**: close the tabs you opened.

## 5. Course files and their terms
The platform stays the master copy; the vault holds a dated backup.
- **Getting the file**: by default the user downloads it. Then find it with a read-only search of their Downloads folder (recent zip, xlsx, csv, pdf), confirm it is the right one (for a ZIP, list names only), and COPY it (never move) into `Resources/` as `W<week>-<NN> <Lesson title>.<ext>`. Downloading it yourself needs the user's explicit OK with file name, source and size.
- **Never unzip or run anything** from an archive, and never unpack it into the vault: store it unopened.
- Add a row to `Resources/Resources.md` (file, lesson, copied-on date, notes) and link the file with a plain `[[file name.ext]]` in the lesson's Source. Mention what is inside only if you listed it. Large files: link to the platform and add them to `.stignore` instead.
- **Datasets (xlsx, csv)**: inspect read-only first (sheets, hidden sheets, headers, row counts, comments, any usage terms or copyright line; an `.xlsm` needs a warning). Then:
  - **Follow the author's terms.** If the sheet or page says what may be done with it, follow that. If there is only a copyright line, tell the user so and treat it as private study: do not mirror the dataset into notes.
  - **Default**: a screening note in `Doing/` listing item NAMES only, grouped, checked against the lesson's criteria that the data can answer (state each threshold, and which criteria the data cannot check). Separate items with blank data. Flag items the lessons call a bad choice. Say the figures are the author's, that the note is a private study aid, and that it should not be shared.
  - **Then ask**: which 2-3 items the user picks. Only for those, build fuller notes with the key facts attributed to the sheet.
  - When a dataset contradicts a lesson, flag it in the note and in "In my life"; do not silently drop or accept it.

## 6. After every batch
1. **Glossary**: if the course has a glossary note, keep `glossary_terms.json` up to date and run `link_glossary.py` from `obsidian-casebook` (dry run, check the words, then `--apply`). Set `folders` to `["Courses", "Concepts"]` and `skip_sections` to `["Cards", "Source", "Concepts used"]`.
2. **Related-notes sweep**: search the vault for the new lesson's key names, terms and figures. Add the lesson to the `Seen in` list of each concept it uses, fix a concept note the new lesson makes imprecise, and list in the reply any earlier lessons or cards whose claims it qualifies. Do not rewrite what a captured lesson reports the course said; offer a one-line see-also instead.
3. **Audit**: run `audit_vault.py` from `obsidian-casebook`. Its course checks switch on with a `Courses/` folder (lesson keys, course maps, Resources indexed and linked) on top of the core and recall checks. Fix every FAIL before reporting.
4. Report in one or two sentences what was built and what is pending, then offer the next chunk as a choice.

## 7. Audit mode
Use when the user asks to check a vault, after changing this skill, or before adding lessons to an older vault. READ-ONLY until they approve fixes. Follow the audit mode in `obsidian-casebook`: run the script, judge each finding (a difference may be a deliberate improvement: ask whether to update the skill or the vault), report one short table, fix only after approval, re-run.

## Pitfalls
- A script that loops over a week folder must skip the week page (it has no lesson frontmatter).
- A `next →` link to a note not built yet, or a placeholder link in `Templates/`, fails the audit: use plain text or a real note.
- In a browser batch, only the first navigation may be followed by page actions: use one batch per page. If a batch is refused, fall back to single calls.
- Do not run the course checks on vaults that are not course vaults: use `--only core`.
