---
name: taiwan-tech-risk-semantic-layer
description: Use when answering data questions for the Taiwan Semiconductor & Tech Stock Risk Dashboard, including risk score definitions, SQLite table choice, API interpretation, freshness, and caveats.
---

# Taiwan Tech Risk Semantic Layer

Use this skill to answer Taiwan Semiconductor & Tech Stock Risk Dashboard data questions with the source-backed context in `references/semantic-layer.md`.

## Start Here

1. Read `references/semantic-layer.md`.
2. Use the listed canonical metrics, tables, grains, joins, filters, and caveats.
3. Check freshness before answering time-sensitive questions.
4. When sources disagree or coverage is weak, say so and verify against the cited source.

## References

- `references/semantic-layer.md`: metrics, tables, filters, query patterns, gotchas, freshness, and open questions.
- `references/source-inventory.md`: sources checked, coverage level, permissions, rejected candidates, and update boundaries.
- `references/evidence.md`: concise provenance for metric, table, and caveat claims.

## Answering Rules

- Treat this skill as source-selection guidance, not as a substitute for live reads.
- Preserve metric grain, time zone, date columns, filters, and join keys.
- Label stale, inferred, partial, or conflicted evidence.
- Do not describe the dashboard as investment advice or a stock-price prediction system.
