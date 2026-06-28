# HANDOFF — Agent Foundry

last_updated: 2026-06-25 (Cycle 6 morning-spark CLOSED; Cycle 7 ready; rung 6 hooks confirmed introduced)
prd_version: v9 + FR-C10 Audience Register + FR-C11 HTML backup rule + FR-F7 Professor Checkpoints (Checkpoint 4 rewritten 2026-06-12)
cycle: 7 READY TO BRAINSTORM · prior: 6 CLOSED · 5 CLOSED · 4 CLOSED · 3 CLOSED · 2 CLOSED · 1 CLOSED

## Cycle 7 — next session

  Rung target: 6 (FOUNDATIONAL carry — hooks in new domain + path-dependent predicate)
               or 7 if Ram wants to push to independent verifier
  Position: FOUNDATIONAL (rung 6 in health-habits domain; path-dependent predicate is the new concept)
  Agent: Habit Streak + Accountability (locked 2026-06-14 as Cycle 7 first-choice)
  Domain: health-habits

  What makes this agent distinctive:
    Path-dependent predicate — the goal shape changes depending on whether the streak was kept or broken.
    "Done" looks different on success (streak logged, encouragement delivered) vs failure (miss logged,
    accountability message delivered, recovery plan offered). Two valid "done" outcomes, one predicate.
    This is the most pedagogically distinctive predicate concept in the candidate list.

  Carry-forward gaps to probe in Phase 0:
    1. Act-strategy adaptation (Cycle 5 gap, CLOSED in Cycle 6 Probe 3) — Ram independently said
       "call a different weather tool" when the primary fails. Gap confirmed closed. No longer carry-forward.
    2. Path-dependent predicate (NEW for Cycle 7) — how do you write briefing_complete() when the
       goal has two valid outcomes (success branch and failure branch)? Both should return True from
       the predicate, but the label matters.
    3. Cost economics (deferred 6 consecutive cycles) — morning-spark cost $0.71 for one clean run.
       Cycle 7 is a natural place to do the daily/monthly dollar-math drill explicitly.

  Recall question for Phase 0 Part B:
    Primary: "Morning Spark's goal predicate had five conditions — all five had to be True.
    In Cycle 7, the agent tracks whether a habit streak was kept or broken. Both outcomes are valid
    completions. How do you write a goal predicate that returns True on both outcomes, but
    also tells the loop which branch fired?"
    (Anchored to Cycle 6 recall_question_next_cycle — path-dependent predicate as new concept)

  Secondary (optional, only if time):
    "What is the difference between the guard denying a tool call and the SDK's permission_mode
    denying a tool call? Which one does the model see a reason for?"
    (Anchored to Cycle 6's two-gate discovery)

  Next session opens with Phase 0 Part A (report card) + Part B (recall questions).

## Cycle 6 — Morning Spark (closed reference)

  Slug: morning-spark · Domain: morning-briefing · Rung: 6 · Closed: 2026-06-25
  Status: files delivered · smoke 32/32 green · main.py ran 3 times (goal met on run 3; $0.71)
          · Phase F2 3 probes complete

### What this agent does

  Produces a morning briefing — weather, today's date, top headline — by calling five tools in
  sequence, then checking quality, then synthesizing. PreToolUse hook fires before every tool call;
  blocks repeated (tool_name, params) pairs with a variation instruction. PostToolUse hook fires
  after every executed tool; writes one JSONL span to morning-spark_spans.jsonl. Goal predicate:
  weather AND date_info AND headline AND quality_passed AND briefing (five-part compound).
  App memory: briefing_log.json persists yesterday's headline_preview for the cross-day guard.

### What makes this rung 6

  Two hooks registered on ClaudeAgentOptions via HookMatcher(matcher=None) — fires on all tools.
  PreToolUse can deny with a reason; PostToolUse writes audit evidence. Module-level _agent_state
  and _hook_state dicts are the bridge between hooks and the agent loop (hooks fire inside the SDK
  pipeline, not inside the while-loop). HookMatcher(matcher=None) matches every tool including
  harness tools (ToolSearch) — the model calls ToolSearch first in every turn to load MCP schemas.

### Run result (2026-06-25 — 3rd attempt)

  Exit: GOAL MET — briefing_complete() = True
  Turns: 1/6 · Tool calls: 6/12 · Hook denials: 0 · Spans written: 6
  Cost: $0.71 / 18,094 in / 777 out tokens · briefing_log.json written

### Three bugs found across 3 runs

  Bug 1 (smoke test): Windows %-d format string in _MOCK_DATE — fix: _now.day integer
  Bug 2 (run 1): hook input_data is a dict, not an object — fix: _get_field() helper
  Bug 3 (run 2): permission_mode='dontAsk' without allowed_tools silently denies all MCP
    tools AFTER PreToolUse says ALLOW. Fix: add ALL_ALLOWED list to ClaudeAgentOptions.
    Diagnostic: PreToolUse prints ALLOW → no PostToolUse span → model says "tool was denied."
    The silence between ALLOW and execution is the signal.

### Gate verdicts

  G1 PASS — five-part compound predicate; all five flipped True in turn 1.
  G2 PASS — model chose "technology" headline category; called fetch_date + fetch_headline in parallel.
  G3 PASS — PreToolUse guard fired 0 times in clean run (insurance pattern); demonstrated in runs 1–2
             when dict bug caused 11 denials and model tried to adapt.
  G4 PASS — both exit paths reachable: goal-met (run 3) and cap-hit (runs 1–2).
  G5 N/A — rung 7 not yet introduced.

### Phase F2 — 3 probes answered (concept-first four-beat register)

  Probe 1 (two-gate problem): Ram said stage-level logging is the fix. Distributed tracing framing
    reached independently. STRONG.
  Probe 2 (PostToolUse as execution proof): Correctly identified result_length: 0 = tool ran,
    returned empty. Stopped short of remediation path. CORRECT.
  Probe 3 (act-strategy on 503s): Ram said "call a different weather tool" — act-strategy
    adaptation applied without scaffolding. Cycle 5 gap confirmed CLOSED. STRONG.

### New GOTCHAs recorded in registry

  hook-input-is-a-dict — use dict.get() or _get_field() helper; getattr() on dict returns default
  dontAsk-requires-allowed-tools — always set allowed_tools with dontAsk; without it, all MCP
    tools silently denied at SDK permission layer after PreToolUse ALLOW

### Files (all in agents/morning-spark/)

  prompt.md                               blueprint, cold-session contract
  morning-spark_learning-guide.html       Part 1 — pre-run 13 sections
  morning-spark_learning-insights.html    Part 2 — post-run 11 sections (generated 2026-06-25)
  main.py                                 hooks + goal predicate + 5-tool MCP server
  smoke_test.py                           32 tests — all green after 3 repairs
  requirements.txt                        claude-agent-sdk, pytest
  .env.example                            auth notes — no ANTHROPIC_API_KEY
  README.md                               run instructions
  briefing_log.json                       app memory — written on goal-met exit
  morning-spark_spans.jsonl               6 spans from run 3
  morning-spark_run_output.log            3 runs appended

## Cycle 5 — Research Project Lead (closed reference)

  Slug: research-lead · Domain: learning-research · Rung: 8 · Closed: 2026-06-13
  Skipped: rungs 6 (hooks) and 7 (independent verifier) — Ram's conscious choice to jump to rung 8
  Status: files delivered (8/8) · smoke 38/38 green · main.py ran (mock-assisted; subagent cap 5/5)
          · Phase F2 3 probes complete

### What this agent does

  Answers a research question by dispatching independent sub-researchers, each investigating a
  different angle, then synthesising their findings into a single confidence-scored briefing.
  Main agent selects research angles (via model decision), dispatches sub-researchers as independent
  ClaudeSDKClient conversations (context compaction), collects reports, detects gaps, dispatches
  follow-ups, and attempts synthesis. Safety caps: 5 sub-researchers total (3 initial + 2 follow-up),
  2 synthesis attempts, confidence threshold 0.7 for synthesis to count as success.

### What makes this rung 8

  Each sub-researcher is its own ClaudeSDKClient instance — its own independent conversation with
  the model, completely invisible to the other sub-researchers. When a sub-researcher finishes, its
  full internal process (all tool calls, reasoning steps, back-and-forth) is compressed into one
  compact structured report and returned to the main agent. The sub-researcher's context window is
  then discarded. This is context compaction: five parallel conversations created and destroyed, each
  handing the main agent only a summary. The main agent never sees the sub-researchers' internal
  reasoning — only the output.

### Run result (2026-06-13 14:07:13)

  Exit: subagent_cap (5/5 sub-researchers used)
  Goal met: FALSE — synthesis not produced
  Sub-researchers: 3 primary (technical, user, contrarian) + 2 follow-up
  All confidence scores: 0.30 (threshold 0.70)
  All gap flags: True
  Run mode: MOCK-ASSISTED — all real SDK calls hit `query() got an unexpected keyword argument
            'max_tokens'`; fallback mock research database (5 pre-seeded records: tech-001,
            tech-002, usr-001, usr-002, con-001) ran correctly for all tool calls
  Elapsed: ~0.0s (mock speed); token tracking unavailable

### What the run demonstrated

  Five rung-8 moments confirmed working in the run log:
    1. Angle selection: `🎲 [MODEL DECISION] selected: technical, user, contrarian · alternatives: market, regulatory, historical`
       The model chose 3 of 6 available angles based on the question — not hard-coded.
    2. Compound goal predicate: `📐 [GOAL PREDICATE] is_goal_met(state) → False · all_dispatched_returned=True · synthesis_produced=False · synthesis_confidence=0.0`
       Three conditions, all required, evaluated at every step.
    3. Gap detection and follow-up dispatch: `🔄 [LOOP FEEDBACK] 3 report(s) need follow-up → dispatching`
       The agent read all three reports, detected gaps, and dispatched reinforcements.
    4. Context isolation: each sub-researcher box in the log (`Sub-Researcher: technical`) ran
       independently — lookup_source → extract_finding → synthesize — with no cross-visibility.
    5. Principled stop: `🏁 EXIT: subagent cap — 5/5 sub-researchers used without producing synthesis`
       Labelled, clean, with full summary.

### Root cause of cap exit — act-strategy gap (CRUCIAL — this is the Cycle 5 learning)

  The follow-up sub-researchers returned identical 0.30 confidence because they queried the same
  mock data source with the same parameters and retrieved the same pre-seeded records. The gap
  detection loop (code-side O-R-A) correctly identified that reports had gaps and dispatched
  follow-ups. But the act step was unchanged: the follow-ups were sent to the same source, not
  a different one. Detecting a gap is necessary but not sufficient — the act step must change
  strategy, not just repeat the attempt.

  This is a design gap, not a code bug. The fix: follow-up dispatch brief should force a different
  source, a different search angle, or a broader framing. The current code sends follow-ups with
  the same tool parameters, producing identical results in a mock environment.

  Rung 6 (hooks) is the natural lever: a PreToolUse hook that detects repeated identical
  `lookup_source` calls and injects a variation instruction before the call executes.

### Phase F2 — 3 probes answered

  Probe 1 (angle selection — model's own choice):
    Ram's answer: "If it was hard coded irrespective of the topic, the same three angles would have
    been used. In cases where it is aligned, it may do the expected level of the work, but in most
    cases it will be misaligned or totally off the mark, in which case the wrong angle will be applied."
    Verdict: STRONG. Unprompted framing of the misalignment consequence — a workflow always applies
    the same lens regardless of topic relevance. Named the right failure mode without prompting.

  Probe 2 (follow-up confidence — learning from what it saw):
    Ram's initial answer: "maybe the agents were not up to the task and that's why they fell below
    the confidence threshold."
    Verdict: PARTIAL — attributed the result to agent quality, not data-source structure.
    Scaffolded to: same data source → same records → identical confidence. The act step didn't
    change, so the result couldn't change. Named and recorded as the act-strategy adaptation gap.
    Carry-forward: "What is the difference between 'try again' and 'try differently'?"

  Probe 3 (sub-agent isolation — interface contract):
    Ram's answer: "The sub researchers, by design, are supposed to be independent. If they were
    exposed to the other, then it will pollute their own independence and also change their outcome
    because they have received inputs from other agents which they should not have. Sub-agents
    typically have a task, a boundary, what input to get and what output to give."
    Verdict: STRONG. Named the four-field interface contract (task, boundary, input, output)
    unprompted. Independently derived the isolation design principle and stated the consequence
    of violating it ("pollute their own independence").

### Gate verdicts

  G1 (did-it-finish check) PASS — compound three-part predicate evaluated at every step;
            stayed False throughout because synthesis_produced never cleared.
  G2 (model's own choice) PASS — model selected 3 of 6 angles based on the research question.
  G3 (learning from what it saw) PARTIAL — gap detection + follow-up dispatch worked correctly
            (code-side O-R-A strong); but act-strategy was unchanged (same source, same params,
            same confidence). Design gap named and recorded for Cycle 6.
  G4 (principled stop) PASS — EXIT: subagent cap 5/5 with labelled reason; full summary printed.
  G5 (independent check) N/A — independent verifier not yet introduced (rung 7 was skipped).

### New GOTCHA recorded in registry

  corrupt-response — when a sub-researcher's query() call returns malformed, empty, or
  unparseable JSON, treat it as low-confidence (confidence=0.0, gap=True) rather than crashing
  the loop. Surfaced from main.py:523 — the fallback classification for unexpected response shapes.

### Files (all in agents/research-lead/)

  prompt.md                                blueprint, cold-session contract
  research-lead_learning-guide.html        Part 1 — lay-first pre-run reading
  research-lead_learning-insights.html     Part 2 — post-run insights (generated 2026-06-13 from run log)
  main.py                                  sub-researcher dispatch loop; 5-slot cap; compound predicate
  smoke_test.py                            38 tests — all green after module-level import repair
  requirements.txt                         claude-agent-sdk, pytest, pytest-asyncio
  .env.example                             auth notes — no ANTHROPIC_API_KEY
  README.md                                PyCharm run mechanics
  research_briefs.json                     5 mock records (tech-001, tech-002, usr-001, usr-002, con-001)
  research-lead_run_output.log             first run log (300 lines; 2026-06-13 14:07:13)

### Smoke test repair (recorded for future reference)

  Original smoke tests failed because `query` was imported locally inside `run_sub_researcher()`
  and `main()`, so `patch('main.query')` couldn't find the symbol at module level.
  Fix: added module-level `try: from claude_agent_sdk import query / except ImportError: query = None`
  and removed the local imports. 38/38 green after repair.

## Cycle 4 — Mac Advisor (closed reference)

  Slug: mac-advisor · Domain: consumer-research · Rung: 5 · Closed: 2026-06-12
  Status: files delivered (8/8) · smoke 25/25 green · main.py ran (cap exit 8/8; $1.87)
          · Phase F2 4 probes complete under new concept-first register

### What this agent does

  Recommends the best MacBook Pro M4 variant for a software developer + AI practitioner workload
  in the Indian market. Two-phase agent loop: Phase 1 (research) gives the model 4 tools —
  search_specs, check_price, analyze_thermal, compare_variants — and denies synthesize_recommendation.
  Phase 2 (synthesis) inverts the palette: synthesize_recommendation is allowed, the 4 research
  tools are explicitly disallowed. Phase boundary is enforced at the SDK level via
  permission_mode='dontAsk', not via system-prompt instructions. The headline rung-5 capability:
  when the model attempted to skip to synthesis in research turn 2, the SDK silently denied the
  call — visible in the run log as "synthesize_recommendation tool is blocked by permission_mode."

### Run result (2026-06-11T19:18:26)

  Exit: research_cap (8/8)
  Goal met: FALSE — no recommendation produced
  Total tool calls: 13/24 (turn 1: 11 calls; turns 2–8: model looped 'nothing to do')
  Cost: ~$1.87 / 16,833 in tokens / 7,040 out tokens
  Price drop detected: TRUE (₹2,49,900 → ₹2,29,900 on 2nd check_price call)
  Thermal conflict detected by code-side O-R-A: TRUE — but resolution didn't propagate to model

### Root cause of cap exit (CRUCIAL — this is the Cycle 4 learning)

  Phase-handoff instruction leak. The code-side O-R-A loop saw the thermal contradiction
  ("none detected" vs "15-20% under sustained AI inference"), computed the right remediation
  step ("call analyze_thermal with sustained_load workload"), and printed it to the terminal:

      ── A ──  Inserting resolution step: call analyze_thermal with 'sustained_load' workload

  But the model's turn-2 context received only the binary state flag conflict_resolved=False —
  not the structured remediation instruction. From turn 3 onward the model said "nothing to do"
  five times because it genuinely had no idea what to do. Cap fired correctly as a principled
  stop. This is NOT an agent failure — it's a state-propagation design lesson. Ram named the
  fix in Phase F2 Probe 1: a "clearance register" pattern.

### Gate verdicts

  G1 PASS — predicate-only, not model text. Production proof: predicate stayed False even
            when model emitted "RESEARCH COMPLETE" because conflict_resolved=False.
  G2 PASS (strongest to date) — model freely selected 11 tool calls in turn 1 from a 4-tool palette.
  G3 PARTIAL — code-side O-R-A strong (conflict detection + remediation computation); model-side
               revealed the propagation gap. Design lesson, not gate failure.
  G4 PASS — cap fired cleanly with labelled exit reason. Execution succeeded; goal didn't.
  G5 N/A — independent verifier first appears at rung 7.

## Cycle 3 — Recipe Companion (closed reference)

  Slug: recipe-companion · Domain: health-habits (food/cooking) · Rung: 4 · Closed: 2026-06-11
  See registry agents[] entry for full detail.

## Cycle 2 — Study Buddy (closed reference)

  Slug: study-buddy · Closed 2026-06-08 · model_done run · ~$0.64 / 18K tokens
  Key win: Ram surfaced soft-stop wrapped in hard-stops on Probe 1.

## Cycle 1 — Study Prep (closed reference)

  Slug: study-prep · Closed 2026-06-07 · cap_reached run · 0/3 topics
  Root cause: mock-DB perception trap; agent worked correctly per FR-A3.

## Repo / hygiene state

  Public · MIT-licensed · all hygiene checks green (carry-forward)
  Branches on origin: master only
  Open issues:
    #3  Add CI smoke-test workflow for all agent folders (still open)
    #4  Cycle 2 brainstorm: SDK rung 3 (closeable)
    (closeable) Cycle 3 brainstorm: SDK rung 4 (custom tools)
    (closeable) Cycle 4 brainstorm: SDK rung 5 (permission_mode)
    (closeable) Cycle 5 brainstorm: SDK rung 6 (hooks + JSONL span trace) — was the Cycle 5 target; now Cycle 6 target
    (new) Cycle 6 brainstorm: SDK rung 6 (hooks — skipped in Cycle 5) — ready to open

## Next session — single primary branch

  Ram types "begin the brainstorm" / "new agent" →
     Phase 0 warm-up (mandatory) → Cycle 7 brainstorm
     Target: rung 6 FOUNDATIONAL (Habit Streak + Accountability) or rung 7 if Ram wants to push
     Phase 0 recall question: "Morning Spark's goal predicate had five conditions — all five had
       to be True. In Cycle 7, the agent tracks whether a habit streak was kept or broken. Both
       outcomes are valid completions. How do you write a predicate that returns True on both
       outcomes but also tells the loop which branch fired?"
     Domain: health-habits (first clean health-habits agent; Habit Streak + Accountability locked)
