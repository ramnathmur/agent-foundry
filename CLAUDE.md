# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Purpose

Ram gives an agent use case. This project turns it into runnable Python code for PyCharm.
The objective is **practical, code-level understanding of agents in action** — every file is a
teaching artifact, not just working software.

**Claude Desktop is the Foundry** (PRD D5). There is no Foundry software. All brainstorming,
gating, code generation, and QA happen in this chat. PyCharm is exclusively where Ram reads
and runs generated agents.

## Commands

```bash
# Run a generated agent's smoke test (from the agent's folder)
python smoke_test.py

# Verify current package version before pinning
pip index versions claude-agent-sdk

# Check CLI login status (required for preflight)
claude --version
claude auth status

# Run the main agent (PyCharm: right-click → Run, or)
python main.py
```

## Operating Cycle (one cycle per "new agent")

**Session start — read these files before doing anything:**
`HANDOFF.md` → `INSIGHTS.md` → `foundry_registry.json` (agents + brainstorm_sessions + preferences) → `ROADMAP.md`

0. **Session Warm-Up** (Phase 0 — skippable on cycle 1; mandatory cycle 2+) — after reading the
   session state files, before the brainstorm begins: deliver the two-part Professor warm-up.
   Ram may bypass at any time with "skip warm-up." Full spec in PRD.md FR-F6.
   **Part A — Brief (target 2–3 min, one-way):** (1) report card drawn from `report_card`
   object in registry (agents built, rungs introduced, domains, gates ever demonstrated),
   (2) complexity arc — one sentence per prior cycle, (3) top 2 active gaps from latest
   agent's `learning.gaps[]`, (4) gotchas mastered — plain-English summary from
   `gotchas_mastered[]` in the registry, (5) forward seed — next SDK rung and what it unlocks.
   **Part B — Interrogation (target 3–5 min, Socratic dialogue):** 2–3 recall questions drawn
   from `recall_question_next_cycle`, `learning.gaps[]`, and a specific runtime output line
   from `post_run_notes` (if present). One question at a time; wait for Ram's answer before
   proceeding. On a partial answer, give one counter-question anchored to a specific code line
   or output line; then give the explanation. End Phase 0 with a forward-looking sentence
   connecting what was recalled to what the upcoming brainstorm will explore.
   **Rules:** Never score or grade. Never ask more than 3 questions in Part B. Total ≤ 8 min.
   Draw all recall questions only from registry artifacts — never from generic agent knowledge.

1. **Brainstorm** — adaptive Q&A (daily-life scope), 9-trait scorecard + G1–G5 gate verdict
   per candidate. For every candidate, compute and display its **Learning Position** label
   before the gate verdict:
   - `FORWARD` — introduces ≥1 SDK rung not in any prior agent OR ≥1 trait/gate not yet
     exercised. The default recommendation. Always surface at least one FORWARD candidate.
   - `LATERAL-RIGHT` — same SDK rungs as all prior agents; new domain. Breadth run.
   - `LATERAL-LEFT` — same rungs; same or similar domain. Consolidation run.
   - `FOUNDATIONAL` — targets a concept in the latest agent's `learning.gaps[]`. Repair run.
     Overrides LATERAL-LEFT when gaps exist.
   - `DIAGNOSTIC` — deliberately fails G1 or G3; offered every 2–3 cycles so the student
     practises gate-rejection. Present it last; label it clearly as a workflow on purpose.
     **State the specific failure mode (which gate fails and why) before Ram locks.**
     When a DIAGNOSTIC candidate is locked, also generate `<slug>_workflow_to_agent.md`
     showing the minimal diff (≤5 lines) that would promote it to a true agent.
   **Classification algorithm** (derive from registry):
   1. Compute `prior_rungs` = union of `sdk_concepts_introduced` across all `agents[]`
   2. Compute `prior_domains` from all locked candidates in `brainstorm_sessions[]`
   3. Compute `current_gaps` from latest agent's `learning.gaps[]`
   4. For each candidate: FORWARD if new rung; FOUNDATIONAL if gap-targeted; else
      LATERAL-RIGHT (new domain) or LATERAL-LEFT (known domain)
   5. **Diversity check** — compute structural similarity:
      `score = (domain_overlap × 0.4) + (rung_overlap_fraction × 0.4) + (trait_overlap × 0.2)`
      If score > 0.7 and not FORWARD → add flag `(HIGH SIMILARITY — mostly review)`
   **Student-facing label** — one sentence per candidate, e.g.:
   - FORWARD: "This introduces custom tools (SDK rung 4) — your learning frontier."
   - LATERAL-RIGHT: "Same concepts as [agent-name], new domain — breadth run."
   - FOUNDATIONAL: "Revisits [gap concept] flagged in your last Professor session."
   - DIAGNOSTIC: "Deliberately fails G3 — your job is to catch it using the gate criteria."
   Present in order: FORWARD → FOUNDATIONAL → LATERAL-RIGHT → LATERAL-LEFT → DIAGNOSTIC.
   Ram locks freely regardless of position label. Check `brainstorm_sessions` to avoid
   repeating rejected/deferred ideas. Check `INSIGHTS.md` § Recommended focus to seed
   domain and trait choices. When FORWARD is available, name the specific SDK rung it
   unlocks and what that enables in future agents.
2. **Log brainstorm** — append to `foundry_registry.json` → `brainstorm_sessions[]`
   immediately after brainstorm (candidates, gate verdicts, decisions, reasons). Do this
   whether or not a lock happens that session.
3. **Lock gate** — Ram types an explicit lock (`lock <candidate>`). **Zero file writes before this.**
   Show a one-page mini-spec and get a second confirmation.
3.5 **Write `prompt.md`** into `agents/<use-case-slug>/` — the blueprint file. Must be complete
   enough that a cold Claude session can regenerate the Python agent from it alone. Write
   this before any `.py` file. Ram may read and approve it before code generation begins.
   **Then generate `<agent-slug>_learning-guide.html` (Part 1) before writing `main.py`.**
   Do not write or share `main.py` until Part 1 HTML is complete and Ram confirms he has
   opened it. Part 1 is the pre-code reading artifact; delivering code first inverts the
   learning contract.
4. **Generate** remaining five files into `agents/<use-case-slug>/` and QA-test before delivery
   (see QA Feedback Loop below). Narrate each repair in chat.
5. **Professor session** (Phase F, skippable) — immediately after green: ~10-min four-part
   conversation (opening/core/probe/handoff). Every probe must anchor to a real briefing
   section or code line.
6. **Update registry** — write structured `learning` object to the agent's registry entry
   (probes_asked, gaps, strengths, recall_question_next_cycle).
7. **Regenerate `INSIGHTS.md`** — rewrite all six sections from current registry state.
   §6 (Recommended focus) must follow the **5-cycle synthesis arc template in PRD.md FR-E4**
   — do not write it as free-form prose. The template provides the synthesis statement,
   cross-agent link, and opening recall question for each cycle number.
8. **Update** `ROADMAP.md`, `HANDOFF.md`, and registry cross-cycle fields:
   - Append this agent's `GOTCHA[]` annotations (plain English, one bullet each) to
     `gotchas_mastered[]` at the top level of `foundry_registry.json`. Never duplicate
     an entry already present — check for an exact or near-exact match before appending.
   - Regenerate `report_card` object from the full `agents[]` array:
     `{agents_understood[], sdk_rungs_introduced[], gate_verdicts_summary,
     domain_coverage[], top_active_gaps[]}`. Overwrite the previous value.
8.5 **Phase F2 — post-run Professor session** (skippable) — triggered by Ram saying "I ran it"
   or equivalent after running `main.py` in PyCharm. Purpose: reinforce agentic concepts
   anchored to actual runtime output lines (not code alone). Ask 3–5 probes drawn from:
   - `[GOAL PREDICATE]` line → probe G1 understanding
   - `[MODEL DECISION]` line → probe G2 ownership
   - `[LOOP FEEDBACK]` delta → probe G3 O→R→A cycle
   - `[ERROR: ...]` classification (if any) → probe LO-12 failure taxonomy
   - `[PLAN REVISED]` or `[PLAN PROGRESS]` → probe autonomy / plan mutability
   - `[SDK →]` / `[← SDK]` brackets → probe LLM boundary visibility
   - Usage summary line → probe subscription billing / credit awareness
   Update `learning.post_run_notes` in the registry after Phase F2:
   `runtime_surprises[]` (what surprised Ram in the output), `post_run_probes_asked[]`,
   `next_cycle_expectation` (what Ram predicts the next rung will unlock).
   If Ram skips Phase F2, record `post_run_notes: {skipped: true}` in the registry.
   **Edge case:** if both Phase F (pre-run Professor session) and Phase F2 are skipped and no
   `learning` object has been written yet, trigger `INSIGHTS.md` regeneration from this step
   rather than waiting for a future cycle to write learning records.

## Hard Requirements (every deliverable)

1. **Runs in PyCharm on Windows** with Python 3.12+. No notebook-only code.
2. **Claude Max plan auth, never an API key.** LLM calls go through `claude-agent-sdk` → Claude
   Code CLI → subscription login. Never read, set, or ask for `ANTHROPIC_API_KEY`. If it is set
   in the environment, warn and strip it **from the child-process environment only** (never mutate
   global env).
3. **Agentic traits explicitly annotated** — see annotation standard below.
4. **QA feedback loop built in** — see below; smoke test must be green before delivery.
5. **Latest, non-deprecated packages only** — see Package Policy.
6. **Per-run usage summary** printed at exit (`usage`, `total_cost_usd` when present). From
   2026-06-15, Agent SDK usage on subscriptions draws from a monthly Agent SDK credit.
7. **`MessageLens` helper** in every agent — one-line console rendering of each SDK message so the
   agent loop is watchable in every run. Prefix all `MessageLens` output lines with `  ┆` (two
   spaces + thin vertical bar) so they are visually indented and clearly secondary to the primary
   emoji-labeled output stream.
8. **Log tee — `main.py` mirrors all stdout to `<agent-slug>_run_output.log`** in the agent
   folder using a `tee_to_log()` context manager. This file is the primary input for generating
   `<agent-slug>_learning-insights.html` (Part 2). Never overwrite — always append with a
   run-separator header. Fallback if log is absent: user pastes terminal output directly.

## Acceptance Gates & Learning Spec

`AGENT_LEARNING_AND_AGENCY_GATES.md` is the binding acceptance spec. Read it before building.

**Agency Gates (G1–G5) — all three Core gates must pass, or the artifact is a workflow:**

| Gate | Pass criterion |
|---|---|
| G1 — Goal is a predicate | `goal_met(state) -> bool` called in code; verdict computed, not narrated |
| G2 — Model owns a real decision | At least one branch chosen by the model at run-time, visible in message log |
| G3 — Closed observe→reason→act loop | Agent reads a tool result and a *subsequent* action demonstrably differs |
| G4 — Principled termination *(required)* | Goal-predicate exit **and** hard cap/budget/timeout; both paths reachable |
| G5 — Verification is independent *(required)* | Pass/fail from a deterministic predicate or separate critic call, fresh context |

Honesty rule: if G1–G3 don't all pass, label the artifact a **workflow** and propose the
minimal agentic fix.

**QA grep contract for every generated `main.py`:** `TRAIT[` ≥ 5, `GATE[` ≥ 5 (G1–G5 each),
`GOTCHA[` ≥ 1.

**G5 annotation when G5 is not applicable** (rungs < 7, no independent verifier in this agent):
write `# GATE[G5]: N/A — independent verifier introduced at rung 7; no critic call in this agent`
at the bottom of the gate-annotation block. This ensures the grep contract `GATE[` ≥ 5 passes
even before rung 7 is reached.

## Runtime Output Standard (FR-C8)

Every generated `main.py` MUST produce this output sequence using `print()` + Unicode box-drawing + emoji. No `rich`, `colorama`, or `logging`.

Elements are ordered by when they fire during a run. **Bold** = core evidence for a specific Agency Gate.

| Element | Emoji + label | Trait/Gate/LO | Fires when |
|---|---|---|---|
| Boot banner | `🤖 [AGENT BOOT]` | Goal-directedness; refuses to start without CLI | Once, after `preflight()` |
| Output guide | `📖 [OUTPUT GUIDE] each labeled line is a teaching element — match to learning-guide.html §6` | All LOs — orients the student before telemetry begins | Once, immediately after `[AGENT BOOT]` |
| Goal set | `🎯 [GOAL SET]` | `GATE[G1]` — goal predicate *declared* | Once, before loop |
| Plan display | `📋 [PLAN GENERATED]` + box list | `TRAIT[planning]` | Once at boot |
| **SDK call open** | `━━━ [SDK →] model · ~N prompt tokens` | All gates — where Python hands off to LLM | Before every `query()` / SDK call |
| Step header | `📍 [STEP N]` | Sequential action | Every iteration |
| Context tracker | `📊 [CONTEXT] ~N tokens in context (~W words) · +M this step` | LO-11 context engineering | Every iteration |
| Memory retrieved | `🧠 [MEMORY RETRIEVED] N findings injected` | `TRAIT[memory]` — session | Every iteration start |
| **Loop feedback** | `🔄 [LOOP FEEDBACK] observed X → changed Y` | **`GATE[G3]`** — what changed because of prior observation | Every iteration after first |
| Tool call | `🔧 [TOOL CALL] name({params})` | `TRAIT[tool-use]` | Every tool dispatch |
| **Model decision** | `🎲 [MODEL DECISION] selected: X · alternatives: Y` | **`GATE[G2]`** — model-owned branch, not Python hard-code | At tool selection |
| Trust fence | `🔒 [TRUST FENCE] source fenced as data` | LO-13 trust boundary | When external content enters prompt |
| Tool result | `📥 [TOOL RESULT] N chars returned` | `TRAIT[perception]` | After every tool call |
| O-R-A triad | `👁 [OBSERVE]` / `🧠 [REASON]` / `⚡ [ACT]` | `GATE[G3]` closed loop | Every iteration |
| **Goal predicate** | `📐 [GOAL PREDICATE] is_goal_met(state) → bool` | **`GATE[G1]`** — predicate *evaluated*, verdict computed | Every iteration |
| Termination check | `🔍 [TERMINATION CHECK] N/M (X%)` | `GATE[G4]` principled termination | End of every step |
| Plan progress | `📋 [PLAN PROGRESS]` ✓/▶/○ live step board | `TRAIT[planning]` as ongoing process | End of every step (all agents, regardless of step count) |
| Session memory | `💾 [SESSION MEMORY] key └─ preview` | `TRAIT[memory]` — **ephemeral**, within-run only | When session state written |
| App memory | `📀 [APP MEMORY] key → file └─ preview` | `TRAIT[memory]` — **persistent**, survives next run | When disk state written |
| Error | `⚠ [ERROR: TRANSIENT/STRUCTURAL/POLICY] → route` | LO-12 failure classification + routing | When tool or SDK error occurs |
| **SDK call close** | `━━━ [← SDK] Ns · +N output tokens` | All gates — where LLM returns to Python | After every `query()` / SDK call |
| Complication | `⚠ [<EVENT> DETECTED]` + `── O/R/A ──` | `GATE[G3]` recalibration | When plan deviates |
| Plan revised | `📝 [PLAN REVISED]` | `TRAIT[autonomy]` + `GOTCHA[control-plane]` | When model mutates plan |
| Exit line | `🏁 [GOAL MET / EXIT: cap / ESCALATED]` | `GATE[G4]` | Loop exit |
| POST-RUN SUMMARY | `╔══ 🧠 AGENT SUMMARY ══╗` | All traits + G1/G2/G3 verdict | Unconditionally at script exit |

**POST-RUN AGENT SUMMARY** covers 7 mandatory items: (1) run narrative, (2) traits-in-action with code-line evidence, (3) every model tool-selection decision (from `[MODEL DECISION]` lines), (4) plan recalibrations and triggers, (5) iteration count + termination reason, (6) memory ledger — session memory keys vs application memory keys kept separate, (7) plain-English G1/G2/G3 verdict pointing to the specific `[GOAL PREDICATE]`, `[MODEL DECISION]`, and `[LOOP FEEDBACK]` lines as runtime proof.

**Structured comment header** — mandatory on every major code block:
```python
# ═══════════════════════════════════════════
# PURPOSE: [one sentence]
# AGENTIC TRAIT: [trait name]
# ACHIEVES: [what the agent can do because of this block]
# DEPENDENCIES: [what must be set up before this block]
# ═══════════════════════════════════════════
```
This coexists with `# TRAIT[]`, `# GATE[]`, `# GOTCHA[]` inline markers — both required.

**QA grep contract addition:** `[AGENT BOOT]` present, `[GOAL SET]` present, `[GOAL PREDICATE]` present, `[MODEL DECISION]` present, `[LOOP FEEDBACK]` present, `[CONTEXT]` present, `[SDK →]` present, `SESSION MEMORY` or `APP MEMORY` present (at least one), `AGENT SUMMARY` present, `═══` header ≥ 5 times — in addition to the existing `TRAIT[` ≥5, `GATE[` ≥5, `GOTCHA[` ≥1.

## Agentic Traits — Annotation Standard

Framework: `reference/agent_traits_chef_guide_v2.html` (9 traits, 3 tiers).

| Tier | Traits |
|---|---|
| **Core** | Goal-directedness, Autonomy, Observe–reason–act loop |
| **Essential** | Perception, Planning & decomposition, Memory, Tool selection & use |
| **Enhancing** | Sequential action-taking, Termination criterion |

Conventions:
- Module docstring: **"AGENTIC TRAITS DEMONSTRATED"** table — trait, where in code, plain-English why.
- Inline: `# TRAIT[autonomy]: ...` at the exact line each trait fires.
- `# GATE[G1]:` through `# GATE[G5]:` at the line satisfying each gate.
- `# GOTCHA[...]:` guard at any line that would have been an annex §5 trap (name the trap avoided).
- Print the control-plane statement (who owns the next decision) in the docstring.
- Print the termination reason on every exit: `GOAL MET` / `EXIT: cap reached` / `ESCALATED`.
- Label session memory vs application memory where each lives.

## QA Feedback Loop — Definition of Done

1. **`preflight()`**: verifies Python version, package imports, `claude` CLI present and logged
   in. Detects `ANTHROPIC_API_KEY` and removes it from child-process environment only. Fails
   fast with a fix-it message.
2. **`smoke_test.py`**: mocks the LLM boundary; exercises the happy path end-to-end; asserts on
   result structure. Every failure/reject/escalate branch must fire at least once under seeded
   fixtures (branch reachability). Goal predicates assert against extracted assistant text only.
3. **Run-before-deliver**: smoke test must exit 0 in Claude's sandbox before handover. Max 3
   repair attempts, each narrated (what failed, what changed, why). Never claim success without
   a green run.
4. **Runtime guards**: retries with backoff on transient errors, timeouts on agent loops,
   max-iteration cap (agent can never spin forever).

## Package Policy

- Verify current versions before writing code: `pip index versions <pkg>` or web search.
- Pin in `requirements.txt` with `>=` floor at the verified-current version.
- Known traps: SDK is `claude-agent-sdk` (NOT deprecated `claude-code-sdk`).
- Default stack: `claude-agent-sdk` + stdlib. Add third-party only when needed; prefer
  `pydantic` v2, `httpx`, `pytest`.

## SDK Concept Ladder

Each new agent must introduce **≥1 SDK concept not used by a prior agent** (tracked in registry).

| Rung | SDK concept |
|---|---|
| 1 | `query()` one-shot + message anatomy (`SystemMessage`, `AssistantMessage`, `ResultMessage`, `usage`) |
| 2 | Goal predicate + agent loop + circuit breaker (G1/G3/G4 in code) |
| 3 | `ClaudeSDKClient` multi-turn + `session_id` capture/resume |
| 4 | Custom tools (`@tool`, `create_sdk_mcp_server`) — model-owned tool choice (G2) |
| 5 | `allowed_tools` / `disallowed_tools` / `permission_mode` (documented modes only) |
| 6 | Hooks: `PreToolUse` guard, `PostToolUse` audit + JSONL span trace |
| 7 | Independent verifier — separate critic call, fresh context, calibrated (G5) |
| 8 | Subagents (own context windows); context compaction |

## `<agent-slug>_learning-guide.html` — 13 Mandatory Sections, Part 1 (FR-C5)

Single self-contained static HTML (inline CSS; vanilla JS for MCQ reveal only; no CDN; offline
double-click). Visual spirit of `agent_traits_chef_guide_v2.html`. Generated **before** the code
runs. Paired with `<agent-slug>_learning-insights.html` (Part 2, generated after the run).
Sections in order:

1. Use case & objective
2. Agent-loop SVG with this agent's actual step names
3. High-level trait summary
4. Trait-to-code map (file/function anchors)
5. Code-block arrangement & guided reading order. **Begin this section with a "Python Reading
   Primer" subsection** (≤10 lines): define 5 concepts the student needs to *recognize* (not
   write) — `def`, `while`/`for`, `if/else`, `print()`, and `async/await` (explained as a black
   box: "think of `await` as 'wait here until the SDK responds'"). This is the only Python
   prerequisite for following the guided reading order.
6. "Run it first" — PyCharm steps + ~10-line annotated expected output
7. Learning insights. **Always include:** (a) one sentence explaining that `query()` calls in
   this agent are stateless — each starts a fresh LLM conversation — and naming what rung 3
   (`session_id`) changes; (b) one sentence noting that `<agent-slug>_run_output.log` accumulates
   every run and will enable cross-cycle comparison in later cycles.
8. Gotchas (≤5, drawn from annex §5, matching the agent's `GOTCHA[...]` lines). **For rung 1–2
   agents, always add a note** that `[PLAN REVISED]` does not fire here because the plan is
   simple and linear, and that students will first see it in cycle 3 when the model encounters
   an unexpected tool result and restructures.
9. Control plane — who owns the next decision (incl. workflow→agent diff when applicable)
10. SDK glossary
11. MCQ self-check (3–5, inline reveal with one-line explanations)
12. Takeaway & ready-gate checklist
13. Provenance footer

≤10-minute read. No code excerpts beyond 10 lines. Boundary rule: README = how to run;
learning-guide = why it's an agent and what to learn (forward-looking); learning-insights = proof
from execution (backward-confirming). No duplication across the three.

## `<agent-slug>_learning-insights.html` — 11 Mandatory Sections, Part 2 (FR-C9)

Single self-contained static HTML (inline CSS; vanilla JS for interactive elements only; no CDN;
offline double-click). Generated **after** the code runs, using `<agent-slug>_run_output.log` as
primary evidence (fallback: user pastes terminal output). Never duplicates Part 1. Sections in order:

1. **Runtime Snapshot Banner** — dashboard card: agent name, run date, iterations, total context
   tokens (from final `[CONTEXT]` line), termination reason, elapsed time
2. **"Why Was This an Agent?"** — G1/G2/G3 proof panel; one quoted output line per gate as
   evidence, one-sentence verdict per gate; most prominent section
3. **Purpose of This Agent** — use case + goal predicate in plain English; sourced from
   `🎯 [GOAL SET]` and AGENT SUMMARY narrative
4. **Traits in Action** — one card per trait that fired: trait name, tier, one quoted output line,
   one-sentence explanation of why that line demonstrates the trait
5. **Life of the Agent** — visual timeline from `🤖 [AGENT BOOT]` to `🏁 [EXIT]`; `[SDK →]`/`[← SDK]`
   brackets shown as visible nodes; loop iterations shown as a repeating arc
6. **Goal Achievement Trace** — `📐 [GOAL PREDICATE]` output from every iteration as a progress
   strip: iteration N → `is_goal_met() → False/True` → condition evaluated
7. **Agent Spectrum Placement** — horizontal scale (Workflow → Simple Agent → Multi-Step Agent →
   Autonomous Agent); "If this were a workflow" contrast callout citing the `[MODEL DECISION]` line
8. **Flashcards** (5–8 flip-on-click): front = term; back = definition anchored to this agent's
   specific runtime behavior, not a generic definition
9. **MCQ Self-Check** (3–5, inline reveal with one-line explanations): mechanism-not-recall; ≥1
   question tests agent/workflow distinction; wrong answers explain why they are wrong
10. **Next Session Brainstorm Seeds** — 3–5 daily-life use-case suggestions; each names the new
    SDK rung or agentic trait it would exercise beyond what this agent introduced
11. **Provenance Footer** — agent slug, run date, SDK rungs introduced, G1–G5 gate verdicts,
    Part 1 companion file name, log source (Option A or B)

## Project Structure

```
agents/                    # ALL generated agents live here
    <use-case-slug>/       # EIGHT mandated files per agent
        prompt.md                              # blueprint — written BEFORE code
        main.py                                # entry point + runtime output standard
        agent.py                               # agent loop / SDK wiring (if main.py > ~150 lines)
        smoke_test.py                          # QA feedback loop (LLM mocked)
        requirements.txt                       # verified-current pins
        README.md                              # how to run in PyCharm (mechanics only)
        <agent-slug>_learning-guide.html       # Part 1: pre-code reading — 13 sections, MCQs
        <agent-slug>_run_output.log            # auto-saved by main.py (tee); input for Part 2
        <agent-slug>_learning-insights.html    # Part 2: post-run reinforcement — 11 sections
reference/                 # chef guide + master guide (self-containment)
reviews/                   # external/persona review artifacts
prompts/                   # reusable prompts that worked
ROADMAP.md                 # index of all use cases built, one line each
HANDOFF.md                 # session continuity — update at end of every cycle
INSIGHTS.md                # learning synthesis — read at session start; regenerated each cycle
foundry_registry.json      # agents[], brainstorm_sessions[], sdk_ladder, preferences
PRD.md                     # governing spec — on file contract, PRD wins
AGENT_LEARNING_AND_AGENCY_GATES.md   # binding acceptance annex
```

**`foundry_registry.json` key schema additions (v8):**
- `brainstorm_sessions[]` — one entry per session: `{date, cycle, candidates[], locked}`
  Each candidate: `{name, domain, gates, decision, notes}`
- `agents[n].learning` — structured Professor record: `{probes_asked[], gaps[],
  strengths[], recall_question_next_cycle}`

Agents are **fully self-contained** (no shared `common/`). Never overwrite an existing agent
folder — version-bump the slug instead (FR-E2).

## Style

- Type hints everywhere. PEP 8.
- Comments explain *why*; trait annotations explain *what's agentic*.
- Lead with truth: if a use case doesn't demonstrate agency, say so and propose the minimal fix.
- Agents non-interactive by default (D12). Opt-in HITL tool only when human-in-the-loop is the
  trait being taught.
- Generated agents may call free public web APIs for perception (D13) — with timeouts, bounded
  retries, and all ingested text fenced as data-not-instructions (LO-13).
