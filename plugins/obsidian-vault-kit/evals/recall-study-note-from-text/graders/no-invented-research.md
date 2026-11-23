---
type: regex
target: { source: file, path: "vault/Notes/The two-minute rule.md" }
pattern: '(?:\d+\s?%|research (?:shows|suggests|finds)|studies (?:show|suggest|find)|according to)'
match: not_contains
flags: i
---
