# Agent Foundry — Cycle 4+ Candidate Analysis
**Date:** 2026-06-11  
**Scope:** 10 agent candidates at SDK rungs 2–4; demonstrating goal-oriented, ReAct loop, memory, and iterativeness traits  
**Method:** Long list → Persona selection → Adversarial review → Prioritized top-10

---

## Phase 1 — Long List (17 Candidates)

Reference state: Rungs 1–4 introduced. Traits demonstrated so far: basic loop, goal predicate, session memory, app memory (flat ledgers), within-turn tool chaining, 4 exit paths. What hasn't been demonstrated yet: multi-source synthesis, graph-state memory, time-aware memory, compound predicates, novelty-detection predicates, multi-branch predicates (failure path), agent reading its own prior outputs, adaptive question strategy based on cross-day patterns.

---

### C01 — Morning Spark v3
```
Name:           morning-spark-v3
Domain:         morning-briefing
Rung level:     4
Trait coverage:
  goal-oriented  → predicate: briefing_complete(state) = all three sources fetched + summary generated
  ReAct loop     → multi-source: fetch weather → fetch date/day → fetch one news headline (mocked APIs) →
                   synthesize → quality-check summary → re-fetch if gaps
  memory         → APP: briefing_log.json (date → summary → topics covered); cross-day repetition guard
  iterativeness  → loop doesn't close until all three sources yield non-empty results AND quality predicate passes
What's new:     First agent with multi-source perception. The ReAct loop's observation feeds from THREE
                independent tools simultaneously; the model must synthesize them into a coherent briefing
                *and* self-check quality before the predicate fires. No prior agent combined multiple
                real-time sources. Cross-day memory guard prevents repeating yesterday's top topic.
Gate difficulty: G1 medium (compound: all-sources-fetched AND summary-quality), G2 medium, G3 hard
                (multi-source feedback), G4 easy (cap + predicate both wired)
```

---

### C02 — Daily Focus Setter
```
Name:           daily-focus-setter
Domain:         morning-briefing
Rung level:     3
Trait coverage:
  goal-oriented  → predicate: focus_stated(state) = Ram has articulated one clear focus statement
  ReAct loop     → adaptive questioning: observes answer quality → adjusts next question (vaguer answers
                   trigger probing; clear answers trigger confirmation + close)
  memory         → APP: focus_log.json stores today's + prior focus statements; agent compares and flags
                   if Ram has been stuck on the same focus >3 consecutive days
  iterativeness  → doesn't close until focus predicate fires or cap; detects circular answers
What's new:     The G3 loop demonstrates *adaptive questioning strategy* — the model changes the *type*
                of question (broader → narrower → concrete) based on what it observes in the answer. Prior
                agents asked questions but didn't change question strategy mid-loop. Memory comparison
                (today vs. prior days) adds the cross-day pattern detection missing from study-buddy.
Gate difficulty: G1 easy (boolean predicate), G2 medium (question-type selection is model's decision),
                G3 medium (question-strategy feedback), G4 easy
```

---

### C03 — Journal Prompt Agent
```
Name:           journal-prompt-agent
Domain:         morning-briefing (adjacent)
Rung level:     3
Trait coverage:
  goal-oriented  → predicate: prompt_accepted(state) = Ram has confirmed today's journal prompt fits
  ReAct loop     → reads yesterday's journal entry (app memory) → generates a tailored prompt →
                   observes Ram's reaction → refines prompt if rejected → confirms if accepted
  memory         → APP: journal_log.json stores past entries AND what prompts were generated. The agent
                   reads its own prior outputs as input — the ledger tracks agent-generated content, not
                   just user input.
  iterativeness  → up to 3 prompt refinements before cap; each refinement is informed by rejection reason
What's new:     First agent where the ledger tracks what the *agent itself generated*, not just what the
                user provided. The agent reads yesterday's prompt alongside yesterday's entry to detect
                whether its prompts are becoming repetitive. This exposes a new face of memory: the agent
                has a self-model of its own prior behavior and uses it to avoid repetition. No prior agent
                does this.
Gate difficulty: G1 easy, G2 medium (prompt generation strategy is model-owned), G3 medium (rejection
                → refinement feedback edge), G4 easy
```

---

### C04 — Sleep Quality Interpreter
```
Name:           sleep-quality-interpreter
Domain:         health-habits / morning-briefing
Rung level:     3
Trait coverage:
  goal-oriented  → predicate: recommendation_issued(state) = agent has given a day-type recommendation
  ReAct loop     → user inputs sleep data → agent compares to 7-day rolling ledger → selects
                   recommendation category → issues recommendation
  memory         → APP: sleep_log.json with 7-day rolling window; agent trims entries older than 7 days
  iterativeness  → thin: single-pass most days; only iterates when data is incomplete
What's new:     Rolling-window memory with automatic trimming — the first agent where the ledger has a
                deliberate *forgetting* mechanism. However, the ReAct loop is thin (mostly one pass).
Gate difficulty: G1 easy, G2 low, G3 low, G4 easy
NOTE:           G2 and G3 are weak. The agent is close to a workflow for most inputs. Flagged for
                adversarial review.
```

---

### C05 — Habit Pulse v2
```
Name:           habit-pulse-v2
Domain:         health-habits
Rung level:     4
Trait coverage:
  goal-oriented  → predicate: session_complete(state) = today's target habits all checked in + streak updated
  ReAct loop     → check_streak → log_habit → analyze_impact_on_streak → suggest_tomorrow (4-tool chain)
  memory         → APP: habits.json (definitions), streaks.json (per-habit streak counters), log.json
                   (daily entries). Three ledgers, each with a distinct role.
  iterativeness  → loops until all target habits are checked or user issues a "skip" — model decides
                   whether a partial check-in is acceptable or whether to keep asking
What's new:     **Streak as goal predicate** — for the first time, the goal predicate is not binary (done/
                not-done) but threshold-based across time: streak_length ≥ target_streak. The model must
                evaluate whether today's action *contributes to* the goal or undermines it — it's a
                *trajectory* predicate, not a snapshot predicate. Also deepens tool chaining: the check →
                log → analyze chain must complete in the correct order because each tool's output is the
                next's input.
Gate difficulty: G1 medium (threshold + trajectory), G2 medium, G3 medium, G4 easy
```

---

### C06 — Mood Journal + Pattern Spotter
```
Name:           mood-journal-pattern-spotter
Domain:         health-habits
Rung level:     4
Trait coverage:
  goal-oriented  → predicate: session_complete = mood logged AND (no pattern → simple close) OR
                   (pattern detected → Ram has acknowledged it)
  ReAct loop     → log_mood → detect_pattern (reads last 7 entries) → if pattern: note_trigger + suggest
  memory         → APP: mood_log.json (date → mood → notes); rolling 7-entry window
  iterativeness  → two paths: simple (1 turn) or pattern-detected (2-3 turns, agent probes trigger)
What's new:     **Diagnostic tool chaining** — the chain is triggered by what was *just logged*, not by
                a fixed sequence. If no pattern exists, the second tool is not called. This teaches that
                tool chaining is conditional (model decides whether to chain), not mandatory. Prior
                recipe-companion always chained all five tools. This demonstrates selective chaining.
Gate difficulty: G1 medium (conditional predicate), G2 medium (chain decision), G3 medium, G4 easy
```

---

### C07 — Medication / Supplement Reminder
```
Name:           supplement-check-agent
Domain:         health-habits
Rung level:     3
Trait coverage:
  goal-oriented  → predicate: all_items_checked(state) = every scheduled item answered (taken or skipped)
  ReAct loop     → read schedule → ask about first unchecked item → log response → update → repeat
  memory         → APP: schedule.json (the items), adherence_log.json (daily records)
  iterativeness  → loops item by item; handles partial completion ("I'll do it later" → recheck at end)
What's new:     **Deferred completion state** — items can be in three states: done, skipped, deferred.
                The goal predicate must handle "deferred" gracefully without treating it as failure. First
                agent where the predicate has three-valued logic rather than binary.
Gate difficulty: G1 medium (three-valued predicate), G2 low (model just sequences items), G3 low,
                G4 easy
NOTE:           G2 is weak — the model doesn't make a real decision; it sequences a list. Borderline.
```

---

### C08 — Meal Log Analyzer
```
Name:           meal-log-analyzer
Domain:         health-habits
Rung level:     4
Trait coverage:
  goal-oriented  → predicate: week_nutrition_adequate(state) = all key nutrients hit their weekly targets
                   across logged meals (compound, multi-ledger predicate)
  ReAct loop     → log_meal → check_nutritional_gaps → if gap: suggest_adjustment → observe acceptance
  memory         → APP: meals.json (daily log), nutrition_targets.json (weekly goals), preferences.json
                   (dislikes/restrictions). Compound predicate reads all three.
  iterativeness  → agent doesn't just log and close; it surfaces the weekly deficit and adapts suggestions
                   based on what's already been logged today AND this week
What's new:     **Compound multi-ledger predicate** — for the first time, the goal predicate reads from
                THREE separate ledgers simultaneously to compute a verdict. This is qualitatively more
                complex than recipe-companion's tool chaining (which operated on single-ledger state).
                The predicate must be evaluated against the *aggregate* of many days' data, not just today.
Gate difficulty: G1 hard (compound cross-ledger predicate), G2 medium, G3 medium, G4 easy
```

---

### C09 — Book Progress + Reflection Agent
```
Name:           book-reflection-agent
Domain:         learning-research
Rung level:     3
Trait coverage:
  goal-oriented  → predicate: new_insight_recorded(state) = Ram has articulated at least one concept not
                   present in prior session reflections
  ReAct loop     → reads prior reflections (app memory) → asks reflection questions → compares answers to
                   prior entries → if no new insight yet: probes differently → closes when predicate fires
  memory         → APP: reading_journal.json stores past reflections indexed by book + date
  iterativeness  → max 4 reflection rounds; the agent changes its probing strategy if early answers
                   mirror prior sessions
What's new:     **Novelty-detection predicate** — the goal predicate doesn't check a counter or threshold,
                it checks whether this session's content is *meaningfully different* from prior sessions.
                This is the first predicate that requires semantic comparison, not just a numeric check.
                It exposes a deep lesson: what counts as "done" can itself be a non-trivial computation.
Gate difficulty: G1 hard (novelty detection requires comparison logic), G2 medium, G3 medium, G4 easy
```

---

### C10 — Language Drill Agent (Spaced Repetition)
```
Name:           language-drill-agent
Domain:         learning-research
Rung level:     4
Trait coverage:
  goal-oriented  → predicate: session_complete = today's due-for-review words have all been tested
                   (due = next_review_date <= today)
  ReAct loop     → load_due_words → for each: pick_word → test_translation → update_mastery_and_schedule
  memory         → APP: vocab_ledger.json stores each word with: mastery_score, review_count,
                   next_review_date. Memory is TIME-AWARE — the predicate depends on dates, not just values.
  iterativeness  → loops over due words; if a word is failed, it's re-queued within the session
What's new:     **Time-aware app memory** — the first agent where the ledger entries have a temporal
                dimension (next_review_date). This fundamentally changes the goal predicate: it depends
                on the *current date* compared against stored dates. No prior agent has this. Also
                demonstrates that iterativeness can mean re-queuing within the same session (a word can
                be tested multiple times per session if failed).
Gate difficulty: G1 medium (date-comparison predicate), G2 medium, G3 medium, G4 easy
```

---

### C11 — Concept Mapper
```
Name:           concept-mapper
Domain:         learning-research
Rung level:     4
Trait coverage:
  goal-oriented  → predicate: map_connected(state) = the concept graph has no isolated nodes AND
                   connectivity_ratio >= 0.7
  ReAct loop     → add_concept → link_concepts → find_gap → probe_ram_about_gap → if gap resolved: re-check
  memory         → APP: concept_map.json — a graph (nodes + edges), not a flat list
  iterativeness  → agent loops until the graph is dense enough; each probe adds nodes/edges that may
                   unlock further gaps
What's new:     **Graph-state memory** — the app memory is a JSON graph, not a list or key-value store.
                The goal predicate evaluates graph properties (connectivity), not counts. This is the
                most structurally novel memory architecture in the candidate list. It also demonstrates
                that iterativeness can be non-linear: adding one concept may retroactively make a
                previously-gapped area connected.
Gate difficulty: G1 hard (graph connectivity predicate), G2 hard (model decides which gap to probe),
                G3 hard (adding a node changes the graph → changes which gaps exist), G4 easy
```

---

### C12 — Habit Streak + Accountability Agent
```
Name:           habit-streak-accountability
Domain:         health-habits
Rung level:     4
Trait coverage:
  goal-oriented  → predicate has TWO paths: if streak_intact → simple_close; if streak_broken →
                   recovery_plan_acknowledged. The predicate is *path-dependent*.
  ReAct loop     → check_streaks → if broken: analyze_failure_pattern → recommend_recovery →
                   observe acceptance → update recovery log
  memory         → APP: streaks.json + failure_log.json + recovery_plans.json
  iterativeness  → recovery plan loop: agent proposes → user adjusts → agent confirms → close
What's new:     **Path-dependent predicate with failure branch** — this is the first agent where the
                goal predicate has different exit shapes depending on the state. A "success" exit and
                a "failure recovery" exit are distinct code paths, both of which the predicate can fire.
                This teaches that G1 predicates need not be symmetric — the "what does done mean?" 
                question has different answers depending on the outcome. Critical lesson for real agents.
Gate difficulty: G1 hard (path-dependent predicate), G2 medium, G3 medium, G4 medium (recovery loop
                has its own termination logic)
```

---

### C13 — Exam Prep Coach
```
Name:           exam-prep-coach
Domain:         learning-research
Rung level:     4
Trait coverage:
  goal-oriented  → predicate: mastery_adequate = all topic scores >= 0.75 in mastery_map
  ReAct loop     → load_topic → generate_question → evaluate_answer → update_mastery → pick_next_topic
  memory         → APP: mastery_map.json (nested: topic → subtopic → score)
  iterativeness  → adapts question difficulty based on score; loops until predicate fires or cap
What's new:     Nested mastery map is richer than study-buddy's flat weak_spots.json. Difficulty
                adaptation is new. However, this is largely study-buddy with more tools.
NOTE (adversarial pre-flag): The core loop is structurally very similar to study-buddy. The new
                elements (difficulty scaling, nested mastery) are incremental. This candidate may be
                rejected by the adversarial reviewer as insufficiently novel.
Gate difficulty: G1 medium, G2 medium, G3 medium, G4 easy
```

---

### C14 — Vocabulary Builder
```
Name:           vocab-builder
Domain:         learning-research
Rung level:     3
Trait coverage:
  goal-oriented  → predicate: mastery_score >= 0.8 for the target word (score computed from probe answers)
  ReAct loop     → ask probe → score answer → update word score → if not mastered: different probe type
  memory         → APP: mastery_ledger.json (word → score → examples_attempted)
  iterativeness  → keeps probing until mastery threshold or cap; changes probe type on retry
What's new:     Score-based predicate (numeric threshold vs. binary boolean). First agent where the
                predicate is a floating-point threshold, not a count or boolean.
NOTE (adversarial pre-flag): Too similar to study-buddy in structure; just narrows to single-word
                scope. The numeric-threshold predicate is interesting but minor as a lesson. Likely to
                be downranked.
Gate difficulty: G1 easy-medium, G2 low-medium, G3 low-medium, G4 easy
```

---

### C15 — Daily Steps Coach
```
Name:           steps-coach
Domain:         health-habits
Rung level:     3
Trait coverage:
  goal-oriented  → predicate: steps_logged AND feedback_given
  ReAct loop     → ask for steps → compare to goal → give feedback → compare to prior days
  memory         → APP: steps_log.json (daily entries)
  iterativeness  → thin: mostly one-pass
What's new:     Very little. The ReAct loop is shallow; the model doesn't make a meaningful decision.
NOTE (adversarial pre-flag): This is a counter with a conversation layer. G2 is essentially absent —
                the model always follows the same sequence. Pre-flagged for rejection.
Gate difficulty: G1 easy, G2 very low, G3 low, G4 easy
```

---

### C16 — Morning Energy Check-in
```
Name:           morning-energy-checkin
Domain:         morning-briefing / health-habits
Rung level:     3
Trait coverage:
  goal-oriented  → predicate: energy_understood = user has confirmed their energy category for today
  ReAct loop     → ask rating → compare to 7-day average → name pattern if one exists → confirm
  memory         → APP: energy_log.json (date → rating → context notes)
  iterativeness  → 1-2 turns normally; up to 3 if pattern is disputed
What's new:     Simpler than Sleep Quality Interpreter. The cross-day comparison is the new element, but
                the loop is thin. Borderline agent-vs-workflow.
NOTE: Similar to C04 (Sleep Quality Interpreter) in structure. One of the two should be dropped.
```

---

### C17 — Research Gap Finder
```
Name:           research-gap-finder
Domain:         learning-research
Rung level:     3–4
Trait coverage:
  goal-oriented  → predicate: all_major_gaps_addressed
  ReAct loop     → fetch topic summary → identify gaps → prioritize gap → research gap → update coverage
  memory         → APP: coverage_map.json (topic → sub-topics covered/gap)
  iterativeness  → loops until all major gaps closed or cap
What's new:     Very similar to study-prep. The multi-source fetching (if rung 4) adds tool chaining,
                but the core loop structure is nearly identical.
NOTE (adversarial pre-flag): This is study-prep v2 with tool chaining. The domain, loop structure,
                and predicate are all recycled. Pre-flagged for rejection.
```

---

## Phase 2 — Persona Selection

### Scoring Persona: `senior_curriculum_architect`

**Justification:** The task is not data analysis or product scoping — it is curriculum sequencing. The Senior Curriculum Architect's competence boundary explicitly includes "module sequence design, prerequisite graph evaluation, and assessment alignment." Every candidate above must be scored on whether it fits the pedagogical arc without skipping forward or repeating prior ground. This is exactly a curriculum prereq graph problem: which candidates add new learning objectives (LOs from `AGENT_LEARNING_AND_AGENCY_GATES.md`) without requiring LOs that haven't been introduced yet? No other persona in the library has this specific lens.

**Rejected alternatives:** `senior_eval_engineer` — evaluates LLM judge systems, not curriculum design. `senior_product_manager` — makes product tradeoffs, not pedagogical sequence decisions. `senior_research_analyst` — researches externally cited material; all the material here is internal to the project.

---

### Adversarial Reviewer: `adversarial_reviewer`

**Justification:** The Adversarial Reviewer's explicit competence boundary: "adversarial test of a plan, decision, or claim." Its behavioral signature is default-skeptical — it looks for candidates that *claim* to teach something new but actually recombine prior elements (the "act-as" proxy problem in pedagogy). It is the right persona to eliminate C13 (Exam Prep Coach = study-buddy + more tools), C15 (Daily Steps Coach = counter with chat), and C17 (Research Gap Finder = study-prep v2) without letting nostalgia for familiar patterns carry them forward. The library's `adversarial_reviewer` is specifically defined as operating with "no conversation context" — it grades on structure, not on the author's intent.

---

## Phase 3 — Adversarial Review

### Evaluation Dimensions

Defined by `adversarial_reviewer` persona against the project's own gates framework:

| Dimension | What it tests | Scale |
|---|---|---|
| **D1 — Trait Novelty** | Does this agent demonstrate a genuinely new *face* of one or more of the four core traits, not seen in the prior 3 agents? | 0 = clone / 3 = new behavioral pattern |
| **D2 — Gate Density** | How many of G1–G4 require non-trivial Python to satisfy? Easy gates = weak learning. | 0 = trivial / 3 = all four have real implementation cost |
| **D3 — Predicate Quality** | Is the goal predicate meaningfully more sophisticated than prior agents? Binary predicates (already demonstrated in Cycle 1) score 0. | 0 = binary boolean / 3 = novel predicate structure |
| **D4 — Pedagogical Safety** | Does this fit the arc without requiring forward knowledge (rung 5+)? Does it confuse rather than clarify? | 0 = disruptive or out-of-arc / 3 = clean fit |
| **D5 — Domain Coverage Value** | Does this fill a gap? morning-briefing = high value (0 agents). Third learning-research = low marginal value. | 0 = over-represented domain / 3 = fills coverage gap |

**Max score: 15. Rejection threshold: <8. Top-10 cutoff: top-10 of qualifying candidates.**

---

### Scoring Table

| ID | Candidate | D1 Trait Novelty | D2 Gate Density | D3 Predicate Quality | D4 Ped. Safety | D5 Domain Value | **Total** | Verdict |
|---|---|---|---|---|---|---|---|---|
| C01 | Morning Spark v3 | **3** | **3** | **2** | **3** | **3** | **14** | ✅ |
| C02 | Daily Focus Setter | **2** | 2 | 1 | **3** | **3** | **11** | ✅ |
| C03 | Journal Prompt Agent | **3** | 2 | 2 | **3** | **3** | **13** | ✅ |
| C04 | Sleep Quality Interpreter | 1 | 1 | 1 | **3** | 2 | **8** | ⚠️ borderline |
| C05 | Habit Pulse v2 | 2 | 2 | **2** | **3** | 2 | **11** | ✅ |
| C06 | Mood Journal + Pattern Spotter | 2 | 2 | 2 | **3** | 2 | **11** | ✅ |
| C07 | Supplement Check Agent | 1 | 1 | 1 | **3** | 2 | **8** | ⚠️ borderline |
| C08 | Meal Log Analyzer | **3** | **3** | **3** | **3** | 2 | **14** | ✅ |
| C09 | Book Reflection Agent | **3** | 2 | **3** | **3** | 1 | **12** | ✅ |
| C10 | Language Drill Agent | **3** | 2 | **2** | **3** | 1 | **11** | ✅ |
| C11 | Concept Mapper | **3** | **3** | **3** | **3** | 1 | **13** | ✅ |
| C12 | Habit Streak + Accountability | **3** | **3** | **3** | **3** | 2 | **14** | ✅ |
| C13 | Exam Prep Coach | 1 | 2 | 1 | **3** | 0 | **7** | ❌ rejected |
| C14 | Vocab Builder | 1 | 1 | 1 | **3** | 0 | **6** | ❌ rejected |
| C15 | Daily Steps Coach | 0 | 0 | 0 | **3** | 2 | **5** | ❌ rejected |
| C16 | Morning Energy Check-in | 1 | 1 | 1 | **3** | 2 | **8** | ⚠️ borderline |
| C17 | Research Gap Finder | 0 | 1 | 0 | **3** | 0 | **4** | ❌ rejected |

**Rejections by adversarial reviewer:**
- **C13 (Exam Prep Coach):** Study-buddy with more tools and a nested mastery map. The core loop structure is recycled. No new predicate pattern. The learning-research domain is already the most-covered (2 agents). Rejected.
- **C14 (Vocab Builder):** Rung 3 + single-word scope = a narrower study-buddy. Numeric threshold predicate is interesting but doesn't justify a full agent cycle. Rejected.
- **C15 (Daily Steps Coach):** G2 is effectively absent. Python owns the sequence; the model responds, it doesn't decide. This is a workflow. Rejected immediately.
- **C17 (Research Gap Finder):** Study-prep v2. Same domain, same loop structure, same predicate type. Rejected.

**Borderline decisions:**
- **C04 (Sleep Quality Interpreter):** The rolling-window-with-forgetting is a conceptually interesting memory pattern (first agent with deliberate forgetting). G2 and G3 are weak, but the memory contribution is genuine. Retained at #10 with a note.
- **C07 (Supplement Check Agent):** Three-valued predicate is real, G2 is weak. Dropped in favor of C04 which has stronger memory novelty.
- **C16 (Morning Energy Check-in):** Structurally too similar to C04. Duplicate. Dropped.

---

## Final Top-10 — Prioritized Build Order

| Rank | Candidate | Score | Rung | Domain | What it teaches next |
|---|---|---|---|---|---|
| **1** | Morning Spark v3 | 14 | 4 | morning-briefing | Multi-source perception + synthesis quality predicate |
| **2** | Habit Streak + Accountability | 14 | 4 | health-habits | Path-dependent predicate with failure branch |
| **3** | Meal Log Analyzer | 14 | 4 | health-habits | Compound multi-ledger predicate |
| **4** | Journal Prompt Agent | 13 | 3 | morning-briefing | Agent reads its own prior outputs as memory |
| **5** | Concept Mapper | 13 | 4 | learning-research | Graph-state memory; non-linear iterativeness |
| **6** | Book Reflection Agent | 12 | 3 | learning-research | Novelty-detection predicate (semantic comparison) |
| **7** | Daily Focus Setter | 11 | 3 | morning-briefing | Adaptive question strategy based on answer quality |
| **8** | Mood Journal + Pattern Spotter | 11 | 4 | health-habits | Conditional (selective) tool chaining |
| **9** | Habit Pulse v2 | 11 | 4 | health-habits | Trajectory predicate (streak threshold across time) |
| **10** | Language Drill Agent | 11 | 4 | learning-research | Time-aware app memory (next_review_date) |
| *(11)* | *(Sleep Quality Interpreter)* | *(8)* | *(3)* | *(health-habits)* | *(Rolling-window memory with forgetting — weak G2)* |

---

## What This Teaches (Trait Map Across the Top-10)

This is the key pedagogical summary — what new face of each trait each agent demonstrates:

| Trait | What's already shown | New faces in this top-10 |
|---|---|---|
| **Goal-oriented** | Binary boolean (C1), score threshold (C2), four-exit (C3) | Compound cross-ledger (C03), path-dependent failure branch (C12), novelty-detection/semantic (C09), trajectory/streak (C05), time-anchored (C10), graph connectivity (C11) |
| **ReAct loop** | Single-source observe → act (C1–C2), tool-chain observe (C3) | Multi-source synthesis (C01), adaptive question strategy (C02), conditional tool chain (C06), graph-gap probing (C11) |
| **Memory** | Session-only (C1), session+app (C2), three flat ledgers (C3) | Agent reads its own outputs (C03), graph-state JSON (C11), time-aware entries with dates (C10), rolling window with forgetting (C04/borderline), compound multi-ledger predicate (C08) |
| **Iterativeness** | Linear cap (C1), four exit paths (C2–C3) | Non-linear (adding a node changes what gaps exist) (C11), re-queue within session on failure (C10), recovery loop with its own termination (C12) |

### Recommended first build: **Morning Spark v3 (C01)**

It's been deferred three times. It introduces multi-source perception — the single most important concept missing from the current curriculum — and its memory (briefing_log cross-day guard) adds a new face of app memory without requiring graph-state complexity. It's rung 4, fits Cycle 4 if Ram defers rung 5 for one more cycle, and directly addresses the domain coverage gap.

### What to build next after that: **Habit Streak + Accountability (C12)**

The path-dependent predicate (failure branch) is the most important pedagogical leap after multi-source perception. It breaks the assumption (established across all three prior agents) that a goal predicate is symmetric — it teaches that "what does done mean?" has different answers depending on how you got there.

---

*This analysis was produced via the Agent Foundry candidate evaluation workflow. Both the `senior_curriculum_architect` and `adversarial_reviewer` persona lenses were applied against the project's Agency Gates framework (G1–G5) and SDK ladder (rungs 1–8). All rejections are traceable to specific gate or novelty failures documented above.*
