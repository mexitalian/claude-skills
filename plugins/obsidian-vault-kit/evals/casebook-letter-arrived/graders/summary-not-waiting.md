---
type: regex
target: { source: file, path: "vault/Cases/Register new address.md" }
pattern: '\*\*Waiting for:\*\*[^\n]*(?:letter|certificate)'
match: not_contains
flags: i
---
