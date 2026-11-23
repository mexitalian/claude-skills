---
type: regex
target: { source: file, path: "vault/Cases/Register new address.md" }
pattern: '(?:reference|case|file|customer) (?:no\.?|number)[^\n]*\d{4}|€|EUR'
match: not_contains
flags: i
---
