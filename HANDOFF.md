# HANDOFF — Agent Foundry

last_updated: 2026-06-07 (end of session)
prd_version: v9 + FR-C10 Audience Register + FR-C11 HTML backup rule + FR-F7 Professor Checkpoints (added 2026-06-07)
cycle: 1 CLOSED → ready for Cycle 2 brainstorm
locked_candidate: (none — Cycle 2 not yet brainstormed)

## Cycle 1 Outcome — study-prep agent

  Slug: study-prep  ·  Domain: learning-research  ·  Rungs introduced: 1+2  ·  Position: FORWARD
  Locked: 2026-06-07  ·  Status: closed (Phase F + F2 skipped per Ram's mid-cycle redirect)

### Run result (2026-06-07 17:35:39)

  exit: cap_reached — 10/10 iterations consumed
  goal_met: false — 0/3 topics covered
  tokens: 137,070 in / 1,438 out
  cost: ~$2.10
  root_cause: mock_perception_trap
    MOCK_SEARCH_DB used exact-key lookup; model's natural-language queries
    never matched a stored key; all 10 searches returned [].
    G4 circuit breaker fired correctly — the loop terminated safely.

### Gate verdicts (this run)

  G1 PASS — is_coverage_met() evaluated as bool every step
  G2 PASS — model chose tool + query at runtime (10 distinct queries)
  G3 PARTIAL — O→R→A loop ran but trapped in zero-information feedback state
  G4 PASS — hard cap fired at 10/10 as designed (principled stop)
  G5 N/A — rung 1-2; verifier first appears at rung 7

### Gotchas mastered (extracted from main.py)

  - duplicate-url     (main.py:88)  — dedup guard before append to coverage_map
  - transient-error   (main.py:107) — ConnectionError routed as TRANSIENT → skip
  - api-key-bypass    (main.py:215) — ANTHROPIC_API_KEY stripped from child env
  - trust-fence       (main.py:260) — external content wrapped before LLM ingestion

### Phase F / F2 status

  Phase F (pre-run Professor session):  SKIPPED
  Phase F2 (post-run Professor session): SKIPPED
  Mid-cycle Ram redirected to a spec rewrite + HTML refresh instead of probes.
  Registry entry for study-prep records this as `learning.skipped: true` with a
  narrative of what was learned by behaviour-evidence rather than formal probes
  (see foundry_registry.json → agents[0] → learning).

## Major spec changes this session

  PRD.md + CLAUDE.md both updated to v9 + extensions. Commits cafde78 (merged via PR #1).

  NEW requirements:
    FR-C10  Audience Register — lay-first body, sidebar deeper-dives,
            gate codes G1-G5 confined to code annotations and the insights file's
            §11 glossary footer; functional aliases used in all student-facing
            surfaces (did-it-finish check, model's own choice, learning from
            what it saw, principled stop, independent check)
    FR-C11  HTML backup-then-rewrite — prior versions preserved as
            *_technical-v<n>.html before regeneration (no-delete honoured)
    FR-F7   Professor Checkpoints — four enforced narration moments:
              Checkpoint 1: Post-lock briefing
              Checkpoint 2: Pre-run framing
              Checkpoint 3: Post-run debrief (BEFORE any Phase F2 probe)
              Checkpoint 4: Pre-probe context

  REWRITTEN contracts:
    FR-C5  13-section learning-guide contract — lay-first titles; sections 4, 5, 10
           marked as deeper-dive sidebars (skippable)
    FR-C9  11-section insights contract — sections 4 (Traits in Action) and 7 (Agent
           Spectrum Placement) preserved verbatim per Ram's audit; §1 expanded to
           "About this run" (setup grid + result snapshot, cold-read fix); §3
           refocused on goal verifiability (no longer redundant with §1)
    FR-F2  Phase F probes rewritten in functional language; gate codes parenthetical only
    FR-F5  Phase F2 probes rewritten in functional language; G1-G5 never spoken to Ram
    CLAUDE.md §8.5 sync'd; new top-level Audience Register section; new
    Enforced Checkpoints subsection under "The Professor — Voice and Character";
    new HTML Regeneration Protocol section

## Study-prep HTMLs — current state on disk

  Lay-first rewrites under new FR-C5 / FR-C9 contracts:
    agents/study-prep/study-prep_learning-guide.html        (Part 1, 40 KB)
    agents/study-prep/study-prep_learning-insights.html     (Part 2, 44 KB)
  Technical-v1 backups preserved per FR-C11:
    agents/study-prep/study-prep_learning-guide_technical-v1.html       (44 KB)
    agents/study-prep/study-prep_learning-insights_technical-v1.html    (50 KB)
  Per-trait runtime anchors added to guide §3 (each trait card names the runtime
  label that proves it).

## Repo hygiene state

  Public · MIT-licensed · social preview uploaded · all hygiene checks green
  PR history (both merged):
    #1  Cycle 1 remediation: lay-first contracts, Professor checkpoints, study-prep HTMLs
    #2  Share-readiness: add MIT LICENSE; remove FRESH_SESSION_PROMPT.md
  Branches on origin: master only (cycle-1-remediation and share-readiness deleted)
  Open issues:
    #3  Add CI smoke-test workflow for all agent folders
    #4  Cycle 2 brainstorm: SDK rung 3 (multi-turn session memory)
  Master branch protection: PR required; force-push and deletion blocked; admin enforced

## Next session — Cycle 2 brainstorm

  RAM_INTENT:   start Cycle 2 brainstorm for SDK rung 3
  TARGET_RUNG:  3 (ClaudeSDKClient multi-turn + session_id capture/resume)
  POSITION:     FORWARD (rung 3 is new ground; satisfies PRD §7.1)
  PLANNING_REF: GitHub issue #4

  PROFESSOR_OPENING — Phase 0 warm-up (FR-F6):
    Part A — Brief (2-3 min, one-way, structured emoji block):
      1. Report card     ← report_card object in registry
      2. Complexity arc  ← one sentence per prior cycle (just Cycle 1)
      3. Top 2 gaps      ← top_active_gaps in registry
      4. Gotchas mastered ← gotchas_mastered array in registry
      5. Forward seed    ← rung 3 unlocks session-carried memory across calls

    Part B — Interrogation (3-5 min, Socratic, 2-3 recall questions):
      Anchored to Cycle 1's specific runtime moments + recall_question_next_cycle
      from agents[0].learning. Functional language only (no G1-G5 codes spoken).
      Sample probes:
        - "When the first search came back empty, what did the agent do? Was
           that the loop working or failing?"
        - "When the safety cap fired at 10/10, was that the agent failing or
           succeeding? Why?"
        - "What's the difference between an empty result and a structural
           failure — how can the agent tell them apart?"

  READ_AT_SESSION_START: SESSION.md (fast path) → this file → foundry_registry.json
                        → INSIGHTS.md → ROADMAP.md
  TRIGGER_PHRASE:        "begin the brainstorm" or "new agent" → Phase 0 fires
