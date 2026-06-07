# Agent Learning Objectives & Agency Gates

> **Source:** Distilled from the *Agents Master Course* (13-chapter Python + Claude Agent SDK
> curriculum, locked at v3). Author: Claude. Date: 2026-06-07.
> **Audience:** The Agent Foundry project and every agent it generates.

---

## 0. How to read this file (read this first)

**What this file is.** A single reference that converts the Agents Master Course into
operating rules for *this* project. It answers three questions the Foundry must answer for
every agent it builds:

1. **What is the learner supposed to understand** by the time an agent runs? (§2)
2. **Is this thing actually an agent, or a workflow wearing an agent costume?** (§3 — the gates)
3. **What must the Python code itself make visible** so the answer is provable, not asserted? (§4)

Plus the part that prevents wasted effort: **the gotchas** — the specific places where the
code *looks* agentic but isn't, and where a learner walks away with a wrong mental model (§5).

**How to use it.**
- The Foundry's classifier (PRD §2) and code-gen step (FR-C2) should treat §3 and §4 as
  **acceptance criteria**, not suggestions. An agent that fails a Core gate in §3 is
  labelled a workflow and gets the minimal-fix proposal — exactly as CLAUDE.md already demands.
- §5 is a checklist of **anti-patterns**. Every generated `main.py` should be greppable for
  the *opposite* of each gotcha (the guard that proves the trap was avoided).
- This file is framework-aligned with the project's canonical 9-trait / 3-tier model
  (CLAUDE.md + PRD §2). Where the course uses different chapter names, §6 maps them.

**Background — the one idea the whole course is built on.**
> An LLM call is a **function**: tokens in, tokens out, stateless, no memory, no decisions.
> An **agent is the system built *around* that function.** Every trait below is *structure
> outside the call* — a loop, a predicate, a sensor, a hook, a verifier. You never make the
> model "more agentic." You add scaffolding. If you can't point at the scaffolding in the
> code, the agency isn't there.

This is why the question "is it an agent?" is always answerable by *reading the Python*,
never by inspecting the model.

---

## 1. The spine: who owns the next decision?

Strip every chapter down and one distinction remains — the **control plane**:

| | Workflow | Agent |
|---|---|---|
| Who decides what runs next? | **Python**, fixed at write-time | **The model**, decided at run-time |
| Number of steps | Known by reading the code | Unknown until it runs |
| Reaction to a surprise | None — the path is hard-coded | Observes, re-reasons, re-routes |

Hold this as the litmus. A multi-call, structured-output, multi-step pipeline can be 100%
workflow if Python owns every branch. The course's two sharpest traps (§5.3, §5.4) are
exactly cases where this looks like agency and isn't.

---

## 2. Learning objectives — what any practical agent project must teach

Any agent built in this project (in Python, over a cloud SDK) should let the learner
**watch** each of these happen and **point to the line** where it fires. Grouped by the
project's 3 tiers.

### Core (absence ⇒ it is a workflow, full stop)
- **LO-1 Goal-directedness.** A goal is a **predicate the program can evaluate** (`is_done(state) → bool`),
  not a wish in the prompt. The learner sees the goal stated to the model *and* checked in code.
- **LO-2 Autonomy.** The *model* selects the next step/tool — Python sets the *what*, the model
  owns the *how*. The learner sees a decision that is **not** a hard-coded `[0]` or `if phase == ...`.
- **LO-3 Observe–reason–act loop.** The agent acts, **reads the outcome**, and **adjusts**.
  The learner sees the loop change course in response to something it observed — not just repeat.

### Essential (present in any non-trivial agent)
- **LO-4 Perception.** A value enters the program **from outside the source code** (a file, an
  API, stdin, a tool result) and becomes part of the prompt or the predicate at run-time.
- **LO-5 Planning & decomposition.** A hard task is split into a sequence *before* acting,
  via a **validated structured plan** (a schema, not free prose).
- **LO-6 Memory.** State persists across steps. The learner sees the two kinds kept **separate**:
  *SDK session memory* (within-run conversation) vs *application memory* (across runs, on disk).
- **LO-7 Tool selection & use.** The model **chooses** which tool and when — selection visible
  in the message log, not dictated by a Python `if`-ladder.

### Enhancing (maturity)
- **LO-8 Sequential action-taking.** Each step's output is the next step's input (chaining),
  with the **dependency** explicit.
- **LO-9 Termination criterion.** The loop has a principled stop: **goal met** *or* a
  **circuit breaker** (max-iteration / budget / timeout). It can never spin forever.

### Cross-cutting (the course teaches these alongside the traits — capture them too)
- **LO-10 Independent verification.** Correctness is judged by something **other than the
  actor** — a deterministic predicate or a separate adversarial critic call.
- **LO-11 Context engineering.** The conversation history a loop accumulates is **bounded**
  (compaction / sliding window), or cost and "context rot" grow without limit.
- **LO-12 Failure handling.** Failures are **classified** (transient / structural / policy)
  and **routed** (retry / re-plan / escalate-to-human), not blanket-retried.
- **LO-13 Trust boundary.** Anything ingested from the outside world is **data, not
  instructions** (prompt-injection defense). Tools absorb transient infra failure so the
  reasoning layer never sees it.
- **LO-14 Observability.** Every tool call leaves a structured audit record (a span trace,
  not a flat list of names) so the agent's behaviour is inspectable after the fact.

---

## 3. The Agency Gates — true agent vs. masqueraded workflow

The go/no-go test before any agent is accepted. **All three Core gates must pass.** These
operationalize the project's 5-question classifier.

| Gate | Pass criterion (must be demonstrable in code) | Fails when… |
|---|---|---|
| **G1 — Goal is a predicate** | There exists a `goal_met(state) -> bool` (or equivalent) the loop calls. The verdict is computed, not narrated by the model. | "Success" is just the model saying it's done. No code-side check. |
| **G2 — The model owns a real decision** | At least one branch (next tool, next step, repair strategy) is chosen by the model at run-time and is observable in the message log. | Every route is a Python `[i]`, `if phase==`, or fixed call sequence. |
| **G3 — Closed observe→reason→act loop** | The agent reads a tool result / outcome and a *subsequent* action demonstrably differs because of it. | The "loop" repeats identical work; outcomes don't feed back into choices. |
| **G4 — Principled termination** (Enhancing, required here) | Exit on goal-predicate **and** a hard cap/budget/timeout. Both paths reachable. | Only one exit, or an unbounded `while True`. |
| **G5 — Verification is independent** (Enhancing, required here) | Pass/fail decided by a deterministic predicate or a **separate** critic call with fresh context. | The actor grades its own work. |

**Honesty rule (inherited from CLAUDE.md):** if G1–G3 don't all pass, the artifact is a
**workflow**. Say so plainly, then propose the *minimal* change that would flip the failing
gate — usually "move the next-step choice from Python into a model tool call" or "replace the
hard-coded `[0]` with a model-emitted selection."

---

## 4. Code-annotation mandate — what every generated `main.py` must surface

The gates in §3 are only credible if the code *shows its work*. The Foundry must enforce all
of the following in generated agents (this extends CLAUDE.md's annotation standard):

1. **Trait table in the module docstring** — `AGENTIC TRAITS DEMONSTRATED`: trait → function/line →
   one-line plain-English why. (Already in CLAUDE.md.)
2. **Inline `# TRAIT[...]` markers** at the *exact* line each trait fires. (Already in CLAUDE.md.)
3. **`# GATE[Gn]:` markers** at the line that satisfies each Agency Gate — so a reviewer can
   grep `GATE\[` and find the predicate, the model-owned decision, the feedback edge, the
   circuit breaker, and the independent verifier. **New — this is the provability layer.**
4. **`# GOTCHA[...]:` guard comments** at any line that *would* have been a §5 trap, naming the
   trap avoided (e.g. `# GOTCHA[control-plane]: the model selects the step here, not Python`).
5. **A visible decision log.** The model's tool/step choices print to console (a `MessageLens`
   one-liner per message) so autonomy (G2) and the feedback loop (G3) are watchable in one run.
6. **The termination reason, printed on exit** — `GOAL MET` vs `EXIT: cap reached` vs
   `ESCALATED` — never a silent stop.
7. **The two memories labelled** where they live — session vs application — so LO-6 isn't blurred.

> Grep contract for the Foundry's QA loop: a generated `main.py` should yield
> `TRAIT[` ≥ 5, `GATE[` ≥ 5 (G1–G5), and at least one `GOTCHA[` guard. Zero is a red flag that
> the agent is a workflow with good comments.

---

## 5. Gotchas — where the code lies and where learning goes wrong

Each is drawn from a real trap in the course. For each: the trap, the tell, the fix.

### 5.1 The bare call mistaken for an agent *(Ch 1)*
- **Trap:** wrapping a single `query()` in a nice CLI and calling it an agent.
- **Tell:** zero traits — no goal predicate, no loop, no perception, no decision.
- **Fix / lesson:** a bare call is a **stateless function**. Count the traits; if it's zero,
  it's a function, not an agent. Don't let polish substitute for structure.

### 5.2 The goal that lives only in the prompt — and the plumbing that fakes failure *(Ch 2)*
- **Trap A:** telling the model the goal but never checking it in code. The model "decides"
  success. → **verifier must be independent of the model.**
- **Trap B (the subtle one):** the predicate runs against the **wrong bytes**. In the course,
  the script concatenated the *entire message stream* (`str(message)`) — hook events, system
  init, everything — and ran the regex on 50 KB of noise. The model returned the right answer;
  the goal-check still said `GOAL MISSED`.
- **Tell:** "the model is broken" complaints that are actually extraction/parsing bugs. The
  model did fine; the wire between model and predicate was wrong.
- **Fix / lesson:** extract **only** the assistant's text before judging. ~80% of "the LLM
  failed" bugs live in this gap between output and predicate. **Mind the plumbing.**

### 5.3 Chaining mistaken for agency — the `[0]` trap *(Ch 3)*
- **Trap:** two LLM calls where call B's input is built from call A's output (a real chain),
  then `plan["steps"][0]` — **Python** reaches in and picks the step.
- **Tell:** the next-step choice is a literal index or a fixed sequence. Reorder-proof = not autonomous.
- **Fix / lesson:** chaining is `output_A → input_B` with a hard dependency — useful, but
  **the control flow is still bolted into Python.** This is a *workflow*. To cross into agency,
  the model must choose the step (G2). Most "AI agents" shipping today are this.

### 5.4 The loop that Python owns — line-63 gotcha *(Ch 4)*
- **Trap:** `for iteration in range(max_iterations):` — the loop exists, but **Python owns the
  counter and the continue/stop decision.** The model is just called repeatedly.
- **Tell:** the loop's continuation isn't driven by an observed outcome; it's a fixed range.
- **Fix / lesson:** iteration ≠ agency by itself. The loop becomes *agentic* only when the
  **goal predicate is the exit condition** (the Ch 2 verifier, now the `while` condition) **and**
  the model's observations change the next action (G3). Two more traps cluster here:
  - **No circuit breaker** → an unreachable goal loops forever and eats the rate-limit window.
    Always pair the goal-exit with a max-iteration/budget cap (G4).
  - **Unbounded context** → history grows every iteration; cost climbs linearly and the model
    fixates on its earlier wrong answers ("context rot"). Apply **compaction / sliding window**
    (LO-11). The course makes this a *number you can watch* (token estimate per iteration), not a vibe.

### 5.5 The loose schema that undercuts its own lesson *(Ch 6)*
- **Trap:** a "structured plan" tool declared as `{"steps": list}` — no inner validation. It
  *looks* like planning discipline but accepts any garbage.
- **Tell:** the schema validates the outer shape only; malformed steps pass.
- **Fix / lesson:** a **tight schema validates the full inner shape** (enum actions, non-empty
  targets, required `expected_outcome`) and **rejects** malformed input with a structured error.
  That rejection is an **inline tutor** — the model reads the error and fixes its plan mid-thought.
  Validation is pedagogy, not just a guardrail.

### 5.6 Rich vs. sparse tool descriptions *(Ch 5)*
- **Trap:** terse tool descriptions ("reads a file") force the model to **guess** what the
  sensor sees → more probing turns, wrong file types, wasted iterations.
- **Tell:** high turn-counts on simple perception tasks.
- **Fix / lesson:** a tool description is part of the prompt. Rich descriptions measurably
  **cut turn-count**. The course proves it by running both and printing the delta.

### 5.7 The self-grading actor *(Ch 9)*
- **Trap:** asking the same model, same context, "did you do well?" It says yes.
- **Tell:** verification shares the actor's context or persona.
- **Fix / lesson:** the critic is a **separate call, fresh context, adversarial system prompt,
  default-skeptical**, returning structured `{accept, confidence, critique}`. **Calibrate it on
  known-bad outputs before trusting its accepts** — an uncalibrated critic that rubber-stamps is
  worse than none.

### 5.8 Dead-code "robustness" *(Ch 10)*
- **Trap:** defining a `classify_failure()` (transient/structural/policy) — then never calling
  it; only a happy-path retry runs. The headline capability is decorative.
- **Tell:** branches that no clean run can reach; failure classes that never fire.
- **Fix / lesson:** **every branch must be reachable and exercised.** Wire the classifier into
  the loop: route transient→retry-with-budget, structural→re-plan-with-context,
  policy→escalate-to-human; apply the promotion rule (K retries ⇒ reclassify as structural).
  If a smoke test can't trigger a branch, that branch is a lie.

### 5.9 Untrusted text treated as instructions *(Ch 7, 13)*
- **Trap:** text fetched from the world (a web page, a file, a tool result) flows into the
  prompt as if it were a command the model should obey → prompt injection.
- **Tell:** ingested content and model instructions share the same channel with no fencing.
- **Fix / lesson:** mark outside text as **data, not control** (CDATA-style / backtick fencing).
  Enforce *acting* under permission via **hooks**: PreToolUse Guard (allow/deny on a path
  invariant), PreToolUse Mutate (clean input first), PostToolUse Observe (audit, fire-and-forget).
  Hook order matters: Mutate → Guard → execute → Observe.

### 5.10 The audit trail that isn't *(Ch 8)*
- **Trap:** "observability" = a flat `list[str]` of tool names. Useless for diagnosis.
- **Fix / lesson:** emit a **span trace** (id, parent_id, tool, start, duration, result summary)
  as JSONL; parent_id from a span stack pushed in PreToolUse / popped in PostToolUse, so nested
  calls form a tree. Use counters (not wall-clocks) in teaching code for reproducibility.

### 5.11 Meta-gotcha — the claim that lives only in prose
- **Trap (visible across the course's own revision notes):** a chapter *asserts* an agentic
  effect the code never makes visible — single happy-path run, effect unfalsifiable, the lesson
  survives only in comments.
- **Fix / lesson:** **make the agentic effect a number or an artifact you can see in one run**
  (turn-count delta, token-growth column, span tree, a reachable REJECT/escalate branch). If the
  learner can't observe it executing, they didn't learn it — they read about it.

---

## 6. Course-chapter → trait/gate map (for cross-reference)

| Course chapter | Primary trait(s) | Gate(s) stressed | Headline gotcha |
|---|---|---|---|
| 1 Bare LLM | (none — baseline) | — | §5.1 polish ≠ agency |
| 2 Goal | Goal-directedness, Verification | G1, G5 | §5.2 prompt-only goal / plumbing |
| 3 Chained | Sequential action | (exposes G2 failure) | §5.3 the `[0]` trap |
| 4 Iteration | Observe-reason-act, Termination, Context eng. | G3, G4 | §5.4 line-63 / runaway / context rot |
| 5 Perceive | Perception, Tool use | — | §5.6 sparse tool descriptions |
| 6 Reason | Planning & decomposition | — | §5.5 loose schema |
| 7 Act | Tool use under permission | (G2 via hooks) | §5.9 hooks & trust boundary |
| 8 Integration | All five core+essential together | G1–G4 | §5.10 fake audit trail |
| 9 Verifier | Independent verification | G5 | §5.7 self-grading actor |
| 10 Recovery | Failure handling, HITL | G4 | §5.8 dead-code dispatcher |
| 11 Resume / Two-agent | Memory (session vs app) | — | session/app memory conflation (LO-6) |
| 12 Orchestrator | Autonomy, decomposition, routing | G2, G3 | decisions-before-model-call; system prompt = score |
| 13 Production | Trust boundary, resilience | G5 | §5.9 injection; transient-failure absorption |

---

## 7. Recommendations — what else to capture (evaluated)

These extend the spec where the learning objective would otherwise have blind spots. Tied to
the trait/SDK concept each reinforces.

| # | Recommendation | Why it matters / what it teaches | Priority |
|---|---|---|---|
| R1 | **Bake the §3 gates into the Foundry's scorecard as pass/fail rows**, alongside the 9-trait score. | Forces the agent/workflow verdict to be mechanical, not vibes. Directly serves PRD S1, S7. | **High** |
| R2 | **`GATE[Gn]` grep contract in the QA loop** (≥5 gate markers + the trait grep). | Makes "is it an agent" provable by a script, not a human read. Extends FR-C2 / S2. | **High** |
| R3 | **Workflow→agent diff in the README** of any generated agent that starts as a workflow. | Captures the *minimal agentic fix* as a teaching artifact — the most instructive moment. | High |
| R4 | **A deliberate "control-plane" callout per agent**: one sentence naming who owns the next decision. | Cements the §1 spine — the single most-misunderstood idea. | High |
| R5 | **Reachability assertion in every smoke test**: each failure/escalate/reject branch fires at least once (seeded fixtures). | Kills §5.8 dead-code robustness. Extends FR-C4/FR-D. | Med |
| R6 | **A one-run "effect-is-visible" check** per trait (a number or artifact printed), per §5.11. | Prevents prose-only learning; aligns with the course's v3 design discipline. | Med |
| R7 | **Cost/usage surfaced per run** (`usage`, `total_cost_usd`) — already in PRD §11; reaffirm as a learning surface. | Termination & budget (G4) become tangible; ties to the post-2026-06-15 Agent SDK credit note. | Med |
| R8 | **A "negative control" exercise**: ship one *intentional workflow* and have the learner run the gates and watch them fail. | The fastest way to internalize §3 is to see a red verdict on purpose. | Med |
| R9 | **Calibration step for any critic** (§5.7): run known-bad inputs, confirm rejects, before trusting accepts. | An uncalibrated verifier is a false sense of safety. Extends G5. | Med |
| R10 | **Context-budget column** in any multi-iteration agent (token estimate per loop). | Makes §5.4 context rot observable; reinforces LO-11. | Low |

---

*End of spec. This file is descriptive of the course and prescriptive for the Foundry; if a
generated agent cannot pass §3 and surface §4, label it a workflow and propose the minimal fix —
that honesty is itself the lesson.*
