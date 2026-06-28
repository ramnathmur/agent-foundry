# Agent Foundry -- OpenAI Independent Candidate Analysis

## Phase 1 -- Long List (15 candidates)

### C01 -- morning-weighted-priority-briefing
- `Name`: morning-weighted-priority-briefing
- `Domain`: morning-briefing
- `SDK rung level`: 4
- `Trait coverage`:
  - Goal-oriented: `briefing_ready(state)` fires only when the weighted score across the day's priorities crosses the minimum threshold.
  - ReAct loop: the model weighs competing inputs, chooses the next clarifying question or suggestion, then re-evaluates the weighted score after the answer.
  - Memory: `priority_profile.json` stores per-day weights, prior tradeoffs, and which priorities tend to dominate.
  - Iterativeness: the loop repeats until the weighted score is high enough or the time cap is reached.
- `What's new vs. all prior work`: weighted multi-objective predicate. The novelty is that "done" is not a single condition; it is a scored tradeoff across multiple goals, with explicit weights in code.
- `Gate difficulty`: G1 hard, G2 medium, G3 medium, G4 easy
- `Overlap check`: No overlap with Claude-10 primary novelty patterns.

### C02 -- morning-confidence-band-check
- `Name`: morning-confidence-band-check
- `Domain`: morning-briefing
- `SDK rung level`: 3
- `Trait coverage`:
  - Goal-oriented: `confidence_ready(state)` fires only when the agent's confidence interval around the day's plan narrows enough to justify closing.
  - ReAct loop: the model asks targeted follow-up questions when uncertainty is wide, then updates the estimate after each answer.
  - Memory: `confidence_log.json` stores prior confidence estimates and whether the agent was overconfident or underconfident.
  - Iterativeness: the loop repeats until the interval is tight enough or the cap fires.
- `What's new vs. all prior work`: confidence-interval predicate. The agent closes on statistical certainty, not on a raw count, threshold, or boolean.
- `Gate difficulty`: G1 hard, G2 medium, G3 medium, G4 easy
- `Overlap check`: No overlap with Claude-10 primary novelty patterns.

### C03 -- morning-budget-briefing
- `Name`: morning-budget-briefing
- `Domain`: morning-briefing
- `SDK rung level`: 4
- `Trait coverage`:
  - Goal-oriented: `budget_safe(state)` fires only when the briefing is useful and the cumulative cost stays below the fixed budget.
  - ReAct loop: the model decides whether to spend one more question or stop based on remaining budget versus expected value.
  - Memory: `budget_history.json` stores prior overspends, question counts, and how much budget each day consumed.
  - Iterativeness: the loop stops by budget exhaustion or by hitting the usefulness threshold.
- `What's new vs. all prior work`: budget/cost predicate. This teaches that a goal can be defined by resource consumption, not only by task completion.
- `Gate difficulty`: G1 medium, G2 medium, G3 medium, G4 easy
- `Overlap check`: No overlap with Claude-10 primary novelty patterns.

### C04 -- morning-user-approval-agenda
- `Name`: morning-user-approval-agenda
- `Domain`: morning-briefing
- `SDK rung level`: 3
- `Trait coverage`:
  - Goal-oriented: `user_approved(state)` fires only when Ram explicitly signs off on one agenda.
  - ReAct loop: the model proposes an agenda, observes approval or rejection, revises, and asks again if needed.
  - Memory: `agenda_history.json` stores prior proposals and which version the user actually accepted.
  - Iterativeness: the process is user-paced; each milestone ends in an explicit check-in rather than silent auto-close.
- `What's new vs. all prior work`: user-approval predicate. The predicate is satisfied by explicit user sign-off, not by the model saying it is done.
- `Gate difficulty`: G1 medium, G2 medium, G3 medium, G4 easy
- `Overlap check`: No overlap with Claude-10 primary novelty patterns.

### C05 -- morning-self-audit-adversarial-check
- `Name`: morning-self-audit-adversarial-check
- `Domain`: morning-briefing
- `SDK rung level`: 4
- `Trait coverage`:
  - Goal-oriented: `plan_survives_challenge(state)` fires only when the plan passes an internal contradiction check and the agent repairs every flagged issue.
  - ReAct loop: the model proposes a plan, runs a challenge pass, observes the failure report, and revises the plan before re-checking.
  - Memory: `audit_trace.json` stores failed assertions, repaired assertions, and which checks have already been cleared.
  - Iterativeness: the loop continues until the adversarial check is satisfied or the cap fires.
- `What's new vs. all prior work`: adversarial predicate. The goal is gated by a challenge function that actively tries to invalidate the agent's own answer.
- `Gate difficulty`: G1 hard, G2 medium, G3 hard, G4 easy
- `Overlap check`: No overlap with Claude-10 primary novelty patterns.

### C06 -- recovery-branch-planner
- `Name`: recovery-branch-planner
- `Domain`: health-habits
- `SDK rung level`: 4
- `Trait coverage`:
  - Goal-oriented: `both_branches_complete(state)` fires only when the setup branch and the behavior branch both finish.
  - ReAct loop: the agent splits into two parallel chains, observes each branch's result, then recombines before deciding the next step.
  - Memory: `branch_state.json` keeps both branch states, which branch is blocked, and which branch is already resolved.
  - Iterativeness: the loop is explicitly branching, not linear; one successful branch does not end the session.
- `What's new vs. all prior work`: branching iteration. The loop forks and recombines, so the agent has to manage parallel partial progress rather than a single line of steps.
- `Gate difficulty`: G1 hard, G2 medium, G3 hard, G4 easy
- `Overlap check`: No overlap with Claude-10 primary novelty patterns.

### C07 -- recovery-critic-loop
- `Name`: recovery-critic-loop
- `Domain`: health-habits
- `SDK rung level`: 4
- `Trait coverage`:
  - Goal-oriented: `critic_approved(state)` fires only after the producer plan survives an explicit critique pass.
  - ReAct loop: the agent drafts a recovery plan, switches to a critic lens, observes the critique, then rewrites the plan.
  - Memory: `plan_trace.json` stores the producer draft, critic notes, and final revision so the next turn can reuse the critique pattern.
  - Iterativeness: the producer->critic->producer cycle can repeat multiple times before closing.
- `What's new vs. all prior work`: two-agent inner loop. The model is made to argue with itself in a structured producer/critic cycle without requiring a separate rung-7 verifier.
- `Gate difficulty`: G1 medium, G2 hard, G3 hard, G4 easy
- `Overlap check`: No overlap with Claude-10 primary novelty patterns.

### C08 -- diminishing-returns-move-coach
- `Name`: diminishing-returns-move-coach
- `Domain`: health-habits
- `SDK rung level`: 3
- `Trait coverage`:
  - Goal-oriented: `marginal_gain_acceptable(state)` fires only when the next small adjustment is no longer worth the cost.
  - ReAct loop: the agent tries one small change, observes the gain, updates the gain curve, and chooses whether another iteration is worth it.
  - Memory: `gain_curve.json` stores the observed marginal gains across prior attempts.
  - Iterativeness: the stop condition is not "goal met" but "additional iteration no longer pays for itself."
- `What's new vs. all prior work`: diminishing-return stop condition. The loop ends on marginal utility, not on a hard success threshold.
- `Gate difficulty`: G1 hard, G2 medium, G3 medium, G4 easy
- `Overlap check`: No overlap with Claude-10 primary novelty patterns.

### C09 -- hydration-caffeine-shared-ledger
- `Name`: hydration-caffeine-shared-ledger
- `Domain`: health-habits
- `SDK rung level`: 4
- `Trait coverage`:
  - Goal-oriented: `balance_ok(state)` fires when both hydration and caffeine constraints are within range.
  - ReAct loop: the agent can read from the hydration tool or the caffeine tool first, but both tools write into one shared balance ledger before the final decision.
  - Memory: `balance_ledger.json` is updated by two independent tools that do not depend on each other.
  - Iterativeness: the agent revisits the ledger after each update and chooses the next action based on the shared state, not a fixed script.
- `What's new vs. all prior work`: shared memory between two concerns. The ledger is updated by two independent tools that feed the same state object.
- `Gate difficulty`: G1 medium, G2 medium, G3 medium, G4 easy
- `Overlap check`: No overlap with Claude-10 primary novelty patterns.

### C10 -- study-session-compressor
- `Name`: study-session-compressor
- `Domain`: learning-research
- `SDK rung level`: 3
- `Trait coverage`:
  - Goal-oriented: `compression_valid(state)` fires only when the compressed notes still pass a recall probe.
  - ReAct loop: the agent reads prior session notes, compresses them, then tests whether the compressed version still supports a later recall question.
  - Memory: `compressed_notes.json` stores the compressed summary alongside the raw notes so the next session starts from a smaller context.
  - Iterativeness: the agent can re-compress if recall fails, but it stops once compression is faithful enough.
- `What's new vs. all prior work`: summarized/compressed memory. The agent does not just remember more or less; it actively rewrites memory into a shorter representation for later reuse.
- `Gate difficulty`: G1 medium, G2 medium, G3 medium, G4 easy
- `Overlap check`: No overlap with Claude-10 primary novelty patterns.

### C11 -- morning-stall-escalator
- `Name`: morning-stall-escalator
- `Domain`: morning-briefing
- `SDK rung level`: 3
- `Trait coverage`:
  - Goal-oriented: `agenda_clear(state)` fires once the user's intent is unblocked.
  - ReAct loop: the agent tries an open question, then a narrower prompt, then a forced-choice fallback if the answer is still vague.
  - Memory: `stall_log.json` records which prompt shapes produced vague answers.
  - Iterativeness: the escalation ladder is finite, but the core decision is still mostly scripted.
- `What's new vs. all prior work`: escalation strategy, but only superficially. The model is mostly following a fixed fallback ladder.
- `Gate difficulty`: G1 easy, G2 low, G3 low, G4 easy
- `Overlap check`: Overlaps Claude's Daily Focus Setter pattern too closely and does not add a new primary novelty face.

### C12 -- user-paced-plan-maker
- `Name`: user-paced-plan-maker
- `Domain`: morning-briefing
- `SDK rung level`: 3
- `Trait coverage`:
  - Goal-oriented: `user_signoff(state)` fires only after Ram confirms the plan at each milestone.
  - ReAct loop: the agent proposes a milestone, waits, observes the response, and only then moves forward.
  - Memory: `milestone_log.json` stores which milestone was reached and whether the user paused or continued.
  - Iterativeness: the loop is user-paced, but the structure is otherwise a standard sign-off gate.
- `What's new vs. all prior work`: user-paced iteration. The agent gives up control of the tempo and waits for the user at each milestone.
- `Gate difficulty`: G1 medium, G2 low, G3 low, G4 easy
- `Overlap check`: Overlaps C04's user-approval predicate too closely; the loop tempo changes, but the primary novelty is not distinct enough.

### C13 -- adversarial-confidence-check
- `Name`: adversarial-confidence-check
- `Domain`: morning-briefing
- `SDK rung level`: 4
- `Trait coverage`:
  - Goal-oriented: `confidence_survives_critique(state)` fires only when the agent's confidence estimate survives an internal challenge.
  - ReAct loop: the model estimates confidence, runs a critic pass, and then revises the estimate if the challenge exposes weak evidence.
  - Memory: `confidence_audit.json` keeps both the original estimate and the criticized estimate.
  - Iterativeness: the loop can repeat, but the main action is still a confidence update.
- `What's new vs. all prior work`: this tries to add an adversarial predicate, but it does not separate cleanly from C02's confidence-interval predicate.
- `Gate difficulty`: G1 medium, G2 medium, G3 medium, G4 easy
- `Overlap check`: Primary novelty overlaps C02; the critic pass is not a distinct enough face to justify another build.

### C14 -- decay-prune-habit-log
- `Name`: decay-prune-habit-log
- `Domain`: health-habits
- `SDK rung level`: 3
- `Trait coverage`:
  - Goal-oriented: `memory_still_useful(state)` fires only if the log has not decayed past the prune threshold.
  - ReAct loop: the agent reads the log, decays old entries, and decides whether a fresh prompt is needed.
  - Memory: `habit_log.json` includes a decay score that shrinks over time, and old entries are pruned when they fall below the cutoff.
  - Iterativeness: the agent revisits the log on later days, but the loop is shallow.
- `What's new vs. all prior work`: decay/forgetting over time, but the pattern is too close to the earlier rolling-window memory face to earn a fresh cycle.
- `Gate difficulty`: G1 medium, G2 low, G3 low, G4 easy
- `Overlap check`: Too close to Claude's Sleep Quality Interpreter memory pattern; it is a recycling of forgetting, not a new primary novelty.

### C15 -- priority-review-queue
- `Name`: priority-review-queue
- `Domain`: learning-research
- `SDK rung level`: 3
- `Trait coverage`:
  - Goal-oriented: `queue_processed(state)` fires after every item in the ranked queue has been handled or explicitly demoted.
  - ReAct loop: the agent picks the highest-ranked item, reviews it, then reorders the queue based on the observed outcome.
  - Memory: `review_queue.json` stores a ranked list instead of a flat log.
  - Iterativeness: the queue is revisited across turns, but the decision logic is mostly ordering, not adaptation.
- `What's new vs. all prior work`: priority-ranked memory. The ledger is ordered by rank rather than stored as a flat history.
- `Gate difficulty`: G1 medium, G2 low, G3 low, G4 easy
- `Overlap check`: No direct Claude-10 overlap, but the candidate is too thin to justify a build cycle.

## Phase 2 -- Evaluation Dimensions

I am using a five-dimension rubric because the task is not just novelty hunting; it is curriculum sequencing for a solo learner.

- `D1 -- Trait Novelty`:
  - Tests whether the candidate introduces a new face of one of the four core traits.
  - Score 0 means recycled behavior; score 3 means clearly new behavior that the prior analysis does not already cover.
- `D2 -- Gate Density`:
  - Tests how much real code is required to make G1-G4 true.
  - Score 0 means the gates are basically decorative; score 3 means the gates force real control flow, state tracking, and termination logic.
- `D3 -- Predicate Sophistication`:
  - Tests how interesting the goal predicate is as a code-side computation.
  - Score 0 means a trivial boolean; score 3 means a nontrivial structure such as weights, confidence, adversity, or branch-completion logic.
- `D4 -- Curriculum Safety`:
  - Tests whether the candidate fits the rungs 1-4 ladder without requiring rung 5+ ideas.
  - Score 0 means it leans on unavailable capabilities; score 3 means it is cleanly buildable with the unlocked stack.
- `D5 -- Domain Coverage Value`:
  - Tests whether the candidate fills an underused daily-life domain or reinforces a deliberately prioritized one.
  - Score 0 means low marginal value; score 3 means it fills a high-value gap, especially morning-briefing.

These dimensions are enough to rank the candidates without pretending that every kind of novelty is equally useful for this learner.

## Phase 3 -- Adversarial Review

| ID | Candidate | D1 | D2 | D3 | D4 | D5 | Total | Verdict |
|---|---|---:|---:|---:|---:|---:|---:|---|
| C01 | morning-weighted-priority-briefing | 3 | 3 | 3 | 3 | 3 | 15 | Accept |
| C02 | morning-confidence-band-check | 3 | 3 | 3 | 3 | 3 | 15 | Accept |
| C03 | morning-budget-briefing | 3 | 3 | 3 | 3 | 3 | 15 | Accept |
| C04 | morning-user-approval-agenda | 3 | 2 | 2 | 3 | 3 | 13 | Accept |
| C05 | morning-self-audit-adversarial-check | 3 | 3 | 3 | 3 | 3 | 15 | Accept |
| C06 | recovery-branch-planner | 3 | 3 | 3 | 3 | 2 | 14 | Accept |
| C07 | recovery-critic-loop | 3 | 3 | 2 | 3 | 2 | 13 | Accept |
| C08 | diminishing-returns-move-coach | 3 | 3 | 3 | 3 | 2 | 14 | Accept |
| C09 | hydration-caffeine-shared-ledger | 3 | 3 | 2 | 3 | 2 | 13 | Accept |
| C10 | study-session-compressor | 3 | 3 | 2 | 3 | 1 | 12 | Accept |
| C11 | morning-stall-escalator | 1 | 1 | 1 | 2 | 3 | 8 | Reject |
| C12 | user-paced-plan-maker | 1 | 1 | 1 | 3 | 3 | 9 | Reject |
| C13 | adversarial-confidence-check | 1 | 2 | 1 | 3 | 3 | 10 | Reject |
| C14 | decay-prune-habit-log | 1 | 1 | 1 | 2 | 2 | 7 | Reject |
| C15 | priority-review-queue | 1 | 1 | 1 | 2 | 1 | 6 | Reject |

### Rejection verdicts
- C11 `morning-stall-escalator`: Rejected because G2 is effectively scripted. Python owns the escalation ladder, and the model is only filling in slots. It also overlaps Claude's `Daily Focus Setter` adaptive-question pattern too closely.
- C12 `user-paced-plan-maker`: Rejected because it is the same primary user-approval gate as C04 with a tempo change only. That is not a new trait face.
- C13 `adversarial-confidence-check`: Rejected because it collapses into C02. The adversarial pass does not create a distinct primary novelty pattern.
- C14 `decay-prune-habit-log`: Rejected because it recycles the rolling-forgetting idea already explored in Claude's earlier memory work. G2 and G3 are too weak to justify a fresh cycle.
- C15 `priority-review-queue`: Rejected because G2 is absent or near-absent. Ranking alone does not give the model a real decision; it becomes a workflow around an ordered list.

## Top-10 -- Prioritized Build Order

| Rank | Candidate | D1 | D2 | D3 | D4 | D5 | Total | What it teaches |
|---|---|---:|---:|---:|---:|---:|---:|---|
| 1 | morning-weighted-priority-briefing | 3 | 3 | 3 | 3 | 3 | 15 | Weighted multi-objective predicate |
| 2 | morning-confidence-band-check | 3 | 3 | 3 | 3 | 3 | 15 | Confidence-interval predicate |
| 3 | morning-budget-briefing | 3 | 3 | 3 | 3 | 3 | 15 | Budget/cost predicate |
| 4 | morning-self-audit-adversarial-check | 3 | 3 | 3 | 3 | 3 | 15 | Adversarial predicate |
| 5 | recovery-branch-planner | 3 | 3 | 3 | 3 | 2 | 14 | Branching iteration |
| 6 | diminishing-returns-move-coach | 3 | 3 | 3 | 3 | 2 | 14 | Diminishing-return stop condition |
| 7 | morning-user-approval-agenda | 3 | 2 | 2 | 3 | 3 | 13 | User-approval predicate |
| 8 | recovery-critic-loop | 3 | 3 | 2 | 3 | 2 | 13 | Two-agent inner loop |
| 9 | hydration-caffeine-shared-ledger | 3 | 3 | 2 | 3 | 2 | 13 | Shared memory between two concerns |
| 10 | study-session-compressor | 3 | 3 | 2 | 3 | 1 | 12 | Summarized/compressed memory |

## Trait Map

| Trait | Already demonstrated (cite Claude-10) | New faces in your top-10 |
|---|---|---|
| Goal-oriented | `C04 Sleep Quality Interpreter` (rolling window), `C05 Habit Pulse v2` (trajectory/streak), `C09 Book Reflection Agent` (novelty detection), `C10 Language Drill Agent` (time-aware threshold), `C11 Concept Mapper` (graph predicate), `C12 Habit Streak + Accountability` (path-dependent failure branch) | Weighted multi-objective (`morning-weighted-priority-briefing`), confidence-interval (`morning-confidence-band-check`), budget/cost (`morning-budget-briefing`), adversarial (`morning-self-audit-adversarial-check`), user-approval (`morning-user-approval-agenda`) |
| ReAct loop | `C01 Morning Spark v3` (multi-source synthesis), `C02 Daily Focus Setter` (adaptive questioning), `C06 Mood Journal + Pattern Spotter` (conditional chaining), `C11 Concept Mapper` (gap probing), `C12 Habit Streak + Accountability` (failure recovery) | Branching/recombining (`recovery-branch-planner`), producer-critic inner loop (`recovery-critic-loop`), budget-aware stop/continue decisions (`morning-budget-briefing`), user-paced sign-off loops (`morning-user-approval-agenda`), adversarial challenge-and-repair (`morning-self-audit-adversarial-check`) |
| Memory | `C03 Journal Prompt Agent` (agent reads its own outputs), `C04 Sleep Quality Interpreter` (rolling window), `C05 Habit Pulse v2` (three flat ledgers), `C10 Language Drill Agent` (time-aware entries), `C11 Concept Mapper` (graph memory) | Shared ledger across two tools (`hydration-caffeine-shared-ledger`), compressed memory (`study-session-compressor`), ranked memory as a rejected edge case (`priority-review-queue`) but not a build pick |
| Iterativeness | `C02 Daily Focus Setter` (question adaptation), `C03 Journal Prompt Agent` (refinement rounds), `C10 Language Drill Agent` (re-queue on failure), `C11 Concept Mapper` (nonlinear graph growth), `C12 Habit Streak + Accountability` (recovery loop) | User-paced iteration (`morning-user-approval-agenda`), branching iteration (`recovery-branch-planner`), diminishing-return stop condition (`diminishing-returns-move-coach`) |

## Recommended First Build

`morning-weighted-priority-briefing` should be the first build. It gives the learner the cleanest next step because it introduces a genuinely new goal predicate pattern, weighted multi-objective scoring, without asking for any rung-5 capability. It also fits the underused morning-briefing domain, so the project gets both curriculum novelty and domain coverage at the same time. Most importantly, it teaches the right lesson for this stage: "done" can be a computed tradeoff, not a yes/no label.
