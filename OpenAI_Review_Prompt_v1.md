# Wrapper prompt for OpenAI / ChatGPT — PRD review
# Paste everything below this line into ChatGPT (enable web browsing).

<role>
You are a senior product reviewer and AI-engineering educator. You are reviewing a PRD written by another AI assistant (Claude) for a personal learning project. Bring an independent, critical perspective.
</role>

<context>
The project owner is a senior consultant (15 yrs financial services) going deeper technically into AI agents. The project, "Agent Foundry," is a learning exercise: a Python console application that, on each run, (1) brainstorms daily-life agent ideas with the owner interactively, (2) locks one candidate with explicit approval, (3) generates that agent's complete Python code into a project subfolder, and (4) QA-tests its own generated code and repairs it until the smoke test passes. All code runs locally in the PyCharm IDE on Windows, Python 3.12+. LLM access is exclusively through the Claude Agent SDK (`claude-agent-sdk` Python package), authenticated via a Claude Max subscription through the Claude Code CLI login — never an API key. Generated code must verify it runs (preflight checks, smoke tests) and must use current, non-deprecated library versions. Every file must neatly annotate which agentic traits it demonstrates (goal-directedness, perception, planning, memory, tool use, sequential actions, autonomy, observe–reason–act feedback loop, termination criterion) and how they come together. The PRD was developed through an interrogative brainstorm: the owner answered structured questions on domain, inputs, focus trait, and build size; candidates were scored against a 9-trait framework; web research added sections on non-goals, failure modes, approval gates, audit trails, and measurable success criteria. The full PRD is pasted below.

--- BEGIN PRD.md ---

# PRD — Agent Foundry v1

**Status:** DRAFT — awaiting Ram's lock
**Date:** 2026-06-07
**Owner:** Ram | **Author:** Claude (brainstormed interrogatively with Ram)

## 1. Overview & Learning Objectives

Agent Foundry is a console application, run from PyCharm, that builds agents through
conversation. Each invocation: it brainstorms a daily-life agent candidate with Ram
(Claude-driven, adaptive questioning), scores the candidate against the 9-trait framework,
gates it through the 5-question classifier, and — after Ram explicitly locks it — generates
that agent's complete Python code into a new subfolder, then tests and repairs its own
output until the generated smoke test passes.

Why this product: the Foundry is itself the first teaching artifact. It demonstrates
every agentic trait while manufacturing further agents that each demonstrate the traits
again. One codebase, two layers of learning.

Learning objectives (in priority order):
1. Watch the observe–reason–act feedback loop fire for real (Ram's chosen focus trait):
   the Foundry runs generated code, reads failures, and regenerates.
2. Understand SDK wiring: how `claude-agent-sdk` drives an adaptive dialogue and code generation.
3. Internalize the 9-trait framework by seeing it used as a gate, not a poster.

## 2. The Trait Framework (evaluation lens)

Source: agent_traits_chef_guide_v2.html (chef-in-a-kitchen guide). Nine traits, three tiers:

| # | Trait | Tier |
|---|-------|------|
| 1 | Goal-directedness | Core |
| 2 | Perception | Essential |
| 3 | Planning & decomposition | Essential |
| 4 | Memory | Essential |
| 5 | Tool selection & use | Essential |
| 6 | Sequential action-taking | Enhancing |
| 7 | Autonomy | Core |
| 8 | Observe–reason–act loop | Core |
| 9 | Termination criterion | Enhancing |

Rules adopted from the guide:
- A candidate missing any Core trait is a workflow, not an agent → Foundry must say so
  and propose the minimal change that makes it agentic.
- The guide's 5-question classifier is the go/no-go gate before any code generation.
  Minimum to proceed: all 3 Core traits present.
- This 9-trait/3-tier framework supersedes the 7-trait list in CLAUDE.md for scoring.

## 3. Trait Coverage Matrix — the Foundry itself

| Trait | Where it lives in the Foundry |
|-------|-------------------------------|
| Goal-directedness | Session goal: "one locked candidate turned into green-tested code" |
| Perception | Reads project folder (existing agents, registry), reads Ram's answers |
| Planning | Claude plans next brainstorm question from answers so far; plans code-gen steps |
| Memory | foundry_registry.json — agents already built, topics covered, Ram's preferences |
| Tool selection | Chooses among: ask-Ram, call-Claude, write-files, run-smoke-test |
| Sequential actions | brainstorm → score → lock → generate → test → repair → register |
| Autonomy | Decides its own next question and repair strategy; Ram only sets the goal and locks |
| Feedback loop | Centerpiece: runs generated smoke_test.py, parses failures, regenerates (≤3) |
| Termination | Green test, or 3 failed repair attempts (honest failure report), or Ram quits |

## 4. User Stories

1. As Ram, I run main.py in PyCharm and am interviewed — short, adaptive questions —
   until a shortlist of daily-life agent candidates emerges with trait scores.
2. As Ram, I see an honest classifier verdict per candidate and must type an explicit
   lock before any code is written.
3. As Ram, I watch the Foundry generate, test, and repair the agent code, with each
   feedback-loop iteration narrated.
4. As Ram, I open the generated subfolder in PyCharm and run the new agent immediately.
5. As Ram, on the next invocation the Foundry remembers what was already built.

## 5. Functional Requirements

Phase A — Brainstorm (Claude-driven, adaptive):
- FR-A1: Console Q&A; Claude decides each next question from answers so far (not a fixed tree).
- FR-A2: Scope anchor: daily-life agents, not corporate. Foundry proposes; Ram disposes.
- FR-A3: Each candidate presented with a 9-trait scorecard and classifier verdict.
- FR-A4: Honesty rule: workflows must be called workflows, with the minimal agentic fix proposed.

Phase B — Lock gate (human approval):
- FR-B1: Explicit typed confirmation required; nothing written before it.
- FR-B2: On lock, Foundry writes a one-page mini-spec and shows it for second confirmation.

Phase C — Code generation:
- FR-C1: Generate into /<use-case-slug>/ per CLAUDE.md: main.py, smoke_test.py,
  requirements.txt, README.md (+ agent.py if main exceeds ~150 lines).
- FR-C2: Generated code carries the AGENTIC TRAITS docstring table and inline
  TRAIT[...] markers, Feynman-ordered explanations.
- FR-C3: Generated agents authenticate exactly like the Foundry (subscription, never API key).

Phase D — QA feedback loop (auto-fix until green):
- FR-D1: Run generated smoke_test.py via subprocess; capture stdout/stderr.
- FR-D2: On failure, send code + error to Claude with repair instructions; rewrite; rerun.
- FR-D3: Max 3 repair attempts; then an honest failure report. Never claim success
  without a green run.
- FR-D4: Narrate each loop iteration to the console — this is the teaching moment.

Phase E — Registry & bookkeeping:
- FR-E1: Append to foundry_registry.json and ROADMAP.md per generated agent.
- FR-E2: Never overwrite an existing agent folder without explicit confirmation.

## 6. Non-Goals

- NOT a web app, no GUI in v1 (CLI only).
- NOT multi-user; single user (Ram), single machine, Windows + PyCharm.
- NOT corporate/enterprise agents; daily-life learning scope only.
- NOT using ANTHROPIC_API_KEY, LangChain, CrewAI, AutoGen, or any agent framework —
  claude-agent-sdk + stdlib is the point.
- NOT generating agents that act outside their own subfolder, send email/messages,
  spend money, or run unattended on a schedule.
- NOT optimizing for token efficiency or speed; optimizing for legibility of agency.
- Generated agents do NOT pause for typed user input mid-run.

## 7. Tech Stack & Auth

| Concern | Decision |
|---|---|
| Python | 3.12+ (PyCharm-configured interpreter) |
| LLM access | claude-agent-sdk → local Claude Code CLI → Max plan subscription login |
| API key policy | Never. If ANTHROPIC_API_KEY is set, warn and unset for the process |
| Usage note | From 2026-06-15, Agent SDK usage on subscriptions draws from the monthly Agent SDK credit |
| Third-party | pytest, httpx (only if needed), pydantic v2. Verify current versions at build time |
| Data | foundry_registry.json (memory), generated folders (output) |

## 8. Guardrails & Failure Modes

| Failure mode | Detection | Response | Recovery |
|---|---|---|---|
| Claude CLI not installed/logged in | preflight() at startup | Fix-it message | Ram logs in, reruns |
| LLM call timeout/transient error | Timeout + exception | Retry with backoff (max 2) | Honest abort |
| Generated code fails smoke test | Subprocess exit code | Repair loop (≤3) | Failure report |
| Repair loop oscillation | Attempt counter | Hard stop at 3 | Registry marks FAILED |
| Runaway loop in generated code | Mandated iteration caps + timeouts | Self-terminates | Documented in README |
| Foundry writes outside project | Path validation before every write | Refuse + log | Prevented |
| Kill switch | Ctrl+C anywhere | Clean exit, atomic registry writes | Rerun resumes fresh |

## 9. Human Approval Gates

1. Lock gate — no code generation before typed lock.
2. Overwrite gate — no destruction of prior work, ever.
3. Phase verification — after each generated agent, Foundry prints what to check manually.

## 10. Evaluation & Success Criteria

- S1: Locked candidate has ≥3/3 Core traits and classifier verdict ≥ borderline-agentic.
- S2: Generated folder contains all four mandated files with trait annotations present
  (greppable: TRAIT[ appears ≥5 times in main.py).
- S3: Generated smoke_test.py exits 0 in the Foundry's QA loop.
- S4: Registry and ROADMAP.md updated; rerun shows the new agent in memory.
- S5 (learning): Ram can point to the exact line where each Core trait fires.

## 11. Audit Trail

Every session appends to foundry_sessions.log: timestamp, questions asked, candidate
locked, generation attempts, test outcomes, files written. Human-readable.

## 12. Build Roadmap

| Phase | Deliverable | Testable outcome |
|---|---|---|
| 1 | Skeleton + preflight() + registry read/write | Runs in PyCharm, fails fast without CLI |
| 2 | Claude-driven brainstorm loop + trait scorecard | Mock-LLM test produces a scored shortlist |
| 3 | Lock gate + mini-spec | No file writes occur pre-lock |
| 4 | Code generation into subfolder | Generated files exist, parse, import |
| 5 | QA feedback loop (run→diagnose→repair≤3) | Seeded-bug fixture gets repaired to green |
| 6 | Registry/ROADMAP bookkeeping + session log | Re-invocation perceives prior state |

## 13. Open Items

- Foundry's own slug: agent-foundry/ (proposed).
- Shared common/ helper vs fully self-contained generated agents. Proposed: self-contained.

--- END PRD.md ---
</context>

<goal>
Evaluate whether this PRD makes sense for its stated learning objective, and recommend additional features that would reinforce practical, code-level understanding of the Claude Agent SDK. Perform web research before answering: investigate current Claude Agent SDK capabilities (subagents, hooks, custom tools, MCP, sessions/memory), common agent-design pedagogy, and comparable learning projects, then judge whether this PRD captures all requirements such a learning objective demands.
</goal>

<constraints>
Always treat the Claude Agent SDK as the fixed technology choice — never recommend switching to the OpenAI SDK, Assistants API, LangChain, or any other framework; recommendations must work within claude-agent-sdk + Python stdlib. Always distinguish clearly between flaws (the PRD is wrong or self-contradictory), gaps (missing for the learning objective), and enhancements (nice-to-have features). Always tie every recommended feature to the specific agentic trait or SDK concept it teaches. Always state when web research contradicts an assumption in the PRD, citing the source. Never pad the review with praise; be direct and specific.
</constraints>

<output_format>
Produce six sections:
1. Verdict — does this PRD make sense for the learning objective? (3–5 sentences)
2. Flaws — numbered list, each with PRD section reference and suggested fix
3. Gaps — requirements missing for the stated learning objective, each with rationale
4. Recommended additional features — table: Feature | Agentic trait / SDK concept it teaches | Effort (S/M/L) | Priority
5. Web-research findings — what current sources say about Claude Agent SDK capabilities relevant to this project, with links
6. Top 3 actions — the three highest-leverage changes to make before building
</output_format>

<examples>
Example of a well-formed feature recommendation (row in section 4):
"Add a --replay flag that re-runs a logged session step-by-step | Teaches observe–reason–act loop inspection and SDK message streaming | M | High — turns the audit log into an interactive teaching tool"
</examples>

<tone>
Direct, technically precise, collegial peer-review register. Truth over politeness. Define any jargon the first time it is used.
</tone>
