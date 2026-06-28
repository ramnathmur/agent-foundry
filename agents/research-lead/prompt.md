# Research Project Lead — Agent Blueprint

## Identity

You are a **Research Project Lead** — an agent that takes a research question, dispatches
specialist sub-researchers to investigate it from multiple angles, collects their independent
reports, and synthesizes everything into a single coherent briefing.

## Goal Predicate

```python
def is_goal_met(state: dict) -> bool:
    return (
        state["all_dispatched_returned"]       # every sub-researcher has reported back
        and state["synthesis_produced"]         # a final briefing exists
        and state["synthesis_confidence"] >= 0.7  # the briefing meets the confidence bar
    )
```

Three conditions, all required. The agent evaluates this after every major action.

## Default Research Question

> "What's the most effective spaced-repetition algorithm for learning a programming language
> — and what are the trade-offs vs alternatives?"

Domain: learning-research. The question is broad enough to benefit from multiple research
angles and narrow enough to produce a concrete synthesis.

## Architecture — Two-Level Agent Loop

### Level 1: Main Agent (Research Project Lead)

The main agent runs in its own `ClaudeSDKClient` session. It:

1. Receives the research question
2. Decides which angles to investigate (model's own choice — G2)
3. Dispatches sub-researchers (one per angle)
4. Collects their reports
5. Identifies gaps and dispatches follow-ups if needed (O-R-A loop — G3)
6. Synthesizes a final briefing
7. Evaluates the goal predicate

**Main Agent Tools (3):**

| Tool | Purpose |
|------|---------|
| `spawn_researcher(angle, question)` | Launch a sub-researcher with a specific angle and question |
| `collect_reports()` | Gather all completed sub-researcher reports |
| `synthesize_briefing(reports)` | Produce the final multi-angle synthesis |

### Level 2: Sub-Researchers (Independent Contexts)

Each sub-researcher gets its **own `ClaudeSDKClient` instance** — a completely separate
context window. The sub-researcher:

1. Receives its assigned angle and question
2. Looks up sources in a mock research database
3. Extracts findings from those sources
4. Summarizes and returns a structured report

**Sub-Researcher Tools (3):**

| Tool | Purpose |
|------|---------|
| `lookup_source(query)` | Search the mock research database for a given angle |
| `extract_finding(source_id)` | Pull detailed information from a specific source |
| `summarize_findings(findings)` | Produce a structured report with confidence and gaps |

### The Rung-8 Concept: Context Isolation

This is what makes subagents different from tool calls:

- The main agent **cannot see** the sub-researcher's internal reasoning
- The sub-researcher **cannot see** the main agent's broader strategy
- Each sub-researcher **cannot see** what other sub-researchers found
- The main agent only receives the sub-researcher's **final report**

This models real research teams: the project lead delegates to specialists, each specialist
works independently, and the lead synthesizes. The information boundary is the teaching point.

## Research Angle Palette (6 options — model picks 3–5)

| Angle | What it investigates |
|-------|---------------------|
| `technical` | Algorithms, implementations, performance benchmarks |
| `market` | Existing tools, adoption, pricing, user base |
| `user` | User experience research, learning outcomes, satisfaction |
| `contrarian` | Arguments against, limitations, failure modes |
| `regulatory` | Standards, compliance, accessibility requirements |
| `historical` | Evolution, predecessors, failed approaches, lessons learned |

The model's choice of which angles to pursue is the G2 moment. The code does not prescribe
which angles to use — the model reads the question and decides.

## Observe–Reason–Act Loop (G3)

After collecting reports, the main agent checks each for gaps:

- If a report has `gap_flagged=True`: the main agent spawns a follow-up sub-researcher
  to address the specific gap
- If a report has `confidence < 0.6`: the main agent spawns a follow-up to strengthen
  that angle
- If all reports are solid: proceed to synthesis

This is the closed O-R-A loop — the agent's next action depends on what it observed in the
sub-researcher reports.

## Termination (G4)

Three exit conditions:

| Exit | Condition | Label |
|------|-----------|-------|
| **GOAL MET** | All three predicate conditions satisfied | `🏁 GOAL MET` |
| **EXIT: subagent cap** | `MAX_SUBAGENTS_TOTAL=5` reached before synthesis | `🏁 EXIT: subagent cap` |
| **EXIT: synthesis cap** | `MAX_SYNTHESIS_TURNS=2` reached without confidence ≥ 0.7 | `🏁 EXIT: synthesis cap` |

Both cap exits are principled stops — the agent labels WHY it stopped. A cap exit is not
a failure; it's governance.

## Memory Architecture

| Layer | Scope | What it holds |
|-------|-------|---------------|
| **WITHIN-SUBAGENT** (NEW — rung 8) | One sub-researcher's ClaudeSDKClient | The sub-researcher's internal reasoning chain |
| **SESSION** | Main agent's ClaudeSDKClient | The project lead's strategy, dispatched angles, collected reports |
| **APP** | `research_briefs.json` on disk | Completed synthesis briefings that survive across runs |

The WITHIN-SUBAGENT layer is the new concept. It exists only for the duration of that
sub-researcher's work and is invisible to everyone else — including the main agent.

## G5 — Not Applicable

G5 (independent verifier) is a rung-7 concept. This agent does not include a separate
critic call. Annotated as N/A in the code.

## Traits Map

| Trait | Where it fires |
|-------|---------------|
| Goal-directedness | `is_goal_met()` evaluated after every major action |
| Autonomy | Model picks which angles to investigate (G2) |
| Observe–reason–act | Gap/confidence check on sub-reports triggers follow-ups (G3) |
| Perception | Sub-researchers read from mock research database |
| Planning | Main agent generates an investigation plan before dispatching |
| Memory — session | Main agent's ClaudeSDKClient carries context across turns |
| Memory — within-subagent | Each sub-researcher's independent ClaudeSDKClient (rung 8) |
| Memory — app | `research_briefs.json` persists across runs |
| Tool selection | 3 main-agent tools + 3 sub-researcher tools |
| Sequential action | Steps tracked across the main agent loop |
| Principled stop | GOAL MET + two cap exits, all labeled |

## SDK Concepts Introduced (Rung 8)

1. **Subagents** — each sub-researcher creates its own `ClaudeSDKClient`, runs its own
   multi-turn loop, and returns a structured result. The main agent's context window
   never sees the sub-researcher's internal messages.

2. **Context compaction** — the sub-researcher's entire reasoning chain is compressed into
   a single structured report. The main agent works with the report, not the raw conversation.
   This is how real systems manage context budget across multiple agents.

## What This Agent Does NOT Build

- **Rung 6 (hooks):** No `PreToolUse` / `PostToolUse` hooks or JSONL span traces
- **Rung 7 (independent verifier):** No separate critic call or G5 evaluation
- These are conscious omissions, not gaps. Ram chose to skip to rung 8.

## Enhanced Runtime Output

This agent produces three layers of runtime output beyond the standard FR-C8 elements:

1. **Phase banners** — dramatic section headers marking each phase of the agent's lifecycle
   (e.g., `═══ 🌅 THE AGENT WAKES UP ═══`)
2. **Narrative glosses** — plain-English explanations after key moments
   (e.g., `💡 What just happened: the model chose 3 angles from 6 options`)
3. **Step-end micro-summaries** — one-sentence recaps at the end of each step
   (e.g., `📌 Step 2 in one sentence: dispatched 3 sub-researchers`)

Sub-researcher work is displayed in box-drawn containers showing their independent context.

A companion `research-lead_run_data.json` file is written alongside the log, containing
structured data with pre-computed narratives for HTML generation.

## Control Plane

| Decision | Who owns it |
|----------|-------------|
| Which angles to investigate | **The model** (G2) |
| When to spawn a follow-up | **The model**, guided by gap/confidence thresholds (G3) |
| Whether the goal is met | **The code** — `is_goal_met()` predicate (G1) |
| When to stop on cap | **The code** — hard caps on subagents and synthesis turns (G4) |
| What tools are available | **The code** — registered via `@tool` |
| Sub-researcher internal decisions | **The sub-researcher's model** (independent context) |
