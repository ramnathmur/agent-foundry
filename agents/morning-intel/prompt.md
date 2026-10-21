# Morning Intel — Agent Blueprint
## Cycle 7 · Rung 8 (LATERAL-RIGHT) · morning-briefing

---

## Purpose

Morning Intel is a morning briefing agent that dispatches three independent specialist
sub-agents — WeatherAnalyst, NewsScanner, CalendarPrep — each in its own context window.
Each specialist gathers data, formats a section, and returns a structured report.
The main agent collects all three reports, runs a quality check, and calls the model
to synthesize a single prioritized morning brief.

The key architectural lesson over research-lead: the three sub-agents are **heterogeneous**.
They have different jobs, different tools, and different expertise. When one fails, the
main agent must reissue to *that specific specialist* with *different parameters* — not
re-dispatch generically. This makes the act-strategy adaptation more explicit.

---

## Goal Predicate

```
briefing_complete(state) -> bool

  state["sections"]["weather"] is not None          # WeatherAnalyst returned
  AND state["sections"]["news"] is not None          # NewsScanner returned
  AND state["sections"]["calendar"] is not None      # CalendarPrep returned
  AND all section quality_score >= MIN_QUALITY (0.6) # no degraded section
  AND state["synthesis_produced"] is True            # final brief written
```

Evaluated every main-loop iteration. Returns True only when all five conditions hold.
The model's statement "I'm done" does not satisfy this predicate.

---

## Sub-Agent Architecture

Each sub-agent is a Python async function that creates its own query() call —
a separate context window, no shared state with the main agent or other sub-agents.

| Sub-agent       | Domain      | Mock data source         | Returns               |
|-----------------|-------------|--------------------------|------------------------|
| WeatherAnalyst  | weather     | MOCK_WEATHER_DATA        | weather section dict   |
| NewsScanner     | news        | MOCK_HEADLINES           | news section dict      |
| CalendarPrep    | calendar    | MOCK_CALENDAR_DATA       | calendar section dict  |

Each sub-agent returns:
```json
{
  "section_type": "weather|news|calendar",
  "content": "2-3 sentence briefing section",
  "quality_score": 0.0-1.0,
  "gap_flag": false,
  "notes": "optional note"
}
```

---

## Main Agent Flow

```
Turn 1  →  Observe: dispatch all 3 sub-agents
           Reason: assess each report's quality_score
           Act: identify any below-threshold sections

Turn 2  →  (if follow-up needed)
           Observe: re-dispatch low-quality section with different params    [G3]
           Reason: re-assess quality
           Act: proceed to synthesis if all OK

Turn 2/3 → Synthesis: query() call — model reads all 3 sections,
           decides which leads (weather urgency vs calendar priority
           vs news significance), writes final briefing                       [G2]

Exit    →  GOAL MET (briefing_complete() = True)
           or EXIT: cap (MAX_MAIN_TURNS or MAX_SUBAGENTS reached)             [G4]
```

---

## Agency Gates

| Gate | Implementation                                                     |
|------|--------------------------------------------------------------------|
| G1   | `briefing_complete()` called every turn — predicate not narration |
| G2   | Model selects lead section in synthesis query() call               |
| G3   | Low quality_score → reissue brief with different params            |
| G4   | MAX_MAIN_TURNS=4 (loop cap) + MAX_SUBAGENTS=6 (dispatch cap)       |
| G5   | N/A — rung 7 not yet introduced                                    |

---

## Memory Design

| Layer     | Where                              | What                                    |
|-----------|------------------------------------|-----------------------------------------|
| SESSION   | main agent's query() context       | carries sub-reports across turns        |
| SUBAGENT  | each sub-agent's query() call      | independent, discarded after return     |
| APP       | morning-intel_briefing_log.json    | yesterday's lead section for context    |

---

## Key Contrast with research-lead (rung 8 learning arc)

| Dimension         | research-lead                    | morning-intel                         |
|-------------------|----------------------------------|---------------------------------------|
| Sub-agent jobs    | Homogeneous (all: research X)    | Heterogeneous (weather / news / cal)  |
| G2 moment         | Pre-dispatch (which angles?)     | Post-collection (which section leads?)|
| Follow-up logic   | Re-dispatch any researcher       | Must target specific specialist type  |
| Context windows   | 5 (same template per researcher) | 3 (different system prompt per agent) |

---

## Runtime Labels (key ones to watch)

```
📤 [DISPATCHING: weather-analyst]       sub-agent dispatch event
📬 [REPORT RECEIVED: weather-analyst]   report collected, quality shown
🎲 [MODEL DECISION] lead=weather        G2 — model-owned choice
🔄 [LOOP FEEDBACK] low news quality → changed category
```

---

## Files

```
agents/morning-intel/
  prompt.md                             ← this file
  morning-intel_learning-guide.html     ← Part 1: pre-run reading
  main.py                               ← entry point + agent loop
  smoke_test.py                         ← QA: all branch paths
  requirements.txt
  .env.example
  README.md
  morning-intel_run_output.log          ← auto-created by main.py
  morning-intel_briefing_log.json       ← auto-created on goal-met
```
