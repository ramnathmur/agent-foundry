# ROADMAP — Agent Foundry

One line per agent built (FR-E1). Cycle plan from PRD v9 §12.

| Cycle | Slug | Date | Gates | SDK rungs | Status |
|---|---|---|---|---|---|
| 1 | study-prep | 2026-06-07 | G1 G2 G3(partial) G4 / G5 N/A | 1+2 | closed — cap reached; agent worked correctly per FR-A3 |
| 2 | study-buddy | 2026-06-08 | G1 G2 G3 G4 / G5 N/A | 3 | closed — ran 15:13; model-done at turn 5; goal_met=true; ~$0.64 / 18K tokens; Phase F2 ran 3 of 4 probes |
| 3 | recipe-companion | 2026-06-08 | G1 G2(deepened) G3(three-layer) G4(four exits) / G5 N/A | 4 | closed 2026-06-11 — Phase F2 ran 3 probes (conceptual; main.py env dep unresolved); gaps recorded |
| 4 | mac-advisor | 2026-06-12 | G1 G2(strongest) G3(partial-design-gap) G4(cap clean) / G5 N/A | 5 | closed 2026-06-12 — ran cap_exit 8/8; cost $1.87; Phase F2 4 probes under new concept-first register; all 4 landed strongly |
| 5 | research-lead | 2026-06-13 | G1(compound) G2 G3(partial-act-strategy-gap) G4 / G5 N/A | 8 | closed 2026-06-13 — mock-assisted run; max_tokens kwarg error on real SDK calls; subagent cap 5/5; synthesis not produced; Phase F2 3 probes (Probe 1 STRONG, Probe 2 partial, Probe 3 STRONG); rungs 6+7 consciously skipped |

**Planned curriculum (PRD §12):**

1. ✅ First minimal agent (study-prep — learning-research) — rungs 1–2 — *closed Cycle 1*
2. ✅ Multi-turn agent (study-buddy — learning-research) — rung 3 — *closed Cycle 2*
3. ✅ Custom tools (recipe-companion — health-habits/food) — rung 4 — *closed Cycle 3; Phase F2 3 probes complete*
4. ✅ Permission modes / allowed_tools (mac-advisor — consumer-research) — rung 5 — *closed Cycle 4; ran cap_exit; phase-handoff instruction-leak design lesson surfaced and named by Ram*
5. ⬜ Hooks + JSONL span trace — rung 6 — *Cycle 6 target (skipped in Cycle 5 by Ram's choice)*
6. ⬜ Independent verifier — rung 7 *(skipped in Cycle 5 by Ram's choice)*
7. ✅ Subagents + context compaction — rung 8 — *introduced Cycle 5 (research-lead); rungs 6+7 skipped; mock-assisted run*
- Any cycle: negative-control workflow (watch the gates fail red)

**Domain coverage status (after Cycle 5):**

| Domain | Agents built | Notes |
|---|---|---|
| learning-research | 3 | study-prep, study-buddy, research-lead — all closed |
| morning-briefing | 0 | candidate available: Morning Spark v4; deferred 4× now — overdue for serious consideration in Cycle 6 |
| health-habits | 1 | recipe-companion — closed. Habit Pulse v3 candidate still available |
| consumer-research | 1 | mac-advisor — closed. Added as new domain via others-shortcut in Cycle 4 |

**Spec evolution log:**

- 2026-06-07 — PRD v8 → v9 + FR-C10 (Audience Register), FR-C11 (HTML backup), FR-F7 (Professor Checkpoints). FR-C5/C9/F2/F5 rewritten lay-first.
- 2026-06-08 — Cycle 2 study-buddy delivered + ran + closed. main.py introduced the
  predicate-satisfied exit branch (4 total exit paths). New active gap recorded:
  feature-vs-capability distinction.
- 2026-06-08 (later) — Cycle 3 recipe-companion delivered. main.py introduces the
  `🔗 [TOOL CHAIN] N` runtime label — first cycle where the count can exceed 1.
  Smoke test caught one repair: the @tool decorator wraps each function into an
  SdkMcpTool object whose underlying coroutine lives at `.handler`. Pattern
  documented in gotchas_mastered for future @tool-using agents.
- 2026-06-11 — Cycle 3 recipe-companion closed. Phase F2 ran 3 probes (conceptual;
  main.py not run due to env dep issue in PyCharm venv). Feature-vs-capability gap
  (carried from Cycle 2) confirmed closed in Phase 0. New gap recorded:
  predicate-vs-signal reliability. Cycle 4 ready — rung 5 target.
- 2026-06-12 — Cycle 4 mac-advisor delivered, ran, and closed. First others-shortcut
  lock in registry (spec file → adapt → confirm). Rung 5 demonstrated visibly: model
  attempted synthesize_recommendation in research turn 2 and was SDK-level blocked.
  Cap fired at 8/8 — labelled exit "EXIT: research cap" vs "GOAL MET" distinction
  visible in output. Root cause analysis revealed phase-handoff instruction leak
  (code-side O-R-A printed remediation to terminal, not into model context) — new
  carry-forward gap, with Ram having named the fix in Probe 1 (clearance-register
  pattern). **PRD/CLAUDE.md Checkpoint 4 register change** applied mid-cycle:
  rewritten from quote-first to concept-first four-beat structure (real-world
  analogy → why it matters → runtime line as illustration → open concept question).
  Probes 1–4 all landed strongly under the new register — first cycle in 4 where
  Ram didn't push back on probes. Format change permanent — applies to all future
  cycles.
- 2026-06-13 — Cycle 5 research-lead delivered, ran, and closed. Ram consciously skipped
  rungs 6 (hooks) and 7 (independent verifier) to jump to rung 8 (subagents + context
  compaction). Mock-assisted run: all real SDK calls failed with `query() got an
  unexpected keyword argument 'max_tokens'`; fallback mock research database ran
  correctly. Architecture demonstration valid: angle selection, sub-researcher dispatch,
  gap detection, follow-up dispatch, principled stop all worked. New gap surfaced:
  act-strategy adaptation on starvation — detecting a gap and re-dispatching to the
  same data source with the same parameters is not a change in act-strategy.
  Phase F2 3 probes: Probe 1 (angle selection → model autonomy) STRONG; Probe 2
  (follow-up confidence → act-strategy) partial with scaffolding; Probe 3 (sub-agent
  isolation → interface contract) STRONG. Sub-agent interface contract named by Ram:
  "task, boundary, what input to get and what output to give."
