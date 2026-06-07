# HANDOFF — Agent Foundry

**Last updated:** 2026-06-07

## Cold-start in 30 seconds

1. Read `PRD.md` §0 (mission + decision log D1–D21) and `CLAUDE.md`.
2. Read `INSIGHTS.md` — learning arc, brainstorm history, recommended focus.
3. Read `foundry_registry.json` — check `preferences`, `agents[]`, `brainstorm_sessions[]`.
4. You are ready. Wait for Ram's trigger.

**Trigger phrases:**
- `"begin the brainstorm"` → start Cycle 1 brainstorm (adaptive Q&A, 3–4 candidates, trait scorecard + G1–G5 gates per candidate)
- `"new agent"` → same as above
- `"lock <candidate name>"` → skip brainstorm, go straight to mini-spec + confirmation
- `"I ran it"` → trigger Phase F2 (post-run Professor session, skippable)

## What this project is

Claude Desktop is the Foundry. There is no separate application. Ram opens this project,
says "begin the brainstorm," and Claude runs the full cycle:

1. **Brainstorm** — interactive Q&A, candidates with Learning Position labels (FORWARD /
   FOUNDATIONAL / LATERAL-RIGHT / LATERAL-LEFT / DIAGNOSTIC), 9-trait scores + G1–G5
   verdicts; DIAGNOSTIC slot offered every 2–3 cycles
2. **Lock** — Ram types explicit approval; zero files written before this
3. **Mini-spec** — show goal predicate, tools, memory, loop, termination, SDK rungs; get second confirmation
4. **Generate** — write eight files into `agents/<slug>/`; QA (smoke test green) before handover
5. **Professor session** (Phase F, skippable) — ~10-min pre-run walkthrough + comprehension probes
6. **Ram** opens `<agent-slug>_learning-guide.html` (Part 1), reads it, then opens PyCharm
   and runs `main.py` — the run auto-saves `<agent-slug>_run_output.log`
7. **Post-run session** (Phase F2, skippable) — Ram says "I ran it"; Claude asks 3–5 probes
   anchored to actual runtime output lines; writes `post_run_notes` to registry
8. **Claude** generates `<agent-slug>_learning-insights.html` (Part 2) from the log

## Current state (2026-06-07)

**PRD status:** v8 FINAL — **LOCKED**

**What happened this session (2026-06-07):**

Two major improvement rounds completed:

**Round 1 — Runtime output standard extended (24 elements):**
- FR-C8 expanded from 15 to 24 runtime output elements; ordered by execution phase
- New elements: `[SDK →]`/`[← SDK]` (LLM boundary), `[GOAL PREDICATE]` (G1 evidence),
  `[MODEL DECISION]` (G2 evidence), `[LOOP FEEDBACK]` (G3 evidence), `[CONTEXT]`
  (token tracker), `[SESSION MEMORY]`/`[APP MEMORY]` (memory type labels), `[ERROR: ...]`
  (failure classification), `[TRUST FENCE]`, `[PLAN PROGRESS]` (all agents, mandatory)
- QA grep contract updated to require 8 new mandatory output elements
- Hard Requirement #8 added: `tee_to_log()` context manager mirrors stdout to
  `<agent-slug>_run_output.log`

**Round 2 — Paired HTML artifacts + 8 curriculum improvements:**
- `briefing.html` renamed to `<agent-slug>_learning-guide.html` (Part 1, pre-run, 13 sections)
- New `<agent-slug>_learning-insights.html` (Part 2, post-run, 11 sections) added as
  mandated file — generated from runtime log; proves agency with quoted output lines
- Agent file count raised from 5 to 8 mandated files
- **Learning Position System** added to brainstorm step: FORWARD / FOUNDATIONAL /
  LATERAL-RIGHT / LATERAL-LEFT / DIAGNOSTIC labels with classification algorithm
- **Compound similarity score** (domain×0.4 + rungs×0.4 + traits×0.2; >0.7 = HIGH SIMILARITY)
- **DIAGNOSTIC slot** (every 2–3 cycles): deliberately fails G1 or G3 so Ram practises
  gate rejection
- **LO-12 coverage trigger**: steer toward failure-prone domain when no prior agent has
  produced `[ERROR: STRUCTURAL]` or `[ERROR: POLICY]`
- **Phase F2** (post-run Professor session): 7 probe types anchored to runtime output lines;
  writes `post_run_notes` to registry
- **`post_run_notes` schema**: `runtime_surprises[]`, `post_run_probes_asked[]`,
  `next_cycle_expectation`, `skipped`
- **5-cycle synthesis arc** in FR-E4: per-cycle synthesis statement, cross-agent link,
  opening recall question — template for §6 of INSIGHTS.md
- **Agent schema** documented in `foundry_registry.json` → `_agent_schema_note`

**Files modified this session:**
- `CLAUDE.md` — Operating Cycle steps 1 and 8.5 (new); Hard Requirement #8; FR-C8 table;
  QA grep contract; project structure; learning-insights.html spec
- `PRD.md` — FR-A1, FR-A3, FR-E1, FR-E4, FR-F5 (new); FR-C8/FR-C9; decision log D20/D21
- `foundry_registry.json` — `_agent_schema_note` object added
- `HANDOFF.md` — this file

**Exists:**
- `PRD.md` v8 (locked) · `CLAUDE.md` (synced) · `AGENT_LEARNING_AND_AGENCY_GATES.md`
- `foundry_registry.json` (preferences seeded + brainstorm_sessions[] with cycle-1 candidates
  + `_agent_schema_note` documenting full agents[] schema)
- `INSIGHTS.md` (initialized — no cycles yet; brainstorm history from 2026-06-07 session)
- `ROADMAP.md` (no agents yet)
- Folder structure: `agents/` · `reference/` (chef guide + master guide) · `reviews/` · `prompts/`

**Does not exist yet:** any generated agent, any `_learning-guide.html`, any
`_learning-insights.html`, any `_run_output.log`, any `learning` or `post_run_notes` records

## Next steps

1. Ram opens Claude Desktop, loads this project folder, says **"begin the brainstorm"**
2. Cycle 1 brainstorm seeded from `foundry_registry.json` preferences:
   - Domains: morning-briefing / health-habits / learning-research
   - Focus trait: observe–reason–act feedback loop
   - Build size: minimal
   - SDK target: rungs 1–2 (`query()` + message anatomy; goal predicate + loop + circuit breaker)
3. Previous session surfaced three candidates — assign Learning Position labels:
   - **A — Morning Spark** (morning-briefing): FORWARD (rungs 1–2 not started); all 5 gates pass ✓ *(recommended)*
   - **C — Study Prep Agent** (learning-research): FORWARD (rungs 1–2 not started); all 5 gates pass ✓
   - **B — Focus Booster** (health-habits): G3 borderline; needs-fix before lock
   - *No DIAGNOSTIC slot yet (cycle 1 — not required until cycle 2–3)*
4. Ram locks a candidate → Claude generates eight files + QA → Professor session (Phase F)
5. Ram runs agent in PyCharm → Phase F2 triggered by "I ran it"
6. Claude generates `_learning-insights.html` (Part 2) from `_run_output.log`

## Open questions

- None blocking. PRD v8 locked. Awaiting first brainstorm session in Claude Desktop.
