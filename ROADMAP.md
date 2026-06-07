# ROADMAP — Agent Foundry

One line per agent built (FR-E1). Cycle plan from PRD v9 §12.

| Cycle | Slug | Date | Gates | SDK rungs | Status |
|---|---|---|---|---|---|
| 1 | study-prep | 2026-06-07 | G1 G2 G3(partial) G4 / G5 N/A | 1+2 | delivered — cap reached; agent worked correctly per FR-A3 (mock-DB perception trap, not agent failure) |
| 2 | *(TBD — Cycle 2 brainstorm pending; see GitHub issue #4)* | | | 3 | brainstorm awaiting |

**Planned curriculum (PRD §12):**

1. ✅ First minimal agent (study-prep — learning-research) — rungs 1–2 — *delivered Cycle 1*
2. ➡️ Multi-turn agent — rung 3 — *Cycle 2 target (FORWARD)*
3. Custom tools + permissions — rungs 4–5
4. Hooks, span trace, independent verifier — rungs 6–7
5. Subagents + context compaction — rung 8
- Any cycle: negative-control workflow (watch the gates fail red)

**Spec evolution log:**

- 2026-06-07 — PRD v8 locked, then extended same day with FR-C10 (Audience Register),
  FR-C11 (HTML backup), FR-F7 (Professor Checkpoints). FR-C5 / FR-C9 / FR-F2 / FR-F5
  rewritten lay-first. See HANDOFF.md for the change set.
