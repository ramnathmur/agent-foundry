# PROJECT.md — Agent Foundry

**Machine-readable project manifest.** This file is written for AI sessions, automated tools,
and any non-human process that needs to understand this folder before operating on it.
Last updated: 2026-06-07. Governed by PRD v9.

---

## What This Project Does

Agent Foundry is a personal learning system for building practical, code-level understanding
of AI agents. Each session (one "cycle") takes one brainstormed daily-life idea and turns it
into a fully annotated, runnable Python agent. The student (Ram) does not write code — he
reads, runs, and explains it. The code IS the curriculum.

**The operating model in one sentence:** Claude Desktop is the teacher and code generator;
PyCharm is where the student runs generated agents; no other application exists.

**What makes an output an "agent" (not a workflow):** Five Agency Gates (G1–G5) must pass.
G1–G3 are mandatory — if any fail, the artifact is labeled a workflow and a fix is proposed.
The gates are defined in `AGENT_LEARNING_AND_AGENCY_GATES.md`.

---

## Inputs

| Input | Source | When |
|---|---|---|
| A daily-life use-case idea | Ram, in the brainstorm conversation | Every cycle |
| Session state | `HANDOFF.md`, `INSIGHTS.md`, `foundry_registry.json`, `ROADMAP.md` | Every session start |
| Student answers to Professor probes | Ram, in Phase F and Phase F2 conversations | After code delivery and after runtime |
| Runtime log | `agents/<slug>/<slug>_run_output.log` | After Ram runs `main.py` in PyCharm |

**Claude reads these four files at every session start, in this order:**
`HANDOFF.md` → `INSIGHTS.md` → `foundry_registry.json` → `ROADMAP.md`

---

## Outputs

### Per cycle (8 mandated files written into `agents/<use-case-slug>/`)

| File | Purpose | When generated |
|---|---|---|
| `prompt.md` | Blueprint — self-contained spec to regenerate the agent in a cold session | Before any Python code |
| `main.py` | Runnable agent — 24-element annotated runtime output; entry point for PyCharm | After Part 1 HTML confirmed open |
| `agent.py` | Agent loop / SDK wiring (only if main.py > ~150 lines) | With main.py |
| `smoke_test.py` | QA tests with mocked LLM; must exit 0 before handover | With main.py |
| `requirements.txt` | Pinned, verified-current packages | With main.py |
| `README.md` | PyCharm run instructions only (mechanics, no concepts) | With main.py |
| `<slug>_learning-guide.html` | Part 1 — pre-run reading artifact; 13 sections, MCQs, SVG loop diagram | Before main.py |
| `<slug>_run_output.log` | Auto-saved runtime log via `tee_to_log()` context manager; input for Part 2 | On first run in PyCharm |
| `<slug>_learning-insights.html` | Part 2 — post-run reinforcement; 11 sections; proof of agency from runtime log | After first run |

### Per cycle (project-level files updated)

| File | What changes | When |
|---|---|---|
| `foundry_registry.json` | New agent entry appended; `gotchas_mastered[]` updated; `report_card` regenerated | End of cycle |
| `INSIGHTS.md` | Fully regenerated — 6 sections including 5-cycle synthesis arc for §6 | End of cycle |
| `ROADMAP.md` | One line appended for the new agent | End of cycle |
| `HANDOFF.md` | Full rewrite — session state, what changed, next steps | End of cycle |

---

## File Map — Every File in This Folder

### Spec and operating files (read by Claude at every session)

| File | Role | Mutated? |
|---|---|---|
| `CLAUDE.md` | Operating guide for Claude — the full cycle procedure, all hard requirements, annotation standards, QA contract. **This is the session instruction set.** | Only when spec changes |
| `PRD.md` | Governing product spec (v9). On any conflict between PRD and CLAUDE.md, PRD wins. Defines all functional requirements FR-A through FR-F. | Only when spec changes |
| `AGENT_LEARNING_AND_AGENCY_GATES.md` | Binding acceptance annex — defines the 5 Agency Gates (G1–G5) and the 9-trait framework. Claude reads this before building any agent. | Frozen (reference) |
| `HANDOFF.md` | Session continuity. Rewritten every cycle. A cold Claude session can orient itself from this file + PRD alone. | Every cycle |
| `INSIGHTS.md` | Learning synthesis — 6 sections. Regenerated every cycle from registry state. Contains the 5-cycle arc for §6. | Every cycle |
| `ROADMAP.md` | One-line index of all agents built. Appended each cycle. | Every cycle |
| `foundry_registry.json` | Structured learning record — all agents, brainstorm sessions, SDK ladder state, preferences, cross-cycle gotchas and report card. The memory system. | Every cycle |
| `PROJECT.md` | This file. Machine-readable project manifest. | When project structure changes |
| `AgentFoundry_Project-Overview_v1.html` | Human-readable project overview for distribution or external publication. Self-contained HTML (no CDN). | When generated |

### Reference files (read-only, never modified by the cycle)

| File | Contents |
|---|---|
| `reference/agent_traits_chef_guide_v2.html` | The 9-trait, 3-tier agentic framework. Primary teaching reference. Self-contained HTML. |
| `reference/Master-Guide-to-Create-Learning-Applications_v3.md` | Learning application design guide. Source for Professor persona and HTML artifact patterns. |

### Generated agent folders (`agents/<use-case-slug>/`)

Each folder contains the 8 mandated files listed above. Folders are never overwritten —
if a re-build is needed, the slug is version-bumped (e.g., `morning-spark-v2`).

### Empty placeholder folders (will be populated as the project grows)

| Folder | Purpose |
|---|---|
| `prompts/` | Reusable prompts that worked well across cycles |
| `reviews/` | External or persona review artifacts |

---

## Key Data Structures

### `foundry_registry.json` top-level shape

```json
{
  "project": "Agent Foundry",
  "prd_version": "v9",
  "preferences": { "domains": [], "focus_trait": "", "build_size": "" },
  "sdk_ladder": { "1_query_message_anatomy": "not_started | introduced | internalized", ... },
  "gotchas_mastered": ["plain English description of GOTCHA[] trap 1", ...],
  "report_card": {
    "agents_understood": ["slug1"],
    "sdk_rungs_introduced": [1, 2],
    "gate_verdicts_summary": { "G1": "demonstrated", ... },
    "domain_coverage": { "morning-briefing": 1 },
    "top_active_gaps": ["gap 1 (cycle N)"]
  },
  "agents": [ { ...per-agent record... } ],
  "brainstorm_sessions": [ { ...per-session record... } ]
}
```

### Per-agent record in `agents[]`

```json
{
  "slug": "morning-spark",
  "date": "2026-06-07",
  "domain": "morning-briefing",
  "traits_demonstrated": ["goal-directedness", "observe-reason-act", "tool-use"],
  "gates_passed": ["G1", "G2", "G3", "G4"],
  "sdk_concepts_introduced": [1, 2],
  "status": "delivered",
  "learning_position": "FORWARD",
  "learning": {
    "probes_asked": ["..."],
    "gaps": ["stateless vs. stateful query()"],
    "strengths": ["goal predicate definition"],
    "recall_question_next_cycle": "Why does session_id matter if query() already returns a response?"
  },
  "post_run_notes": {
    "runtime_surprises": ["80 lines before the brief appeared"],
    "post_run_probes_asked": ["..."],
    "next_cycle_expectation": "rung 3 will let the model remember across calls",
    "skipped": false
  }
}
```

---

## Session Trigger Phrases

A new Claude Desktop session should recognize these phrases and act accordingly:

| Phrase | Action |
|---|---|
| `"begin the brainstorm"` or `"new agent"` | Read session state → Phase 0 warm-up → routing question → brainstorm |
| `"lock <candidate name>"` | Lock the named brainstorm candidate; go to mini-spec + confirmation |
| `"I ran it"` | Trigger Phase F2 (post-run Professor session) |
| `"skip warm-up"` | Bypass Phase 0 and go directly to the routing question |
| `"skip professor"` or `"done"` | End Phase F or F2 immediately |
| `"Others: <description>"` | Stop current Q&A or Phase 0 Part B; treat description as the candidate spec; run silent gate check; proceed to mini-spec |
| `"Others: <absolute file path>"` | Stop current Q&A or Phase 0 Part B; read the file; extract candidate intent; run silent gate check; proceed to mini-spec |

---

## Hard Constraints (always enforce)

- **Never read, set, or ask for `ANTHROPIC_API_KEY`.** Auth is via Claude Code CLI + Max plan subscription. If the key is in the environment, warn and strip it from child-process env only — never mutate global env.
- **Zero file writes before Ram types an explicit lock command.** The brainstorm phase is read-only.
- **Part 1 HTML delivered before `main.py`.** Never share the code before the learning guide is confirmed open.
- **Smoke test must exit 0** before any handover. If it does not pass after 3 repair attempts, report honestly — never claim success without a green run.
- **Never overwrite an existing agent folder.** Version-bump the slug instead.
- **PRD wins** on any conflict with CLAUDE.md.
- **No LMS machinery** — no scoring, rubrics, mastery tiers, or student models.

---

## SDK Concept Ladder (current state)

| Rung | Concept | Status |
|---|---|---|
| 1 | `query()` + message anatomy (`SystemMessage`, `AssistantMessage`, `ResultMessage`, `usage`) | not_started |
| 2 | Goal predicate + agent loop + circuit breaker (G1/G3/G4 in code) | not_started |
| 3 | `ClaudeSDKClient` multi-turn + `session_id` capture/resume | not_started |
| 4 | Custom tools (`@tool`) — model-owned tool choice (G2) | not_started |
| 5 | `allowed_tools` / `permission_mode` | not_started |
| 6 | Hooks: `PreToolUse` guard, `PostToolUse` audit + JSONL span trace | not_started |
| 7 | Independent verifier — separate critic call, fresh context (G5) | not_started |
| 8 | Subagents + context compaction | not_started |

*This table reflects the state at project initialization. The canonical source is `sdk_ladder` in `foundry_registry.json`.*

---

## What This Project Is Not

- Not a Python course (Ram reads code, does not write it)
- Not a product for other users (one student, one machine)
- Not a SaaS or course platform
- Not a PyCharm application (Claude Desktop is the Foundry; PyCharm only runs generated agents)
- Not API-key-dependent (Claude Max plan subscription only)
