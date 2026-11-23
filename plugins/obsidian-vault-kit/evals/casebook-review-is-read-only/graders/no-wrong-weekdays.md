---
type: regex
target: last_message
pattern: '(?:Mon|Wed|Thu|Fri|Sat|Sun)[a-z]*,? (?:1 Dec|December 1\b)|(?:Mon|Tue|Wed|Thu|Sat|Sun)[a-z]*,? (?:4 Dec|December 4\b)|(?:Mon|Tue|Wed|Fri|Sat|Sun)[a-z]*,? (?:10 Dec|December 10\b)'
match: not_contains
weight: 2
---
