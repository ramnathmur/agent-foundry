# Morning Spark — Prompt Blueprint
Cycle 6 · SDK Rung 6 · FORWARD · Domain: morning-briefing
Generated: 2026-06-14

---

## What This Agent Does

Morning Spark is a morning briefing agent. It fetches three independent pieces of
morning information — today's weather forecast, today's date and day, and a top news
headline — checks that all three came back with usable content, and synthesises them
into a short morning briefing.

The agent introduces **SDK rung 6: hooks**. Two hook types fire on every tool call:
a `PreToolUse` guard that intercepts before a tool executes (detecting and blocking
repeated identical parameters) and a `PostToolUse` audit that fires after every
successful execution (writing a JSONL span record to `morning-spark_spans.jsonl`).

---

## Agency Gates

| Gate | Verdict | Evidence |
|---|---|---|
| G1 — did-it-finish check | PASS | `briefing_complete(state)` = all 3 sources fetched AND quality_passed AND briefing synthesized |
| G2 — model's own choice | PASS | Model selects tool order and headline category; decides when quality is sufficient |
| G3 — learning from what it saw | PASS | PreToolUse detects repeated params → denies → model adapts category; PostToolUse spans close the audit loop |
| G4 — principled stop | PASS | Cap at MAX_TOOL_CALLS (12) + cap at MAX_LOOP_TURNS (6); both exit paths reachable |
| G5 — independent check | N/A | Rung 7 not yet introduced; annotation at gate block |

---

## Tools (5 — all mocked, no real HTTP calls)

| Tool | Args | What it returns | Side effect |
|---|---|---|---|
| `fetch_weather` | none | Weather forecast string | Sets `_agent_state["weather"]` |
| `fetch_date` | none | Today's date + day string | Sets `_agent_state["date_info"]` |
| `fetch_headline` | `category: str` | Top headline for category | Sets `_agent_state["headline"]` + `["headline_category"]` |
| `check_quality` | none | `{quality_passes, issues}` JSON | Sets `_agent_state["quality_passed"]` + `["quality_issues"]` |
| `synthesize_briefing` | none | `{status, briefing}` JSON | Sets `_agent_state["briefing"]`; writes `briefing_log.json` |

Categories for fetch_headline: general, technology, science, health, world, business

---

## Rung 6 Hooks

### PreToolUse guard — `pre_tool_use_guard(input_data, tool_use_id, context)`
- Fires BEFORE every tool call (registered via `HookMatcher(matcher=None)`)
- Builds call signature: `(tool_name, json.dumps(tool_input, sort_keys=True))`
- If signature already in `_hook_state["calls_made"]`: returns `permissionDecision: deny`
  with reason instructing model to try a different category or move to next step
- Otherwise: appends to `_hook_state["calls_made"]` and returns `{}`

### PostToolUse audit — `post_tool_use_audit(input_data, tool_use_id, context)`
- Fires AFTER every successful tool call (registered via `HookMatcher(matcher=None)`)
- Builds JSONL span: `{timestamp, tool_name, tool_input, result_length, result_preview, tool_use_id}`
- Appends span to `_hook_state["spans"]` and writes line to `morning-spark_spans.jsonl`
- Returns `{}`

---

## Goal Predicate

```python
def briefing_complete() -> bool:
    return (
        _agent_state.get("weather") is not None
        and _agent_state.get("date_info") is not None
        and _agent_state.get("headline") is not None
        and _agent_state.get("quality_passed", False)
        and _agent_state.get("briefing") is not None
    )
```

---

## App Memory — `briefing_log.json`

Written by `synthesize_briefing` tool on goal-met exit. Schema:
```json
{
  "last_run": "ISO timestamp",
  "date": "Monday, June 14, 2026",
  "headline_category": "technology",
  "headline_preview": "first 100 chars of headline",
  "briefing_preview": "first 150 chars of briefing"
}
```

Cross-day guard: system prompt includes yesterday's headline_preview (if log exists).
Model instructed to try a different headline category if today's matches yesterday's topic.

---

## Hook State (module-level, reset per run)

```python
_hook_state: dict = {
    "calls_made": [],    # list of (tool_name, params_json) tuples
    "spans": [],         # accumulated PostToolUse span records
    "denied_count": 0,   # how many times PreToolUse fired a denial
}
```

---

## Agent State (module-level, reset per run)

```python
_agent_state: dict = {
    "weather": None,
    "date_info": None,
    "headline": None,
    "headline_category": None,
    "quality_passed": False,
    "quality_issues": [],
    "briefing": None,
}
```

---

## System Prompt Template

```
You are Morning Spark, a morning briefing agent.

Your goal: produce a complete morning briefing by calling these tools in order:
1. fetch_weather() — get today's weather
2. fetch_date() — get today's date and day
3. fetch_headline(category) — get a top news headline
   Categories: general, technology, science, health, world, business
4. check_quality() — verify all sources are complete
5. synthesize_briefing() — produce the final briefing

If a tool call is denied because you already tried it with those parameters,
use a DIFFERENT category for fetch_headline, or proceed to check_quality if
you already have weather, date, and a headline.

Yesterday's top topic: {yesterday_preview}
If today's headline is similar to yesterday's topic, try a different category.

After synthesize_briefing returns with status "complete", you are done.
```

---

## Constants

| Constant | Value | Purpose |
|---|---|---|
| `MAX_LOOP_TURNS` | 6 | Cap on total agent loop iterations |
| `MAX_TOOL_CALLS` | 12 | Cap on total tool calls across all turns |
| `MODEL_ID` | `claude-opus-4-8` | Model used for all turns |
| `AGENT_SLUG` | `morning-spark` | Folder name and log prefix |
| `AGENT_VERSION` | `v1` | Printed at boot |

---

## Files

| File | Purpose |
|---|---|
| `prompt.md` | This file — self-contained cold-session spec |
| `morning-spark_learning-guide.html` | Part 1 — pre-run learning guide (13 sections) |
| `main.py` | Runnable agent — hooks, loop, runtime output |
| `smoke_test.py` | QA tests — hooks, tools, predicates, both exit paths |
| `requirements.txt` | Pinned packages |
| `.env.example` | Auth notes (no API key) |
| `README.md` | PyCharm run instructions |
| `briefing_log.json` | App memory — created on first goal-met exit |
| `morning-spark_spans.jsonl` | PostToolUse audit trail — appended each run |
| `morning-spark_run_output.log` | Tee log — appended each run |

---

## Auth Notes

Never read, set, or ask for `ANTHROPIC_API_KEY`. Auth is via:
`claude-agent-sdk` → Claude Code CLI → Max plan subscription login.
If key is in environment: strip from child-process env only (never mutate global env).

---

## Rung 6 Teaching Points

1. **The interception window**: there is a moment BEFORE a tool executes and a moment
   AFTER. PreToolUse is the last point at which you can change what the tool receives
   (or prevent it from running at all). PostToolUse is the first point at which you know
   what actually happened.

2. **Act-strategy adaptation**: when the PreToolUse guard denies a repeated call, the model
   sees the denial reason and must choose a different approach. This is the Cycle 5 gap
   (research-lead follow-ups hit same source) implemented in code — the hook enforces
   strategy change at the execution boundary, not just at the dispatch level.

3. **JSONL audit trail**: each PostToolUse span records tool_name, params, result length,
   and a preview — a structured, machine-readable audit log of exactly what the agent did
   and in what order. This is the foundation for debugging, cost tracking, and compliance.

4. **Hook state scope**: hooks fire in the SDK's execution path, not in our Python loop.
   State shared between hooks and the main loop MUST live at module level. Local variables
   inside hook functions are invisible to the loop.
