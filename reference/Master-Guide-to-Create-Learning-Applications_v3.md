# Master Guide to Create Learning Applications
*A blueprint for building AI-first, adaptive, memory-aware learning applications — version 3.0, revised after architecture QA and preservation review*

> **How to use this guide:** Follow the phases in order for a new course. Each phase has a goal, a rationale, a checklist, and one or more ready-made prompts you can paste directly into Claude. Prompts marked `[ADAPT]` require you to fill in your topic, audience, or depth before using.
>
> **Two tracks:**
> - **Full build** — all phases, in order. Best result. 6–10 weeks for a substantial course.
> - **Minimum Viable Course (MVC)** — Phases 0, 1, A, B, 6, 2, 4 (5 lessons), 7 (Mastery Judge + Socratic Chain only), and 8. Deployable in 2–3 weeks. Add remaining mechanisms iteratively.
>
> **Version 3.0 upgrade:** The original guide is preserved and tightened. This version makes the dependency order explicit, adds the core AI learning loop, elevates calibration from appendix to required design work, adds transfer-project evidence, and adds privacy/accessibility guardrails.

---

## The Big Picture

This guide distils the full lifecycle of building a learning application — from raw idea to a deployed, evaluated, AI-first course. It is grounded in two sources:

1. **Observed practice** across multiple AI-assisted learning projects (Agent 101, Master Course on Agents), where the process evolved iteratively until it worked.
2. **Established frameworks** from instructional design: ADDIE (Analyse → Design → Develop → Implement → Evaluate), Bloom's Taxonomy, Gagné's Nine Events of Instruction, and modern AI-augmented pedagogy principles.

**The core design principle is AI-first.** This means: the AI is the professor. Static content is the structure that gives the AI something to reason against. The student does not experience a course with AI features bolted on — they experience a course whose next move is chosen by an AI professor using a persistent model of the learner.

**Three key innovations in this workflow:**
- **Student Model** — a persistent data structure that tracks not just completion but cognition: where the student guesses, struggles, or coasts
- **Rubric-Calibrated AI Evaluation** — mastery judgments are anchored against exemplars, misconception patterns, and professor-reviewed calibration answers
- **Adaptive Repair Loop** — the system does not merely grade; it asks, pushes back, updates the learner model, and changes what the student sees next

**Supporting innovations:**
- **AI Persona Evaluator** — a named, role-defined persona critiques your course before or after mechanism design
- **Cross-Chapter Intelligence** — the AI ingests the student's weakness profile before every session and generates questions that connect current material to prior gaps

---

## The Core AI Learning Loop

Every AI-first learning application in this guide is built around one loop:

> **Diagnose → Teach → Ask → Evaluate → Repair → Update Model → Adapt Next Experience**

This loop is the minimum viable intelligence of the course. A feature is AI-first only if it changes at least one of these steps. If an AI call merely comments on the student without changing instruction, practice, evaluation, repair, routing, or escalation, it is decorative and should be deferred.

| Loop step | Required artifact | Runtime behaviour |
|---|---|---|
| Diagnose | Learning brief, diagnostic questions, misconception library | Establish starting hypotheses about the learner |
| Teach | Lesson content and tier variants | Present the right explanation at the right depth |
| Ask | Mastery question or project prompt | Require retrieval, explanation, application, or critique |
| Evaluate | Rubric, exemplars, calibration set | Judge understanding without rewarding fluent vagueness |
| Repair | Socratic protocol, targeted explanation rules | Push back, reframe, or explain the specific gap |
| Update Model | Student model schema, concept tags, misconception tags | Store evidence of understanding, weakness, guessing, and resolution |
| Adapt Next Experience | Routing rules, warm-up rules, escalation rules | Change the next lesson, question, project, or professor alert |

**Version 3.0 rule:** No student-model field should exist unless it drives a runtime decision. No AI mechanism should exist unless its output changes the learner's next experience.

---

## Required Artifacts Before Build

Do not start frontend work until these artifacts exist, even in rough form:

1. **Learning Brief** — learner, goal, depth, scope, success definition
2. **Curriculum Architecture** — modules, lessons, objectives, prerequisite order
3. **Concept Tag Vocabulary** — atomic ideas the AI tracks across lessons
4. **Misconception Library** — common wrong mental models the AI must detect
5. **Student Model Schema** — what is remembered, why, and how it changes runtime behaviour
6. **Mastery Rubrics** — criteria, PASS/EDGE/FAIL exemplars, concept tags, misconception tags
7. **Calibration Set** — professor-approved strong, weak, guessing, and misconception answers
8. **Transfer Project Plan** — realistic artifacts learners must produce, critique, or revise
9. **Privacy and Accessibility Requirements** — what is stored, how it can be reset/exported, and how all learners can use the interface

---

## Phase Overview

| # | Phase | Key Output | MVC? |
|---|---|---|---|
| 0 | **Concept & Scoping** | Learning brief — topic, audience, depth, format | ✅ |
| 1 | **Curriculum Architecture** | Module map with learning objectives | ✅ |
| **A** | **AI-First Architecture Design** | Student model schema, AI responsibility map, difficulty tiers | ✅ |
| 6 | **Rubric & Mastery Design** | Per-lesson mastery criteria with concept tags | — |
| **B** | **Student Model & Memory Design** | Weakness profile schema, concept graph, session design | — |
| 2 | **Frontend Design** | Course player UI with student model wired in | ✅ |
| 3 | **Project Scaffolding** | Folder structure, HANDOFF.md, ROADMAP.md | — |
| 4 | **Content Population** | All lessons written and embedded | ✅ (5 lessons for MVC) |
| 4.5 | **Transfer Project & Capstone Design** | Real-world project briefs, critique loops, revision criteria | ✅ (1 project for MVC) |
| 5 | **AI Persona Evaluation** | Multi-dimension scorecard, prioritised recommendations | ✅ |
| 7 | **Mechanism Build** | Feynman, Mastery Judge, Cross-Chapter Q-Gen, Socratic Chain | — |
| **C** | **Adaptive Difficulty Design** | Three-tier content per lesson, routing logic | — |
| 8 | **Navigation & Pedagogy QA** | Smoke-test checklist, pushback verification | — |
| 9 | **Iteration Loops** | Scorecard-driven improvements | — |

**Dependency note:** Phase numbers are kept for continuity with earlier versions of this guide. The build dependency is stricter than the numeric labels: Phase A, Phase 6, and Phase B must happen before Phase 2 if the course is truly AI-first.

**MVC rule:** The minimum viable course should prove the core loop with 5 lessons, 1 transfer project, a working student model, a mastery judge, a Socratic repair chain, and QA against bad answers. Warm-ups, cross-chapter intelligence, and professor escalation can wait until the judgment-and-repair loop is reliable.

**Recommended execution order for a new build:**
1. Phase 0 — Concept & Scoping
2. Phase 1 — Curriculum Architecture
3. Phase A — AI-First Architecture Design
4. Phase B — Student Model & Memory Design
5. Phase 6 — Rubric & Mastery Design
6. Phase 2 — Frontend Design
7. Phase 3 — Project Scaffolding
8. Phase 4 — Content Population
9. Phase 4.5 — Transfer Project & Capstone Design
10. Phase 7 — Mechanism Build
11. Phase C — Adaptive Difficulty Design
12. Phase 5 — AI Persona Evaluation
13. Phase 8 — Navigation & Pedagogy QA
14. Phase 9 — Iteration Loops

---

## Phase 0 — Concept & Scoping

**Goal:** Crystallise *what* the course is, *who* it is for, and *how deep* it goes — before writing a single lesson.

**Why this matters:** The single most common failure in self-built courses is scope drift. You start with "learn Python" and end up with 200 lessons you never finish. A tight brief enforces discipline.

**Checklist:**
- [ ] Topic is specific enough to complete in one course (not a career)
- [ ] Target learner is defined (experience level, prior knowledge, goal)
- [ ] Depth level is set: awareness / practitioner / expert
- [ ] Format decision made: linear / modular / project-gated
- [ ] Estimated lesson count (aim for 20–60 lessons for a substantial course)
- [ ] Success definition: what does the learner *do* differently after completing?

---

### 🔑 Prompt 0 — Learning Brief Generator

```
You are an instructional design strategist. Help me scope a self-paced learning application.

Topic: [ADAPT — e.g., "AI Agent Systems"]
Target learner: [ADAPT — e.g., "Senior consultant, non-coder, wants to apply AI agents in FS strategy work"]
Depth: [ADAPT — awareness / practitioner / expert]
Intended outcome: [ADAPT — e.g., "Understand, evaluate, and recommend agentic AI architectures"]

Produce a one-page Learning Brief with the following sections:
1. Course title (specific, not generic)
2. Learner persona — 3 sentences on who this person is and what they already know
3. Learning outcomes — 5 measurable outcomes using Bloom's Taxonomy verbs (mix levels: remember, understand, apply, analyse, evaluate)
4. Scope decision — what is explicitly OUT of scope and why
5. Format recommendation — linear / modular / project-gated, with rationale
6. Estimated module count and lesson count
7. Success criteria — how will we know the learner has achieved the outcomes?

Be opinionated. If the topic is too broad, say so and suggest a tighter scope.
```

---

## Phase 1 — Curriculum Architecture

**Goal:** Build the full module and lesson map before writing any content.

**Why this matters:** Curriculum structure is an architectural decision. Getting it wrong mid-build means rewriting lessons, not just reordering them. Bloom's Taxonomy should drive lesson sequencing: lower-order cognition (remember, understand) at the start of each module, higher-order (apply, analyse, evaluate) at the end.

**Checklist:**
- [ ] Modules have clear, distinct themes (no overlap)
- [ ] Each module has 3–6 lessons (too few = shallow; too many = exhausting)
- [ ] Each module ends with a mastery check lesson
- [ ] Lesson titles are outcome-oriented, not topic labels (e.g., "Why Agents Fail" not "Failures")
- [ ] A "Level 0 / Mental Models" module exists — calibrates the learner's mental model first
- [ ] A reference module exists — glossary, reading list, project briefs
- [ ] Learning objectives are written per lesson (one sentence, one verb, one outcome)
- [ ] Prerequisites are marked between modules if order matters

---

### 🔑 Prompt 1a — Curriculum Generator

```
You are a senior instructional designer building a self-paced technical course.

Use this Learning Brief as context:
[PASTE YOUR PHASE 0 OUTPUT HERE]

Design the full curriculum for this course. Output a structured curriculum with:

For each MODULE:
- Module number and title
- Module description (2 sentences — what and why)
- Learning objective (one sentence, Bloom's verb)
- Prerequisite modules (if any)

For each LESSON within the module:
- Lesson number and title (outcome-oriented, not topic label)
- Learning objective (one sentence, Bloom's verb)
- Estimated read time (5–15 min)
- Lesson type: Concept / Mechanism / Case Study / Practice / Mastery Check

Rules:
- 3–6 lessons per module
- Every module must end with a Mastery Check lesson
- Include a Level 0 "Mental Models" module that runs first
- Include a Reference module at the end (Glossary, Reading List, Projects)
- Sequence within modules: Concept → Mechanism → Application → Mastery Check
- Do not write lesson content — only structure and objectives

Flag any topics where a beginner's mental model commonly breaks (common misconceptions). These need dedicated "myth-busting" lessons.
```

---

### 🔑 Prompt 1b — Curriculum Depth Review

```
Review this curriculum for a [TOPIC] course targeted at [LEARNER PERSONA].

[PASTE CURRICULUM OUTPUT HERE]

Evaluate it on four dimensions and give a verdict (PASS / FIX / FAIL) for each:

1. COMPLETENESS — Are there important topics missing? Flag gaps.
2. SEQUENCING — Does the order support progressive understanding? Flag any lessons that assume knowledge not yet taught.
3. BLOOM'S BALANCE — Are higher-order objectives (apply, analyse, evaluate) present, or is it all recall?
4. SCOPE DISCIPLINE — Is anything here that should be cut or moved to a separate course?

Output: A structured critique with specific fix recommendations, ordered by priority.
```

---

## Phase A — AI-First Architecture Design

**Goal:** Before writing a line of frontend code, decide exactly what the AI is responsible for and what static content is responsible for. This decision shapes every phase that follows.

**Why this matters:** Most e-learning tools treat AI as a feature layer added to a finished course. That produces a reading list with a chatbot attached. AI-first design inverts this: the AI is the professor; the course content is the structure that gives the AI something to reason against. This phase makes that distinction explicit before any code is written.

**The three responsibilities to assign:**

| Responsibility | Static content handles | AI handles |
|---|---|---|
| Knowledge delivery | Lesson text, diagrams, examples | Adaptive explanations when student is stuck |
| Assessment | Mastery criteria in rubric | Evaluating free-text answers, detecting guessing |
| Personalisation | None | Routing to difficulty tiers, generating cross-chapter questions |
| Escalation | None | Flagging persistent gaps to the professor |

**Difficulty tier design (define before building content):**
Every lesson should have three content tiers. Write them in Phase 4:
- **Standard** — the default lesson for the target learner persona
- **Scaffolded** — a simpler version with more analogies and smaller steps; served when student fails mastery check on the prior lesson
- **Deep-Dive** — extends into mechanism internals or edge cases; served when student is passing comfortably and rapidly

**AI responsibility map — fill this in before Phase 2:**
```
Course: [NAME]
AI is responsible for:
  [ ] Evaluating free-text mastery answers
  [ ] Detecting guessing vs. genuine understanding
  [ ] Generating cross-chapter recall questions
  [ ] Routing to difficulty tiers (Scaffolded / Standard / Deep-Dive)
  [ ] Socratic pushback chain (how many attempts before explaining?)
  [ ] Professor escalation (trigger condition: _______)
  [ ] Session warm-up question (draws from student weakness profile)

Static content is responsible for:
  [ ] Lesson text, structure, diagrams
  [ ] Mastery criteria and rubric exemplars
  [ ] Concept tag vocabulary
  [ ] Difficulty tier variants per lesson
```

**Minimum viable intelligence loop — fill this before implementation:**
```
When the learner opens a lesson:
  AI / app reads: [student model fields]
  App chooses: [content tier or default]

When the learner answers:
  AI reads: [rubric + calibration anchors + student answer]
  AI outputs: [PASS / EDGE / FAIL + private concept/misconception tags]
  App writes: [lessonHistory + weaknessConcepts + misconceptionSignals]

When the learner struggles:
  AI chooses: [Socratic pushback / reframe / targeted explanation]
  App writes: [attempt count + weak tag + repair outcome]

When the next lesson opens:
  App changes: [tier / warm-up / project prompt / escalation]
```

**Decision test:** Every AI field and every AI response must answer, "What happens differently because the system knows this?" If the answer is "nothing," remove the field or defer the feature.

**Checklist:**
- [ ] AI responsibility map is filled in and agreed
- [ ] Three difficulty tiers defined for each lesson (at least in principle)
- [ ] Socratic pushback chain depth decided (recommended: 3 attempts)
- [ ] Professor escalation trigger defined (recommended: 3 consecutive FAIL/EDGE on same concept)
- [ ] Student model schema designed (see Phase B for full design)
- [ ] Concept tag vocabulary drafted (20–50 tags covering the full curriculum)
- [ ] Misconception vocabulary drafted for the 10–20 most common wrong mental models
- [ ] Calibration plan defined: who reviews anchor answers, how many examples, and what "good enough" agreement means
- [ ] Every AI mechanism has a named runtime consequence, not just an output

---

### 🔑 Prompt A — AI-First Architecture Brief

```
I am building an AI-first learning application on the topic: [ADAPT]
Target learner: [ADAPT]
Course size: [ADAPT — number of lessons, modules]

Help me design the AI-first architecture for this course. Produce:

1. AI RESPONSIBILITY MAP — for each of these functions, decide whether AI or static content handles it, and describe the specific behaviour:
   - Knowledge delivery (first exposure to concept)
   - Re-explanation when student is stuck
   - Mastery assessment
   - Guessing detection
   - Adaptive routing (easier/harder content)
   - Cross-chapter recall
   - Professor escalation

2. STUDENT MODEL SCHEMA — a JSON object structure that captures everything the AI needs to personalise the experience. Include fields for: completion, per-lesson answer quality, concept-level weakness tags, guessing signals, session history, difficulty tier assignments.

3. CONCEPT TAG VOCABULARY — 20–40 concept tags that span the full curriculum. These are the atomic units the AI tracks, not lesson titles. Format: tag_name: one-line definition.

4. DIFFICULTY ROUTING LOGIC — plain-language rules for when the AI routes a student to Scaffolded vs. Standard vs. Deep-Dive content. Base this on the student model fields.

5. PROFESSOR ESCALATION SPEC — what triggers an escalation, what the professor receives (the "Professor Alert" format), and what the student sees in the UI while waiting.

Be specific. Avoid vague statements like "the AI adapts to the learner." Name the exact data field that triggers the adaptation and the exact behaviour that results.
```

---

## Phase 2 — Frontend Design

**Goal:** Build the course player UI — the shell that will host all lesson content, navigation, and progress tracking.

**Why this matters:** The UI is infrastructure, not decoration. A well-designed player gives the learner a mental map of where they are in the course, makes progress visible, and stays out of the way of content. Building it once, correctly, saves dozens of hours of rework later.

**Key decisions to make before designing:**
- **Runtime environment:** Local file, localhost server, or embedded artifact (e.g., Cowork artifact)?
- **Content model:** Separate HTML files per lesson, or all content inline in one file?
- **Student model storage:** localStorage (single user) or a backend (multi-student / professor dashboard)?
- **AI interactivity:** None (Phase 1), or AI-powered features via an API?
- **Theme:** Match the learner's context (dark IDE aesthetic for technical courses; light academic for general courses)
- **Privacy boundary:** What learning data is stored, how it can be exported/reset, and whether any sensitive personal data is forbidden
- **Accessibility baseline:** Keyboard access, contrast, readable type, semantic headings, screen-reader labels, and non-colour-only progress signals

> **Critical:** Do NOT use localStorage for completion tracking only. Design the student model schema (Phase A) first, then wire the full schema into localStorage from the start. Retrofitting this later is expensive.

> **Privacy rule:** Store only learning-relevant evidence. Prefer answer snippets and concept tags over full personal narratives unless the learner explicitly chooses to save them. Always provide a visible reset/export path for the student model.

**Checklist:**
- [ ] Sidebar navigation with module and lesson hierarchy
- [ ] Current lesson highlighted; completed lessons marked
- [ ] Progress bar showing overall completion (X/N lessons)
- [ ] Previous / Next navigation buttons
- [ ] Keyboard navigation (← → M for mark-complete)
- [ ] Module-level completion badges
- [ ] Resume on re-open (loads last visited lesson)
- [ ] Responsive enough to use comfortably
- [ ] CSS class system documented for content authors
- [ ] Progress and status are not conveyed by colour alone
- [ ] All controls have accessible labels and visible focus states
- [ ] Student model reset/export option exists
- [ ] The app avoids storing unnecessary sensitive personal data

---

### 🔑 Prompt 2 — Course Player UI Design

```
Design a complete, self-contained single-file course player for a self-paced learning application.

Course details:
- Title: [ADAPT]
- Total lessons: [ADAPT — e.g., 60]
- Module count: [ADAPT — e.g., 13]
- Runtime: [ADAPT — Cowork artifact / localhost / standalone HTML file]
- Theme: [ADAPT — light / dark]
- AI features in scope for Phase 1: None (display only)

Requirements:
1. Single HTML file — HTML, CSS, JavaScript all inline
2. Sidebar: collapsible module list with lesson links; show lesson completion status (✓) and module progress badge (X/N)
3. Header: course title + progress bar (percentage and fraction)
4. Main content area: renders lesson HTML passed in from a CONTENT data object
5. Footer: Previous / Next buttons + Mark Complete button (changes to "Completed ✓" when done)
6. Keyboard nav: ← previous, → next, M = mark complete
7. Progress persistence: localStorage — save completed lesson IDs and last-visited lesson; restore on page load
8. CSS class system for lesson content: define at minimum — lesson container, section heading, blockquote, tip callout, warning callout, takeaway box, mastery criteria list, styled table, ASCII diagram box
9. Light mode with a clean, readable palette (e.g., GitHub Light or similar)

Output: The complete HTML file. Include a comment block at the top listing all CSS classes available for content authors.
```

---

## Phase 3 — Project Scaffolding

**Goal:** Create a consistent, navigable project structure so that future sessions can be resumed without context-setting overhead.

**Why this matters:** AI-assisted projects are multi-session by nature. Without structure, you spend the first 20 minutes of every session re-establishing context. A good scaffold means Claude (or any collaborator) can read HANDOFF.md and be fully operational in under 2 minutes.

**Standard folder structure:**
```
project-root/
├── HANDOFF.md          ← Session continuity — always read first, update last
├── CLAUDE.md           ← Project instructions for Claude
├── docs/
│   ├── PRD.md          ← Requirements and goals
│   └── ROADMAP.md      ← Phases, milestones, status
├── curriculum/         ← Module definitions (markdown)
│   └── {module-name}/
│       └── module.md   ← Lesson titles, order, objectives
├── app/                ← The web application
│   └── course.html     ← Course player (single file if embedded content model)
├── evaluations/        ← Persona evaluation reports and rubrics
│   ├── rubrics/        ← Per-lesson mastery rubrics
│   └── {persona}_evaluation_v1.md
├── memory/
│   └── decisions.md    ← Key decisions and rationale
└── prompts/            ← Reusable prompts used in this project
```

**Checklist:**
- [ ] HANDOFF.md exists and is current
- [ ] ROADMAP.md reflects actual phase status
- [ ] decisions.md logs every non-obvious choice with rationale
- [ ] Curriculum files are in `curriculum/` and treated as source of truth
- [ ] Prompts that worked are saved to `prompts/` for reuse

---

### 🔑 Prompt 3 — HANDOFF.md Template

```
Generate a HANDOFF.md file for this project.

Project name: [ADAPT]
Current date: [DATE]
What was done this session: [ADAPT — brief bullet summary]
Current state — what exists and what doesn't: [ADAPT]
Immediate next steps in priority order: [ADAPT]
Open questions / decisions pending: [ADAPT]

Format: Clean markdown. Sections: Last Session, Current State (two sub-lists: exists / does not exist), Next Steps (priority ordered), Open Questions, Quick Context (2-sentence summary for cold-start). Treat it as documentation for a colleague who has never seen this project.
```

---

## Phase 4 — Content Population

**Goal:** Write and embed all lesson content into the course player.

**Why this matters:** Content is the hardest part to generate at quality. The risk here is writing too fast and getting shallow, generic content that doesn't actually teach. The cure is to hold yourself to a lesson template that forces depth.

**The lesson template (use for every lesson):**
1. **Eye-line** — one sentence that tells the learner exactly what they will understand by the end
2. **Lead paragraph** — the intuition, stated plainly (no jargon on first use)
3. **Mechanism** — how it actually works (with a real example, not a toy example)
4. **Contrast** — what it is NOT (clears up the most common misconception)
5. **Diagram or table** — a visual aid where useful (ASCII diagram if in-code)
6. **Takeaway box** — 2–3 sentences the learner should be able to say back to someone else
7. **Mastery criteria** — 3–5 things a learner who truly understood this lesson can do

**Checklist:**
- [ ] Every lesson has a takeaway box
- [ ] Every lesson surfaces at least one "why this matters" signal
- [ ] Mastery check lessons contain only criteria — no new content
- [ ] Content reads at the right level for the target learner (no patronising simplification; no unexplained jargon)
- [ ] Examples are domain-appropriate (use the learner's world, not generic examples)

---

### 🔑 Prompt 4 — Lesson Content Generator

```
Write a lesson for a self-paced course on [TOPIC].

Lesson title: [ADAPT]
Learning objective: By the end of this lesson, the learner will be able to [ADAPT — Bloom's verb + outcome]
Target learner: [PASTE LEARNER PERSONA]
Prior lessons in this module: [ADAPT — list what they've already covered]

Write the lesson following this structure exactly:
1. **Eye-line** — one sentence hook that states what the learner will walk away knowing
2. **The intuition** — explain the concept as you would to a smart generalist; no jargon without definition
3. **The mechanism** — how it actually works; include a concrete, domain-relevant example
4. **The contrast** — what this concept is NOT; address the single most common misconception
5. **A diagram or table** — use ASCII art or a markdown table; only if it adds clarity
6. **Takeaway** — 2–3 sentences the learner should be able to say back to someone who has never heard of this
7. **Mastery criteria** — 3–5 specific things a learner who understood this lesson can do or explain

Output: HTML using these CSS classes:
- .lc-wrap (outer container)
- .lc-hd + .lc-ey + h1 + .lc-lead (header block)
- h2 (section heading)
- .lc-tk (takeaway box — wrap label in <b>YOUR NAME'S TAKEAWAY</b>)
- .lc-mc (mastery criteria list — numbered)
- .lc-tip / .lc-warn (callout boxes)
- .dia (ASCII diagram in monospace)
- table.t (styled table)

Do not write generic content. If you do not know enough about the topic to write with specificity, say so.
```

---

## Phase 4.5 — Transfer Project & Capstone Design

**Goal:** Define the real-world artifacts learners must produce, critique, revise, or defend to prove that lesson-level understanding transfers into practical judgment.

**Why this matters:** A learner can pass individual mastery checks and still fail at real application. AI-first learning applications need evidence beyond micro-answers. Transfer projects force the learner to use concepts in messy, realistic scenarios where there is no single obvious answer.

**The project loop:**
1. **Commission** — learner writes a brief, spec, plan, diagnosis, or design decision
2. **Critique** — AI evaluates the artifact against a project rubric
3. **Pressure-test** — AI asks what could fail, what is assumed, and what must be measured
4. **Revise** — learner improves the artifact
5. **Compare** — AI compares v1 and v2 and updates concept/misconception tags

**Project evidence should test at least one of these transfer behaviours:**
- Explain a concept to a stakeholder
- Choose between design alternatives
- Diagnose a failure mode
- Critique a vendor, tool, architecture, or answer
- Produce a specification another AI or human could implement
- Revise an artifact after receiving feedback

**Checklist:**
- [ ] Every major module has at least one transfer task or project checkpoint
- [ ] At least one project requires critique, not just creation
- [ ] Project rubrics include concept tags and misconception tags
- [ ] Project feedback updates the same student model as lesson mastery checks
- [ ] The capstone requires the learner to revise an artifact after AI critique
- [ ] MVC includes at least one realistic project, even if only 5 lessons are built

---

### 🔑 Prompt 4.5 — Transfer Project Designer

```
Design a transfer project for this AI-first learning application.

Course topic: [ADAPT]
Target learner: [ADAPT]
Relevant modules/lessons: [ADAPT]
Concept tags to test: [ADAPT]
Known misconception tags to surface: [ADAPT]

Produce:
1. PROJECT BRIEF — a realistic scenario where the learner must create, critique, diagnose, or revise an artifact
2. LEARNER DELIVERABLE — exactly what the learner must submit
3. PROJECT RUBRIC — 5–7 criteria, each mapped to concept tags and misconception tags
4. AI CRITIQUE PROTOCOL — how the AI evaluates the first submission without over-helping
5. REVISION PROMPT — what the learner must improve in v2
6. STUDENT MODEL UPDATES — which fields should be updated after the project

Rules:
- The project must require transfer, not recall
- The task should feel like something the target learner would actually do
- Include at least one plausible wrong answer pattern the rubric must catch
- Do not make the project depend on skills outside the course scope
```

---

## Phase 5 — AI Persona Evaluation

**Goal:** Evaluate the full course through the eyes of a named, role-defined persona before building the interactive mechanism layer.

**Why this matters:** This is the key innovation in this workflow. Most courses are evaluated by their creator — who knows the content and unconsciously fills in gaps the learner cannot. A persona evaluation forces you to see the course from the outside. It catches structural weaknesses, pedagogical gaps, and missing content while it is still cheap to fix. The persona should be someone who will stress-test the course, not validate it.

**Persona design principles:**
- Give the persona a name, a background, and a specific learning goal
- Define their prior knowledge precisely (what they know and don't know)
- Give them a critical disposition — they are there to find problems, not praise good work
- Ask for a scorecard with numeric grades, not just qualitative feedback
- Ask for prioritised recommendations — 15–20 specific, actionable items

**Evaluation dimensions (standard scorecard):**
| Dimension | What it measures |
|---|---|
| Content accuracy | Is what's being taught actually correct? |
| Conceptual depth | Does it go beyond surface recall to mechanism understanding? |
| Pedagogical sequencing | Does each lesson build on the prior? No assumed knowledge? |
| Clarity and prose | Is it readable for the target learner? |
| Example quality | Are examples domain-appropriate and non-trivial? |
| Mastery criteria rigour | Are the criteria specific enough to be evaluated? |
| Coverage completeness | Are important topics missing or underserved? |
| Engagement | Would the learner stay motivated across the full course? |

---

### 🔑 Prompt 5a — Persona Evaluator

```
You are [PERSONA NAME], [PERSONA ROLE AND BACKGROUND — 2 sentences].

Your learning goal: [ADAPT — what the persona is trying to achieve by taking this course]
Your prior knowledge: You know [ADAPT — what they know]. You do NOT yet know [ADAPT — what they don't].
Your disposition: You are a demanding learner. You notice when explanations are shallow, when examples are generic, and when a lesson claims to teach something but doesn't actually deliver understanding.

Review the full course below. Evaluate it across the following 8 dimensions. For each dimension:
- Give a numeric grade: 1.0 (poor) to 5.0 (excellent) in 0.5 increments
- Write 2–4 sentences of specific justification
- List the top 2 specific fix recommendations for that dimension

After the dimension scores:
- Calculate an overall weighted average (equal weights)
- Write a 3-paragraph "Honest Assessment" — what works, what fails, what would make you abandon the course halfway through
- List 15–20 prioritised recommendations (numbered, most impactful first), each with a specific location (lesson ID) and a concrete fix, not a vague suggestion
- Flag 3–5 "hidden gaps" — things the course does not teach that the learner will need to know to actually apply this material

[PASTE FULL COURSE CONTENT OR CURRICULUM HERE]
```

---

### 🔑 Prompt 5b — Second-Pass Evaluation (Post-Fix)

```
You are [SAME PERSONA AS 5a].

Below is the original evaluation you gave this course:
[PASTE PHASE 5a OUTPUT]

The course has now been revised. Below are the specific changes made:
[ADAPT — list the changes made, referencing recommendation numbers]

Re-evaluate only the dimensions and recommendations that were addressed. For each:
- Was the fix substantively delivered? (YES / PARTIAL / NO)
- Has the grade for that dimension changed? If so, new grade and why.
- Any new issues introduced by the fix?

Output: A concise re-evaluation report (not a full redo). End with an updated overall grade.
```

---

## Phase 6 — Rubric & Mastery Design

**Goal:** For each lesson, write a mastery rubric — a structured set of criteria and exemplar answers that define what PASS looks like.

**Why this matters:** Without rubrics, the AI-powered mastery evaluator (Phase 7) has no ground truth to evaluate against. It will hallucinate pass/fail decisions. Rubrics also force you to be specific about what you actually want the learner to be able to do — which often reveals that your mastery criteria from Phase 4 were too vague.

**Version 3.0 calibration rule:** Rubrics are necessary but not sufficient. Every high-stakes rubric needs calibration anchors: professor-approved examples of strong answers, weak-but-fluent answers, guessing answers, and misconception-driven answers. The AI evaluator should be tested against these anchors before it is allowed to update the student model.

**Rubric format (locked):**
```
Lesson ID: {id}
Lesson title: {title}

CRITERIA (3–5):
1. [Criterion — one specific thing the learner can do or explain]
   PASS: [Exemplar — ≤150 words, plausible student voice, not a textbook answer]
   FAIL: [Anti-exemplar — plausible-sounding but wrong; not a strawman]
   EDGE: [Edge case that could go either way; describe how to decide]

JUDGE PROTOCOL:
- Only PASS / FAIL / EDGE as outputs
- PASS requires all criteria met
- EDGE triggers a follow-up question (ask the student to clarify one specific point)
- Never explain why an answer fails — only ask the follow-up question

CALIBRATION ANCHORS:
- STRONG: [answer that should clearly pass]
- FLUENT BUT WEAK: [answer that sounds articulate but misses the mechanism]
- GUESSING: [short or vague answer that should fail even if it uses a few keywords]
- MISCONCEPTION: [answer that reveals a named wrong mental model]
```

**Checklist:**
- [ ] Every lesson has 3–5 criteria (not 1–2, not 8+)
- [ ] Pass exemplars are ≤150 words (longer = the bar is too high for real students)
- [ ] Fail exemplars are plausible-sounding, not obviously wrong (strawmen don't catch real misunderstandings)
- [ ] EDGE protocol is defined (what triggers a follow-up?)
- [ ] Rubrics reference only content already taught in the course (no knowledge injection)
- [ ] Each major rubric has at least 4 calibration anchors
- [ ] Calibration anchors include at least one fluent-but-wrong answer
- [ ] Each rubric maps criteria to concept tags and misconception tags
- [ ] Low-confidence judgments are handled as EDGE, not hard PASS/FAIL

---

### 🔑 Prompt 6 — Mastery Rubric Generator

```
Write a mastery evaluation rubric for the following lesson.

Lesson ID: [ADAPT]
Lesson title: [ADAPT]
Learning objective: [ADAPT]
Lesson content summary: [PASTE OR SUMMARISE LESSON CONTENT]

Output a rubric following this format exactly:

---
Lesson ID: {id}
Lesson title: {title}

CRITERIA:
[3–5 criteria. For each:]
{N}. {Criterion — one specific, testable claim about what the learner can do}
   PASS: {≤150 word exemplar in a plausible student voice — not textbook prose, not perfect, just clearly correct}
   FAIL: {Plausible-sounding answer that sounds like it might be right but reveals a specific misunderstanding}
   EDGE: {A borderline answer. Describe what about it is ambiguous and what follow-up question resolves it.}

JUDGE PROTOCOL:
- Output only: PASS / FAIL / EDGE
- PASS requires all criteria met
- EDGE → ask one specific follow-up question (do not explain why it's an edge)
- Never reveal which criterion failed

INTENTIONAL CONTENT SURFACE:
[List the 2–3 specific concepts from the lesson that these criteria are designed to surface. This keeps rubrics honest — they must test what was actually taught.]

CALIBRATION ANCHORS:
- STRONG: {A plausible learner answer that should pass}
- FLUENT BUT WEAK: {A polished answer that should fail or edge because it lacks mechanism understanding}
- GUESSING: {A short/vague answer that should fail}
- MISCONCEPTION: {An answer that reveals a named misconception}

TAG MAP:
- Concept tags tested: {list}
- Misconception tags watched: {list}
---

Rules:
- All exemplars ≤150 words
- FAIL exemplars must be plausible, not obviously wrong
- Do not introduce concepts not covered in the lesson
- If the lesson is a Mastery Check, consolidate criteria across the module's lessons
- Include calibration anchors; these are used later to test evaluator consistency
```

---

## Phase 7 — Mechanism Build (AI Features)

**Goal:** Build four distinct AI mechanisms: Mastery Judge, Feynman Evaluator, Cross-Chapter Question Generator, and Socratic Pushback Chain. Each has a separate prompt, a separate output format, and a separate trigger condition.

**Why this matters:** Each mechanism serves a different cognitive function. Conflating them into one "AI layer" produces a system that does all four poorly. The Mastery Judge is strict and binary. The Feynman Evaluator is conversational and probing. The Question Generator requires access to the student model. The Socratic Chain escalates in three defined steps. These must be separate.

**The four mechanisms:**

| Mechanism | Trigger | Output | Prompt |
|---|---|---|---|
| **Mastery Judge** | Student submits free-text answer | PASS / FAIL / EDGE: [follow-up] | Prompt 7 |
| **Feynman Evaluator** | Student clicks "Explain this to me" | Conversational probe (not a grade) | Prompt 7b |
| **Cross-Chapter Q-Gen** | Session warm-up, or post-pass | A question connecting weak prior concept to current lesson | Prompt B2 |
| **Socratic Chain** | EDGE or FAIL verdict → attempt 2 or 3 | Probe / reframe / explain (by attempt number) | Prompt B3 |

**Architecture pattern (for Cowork artifact):**
```javascript
// Mastery Judge — reads student model, writes verdict back
async function evaluateMastery(lessonId, studentAnswer, attemptNumber) {
  const rubric = RUBRICS[lessonId];
  const studentModel = JSON.parse(localStorage.getItem('student_model'));
  
  const prompt = buildMasteryPrompt(rubric, studentAnswer, attemptNumber);
  const verdict = await window.cowork.askClaude(prompt, []);
  
  // Write verdict to student model
  updateStudentModel(studentModel, lessonId, verdict, studentAnswer);
  localStorage.setItem('student_model', JSON.stringify(studentModel));
  
  return verdict;
}

// Cross-chapter Q-Gen — reads weakness profile, generates question
async function generateCrossChapterQuestion(lessonId) {
  const studentModel = JSON.parse(localStorage.getItem('student_model'));
  const weakConcepts = getUnresolvedWeaknesses(studentModel);
  const currentConceptTags = LESSONS[lessonId].conceptTags;
  
  const prompt = buildCrossChapterPrompt(weakConcepts, currentConceptTags, lessonId);
  return await window.cowork.askClaude(prompt, []);
}
```

**Guessing Detector pattern:**
```javascript
function detectGuessing(studentModel, lessonId, verdict, answer) {
  const previousLesson = getPreviousLessonId(lessonId);
  const prevHistory = studentModel.lessonHistory[previousLesson];
  
  // Signal 1: passed current lesson at attempt 1 after failing previous at attempt 3
  if (verdict === 'PASS' && answer.attempt === 1) {
    if (prevHistory && prevHistory.verdicts.slice(-1)[0] === 'FAIL' 
        && prevHistory.attempts >= 3) {
      return true;  // Implausible improvement — flag as guess
    }
  }
  // Signal 2: answer too short for a complex question
  if (answer.text.split(' ').length < 25 && LESSONS[lessonId].complexity === 'high') {
    return true;
  }
  return false;
}
```

**Checklist:**
- [ ] Mastery Judge and Feynman Evaluator are on separate prompts (never the same call)
- [ ] Mastery Judge output is strictly constrained (PASS / FAIL / EDGE: [question] only)
- [ ] Student model is written after every AI interaction, not just lesson completion
- [ ] Guessing detector is implemented and flags written to `student.guessingSignals`
- [ ] Socratic Chain has a defined depth (3 attempts maximum)
- [ ] After attempt 3 failure, Professor Alert is generated and stored in `student.professorAlerts`
- [ ] All four mechanisms calibrated on 5 real answers before deployment (see Phase 8)
- [ ] Cross-chapter Q-Gen only fires when `weaknessConcepts` has ≥ 1 unresolved entry
- [ ] The evaluator is regression-tested against calibration anchors after prompt changes
- [ ] If confidence is low, the mechanism returns EDGE rather than forcing PASS or FAIL

---

### 🔑 Prompt 7 — Mastery Evaluator System Prompt

```
You are a strict mastery evaluator for a self-paced technical course.

Your role: evaluate whether the learner's free-text answer demonstrates genuine understanding of the lesson concepts — not surface recall, not parroting definitions.

RUBRIC FOR THIS LESSON:
[PASTE LESSON RUBRIC FROM PHASE 6]

CALIBRATION ANCHORS FOR THIS LESSON:
[PASTE STRONG / FLUENT BUT WEAK / GUESSING / MISCONCEPTION ANCHORS]

EVALUATION PROTOCOL:
1. Read the student's answer against each criterion in the rubric
2. Compare the answer against the calibration anchors before deciding
3. If ALL criteria are met: output PASS
4. If any criterion is clearly failed: output FAIL
5. If borderline or evaluator confidence is low: output EDGE: [one specific follow-up question that would resolve the ambiguity]

RULES:
- Do NOT explain which criterion failed
- Do NOT praise the student
- Do NOT give hints or rephrase the question
- If the student has NOT answered (short, off-topic, or "I don't know"): output FAIL
- Output format: exactly one of — PASS | FAIL | EDGE: [follow-up question]
- Do not reward fluent vagueness; polished wording without mechanism understanding is FAIL or EDGE

STUDENT ANSWER:
[STUDENT INPUT INJECTED HERE AT RUNTIME]
```

---

## Phase B — Student Model & Memory Design

**Goal:** Design the data structure that makes the AI remember the student — not just what they completed, but where they guessed, where they struggled, and what concepts remain weak across sessions.

**Why this matters:** Without a student model, every session starts from zero. The AI cannot ask a question that connects Chapter 7 to a gap the student showed in Chapter 3. It cannot detect a student who is coasting through lessons without truly understanding them. The student model is what transforms the AI from a rubric-runner into a digital professor.

**The student model schema:**
```json
{
  "studentId": "unique-id",
  "courseId": "course-name",
  "lastSession": "ISO-timestamp",
  "totalSessions": 0,
  "completedLessons": [],
  "difficultyAssignments": {
    "lesson-id": "standard | scaffolded | deep-dive"
  },
  "lessonHistory": {
    "lesson-id": {
      "attempts": 1,
      "verdicts": ["EDGE", "PASS"],
      "answerSnippets": ["first 100 chars of each answer"],
      "guessingFlag": false,
      "conceptsTagged": ["concept-tag-1", "concept-tag-2"],
      "timestamp": "ISO-timestamp"
    }
  },
  "weaknessConcepts": {
    "concept-tag": {
      "failCount": 0,
      "edgeCount": 0,
      "lastSeen": "lesson-id",
      "resolved": false
    }
  },
  "misconceptionSignals": {
    "misconception-tag": {
      "evidenceCount": 0,
      "relatedConceptTags": ["concept-tag"],
      "lastSeen": "lesson-id",
      "resolved": false,
      "evidenceSnippets": ["short answer evidence only"]
    }
  },
  "guessingSignals": ["lesson-id-list"],
  "professorAlerts": [],
  "sessionLog": [
    {
      "date": "ISO-date",
      "lessonsAttempted": [],
      "crossChapterQuestionsAsked": []
    }
  ]
}
```

**Misconception library pattern:**
Concept tags name the topic area; misconception tags name the wrong mental model. Both are needed. A student can be weak on `memory-systems`, but the useful teaching signal is more specific: `long-context-solves-memory`, `retrieval-equals-memory`, or `memory-is-just-chat-history`.

```
misconception-tag:
  conceptTags: [related concept tags]
  description: [the wrong belief in one sentence]
  commonSurfaceForm: [how it appears in student answers]
  repairStrategy: [analogy, counterexample, project task, or Socratic question]
```

**Guessing detection signals (define at least two):**
- Answer is correct but uses terminology not introduced in the course up to this point
- Student passed this lesson at attempt 1 but failed the prior lesson at attempt 3 (implausible jump)
- Answer length is < 20 words on a deep-mechanism question (too short to have reasoned through it)
- Response time < 30 seconds on a lesson marked "complex" (too fast for genuine engagement)

**The session warm-up pattern:**
Every session should start with one warm-up question generated from the student's `weaknessConcepts` object. This replaces the "start where you left off" UX with "start where you *should* have left off."

**Cross-chapter question generation logic:**
```
Before generating a question for lesson N:
1. Read student.weaknessConcepts — all concepts where failCount > 0 and resolved = false
2. Check if any weak concept has a dependency relationship to lesson N's concept tags
3. If yes: generate a question that requires applying the weak concept in the context of lesson N's topic
4. If no: generate a standard mastery question for lesson N
```

**Professor Alert format:**
```
STUDENT ALERT — [Student ID] — [Date]
Persistent gap detected: [concept-tag]
Lessons affected: [lesson-id list]
Pattern: [1-sentence description — e.g., "Student consistently confuses X with Y"]
Evidence: [2-3 verbatim answer snippets]
Suggested professor action: [specific intervention, not generic advice]
```

**Checklist:**
- [ ] Student model schema defined and matches Phase A output
- [ ] localStorage write happens after every AI interaction, not just lesson completion
- [ ] Concept tag vocabulary is shared between rubrics (Phase 6) and student model
- [ ] Misconception tags are shared between rubrics, projects, and student model
- [ ] Guessing signals are defined and detectable from observable answer properties
- [ ] Professor Alert trigger condition is coded (not just described)
- [ ] Session warm-up question prompt is written (see Prompt B)
- [ ] Cross-chapter question logic is written as a prompt (see Prompt B2)
- [ ] Every stored field has a documented runtime consequence

---

### 🔑 Prompt B1 — Session Warm-Up Question Generator

```
You are a professor who knows this student well.

STUDENT WEAKNESS PROFILE:
[INJECT student.weaknessConcepts object here]

CURRENT SESSION — Lesson about to be studied:
Title: [ADAPT]
Core concept: [ADAPT]
Concept tags for this lesson: [ADAPT]

Generate one warm-up question for the start of this session. The question must:
1. Draw from a concept in the student's weakness profile (failCount > 0, resolved = false)
2. Connect that weak concept to something relevant to today's lesson
3. Be specific — no generic "what do you remember about X?" questions
4. Be answerable in 2–4 sentences by a student who truly understood the prior material

After the question, add a private note (not shown to student) in [brackets]:
[EVALUATOR NOTE: This question targets [concept-tag]. A correct answer requires [specific mechanism or distinction]. Flag EDGE or FAIL if the student [specific failure mode to watch for].]

Output only the question and the evaluator note. Nothing else.
```

---

### 🔑 Prompt B2 — Cross-Chapter Intelligence Question Generator

```
You are generating a question for a student in an AI-powered learning application.

STUDENT PROFILE:
- Current lesson: [lesson-id] — [lesson title]
- Current lesson concept tags: [ADAPT]
- Weak concepts from prior chapters (unresolved):
  [INJECT weaknessConcepts entries where resolved = false]
- Lessons where guessing was flagged: [INJECT guessingSignals list]

COURSE CONCEPT DEPENDENCY MAP:
[INJECT a brief dependency map: "concept-A requires concept-B; concept-C is an application of concept-A" etc.]

TASK: Generate one cross-chapter integration question that:
1. Requires the student to apply a weak prior concept to explain something in the current lesson
2. Cannot be answered correctly by someone who only read today's lesson — they must draw on the prior chapter
3. Tests mechanism understanding, not recall
4. Is specific to this student's actual gap (not a generic cross-topic question)

Format:
QUESTION: [the question]
WEAK CONCEPT TARGETED: [concept-tag]
CORRECT ANSWER REQUIRES: [what the student must demonstrate to pass]
GUESSING INDICATOR: [what a correct-sounding but hollow answer would look like]
```

---

### 🔑 Prompt B3 — Socratic Pushback Chain

```
You are a Socratic tutor. A student has just answered a mastery question and their answer was evaluated as EDGE or FAIL.

LESSON: [ADAPT]
MASTERY CRITERION BEING TESTED: [PASTE SPECIFIC CRITERION]
STUDENT'S ANSWER: [INJECT student answer]
EVALUATION: [EDGE / FAIL]
ATTEMPT NUMBER: [1 / 2 / 3]

PROTOCOL BY ATTEMPT:
- Attempt 1: Ask one probing question that targets the specific gap without revealing what the gap is. The question should force the student to reason about the mechanism, not recall a definition.
- Attempt 2: Reframe the scenario. Give the student a concrete, novel situation and ask them to apply the concept to it. Do not re-ask the original question.
- Attempt 3: If still failing — give a targeted explanation of only the specific gap (not the full lesson). Then ask the student to restate the concept in their own words one final time.

Output only the response for the current attempt number. Do not explain the protocol to the student. Do not say "attempt 1 of 3." Just respond naturally, as a professor would.
```

---

## Phase C — Adaptive Difficulty Design

**Goal:** Design the rules and content variants that allow the course to adjust its depth based on how the student is performing, lesson by lesson.

**Why this matters:** A fixed-difficulty course serves no one well. The student who is struggling falls further behind each lesson; the student who is ahead gets bored and disengages. Adaptive difficulty is what makes the course feel like it was designed specifically for this student — because at runtime, it was.

**The three-tier model:**

| Tier | When it triggers | What it delivers |
|---|---|---|
| **Scaffolded** | Student failed prior lesson mastery check (at all 3 attempts), OR fail rate > 60% in current module | Simpler analogies, smaller steps, more concrete examples, fewer concepts per lesson |
| **Standard** | Default — no signal either way | The planned lesson as written |
| **Deep-Dive** | Student passed last 3 lessons at attempt 1, prerequisite tags are resolved, and answers show mechanism/application quality | Extended mechanism, edge cases, cross-domain connections, open-ended synthesis question |

**Routing decision tree (in pseudocode):**
```
function getContentTier(studentModel, lessonId):
  recentFailRate = calculateFailRate(studentModel, last=3)
  lastLessonVerdict = studentModel.lessonHistory[previousLesson].verdicts[-1]
  passingStreak = countConsecutivePasses(studentModel)
  
  if lastLessonVerdict == "FAIL" AND recentFailRate > 0.5:
    return "scaffolded"
  elif passingStreak >= 3 AND averageAttempts(last=3) == 1 AND prerequisiteTagsResolved(lessonId):
    return "deep-dive"
  else:
    return "standard"
```

**Routing caution:** Do not use answer length alone as a proxy for understanding. Long answers can be vague, and concise answers can be excellent. Use answer quality, concept resolution, misconception absence, and attempt history as the primary signals.

**Content authoring for three tiers:**
When writing lessons in Phase 4, write the Standard tier first, then:
- **Scaffolded variant:** Add 2–3 more concrete analogies. Break each step into smaller sub-steps. Remove the most abstract mechanism section. Add a "What this is NOT" paragraph.
- **Deep-Dive variant:** Add a section on edge cases and failure modes. Add one cross-domain connection. Replace the takeaway box with an open-ended synthesis question: "Given what you now know about X, how would you design a system that..."

**Engagement retention signals (monitor these):**
- Rising EDGE rate across consecutive lessons → student is at ceiling; route to Scaffolded or slow down
- Passing too fast (below expected reading time) → flag as potential guessing, run a surprise cross-chapter question
- Long gap between sessions (> 7 days) → session starts with two warm-up questions from weakness profile, not the next lesson

**Checklist:**
- [ ] Routing logic is implemented in the course player JS
- [ ] Every lesson has all three tier variants written (or planned with a Phase 4 annotation)
- [ ] Tier assignment is stored in the student model (`difficultyAssignments` field)
- [ ] Engagement signals are being written to the student model in real-time
- [ ] Deep-Dive tier includes at least one open-ended synthesis question
- [ ] Scaffolded tier removes, not just simplifies, the most complex section

---

### 🔑 Prompt C1 — Three-Tier Lesson Variant Generator

```
I have written a Standard-tier lesson. Generate the Scaffolded and Deep-Dive variants.

STANDARD LESSON:
[PASTE FULL LESSON CONTENT]

Target learner persona: [ADAPT]
Core concept of this lesson: [ADAPT]
Concept tags: [ADAPT]

SCAFFOLDED VARIANT rules:
- Same learning objective, lower abstraction
- Replace any technical terminology introduced without analogy with an analogy first
- Break the mechanism explanation into numbered micro-steps (no step should require more than one inference)
- Add a "What this is NOT" paragraph that addresses the single most common misconception
- Remove the most complex mechanism section and note: "[Deep content moved to Standard tier]"
- Keep the takeaway box but simplify to 2 sentences

DEEP-DIVE VARIANT rules:
- Same core concept, extended into edge cases and failure modes
- Add a section: "Where this breaks down" — 2–3 specific conditions where the mechanism fails or produces unexpected results
- Add one cross-domain connection: how does this concept appear in a different field or system?
- Replace the standard takeaway box with: "Synthesis question — Given what you now know about [concept], how would you approach [novel scenario that requires applying the concept in a new context]?"
- Do not add new foundational content — only extend the existing mechanism

Output both variants in the same HTML format as the original lesson.
```

---

### 🔑 Prompt C2 — Engagement Drift Detector

```
Review this student's session log and produce an engagement risk assessment.

STUDENT MODEL (relevant fields):
- lessonHistory: [INJECT]
- weaknessConcepts: [INJECT]
- sessionLog: [INJECT]
- guessingSignals: [INJECT]

Assess across four dimensions:

1. STRUGGLE SIGNAL — Is the student's fail/edge rate rising, holding, or falling across the last 5 lessons?
2. COAST SIGNAL — Is the student passing too quickly? (Average time-per-lesson below expected, or first-attempt pass rate > 90%)
3. DRIFT SIGNAL — Has the gap between sessions increased? Is engagement frequency declining?
4. GUESSING SIGNAL — Are guessing flags concentrated in specific modules or concept tags?

For each dimension: status (GREEN / AMBER / RED) and a one-sentence action recommendation.

Final output: a plain-language "Instructor Note" — 3 sentences max — that a professor could read in 10 seconds and know exactly what to do.
```

---

## Phase 8 — Navigation & Pedagogy QA

**Goal:** Verify that the completed course works end-to-end — navigation, persistence, content rendering, and pedagogical responsiveness.

**Why this matters:** A course that loses progress on restart, breaks on certain lesson IDs, or accepts any answer as PASS is worse than no course — it creates false confidence. QA must be deliberate, not incidental.

**Navigation smoke-test checklist:**
- [ ] Welcome screen renders correctly on first open
- [ ] All modules and lessons appear in the sidebar
- [ ] Clicking any lesson loads its content
- [ ] Mark Complete updates sidebar ✓, module badge, and progress bar
- [ ] Previous / Next navigation moves through all lessons in order
- [ ] Keyboard nav works (← → M)
- [ ] Fully quit app and reopen: progress is preserved
- [ ] Last-visited lesson is restored on reopen
- [ ] Student model export/reset works
- [ ] Focus states are visible and all controls are keyboard reachable
- [ ] Progress/status remains understandable without colour cues

**Pedagogy QA checklist:**
- [ ] AI evaluator rejects shallow answers (test with 1–2 sentence non-answers)
- [ ] AI evaluator accepts correct but imperfectly-worded answers
- [ ] EDGE cases trigger follow-up questions, not PASS/FAIL
- [ ] Feynman explainer distinguishes "reciting a definition" from "explaining the mechanism"
- [ ] No lesson's mastery criteria can be passed by Googling the title and reading the first paragraph
- [ ] Calibration anchors produce the expected verdicts
- [ ] Fluent-but-wrong answers are caught
- [ ] Misconception-tagged answers update the student model correctly
- [ ] Transfer projects require revision, critique, or design judgment
- [ ] Every stored student-model field has at least one tested runtime effect

---

### 🔑 Prompt 8a — Student Comprehension Pushback Test

```
You are a student who has just completed [LESSON TITLE] in a course on [TOPIC].

Your understanding: [ADAPT — describe partial or surface-level understanding; enough to sound plausible but not actually demonstrate mechanism knowledge]

Attempt to pass the mastery check for this lesson. Give your answer in 100–150 words, in the voice of a student who read the lesson but didn't deeply engage with the mechanism.

After your answer, step out of the student role and assess: Would a well-designed rubric catch that this answer lacks genuine understanding? What is the specific gap it exploits?
```

---

### 🔑 Prompt 8b — Pedagogy Audit (Full Course)

```
Audit the pedagogy of this learning application.

Course topic: [ADAPT]
Target learner: [ADAPT]

Evaluate across 5 dimensions:

1. SCAFFOLDING — Does each lesson build on what came before? Are there knowledge jumps?
2. ACTIVE RECALL — Does the course force the learner to retrieve information, or does it allow passive reading?
3. FEEDBACK LOOPS — How quickly does the learner know if they've understood something?
4. SPACED REPETITION — Are key concepts revisited across modules?
5. TRANSFER — Are learners given the chance to apply concepts to new situations, or only to practice in the same context?

For each dimension: grade (1–5), 2-sentence justification, one specific improvement.

[PASTE COURSE STRUCTURE OR CONTENT SAMPLE]
```

---

## Phase 9 — Iteration Loops

**Goal:** Use the outputs of Phase 5 (persona scorecard) and Phase 8 (QA audit) as a structured backlog for improvement.

**The iteration loop:**
1. Take the ranked recommendations list from Phase 5a
2. Assign each recommendation to a phase (content fix, mechanism fix, structure fix)
3. Execute in priority order — highest impact first
4. After a batch of fixes, run Phase 5b (second-pass evaluation) to verify improvement
5. Never mark a recommendation as done without re-running the specific rubric or QA check that would catch it

**Checklist:**
- [ ] Every recommendation has a specific lesson ID and a concrete fix (not "improve clarity")
- [ ] Fixes are batched by type (all content fixes together, then mechanism fixes)
- [ ] Each batch ends with a gated review before the next batch starts
- [ ] HANDOFF.md is updated after every session with the current status of the recommendation list

---

## Appendix A — The AI Persona Evaluator Innovation

This is the most distinctive element of the workflow above. The idea: before you can objectively evaluate your own course, you need to *exit* the role of course author and enter the role of a demanding learner.

**Why personas work better than generic review:**
- Generic review ("is this good?") produces generic answers ("it's clear and well-structured")
- A persona with a name, background, and specific goal produces specific answers ("Aryan, a senior ML engineer, would abandon this course at Level 3 because the loss function explanation assumes calculus familiarity that was never established")

**Persona design formula:**
```
Name: [Specific person, not "a student"]
Role: [Job title and industry]
Learning goal: [Specific thing they want to be able to do]
Prior knowledge: [What they already know — be precise]
Prior misconceptions: [What wrong mental models they bring in]
Disposition: [Critical / sceptical / time-pressured — not "motivated learner"]
```

**Multiple personas for different dimensions:**
- **The Demanding Learner** (Aryan) — finds pedagogical gaps
- **The Subject Matter Expert** — finds content inaccuracies
- **The Time-Pressed Practitioner** — finds bloat, poor prioritisation
- **The Absolute Beginner** — finds assumed knowledge

Run at least two personas with different dispositions. The scorecard's value is in the *disagreements* between personas — those surface the tension between depth and accessibility.

---

## Appendix B — Instructional Design Frameworks (Reference)

| Framework | Core idea | When to use |
|---|---|---|
| **ADDIE** | Analyse → Design → Develop → Implement → Evaluate | Overall project lifecycle structure |
| **Bloom's Taxonomy** | Hierarchy of cognitive complexity: remember → understand → apply → analyse → evaluate → create | Writing learning objectives; sequencing lessons |
| **Gagné's Nine Events** | Attention → Inform → Recall → Content → Example → Practice → Feedback → Assessment → Transfer | Designing individual lesson structure |
| **Feynman Technique** | If you can't explain it simply, you don't understand it | Mastery evaluator design; calibrating rubrics |
| **Spaced Repetition** | Re-expose concepts at increasing intervals for long-term retention | Structuring module openers; project briefs |
| **Dual Coding** | Pair text with visuals to reduce cognitive load | Lesson design; diagram inclusion |

---

## Appendix C — Common Failure Modes

| Failure mode | Symptom | Fix |
|---|---|---|
| Scope creep | 100+ lessons planned; none finished | Enforce Phase 0 — set lesson cap before writing |
| Shallow content | Lessons pass persona review but learners can't apply the knowledge | Run Phase 8b (pedagogy audit) specifically on transfer |
| Sycophantic evaluator | AI evaluator passes every answer | Constrain output strictly (PASS/FAIL/EDGE only); test with bad answers |
| Orphaned curriculum | Curriculum written but course never built | Timebox Phase 1 output; start Phase 2 with a rough curriculum |
| Skipped QA | Course deployed without smoke test | Phase 8 checklist is non-negotiable |
| No session continuity | Every session re-establishes context | HANDOFF.md read at start, updated at end, every session |

---

## Appendix D — Professor Efficiency Track

For a professor converting existing courses under time pressure, the phases above can be sequenced for maximum early value.

**Time estimates (rough):**

| Phase | Time investment | Notes |
|---|---|---|
| Phase 0 — Scoping | 1–2 hrs | One prompt + 1 round of editing |
| Phase 1 — Curriculum | 2–4 hrs | Generation + depth review + manual check |
| Phase A — AI Architecture | 2–3 hrs | The most important phase. Don't rush. |
| Phase 2 — Frontend | 3–6 hrs | One prompt + debugging + student model wiring |
| Phase 3 — Scaffolding | 1 hr | Templates exist; adapt them |
| Phase 4 — Content (per lesson) | 30–45 min/lesson | Budget 40 hrs for a 60-lesson course |
| Phase 5 — Persona Evaluation | 2–3 hrs | Run two personas; compare verdicts |
| Phase 6 — Rubrics (per lesson) | 20–30 min/lesson | Budget 25 hrs for a 60-lesson course |
| Phase B — Student Model | 3–4 hrs | Schema + logic + integration |
| Phase 7 — Mechanism Build | 6–10 hrs | Four mechanisms; test each separately |
| Phase C — Adaptive Difficulty | 4–6 hrs | Routing logic + tier variants |
| Phase 8 — QA | 2–3 hrs | Non-negotiable |
| Phase 9 — Iteration | Ongoing | 1–2 hrs per batch |

**Total for a full 60-lesson course: ~120–160 hrs of directed work**
**Minimum Viable Course (5 lessons): ~30–40 hrs**

**Reuse strategy — what carries across courses:**
Once the first course is built, save these as templates in a `_course-templates/` folder:
- `student-model.schema.json` — the student model structure (same for all courses)
- `misconception-library-template.md` — common wrong mental model format
- `course-player.html` — the UI shell (swap CONTENT and LESSONS objects)
- `rubric-template.md` — the rubric format (swap criteria and exemplars)
- `calibration-anchors-template.md` — strong, fluent-but-weak, guessing, and misconception examples
- `transfer-project-template.md` — project brief, critique protocol, revision loop
- All system prompts from Phases 7, B, C — parameterised with `[LESSON_CONTENT]` and `[STUDENT_MODEL]` placeholders
- `HANDOFF.md` template
- `CLAUDE.md` project instructions

Second course build time: approximately 60% of the first, because the infrastructure is done.

---

## Quick-Reference — All Prompts

| Prompt | Phase | Purpose |
|---|---|---|
| Prompt 0 | Concept & Scoping | Generate Learning Brief |
| Prompt 1a | Curriculum | Generate full curriculum structure |
| Prompt 1b | Curriculum | Depth and sequencing review |
| Prompt A | AI-First Architecture | AI responsibility map + student model schema |
| Prompt 2 | Frontend | Course player UI design (with student model wired in) |
| Prompt 3 | Scaffolding | HANDOFF.md template |
| Prompt 4 | Content | Individual lesson generator |
| Prompt 4.5 | Transfer | Project and capstone designer |
| Prompt 5a | Evaluation | Full persona evaluation + scorecard |
| Prompt 5b | Evaluation | Second-pass evaluation after fixes |
| Prompt 6 | Rubrics | Per-lesson mastery rubric + concept tags |
| Prompt 7 | Mechanism | Mastery Judge system prompt |
| Prompt B1 | Student Memory | Session warm-up question generator |
| Prompt B2 | Student Memory | Cross-chapter intelligence question generator |
| Prompt B3 | Student Memory | Socratic pushback chain (3-attempt protocol) |
| Prompt C1 | Adaptive Difficulty | Three-tier lesson variant generator |
| Prompt C2 | Adaptive Difficulty | Engagement drift detector |
| Prompt 8a | QA | Student pushback test |
| Prompt 8b | QA | Full pedagogy audit |

---

## Appendix E — The Professor-as-Digital-Avatar Model

The full vision of this guide is not "a course with AI features." It is a system where the AI is the professor's digital avatar — capable of handling all routine teaching interactions without escalation, while surfacing only the students who genuinely need the professor's judgment.

**What the AI handles (no escalation):**
- First-pass knowledge delivery (Standard tier lesson content)
- Mastery assessment on every lesson
- 3-attempt Socratic pushback chains
- Adaptive routing to Scaffolded or Deep-Dive content
- Cross-chapter recall questions
- Session warm-up personalisation
- Engagement monitoring and flagging

**What escalates to the professor:**
- 3 consecutive FAIL/EDGE verdicts on the same concept (persistent gap)
- Guessing signals concentrated in a high-stakes module
- Engagement drift detected (AMBER → RED)
- Student explicitly requests human help

**The Professor Alert format (the only interface the professor needs to check daily):**
```
STUDENT: [name/ID] | COURSE: [name] | DATE: [date]
GAP: [concept-tag] — [1-sentence description of specific misunderstanding]
EVIDENCE: [3 answer snippets, one per attempt]
RECOMMENDED INTERVENTION: [specific 1–2 sentence action]
URGENCY: LOW / MEDIUM / HIGH
```

**Calibrating the AI to the professor's standards:**
Before deploying any course, the professor should spend 2–3 hours answering their own course questions as three student types:
- A student who genuinely understands the material
- A student who is guessing
- A student who has a specific, common misconception

The AI evaluator's responses should be reviewed by the professor and refined until the verdicts match the professor's own judgment. This is what makes it a *digital avatar* — not mimicry, but calibrated alignment.

---

## Appendix F — Version 3.0 Quality Gate

Before using this guide as the source prompt for a new AI-first learning application, run this final gate:

| Gate | PASS condition |
|---|---|
| Core loop | The course can state exactly how it diagnoses, teaches, asks, evaluates, repairs, updates memory, and adapts |
| Runtime consequence | Every student-model field changes a future lesson, question, project, routing decision, or alert |
| Calibration | Every high-stakes evaluator has anchors for strong, fluent-but-weak, guessing, and misconception answers |
| Transfer | The learner must produce, critique, or revise at least one realistic artifact |
| Misconceptions | Common wrong mental models are named separately from concept tags |
| Privacy | Stored learning data is minimal, resettable, and exportable |
| Accessibility | The UI can be navigated by keyboard and understood without colour-only cues |
| MVC discipline | The first release proves judgment-and-repair before adding warm-ups, cross-chapter intelligence, and alerts |

**Final standard:** If applying the original review prompt to this document, the expected result should be that the previous recommendations are now explicitly represented: cleaner dependency order, a named core learning loop, calibration as a required practice, transfer-project evidence, misconception tracking, privacy/accessibility requirements, and reduced reliance on decorative AI behaviour.

---

*Guide version 3.0 — revised after architecture QA. Preserves the version 2.0 guide while adding the core AI learning loop, required artifacts, calibration anchors, misconception library, transfer project design, privacy/accessibility guardrails, and a final quality gate.*
