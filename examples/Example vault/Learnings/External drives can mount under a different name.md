---
type: learning
area: "Home server"
kind: tech
basis: experience
last_verified: 2026-11-10
tags: [learning, tech]
---
# External drives can mount under a different name

A drive's mount name can change between reboots or ports, so a script that points at the old name fails; mount by the drive's label instead.

## How it actually works
- The system names drives in the order it finds them unless told otherwise.
- Mounting by label (or by its unique ID) gives the same path every time.

## Gotchas
- The error a backup tool shows ("repository does not exist") does not mention the drive.

## Evidence
- Nightly job failed after a reboot; worked again after mounting by label — basis: experience — [[Home server backups]], 2026-11-10

## Seen in
- [[Home server backups]]

## Not to be confused with
- A full or failing drive, which gives write errors instead.
