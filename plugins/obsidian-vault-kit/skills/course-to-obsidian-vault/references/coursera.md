# Capturing from Coursera

Read this before capturing lessons from Coursera. Page structure was accurate in November 2026; if something here no longer matches what you see, trust the page and tell the user.

1. **Sign-in**: without a session, course URLs redirect to the public page (module titles only). The user signs in and must be enrolled (auditing is fine).
2. **Outline**: open `/learn/<slug>/home/module/N`, wait about 7 seconds (earlier reads return "Loading..."), then read the page text: sections, item types and durations, practice assignments and quiz due dates. Record them in the course map with the date read.
3. **Lesson pages**: videos are `/learn/<slug>/lecture/<id>/<slug>`, readings `/supplement/<id>/<slug>`. Get the ids from the sidebar entries ("Video, <title>, Not submitted, N min"; "Not submitted" means not done). Only the open section's links show. Opening a reading page can tick it as done on Coursera: open readings only when the user asks, and say that a tick may come from the visit.
4. **Video text**: open the Transcript panel beside the video (it stays open on the next lecture); the page text then includes the full transcript, so no audio transcription is needed. Reading the whole page also gives the sidebar progress for the week page.
5. **Long readings**: when a reading links to a long source and the user supplies the file, copy it into `Resources/` with the lesson id in the name, read the whole text (not an automated summary), and rewrite the note from it. Add page ranges for the key parts under Source, and check every figure against the text.
6. **Capture**: videos and readings become lesson notes, `W<module>-<NN>` in course order. Practice assignments, ungraded items and graded quizzes stay on Coursera: list them on the week page under "On Coursera only (not captured here)", and say when a quiz is overdue or due soon.
7. **Finish**: close the tabs you opened.
