# PRD — Agent Foundry v9 (FINAL)

**Status:** v9 FINAL — lock-ready
**Date:** 2026-06-07
**Owner:** Ram | **Author:** Claude | **Reviewers:** Claude (adversarial), OpenAI (external), Senior Product Manager persona (traceability), Ram (architecture)

**Changelog v6 → v7:** added §0 Mission & Conception (self-contained purpose, delivery
model, and decision log so any future build can start from this document alone); restored
three approved-but-dropped requirements found by the SPM traceability review — briefing
aesthetic standard (FR-C5), generated-agent web-API permission (§7.2), learner-preference
registry field (FR-E1); added HANDOFF.md session-continuity requirement (FR-E3);
CLAUDE.md synced to the five-file contract.

**Changelog v5 → v6:** added the **Professor Persona** (Phase F): a skippable ~10-minute
interactive teaching session in Claude Desktop after each delivery — opening/core/probe/
handoff shape, 2-attempt Socratic repair, probes anchored to real briefing sections and
code lines, one `professor_notes` registry field enabling a single recall question next
cycle. LMS machinery (student models, rubrics, tiers, scoring) explicitly excluded.
Patterns selectively adopted from `Master-Guide-to-Create-Learning-Applications_v3.md`.

**Changelog v4 → v5 (ARCHITECTURE CHANGE):** the Foundry is no longer a Python console
app. **Claude Desktop (Cowork) is the Foundry.** Brainstorming, candidate scoring, lock,
code generation, and pre-delivery QA all happen in the Claude Desktop chat with project-
folder access. PyCharm is exclusively where the student reads and runs **generated agents**.
The SDK learning curriculum relocates from the Foundry's own code into a **concept ladder
across generated agents** (§7). Gates annex, five-file contract, briefing.html, and the
grep contract survive unchanged. Prior changelogs retained at end of file.

---

## 0. Mission & Conception *(self-contained — read this first on any future build)*

### Mission statement
Give Ram a **practical, code-level understanding of AI agents** by manufacturing them:
every cycle turns one brainstormed daily-life idea into a runnable, exhaustively annotated
Python agent whose agency is *provable from its code* — and the manufacturing process
itself (brainstorm → gate → generate → test → repair → teach) is the first live
demonstration of every concept being taught.

### Purpose & goals
- **Primary goal (student):** Ram can read any generated agent and point to the exact
  line where each agentic trait and Agency Gate fires; over successive cycles he climbs
  a ladder of Claude Agent SDK concepts until he can design agents unaided.
- **Secondary goal (consulting IP):** the artifacts — trait framework, gates annex,
  briefings, annotated agents — accumulate into reusable intellectual property at the
  AI + consulting-strategy intersection.
- **Non-purpose:** this is not a product for others, not a SaaS, not a course platform.
  One student, one machine, learning by building.

### How it was conceived
Conceived in a single working session (2026-06-07) through interrogative brainstorming
between Ram and Claude, hardened by three independent reviews (OpenAI external review;
Claude adversarial review; Senior Product Manager persona traceability review) and two
of Ram's own authored specs: `agent_traits_chef_guide_v2.html` (the 9-trait teaching
framework) and `AGENT_LEARNING_AND_AGENCY_GATES.md` (the binding acceptance annex,
distilled from his Agents Master Course). The project began as a planned PyCharm
console application ("Foundry app", v1–v4) and pivoted at v5 to the simpler, truer
architecture below.

### How it is delivered (the operating model)
**Claude Desktop (Cowork) is the Foundry.** There is no Foundry software. Each cycle:
Ram says "new agent" in this project → Claude brainstorms interactively (trait scorecard
+ G1–G5 gate verdict per candidate) → Ram types an explicit lock → Claude generates the
eight-file agent folder and QA-repairs it in its sandbox until green → a short Professor
conversation verifies Ram's understanding → Ram reads `<agent-slug>_learning-guide.html`
(Part 1) → Ram opens the folder in **PyCharm** and runs `main.py` → the run auto-saves
`<agent-slug>_run_output.log` → Claude generates `<agent-slug>_learning-insights.html`
(Part 2) from that log → Ram reads Part 2 for post-run reinforcement.
Memory between cycles lives in `foundry_registry.json`, `ROADMAP.md`, and `HANDOFF.md` —
not in chat history.

### Decision log (binding; do not silently re-decide)
| # | Decision | Rationale |
|---|---|---|
| D1 | Auth = Claude Max subscription via `claude` CLI login; **never** `ANTHROPIC_API_KEY` | Ram's plan; key detected → warn, strip from child env only |
| D2 | Stack = `claude-agent-sdk` + stdlib; no LangChain/CrewAI/AutoGen | The SDK *is* the curriculum |
| D3 | Teaching lens = 9-trait/3-tier chef-guide framework | Ram's authored framework |
| D4 | Acceptance authority = Agency Gates G1–G5 (annex); G1–G3 all-or-workflow; G4–G5 required at code time | Agency must be provable, not asserted |
| D5 | Architecture = Model B: Claude Desktop is the Foundry; PyCharm only runs generated agents (chosen over PyCharm Foundry app and hybrid) | Matches Ram's actual UX; agents are the study material |
| D6 | Brainstorm = Claude-driven adaptive Q&A; daily-life scope; nothing written before a typed lock | Learning project, not corporate tooling |
| D7 | QA = auto-repair until green, max 3 attempts, narrated; smoke tests mock the LLM | Protects quota; clean failure signal; honest delivery |
| D8 | Eight files per agent incl. two paired HTML learning artifacts: `<agent-slug>_learning-guide.html` (Part 1, 13 sections, pre-code, chef-guide aesthetic) + `<agent-slug>_learning-insights.html` (Part 2, 11 sections, post-run, evidence-based); also `<agent-slug>_run_output.log` (tee of stdout) | Pre-code comprehension (Part 1) + post-run reinforcement (Part 2) form a complete learning cycle |
| D9 | Grep contract: `TRAIT[`≥5, `GATE[`≥5, `GOTCHA[`≥1 + branch reachability + assistant-text-only predicates | Annotations are acceptance criteria |
| D10 | SDK concept ladder: each new agent introduces ≥1 new SDK rung (8 rungs defined) | Replaces the SDK learning lost in the v5 pivot |
| D11 | Professor session: light-touch 4-part conversation, 2-attempt Socratic repair, one registry field; **no LMS machinery ever** (no student models, rubrics, tiers, scores) | Ram's explicit anti-overcomplication mandate |
| D12 | Generated agents non-interactive by default; bounded HITL tool only when that's the trait being taught | Ram's explicit choice; protects autonomy trait |
| D13 | Generated agents may call **free public web APIs** for perception; writes sandboxed to own folder; external text fenced as data (LO-13) | Ram-approved guardrail set |
| D14 | Agents fully self-contained — no shared `common/` | Legibility beats DRY in a teaching codebase |
| D15 | Rejected permanently: nonexistent `permission_mode="dontAsk"`; LMS features; PyCharm Foundry app (capstone non-commitment only) | Documented so future builds don't relitigate |
| D16 | Learner profile seed: domains = morning-briefing / health-habits / learning-research; focus trait = observe–reason–act feedback loop; first build minimal | Ram's brainstorm answers, cycle-1 starting point |
| D17 | Brainstorm session log added to registry (`brainstorm_sessions[]`): every session records proposals + decisions + reasons, whether or not a lock happens | Prevents repeat proposals; feeds INSIGHTS.md brainstorm history; cold Claude sessions re-use prior session data |
| D18 | `INSIGHTS.md` at project root: Claude-authored human-readable synthesis (6 sections), regenerated each cycle, read at every session start | Accumulates learning arc across cycles; informs brainstorm seeding; gives Ram a single glance-view of progress. NOT an LMS artifact — no scores, rubrics, or tiers |
| D19 | Runtime output standard (FR-C8) + `prompt.md` blueprint (FR-C7) mandated for all generated agents; `═══` comment header format added alongside existing `TRAIT[]/GATE[]/GOTCHA[]` inline markers | The runtime output makes every trait/gate visible at execution time — it is the runtime equivalent of code annotations; `prompt.md` ensures cold-session reproducibility; model: macbook_agent_prompt.md + agent_test_code.py (existing reference artifacts) |
| D21 | Two paired HTML learning artifacts per agent: `<agent-slug>_learning-guide.html` (Part 1, renamed from `briefing.html`) + `<agent-slug>_learning-insights.html` (Part 2, new); `main.py` tees stdout to `<agent-slug>_run_output.log` as Part 2 input; fallback = user pastes terminal output | Part 1 is forward-looking explanation; Part 2 is backward-confirming evidence from execution — together they complete the learning cycle; the log-tee makes Part 2 generation reproducible without manual copy-paste |
| D20 | FR-C8 extended from 15 to 24 runtime output elements: SDK call boundary brackets `[SDK →]/[← SDK]`, `[GOAL PREDICATE]` per-iteration evaluation, `[MODEL DECISION]` at tool selection, `[LOOP FEEDBACK]` delta per iteration, `[CONTEXT]` token tracker, session vs. application memory labels, `[ERROR]` classification, `[TRUST FENCE]` for external content, `[PLAN PROGRESS]` live board. FR-D4 grep contract extended to cover the 8 new mandatory elements. | Gap analysis found that G1/G2/G3 gate evidence, context growth (LO-11), memory type distinction (LO-6), failure routing (LO-12), and the Python↔LLM boundary were invisible in the original 15 elements — a student could watch the agent run without being able to prove agency from the output |

---

## 1. Overview & Learning Objectives

Agent Foundry is a **working method, not an app**: a Claude Desktop (Cowork) project that
turns agent ideas into runnable, annotated Python learning agents.

**The user journey (one cycle):**
1. Ram opens this project in Claude Desktop and says "new agent" (or brings an idea).
2. Claude brainstorms interactively — structured questions, daily-life candidates, a
   9-trait scorecard and G1–G5 gate verdict per candidate (annex-governed).
3. Ram **locks** a candidate (explicit approval; nothing written before it).
4. Claude generates the agent into `/<use-case-slug>/` — eight files including
   `<agent-slug>_learning-guide.html` (Part 1) — and **QA-tests its own output before
   delivery**: smoke test run in the sandbox (LLM mocked), grep contract verified,
   repairs applied until green.
5. Claude opens a short **Professor session** (skippable) — an interactive walkthrough
   of what this agent is, its control plane, and its key traits, with comprehension
   probes — before any offline reading.
6. Ram double-clicks `<agent-slug>_learning-guide.html` (Part 1), reads it (≤10 min),
   passes the MCQ self-check.
7. Ram opens the folder in PyCharm and runs `main.py` on his Claude Max plan. The run
   auto-saves `<agent-slug>_run_output.log` via the tee context manager.
8. Claude reads the log (or Ram pastes terminal output as fallback) and generates
   `<agent-slug>_learning-insights.html` (Part 2). Ram reads Part 2 to confirm and
   reinforce understanding of what they just witnessed.

**Learning objectives (priority order):**
1. Watch the **observe–reason–act feedback loop** fire for real — inside each generated
   agent's code, and visibly in Claude's QA-repair narration before delivery.
2. Learn the **Claude Agent SDK hands-on through the generated agents**: each new agent
   introduces at least one new SDK concept (the concept ladder, §7).
3. Internalize the 9-trait framework and Agency Gates by seeing them used as *gates*,
   not posters.

## 2. The Trait Framework & Acceptance Authority

Source: `agent_traits_chef_guide_v2.html`. Nine traits, three tiers:

| # | Trait | Tier |
|---|-------|------|
| 1 | Goal-directedness | **Core** |
| 2 | Perception | Essential |
| 3 | Planning & decomposition | Essential |
| 4 | Memory | Essential |
| 5 | Tool selection & use | Essential |
| 6 | Sequential action-taking | Enhancing |
| 7 | Autonomy | **Core** |
| 8 | Observe–reason–act loop | **Core** |
| 9 | Termination criterion | Enhancing |

**Acceptance authority:** `AGENT_LEARNING_AND_AGENCY_GATES.md` is the binding acceptance
annex. Gates G1–G5 (annex §3) are the **pass/fail authority** for accepting generated
code; the 9 traits are the **teaching lens**; the 5-question classifier is the
**brainstorm-stage instrument**. G1 (goal is a predicate), G2 (model owns a real
decision), G3 (closed observe→reason→act loop) must all pass or the artifact is labelled
a workflow with a minimal-fix proposal. G4 (principled termination) and G5 (independent
verification) are required at code acceptance despite their Enhancing tier.

A candidate missing any Core trait is a workflow, not an agent → Claude says so and
proposes the minimal agentic fix. CLAUDE.md carries the same framework (single source
of truth).

## 3. Where the Agency Lives (Model B)

| Layer | Role | Agentic? |
|---|---|---|
| **Claude Desktop (the Foundry)** | Brainstorm, score, gate, generate, QA-repair, registry upkeep | Yes — but its agency is *demonstrated in conversation*, not studied as code |
| **Generated agents (PyCharm)** | The study material: every trait and gate provable in their Python | Yes — this is where the learning happens |

The generated agents are the curriculum. Claude's own loop (generate → test → repair)
is narrated live in chat so Ram watches a feedback loop work before reading one.

## 4. User Stories

1. As Ram, I say "new agent" in Claude Desktop and am interviewed — short, adaptive
   questions — until a shortlist of daily-life candidates emerges with trait scores and
   G1–G5 verdicts.
2. As Ram, I see honest verdicts (workflow / borderline / agentic) and must type an
   explicit lock before any file is written.
3. As Ram, I watch Claude generate the code, run its smoke test in the sandbox, and
   repair failures — narrated, with the grep contract checked — before it's handed over.
4. As Ram, I double-click `<agent-slug>_learning-guide.html` (Part 1), read it (≤10 min),
   pass the MCQ self-check, and know which file and function to read first.
4b. As Ram, after running the agent I double-click `<agent-slug>_learning-insights.html`
   (Part 2) and see visual proof — from the actual runtime output — of why the agent was
   an agent, how each trait fired, and where it sits in the broader spectrum. The flashcards
   and MCQ reinforce what I witnessed. The brainstorm seeds show me what to build next.
5. As Ram, I open the folder in PyCharm and run `main.py` immediately on my Max plan.
6. As Ram, in later sessions Claude remembers what was built (registry + ROADMAP.md)
   and steers brainstorming away from repeats; each new agent climbs the SDK ladder.
7. As Ram, right after delivery the Professor walks me through what this agent is and
   probes whether I've understood — pushing back Socratically when I'm wrong, pointing
   me to the exact briefing section or code line — so I arrive at PyCharm already
   oriented. Next cycle, it opens with one recall question on my weakest concept.

## 5. Functional Requirements

### Phase A — Brainstorm (in Claude Desktop chat)
- FR-A1: Interactive Q&A using structured questions; Claude adapts each round to prior
  answers. Daily-life scope; Claude proposes, Ram disposes. For every candidate, Claude
  computes and displays a **Learning Position label** before the gate verdict:
  - `FORWARD` — introduces ≥1 new SDK rung or trait not exercised by any prior agent.
    Recommend by default; surface at least one FORWARD candidate per session.
  - `LATERAL-RIGHT` — same SDK rungs, new domain. Breadth run.
  - `LATERAL-LEFT` — same rungs, same or similar domain. Consolidation run.
  - `FOUNDATIONAL` — targets a concept in the latest agent's `learning.gaps[]`. Repair run.
    Overrides LATERAL-LEFT when gaps exist.
  - `DIAGNOSTIC` — deliberately fails G1 or G3; offered every 2–3 cycles so Ram practises
    gate rejection. Presented last; labeled clearly as a workflow on purpose.
  **Diversity check:** for each candidate compute structural similarity
  `score = (domain_overlap × 0.4) + (rung_overlap_fraction × 0.4) + (trait_overlap × 0.2)`;
  if score > 0.7 and not FORWARD, flag with `(HIGH SIMILARITY — mostly review)`.
  **LO-12 coverage trigger:** if no prior agent has produced a `[ERROR: STRUCTURAL]` or
  `[ERROR: POLICY]` output element, steer at least one candidate toward a domain where tool
  failure is natural (e.g. web API with strict rate limits, ambiguous task requiring escalation)
  and note this in the candidate's scorecard.
  Student-facing label for each candidate: one sentence naming the specific rung it unlocks
  or the gap it repairs (e.g. "Introduces custom tools — SDK rung 4, your learning frontier").
- FR-A2: Each candidate gets a 9-trait scorecard, classifier verdict, **and a G1–G5
  pass/fail row per Agency Gate**.
- FR-A3: Honesty rule: workflows are called workflows, with the minimal agentic fix.
  **DIAGNOSTIC slot:** every 2–3 cycles, Claude also offers one candidate explicitly designed
  to fail G1 or G3. Purpose: Ram practises gate-rejection against real, plausible code rather
  than toy examples. The DIAGNOSTIC candidate is always presented after genuine candidates;
  its failure mode is stated before Ram locks. Ram may lock a DIAGNOSTIC candidate to build a
  deliberate "workflow" and then extend it to meet the gates — this is a valid learning cycle.
- FR-A4: Claude checks `foundry_registry.json` + ROADMAP.md first; no repeat candidates
  unless Ram asks for an iteration on an existing agent.
- FR-A5: **Brainstorm routing question** — before any Q&A, Claude asks whether Ram wants
  proposed candidates or has an idea ready. Three options: (A) propose candidates (default),
  (B) describe idea directly, (C) provide a file path. Options B and C, plus the `Others:`
  mid-session trigger phrase, activate the **Others shortcut**:
  - Trigger: Ram types `Others: <description or absolute file path>` at any point during
    brainstorm Q&A *or* Phase 0 Part B interrogation. Also fires on routing option B or C.
  - **File path branch:** Claude reads the file and extracts the candidate intent. The file
    may be any plain-text or markdown document describing the desired agent. It does not need
    to follow `prompt.md` format.
  - **Free-text branch:** the description after the colon is treated as the candidate spec.
  - **Gate check (silent):** Claude runs G1–G5 verdicts and computes the Learning Position
    label from the supplied spec without Q&A. Gate failures are surfaced explicitly before
    the mini-spec is shown — never suppressed.
  - **Learning Position display:** the inferred label (FORWARD / FOUNDATIONAL / etc.) is
    shown prominently in the mini-spec with an invitation to correct if wrong.
  - **Registry log:** append to `brainstorm_sessions[]` with `decision: "others-shortcut"`
    and `source: "free-text"` or `source: "file:<path>"` as applicable.
  - **Proceed to step 3** (mini-spec + confirmation) directly. The normal brainstorm Q&A
    and step 2 (log) are replaced by this abbreviated path; the log write happens here.
  - **Phase 0 edge case:** if `Others:` fires during Phase 0 Part B, Part A is already
    complete and is not repeated. Part B stops at the current question.

### Phase B — Lock gate (human approval)
- FR-B1: Explicit lock required ("lock <candidate>"); zero file writes before it.
- FR-B2: On lock, Claude shows a one-page mini-spec (goal predicate, tools, memory,
  loop, termination, trait/gate map, SDK concepts introduced) for second confirmation.

### Phase C — Code generation (by Claude, into the project folder)
- FR-C1: Generate into `/agents/<use-case-slug>/` — **eight** mandated files: `prompt.md`,
  `main.py`, `smoke_test.py`, `requirements.txt`, `README.md`,
  `<agent-slug>_learning-guide.html` (Part 1), `<agent-slug>_run_output.log` (created on
  first run), `<agent-slug>_learning-insights.html` (Part 2, generated after first run).
  Plus `agent.py` if main exceeds ~150 lines. Project folders: `agents/` (generated work),
  `reference/` (chef guide + master guide copies — self-containment), `reviews/`, `prompts/`.
- FR-C2: Generated code carries the AGENTIC TRAITS docstring table; inline `# TRAIT[...]`
  markers; `# GATE[Gn]:` markers at each gate-satisfying line; `# GOTCHA[...]:` guards
  naming avoided annex-§5 traps; a one-sentence control-plane statement in the docstring;
  a printed termination reason on every exit (`GOAL MET` / `EXIT: cap reached` /
  `ESCALATED`); session-vs-application memory labelled where each lives. Feynman order
  throughout.
- FR-C3: Generated agents authenticate via `claude-agent-sdk` → Claude Code CLI →
  **Max plan subscription login**; never an API key (§7.4).
- FR-C4: Generated `smoke_test.py` mocks the LLM boundary; one optional live-call
  verification runs once, after green, on Ram's machine with his confirmation.
- FR-C5: **`<agent-slug>_learning-guide.html`** (Part 1, pre-code, **lay-first per FR-C10**) —
  single self-contained static HTML (inline CSS; vanilla JS only for MCQ reveal + navigation;
  no CDN/framework/build; offline double-click). **Beautifully made**: typographic care,
  generous whitespace, color-coded callouts — in the visual spirit of
  `agent_traits_chef_guide_v2.html` — a reading document Ram *wants* to read, not a rendered
  README. Generated before code runs. Sections 4, 5, and 10 are deeper-dive sidebars (FR-C10
  §2) — clearly marked optional and skippable without losing comprehension of the body.
  Mandatory sections in order:
  1. **What this agent is for** — use case + objective in plain English. Names what the
     agent does, not what its code looks like.
  2. **How this agent thinks** — agent-loop SVG with non-coder stage names (Wake up → Plan
     → Try → Look → Try again → Stop) tailored to this specific agent's steps.
  3. **What makes this an "agent" (in plain English)** — high-level trait summary using
     functional aliases (FR-C10 §3), not gate codes. One short paragraph per Core trait.
  4. *Deeper dive — Where each trait lives in the code* (optional, sidebar-styled) —
     trait-to-code map with file:line anchors. Marked clearly as skippable.
  5. *Deeper dive — Reading the code* (optional, sidebar-styled) — code-block arrangement
     and guided reading order. Begins with a ≤10-line "Python Reading Primer" defining
     `def` / `while` / `for` / `if/else` / `print()` / `async/await` for *recognition only*,
     not authoring (the only Python prerequisite for following the guided order).
  6. **What to expect when you run it** — PyCharm run steps + ~10-line annotated expected
     output, with each line glossed in plain English.
  7. **Things worth noticing during the run** — learning insights. **Always includes:**
     (a) one plain-English sentence that this agent's LLM calls start fresh each time —
     "the agent doesn't remember what it asked the LLM in the previous step" — and one
     sentence naming the future capability that will change that;
     (b) one sentence noting that `<agent-slug>_run_output.log` accumulates every run and
     will enable cross-cycle comparison in later cycles.
  8. **Watch out for these** — gotchas (≤5, drawn from annex §5, matching the agent's
     `GOTCHA[...]` lines). Each gotcha named in plain English. For rung 1–2 agents,
     **always include the standing note** that `[PLAN REVISED]` does not fire here because
     the plan is simple and linear, and students will first see it in cycle 3.
  9. **Who's making the decisions** — control plane in plain English. Names who or what
     owns each branching choice (code? model? Ram?). Workflow→agent diff when applicable.
  10. *Deeper dive — SDK glossary* (optional, sidebar-styled, end-positioned) — appears
      at the very end, marked clearly as skippable.
  11. **A few self-check questions** — 3–5 MCQ inline-reveal with one-line explanations.
      Questions phrased functionally (e.g., "Did the agent know when to stop?"), never in
      gate-code vocabulary.
  12. **Before you hit Run** — takeaway + ready-gate checklist in plain English.
  13. **Provenance footer** — agent slug, generation date, SDK rung introduced, file
      pointers, version stamps. Technical content permitted in this footer.
  ≤10-minute read; no code excerpts beyond 10 lines. **Boundary rule:** README = mechanics;
  learning-guide = why this is an agent and what to expect (lay, forward-looking);
  learning-insights = proof from execution (lay, backward-confirming). No content
  duplication across the three; one-line cross-references permitted.
- FR-C6: Three-file boundary rule: README = how to run (mechanics only); learning-guide =
  why it's an agent and what to learn (forward-looking, pre-run); learning-insights = proof
  from execution (backward-confirming, post-run). No content duplication across the three.
  One-line cross-references permitted.
- FR-C9: **`<agent-slug>_learning-insights.html`** (Part 2, post-run, **lay-first per FR-C10**) —
  single self-contained static HTML (inline CSS; vanilla JS for flip-cards + MCQ reveal; no
  CDN; offline double-click). Generated **after** `main.py` runs, using
  `<agent-slug>_run_output.log` as primary input (fallback: user pastes terminal output).
  Same visual quality standard as Part 1. Never generated before the first run; never
  duplicates Part 1 content. **Sections 4 and 7 retain their current titles and intent
  verbatim — Ram's audit found them well-implemented.** All other sections use functional
  language (FR-C10). G1/G2/G3 codes appear only in §11's provenance-footer glossary.
  Input pipeline — two options in order of preference:
  *Option B (standard):* `main.py` tees all stdout to `<agent-slug>_run_output.log` via a
  `tee_to_log()` context manager; Claude reads the file. Add to every `main.py` as FR-C8
  Hard Requirement #8.
  *Option A (fallback):* user copies PyCharm terminal output and pastes into Claude Desktop.
  Mandatory sections in order:
  1. **About this run** — two halves designed for cold-read. A student who opens the file
     without having read Part 1 should be fully oriented after §1 and able to make sense of
     every subsequent section.
     *Top half — Setup grid:* a grid of small context cards. Five required items: (a) the
     agent's role in one plain-English sentence; (b) the specific input the agent was given
     for this run (the actual topics, parameters, queries, or whatever inputs the agent
     consumed); (c) the success rule (the goal in lay English — what counts as "done"); (d)
     the hard cap or safety limit imposed by us, naming who imposed it (so the student knows
     it wasn't the agent's choice); (e) the tools the agent had available (lay names, not SDK
     names). One optional item when applicable: (f) a caveat about the data world the agent
     operated in — e.g., mock-vs-real, sandbox-vs-production, or any other context the
     student needs to interpret outcomes correctly.
     *Bottom half — Result snapshot:* the runtime snapshot card. Iterations used, key outcome
     metric (e.g., topics covered, coverage met, goal reached), termination reason in plain
     English ("the agent decided it was done" / "the agent hit its safety cap" / "the agent
     escalated"), cost (tokens in/out + dollar estimate where present), and total elapsed
     time.
     *Visual contract:* setup cards use a calm/informational treatment (cards or chips,
     muted accent); the snapshot uses a high-contrast dashboard with color-coded warn/ok
     cells so the result reads at a glance. The two halves are visually distinguished and
     separated by a sub-heading or divider. **Rationale:** Ram's cold-read audit
     (2026-06-07) found that the prior §1 (snapshot only) left a cold reader unable to
     interpret outcome numbers — they saw "10/10 tries" without knowing 10 was a cap we
     set, and "0/3 topics" without knowing what the three topics were.
  2. **Was this really an agent? Here's the proof** — most prominent section. Three
     functional questions answered with quoted runtime evidence:
     • "Did the agent decide when it was done?" → quote one `[GOAL PREDICATE]` line.
     • "Did the agent choose its own next move?" → quote one `[MODEL DECISION]` line.
     • "Did the agent learn from what it saw?" → quote one `[LOOP FEEDBACK]` line.
     One plain-English verdict per question (e.g., "Yes — the agent ran a check each step
     and reported what it found"). Gate codes (G1/G2/G3) are NOT used in the question
     text or verdict prose — only in §11's glossary.
  3. **Why this goal counted as a real check** — depth on the fact that the agent's goal
     was a *computable test* the agent ran on itself at every step, not a fuzzy aspirational
     outcome. Explains in plain English the difference between a "did-it-finish check" (the
     agent computes a yes/no verdict from its current state) and a wish-based stopping
     condition (which can't be honestly verified). Anchored to one quoted
     `📐 [GOAL PREDICATE]` line — the literal moment the agent evaluated itself. One short
     section, ≤4 paragraphs. **This section's job is to make the verifiability of the goal
     feel concrete, not to restate what the goal was** — the goal content moved into §1's
     setup grid in the cold-read restructure. The lay framing of this section connects
     directly to the first core trait ("it knows what done means") and explains why a
     real verifiable check is what separates an agent from a hopeful loop.
  4. **Traits in Action** — **UNCHANGED title and intent.** One card per fired trait:
     trait name, tier, one quoted output line, one-sentence explanation of why that line
     demonstrates the trait. (Ram's audit: well-implemented; preserve.)
  5. **The life of this agent (from wake-up to goodbye)** — visual timeline with
     non-coder stage names: **Wake up → Plan → Try → Look → Try again → Stop**. Each
     stage gets one plain-English sentence anchored to a specific runtime output line
     ("Wake up: 🤖 [AGENT BOOT] — the agent introduces itself"; "Plan: 📋 [PLAN GENERATED]
     — the agent breaks the goal into steps before doing anything"; etc.). An optional
     collapsible *"Technical view: the SDK call sequence"* (FR-C10 sidebar) may show
     `[SDK →]`/`[← SDK]` brackets and loop iterations as a repeating arc for readers
     who want the under-the-hood view.
  6. **Did the agent reach its goal? (the progress trace)** — `📐 [GOAL PREDICATE]`
     from every iteration as a progress strip (False → True or cap hit), with one
     plain-English line of narration beside each verdict explaining what the agent
     checked at that step.
  7. **Agent Spectrum Placement** — **UNCHANGED title and intent.** Horizontal scale
     (Workflow → Simple Agent → Multi-Step Agent → Autonomous Agent); "If this were a
     workflow" contrast callout citing the `[MODEL DECISION]` line as the difference
     marker. (Ram's audit: well-implemented; preserve.)
  8. **Flashcards** — 5–8 flip-on-click; front: term in plain English; back: definition
     anchored to *this agent's specific runtime behavior*, not a generic definition.
  9. **Quick self-check** — 3–5 MCQ inline-reveal with one-line explanations; ≥1
     question tests agent/workflow distinction; wrong answers explain why they're
     wrong. Phrased functionally (e.g., "When the agent's first search came back empty,
     what did it do?") — no gate codes in question text.
  10. **What you could build next** — 3–5 daily-life use-case suggestions; each names
      in plain English the new capability it would exercise beyond this agent
      (e.g., "An agent that remembers what you asked yesterday" rather than "rung 3 —
      `session_id`").
  11. **Provenance footer + glossary** — agent slug, run date, SDK rungs introduced,
      G1–G5 verdicts, Part 1 companion file, log source (Option A or Option B).
      **Glossary block:** maps functional aliases (FR-C10 §3) to their G1–G5 codes for
      readers who want the technical mapping. **This is the ONLY student-facing surface
      where G1–G5 codes appear.**
- FR-C7: **`prompt.md` blueprint** — written **before any Python code**, into the agent's
  folder. Self-contained: a cold Claude session reading only this file plus CLAUDE.md
  must be able to regenerate the Python agent without any other context. Required
  sections: (1) candidate selection rationale with G1–G5 verdicts and 9-trait scorecard,
  (2) SDK rungs introduced, (3) goal predicate as a code-ready `is_goal_met(state)->bool`
  signature, (4) tool definitions with mock response specifications (realistic data),
  (5) memory design (keys, types, stored/retrieved at which step), (6) termination
  conditions (predicate + circuit breaker), (7) complications to inject (if any),
  (8) pointer to the runtime output standard (FR-C8), (9) `═══` comment header format,
  (10) QA self-verification checklist, (11) PyCharm run instructions. `prompt.md` is the
  sixth mandated file per agent (joining main.py, agent.py, smoke_test.py,
  requirements.txt, README.md, `<agent-slug>_learning-guide.html`). It is the design
  artifact; `_learning-guide.html` is the pre-run learning artifact; `_learning-insights.html`
  is the post-run reinforcement artifact — all three serve different purposes and must not
  duplicate each other.
- FR-C8: **Runtime output standard** — every generated `main.py` MUST produce the
  following output elements, in this order, using `print()` with Unicode box-drawing
  characters and emoji. No `rich`, `colorama`, or `logging` module.
  **(a) Boot banner:** `🤖 [AGENT BOOT]` with agent name + auth line, framed by `═` dividers.
  **(b) Goal set:** `🎯 [GOAL SET]` printing the goal predicate as one plain-English sentence.
  **(c) Plan display:** `📋 [PLAN GENERATED]` with a box-drawn list (○ PENDING / ▶ ACTIVE /
    ✓ DONE); reprinted at the start of every loop step with live status.
  **(d) Per-step header:** `📍 [STEP <id>]` at the start of every iteration.
  **(e) Tool call:** `🔧 [TOOL CALL] tool_name({params})` — makes GATE[G2] visible.
  **(f) Tool result:** `📥 [TOOL RESULT] N chars returned` — makes TRAIT[perception] visible.
  **(g) O-R-A triad:** `👁 [OBSERVE]` / `🧠 [REASON]` / `⚡ [ACT]` — one line each — makes
    GATE[G3] visible every iteration.
  **(h) Step finding:** `📝 [STEP FINDING]` with the finding text.
  **(i) Memory stored:** `💾 [MEMORY STORED] key  └─ <100-char preview>` — TRAIT[memory].
  **(j) Memory retrieved:** `🧠 [MEMORY RETRIEVED] N prior findings injected` at step start.
  **(k) Termination check:** `🔍 [TERMINATION CHECK]` with steps done N/M (X%), confidence
    level, and `→ ○ CONTINUING` or `→ ✅ STOPPING CONDITION MET` — makes GATE[G4] visible.
  **(l) Complication block [when applicable]:** `⚠ [<EVENT> DETECTED]` with a three-line
    `── OBSERVE / REASON / ACT ──` block — makes GATE[G3] recalibration visible.
  **(m) Plan revision [when applicable]:** `📝 [PLAN REVISED]` showing old/new steps — makes
    TRAIT[autonomy] and GOTCHA[control-plane] visible.
  **(n) Termination line:** `🏁 [GOAL MET]` or `EXIT: cap reached` or `ESCALATED` — always.
  **(o) POST-RUN AGENT SUMMARY:** fires unconditionally at script exit (even on error or cap).
    Must cover all seven items: (1) narrative of how the agent ran, (2) traits in action
    with code-line evidence per trait, (3) every tool-selection decision the model made
    (reference `[MODEL DECISION]` lines), (4) plan recalibrations and triggers,
    (5) iteration count and termination reason, (6) memory ledger — session memory keys
    and application memory keys listed separately, (7) plain-English G1/G2/G3 verdict
    pointing to specific `[GOAL PREDICATE]`, `[MODEL DECISION]`, and `[LOOP FEEDBACK]`
    lines as runtime proof.
  **(p) SDK call boundary:** `━━━ [SDK →] model · ~N prompt tokens` immediately before
    every `query()` / SDK call; `━━━ [← SDK] Xs · +N output tokens` immediately after.
    Makes the exact boundary where Python hands off to the LLM — and where it resumes —
    visible. Required: every generated agent. Rationale: all Agency Gates (G1–G3) are
    resolved by reasoning that happens inside this bracket; without the brackets, the
    agent is a black box.
  **(q) Goal predicate evaluation:** `📐 [GOAL PREDICATE] is_goal_met(state) → False/True`
    printed every time the loop calls the goal predicate, showing the evaluated condition
    (e.g. `articles_found=3 · min_required=5 → condition not met`). Required: every
    iteration. Rationale: makes GATE[G1] a *demonstrated* event at runtime — not just
    an annotation in code comments.
  **(r) Model decision marker:** `🎲 [MODEL DECISION] selected: <tool> · alternatives: <X|Y>`
    printed at tool selection time, making explicit that the model — not a Python `if`-
    ladder — chose the next action. Required: every tool dispatch. Rationale: makes
    GATE[G2] undeniable; the `GOTCHA[control-plane]` annotation in code gains a runtime
    counterpart.
  **(s) Loop feedback delta:** `🔄 [LOOP FEEDBACK] observed: X → changed: Y` at the start
    of every iteration after the first, naming what the previous step's result changed
    about the current step's approach (e.g. old query vs new query). Required: every
    iteration from step 2 onwards. Rationale: makes GATE[G3] a *proved* feedback loop,
    not a loop that could be a scripted sequence.
  **(t) Context token tracker:** `📊 [CONTEXT] ~N tokens in context · +M this step`
    printed once per iteration. Token estimate may be approximate (char count / 4).
    Required: every iteration. Rationale: makes LO-11 (context engineering) a visible
    number the student watches grow — without it, context rot is purely theoretical.
  **(u) Memory type labels (replaces generic MEMORY STORED):** session memory uses
    `💾 [SESSION MEMORY] key └─ preview` (ephemeral — within-run conversation);
    application memory uses `📀 [APP MEMORY] key → file └─ preview` (persistent — survives
    the next run). Required: every memory write. Rationale: makes LO-6's session-vs-
    application memory distinction visible; the two kinds look identical without labels.
  **(v) Error classification:** `⚠ [ERROR: TRANSIENT] → retry (1/3)`,
    `⚠ [ERROR: STRUCTURAL] → re-planning`, or `⚠ [ERROR: POLICY] → escalating`
    depending on the failure class. Required: whenever a tool or SDK call fails.
    Rationale: makes LO-12 (failure classification and routing) visible; turns error
    handling from a silent try/except into a student-visible routing decision.
  **(w) Trust fence [conditional]:** `🔒 [TRUST FENCE] <source> fenced as data`
    printed when external content (API response, file, stdin) enters the prompt.
    Required: agents that ingest external web or file content (D13). Optional: agents
    that operate on no external data. Rationale: makes LO-13 (trust boundary) tangible
    at the exact moment untrusted data crosses the boundary.
  **Plan progress is required on all agents** (not optional for short agents): even a
    2-step agent must print `[PLAN PROGRESS]` at the end of every step — the student
    learns to read planning as an ongoing process, not a one-time declaration at boot.
  **G5 future element (reserved for rung-7 agents):** when an independent verifier is
    introduced, add `🔬 [VERIFIER CALL]` before the critic's SDK call and
    `[VERIFIER VERDICT] pass/fail` after. Not required until rung 7.
  **Structured comment header** — mandatory on every major code block:
  ```python
  # ═══════════════════════════════════════════
  # PURPOSE: [one sentence]
  # AGENTIC TRAIT: [trait name]
  # ACHIEVES: [what the agent can do because of this block]
  # DEPENDENCIES: [what must be set up before this block]
  # ═══════════════════════════════════════════
  ```
  This coexists with (does not replace) the existing `# TRAIT[]`, `# GATE[]`, `# GOTCHA[]`
  inline markers — both are required.
- FR-C10: **Audience Register.** All student-facing artifacts (the two `.html` files, runtime
  banners visible in the agent's stdout, Professor narration in chat, Phase F and Phase F2
  probes, README prose) are written **lay-first**: a non-coder reads the body and understands
  what the agent does and what just happened. Three hard constraints:
  1. **Body register** — plain English. No SDK or framework vocabulary in body prose
     (`query()`, `predicate`, `SDK rung`, `permission_mode`, `MessageLens`, etc.).
     Define-on-first-use for any retained domain term.
  2. **Deeper-dive sidebars** — technical content (SDK names, code anchors, gate codes) lives
     in clearly marked optional callouts: `<aside class="deep-dive">` in HTML, or a
     "Deeper dive (skip if not curious):" prefix in chat. Skippable without losing
     comprehension of the body.
  3. **G1–G5 codes** — appear in code annotations (`# GATE[Gn]: ...`), in the FR-D4 grep
     contract, and in the insights file's §11 provenance-footer glossary only. Never in body
     prose, runtime banners visible to Ram, probes spoken to Ram, or section titles of any
     student-facing artifact. Functional aliases used in student-facing surfaces:
     "did-it-finish check" (G1), "model's own choice" (G2), "learning from what it saw" (G3),
     "principled stop" (G4), "independent check" (G5).
  Code annotations (`TRAIT[]`/`GATE[]`/`GOTCHA[]` inline markers in `main.py`) are exempt —
  they teach the SDK and are read by Ram in code-reading mode, not by laypersons.
  **Enforcement (Translator persona):** every student-facing artifact is reviewed before
  delivery in Phase D under FR-D3. Any sentence requiring a coding background to parse is
  a defect and goes back. The phrase "if a non-coder couldn't read it over coffee and
  understand what the agent does, it goes back" is the working test.
- FR-C11: **HTML backup-then-rewrite.** When regenerating either HTML artifact for an
  existing agent (e.g., remediation pass under a new register, register refinement, or any
  rewrite that produces a new lay-first version), the prior version MUST be renamed to
  `<filename>_<reason>-v<n>.html` before the new version is written. Examples:
  `study-prep_learning-guide_technical-v1.html` preserves the original technical version
  when rewriting under FR-C10's lay-first register; `study-prep_learning-insights_v2.html`
  preserves a previous lay-first iteration before a refinement pass. Honors the no-delete
  folder protocol (CLAUDE.md). Never overwrite an existing HTML artifact in
  `agents/<slug>/` — always rename-then-write.

### Phase D — QA before delivery (by Claude, in the sandbox)
- FR-D1: Claude runs the generated `smoke_test.py` in its sandbox (LLM mocked) and must
  see it green before handing over. Syntax, imports, and logic verified even though live
  LLM calls can't run in the sandbox.
- FR-D2: On failure: diagnose, repair, rerun — max 3 attempts, each narrated in chat
  (what failed, what changed, why). Then an honest failure report. Never claim success
  without a green run.
- FR-D3: **Part 1 validation:** `<agent-slug>_learning-guide.html` parses; every
  file/function cited in the trait-to-code map exists in the code; MCQ count 3–5 with
  explanations. Part 2 (`_learning-insights.html`) is validated after the first run —
  not part of the pre-delivery QA gate (it cannot be generated until the log exists).
- FR-D4: **Grep contract & reachability:** `TRAIT[` ≥ 5, `GATE[` ≥ 5 (G1–G5 each),
  `GOTCHA[` ≥ 1 in main.py. Every failure/reject/escalate branch fires at least once
  under seeded fixtures. Goal predicates run against extracted assistant text only,
  asserted in the smoke test. **Runtime output contract (FR-C8):** `[AGENT BOOT]`,
  `[GOAL SET]`, `[GOAL PREDICATE]`, `[MODEL DECISION]`, `[LOOP FEEDBACK]`, `[CONTEXT]`,
  `[SDK →]`, `[TERMINATION CHECK]` all present; `SESSION MEMORY` or `APP MEMORY` present
  (at least one); `POST-RUN AGENT SUMMARY` block present (grep: `AGENT SUMMARY`);
  structured comment header `═══` present ≥ 5 times.

### Phase E — Registry & bookkeeping
- FR-E1: Append per agent to `foundry_registry.json`:
  - Top-level fields: slug, date, traits demonstrated, gates passed, SDK concepts
    introduced, status.
  - **`learning` object** (replaces single-line `professor_notes`): structured record
    written at the end of Phase F (pre-run Professor session) —
    `probes_asked` (list), `gaps` (list of concepts that were weak),
    `strengths` (list of concepts demonstrated correctly),
    `recall_question_next_cycle` (one sentence — the weakest gap, asked at next cycle's
    Professor opening).
  - **`post_run_notes` subobject** (written after Phase F2, post-run Professor session) —
    `runtime_surprises` (list of strings: things that surprised Ram in the runtime output),
    `post_run_probes_asked` (list of strings: probes asked during Phase F2),
    `next_cycle_expectation` (one sentence: what Ram predicts the next SDK rung will unlock),
    `skipped` (boolean: true if Ram skipped Phase F2 without interaction).
    If Phase F2 is skipped entirely, record `post_run_notes: {"skipped": true}`.
  - The registry also carries a **`preferences`** object (Ram's learner profile:
    preferred domains, focus traits, build-size appetite — seeded from D16, updated as
    answers reveal changes) used to steer future brainstorms.
  - One line appended to `ROADMAP.md`.
- FR-E2: Never overwrite an existing agent folder without explicit confirmation
  (version-bump the slug instead).
- FR-E3: **`HANDOFF.md` at project root, updated at the end of every cycle**: what was
  built, current registry state, next intended cycle, open questions. Purpose: a brand-new
  Claude Desktop session must be fully operational from `HANDOFF.md` + this PRD alone —
  chat history is not the memory system (D5 corollary).
- FR-E4: **`INSIGHTS.md` at project root, regenerated at the end of every cycle.**
  A human-readable synthesis document with six sections (in order):
  1. *Understood* — concepts Ram demonstrated correctly in Professor probes (with cycle
     evidence).
  2. *Active gaps* — concepts that came up weak; pending reinforcement in future cycles.
  3. *SDK ladder* — introduced vs. demonstrably internalized (can explain unprompted),
     per rung.
  4. *Domain coverage* — agents built per domain (morning-briefing / health-habits /
     learning-research).
  5. *Brainstorm history* — table: date | candidate name | domain | gate verdict |
     decision (locked / deferred / rejected / needs-fix) | reason.
  6. *Recommended focus for next cycle* — one paragraph: which gap to reinforce, which
     domain is under-represented, which SDK rung is next. Claude generates this section
     from the **5-cycle synthesis arc template** (below) for the current cycle number.
  Claude reads `INSIGHTS.md` at every session start (alongside `HANDOFF.md`) as one of
  the brainstorm inputs. It must never be deleted; it grows across cycles.

  **5-cycle synthesis arc** — Claude follows this template when writing §6 for each cycle.
  Adapt the verbiage; the structure is mandatory:

  | Cycle | Synthesis statement | Cross-agent link | Opening recall question |
  |---|---|---|---|
  | 1 | "You have one agent. The core loop exists. The O→R→A pattern is live but untested across domains." | n/a (no prior agent) | n/a |
  | 2 | "You have the loop and [cycle-1 agent slug]'s domain. Cycle 2 adds [new rung]. How would the two loops differ if you composed them?" | Links cycle-2 to cycle-1 trait map | Recall question from cycle-1 `recall_question_next_cycle` |
  | 3 | "Multi-turn memory (rung 3) means state persists across SDK calls. Contrast: what cycle-1 forgot after each call vs. what cycle-3 remembers." | Rung 3 vs rung 1 memory model | Cycle-2 `recall_question_next_cycle` |
  | 4 | "Tool use (rung 4) is where G2 becomes real. The model doesn't just observe — it decides *which* tool. Compare rung-4 MODEL DECISION output to rung-2." | G2 evidence in cycles 2 vs 4 | Cycle-3 `recall_question_next_cycle` |
  | 5 | "The ladder is [rungs introduced so far]. What's left is [remaining rungs]. If you were designing an agent for [Ram's use case], which rungs would you need and why?" | Full ladder survey | Cycle-4 `recall_question_next_cycle` |

  For cycles 6+, extend the arc: synthesize from the most recent two agents, pick the
  widest skill gap from `learning.gaps[]` as the cross-agent link, carry the
  `recall_question_next_cycle` forward.
- FR-E5: **Brainstorm session log** — append one entry to
  `foundry_registry.json` → `brainstorm_sessions[]` at the end of every brainstorm
  (whether or not a candidate is locked that session). Fields: date, cycle number,
  candidates array (name, domain, gate verdict, decision, notes), locked (slug or null).
  Purpose: prevents repeat proposals and feeds FR-E4's brainstorm history table.

### Phase F — Professor session *(new in v6; skippable, in Claude Desktop chat)*
- FR-F1: **Trigger & bound.** Immediately after delivery (Phase D green), Claude offers
  a Professor session: ~10 minutes, four parts. Ram may skip or end it at any time
  ("skip professor" / "done"). Conversational behavior only — no new files, no tooling.
- FR-F2: **Shape.** All four sub-phases follow FR-C10 (lay-first body, no gate codes
  spoken to Ram). When the Professor session immediately follows lock + green QA, the
  opening and handoff sub-phases use the FR-F7 checkpoint templates verbatim.
  (1) *Opening* ~2 min: what this agent is, the goal in one sentence, what Ram will see
  when it runs — intuition first. **Delivered via the Post-lock briefing template
  (FR-F7 Checkpoint 1)** when timing permits; otherwise its own opening narration in
  the same lay register.
  (2) *Core* ~3 min: the 2–3 ideas that matter for this agent — the control plane (who
  owns each decision, in plain English), the centerpiece traits in functional language
  ("this agent's did-it-finish check is `is_coverage_met()`" — NOT "G1 verifier"), and
  the one gotcha it guards against (named in lay terms).
  (3) *Probe* ~4 min: 2–3 comprehension questions targeting mechanism, not recall.
  **Probe text uses FR-C10 functional language; gate codes (G1–G5) NEVER appear in what
  Ram hears.** Each probe MUST be introduced by the Pre-probe context Professor
  checkpoint (FR-F7 Checkpoint 4) — quote a specific code line or runtime-output label,
  then state the functional question. Example probes (mirror FR-F5's shape, anchored
  pre-run to code rather than runtime output):
  - *Goal predicate function (`is_coverage_met()`)* → "Look at the function that decides
    when the agent is done. What would happen if it returned True too early? What would
    the agent miss?" *(probes did-it-finish check / G1)*
  - *Model-decision dispatch site* → "Find the line in the loop where the agent
    dispatches the model's choice. What would change if we hard-coded the tool here
    instead?" *(probes model's own choice / G2)*
  - *State injection at iteration start* → "The agent injects its current state into
    the prompt at the top of every iteration. Why does it have to do that? What would
    the model 'know' without this injection?" *(probes learning from what it saw / G3)*
  - *Safety cap constant and exit branch* → "There are two ways this agent can exit.
    Find both in the code. Why do we need both?" *(probes principled stop / G4)*
  (4) *Handoff* ~1 min: reading order, what to watch in the first run, registry note.
  **Delivered via the Pre-run framing template (FR-F7 Checkpoint 2)** when the run is
  imminent — names the three labeled output lines Ram should watch and the conditions
  for the agent to stop.
- FR-F3: **Repair protocol (bounded).** On a wrong/shaky answer: attempt 1 — one
  Socratic counter-question; attempt 2 — brief targeted re-explanation pointing to the
  exact briefing section or code line; then move on. Never loops, never scores, never
  shames. Every probe and reteach must reference a real artifact (briefing § or
  file:line) — the anchor rule.
- FR-F4: **Structured memory.** Session ends by writing the `learning` object to the
  registry (FR-E1) and triggering `INSIGHTS.md` regeneration (FR-E4). The next cycle's
  Professor opens with **one** recall question drawn from `recall_question_next_cycle` in
  the most recent agent's `learning` record. No LMS machinery: no scoring, no rubrics,
  no mastery tiers — the structured object is a structured *note*, not a student model.
- FR-F5: **Phase F2 — post-run Professor session** *(skippable, triggers after Ram runs
  the agent in PyCharm)*. Triggered when Ram says "I ran it" or equivalent. Separate
  from Phase F (which is pre-run). Purpose: reinforce agentic concepts anchored to *actual
  runtime output* rather than code alone — the difference between understanding code and
  understanding the agent in motion. **All probes follow FR-C10 (lay-first body, no gate
  codes in probe text) and are preceded by the Post-run debrief and Pre-probe context
  Professor checkpoints (FR-F7).**
  - **Shape:** 3–5 probes, conversational. No four-part structure required (shorter than F).
    Each probe MUST anchor to a specific labeled output line from the runtime log AND
    MUST be introduced by the Pre-probe context template (FR-F7). The Post-run debrief
    (FR-F7 Checkpoint 3) is delivered ONCE before the first probe and explains in plain
    English what happened in the run.
  - **Probe types (Claude picks from these, selecting what fired in Ram's actual run).
    Probe text is written in functional language; gate codes in parentheses are spec
    traceability only and NEVER appear in the probe spoken to Ram:**
    1. `[GOAL PREDICATE]` line → "The agent itself decided whether it was done yet at this
       step. How did it make that call? What would happen if it didn't check?" *(probes the
       did-it-finish check / G1)*
    2. `[MODEL DECISION]` line → "The model picked one tool out of several at this moment.
       What were the alternatives? Why did this one win — and could it have gone
       differently next time?" *(probes the model's own choice / G2)*
    3. `[LOOP FEEDBACK]` delta → "Look at what the agent did in step N versus step N+1.
       What changed because of what it saw? A non-agent script would have repeated the
       same thing — what made this run different?" *(probes learning from what it saw / G3)*
    4. `[ERROR: STRUCTURAL]` or `[ERROR: POLICY]` (if present) → "Something broke here.
       Was it a temporary blip, a real bug in how the agent was set up, or a permission
       issue? How can you tell from this line?" *(probes failure classification / LO-12)*
    5. `[PLAN REVISED]` or `[PLAN PROGRESS]` → "The plan changed mid-run. Who decided to
       change it — your code, or the model in the moment? How can you tell from the
       output?" *(probes autonomy)*
    6. `[SDK →]` / `[← SDK]` pair → "These two lines mark where your code hands off to the
       LLM and where it gets the answer back. What's happening in that gap? Why does it
       matter that you can see those moments?" *(probes LLM boundary visibility / LO-7)*
    7. Usage summary line → "This run cost about N tokens / X cents. If you ran this every
       morning, what would the monthly cost look like? What would you change to keep it
       cheap?" *(probes cost awareness / §7.2)*
  - **Repair:** same bounded two-attempt Socratic repair as FR-F3. Repair language also
    follows FR-C10 — counter-questions and re-explanations use functional aliases, never
    gate codes.
  - **Memory:** writes `post_run_notes` subobject to the registry (FR-E1). If skipped,
    records `{"skipped": true}`. Does NOT re-trigger `INSIGHTS.md` regeneration (that
    happens at end of Phase F). If Phase F was also skipped and this is the only
    structured record, trigger `INSIGHTS.md` regeneration here instead.

- FR-F6: **Phase 0 — Session Warm-Up** *(new in v9; mandatory cycle 2+, skippable cycle 1)*
  Fires automatically at every "begin the brainstorm" / "new agent" trigger after cycle 1,
  immediately after Claude reads the four session state files and before any brainstorm
  question is asked. Ram bypasses with "skip warm-up."
  - **Part A — Brief (target 2–3 minutes, one-way):** Structured in-chat block with labeled
    sections delivered in this order: (1) Report card — drawn from `report_card` registry
    object: agents built, SDK rungs introduced, domains covered, gates ever demonstrated.
    (2) Complexity arc — one sentence per prior cycle showing how agents grew in
    sophistication. (3) Top 2 active gaps — from latest agent's `learning.gaps[]`, with
    source cycle noted. (4) Gotchas mastered — plain-English summary of `gotchas_mastered[]`
    accumulated across all cycles. (5) Forward seed — names the specific next SDK rung and
    one sentence on what it unlocks for future agents. Format: emoji-labeled block using the
    standard layout defined in the Phase 0 prompt spec (🧠 header, ━━━ dividers, per-item
    emoji labels 📊 📈 🔍 ⚠️ 🔮).
  - **Part B — Interrogation (target 3–5 minutes, Socratic dialogue):** 2–3 recall questions,
    one at a time. Sources: `recall_question_next_cycle` from most recent agent, active
    `learning.gaps[]`, and (when present) a specific labeled output line from `post_run_notes`.
    Claude waits for Ram's answer before proceeding. On a correct answer: one-sentence
    validation, move on. On a partial answer: one Socratic counter-question anchored to a
    specific code line (file:line) or runtime output line label (e.g. `[MODEL DECISION]`);
    then give the explanation. Maximum one counter per question — never loops. After all
    questions, one forward-looking sentence connecting what was recalled to what the brainstorm
    will explore. Never ask more than 3 questions in Part B.
  - **Hard rules:** Never score or grade. Never exceed 8 minutes total. Never draw recall
    questions from generic agent knowledge — only from this project's registry artifacts.
    Part A always completes before Part B begins. Phase 0 ends before brainstorm starts.
  - **Registry dependency:** Phase 0 reads `report_card` (FR-E6) and `gotchas_mastered[]`
    (FR-E6). If these fields are absent (cycle 1 edge case), skip Phase 0 gracefully and
    note that warm-up will begin at cycle 2.

- FR-F7: **Professor Checkpoints (enforced).** The Professor persona (CLAUDE.md
  "The Professor — Voice and Character") stops being aspirational. Four named checkpoints
  fire at fixed moments in the operating cycle and are gate requirements, not stylistic
  guidance. Each has a ≤5-sentence template; the Professor MUST deliver the checkpoint
  before proceeding to the next step. All templates follow FR-C10 (lay-first body, no
  gate codes). The templates are scaffolding; the delivery is conversational and in
  voice — never bullet points or status updates.

  **Checkpoint 1 — Post-lock briefing** *(fires immediately after Ram types
  `lock <candidate>`; before any file is written; before operating cycle step 3.5).*
  ≤5 sentences, all in plain English:
  1. "Locked: [agent name]. Here's what we're building and why."
  2. "In plain English, this agent will [goal in lay language]."
  3. "The traits to watch as we build: [trait 1], [trait 2], [trait 3] — explained
     in one sentence each."
  4. "The one thing that might surprise you: [unexpected behavior or gotcha in plain
     English]."
  5. "Files will arrive in one continuous pass. I'll narrate the salient line(s) as
     each file lands."

  **Checkpoint 2 — Pre-run framing** *(fires after all 8 files are written and the
  smoke test is green; before Ram is directed to PyCharm).* ≤5 sentences:
  1. "Ready for your first run."
  2. "What you should see in the terminal, roughly: [output flow in one plain-English
     sentence]."
  3. "The three moments worth watching: [labeled output line 1], [line 2], [line 3]
     — these are where the did-it-finish check, the model's own choice, and learning
     from what it saw become real."
  4. "The agent will stop when [goal predicate condition in plain English] OR when it
     hits its safety cap at [N iterations]."
  5. "If anything looks weird, that's actually [what it might be teaching]."

  **Checkpoint 3 — Post-run debrief** *(fires when Ram says "I ran it" or pastes
  terminal output; BEFORE any Phase F2 probe; replaces "the Professor just started
  asking questions" failure mode from Cycle 1).* ≤5 sentences:
  1. "Here's what just happened, in plain English."
  2. "The agent [one-sentence narrative summary of the run]."
  3. "The two output lines worth re-reading are: [line 1 with one-line gloss], [line 2
     with one-line gloss]."
  4. "Functional verdict: did the agent finish? did it own its choices? did it learn
     from what it saw? — answered in plain English with the run's evidence."
  5. "I have [3–5] probes to check what you noticed. Want me to start, or do you have
     questions about what you saw?"

  **Checkpoint 4 — Pre-probe context** *(fires before EACH Phase F2 probe; immediately
  precedes the probe text).* ≤2 sentences:
  1. "Quoting the line from your run: [exact line, indented]."
  2. "What I'm asking: [functional question in plain English]."

  **Enforcement:** A cycle that skips a checkpoint is incomplete and must be repaired.
  Checkpoint delivery is in conversational voice — the templates above are the *content*
  contract, not the *form* contract. Phase F (pre-run Professor session, FR-F2) and
  Phase F2 (post-run, FR-F5) probes inherit the same FR-C10 register — functional
  language, no gate codes spoken to Ram.

### Phase E — Registry & bookkeeping (additions)
- FR-E6: **Cross-cycle registry fields** — written at the end of every cycle (step 8 of
  Operating Cycle), after Phase F2 or after Phase F if F2 is skipped:
  - **`gotchas_mastered[]`** (top-level array, cumulative): append this agent's `GOTCHA[]`
    annotations in plain English, one entry per annotation. Never duplicate an existing
    entry. Source: grep `GOTCHA[` from `main.py`, extract the trap name and plain-English
    description. This array is the input for Phase 0 Part A item (4).
  - **`report_card`** (top-level object, regenerated each cycle from full `agents[]`):
    ```json
    {
      "agents_understood": ["slug1", "slug2"],
      "sdk_rungs_introduced": [1, 2, 3],
      "gate_verdicts_summary": {"G1": "demonstrated", "G2": "demonstrated", "G3": "demonstrated", "G4": "demonstrated", "G5": "N/A"},
      "domain_coverage": {"morning-briefing": 1, "learning-research": 1},
      "top_active_gaps": ["gap concept 1 (cycle N)", "gap concept 2 (cycle N)"]
    }
    ```
    Overwrite the previous value on every cycle. This object is the input for Phase 0
    Part A item (1) and is the "report card" delivered in the session warm-up.

## 6. Non-Goals (explicit)

- NOT a Python console app for brainstorming (that was v1–v4; superseded by Model B).
  Building a PyCharm "Foundry app" is out of scope; it may be revisited someday as a
  capstone generated project, but is a non-commitment.
- NOT multi-user; single user (Ram), single machine, Windows + PyCharm + Claude Desktop.
- NOT corporate/enterprise agents; daily-life learning scope only.
- NOT `ANTHROPIC_API_KEY`-based auth; NOT third-party orchestration frameworks
  (LangChain, CrewAI, AutoGen) — `claude-agent-sdk` + stdlib is the curriculum.
- NOT generating agents that act outside their own subfolder, send messages, spend
  money, or run unattended on a schedule.
- Generated agents are non-interactive by default (Ram's explicit choice). Opt-in
  exception per use case: a bounded human-approval tool when human-in-the-loop control
  is the trait being taught.
- NOT optimizing for token efficiency or speed; optimizing for legibility of agency.
- NOT a learning-management system: no student-model schema, no mastery rubrics or
  calibration sets, no difficulty tiers, no scoring, no escalation alerts. The Professor
  (Phase F) is a bounded conversation plus one registry field — by design.

## 7. SDK Curriculum Contract *(restructured in v5)*

The SDK is learned **through the generated agents**. Two rules:

### 7.1 The concept ladder
Every generated agent must introduce **at least one SDK concept not used by a previous
agent** (tracked in the registry). Suggested progression — order flexes with use cases:

| Rung | SDK concept | Typically taught by |
|---|---|---|
| 1 | `query()` one-shot + message anatomy (`SystemMessage`, `AssistantMessage`, `ResultMessage`, `usage`) | first agent |
| 2 | Goal predicate + agent loop + circuit breaker (G1/G3/G4 in code) | first/second agent |
| 3 | `ClaudeSDKClient` multi-turn + `session_id` capture/resume | second agent |
| 4 | Custom tools (`@tool`, `create_sdk_mcp_server`) — model-owned tool choice (G2) | third agent |
| 5 | `allowed_tools` / `disallowed_tools` / `permission_mode` (documented modes only: `default`, `acceptEdits`, `plan`, `bypassPermissions`) | third/fourth agent |
| 6 | Hooks: `PreToolUse` guard, `PostToolUse` audit + JSONL span trace | fourth agent |
| 7 | Independent verifier — separate critic call, fresh context, calibrated (G5/LO-10) | fourth/fifth agent |
| 8 | Subagents (own context windows); context compaction (LO-11) | fifth+ agent |

### 7.2 Per-agent SDK requirements (every generated agent)
- A `MessageLens`-style helper: one-line simplified console rendering of each SDK
  message, so the agent loop is watchable in every run.
- `preflight()`: Python version, imports, `claude` CLI present and logged in; detect
  `ANTHROPIC_API_KEY`, warn it would take precedence, remove it **from the child-process
  environment only** — never mutate the global environment.
- Per-run usage summary at exit (`usage`, `total_cost_usd` when present). Note: from
  2026-06-15, Agent SDK usage on subscriptions draws from the monthly Agent SDK credit.
- Mock-LLM boundary for tests: a client adapter whose fake replays canned messages
  (FR-C4); seeded-failure fixtures for branch reachability (FR-D4).
- **Web perception permitted (D13):** generated agents may call free public web APIs
  (weather, news, prices) for real perception — with timeouts, bounded retries, and all
  ingested text fenced as data-not-instructions (LO-13). File writes remain sandboxed to
  the agent's own folder.

### 7.3 Cross-cutting objectives — scaling rule (annex LO-10–14)
- Gates G1–G5: always.
- LO-13 trust boundary (outside text is data, not instructions — fenced): mandatory
  whenever an agent ingests external content.
- Minimal agents: remaining LOs optional, named in the mini-spec when included.
- Medium+ agents: LO-10 (independent verification) and LO-12 (failure routing with
  reachable branches) also mandatory.

## 8. Guardrails & Failure Modes

**Claude-side (Foundry duties, every cycle):**

| Failure mode | Detection | Response |
|---|---|---|
| Writing before lock | Lock-gate discipline (FR-B1) | No Write/Edit calls pre-lock |
| Overwriting prior work | Folder-exists check (FR-E2) | Version-bump slug or ask |
| Claiming untested success | Run-before-deliver (FR-D1) | Evidence (green run) before assertions |
| Stale package knowledge | Verify versions at build time (`pip index versions` / web) | Pin verified-current floors |

**Generated-agent-side (in every agent's code):**

| Failure mode | Detection | Response | Recovery |
|---|---|---|---|
| CLI missing / not logged in / API-key precedence | `preflight()` | Fix-it message with exact commands | Ram fixes, reruns |
| LLM timeout/transient error | Timeout + `ResultMessage` error subtype | Bounded retry with backoff | Honest abort |
| Runaway loop | Goal-predicate exit **and** max-iteration/budget cap (G4) | Self-terminates, prints reason | Documented in README |
| Unbounded context growth | Token estimate per iteration (when looping) | Compaction / sliding window (ladder rung 8) | Visible number, not a vibe |
| Kill switch | Ctrl+C | Clean exit, no corrupted state | Rerun |

## 9. Human Approval Gates

1. **Lock gate** — no code generation before typed lock.
2. **Mini-spec confirmation** — second yes after the locked candidate's spec is shown.
3. **Overwrite gate** — no destruction of prior work, ever.
4. **Live-call gate** — optional post-green live verification runs only on Ram's machine
   with his confirmation.

## 10. Evaluation & Success Criteria (per generated agent)

- S1: Candidate passes Agency Gates G1–G3 (pass/fail, no "borderline" at acceptance);
  G4–G5 demonstrated in code.
- S2: All five mandated files present; grep contract met: `TRAIT[` ≥5, `GATE[` ≥5,
  `GOTCHA[` ≥1.
- S3: `smoke_test.py` (LLM mocked) exits 0 in Claude's sandbox before delivery.
- S4: Registry + ROADMAP.md updated; next session perceives the new agent.
- S5: README contains the trait-evidence table (trait → file:line).
- S6: Smoke test asserts termination cap honored, no outside-folder writes, and branch
  reachability (FR-D4).
- S7: `<agent-slug>_learning-guide.html` (Part 1) passes validation (FR-D3); `_learning-insights.html` (Part 2) generated after first run from log or pasted output.
- S8: Termination reason printed on every exit; each claimed trait has one **visible
  run-time effect** (a number or artifact in a single run — annex §5.11).
- S9: At least one new SDK ladder rung introduced and named in the registry entry.
- S10 (learning): Ram can point to the exact line where each Core gate fires.
- S11: Professor session offered after every delivery; every probe and reteach
  references a real briefing section or code line (anchor rule); `professor_notes`
  written to the registry.

## 11. Learning Evidence

| Learning objective | Where Ram sees it | Mechanism |
|---|---|---|
| Feedback loop (before code) | Claude's narrated QA-repair cycle in chat | FR-D2 |
| Feedback loop (in code) | The agent's own loop changing course on an observed result | G3 + `GATE[G3]` marker |
| Agent loop anatomy | MessageLens one-liners in every run | §7.2 |
| Sessions vs app memory | `session_id` logged + labelled memories | ladder rung 3 |
| Real tool selection | Log shows model choosing tools unprompted | ladder rung 4, G2 |
| Permissions as autonomy dial | Behavior difference across permission modes | ladder rung 5 |
| Hook-based control | A blocked write appears as BLOCKED in the audit | ladder rung 6 |
| Agency provable, not asserted | `grep GATE\[ main.py` lands on predicate, decision, feedback edge, cap, verifier | FR-C2/FR-D4 |
| Trap avoidance | `GOTCHA[...]` guards at the exact dodged-trap lines | annex §5 |
| Pre-code comprehension | `_learning-guide.html` (Part 1) + MCQ before opening main.py | FR-C5/FR-D3 |
| Post-run reinforcement | `_learning-insights.html` (Part 2) after first run; proof from execution | FR-C9 |
| Verified understanding before code | Professor probes + Ram's own restatement, with bounded Socratic repair | Phase F |
| Retention across cycles | One recall question at next cycle's Professor opening | FR-F4 / professor_notes |
| Cost awareness | Per-run usage summary | §7.2 |

## 12. Roadmap (a curriculum of agents, not app phases)

| Cycle | Deliverable | New SDK rungs (target) |
|---|---|---|
| 1 | First generated agent (minimal; e.g., the brainstormed morning-learning-briefing candidate or successor) | 1–2 |
| 2 | Second agent — multi-turn | 3 |
| 3 | Third agent — custom tools, permissions | 4–5 |
| 4 | Fourth agent — hooks, span trace, independent verifier | 6–7 |
| 5 | Fifth agent — subagents, context compaction | 8 |
| — | **Negative control** (any cycle): one intentional workflow shipped so the gates can be watched failing red, with the minimal-fix diff | annex §7 R8 |

## 13. Open Items

- Generated agents stay fully self-contained (no shared `common/`). **Confirmed.**
- `foundry_registry.json` lives at project root. **Proposed.**

## 14. Binding Annex

`AGENT_LEARNING_AND_AGENCY_GATES.md` (project root) is the binding learning and
acceptance spec — gates (§3), annotation mandate (§4), gotcha checklist (§5), chapter
map (§6). Not duplicated here. On acceptance criteria the annex wins; on product scope
this PRD wins. Briefing gotchas sections select from annex §5 the traps each specific
agent guards against, cross-referenced to its `GOTCHA[...]` lines.

---

**Prior changelogs.**
*v3 → v4:* gates annex adopted as acceptance authority; GATE/GOTCHA markers; grep
contract; span trace; LO scaling rule; negative control.
*v2 → v3:* briefing.html added as fifth artifact with QA validation.
*v1 → v2:* SDK Implementation Contract; Learning Evidence; SDK-native tools/hooks;
auth hardening; mock boundary; scope staging.
