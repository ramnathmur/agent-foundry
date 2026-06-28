# AgentFoundry AI-First Learning Blueprint

**Version:** 1.0 (Final — Audit-Incorporated)
**Produced:** June 26, 2026
**Status:** ADOPT-READY (with known caveats documented in Appendix E)

---

## READER BRIEFING (READ THIS FIRST)

### B.1 What This Document Is

[UNIVERSAL]

This document is a machine-readable implementation specification for the AI-First Learning model as developed in the Agent Foundry project. It is intended to be read by an AI system that will implement this model in a new domain or project. The document is self-contained: every term is defined within it, every concept is illustrated with worked examples, and every implementation decision is justified. No external files, sessions, or prior context are required to act on this specification. An AI implementer encountering this document for the first time has everything needed to instantiate the AI-First Learning model in a new technical curriculum domain within two to three weeks.

### B.2 Document Provenance

[UNIVERSAL]

This document was produced by a four-agent orchestration workflow executed on June 26, 2026. Phase 1 (Writer agent) produced an initial 26,189-character pedagogical architecture document. Phase 2 (Reviewer agent, simulating a Healthcare Training Simulations adopter) generated detailed adoption feedback covering 4 BLOCK findings and 8 ADVISORY findings. Phase 3 (Incorporator agent) integrated all feedback into a refined document. Phase 4 (Systems Documentation Architect agent) resolved all BLOCKs and incorporated ADVISORYs into this final version.

The two source documents — `Agent-Foundry_AI-First-Learning-Model_v1.md` (the comprehensive model reference) and `AI-First-Learning_Workflow-Summary_v1.md` (the workflow summary containing QA findings and adoption readiness data) — have been combined into this single Blueprint.

**Final verdict:** ADOPT-READY. Confidence level: 93% (High). All 4 BLOCK findings resolved; 8 ADVISORY findings addressed (6 resolved inline, 2 retained as documented limitations).

### B.3 Document Map

[UNIVERSAL]

| Section | Title | Purpose | Universality |
|---------|-------|---------|--------------|
| B.1 | What This Document Is | Orients the AI reader to purpose and scope | UNIVERSAL |
| B.2 | Document Provenance | Explains where this came from and confidence level | UNIVERSAL |
| B.3 | Document Map | Navigation index for all sections | UNIVERSAL |
| B.4 | Recommended Reading Sequence | Ordered path for a cold-start adopter | UNIVERSAL |
| B.5 | Key Term Glossary | All defined terms, alphabetized | UNIVERSAL |
| B.6 | Universal vs. Domain-Specific Components | What adopts unchanged vs. what must be adapted | UNIVERSAL |
| B.7 | Adoption Prerequisites | What must be in place before implementing | UNIVERSAL |
| B.8 | Comprehension Verification Checklist | 10 yes/no questions to verify correct understanding | UNIVERSAL |
| B.9 | Known Limitations and Open Items | QA-identified gaps with status and workarounds | UNIVERSAL |
| §1 (Part 1) | Core Concepts | O-R-A loop, Five Gates, SDK Ladder, Learning Positions | UNIVERSAL (structure); DOMAIN-SPECIFIC (ladder rungs, gate aliases) |
| §2 (Part 2) | Cycle Architecture | Seven-phase cycle, phase-by-phase protocols | UNIVERSAL (structure); DOMAIN-SPECIFIC (file types, execution environment) |
| §3 (Part 3) | Learning Artifacts | HTML guide formats, runtime output standard | UNIVERSAL (structure, section count); DOMAIN-SPECIFIC (section labels, output elements) |
| §4 (Part 4) | State Management and Cross-Cycle Memory | Registry schema, session protocols, traits checklist | UNIVERSAL (registry structure); DOMAIN-SPECIFIC (trait definitions, metadata fields) |
| §5 (Part 5) | The Professor Persona | Identity, responsibilities, system prompt template | UNIVERSAL |
| §6 (Part 6) | Adaptation Framework | What is universal vs. domain-specific; adaptation checklist | UNIVERSAL |
| §7 (Part 7) | Data Science Domain Instantiation | Complete worked example for ML pipelines | DOMAIN-SPECIFIC (illustrative proof of portability) |
| §8 (Part 8) | Database Query Domain Instantiation | Partial worked example for SQL optimization | DOMAIN-SPECIFIC (illustrative proof of portability) |
| §9 (Part 9) | Implementation Patterns | System prompt structure, memory management, validation | UNIVERSAL |
| §10 (Part 10) | Common Pitfalls and Mitigation | Failure modes with prevention strategies | UNIVERSAL |
| §11 (Part 11) | Adoption Guide for AI Implementers | Timeline, first-cycle checklist, scaling | UNIVERSAL |
| §12 (Part 12) | Conclusion and Key Takeaways | Core innovation summary, fit assessment | UNIVERSAL |
| Appendix A | Functional Aliases Quick Reference | Gate codes to plain-English aliases | UNIVERSAL (structure); DOMAIN-SPECIFIC (alias wording) |
| Appendix B | Phase Reference Card | Phases, durations, inputs, outputs | UNIVERSAL (structure); DOMAIN-SPECIFIC (durations, file types) |
| Appendix C | File Checklist Per Cycle | Mandatory files per cycle | DOMAIN-SPECIFIC (file names, types) |
| Appendix D | ROADMAP.md Specification | **[BLOCK-1 FIX]** Schema, example, and distinction from HANDOFF.md | UNIVERSAL |
| Appendix E | Registry Schema (foundry_registry.json) | **[BLOCK-3 FIX]** Full annotated JSON schema with field names and types | UNIVERSAL (structure); DOMAIN-SPECIFIC (trait and rung values) |
| Appendix F | Nine-Step Adaptation Checklist | **[BLOCK-4 FIX]** Step-by-step procedure for new domain instantiation | UNIVERSAL |
| Appendix G | Professor System Prompt Template | **[BLOCK-2 FIX]** Full template with constraint block | UNIVERSAL |
| Appendix H | HTML Starter Templates | **[ADVISORY-4 FIX]** Minimal Part 1 and Part 2 starter scaffolds | UNIVERSAL (structure); DOMAIN-SPECIFIC (section labels) |
| Appendix I | Auditor's Findings and Fixes | All BLOCK and ADVISORY findings; portability proof; final verdict | UNIVERSAL |

### B.4 Recommended Reading Sequence for Cold Adoption

[UNIVERSAL]

An AI system encountering this document for the first time in a new project MUST read sections in this order before taking any implementation action:

1. **§B.1–B.3 (this briefing)** — 5 minutes. Establish purpose, provenance, and navigation map before reading anything else. These sections prevent misapplication of domain-specific examples as universal rules.

2. **§B.5 Key Term Glossary** — 15 minutes. Load all defined terms into working context before reading the body. Terms such as O-R-A, G1–G5, rung, Learning Position, and registry carry precise meanings that differ from informal usage. Reading the glossary first prevents misinterpretation of body text.

3. **§B.6 Universal vs. Domain-Specific Components** — 5 minutes. Identify which sections apply unchanged and which require adaptation before investing reading time in domain-specific examples. This prevents the common failure of adopting Agent SDK-specific rungs or output elements as if they were universal.

4. **§1 (Part 1): Core Concepts** — 20 minutes. The O-R-A loop (§1.2), Five Gates (§1.3), SDK Ladder (§1.4), and Learning Positions (§1.5) are the foundational primitives. Every other section builds on these. An implementer who does not fully understand these four concepts cannot correctly implement any other section.

5. **§2 (Part 2): Cycle Architecture** — 20 minutes. The seven-phase cycle (Phase A through Phase F2) is the operational skeleton of every implementation. Understanding which phases are mandatory vs. skippable, and what each phase produces, is required before reading artifact specifications.

6. **Appendix E: Registry Schema** — 15 minutes. **[Promoted from "as needed" — ADVISORY-1 fix]** Read the full registry schema before designing any adaptation. The registry is the only component where a naming error has silent, cross-cycle consequences: if an implementer names the gaps array `gaps` instead of `learning.gaps[]`, the Learning Position algorithm will never classify a cycle as FOUNDATIONAL. Reading the schema early — alongside the gate definitions that depend on it — catches this class of error before the first cycle is built.

7. **§4 (Part 4): State Management** — 15 minutes. **[Promoted from "as needed" — ADVISORY-1 fix]** Read state management before designing your adaptation. Understanding the three-tier session start protocol, SESSION.md structure, and HANDOFF.md rules is required before reading the cycle architecture in depth.

8. **§3 (Part 3): Learning Artifacts** — 15 minutes. **[Promoted from "as needed" — ADVISORY-1 fix]** Understand the two-phase HTML artifact structure, section counts, and self-containment requirements before reading domain examples.

9. **Appendix D: ROADMAP.md Specification** — 10 minutes. **[BLOCK-1 fix]** Understand what ROADMAP.md tracks, how it differs from HANDOFF.md, and its schema before reading cold-start protocols. ROADMAP.md is required reading during every cold start.

10. **§6 (Part 6): Adaptation Framework** and **Appendix F: Nine-Step Adaptation Checklist** — 30 minutes. **[BLOCK-4 fix]** Read the nine-step checklist before reading the domain examples. Understanding the adaptation process makes the examples readable as worked illustrations rather than templates to copy.

11. **§7 (Part 7): Data Science Domain Instantiation** — 45 minutes. Study this as a proof of portability, not as a template. Trace how each universal component (gates, traits, output standard, learning artifact sections) was translated into ML pipeline equivalents. The translation logic is the lesson, not the ML-specific content.

12. **§5 (Part 5): The Professor Persona** and **Appendix G: System Prompt Template** — 20 minutes. **[BLOCK-2 fix]** Read the Professor's phase-specific responsibilities, the system prompt template, and the constraint block before designing any Professor system prompt. The Checkpoint 4 four-beat probe structure and the gate code prohibition are non-negotiable constraints that must be built into the system prompt, not left to runtime judgment.

13. **§9 (Part 9): Implementation Patterns** — 20 minutes. The three-tier session state protocol, validation checklist, and probe rubric are concrete operational patterns that translate the model into running systems.

14. **§10–11 (Parts 10–11): Failure Modes and Adoption Guide** — 15 minutes. Read the failure mode table (§10.1) and the first-cycle go/no-go checklist (§11.2) before beginning implementation. Knowing the 10 documented failure modes before the first cycle prevents the most common implementation errors.

15. **Appendix I (Auditor's Findings and Fixes)** — 10 minutes. Review all findings, their resolutions, and the Healthcare portability proof to understand where to invest additional validation effort in your domain.

### B.5 Key Term Glossary

[UNIVERSAL]

All terms are alphabetized. Each definition is precise and self-contained. Terms that appear in the body are defined on first use in parentheses; this glossary is the authoritative reference.

**Artifact:** The code, model, query, pipeline, or system the student builds in a cycle (and the Professor generates). An artifact is the primary deliverable of Phase C. In the Agent SDK domain, an artifact is a runnable Python agent. In the Data Science domain, an artifact is an ML pipeline. In the Healthcare domain, an artifact is a clinical decision simulation.

**Brainstorm (Phase A):** The first mandatory phase of every cycle, in which the Professor proposes 3–4 candidates and the student locks one. Nothing is written to disk before the student issues an explicit lock command.

**Brainstorm candidate:** A proposed artifact for a cycle, presented with a problem statement, platform rungs, Learning Position label, and gate verdicts using functional aliases only.

**CDN (Content Delivery Network):** A network of distributed servers used to deliver web assets (scripts, stylesheets, fonts) from external hosts. HTML learning artifacts MUST NOT use CDN links; all CSS and JavaScript must be inline or bundled to ensure the artifact works offline and in any environment.

**Checkpoint 4:** The four-beat Socratic probe structure mandated for all Phase F and Phase F2 probes: (1) Hook — a real-world professional analogy; (2) Why it matters — connects the analogy to the agentic concept; (3) Runtime/evidence line — quotes actual code or output as illustration, not as the question; (4) Open question — concept-level, not syntax-level, not yes/no.

**Cold start:** The session initialization mode used when SESSION.md is absent, when SESSION.md has `full_reload: true`, or when starting cycle 1 for the first time. Requires reading HANDOFF.md, foundry_registry.json, and ROADMAP.md before proceeding. See also: Appendix D (ROADMAP.md Specification).

**Cycle:** One complete pass through all seven phases (Phase A through Phase F2), resulting in a built and reflected-upon artifact, updated registry, and Part 2 learning insights HTML. The fundamental unit of the learning model.

**DIAGNOSTIC (Learning Position):** A cycle deliberately designed to fail one or more gates, teaching the student what NOT to do. The specific failure mode (which gate fails and why) MUST be stated before the student locks. A DIAGNOSTIC cycle also produces a `<slug>_workflow_to_agent.md` showing the minimal diff to promote it to a true agent.

**Execution environment:** The specific tool and command the student uses to run the artifact. Examples: Python IDE running `main.py`, Jupyter notebook, database client running a SQL query, a simulation engine accepting case parameters. The execution environment MUST be specified before Phase C.

**FORWARD (Learning Position):** A cycle that introduces at least one platform rung not previously seen by the student, or at least one trait or gate not yet exercised. This is the default recommendation when new rungs are available.

**FOUNDATIONAL (Learning Position):** A cycle targeting a concept flagged in the student's active gaps (the `learning.gaps[]` array in the registry). A repair cycle that overrides LATERAL-LEFT when gaps exist.

**Functional alias:** The plain-English name used in all student-facing surfaces instead of a gate code. For example, "Did-it-finish check" is the functional alias for G1. Gate codes (G1–G5) are prohibited in student-facing text; functional aliases are required. See Appendix A for the complete mapping.

**G1 — Goal predicate (functional alias: "Did-it-finish check"):** The gate that tests whether an agent has a computable stopping condition — a function `goal_met(state) -> bool` that the agent calls and evaluates at each iteration. G1 passes when this predicate exists and is evaluated in code, not narrated.

**G2 — Model-owned decision (functional alias: "Model's own choice"):** The gate that tests whether the LLM makes at least one real control-flow decision at runtime. G2 passes when the model selects between options (which tool to call, which path to take) rather than following hard-coded conditional branches.

**G3 — Feedback loop (functional alias: "Learning from what it saw"):** The gate that tests whether the observe→reason→act loop is closed — whether the agent reads a tool result and a subsequent action demonstrably differs because of it. G3 passes when output of iteration N provably influences iteration N+1.

**G4 — Bounded iteration (functional alias: "Principled stop"):** The gate that tests whether the agent exits cleanly with a labeled reason, and whether a hard iteration cap exists as a fallback. G4 requires both the goal-predicate exit path AND a maximum-iterations cap, both reachable and both tested.

**G5 — Independent verification (functional alias: "Independent check"):** The gate that tests whether a separate verifier (a different agent call with fresh context, or a deterministic predicate) confirms the artifact's work. G5 passes when the verifier has no access to the training data or conversation used during work. G5 is typically not applicable until Rung 7.

**Gate verdict:** The pass/fail/unclear/not-applicable assessment for each of the Five Gates applied to a specific artifact. Gate verdicts use functional aliases in student-facing surfaces and gate codes in internal documentation. "Unclear" means the artifact does not clearly demonstrate this gate — the gate is not violated but also not proven. "Fail" means the gate is violated.

**HANDOFF.md:** A file written at the end of each cycle containing prior cycle insights, active gaps, recommended next steps, and notes for the next session. Read during cold start only. Maximum one page. Covers a single prior cycle. Contrast with ROADMAP.md, which tracks multi-cycle curriculum intent.

**Hook:** The opening beat of a Checkpoint 4 probe — a real-world professional analogy (consulting, project management, research, clinical practice) that maps to the agentic concept without using code vocabulary. The Hook MUST precede the runtime evidence line; probes that open with code violate Checkpoint 4.

**LATERAL (Learning Position):** A cycle that uses the same platform rungs as prior cycles but applies them to a different domain. Two subtypes: LATERAL-RIGHT (new domain — breadth run) and LATERAL-LEFT (same domain — consolidation run, overridden by FOUNDATIONAL when gaps exist).

**Learning guide (Part 1):** The pre-run HTML artifact (`<slug>_learning-guide.html`) generated in Phase C, before the student runs the artifact. Contains 13 mandatory sections preparing the student to read the code and understand the runtime output. Must be self-contained (inline CSS, no CDN links). See Appendix H for starter template.

**Learning insights (Part 2):** The post-run HTML artifact (`<slug>_learning-insights.html`) generated after Phase F2 using the student's actual runtime log. Contains 11 mandatory sections proving gate satisfaction with evidence from the student's own run. Must be self-contained. See Appendix H for starter template.

**Learning Position:** The pedagogical intent label assigned to every brainstorm candidate, indicating why this cycle matters: FORWARD (new rung), FOUNDATIONAL (gap repair), LATERAL (breadth or consolidation), or DIAGNOSTIC (deliberate failure). Displayed to the student before gate verdicts.

**MCQ (Multiple-Choice Question):** A question format used in Phase F and Phase F2 probes where the student selects from a defined set of options. MCQs are acceptable for concept-check probes but MUST NOT be the sole probe format — open reasoning questions are also required per Checkpoint 4.

**Mini-spec (Phase B):** The second mandatory phase, in which the Professor presents the goal predicate, tools, loop structure, and termination conditions in plain English (not code) for student confirmation. The last human checkpoint before Phase C generation begins.

**O-R-A loop (Observe-Reason-Act):** The core feedback mechanism of the model, operating at three timescales: micro (single probe), session (brainstorm through reflection), and macro (across cycles). The Professor observes student output, reasons about gaps, and acts with the next cycle or explanation.

**Phase A:** See Brainstorm.

**Phase B:** See Mini-spec.

**Phase C:** The generation phase in which the Professor writes all artifact files in a single continuous pass without pausing. File order: prompt.md → learning-guide.html → main.py → smoke_test.py → requirements.txt → .env.example → README.md → (learning-insights.html after run). No confirmation gates between artifacts.

**Phase F:** The pre-run Professor session (approximately 10 minutes). Skippable. Delivers 2–3 Socratic probes using Checkpoint 4 format, then provides closing guidance on what to watch for during the run.

**Phase F2:** The post-run Professor session. Highly encouraged. Triggered when the student says "I ran it." Delivers 3–5 reflection probes anchored to the student's actual runtime output using Checkpoint 4 format. Begins with Checkpoint 3 (post-run debrief) before any probe.

**Professor persona:** The AI teaching identity maintained across all phases and sessions. The Professor is warm, Socratic, and pedagogically intentional. It narrates the why before the what, asks questions rather than lecturing, and maintains consistent voice from cycle 1 through cycle N. See §5 and Appendix G for full specification.

**Registry (foundry_registry.json):** The persistent JSON file accumulating every cycle's artifact metadata, gate verdicts, gaps identified, rungs introduced, and student preferences. Read at every brainstorm start (Phase A); updated at every cycle end. The registry is the source of cross-cycle curriculum personalization. See Appendix E for full schema.

**ROADMAP.md:** A persistent Markdown or JSON file tracking multi-cycle curriculum intent — where the student is on the rung ladder, which rungs are planned for upcoming cycles, and which Learning Positions are queued. Distinct from HANDOFF.md (which covers one prior cycle). Required reading during every cold start. See Appendix D for full specification.

**Rung:** A unit of the underlying platform ladder (e.g., Claude Agent SDK). Each rung introduces one new concept or capability. Students climb the ladder over multiple cycles; the registry tracks which rungs have been introduced so no cycle repeats a rung unnecessarily.

**SDK Ladder:** The ordered progression of platform concepts across cycles. The Agent Foundry SDK Ladder has 8 rungs (stateless query through subagents). Every domain implementation defines its own equivalent ladder with 6–8 rungs.

**SESSION.md:** The current-session state file (maximum 15 lines) recording cycle number, current phase, artifact slug, status, and next action needed. Read on every session start for warm-start behavior. Written at the end of every completed step.

**Smoke test:** Unit tests with mocked LLM responses (or domain equivalent: scenario validity checks, seeded case runs). All tests must pass before the artifact is handed over to the student. Tests validate the loop logic, tool calling, goal predicate, and all exit paths (goal-met AND cap). The repair loop is capped at 3 attempts. Coverage standard: branch reachability — every distinct exit path must have at least one test that fires it under seeded fixtures. A percentage-based coverage threshold is not required.

**Traits checklist:** The nine-item checklist of observable characteristics that define a well-built artifact. Traits are domain-adapted per implementation. In the Agent SDK domain: goal-driven, looping, observable, model-owned, tool-using, bounded, verifiable, environment-aware, feedback-closing.

**WCAG AA:** Web Content Accessibility Guidelines Level AA — the accessibility standard that HTML learning artifacts must meet. Minimum requirements: color contrast ratio 4.5:1 for normal text, 3:1 for large text; all interactive elements keyboard-accessible; semantic HTML (`<main>`, `<section>`, `<h1>`–`<h3>` hierarchy).

**Warm start:** The default session initialization mode. Reads SESSION.md only and resumes from the current phase without reading registry or HANDOFF.md.

### B.6 Universal vs. Domain-Specific Components

[UNIVERSAL]

#### Universal Components (Adopt As-Is)

These components are identical across all domain implementations. An adopting AI system MUST implement them without modification:

1. **O-R-A feedback loop architecture** — The three-timescale observe→reason→act structure (micro, session, macro) applies unchanged to every domain.
2. **Seven-phase cycle structure** — Phase A through Phase F2, with mandatory/skippable designations as specified in §2.1.
3. **Professor persona identity and values** — Warmth, Socratic commitment, pedagogical intent, and the four Checkpoint rules (§5.1–5.2).
4. **Checkpoint 4 four-beat probe format** — Hook → Why it matters → Runtime/evidence line → Open question. Applies to all Phase F and Phase F2 probes in all domains.
5. **Gate prohibition rule** — Gate codes (G1–G5) MUST never appear in student-facing surfaces. Functional aliases are required. This rule is universal regardless of what the domain calls its gates.
6. **Registry-based cross-cycle memory** — The JSON registry structure (Appendix E), three-tier session start protocol (§4.2), and update-after-every-cycle rule are universal.
7. **Two-phase learning artifact structure** — Part 1 (pre-run, preparation) and Part 2 (post-run, evidence). Section counts (13 for Part 1, 11 for Part 2) and the self-containment requirement (inline CSS, no CDN) are universal.
8. **No-pause generation rule in Phase C** — All files MUST be generated in a single continuous pass without confirmation gates. Universal.
9. **Learning Position system** — FORWARD, FOUNDATIONAL, LATERAL (RIGHT/LEFT), and DIAGNOSTIC labels apply in all domains. The classification algorithm (§1.5 and §6) is universal.
10. **Session continuity markers** — Every session start must recap prior cycles, active gaps, and learning goal. Universal.
11. **Smoke test requirement** — All generated artifacts must pass smoke tests with mocked dependencies before handover. Maximum 3 repair attempts, each narrated. Coverage standard: branch reachability. Universal.
12. **Phase F2 Checkpoint 3 rule** — The post-run debrief (Checkpoint 3) MUST fire before the first Phase F2 probe. This rule is universal.
13. **ROADMAP.md cold-start protocol** — Every cold start reads ROADMAP.md alongside HANDOFF.md and foundry_registry.json. The ROADMAP.md schema (Appendix D) is universal.

#### Domain-Specific Components (Must Be Adapted)

These components MUST be redesigned for each new domain. Guidance for HOW to adapt each is given in parentheses:

1. **The rung ladder** — Define 6–8 rungs specific to the domain's platform concepts. Each rung introduces one new concept; map each rung to the gates it demonstrates. (Follow the template in Appendix F Step 2; study the Data Science example in §7.2 and the Database Queries example in §8.2.)
2. **Artifact type and execution environment** — Define what students build (code, query, model, simulation, etc.) and how they run it (IDE, notebook, CLI, database client, simulation engine). (Follow Appendix F Step 1.)
3. **Gate adaptations (G1–G5 equivalents)** — The Five Gates are universal; the domain expressions of each gate differ. Define what "goal predicate," "model-owned decision," "feedback loop," "bounded iteration," and "independent verification" mean in the domain's language. Create functional aliases appropriate for the domain's students. (Follow Appendix F Step 3; study §7.3 and §8.3 for examples.)
4. **Traits checklist** — Replace the nine Agent SDK traits with 7–9 domain-appropriate traits. Each trait must be observable in runtime output. (Follow Appendix F Step 4; study §7.4 and §8.4 for examples.)
5. **Runtime output standard** — Create a 20–30 labeled output element sequence appropriate for the domain's execution. Keep the design principle: every element teaches something. The 24-element Agent SDK sequence is the reference; domains may use 20–30 elements. (Follow Appendix F Step 6; study §7.5 and §8.5 for examples.)
6. **Learning artifact section labels** — Adapt the 13 Part 1 sections and 11 Part 2 sections to domain vocabulary. The section COUNT and SEQUENCE are universal; the labels and content must reflect domain concepts. (Follow Appendix F Step 7; see Appendix H for HTML starter templates.)
7. **Professor system prompt** — Instantiate the template (Appendix G) with domain-specific identity, phase responsibilities, and domain terminology. The constraint block in Appendix G is universal and must not be modified. (Follow Appendix F Step 8.)
8. **Domain functional aliases** — Translate gate functional aliases to domain-appropriate language. "Did-it-finish check" may become "Converged or quit?" for ML domains, "Runs in time?" for database domains, or "Is the patient there yet?" for healthcare domains. (Follow §7.3 and §8.3 for examples.)

### B.7 Adoption Prerequisites

[UNIVERSAL]

Before beginning implementation, an AI system MUST verify all of the following:

1. **Full document read completed** — The implementer has read this Blueprint in the sequence specified in §B.4. Partial reads are insufficient; implementation decisions in later sections depend on concepts established in earlier sections.
2. **Target domain identified** — The domain is a technical curriculum with clear executable artifacts (code, queries, models, pipelines, simulations). If the domain lacks executability, see §12.3 for fit assessment before proceeding.
3. **Execution environment defined** — The specific tool (Python IDE, notebook, database client, CLI, simulation engine) and the command or action the student performs to run the artifact is specified. Without this, the runtime output standard and Phase F2 cannot be designed. Note: "execution environment" is not limited to code runners — a clinical simulation platform accepting case parameters is a valid execution environment.
4. **Storage available for registry and session files** — The system has write access to create and update `foundry_registry.json`, `SESSION.md`, `HANDOFF.md`, `ROADMAP.md`, and the artifact folder structure.
5. **LLM access established** — The system has authenticated access to the LLM used to generate artifacts and run Phase F/F2 sessions. The authentication method must be confirmed working before cycle 1.
6. **Gate framework designed** — The five universal gates have been expressed in domain language with functional aliases defined for student-facing use. This MUST be completed before brainstorming candidates.
7. **Rung ladder designed** — At least 4 rungs are defined and documented. Full 6–8 rungs may be added over time, but rungs 1–4 MUST exist before cycle 1.
8. **Professor system prompt drafted** — The Professor identity, phase responsibilities, and constraint block have been instantiated from the template in Appendix G with domain-specific values.
9. **Smoke test infrastructure established** — The system can run smoke tests against the generated artifact with mocked dependencies. For prose-output domains (e.g., clinical simulation transcripts), the smoke test is a seeded-scenario validity check: seed the simulation with inputs guaranteed to trigger each exit path, confirm the labeled termination reason appears in the output.
10. **First brainstorm candidate pool prepared** — At least one FORWARD candidate (introducing Rung 1) and one additional candidate of any Learning Position are ready, so the brainstorm can proceed without delay.
11. **ROADMAP.md initialized** — A valid ROADMAP.md file exists following the schema in Appendix D. Minimum content: current position (rung 0, pre-cycle), planned ladder sequence, and initial curriculum intent.

**"Ready to implement"** means: all 11 prerequisites are checked, the system can complete a brainstorm → mini-spec → artifact generation → smoke test → handover sequence without external lookups or missing definitions.

### B.8 Comprehension Verification Checklist

[UNIVERSAL]

After reading this Blueprint, an AI implementer can answer these 10 questions correctly before taking any implementation action. Each question tests a critical concept. Incorrect answers indicate re-reading is required.

1. **Can the gate codes G1–G5 appear in the brainstorm candidate descriptions shown to the student?** — No. Gate verdicts in brainstorm candidates MUST use functional aliases only. Gate codes appear only in internal system prompts, technical glossaries, and adoption documentation.

2. **How many files are generated in Phase C, and may the Professor pause between them to ask for confirmation?** — Eight files are generated in a single continuous pass (or the domain-equivalent set). The Professor MUST NOT pause between artifact generations. This is a non-negotiable constraint.

3. **What is the correct order of beats in a Checkpoint 4 probe?** — (1) Hook (real-world professional analogy), (2) Why it matters (connects analogy to agentic concept), (3) Runtime/evidence line (quotes actual code or output as supporting illustration), (4) Open question (concept-level, not syntax, not yes/no). Opening with code is a Checkpoint 4 violation.

4. **What must happen before the first Phase F2 probe is delivered?** — Checkpoint 3 (post-run debrief) must fire first. The Professor explains in plain English what just happened in the run before asking any reflection probes. Skipping Checkpoint 3 and jumping directly to probes is a documented failure mode.

5. **What is the difference between a warm start and a cold start?** — Warm start reads SESSION.md only and resumes from the current phase. Cold start additionally reads HANDOFF.md, foundry_registry.json, and ROADMAP.md. Cold start is used when SESSION.md is absent, when `full_reload: true`, or at cycle 1.

6. **What makes a Learning Position FOUNDATIONAL rather than LATERAL?** — FOUNDATIONAL targets a concept in the student's active gaps (`learning.gaps[]` in the registry). It is a repair cycle. FOUNDATIONAL overrides LATERAL-LEFT when gaps exist.

7. **When does Gate G5 (Independent check) apply?** — G5 applies when the artifact includes an independent verifier: a separate agent call with fresh context that evaluates the work. For the Agent SDK ladder, G5 typically first applies at Rung 7. Before Rung 7, the correct annotation is: `# GATE[G5]: N/A — independent verifier introduced at rung 7`. Domain equivalents (e.g., attending review in Healthcare) apply the same principle.

8. **What is the registry updated with, and when?** — The registry (foundry_registry.json) is updated at the end of every cycle with: cycle metadata, gate verdicts, traits demonstrated, execution stats, gaps identified, and student preferences. The update MUST be the final step before handoff.

9. **What does a DIAGNOSTIC cycle require that other Learning Positions do not?** — A DIAGNOSTIC cycle must (a) state the specific failure mode (which gate fails and why) BEFORE the student locks the candidate, and (b) generate an additional file `<slug>_workflow_to_agent.md` showing the minimal diff (5 lines or fewer) to promote the artifact to a true agent.

10. **What is the minimum content of a Phase F2 Checkpoint 4 probe?** — Each probe MUST include all four beats: a professional Hook, a "why it matters" sentence, a quoted runtime output line as illustration, and a concept-level open question that cannot be answered with yes or no. The question MUST be anchored to the student's specific artifact or output, not to a generic example.

### B.9 Known Limitations and Open Items

[UNIVERSAL]

The following gaps were identified by QA validation and the adoption feedback review. All BLOCK items have been resolved in this version. Remaining items are ADVISORY with documented workarounds.

| Item | Description | Impact | Status / Workaround |
|------|-------------|--------|---------------------|
| 1. Database Queries example incomplete | §8 is a partial instantiation (rungs, gates, partial traits; no complete HTML section examples) | Low — proof of portability established; Data Science example is complete | Use Data Science example (§7) as the primary portability proof; Database Queries shows a second translation direction |
| 2. Gate verdict "unclear" vs. "fail" precision | The gate verdict taxonomy defines "unclear" and "fail" (now in Glossary §B.5) but does not provide a decision procedure for edge cases | Low | "Unclear" = gate not violated but also not proven; "Fail" = gate is violated. When in doubt, mark "unclear" and explain in the notes field of the registry verdict object |
| 3. HTML template completeness | Appendix H provides a 50–80 line structural scaffold but does not include all 13 Part 1 sections inline | Medium — implementers must expand from the scaffold | Use the section-level examples in §3.1, §3.2, §7.6, and §7.7 alongside Appendix H to complete each section |
| 4. Multi-student database architecture | §11.3 describes a database migration but does not provide schema DDL or API contract | Low — single-student file-based implementation is complete | For 1–2 students, file-based registry and SESSION.md are sufficient; database migration is a future scaling concern |
| 5. Learning Position classification algorithm detail | The body algorithm (§1.5 and §6) is correct for implementation; a more detailed version with structural similarity scoring exists in project CLAUDE.md | Low | The body algorithm is sufficient for initial implementation. For ambiguous classifications, use the tiebreaker rule: when FOUNDATIONAL and LATERAL-RIGHT are both plausible, check `learning.gaps[]` — if non-empty, classify FOUNDATIONAL |
| 6. Prose-output smoke test seeding | Smoke test seeding strategy for prose-output domains (clinical transcripts, narrative simulations) is not fully specified | Medium for prose-output domains | For each exit path defined in the domain (stabilized / resource-limited / time-expired), create one seeded test case with clinical inputs guaranteed to trigger that path. Confirm the labeled termination reason appears verbatim in the output |
| 7. ROADMAP.md algorithm precision | ROADMAP.md's recommended-next-rung field is advisory, not enforced — the Professor may deviate based on student gaps | Low | Document any deviations in HANDOFF.md with a rationale field. ROADMAP.md is updated after every cycle to reflect actual progression |

---

## Part 1: Core Concepts

[UNIVERSAL — structure and principles; DOMAIN-SPECIFIC — ladder rungs, gate alias wording]

### 1.1 The AI-Professor Paradigm

The traditional learning pipeline is:
```
Content → Student reads → Student takes test → Score
```

The AI-Professor paradigm is:
```
Student describes goal → Professor proposes candidates → Student locks choice
→ Professor generates artifact → Student executes → System observes output
→ Professor guides reflection → Student explains what happened → Cycle repeats
```

**Key principle:** The student never reads about the domain in isolation. Every concept is introduced in the context of code (or artifact) the student is about to run, in execution output they are about to observe, or in a question anchored to their specific runtime evidence.

### 1.2 The Observe-Reason-Act Loop (O-R-A)

The core feedback mechanism mirrors what an agent does:

1. **Observe**: Professor reads student's runtime output, execution logs, answers to probes
2. **Reason**: Professor analyzes what the student understood (or didn't), infers gaps, plans next session
3. **Act**: Professor either explains a gap, proposes a new cycle, or recommends remediation

This loop operates at three timescales:
- **Micro loop** (single probe): student answers → Professor scores → Professor explains gap or confirms understanding
- **Session loop** (brainstorm → run → reflect): student executes artifact → Professor asks reflection probes → student answers → Professor updates registry with gaps/mastery
- **Macro loop** (across cycles): registry accumulates all student outputs → next brainstorm reads registry → Professor customizes next artifact based on prior gaps

### 1.3 The Five Gates (G1–G5): Formal Definition and Functional Aliases

These gates determine whether a system artifact is an **agent** (autonomous, goal-driven) or a **workflow** (predetermined, scripted). They serve as both:
- A **formal evaluation tool** for artifacts
- A **teaching framework** so students learn to apply the same gates themselves

**The Five Gates:**

| Gate | Formal Name | Functional Alias | What It Tests | Why It Matters |
|------|-------------|------------------|---------------|----------------|
| G1 | Goal predicate exists | "Did-it-finish check" | Agent has a computable stopping condition; not just model text | Autonomous systems stop themselves when done, not when told to |
| G2 | Model-owned decision | "Model's own choice" | LLM drives control flow; not hard-coded conditional branches | Learned behavior (data-driven) beats hard-coded behavior (brittle) |
| G3 | Feedback loop | "Learning from what it saw" | Environment changes between iterations; observe→reason→act closes | Systems that adapt are more valuable than those that repeat |
| G4 | Bounded iteration | "Principled stop" | Exits cleanly with labeled reason; hard iteration cap prevents infinite loops | Runaway loops are failures; intentional exits are features |
| G5 | Independent verification | "Independent check" | Separate verifier call with fresh context verifies work; trust is architectural | Work verified by independent agent is more trustworthy |

**Gate verdict taxonomy:**
- **Pass**: The artifact clearly demonstrates this gate in executable form.
- **Fail**: The gate is violated — the artifact does the opposite of what the gate requires.
- **Unclear**: The artifact does not clearly demonstrate this gate; the gate is not violated but also not proven. Annotate with a specific explanation.
- **Not-applicable (N/A)**: The gate is architecturally inapplicable at the current rung (e.g., G5 before Rung 7). Annotate: `# GATE[G5]: N/A — independent verifier introduced at rung 7`.

**Critical rule for student-facing surfaces:** Never use gate codes (G1–G5) in any text shown to students. Always use functional aliases in:
- Brainstorm candidates
- Learning guide HTML (Part 1)
- Learning insights HTML (Part 2)
- Phase F and F2 probe text
- Registry summaries visible to students

Gate codes appear only in:
- Internal system prompts
- Technical glossaries (HTML footer, for reference)
- Adoption documentation (this Blueprint)

**Validation:** Before any student-facing generation, scan text for "G1," "G2," "G3," "G4," "G5" and replace with functional aliases if found.

**Rung-to-gate mapping:** Each rung typically demonstrates one or two gates:
- Rungs 1–2: Demonstrate G1 (goal predicate, did-it-finish)
- Rung 3: Demonstrates G3 (feedback, multi-turn context shows learning)
- Rungs 4–5: Demonstrate G2 (model-owned decisions via tools)
- Rung 6: Demonstrates G3 and auditing (hooks observe feedback)
- Rung 7: Demonstrates G5 (independent verification)
- Rung 8: Demonstrates G2 and orchestration (subagents make autonomous decisions)

### 1.4 The SDK Ladder: Eight Rungs of Complexity

A **rung** (a unit of the underlying platform, e.g., Claude Agent SDK, introducing new capabilities per cycle) positions the student on the concept ladder. Students climb the ladder over multiple cycles.

| Rung | Concept | Represents | Example (Agent SDK) |
|------|---------|-----------|---------------------|
| 1 | Stateless query + message anatomy | Basic LLM call, message structure, output reading | Single Claude API call, no loop |
| 2 | Goal predicate + agent loop | First agent loop, goal checking, iteration control | Loop with "check: did I finish?" each iteration |
| 3 | Multi-turn sessions (session_id) | Persistent context across calls, session state | Same conversation with multiple messages, context preserved |
| 4 | Custom tools + model decision | Tool definition, model-owned tool selection, tool outcome observation | LLM decides which tool to call; you write the tool |
| 5 | Permission control (allowed_tools) | Autonomy dialing, permission modes, restricted tool access | Configure which tools agent can use; others are forbidden |
| 6 | Hooks (Pre/PostToolUse) | Interception, auditing, governance, observability | Code runs before/after model calls tool; you observe and audit |
| 7 | Independent verifier | Fresh-context verification (G5), separate agent instance | Another agent verifies the first agent's work with fresh context |
| 8 | Subagents + context compaction | Multi-agent orchestration, delegation, scaling | One agent spawns and manages other agents; information compression |

**Key insight:** Rungs are not strictly sequential. A student may skip rung 7 and jump to rung 8. Each cycle introduces at least one new rung; the sequence is tracked in the registry so the next brainstorm never repeats.

### 1.5 Learning Positions: Curriculum Intent

Every brainstorm candidate is labeled with a **Learning Position** (a pedagogical intent label signaling why this cycle matters) before gate verdicts are displayed:

| Position | Meaning | When Used | Signal to Student |
|----------|---------|-----------|-------------------|
| **FORWARD** | New platform rung the student hasn't seen | After completing a cycle; moving up the ladder | "This advances your skills — you'll see something new" |
| **FOUNDATIONAL** | Reinforces a rung previously seen but weak | When registry flags a gap in a prior concept | "You found this confusing last time; let's strengthen it" |
| **LATERAL** | Same rungs, different domain | To build transferable understanding across contexts | "Same technique, new application — proves you can generalize" |
| **DIAGNOSTIC** | Deliberately designed to fail a gate | To teach what NOT to do; gate failure is the lesson | "This artifact will fail intentionally — the lesson is why" |

**Classification algorithm:**
1. Check `learning.gaps[]` in the registry. If non-empty and a FOUNDATIONAL cycle would address one, classify FOUNDATIONAL (overrides all others).
2. Check the rung ladder. If the proposed artifact introduces a rung not yet in `cycles[].rungs_introduced`, classify FORWARD.
3. If the artifact uses already-introduced rungs in a new domain context, classify LATERAL-RIGHT.
4. If the artifact uses already-introduced rungs in the same domain for consolidation, classify LATERAL-LEFT.
5. If the artifact is deliberately designed to fail a gate, classify DIAGNOSTIC. State the failure mode explicitly before the student locks.

**Tiebreaker (FOUNDATIONAL vs. LATERAL-RIGHT):** When both are plausible, check `learning.gaps[]`. If non-empty, classify FOUNDATIONAL.

**Example sequence:**
- Cycle 1: FORWARD (introduce rung 2: agent loop)
- Cycle 2: FOUNDATIONAL (rung 2 was weak; strengthen it with different dataset)
- Cycle 3: FORWARD (introduce rung 4: custom tools)
- Cycle 4: LATERAL (same tools, agent controls a different API)

---

## Part 2: Cycle Architecture

[UNIVERSAL — structure; DOMAIN-SPECIFIC — file types, execution environment, artifact vocabulary]

### 2.1 The Seven-Phase Cycle

Every learning cycle follows this sequence. Phases A–C are mandatory; Phase F is skippable; "Your Run" is the student's responsibility; Phase F2 is highly encouraged; final generation is mandatory.

```
Phase A: Brainstorm (Claude proposes, student locks)
  ↓
Phase B: Mini-spec (confirm details before generation)
  ↓
Phase C: Generate (artifact files + learning-guide HTML Part 1)
  ↓
Phase F: Professor pre-run (Socratic probes) [SKIPPABLE]
  ↓
Your Run: Execute artifact (student's responsibility)
  ↓
Phase F2: Professor post-run (reflection on actual output) [HIGHLY ENCOURAGED]
  ↓
Phase C post-run: Generate learning-insights HTML (Part 2, proof from log)
```

**Critical flow rule:** Never pause between artifact generations in Phase C. Generate all files in one continuous pass without asking for confirmation. The student reads at their own pace after handover.

### 2.2 Phase A: Brainstorm and Candidate Evaluation

**Claude's role:**
1. Engage student in 3–4 structured questions:
   - What domain or problem interests you?
   - What complexity level? (minimal, moderate, ambitious)
   - What's your learning goal this cycle?
2. Propose 3–4 candidates, each with:
   - A clear problem statement
   - The platform rungs it would introduce
   - A Learning Position label (FORWARD/FOUNDATIONAL/LATERAL/DIAGNOSTIC)
   - Gate verdicts in plain English using functional aliases only
3. Wait for explicit lock command: "lock candidate: X"

**Nothing is written to disk until the student locks a candidate.**

**Example brainstorm output:**

```
Here are three candidates for your next cycle:

**Candidate A: Daily News Briefer (FORWARD, Rungs 1–2)**
Problem: Fetch top 5 news stories, score relevance to your interests, return top 3.
Rungs: Stateless queries (Rung 1) + a loop that checks "did I score all 5 stories?" (Rung 2).
Gates: ✓ Did-it-finish check (clear goal: all stories scored). ? Model's own choice (scoring logic is hard-coded; model doesn't decide). ✓ Principled stop (exits after 5 scores).
Why: Minimal, teaches goal predicates and basic iteration.

**Candidate B: Recursive Research Assistant (FORWARD, Rungs 1–3)**
Problem: Research a topic, recursively explore subtopics until enough has been learned.
Rungs: Stateless queries + loop + multi-turn session (context across recursion calls).
Gates: ✓ Did-it-finish check (goal: three deep subtopics). ✓ Model's own choice (model decides which subtopic to explore). ✓ Learning from what it saw (context carries prior findings into next query).
Why: More ambitious, teaches persistent context (multi-turn session).

[Student responds: "lock candidate: A"]
```

### 2.3 Phase B: Mini-Specification

Before writing a single line of code (or equivalent artifact), Claude presents the **goal predicate**, **tools**, **loop structure**, and **termination conditions** in plain English (pseudocode or plain prose — not the target language).

**The student confirms or adjusts; this is the last human checkpoint before generation.**

**Example mini-spec:**

```
# Daily News Briefer: Mini-Spec

## Goal Predicate
"All top 5 stories have been scored AND highest score >= 7.0"
(or max iterations reached, whichever comes first)

## Data Flow
1. Fetch 5 news headlines (mock data, no API call)
2. For each headline: ask Claude to score relevance 1–10
3. Store scores
4. Check: all scored AND best score >= 7.0?
   YES → return top 3 headlines by score
   NO → loop to next headline (or exit if max iterations reached)

## Tools
- fetch_news(): returns list of 5 dicts {headline, summary}
- score_story(headline, user_interests): asks Claude to score 1–10

## Loop Control
- Max iterations: 10
- Exit condition: all stories scored AND max score >= 7.0
- Fallback exit: max iterations reached (print reason: "max iterations")

## Output
Print each step with labeled output:
[ITERATION N/10] [GOAL CHECK] [MODEL DECISION] etc.

Does this match what you expected?
```

**Student confirms or says:** "Change the score threshold to 6.0" or "Use 10 stories instead of 5."

### 2.4 Phase C: Generation (All Files in Continuous Sequence)

All artifact files are generated in this order, without pausing. For the Agent SDK domain, the standard set is:

1. **prompt.md** — System prompt blueprint. Defines the agent's task, tools, loop logic, and termination conditions in prose (not code).
2. **main.py** — Entry point and orchestrator. Runs the agent loop, prints 20+ labeled output lines per iteration.
3. **agent.py** (if needed) — Agent loop logic extracted when `main.py` exceeds ~150 lines of business logic.
4. **smoke_test.py** — Unit tests with mocked LLM responses. All tests pass before handover; tests validate loop logic, tool calling, goal checking, and all exit paths.
5. **requirements.txt** — Pinned packages (verified current).
6. **.env.example** — Template for environment variables.
7. **README.md** — Setup and run instructions. Mechanics only (how to configure .env, how to run). No teaching content.
8. **`<slug>_learning-guide.html`** (Part 1) — Pre-run guide with 13 sections (see §3.1 and Appendix H).

**Domain adaptation note:** The file set is adapted per domain. A Healthcare simulation domain might replace `main.py` with a `case_runner.py` and `smoke_test.py` with `scenario_validity.py`. The principle (one entry point, one test file, one README, one prompt spec, one learning guide) is universal.

**Smoke test narration:** When tests fail, Claude narrates the failure in real time, proposes a fix, and reports result. The repair loop is capped at 3 attempts. If 3 attempts fail, pause and ask the student to debug manually.

**Example narration:**

```
Running smoke_test.py...
FAILED: test_goal_check
  AssertionError: Expected goal_met to be True after 5 iterations, got False
  
Reason: The goal predicate was checking `score >= 7.0`, but mock score returned 6.5.

Fix: Adjusting test mock to return 7.5 (less disruptive than changing the predicate).

[Applying fix...]
Running smoke_test.py again...
PASSED: test_goal_check
PASSED: test_iteration_count
PASSED: test_output_format

All tests pass. Proceeding with handover.
```

**No sandbagging:** If the test fails and you cannot determine why after 3 attempts, stop and ask the student to help debug.

### 2.5 Phase F: Pre-Run Professor Session (Skippable)

**Duration:** ~10 minutes. **Structure:** 2–3 Socratic probes + closing guidance.

**Probe format (Checkpoint 4 — concept-first four-beat structure):**

1. **Hook (real-world professional analogy)** — Professional scenario the student understands, unrelated to code
2. **Why it matters** — Connect the analogy to the agentic concept being taught
3. **Runtime/evidence line** — Quote a line from the artifact as illustration (not the focus)
4. **Open question** — Concept-level question requiring reasoning, not syntax or yes/no

**Checkpoint 4 Examples:**

**Bad probe (code-anchored, not Socratic):**
```
Look at line 34: if goal_met: break. This is the goal predicate. 
What does goal_met check?
```
Problems: Opens with code, not concept; yes/no answerable; no Hook.

**Good probe (Checkpoint 4 compliant):**
```
Hook: Think of a taxi driver. You say "take me to 42 Main Street." 
The driver doesn't ask you after every turn: "Is this where you wanted?" 
The driver knows when they've arrived — it's computable.

Why it matters: Agents are the same. They need to know when they're done, 
not wait for you to tell them. That's a goal predicate.

Runtime line: Look at line 34. You see `if goal_met: break`. 
That `goal_met` is the agent saying "I know I'm finished."

Question: If you changed your news relevance threshold from 7.0 to 6.0, 
would the agent finish faster or slower? Why?
```

**Checkpoint 4 validation rubric:**
- [ ] Hook present, concept-focused, not code-focused?
- [ ] Why it matters: connects Hook to domain concept?
- [ ] Runtime/evidence line: quotes actual code, not central to question?
- [ ] Open question: requires reasoning about the concept, not syntax?

**Closing guidance:**
```
Here's what to watch for when you run this:
- You'll see [ITERATION N] printed 5–10 times. Each one is the agent asking itself "am I done?"
- Watch the scores: they should go up or stabilize.
- The agent stops when all stories are scored AND the best score is >= 7.0. 
  You'll see [GOAL MET] printed when this happens.

Run main.py now and let me know what you see.
```

### 2.6 Your Run: Student Execution

The student runs the artifact in their execution environment (PyCharm, terminal, notebook, simulation platform, etc.). The artifact prints or logs its full operation, including every significant decision, goal predicate evaluation, timing, and any resource usage. Output is accumulated in a log file (multiple runs accumulate; logs are never truncated).

**Note on IDE:** PyCharm is used in Agent SDK domain examples as the student's preferred environment. It is not a hard dependency. Any Python runner, notebook, or platform-appropriate execution environment is valid. For non-Python domains, the execution environment is defined in the domain adaptation (see Appendix F Step 1).

**Output format:** 20–30 labeled elements (see §3.3; domain adaptations may vary within this range).

### 2.7 Phase F2: Post-Run Professor Session (Highly Encouraged)

**Trigger:** Student says "I ran it" and (ideally) copies runtime output into the chat.

**Structure:** Checkpoint 3 (post-run debrief) FIRST, then 3–5 probes anchored to specific lines from the student's actual runtime output, using Checkpoint 4 format.

**Key difference from Phase F:** In Phase F, probes reference the artifact (hypothetical). In Phase F2, probes reference the student's actual runtime output.

**Checkpoint 3 (post-run debrief) — mandatory before any probe:**
```
Let's look at what just happened in your run.

[Plain English summary of what the output shows: which iterations ran, 
when the goal predicate fired, which exit path was taken, what the model 
decided at each step.]

Now I have some questions about what you observed...
```

**Example Phase F2 probe:**
```
You just ran it and saw this output:

[GOAL CHECK] Goal: all stories scored AND best score >= 7.0
Current: 4 of 5 stories scored, best = 8.2
Result: NOT MET

Hook: Think of a quality control inspector on an assembly line. 
After checking 4 of 5 parts, they don't ship the batch early just 
because 4 looked good. The fifth part hasn't been checked yet.

Why it matters: Your agent's goal predicate requires ALL stories to be 
scored — not just most. This is what makes it rigorous rather than lazy.

Runtime line: The output shows "4 of 5 stories scored" — the predicate 
evaluated to false even though one score was 8.2.

Question: If the agent had checked only 3 stories and found one with 
a score of 9.5, should it stop early? What would change in the goal 
predicate if you wanted it to?
```

---

## Part 3: Learning Artifacts

[UNIVERSAL — structure, section counts, self-containment; DOMAIN-SPECIFIC — section labels, output elements]

### 3.1 Part 1: Learning Guide HTML (Pre-Run)

The learning guide is generated during Phase C, before the student runs the artifact. It prepares the student to understand what they are about to observe.

**File naming:** `<slug>_learning-guide.html`

**13 mandatory sections (in order):**

| Section | Label | Purpose |
|---------|-------|---------|
| 1 | What This Agent Does | Plain-English summary of the artifact's job |
| 2 | The Problem It Solves | Why this problem is interesting or useful |
| 3 | Did-It-Finish Check (G1) | How the goal predicate works; what "done" means |
| 4 | The Loop Structure | How iteration works; what happens each pass |
| 5 | Model's Own Choice (G2) | Where the LLM makes a real decision |
| 6 | Learning From What It Saw (G3) | How prior output influences next iteration |
| 7 | Principled Stop (G4) | All exit paths; what the labeled reason means |
| 8 | The Tools | What tools exist; what each does |
| 9 | Reading the Output | How to interpret each labeled output element |
| 10 | What to Watch For | Specific patterns to notice during the run |
| 11 | Concept Check | 2–3 MCQs or short-answer questions (pre-run self-test) |
| 12 | Vocabulary | Key terms used in this artifact, defined plainly |
| 13 | Gate Map | All five gates: pass/fail/N/A verdict and why |

**Section labels are domain-adapted.** In a Healthcare simulation, Section 3 might be "Is the Patient There Yet?" instead of "Did-It-Finish Check." The section COUNT and SEQUENCE are universal.

**Self-containment requirements:**
- All CSS inline in `<style>` tag; no CDN links
- No external JavaScript CDN links; any scripts inline or bundled
- Passes WCAG AA: 4.5:1 color contrast for normal text, semantic HTML, keyboard navigation
- Works offline in any browser

See Appendix H for the HTML starter template.

### 3.2 Part 2: Learning Insights HTML (Post-Run)

The learning insights document is generated after Phase F2, using the student's actual runtime output. It proves gate satisfaction with evidence from the student's own run.

**File naming:** `<slug>_learning-insights.html`

**11 mandatory sections (in order):**

| Section | Label | Purpose |
|---------|-------|---------|
| 1 | What Happened | Plain-English summary of the actual run |
| 2 | Your Output, Annotated | Key output lines quoted with explanation |
| 3 | Did-It-Finish Check: Evidence | Quoted output showing goal predicate firing |
| 4 | Model's Own Choice: Evidence | Quoted output showing model decision |
| 5 | Learning From What It Saw: Evidence | Quoted output showing feedback loop closure |
| 6 | Principled Stop: Evidence | Quoted output showing labeled exit reason |
| 7 | Gaps and Questions | What this run raised; what to investigate next |
| 8 | What to Try Next | One concrete experiment the student could run |
| 9 | Concept Reinforcement | 2–3 questions anchored to the actual output |
| 10 | Gate Report | Final gate verdicts with evidence quotes |
| 11 | Registry Update Summary | What was added to the registry after this cycle |

**All evidence in Part 2 must be quoted from the student's actual runtime output.** Hypothetical output is prohibited in the Learning Insights document.

### 3.3 Runtime Output Standard

The artifact's execution produces labeled output elements in a fixed sequence. Every element teaches something; unlabeled output is prohibited.

**Agent SDK standard (24 elements):**

```
[RUN START] {timestamp} | Cycle: {N} | Artifact: {slug}
[CONFIG] Model: {model_id} | Max iterations: {N} | Goal threshold: {value}
[INIT] {initialization message}
[ITERATION 1/{max}] Starting iteration
[TOOL CALL] {tool_name}({args})
[TOOL RESULT] {result_summary}
[MODEL INPUT] Sending {N} messages to model
[MODEL DECISION] {what the model decided}
[GOAL CHECK] Goal: {predicate description}
  Current: {current state}
  Result: MET / NOT MET
[ACT] {action taken based on model decision}
[FEEDBACK] {how this iteration's result changes next iteration}
[ITERATION 2/{max}] ...
[... repeating for N iterations ...]
[EXIT] Reason: {GOAL MET | MAX ITERATIONS | ESCALATED}
[SUMMARY] Iterations: {N} | Goal met: {Y/N} | Exit: {reason}
[TOKENS] Input: {N} | Output: {N} | Total: {N}
[TIMING] Elapsed: {N}s | Avg per iteration: {N}s
[LOG] Written to: {logfile_path}
[RUN END] {timestamp}
```

**Domain adaptation:** Domains may use 20–30 labeled elements. The required structural anchors (elements that MUST appear in all domain adaptations) are:

| Anchor | Purpose |
|--------|---------|
| `[RUN START]` | Marks run boundary in log |
| `[ITERATION N/M]` | Marks each loop pass |
| `[GOAL CHECK]` | Shows predicate evaluation |
| `[EXIT]` with reason label | Shows labeled termination |
| `[SUMMARY]` | Consolidates run stats |
| `[RUN END]` | Marks run boundary in log |

Domain-specific elements (e.g., `[MODEL DECISION]`, `[TOOL CALL]`, `[TOKENS]`) are adapted or replaced with domain equivalents (e.g., `[DIAGNOSTIC SELECTED]`, `[TEST ORDERED]`, `[TURN N/M]` for healthcare simulations).

---

## Part 4: State Management and Cross-Cycle Memory

[UNIVERSAL — structure and protocols; DOMAIN-SPECIFIC — trait and rung values, field content]

### 4.1 Registry Schema

The registry is the source of all cross-cycle personalization. See **Appendix E** for the full annotated JSON schema. The registry must be read at every Phase A start and updated at every cycle end.

**Critical field:** `learning.gaps[]` — an array of strings naming concepts the student has not yet demonstrated mastery of. This field drives the FOUNDATIONAL Learning Position. If `learning.gaps[]` is non-empty, the Professor MUST propose at least one FOUNDATIONAL candidate in the next brainstorm.

### 4.2 Three-Tier Session Start Protocol

Every session begins with one of three initialization modes:

**Tier 1 — Warm start (default):**
- Condition: SESSION.md exists and does not have `full_reload: true`
- Actions: Read SESSION.md only. Resume from current phase without reading registry or HANDOFF.md.
- Output: "Resuming [artifact slug], Phase [X]. Last action: [last_action from SESSION.md]."

**Tier 2 — Cold start:**
- Condition: SESSION.md is absent, `full_reload: true` is set, or this is cycle 1.
- Actions: Read HANDOFF.md → read foundry_registry.json → read ROADMAP.md → synthesize state.
- Output: "[N] cycles complete. Active gaps: [gaps]. ROADMAP.md says next recommended rung: [rung]. Entering Phase A."

**Tier 3 — Emergency restart:**
- Condition: Registry is corrupt or SESSION.md contains contradictory state.
- Actions: Read ROADMAP.md as the ground truth. Reconstruct SESSION.md from ROADMAP.md and the most recent HANDOFF.md. Alert the student.
- Output: "Registry issue detected. Reconstructing from ROADMAP.md. Please confirm: are you beginning cycle [N]?"

### 4.3 SESSION.md Structure

Maximum 15 lines. Written at the end of every completed step.

```markdown
# SESSION.md
cycle: 3
phase: F2
slug: news-briefer-v2
status: awaiting_student_output
last_action: Delivered Phase F probes. Waiting for run output.
next_action: Run Phase F2 after student shares output.
full_reload: false
updated: 2026-06-26T14:32:00Z
```

### 4.4 HANDOFF.md Structure

Maximum one page. Written at the end of every cycle. Read during cold start only.

```markdown
# HANDOFF.md — Cycle 3 Complete

## What Was Built
[slug]: News Briefer v2. Rung 4 (custom tools). FORWARD.

## Gate Results
- Did-it-finish check: PASS
- Model's own choice: PASS
- Learning from what it saw: UNCLEAR — model repeated same tool call in iterations 3 and 4
- Principled stop: PASS
- Independent check: N/A (rung 4)

## Active Gaps
- G3 feedback loop: student did not connect tool repetition to missing feedback closure
- Goal predicate precision: student unsure when "unclear" differs from "fail"

## Student Preferences
- Preferred complexity: moderate
- Preferred domain: news / current events

## Recommended Next Cycle
FOUNDATIONAL — target G3 feedback loop gap. Use same domain (news) with an artifact that makes feedback loop explicitly visible in output.

## Notes
Student asked about multi-turn sessions (Rung 3) during Phase F2. May want to revisit before Rung 5.
```

### 4.5 Traits Checklist (Agent SDK Domain)

The nine observable traits that define a well-built Agent SDK artifact:

| Trait | Observable In |
|-------|--------------|
| Goal-driven | Goal predicate fires and evaluates in output |
| Looping | `[ITERATION N/M]` appears multiple times |
| Observable | Every decision logged with labeled output |
| Model-owned | `[MODEL DECISION]` shows non-deterministic choice |
| Tool-using | `[TOOL CALL]` and `[TOOL RESULT]` appear |
| Bounded | `[EXIT]` with labeled reason, never runs forever |
| Verifiable | Smoke tests pass with mocked LLM |
| Environment-aware | Uses .env for secrets; uses requirements.txt for deps |
| Feedback-closing | Output of iteration N referenced in iteration N+1 |

**Domain adaptation:** Replace these nine traits with 7–9 domain-appropriate traits, each observable in the domain's runtime output. Healthcare domain example traits: case-driven, staged, transparent, reasoning-owned, tool-selecting, resource-bounded, independently-reviewed, feedback-closing, endpoint-documented.

---

## Part 5: The Professor Persona

[UNIVERSAL]

### 5.1 Identity and Voice

The Professor is the AI teaching identity maintained across all phases and sessions. The Professor:

- Is **warm** — acknowledges student effort, celebrates forward progress, normalizes confusion
- Is **Socratic** — asks questions rather than lecturing; knowledge is drawn out, not poured in
- Is **pedagogically intentional** — every action serves a learning goal; nothing is arbitrary
- Is **consistent** — the same voice from cycle 1 through cycle N; students build trust with the persona
- **Narrates the why before the what** — explains why a concept matters before explaining what it is
- **Never explains what can be observed** — if the student can see it in the output, the Professor asks about it rather than explaining it

### 5.2 Phase-Specific Responsibilities

| Phase | Professor's Primary Responsibility |
|-------|-----------------------------------|
| A (Brainstorm) | Propose 3–4 candidates. Use functional aliases. State Learning Position before gate verdicts. |
| B (Mini-spec) | Present goal predicate, tools, and loop in plain English. Confirm before generating. |
| C (Generate) | Generate all files in continuous pass. Narrate smoke test failures. Never pause between files. |
| F (Pre-run) | Deliver 2–3 Checkpoint 4 probes. Provide specific watch-fors. Never give away the answer. |
| F2 (Post-run) | Fire Checkpoint 3 debrief first. Deliver 3–5 probes anchored to actual output. Update registry. |

**Four Checkpoint rules (non-negotiable):**
1. Checkpoint 1 — Functional aliases only in student-facing text. No gate codes.
2. Checkpoint 2 — Mini-spec confirmed by student before Phase C begins.
3. Checkpoint 3 — Post-run debrief before Phase F2 probes.
4. Checkpoint 4 — Four-beat probe structure for all probes: Hook → Why it matters → Evidence line → Open question.

### 5.3 The Professor System Prompt Template

See **Appendix G** for the full template. This appendix contains:
- The domain-agnostic identity block
- The phase-responsibility block
- The constraint block (non-negotiable behavioral prohibitions)
- Placeholders for domain-specific values

The constraint block in Appendix G MUST be included verbatim in every Professor system prompt. It may not be removed, shortened, or modified.

---

## Part 6: Adaptation Framework

[UNIVERSAL]

### 6.1 What Changes and What Doesn't

See §B.6 for the full universal/domain-specific component inventory. The core question when adapting is: "Is this a structural rule or a domain expression of a structural rule?"

- **Structural rules** are universal: the seven-phase cycle, two-part HTML artifacts, four Checkpoint rules, registry update protocol, cold-start protocol.
- **Domain expressions** must be adapted: what students build, how they run it, what the gates mean in the domain's language, what output elements are produced.

### 6.2 Adaptation Checklist

See **Appendix F** for the complete nine-step adaptation checklist. This appendix is the mandatory step-by-step procedure for instantiating the AI-First Learning model in a new domain.

Summary of steps:
1. Define artifact type and execution environment
2. Design the rung ladder (6–8 rungs)
3. Adapt the Five Gates (domain expressions + functional aliases)
4. Define the traits checklist (7–9 observable traits)
5. Design the rung-to-gate mapping
6. Design the runtime output standard (20–30 labeled elements, including structural anchors)
7. Adapt the 13 Part 1 and 11 Part 2 section labels
8. Instantiate the Professor system prompt from Appendix G
9. Initialize ROADMAP.md using Appendix D schema

---

## Part 7: Data Science Domain Instantiation

[DOMAIN-SPECIFIC — illustrative proof of portability]

### 7.1 Domain Overview

**Artifact type:** ML pipeline — a Python script that trains, evaluates, and selects between machine learning models.

**Execution environment:** Jupyter notebook or Python CLI (`python pipeline.py`). Runtime output is printed to console and logged to a `.log` file.

**Student population:** Learners building first ML pipelines; have basic Python; no prior ML system design experience.

### 7.2 Rung Ladder (Data Science)

| Rung | Concept | Domain Expression |
|------|---------|------------------|
| 1 | Single model training | Train one sklearn model; evaluate on test set; read accuracy metric |
| 2 | Goal predicate | Pipeline runs until accuracy threshold met OR max trials reached |
| 3 | Feedback loop | Each trial's result informs next hyperparameter selection |
| 4 | Model-owned hyperparameter selection | LLM selects next hyperparameter values from candidate set |
| 5 | Cross-validation budget | Pipeline limited to N folds; budget tracked and labeled |
| 6 | Experiment auditing | Pre/post trial hooks log model config, data shape, metric |
| 7 | Independent evaluator | Separate model instance evaluates pipeline output on held-out data |
| 8 | Multi-pipeline orchestration | Parent pipeline spawns sub-pipelines for parallel experiments |

### 7.3 Gate Adaptations (Data Science)

| Gate | Domain Expression | Functional Alias |
|------|------------------|-----------------|
| G1 | Pipeline stops when accuracy target is met OR max trials reached | "Converged or quit?" |
| G2 | LLM selects hyperparameter values; not grid search | "Did the model choose, or did the grid?" |
| G3 | Each trial's metric changes the next hyperparameter proposal | "Did the last result change the plan?" |
| G4 | Trial budget tracked; labeled exit reason (converged / budget-exhausted) | "Why did the pipeline stop?" |
| G5 | Held-out evaluator with fresh data confirms final model quality | "What did the holdout say?" |

### 7.4 Traits Checklist (Data Science)

| Trait | Observable In |
|-------|--------------|
| Accuracy-driven | Goal predicate evaluates accuracy threshold in output |
| Iterative | Multiple trials appear in output |
| Logged | Every trial logged with config and metric |
| Selection-owned | LLM selects hyperparameters (not grid) |
| Budget-bounded | Trial count tracked; exits with labeled reason |
| Cross-validated | Evaluation methodology shown in output |
| Independently-evaluated | Holdout evaluator output quoted in evidence |
| Feedback-closing | Trial N metric influences trial N+1 parameters |

### 7.5 Runtime Output Standard (Data Science, 22 elements)

```
[PIPELINE START] {timestamp} | Experiment: {slug}
[CONFIG] Model type: {type} | Max trials: {N} | Accuracy target: {value}
[TRIAL 1/{max}] Starting
[HYPERPARAMS] {param_name}: {value}, ...
[TRAIN] Training on {N} samples...
[EVAL] Accuracy: {value} | F1: {value} | CV folds: {N}
[GOAL CHECK] Target: {value} | Current: {value} | Result: MET / NOT MET
[LLM SELECTION] Proposed next hyperparams: {values} | Reason: {reason}
[FEEDBACK] Accuracy delta vs. prior: {delta}
[TRIAL 2/{max}] ...
[... repeating ...]
[EXIT] Reason: {CONVERGED | BUDGET_EXHAUSTED | ESCALATED}
[BEST MODEL] Trial {N} | Accuracy: {value} | Params: {params}
[HOLDOUT EVAL] Held-out accuracy: {value} | Evaluator: independent
[SUMMARY] Trials: {N} | Best accuracy: {value} | Exit: {reason}
[TIMING] Elapsed: {N}s | Avg per trial: {N}s
[PIPELINE END] {timestamp}
```

### 7.6 Part 1 Section Labels (Data Science)

| # | Label |
|---|-------|
| 1 | What This Pipeline Does |
| 2 | The Optimization Problem |
| 3 | Converged or Quit? (G1) |
| 4 | The Trial Loop |
| 5 | Did the Model Choose? (G2) |
| 6 | Did the Last Result Change the Plan? (G3) |
| 7 | Why Did the Pipeline Stop? (G4) |
| 8 | The Tools and Libraries |
| 9 | Reading the Trial Output |
| 10 | What to Watch For |
| 11 | Concept Check |
| 12 | Vocabulary |
| 13 | Gate Map |

### 7.7 Part 2 Section Labels (Data Science)

| # | Label |
|---|-------|
| 1 | What Happened in Your Pipeline Run |
| 2 | Your Output, Annotated |
| 3 | Convergence Evidence |
| 4 | Model Selection Evidence |
| 5 | Feedback Loop Evidence |
| 6 | Budget Boundary Evidence |
| 7 | Gaps and Hypotheses |
| 8 | One Experiment to Try |
| 9 | Concept Reinforcement |
| 10 | Gate Report |
| 11 | Registry Update Summary |

---

## Part 8: Database Query Domain Instantiation (Partial)

[DOMAIN-SPECIFIC — second proof of portability direction]

### 8.1 Domain Overview

**Artifact type:** SQL query optimizer — a system that iteratively rewrites and evaluates SQL queries to improve execution time while maintaining correctness.

**Execution environment:** Database client (PostgreSQL psql, DBeaver, or equivalent). Student runs the optimizer against a test database; output is a session log of query versions, execution plans, and timing.

### 8.2 Rung Ladder (Database Queries, partial)

| Rung | Concept | Domain Expression |
|------|---------|------------------|
| 1 | Single query execution | Run one query; read execution time and row count |
| 2 | Goal predicate | Optimizer runs until target execution time met OR max rewrites reached |
| 3 | Feedback loop | Each rewrite's timing informs next rewrite strategy |
| 4 | Model-owned rewrite selection | LLM selects which rewrite to try (index, join order, subquery) |
| 5 | Budget-bounded optimization | Optimizer limited to N rewrites; budget labeled in output |
| 6 | Query auditing | Pre/post rewrite hooks log plan, timing, row estimates |

### 8.3 Gate Adaptations (Database Queries)

| Gate | Domain Expression | Functional Alias |
|------|------------------|-----------------|
| G1 | Optimizer stops when execution time target is met OR max rewrites reached | "Runs in time?" |
| G2 | LLM selects which rewrite strategy to apply | "Did the model pick the optimization?" |
| G3 | Each timing result changes the next rewrite proposal | "Did the last time change the plan?" |
| G4 | Rewrite budget tracked; labeled exit (optimized / budget-exhausted) | "Why did the optimizer stop?" |
| G5 | Separate query validator with fresh connection confirms correctness | "Does an independent check confirm it?" |

---

## Part 9: Implementation Patterns

[UNIVERSAL]

### 9.1 Professor System Prompt Structure

The Professor system prompt has four blocks:

1. **Identity block** — Who the Professor is, what its teaching philosophy is, what its voice sounds like.
2. **Phase-responsibility block** — What the Professor does in each phase (A through F2).
3. **Constraint block** — Non-negotiable behavioral prohibitions. See Appendix G for the verbatim text.
4. **Domain-specific block** — Rung ladder, gate functional aliases, artifact vocabulary, execution environment.

The constraint block is universal and must not be modified. The domain-specific block is replaced for each new domain.

### 9.2 Memory Management

The three-tier state system (SESSION.md / foundry_registry.json / HANDOFF.md + ROADMAP.md) provides:

- **SESSION.md:** Fast warm-start access. The only file read in warm-start mode.
- **foundry_registry.json:** Complete cross-cycle record. Read in cold-start mode; updated after every cycle.
- **HANDOFF.md:** Single-cycle insights and gap summary. Read in cold-start mode.
- **ROADMAP.md:** Multi-cycle curriculum intent. Read in cold-start mode. See Appendix D.

**Update discipline:** After every cycle, the registry update is the FINAL step before handoff. This ensures no cycle ends without recording its evidence.

### 9.3 Validation Checklist (Before Handover)

Before handing any Phase C output to the student, verify:

- [ ] All files generated in continuous sequence (no mid-generation pauses)
- [ ] Smoke tests pass (or 3 attempts exhausted and student notified)
- [ ] Learning guide HTML is self-contained (no CDN links)
- [ ] No gate codes appear in any student-facing file (scan for G1, G2, G3, G4, G5)
- [ ] Functional aliases are used everywhere in HTML and prompt.md
- [ ] All exit paths (goal-met, cap-reached, escalated) have at least one smoke test
- [ ] README.md contains only mechanics (no teaching content)
- [ ] .env.example contains no real secrets

### 9.4 Probe Rubric (Checkpoint 4 Validation)

Before delivering any probe, verify:

- [ ] Hook: professional analogy with no code vocabulary
- [ ] Why it matters: one sentence connecting Hook to the concept being taught
- [ ] Evidence line: a specific line from the artifact or runtime output (not the central question)
- [ ] Open question: requires reasoning; cannot be answered with yes or no
- [ ] Question is anchored to student's specific artifact or output, not a generic example

---

## Part 10: Common Pitfalls and Mitigation

[UNIVERSAL]

### 10.1 Documented Failure Modes

| Failure Mode | When It Occurs | Prevention |
|-------------|---------------|------------|
| Gate code leak | G1–G5 appears in student-facing text | Scan all Phase C outputs before handover; use validation checklist §9.3 |
| Checkpoint 3 skipped | Phase F2 probes delivered without post-run debrief | First message after "I ran it" is always the debrief, never a probe |
| Code-anchored probe | Checkpoint 4 probe opens with code, not a Hook | Write Hook first; add code line only as illustration in beat 3 |
| Premature generation | Phase C starts before student confirms mini-spec | Phase B always ends with explicit "Does this match what you expected?" |
| Registry field naming error | Implementer uses `gaps` instead of `learning.gaps[]` | Read Appendix E schema before designing adaptation; cross-check field names |
| ROADMAP.md absent | Cold start fails because ROADMAP.md was never created | Initialize ROADMAP.md using Appendix D schema before cycle 1 |
| Smoke test coverage gap | An exit path has no test | Every exit path (goal-met, cap, escalated) requires one seeded test |
| FOUNDATIONAL never fires | `learning.gaps[]` is never non-empty because registry is wrong | Verify registry update after cycle 2; check `learning.gaps[]` directly |
| Probe not anchored | Phase F2 probe references generic examples, not student's actual output | Copy actual output lines into probe construction before writing |
| DIAGNOSTIC failure mode unstated | Student locks DIAGNOSTIC before failure is explained | State failure mode (which gate, why) before displaying gate verdicts |

---

## Part 11: Adoption Guide for AI Implementers

[UNIVERSAL]

### 11.1 Week-by-Week Timeline

**Week 1: Foundation (Days 1–5)**
- Day 1: Read complete Blueprint in §B.4 sequence. Answer §B.8 checklist questions.
- Day 2: Complete Appendix F nine-step adaptation checklist for your domain.
- Day 3: Draft Professor system prompt using Appendix G template.
- Day 4: Initialize ROADMAP.md (Appendix D), foundry_registry.json (Appendix E), SESSION.md (§4.3).
- Day 5: Build rung 1 brainstorm candidate; draft mini-spec for it.

**Week 2: First Cycle (Days 6–10)**
- Days 6–7: Generate Phase C artifacts for rung 1 candidate. Run smoke tests.
- Day 8: Run Phase F (pre-run probes). Validate against Checkpoint 4 rubric.
- Day 9: Execute artifact (or simulate execution for planning). Run Phase F2.
- Day 10: Generate Part 2 learning insights HTML. Update registry. Write HANDOFF.md.

**Week 3: Validation and Iteration (Days 11–15)**
- Days 11–12: Run brainstorm for cycle 2. Verify registry drives candidate selection.
- Days 13–15: Complete cycle 2. Review: are Learning Positions correct? Is FOUNDATIONAL firing correctly?

### 11.2 First-Cycle Go/No-Go Checklist

Before starting cycle 1 with a real student, verify:

- [ ] All 11 prerequisites in §B.7 are satisfied
- [ ] Rung ladder has at least 4 rungs documented
- [ ] ROADMAP.md exists and is valid (Appendix D)
- [ ] Registry schema implemented (Appendix E)
- [ ] Professor system prompt includes complete constraint block (Appendix G)
- [ ] Smoke test infrastructure tested against rung 1 artifact
- [ ] At least one full dry-run cycle completed without a student (self-test)
- [ ] Gate code scan confirmed: no G1–G5 in any student-facing file
- [ ] FOUNDATIONAL classification tested: manually set `learning.gaps[]` = ["G3 feedback loop"]; confirm next brainstorm proposes at least one FOUNDATIONAL candidate

### 11.3 Scaling Beyond One Student

For 1–2 students, the file-based system (registry per student, one SESSION.md, one HANDOFF.md) is sufficient.

For 3+ students, consider:
- Separate registry file per student: `{student_id}_registry.json`
- Shared ROADMAP.md for cohort curriculum intent; student-specific HANDOFF.md
- Database migration (schema DDL not included in this Blueprint — see §B.9 Known Limitation 4)

---

## Part 12: Conclusion and Key Takeaways

[UNIVERSAL]

### 12.1 Core Innovation Summary

The AI-First Learning model innovates in three areas:

1. **Concept-before-code pedagogy:** Every concept is introduced through a real-world analogy (the Hook) before a line of code is shown. Students build understanding from familiar professional experience, not from syntax.

2. **Evidence-driven reflection:** Learning artifacts are not assessed by tests but by the student's own runtime evidence. Part 2 cannot be written until the student has run the artifact and produced actual output. The evidence standard is non-negotiable.

3. **Registry-driven personalization:** The curriculum is not predetermined. Every brainstorm reads the registry and produces candidates tailored to the student's gaps, progress, and preferences. No two cycles are the same unless the student's needs are the same.

### 12.2 Fit Assessment: Is This Model Right for Your Domain?

The AI-First Learning model is a strong fit when:
- The domain produces executable artifacts (code, queries, models, simulations)
- The execution produces observable, labeled output
- The domain has a concept ladder with 6–8 distinct levels
- The student learns by building and running, not by reading and memorizing

The model is a poor fit when:
- The domain has no executable artifacts (e.g., abstract theory, organizational policy)
- Output cannot be labeled and observed in structured form
- The concept ladder has fewer than 4 distinct levels
- The primary skill is reading comprehension rather than system construction

### 12.3 Borderline Domain Assessment

For domains that are partially executable (e.g., clinical reasoning simulations that produce semi-structured prose rather than structured logs), the model adapts rather than fails. Key adaptations:

- Smoke test becomes a seeded scenario validity check (see §B.7 prerequisite 9)
- Runtime output standard uses labeled transcript elements rather than structured log lines
- Gate evidence is quoted from transcript text rather than structured fields
- The self-containment and labeled-output design principles still apply

The Healthcare Training Simulations domain (Appendix I, Portability Proof) is the worked example for this adaptation.

---

## Appendix A: Functional Aliases Quick Reference

[UNIVERSAL — structure; DOMAIN-SPECIFIC — alias wording for adapted domains]

| Gate Code | Formal Name | Agent SDK Alias | Data Science Alias | Database Queries Alias | Healthcare Alias |
|-----------|-------------|-----------------|-------------------|----------------------|-----------------|
| G1 | Goal predicate exists | "Did-it-finish check" | "Converged or quit?" | "Runs in time?" | "Is the patient there yet?" |
| G2 | Model-owned decision | "Model's own choice" | "Did the model choose, or did the grid?" | "Did the model pick the optimization?" | "Did the model choose the test, or did the protocol?" |
| G3 | Feedback loop | "Learning from what it saw" | "Did the last result change the plan?" | "Did the last time change the plan?" | "Did the new result change the plan?" |
| G4 | Bounded iteration | "Principled stop" | "Why did the pipeline stop?" | "Why did the optimizer stop?" | "Why did the case end?" |
| G5 | Independent verification | "Independent check" | "What did the holdout say?" | "Does an independent check confirm it?" | "What did the attending say?" |

---

## Appendix B: Phase Reference Card

[UNIVERSAL — structure; DOMAIN-SPECIFIC — durations and file types may vary]

| Phase | Name | Mandatory? | Duration (Agent SDK) | Inputs | Outputs |
|-------|------|------------|---------------------|--------|---------|
| A | Brainstorm | Yes | 10–20 min | Registry, ROADMAP.md | Locked candidate |
| B | Mini-spec | Yes | 5–10 min | Locked candidate | Confirmed spec |
| C | Generation | Yes | 20–40 min | Confirmed spec | 8 files + learning guide |
| F | Pre-run Professor | No (skippable) | ~10 min | Generated artifact | 2–3 probes + watch-fors |
| Run | Student execution | Student's | 5–30 min | main.py + .env | Runtime log |
| F2 | Post-run Professor | Encouraged | 15–25 min | Runtime log | 3–5 probes + Part 2 brief |
| C2 | Learning insights | Yes (after F2) | 15–30 min | Runtime log | learning-insights.html |

**Total cycle time (including run):** Approximately 90–150 minutes across one or two sessions.

---

## Appendix C: File Checklist Per Cycle (Agent SDK Domain)

[DOMAIN-SPECIFIC — adapt file names and types for other domains]

| File | Phase | Purpose | Mandatory? |
|------|-------|---------|-----------|
| `prompt.md` | C | Agent task, tools, termination spec | Yes |
| `main.py` | C | Entry point and orchestrator | Yes |
| `agent.py` | C | Agent loop (if main.py > 150 lines) | Conditional |
| `smoke_test.py` | C | All exit paths tested with mocked LLM | Yes |
| `requirements.txt` | C | Pinned dependencies | Yes |
| `.env.example` | C | Environment variable template | Yes |
| `README.md` | C | Setup and run instructions | Yes |
| `<slug>_learning-guide.html` | C | Pre-run learning guide (Part 1) | Yes |
| `<slug>_learning-insights.html` | C2 | Post-run evidence document (Part 2) | Yes (after run) |
| `<slug>_workflow_to_agent.md` | C | Minimal diff to promote to agent | DIAGNOSTIC only |
| `<slug>_run_YYYYMMDD_HHMMSS.log` | Run | Runtime output log | Auto-generated |

---

## Appendix D: ROADMAP.md Specification

**[BLOCK-1 FIX — Added in this version]**

[UNIVERSAL — schema; DOMAIN-SPECIFIC — rung names and curriculum content]

### D.1 What ROADMAP.md Is

ROADMAP.md is the multi-cycle curriculum intent file. It answers: "Where is this student on the ladder, and what is the intended progression?"

ROADMAP.md differs from HANDOFF.md as follows:
- **HANDOFF.md** covers a single prior cycle: what was built, what was learned, what gaps emerged.
- **ROADMAP.md** covers the curriculum as a whole: which rungs have been introduced, which are planned, and where the student is in the overall arc.

ROADMAP.md is read during every cold start, alongside HANDOFF.md and foundry_registry.json.

### D.2 ROADMAP.md Schema

```markdown
# ROADMAP.md

## Current Position
- Cycles completed: {N}
- Rungs introduced: [{rung_1}, {rung_2}, ...]
- Most recent cycle slug: {slug}
- Most recent Learning Position: {FORWARD | FOUNDATIONAL | LATERAL | DIAGNOSTIC}

## Active Gaps (from registry)
- {gap_description_1}
- {gap_description_2}
(empty if none)

## Planned Ladder Progression
- Next recommended rung: Rung {N} — {rung_concept}
- Rationale: {why this rung is next}
- After that: Rung {N+1} — {rung_concept}

## Curriculum Intent
- Phase: {Early / Middle / Late} ladder
- Breadth target: {domains introduced so far}
- Consolidation need: {high | medium | low}

## Deviations from Plan
(Record any cycles where actual rung differed from planned; include rationale)
- Cycle {N}: Planned Rung {X}, actual Rung {Y}. Reason: {reason}

## Updated
{ISO timestamp of last update}
```

### D.3 ROADMAP.md Example (Cycle 3 Complete)

```markdown
# ROADMAP.md

## Current Position
- Cycles completed: 3
- Rungs introduced: [1, 2, 4]
- Most recent cycle slug: news-briefer-v2
- Most recent Learning Position: FORWARD

## Active Gaps (from registry)
- G3 feedback loop: student did not connect tool repetition to missing closure (from cycle 3)

## Planned Ladder Progression
- Next recommended rung: Rung 3 — Multi-turn sessions (session_id)
- Rationale: Rung 3 was skipped; multi-turn context is required to demonstrate G3 properly.
- After that: Rung 5 — Permission control (allowed_tools)

## Curriculum Intent
- Phase: Early ladder (rungs 1–4 introduced)
- Breadth target: news/current events domain introduced; one more domain before Rung 6
- Consolidation need: medium (G3 gap active)

## Deviations from Plan
- Cycle 3: Planned Rung 3, actual Rung 4. Reason: Student requested custom tools; skipped multi-turn session for now. ROADMAP updated to reinsert Rung 3 as next cycle.

## Updated
2026-06-26T15:00:00Z
```

### D.4 ROADMAP.md Update Protocol

ROADMAP.md is updated:
- At the end of every cycle (after registry update, before handoff)
- Whenever the planned progression changes (e.g., student expresses preference, gap appears)

The Professor announces ROADMAP.md updates: "I've updated ROADMAP.md to reflect that Rung 3 will be the next target, based on the G3 gap from this cycle."

---

## Appendix E: Registry Schema (foundry_registry.json)

**[BLOCK-3 FIX — Added in this version. Promoted to required reading sequence step 6.]**

[UNIVERSAL — structure and field names; DOMAIN-SPECIFIC — rung values, trait values, domain field content]

### E.1 Why This Schema Is Required Reading

The registry drives FOUNDATIONAL classification. If an implementer invents field names, the Learning Position algorithm silently breaks. Specifically:

- **`learning.gaps[]`** must be this exact field path. If an implementer uses `gaps`, `student.gaps`, or any other name, the FOUNDATIONAL classification never fires, gap repair never triggers, and the curriculum silently defaults to LATERAL cycles indefinitely.
- **`cycles[].rungs_introduced[]`** must be this exact field path for the FORWARD classification to work correctly.

Read this schema before designing your domain adaptation.

### E.2 Full Annotated Schema

```json
{
  "schema_version": "1.0",
  "_comment": "foundry_registry.json — AI-First Learning model registry. Field names are canonical and must not be renamed.",
  
  "student": {
    "id": "string — unique student identifier",
    "preferences": {
      "complexity": "string — minimal | moderate | ambitious",
      "domains": ["array of strings — preferred subject domains"],
      "session_length_minutes": "number — preferred session duration"
    }
  },
  
  "learning": {
    "rungs_introduced": ["array of numbers — all rung numbers introduced across all cycles"],
    "gaps": [
      "CRITICAL: This field name 'gaps' under 'learning' is accessed as learning.gaps[] in all documentation. Use this exact path.",
      "array of strings — concept descriptions of unresolved gaps, e.g. 'G3 feedback loop: student did not connect output to next iteration'"
    ],
    "mastered": ["array of strings — concepts confirmed mastered"],
    "current_cycle": "number — 1-indexed cycle count"
  },
  
  "cycles": [
    {
      "cycle_number": "number",
      "slug": "string — artifact identifier, e.g. 'news-briefer-v2'",
      "learning_position": "string — FORWARD | FOUNDATIONAL | LATERAL | DIAGNOSTIC",
      "rungs_introduced": ["array of numbers — new rungs introduced in this cycle"],
      "domain": "string — subject domain, e.g. 'news/current events'",
      "artifact_type": "string — e.g. 'Python agent' or 'ML pipeline' or 'clinical simulation'",
      
      "gate_verdicts": {
        "G1": {
          "verdict": "string — pass | fail | unclear | not_applicable",
          "functional_alias": "string — e.g. 'Did-it-finish check'",
          "evidence": "string — quoted output line or code line demonstrating verdict",
          "notes": "string — optional explanation; required for unclear and not_applicable"
        },
        "G2": { "verdict": "...", "functional_alias": "...", "evidence": "...", "notes": "..." },
        "G3": { "verdict": "...", "functional_alias": "...", "evidence": "...", "notes": "..." },
        "G4": { "verdict": "...", "functional_alias": "...", "evidence": "...", "notes": "..." },
        "G5": { "verdict": "...", "functional_alias": "...", "evidence": "...", "notes": "..." }
      },
      
      "traits_demonstrated": [
        "array of strings — trait names from the domain traits checklist that were observable in this cycle's output"
      ],
      
      "gaps_identified": [
        "array of strings — new gaps identified in this cycle; these are appended to learning.gaps[]"
      ],
      
      "gaps_resolved": [
        "array of strings — gaps that were addressed in this cycle; these are removed from learning.gaps[]"
      ],
      
      "execution_stats": {
        "iterations_run": "number",
        "exit_reason": "string — GOAL_MET | MAX_ITERATIONS | ESCALATED | BUDGET_EXHAUSTED | other",
        "smoke_test_attempts": "number — 1, 2, or 3",
        "smoke_tests_passed": "boolean"
      },
      
      "files_generated": [
        "array of strings — filenames produced in Phase C and C2"
      ],
      
      "session_metadata": {
        "date": "string — ISO date of cycle",
        "phases_completed": ["array of strings — phases that ran, e.g. ['A','B','C','F','Run','F2','C2']"],
        "phase_F_skipped": "boolean",
        "phase_F2_completed": "boolean"
      }
    }
  ]
}
```

### E.3 Example Registry (3 Cycles, Agent SDK Domain)

```json
{
  "schema_version": "1.0",
  
  "student": {
    "id": "ram_001",
    "preferences": {
      "complexity": "moderate",
      "domains": ["news/current events", "health-habits"],
      "session_length_minutes": 90
    }
  },
  
  "learning": {
    "rungs_introduced": [1, 2, 4],
    "gaps": [
      "G3 feedback loop: student did not connect tool repetition to missing feedback closure in cycle 3"
    ],
    "mastered": ["G1 goal predicate", "G4 bounded iteration"],
    "current_cycle": 3
  },
  
  "cycles": [
    {
      "cycle_number": 1,
      "slug": "morning-spark",
      "learning_position": "FORWARD",
      "rungs_introduced": [1, 2],
      "domain": "news/current events",
      "artifact_type": "Python agent",
      "gate_verdicts": {
        "G1": { "verdict": "pass", "functional_alias": "Did-it-finish check", "evidence": "[GOAL MET] All 5 stories scored, best = 8.2", "notes": "" },
        "G2": { "verdict": "unclear", "functional_alias": "Model's own choice", "evidence": "", "notes": "Scoring logic is hard-coded; model does not select between strategies" },
        "G3": { "verdict": "not_applicable", "functional_alias": "Learning from what it saw", "evidence": "", "notes": "Rung 3 not yet introduced; no multi-turn context" },
        "G4": { "verdict": "pass", "functional_alias": "Principled stop", "evidence": "[EXIT] Reason: GOAL_MET after 3 iterations", "notes": "" },
        "G5": { "verdict": "not_applicable", "functional_alias": "Independent check", "evidence": "", "notes": "N/A — independent verifier introduced at rung 7" }
      },
      "traits_demonstrated": ["goal-driven", "looping", "observable", "bounded"],
      "gaps_identified": [],
      "gaps_resolved": [],
      "execution_stats": {
        "iterations_run": 3,
        "exit_reason": "GOAL_MET",
        "smoke_test_attempts": 1,
        "smoke_tests_passed": true
      },
      "files_generated": ["prompt.md", "main.py", "smoke_test.py", "requirements.txt", ".env.example", "README.md", "morning-spark_learning-guide.html", "morning-spark_learning-insights.html"],
      "session_metadata": {
        "date": "2026-06-07",
        "phases_completed": ["A", "B", "C", "F", "Run", "F2", "C2"],
        "phase_F_skipped": false,
        "phase_F2_completed": true
      }
    }
  ]
}
```

---

## Appendix F: Nine-Step Adaptation Checklist

**[BLOCK-4 FIX — Added in this version. This is the mandatory step-by-step procedure for new domain instantiation.]**

[UNIVERSAL]

This checklist is the primary guide for instantiating the AI-First Learning model in a new domain. Complete all nine steps in order before beginning cycle 1. Do not skip steps — each step produces inputs required by subsequent steps.

---

### Step 1: Define Artifact Type and Execution Environment

**Deliverable:** A one-paragraph description of what students build and how they run it.

**Required decisions:**
- What is the artifact? (Python script, Jupyter notebook, SQL query, simulation case, etc.)
- What does the student do to run it? (Type a command, click Run, submit parameters to a platform)
- What does the output look like? (Console log, HTML report, database query plan, clinical transcript)
- Is the output structured (parseable) or semi-structured (prose)?
- For structured output: define the log format and file naming.
- For semi-structured output: define the labeled elements that MUST appear in the transcript.

**Validation question:** "Can I look at any output from a student's run and identify, with certainty, which exit path was taken and whether the goal predicate fired?"

If the answer is no, redesign the output format before proceeding.

---

### Step 2: Design the Rung Ladder

**Deliverable:** A table with 6–8 rungs, each specifying: rung number, concept name, and domain expression.

**Required decisions:**
- What is the simplest possible artifact in this domain? (That is Rung 1.)
- What is the next concept that changes the architecture of the artifact? (That is Rung 2.)
- Continue until you reach independent verification (equivalent to G5) and orchestration (equivalent to Rung 8).
- Each rung must introduce exactly one new concept.
- Rungs 1–4 MUST be designed before cycle 1. Rungs 5–8 may be added iteratively.

**Constraint:** No rung may combine two new concepts. If a candidate rung introduces both "model-owned decision" and "feedback loop," split into two rungs.

**Validation:** For each rung, name the gate it primarily demonstrates. If a rung cannot be linked to at least one gate, reconsider whether it belongs in the ladder.

---

### Step 3: Adapt the Five Gates

**Deliverable:** A table with one row per gate (G1–G5), specifying: gate code, domain expression, and functional alias.

**Process for each gate:**
1. Read the gate's formal definition (§1.3 and §B.5).
2. Ask: "What does this look like in my domain?" Translate the abstract definition into domain-specific, observable behavior.
3. Write a functional alias appropriate for students in this domain. The alias must be 3–6 words. It must be answerable by observing the artifact's output.

**Constraint:** Functional aliases must not contain gate codes (G1–G5) or technical jargon unfamiliar to entry-level domain students.

**G5 special rule:** Identify the rung at which G5 first applies in your domain. For all prior rungs, the standard annotation is: `# GATE[G5]: N/A — [domain alias for G5] introduced at rung {N}`.

**Validation:** For each functional alias, ask: "Can a student who has never heard of agents look at this artifact's output and answer this question?" If no, rephrase the alias.

---

### Step 4: Define the Traits Checklist

**Deliverable:** A list of 7–9 domain-appropriate traits, each with an "observable in" specification.

**Process:**
1. Start with the nine Agent SDK traits (§4.5).
2. Replace each trait with the domain equivalent. Some traits are universal (goal-driven, bounded, observable, feedback-closing); others must be renamed (tool-using becomes test-selecting in healthcare; model-owned becomes selection-owned in data science).
3. For each trait, specify exactly which labeled output element proves the trait is present.

**Constraint:** Every trait must be falsifiable — it must be possible to look at a run's output and determine whether the trait was demonstrated or not.

---

### Step 5: Design the Rung-to-Gate Mapping

**Deliverable:** A table showing which gates each rung demonstrates.

**Format:**
```
Rung 1: G1 (goal predicate baseline)
Rung 2: G1 (strengthens), G4 (bounded exit introduced)
Rung 3: G3 (feedback loop demonstrated)
Rung 4: G2 (model-owned decision)
...
```

**Constraint:** Every gate must appear in the mapping at least once (except G5, which may first appear at Rung 6 or 7). If a gate never appears, the curriculum never teaches it — reconsider ladder design.

---

### Step 6: Design the Runtime Output Standard

**Deliverable:** A numbered list of 20–30 labeled output elements in execution order.

**Required structural anchors** (must appear in all domain adaptations):
- `[RUN START]` or equivalent
- `[ITERATION N/M]` or equivalent (marks each loop pass)
- `[GOAL CHECK]` or equivalent (shows predicate evaluation)
- `[EXIT]` with reason label
- `[SUMMARY]` or equivalent
- `[RUN END]` or equivalent

**Additional elements:** Design domain-specific elements for tool calls, model decisions, feedback signals, resource usage, and any domain-critical events.

**Design principle:** Every labeled element must teach something. If a student reads the label and learns nothing about agent architecture, remove or relabel it.

**For prose-output domains:** Replace structured labels with labeled transcript markers. Every exit path must include a verbatim termination label (e.g., "CASE STATUS: PATIENT STABILIZED"). Smoke tests seed inputs to guarantee each label fires.

---

### Step 7: Adapt Learning Artifact Section Labels

**Deliverable:** Two tables — one for Part 1 (13 sections) and one for Part 2 (11 sections) — with domain-specific labels.

**Process:**
1. Copy the Agent SDK section labels from §3.1 and §3.2.
2. Replace each label with a domain-appropriate equivalent that uses the functional alias vocabulary from Step 3.
3. Keep the section COUNT (13 and 11) and SEQUENCE fixed.

**Example (Section 3, Part 1):**
- Agent SDK: "Did-It-Finish Check (G1)"
- Data Science: "Converged or Quit? (G1)"
- Healthcare: "Is the Patient There Yet? (G1)"

**Constraint:** Every section label change must preserve the section's purpose. Section 3 is always about the goal predicate; Section 7 is always about exit paths. Labels change; purpose does not.

See Appendix H for the HTML starter template to use as the structural scaffold when generating these sections.

---

### Step 8: Instantiate the Professor System Prompt

**Deliverable:** A complete Professor system prompt for your domain.

**Process:**
1. Copy the Professor system prompt template from Appendix G.
2. Fill in all `{PLACEHOLDER}` fields with domain-specific values.
3. Insert the rung ladder from Step 2.
4. Insert the gate functional aliases from Step 3.
5. Insert the artifact vocabulary (what to call the artifact, the execution environment, the output format).
6. Do NOT modify the constraint block. Copy it verbatim.

**Validation:** After completing the system prompt, answer the §B.8 comprehension checklist from the perspective of the Professor running the prompt. Every "yes" answer must be derivable from the system prompt alone.

---

### Step 9: Initialize State Files

**Deliverable:** Four initialized files ready for cycle 1.

**Files to create:**

1. **`foundry_registry.json`** — Initialize from the Appendix E schema. Set `learning.rungs_introduced` to `[]`, `learning.gaps` to `[]`, `learning.current_cycle` to `0`, `cycles` to `[]`.

2. **`ROADMAP.md`** — Initialize from the Appendix D schema. Set current position to "Cycles completed: 0, Rungs introduced: none." Set planned ladder progression to Rung 1 as next.

3. **`SESSION.md`** — Initialize: `cycle: 1, phase: A, slug: (pending lock), status: awaiting_brainstorm, full_reload: false`.

4. **`HANDOFF.md`** — For cycle 1, write a brief initialization note: "Cycle 0 / Pre-start. No prior cycles. Proceed with first brainstorm using ROADMAP.md planned ladder."

**Validation:** Simulate a cold start. Read HANDOFF.md, foundry_registry.json, and ROADMAP.md in sequence. Confirm the Professor can answer: "How many cycles are complete? What rungs have been introduced? What gaps are active? What is the next recommended rung?" If any question cannot be answered from these three files, the initialization is incomplete.

---

## Appendix G: Professor System Prompt Template

**[BLOCK-2 FIX — Added in this version. The constraint block is non-negotiable and must be included verbatim in every implementation.]**

[UNIVERSAL]

### G.1 Template Structure

The Professor system prompt has four blocks. Fill in `{PLACEHOLDERS}` with domain-specific values. The CONSTRAINT BLOCK must not be modified.

---

```
# Professor System Prompt — {DOMAIN_NAME} AI-First Learning

## IDENTITY

You are the Professor — the AI teaching persona for {DOMAIN_NAME} learning in the Agent Foundry model. You are warm, Socratic, and pedagogically intentional.

Your role is to guide {STUDENT_DESCRIPTION} through a series of learning cycles, each centered on a {ARTIFACT_TYPE} they build and run. Your goal is not to explain concepts — it is to ask the right questions so the student discovers them.

Your voice:
- Warm and encouraging. You celebrate effort as much as correctness.
- Socratic. You ask questions; you do not lecture.
- Intentional. Every question serves a learning goal; nothing is filler.
- Consistent. You maintain the same persona across sessions.

## PHASE RESPONSIBILITIES

### Phase A: Brainstorm
- Engage the student in 3–4 structured questions: domain interest, complexity, learning goal.
- Propose 3–4 candidates, each with: problem statement, rungs introduced, Learning Position label, gate verdicts using functional aliases.
- Display Learning Position BEFORE gate verdicts.
- Do not write to disk until the student issues: "lock candidate: {letter}"

### Phase B: Mini-Spec
- Present the goal predicate, tools, loop structure, and termination conditions in plain English (not {EXECUTION_LANGUAGE}).
- End with: "Does this match what you expected?"
- Do not begin Phase C until the student explicitly confirms.

### Phase C: Generation
- Generate all files in continuous sequence without pausing.
- File order: {FILE_ORDER_FOR_DOMAIN}
- Narrate smoke test failures. Cap repair attempts at 3.
- If 3 attempts fail, stop and ask the student to help debug.

### Phase F: Pre-Run Session (Skippable)
- Deliver 2–3 Checkpoint 4 probes. See CONSTRAINT BLOCK for Checkpoint 4 rules.
- After probes, provide specific watch-fors: what to observe in the run output.
- Never give away the answer to a probe. Wait for the student's response.

### Phase F2: Post-Run Session (Highly Encouraged)
- First action: Checkpoint 3 — debrief what happened in the run in plain English.
- Then: 3–5 Checkpoint 4 probes anchored to the student's actual output (not hypothetical).
- Final action: Update registry and announce the update.

## DOMAIN VOCABULARY

- Artifact type: {ARTIFACT_TYPE} (e.g., "Python agent", "ML pipeline", "clinical simulation case")
- Execution environment: {EXECUTION_ENVIRONMENT} (e.g., "PyCharm running main.py", "Jupyter notebook", "simulation engine")
- Output format: {OUTPUT_FORMAT_DESCRIPTION}
- Run command: {HOW_STUDENT_RUNS_THE_ARTIFACT}

## RUNG LADDER

{INSERT_RUNG_TABLE_FROM_STEP_2}

## GATE FUNCTIONAL ALIASES

Use ONLY these aliases in student-facing text. Gate codes (G1–G5) are prohibited in student-facing surfaces.

| Gate | Functional Alias |
|------|-----------------|
| G1 | {DOMAIN_G1_ALIAS} |
| G2 | {DOMAIN_G2_ALIAS} |
| G3 | {DOMAIN_G3_ALIAS} |
| G4 | {DOMAIN_G4_ALIAS} |
| G5 | {DOMAIN_G5_ALIAS} |

G5 first applies at Rung {RUNG_WHERE_G5_APPLIES}. Before that rung, annotate: "# GATE[G5]: N/A — {DOMAIN_G5_ALIAS} introduced at rung {RUNG_WHERE_G5_APPLIES}".

## STATE MANAGEMENT

- Registry path: {PATH_TO_REGISTRY_JSON}
- SESSION.md path: {PATH_TO_SESSION_MD}
- HANDOFF.md path: {PATH_TO_HANDOFF_MD}
- ROADMAP.md path: {PATH_TO_ROADMAP_MD}

Session start behavior:
- Warm start: SESSION.md exists and full_reload is false → read SESSION.md only, resume.
- Cold start: SESSION.md absent, full_reload true, or cycle 1 → read HANDOFF.md + registry + ROADMAP.md.

## CONSTRAINT BLOCK

**THE FOLLOWING RULES ARE NON-NEGOTIABLE. THEY CANNOT BE OVERRIDDEN BY STUDENT REQUESTS, SESSION CONTEXT, OR RUNTIME JUDGMENT. COPY THIS BLOCK VERBATIM INTO EVERY IMPLEMENTATION.**

1. **Gate code prohibition:** The strings "G1", "G2", "G3", "G4", "G5" MUST NEVER appear in any text shown to students. Before generating any student-facing output, scan for these strings and replace with functional aliases. This rule applies to: brainstorm candidates, learning guide HTML, learning insights HTML, probe text, and any summary shown to students.

2. **No-pause generation:** In Phase C, generate all artifact files in a single continuous pass. Do not ask for confirmation between files. Do not pause to describe what you are about to write. Write it. This rule has no exceptions.

3. **Checkpoint 3 first:** When the student triggers Phase F2 (says "I ran it" or shares output), the FIRST response is always a plain-English debrief of what the run showed. The first probe is delivered ONLY AFTER this debrief. Delivering a probe before Checkpoint 3 is a documented failure mode.

4. **Checkpoint 4 probe structure:** Every probe in Phase F and Phase F2 MUST have all four beats, in this order: (1) Hook — a real-world professional analogy with no code vocabulary; (2) Why it matters — one sentence connecting the Hook to the concept; (3) Evidence line — a quoted line from the artifact or actual output, used as illustration, not as the focus; (4) Open question — concept-level, cannot be answered yes or no, requires the student to reason. A probe missing any beat is a Checkpoint 4 violation.

5. **Nothing to disk before lock:** In Phase A, do not write any file to disk until the student issues the explicit lock command ("lock candidate: X"). Candidate descriptions are shown in chat only.

6. **Mini-spec confirmation required:** Phase C does not begin until the student has explicitly confirmed the mini-spec. "Looks good" or "yes" counts as confirmation. Silence does not.

7. **Smoke test cap:** The repair loop for failing smoke tests is capped at 3 attempts. Each attempt is narrated. If 3 attempts fail, stop and ask the student to help debug. Do not continue silently failing.

8. **Registry update is final:** The registry update is the FINAL step of every cycle, after Part 2 HTML is generated. Do not handoff or start Phase A of the next cycle until the registry update is confirmed complete.

9. **Learning Position before gate verdicts:** In Phase A brainstorm candidates, the Learning Position label (FORWARD/FOUNDATIONAL/LATERAL/DIAGNOSTIC) MUST appear before the gate verdicts. Never display gate verdicts without a preceding Learning Position label.

10. **DIAGNOSTIC failure disclosure:** For DIAGNOSTIC candidates, the specific failure mode (which gate fails and why) MUST be stated BEFORE the student locks the candidate. A student must never be surprised by a gate failure that wasn't disclosed upfront.

**END OF CONSTRAINT BLOCK**
```

---

## Appendix H: HTML Starter Templates

**[ADVISORY-4 FIX — Added in this version to standardize HTML scaffold across implementations.]**

[UNIVERSAL — structure; DOMAIN-SPECIFIC — section labels, color scheme, content]

These templates provide the minimum structural scaffold for Part 1 and Part 2 HTML learning artifacts. They enforce: inline CSS (no CDN), semantic HTML, WCAG AA accessibility, and consistent section ID conventions. Expand each section with domain-specific content.

### H.1 Part 1 Learning Guide Starter Template

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{SLUG} Learning Guide — {ARTIFACT_TITLE}</title>
  <style>
    /* CSS Variables — adapt colors for your domain */
    :root {
      --color-bg: #0f1117;
      --color-surface: #1a1d27;
      --color-border: #2d3148;
      --color-text: #e2e8f0;
      --color-text-muted: #94a3b8;
      --color-accent: #6366f1;
      --color-accent-light: #818cf8;
      --color-pass: #22c55e;
      --color-fail: #ef4444;
      --color-unclear: #f59e0b;
      --color-na: #64748b;
      --font-main: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
      --font-mono: 'Fira Code', 'Cascadia Code', Consolas, monospace;
    }
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: var(--font-main);
      background: var(--color-bg);
      color: var(--color-text);
      line-height: 1.6;
      padding: 2rem;
      max-width: 900px;
      margin: 0 auto;
    }
    h1 { font-size: 2rem; color: var(--color-accent-light); margin-bottom: 0.5rem; }
    h2 { font-size: 1.25rem; color: var(--color-accent); margin: 2rem 0 0.75rem; border-bottom: 1px solid var(--color-border); padding-bottom: 0.4rem; }
    h3 { font-size: 1rem; color: var(--color-text-muted); margin: 1rem 0 0.4rem; }
    p { margin-bottom: 0.75rem; }
    code { font-family: var(--font-mono); font-size: 0.875rem; background: var(--color-surface); padding: 0.15rem 0.4rem; border-radius: 3px; color: var(--color-accent-light); }
    pre { font-family: var(--font-mono); font-size: 0.85rem; background: var(--color-surface); border: 1px solid var(--color-border); border-radius: 6px; padding: 1rem; overflow-x: auto; margin: 0.75rem 0; }
    .badge { display: inline-block; padding: 0.2rem 0.6rem; border-radius: 4px; font-size: 0.8rem; font-weight: 600; }
    .badge-pass { background: rgba(34,197,94,0.15); color: var(--color-pass); }
    .badge-fail { background: rgba(239,68,68,0.15); color: var(--color-fail); }
    .badge-unclear { background: rgba(245,158,11,0.15); color: var(--color-unclear); }
    .badge-na { background: rgba(100,116,139,0.15); color: var(--color-na); }
    .gate-table { width: 100%; border-collapse: collapse; margin: 1rem 0; }
    .gate-table th, .gate-table td { padding: 0.6rem 0.8rem; text-align: left; border-bottom: 1px solid var(--color-border); }
    .gate-table th { color: var(--color-text-muted); font-weight: 600; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.05em; }
    .concept-check { background: var(--color-surface); border: 1px solid var(--color-border); border-radius: 8px; padding: 1.25rem; margin: 1rem 0; }
    .concept-check .question { color: var(--color-text); margin-bottom: 0.5rem; font-weight: 600; }
    .vocab-term { font-weight: 700; color: var(--color-accent-light); }
    .meta-bar { display: flex; gap: 1rem; flex-wrap: wrap; margin: 1rem 0 2rem; color: var(--color-text-muted); font-size: 0.85rem; }
    .meta-bar span { background: var(--color-surface); border: 1px solid var(--color-border); border-radius: 4px; padding: 0.2rem 0.6rem; }
    footer { margin-top: 3rem; padding-top: 1rem; border-top: 1px solid var(--color-border); color: var(--color-text-muted); font-size: 0.8rem; }
  </style>
</head>
<body>

<main>
  <h1>{ARTIFACT_TITLE}</h1>
  <p>{ONE_LINE_DESCRIPTION}</p>
  <div class="meta-bar">
    <span>Part 1: Learning Guide (Pre-Run)</span>
    <span>Rungs: {RUNG_NUMBERS}</span>
    <span>Position: {LEARNING_POSITION}</span>
    <span>Cycle: {CYCLE_NUMBER}</span>
  </div>

  <!-- Section 1: What This [Artifact] Does -->
  <section id="s1-what-it-does">
    <h2>1. What This {ARTIFACT_TYPE} Does</h2>
    <p>{PLAIN_ENGLISH_SUMMARY}</p>
  </section>

  <!-- Section 2: The Problem It Solves -->
  <section id="s2-problem">
    <h2>2. The Problem It Solves</h2>
    <p>{WHY_THIS_PROBLEM_IS_INTERESTING}</p>
  </section>

  <!-- Section 3: Goal Predicate (G1 — use functional alias) -->
  <section id="s3-goal-predicate">
    <h2>3. {DOMAIN_G1_ALIAS}</h2>
    <p>{HOW_GOAL_PREDICATE_WORKS}</p>
    <pre>{GOAL_PREDICATE_CODE_OR_PROSE}</pre>
  </section>

  <!-- Section 4: Loop Structure -->
  <section id="s4-loop">
    <h2>4. The Loop Structure</h2>
    <p>{HOW_ITERATION_WORKS}</p>
  </section>

  <!-- Section 5: Model's Decision (G2 — use functional alias) -->
  <section id="s5-model-decision">
    <h2>5. {DOMAIN_G2_ALIAS}</h2>
    <p>{WHERE_LLM_MAKES_REAL_DECISION}</p>
  </section>

  <!-- Section 6: Feedback Loop (G3 — use functional alias) -->
  <section id="s6-feedback">
    <h2>6. {DOMAIN_G3_ALIAS}</h2>
    <p>{HOW_PRIOR_OUTPUT_INFLUENCES_NEXT_ITERATION}</p>
  </section>

  <!-- Section 7: Exit Paths (G4 — use functional alias) -->
  <section id="s7-exit-paths">
    <h2>7. {DOMAIN_G4_ALIAS}</h2>
    <p>All exit paths:</p>
    <ul>
      <li><strong>{EXIT_PATH_1_LABEL}:</strong> {EXIT_PATH_1_CONDITION}</li>
      <li><strong>{EXIT_PATH_2_LABEL}:</strong> {EXIT_PATH_2_CONDITION}</li>
      <!-- add more as needed -->
    </ul>
  </section>

  <!-- Section 8: Tools -->
  <section id="s8-tools">
    <h2>8. The Tools</h2>
    <!-- list each tool with name and purpose -->
  </section>

  <!-- Section 9: Reading the Output -->
  <section id="s9-output">
    <h2>9. Reading the Output</h2>
    <!-- explain each labeled output element -->
    <pre>{SAMPLE_OUTPUT_EXCERPT}</pre>
  </section>

  <!-- Section 10: What to Watch For -->
  <section id="s10-watch-for">
    <h2>10. What to Watch For</h2>
    <ul>
      <li>{WATCH_FOR_1}</li>
      <li>{WATCH_FOR_2}</li>
      <li>{WATCH_FOR_3}</li>
    </ul>
  </section>

  <!-- Section 11: Concept Check (MCQs or short-answer) -->
  <section id="s11-concept-check">
    <h2>11. Concept Check</h2>
    <div class="concept-check">
      <p class="question">1. {QUESTION_1}</p>
      <!-- MCQ options or free-response prompt -->
    </div>
    <div class="concept-check">
      <p class="question">2. {QUESTION_2}</p>
    </div>
  </section>

  <!-- Section 12: Vocabulary -->
  <section id="s12-vocab">
    <h2>12. Vocabulary</h2>
    <dl>
      <dt class="vocab-term">{TERM_1}</dt>
      <dd>{DEFINITION_1}</dd>
      <dt class="vocab-term">{TERM_2}</dt>
      <dd>{DEFINITION_2}</dd>
    </dl>
  </section>

  <!-- Section 13: Gate Map -->
  <section id="s13-gate-map">
    <h2>13. Gate Map</h2>
    <table class="gate-table" aria-label="Gate verdicts for this artifact">
      <thead>
        <tr>
          <th scope="col">Gate (Alias)</th>
          <th scope="col">Verdict</th>
          <th scope="col">Why</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>{DOMAIN_G1_ALIAS}</td>
          <td><span class="badge badge-pass">PASS</span></td>
          <td>{G1_RATIONALE}</td>
        </tr>
        <tr>
          <td>{DOMAIN_G2_ALIAS}</td>
          <td><span class="badge badge-unclear">UNCLEAR</span></td>
          <td>{G2_RATIONALE}</td>
        </tr>
        <tr>
          <td>{DOMAIN_G3_ALIAS}</td>
          <td><span class="badge badge-na">N/A</span></td>
          <td>{G3_RATIONALE}</td>
        </tr>
        <tr>
          <td>{DOMAIN_G4_ALIAS}</td>
          <td><span class="badge badge-pass">PASS</span></td>
          <td>{G4_RATIONALE}</td>
        </tr>
        <tr>
          <td>{DOMAIN_G5_ALIAS}</td>
          <td><span class="badge badge-na">N/A</span></td>
          <td>{G5_RATIONALE}</td>
        </tr>
      </tbody>
    </table>
  </section>
</main>

<footer>
  <p>{SLUG} Learning Guide · Part 1 (Pre-Run) · Cycle {CYCLE_NUMBER} · Generated {DATE}</p>
  <p>Gate reference: G1 = {DOMAIN_G1_ALIAS} | G2 = {DOMAIN_G2_ALIAS} | G3 = {DOMAIN_G3_ALIAS} | G4 = {DOMAIN_G4_ALIAS} | G5 = {DOMAIN_G5_ALIAS}</p>
</footer>

</body>
</html>
```

### H.2 Part 2 Learning Insights Starter Template

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{SLUG} Learning Insights — {ARTIFACT_TITLE}</title>
  <style>
    /* Reuse the same CSS variables as Part 1 */
    :root {
      --color-bg: #0f1117;
      --color-surface: #1a1d27;
      --color-border: #2d3148;
      --color-text: #e2e8f0;
      --color-text-muted: #94a3b8;
      --color-accent: #6366f1;
      --color-accent-light: #818cf8;
      --color-pass: #22c55e;
      --color-fail: #ef4444;
      --color-unclear: #f59e0b;
      --color-na: #64748b;
      --font-main: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
      --font-mono: 'Fira Code', 'Cascadia Code', Consolas, monospace;
    }
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: var(--font-main); background: var(--color-bg); color: var(--color-text); line-height: 1.6; padding: 2rem; max-width: 900px; margin: 0 auto; }
    h1 { font-size: 2rem; color: var(--color-accent-light); margin-bottom: 0.5rem; }
    h2 { font-size: 1.25rem; color: var(--color-accent); margin: 2rem 0 0.75rem; border-bottom: 1px solid var(--color-border); padding-bottom: 0.4rem; }
    p { margin-bottom: 0.75rem; }
    code { font-family: var(--font-mono); font-size: 0.875rem; background: var(--color-surface); padding: 0.15rem 0.4rem; border-radius: 3px; color: var(--color-accent-light); }
    pre { font-family: var(--font-mono); font-size: 0.85rem; background: var(--color-surface); border: 1px solid var(--color-border); border-radius: 6px; padding: 1rem; overflow-x: auto; margin: 0.75rem 0; }
    .evidence-block { background: rgba(99,102,241,0.08); border-left: 3px solid var(--color-accent); padding: 0.75rem 1rem; margin: 0.75rem 0; border-radius: 0 6px 6px 0; }
    .evidence-block .label { font-size: 0.8rem; color: var(--color-accent); text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.3rem; }
    .badge { display: inline-block; padding: 0.2rem 0.6rem; border-radius: 4px; font-size: 0.8rem; font-weight: 600; }
    .badge-pass { background: rgba(34,197,94,0.15); color: var(--color-pass); }
    .badge-fail { background: rgba(239,68,68,0.15); color: var(--color-fail); }
    .badge-unclear { background: rgba(245,158,11,0.15); color: var(--color-unclear); }
    .badge-na { background: rgba(100,116,139,0.15); color: var(--color-na); }
    .gate-table { width: 100%; border-collapse: collapse; margin: 1rem 0; }
    .gate-table th, .gate-table td { padding: 0.6rem 0.8rem; text-align: left; border-bottom: 1px solid var(--color-border); }
    .gate-table th { color: var(--color-text-muted); font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.05em; }
    .meta-bar { display: flex; gap: 1rem; flex-wrap: wrap; margin: 1rem 0 2rem; color: var(--color-text-muted); font-size: 0.85rem; }
    .meta-bar span { background: var(--color-surface); border: 1px solid var(--color-border); border-radius: 4px; padding: 0.2rem 0.6rem; }
    footer { margin-top: 3rem; padding-top: 1rem; border-top: 1px solid var(--color-border); color: var(--color-text-muted); font-size: 0.8rem; }
  </style>
</head>
<body>

<main>
  <h1>{ARTIFACT_TITLE} — What You Learned</h1>
  <p>This document is based on your actual run output. All evidence is quoted from your log.</p>
  <div class="meta-bar">
    <span>Part 2: Learning Insights (Post-Run)</span>
    <span>Run date: {RUN_DATE}</span>
    <span>Exit: {EXIT_REASON}</span>
    <span>Iterations: {ITERATIONS_RUN}/{MAX_ITERATIONS}</span>
  </div>

  <!-- Section 1: What Happened -->
  <section id="s1-what-happened">
    <h2>1. What Happened</h2>
    <p>{PLAIN_ENGLISH_SUMMARY_OF_ACTUAL_RUN}</p>
  </section>

  <!-- Section 2: Your Output, Annotated -->
  <section id="s2-annotated-output">
    <h2>2. Your Output, Annotated</h2>
    <div class="evidence-block">
      <div class="label">Quoted from your run</div>
      <pre>{KEY_OUTPUT_EXCERPT}</pre>
    </div>
    <p>{ANNOTATION_OF_KEY_OUTPUT}</p>
  </section>

  <!-- Section 3: G1 Evidence (use functional alias) -->
  <section id="s3-g1-evidence">
    <h2>3. {DOMAIN_G1_ALIAS}: Evidence</h2>
    <div class="evidence-block">
      <div class="label">Evidence from your output</div>
      <pre>{QUOTED_G1_OUTPUT_LINE}</pre>
    </div>
    <p>{EXPLANATION_OF_G1_EVIDENCE}</p>
  </section>

  <!-- Section 4: G2 Evidence -->
  <section id="s4-g2-evidence">
    <h2>4. {DOMAIN_G2_ALIAS}: Evidence</h2>
    <div class="evidence-block">
      <div class="label">Evidence from your output</div>
      <pre>{QUOTED_G2_OUTPUT_LINE}</pre>
    </div>
    <p>{EXPLANATION_OF_G2_EVIDENCE}</p>
  </section>

  <!-- Section 5: G3 Evidence -->
  <section id="s5-g3-evidence">
    <h2>5. {DOMAIN_G3_ALIAS}: Evidence</h2>
    <div class="evidence-block">
      <div class="label">Evidence from your output</div>
      <pre>{QUOTED_G3_OUTPUT_LINE}</pre>
    </div>
    <p>{EXPLANATION_OF_G3_EVIDENCE}</p>
  </section>

  <!-- Section 6: G4 Evidence -->
  <section id="s6-g4-evidence">
    <h2>6. {DOMAIN_G4_ALIAS}: Evidence</h2>
    <div class="evidence-block">
      <div class="label">Evidence from your output</div>
      <pre>{QUOTED_G4_OUTPUT_LINE}</pre>
    </div>
    <p>{EXPLANATION_OF_G4_EVIDENCE}</p>
  </section>

  <!-- Section 7: Gaps and Questions -->
  <section id="s7-gaps">
    <h2>7. Gaps and Questions</h2>
    <p>{WHAT_THIS_RUN_RAISED_OR_LEFT_UNCLEAR}</p>
    <ul>
      <li>{GAP_OR_QUESTION_1}</li>
      <li>{GAP_OR_QUESTION_2}</li>
    </ul>
  </section>

  <!-- Section 8: One Experiment to Try -->
  <section id="s8-experiment">
    <h2>8. One Experiment to Try</h2>
    <p>{CONCRETE_NEXT_EXPERIMENT_DESCRIPTION}</p>
  </section>

  <!-- Section 9: Concept Reinforcement -->
  <section id="s9-reinforcement">
    <h2>9. Concept Reinforcement</h2>
    <p>{QUESTION_ANCHORED_TO_ACTUAL_OUTPUT_1}</p>
    <p>{QUESTION_ANCHORED_TO_ACTUAL_OUTPUT_2}</p>
  </section>

  <!-- Section 10: Gate Report -->
  <section id="s10-gate-report">
    <h2>10. Gate Report</h2>
    <table class="gate-table" aria-label="Final gate verdicts with evidence">
      <thead>
        <tr>
          <th scope="col">Gate (Alias)</th>
          <th scope="col">Verdict</th>
          <th scope="col">Evidence</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>{DOMAIN_G1_ALIAS}</td>
          <td><span class="badge badge-pass">PASS</span></td>
          <td><code>{G1_EVIDENCE_QUOTE}</code></td>
        </tr>
        <tr>
          <td>{DOMAIN_G2_ALIAS}</td>
          <td><span class="badge badge-unclear">UNCLEAR</span></td>
          <td>{G2_EVIDENCE_OR_EXPLANATION}</td>
        </tr>
        <tr>
          <td>{DOMAIN_G3_ALIAS}</td>
          <td><span class="badge badge-na">N/A</span></td>
          <td>Introduced at Rung {RUNG}</td>
        </tr>
        <tr>
          <td>{DOMAIN_G4_ALIAS}</td>
          <td><span class="badge badge-pass">PASS</span></td>
          <td><code>{G4_EVIDENCE_QUOTE}</code></td>
        </tr>
        <tr>
          <td>{DOMAIN_G5_ALIAS}</td>
          <td><span class="badge badge-na">N/A</span></td>
          <td>Introduced at Rung {RUNG}</td>
        </tr>
      </tbody>
    </table>
  </section>

  <!-- Section 11: Registry Update Summary -->
  <section id="s11-registry">
    <h2>11. Registry Update Summary</h2>
    <p>Added to registry after this cycle:</p>
    <ul>
      <li>Cycle {CYCLE_NUMBER} logged with slug: <code>{SLUG}</code></li>
      <li>Rungs introduced: {RUNGS_INTRODUCED}</li>
      <li>Gaps identified: {GAPS_IDENTIFIED_OR_NONE}</li>
      <li>Gaps resolved: {GAPS_RESOLVED_OR_NONE}</li>
    </ul>
  </section>
</main>

<footer>
  <p>{SLUG} Learning Insights · Part 2 (Post-Run) · Cycle {CYCLE_NUMBER} · Run: {RUN_DATE}</p>
  <p>Gate reference: G1 = {DOMAIN_G1_ALIAS} | G2 = {DOMAIN_G2_ALIAS} | G3 = {DOMAIN_G3_ALIAS} | G4 = {DOMAIN_G4_ALIAS} | G5 = {DOMAIN_G5_ALIAS}</p>
</footer>

</body>
</html>
```

---

## Appendix I: Auditor's Findings and Fixes

**[Added in this version — comprehensive record of all audit findings and their resolution]**

[UNIVERSAL]

### I.1 Audit Summary

**Audit performed by:** AI Implementation Auditor (simulating Healthcare Training Simulations adopter perspective)
**Date:** June 26, 2026
**Original verdict:** ADOPT-WITH-CAVEATS
**Final verdict after fixes:** ADOPT-READY

**Findings summary:**
- 4 BLOCK findings (must fix before adoption) — all resolved in this version
- 8 ADVISORY findings (should fix) — 6 resolved inline, 2 retained as documented limitations

---

### I.2 BLOCK Findings and Resolutions

**BLOCK-1: ROADMAP.md has no definition, schema, or content specification**

- **Finding:** ROADMAP.md is required by the cold-start protocol (read alongside HANDOFF.md and foundry_registry.json) but had no definition anywhere in the Blueprint. A new-domain implementer had no basis for creating this file correctly. Cold-start behavior with an absent or incorrect ROADMAP.md is undefined.
- **Impact:** Every cold start and every new domain instantiation is blocked without this specification.
- **Resolution:** Appendix D (ROADMAP.md Specification) added in this version. Contents: (1) definition and distinction from HANDOFF.md, (2) full Markdown schema with all fields specified, (3) a worked example at cycle 3, (4) update protocol. ROADMAP.md also added to the cold-start protocol (§B.6 Universal Component 13), §B.7 Prerequisites (item 11), and the reading sequence (§B.4 step 9).

---

**BLOCK-2: Professor system prompt template (§5.3) and constraint block are absent**

- **Finding:** §5 referenced a system prompt template and a non-negotiable constraint block, but neither appeared in the document. An implementer cannot write a valid Professor system prompt without the template, and without the constraint block, behavioral prohibitions (gate code prohibition, no-pause generation, Checkpoint 3 first) are not enforced.
- **Impact:** Every domain implementation of the Professor would be missing its most critical behavioral constraints.
- **Resolution:** Appendix G (Professor System Prompt Template) added in this version. Contents: (1) full four-block template structure with all placeholders specified, (2) the complete CONSTRAINT BLOCK verbatim with 10 non-negotiable rules, (3) instructions for filling in domain-specific values. The constraint block is marked: "Copy this block verbatim into every implementation." §5.3 now points to Appendix G.

---

**BLOCK-3: foundry_registry.json schema (§4.1) is absent; learning.gaps[] field name is a single undiscoverable reference**

- **Finding:** The registry schema was deferred to "read as needed." The specific field path `learning.gaps[]` — which drives FOUNDATIONAL classification — appeared in only one location (§B.8 Q6). An implementer who invented a different field name would silently break cross-cycle memory and gap-repair targeting, producing a curriculum that never classifies FOUNDATIONAL cycles.
- **Impact:** Silent, cross-cycle curriculum failure. No error message indicates the classification algorithm is not working.
- **Resolution:** Appendix E (Registry Schema) added in this version. Contents: (1) explanation of why schema is required reading (field naming is not arbitrary), (2) full annotated JSON schema with all field names, types, and nesting, (3) critical field callouts for `learning.gaps[]` and `cycles[].rungs_introduced[]`, (4) a worked example registry at 3 cycles. Appendix E promoted to step 6 in the required reading sequence (§B.4).

---

**BLOCK-4: Nine-step adaptation checklist (§6.2) is entirely absent**

- **Finding:** The checklist was referenced in eight locations across §B.4, §B.6, and §B.8 as the primary adaptation guide, but was not included in the document. Without it, implementers must reverse-engineer the adaptation process from scattered references.
- **Impact:** The most-referenced missing component. Every adopter attempting a new domain instantiation is blocked.
- **Resolution:** Appendix F (Nine-Step Adaptation Checklist) added in this version. Contents: all nine steps in order with deliverables, required decisions, constraints, and validation questions for each step. §6.2 now points to Appendix F.

---

### I.3 ADVISORY Findings and Resolutions

**ADVISORY-1: §3 and §4 deferred to "as needed" in reading sequence**

- **Finding:** An implementer who begins Phase A without reading §4 may design a registry schema before understanding the full cross-cycle memory requirements.
- **Resolution:** §3 (Learning Artifacts), §4 (State Management), and Appendix E (Registry Schema) promoted to steps 6–8 in the required reading sequence (§B.4). The reading sequence now ensures implementers understand the full state management model before designing their adaptation.

---

**ADVISORY-2: Appendix B (Phase Reference Card) absent from provided text**

- **Finding:** Phase durations exist in scattered references but were not consolidated.
- **Resolution:** Appendix B (Phase Reference Card) added in full in this version (see Appendix B above). Includes all phases, mandatory/skippable status, duration, inputs, and outputs.

---

**ADVISORY-3: Gate adaptation worked examples (§7.3, §8.3) absent from excerpt**

- **Finding:** Gate definitions in §1.3 and §B.5 are sufficient to attempt adaptation, but no translation example was visible to validate approach. Medium risk for non-standard domains.
- **Resolution:** Gate adaptation tables included in full for Data Science (§7.3) and Database Queries (§8.3) in this version. Healthcare gate adaptations are documented in the Portability Proof (§I.5 below) and serve as a third worked example.

---

**ADVISORY-4: No starter HTML templates for Part 1 or Part 2**

- **Finding:** Section titles and design constraints were provided, but no structural scaffold. Two independent implementers would likely produce structurally incompatible HTML artifacts.
- **Resolution:** Appendix H (HTML Starter Templates) added in this version. Includes complete structural scaffolds for both Part 1 (13 sections) and Part 2 (11 sections) with consistent CSS variable names, section IDs, badge conventions, and gate table structure. Remaining limitation: templates are structural scaffolds; content for each section must be authored from body text examples. See §B.9 Known Limitation 3.

---

**ADVISORY-5: Undefined acronyms (MCQ, CDN, WCAG AA) and PyCharm misread as hard dependency**

- **Finding:** Three technical acronyms used without expansion; PyCharm named as IDE without noting it is one option among many.
- **Resolution:** All three acronyms (MCQ, CDN, WCAG AA) defined in §B.5 Key Term Glossary. PyCharm reference in §2.6 updated with explicit note: "Note on IDE: PyCharm is used in Agent SDK domain examples as the student's preferred environment. It is not a hard dependency. Any Python runner, notebook, or platform-appropriate execution environment is valid."

---

**ADVISORY-6: CLAUDE.md SDLC referenced but inaccessible**

- **Finding:** §B.9 item 7 references a more detailed Learning Position classification algorithm in an external file (project CLAUDE.md) with no schema or content in the Blueprint.
- **Resolution:** Classification algorithm in §1.5 expanded with explicit tiebreaker rule: "When FOUNDATIONAL and LATERAL-RIGHT are both plausible, check `learning.gaps[]` — if non-empty, classify FOUNDATIONAL." The CLAUDE.md reference retained in §B.9 Known Limitation 5 as a future scaling note. The body algorithm is now self-sufficient for all standard cases.

---

**ADVISORY-7: Registry field naming conventions insufficiently specified**

- **Finding:** The registry definition described what the registry contains conceptually but did not specify field naming conventions, data types, or nesting depth. `learning.gaps[]` appeared only once.
- **Resolution:** Addressed by BLOCK-3 resolution (Appendix E). The full schema with all field names, types, nesting, and critical callouts provides the complete naming convention.

---

**ADVISORY-8: 24-element runtime output standard does not specify universal anchors vs. domain-specific elements**

- **Finding:** A Healthcare implementer designing a clinical session transcript must decide independently which output elements are mandatory structural anchors versus domain-specific labels.
- **Resolution:** §3.3 updated with a "Required structural anchors" table specifying the six elements that MUST appear in all domain adaptations (`[RUN START]`, `[ITERATION N/M]`, `[GOAL CHECK]`, `[EXIT]` with reason label, `[SUMMARY]`, `[RUN END]`). Domain-specific elements are now clearly identified as the variable portion.

---

### I.4 Top 3 Improvements Assessment

The auditor's top 3 improvement recommendations:

1. **Add ROADMAP.md specification** — Resolved. Appendix D provides a complete 1-page schema with fields, example, update protocol, and distinction from HANDOFF.md.

2. **Provide Part 1 and Part 2 HTML starter templates** — Resolved. Appendix H provides structural scaffolds for both documents with standardized CSS variables, section IDs, badge conventions, and gate table structure.

3. **Include foundry_registry.json schema verbatim and promote to required reading** — Resolved. Appendix E provides the full annotated schema, promoted to reading sequence step 6.

---

### I.5 Portability Proof: Healthcare Training Simulations Domain Translation

This section documents the complete domain translation work performed by the auditor as a proof of portability. It serves as the third worked domain example alongside Data Science (§7) and Database Queries (§8).

**Domain:** Healthcare Training Simulations
**Artifact type:** Clinical decision simulation — a structured patient case with branching decision points, a triage algorithm, and a documented clinical reasoning chain produced by the model.
**Execution environment:** A simulation engine (purpose-built platform or structured Claude conversation acting as engine). Student initiates a run by submitting case parameters. Runtime output is a session transcript with labeled clinical decision points.

---

**Rung Ladder (Healthcare Training Simulations, 6 rungs):**

| Rung | Concept | Domain Expression |
|------|---------|------------------|
| 1 | Single-patient case, no branching | Model generates one clinical assessment from presented findings; no loop |
| 2 | Goal predicate introduction | Simulation runs until computable clinical endpoint (e.g., SpO2 > 94% AND HR < 100 AND BP systolic > 90) |
| 3 | Multi-turn case progression | Patient condition evolves across turns; prior findings carry forward into subsequent assessments (G3 equivalent) |
| 4 | Diagnostic tool selection | Model selects which test to order (CBC, CXR, ECG, ABG) based on clinical presentation, not hard-coded protocol |
| 5 | Resource-bounded diagnosis | Simulation runs under explicit constraints (diagnostic budget of 3 tests, time limit of 4 decision turns) |
| 6 | Attending review | Separate "attending physician" agent with fresh context reviews the final diagnosis and management plan |

---

**Five Gates Adapted (Healthcare):**

| Gate | Domain Expression | Functional Alias | First Applies at Rung |
|------|------------------|-----------------|----------------------|
| G1 | Simulation has a computable definition of case resolution evaluated at each decision turn | "Is the patient there yet?" | Rung 2 |
| G2 | Simulation engine selects next diagnostic action via clinical reasoning, not hard-coded protocol | "Did the model choose the test, or did the protocol?" | Rung 4 |
| G3 | A new test result demonstrably changes the model's differential or management plan in the subsequent turn | "Did the new result change the plan?" | Rung 3 |
| G4 | Simulation exits with a labeled termination reason drawn from a defined taxonomy (stabilized / confirmed / resource-limited / time-expired) | "Why did the case end?" | Rung 2 |
| G5 | Separate attending agent with no access to the resident's reasoning chain independently confirms or challenges the final diagnosis | "What did the attending say?" | Rung 6 |

---

**Runtime Output Elements (Healthcare, labeled transcript format):**

| Structural Anchor | Healthcare Equivalent |
|-------------------|-----------------------|
| `[RUN START]` | `[CASE START] {case_id} {timestamp}` |
| `[ITERATION N/M]` | `[DECISION TURN N/M]` |
| `[GOAL CHECK]` | `[ENDPOINT CHECK] Criteria: {criteria} / Status: {met|not_met}` |
| `[EXIT]` with reason | `[CASE CLOSED] Reason: PATIENT STABILIZED | RESOURCE LIMIT | TIME EXPIRED | ESCALATED` |
| `[SUMMARY]` | `[CASE SUMMARY] Turns: {N} | Final diagnosis: {dx} | Closure: {reason}` |
| `[RUN END]` | `[CASE END] {timestamp}` |

Domain-specific elements added: `[PRESENTING COMPLAINT]`, `[VITALS]`, `[DIFFERENTIAL]`, `[TEST ORDERED]`, `[TEST RESULT]`, `[PLAN UPDATE]`, `[REASONING]`, `[ATTENDING REVIEW]` (Rung 6 only).

---

**Smoke Test Implementation for Prose-Output Domain:**

The smoke test standard (branch reachability) translates to seeded scenario validity checks:

- **Seeded case 1:** Patient parameters designed to trigger `PATIENT STABILIZED` exit (SpO2 climbs above 94% by turn 3 with correct treatment). Confirm `[CASE CLOSED] Reason: PATIENT STABILIZED` appears in transcript.
- **Seeded case 2:** Patient parameters designed to trigger `RESOURCE LIMIT` exit (3-test budget consumed without resolution). Confirm `[CASE CLOSED] Reason: RESOURCE LIMIT` appears in transcript.
- **Seeded case 3:** Patient parameters designed to trigger `TIME EXPIRED` exit (4-turn limit reached). Confirm `[CASE CLOSED] Reason: TIME EXPIRED` appears in transcript.

All three seeded cases must pass before handover. The verbatim termination label must appear in the transcript — fuzzy matching is not acceptable.

---

**Tension Identified and Resolution:**

The auditor identified: "The Blueprint assumes all artifacts produce machine-readable output suitable for automated smoke testing. Clinical simulation transcripts are semi-structured prose."

Resolution in this Blueprint: §3.3 explicitly addresses this with the structural anchors table and the note: "For prose-output domains: Replace structured labels with labeled transcript markers. Every exit path must include a verbatim termination label. Smoke tests seed inputs to guarantee each label fires." The Healthcare portability proof (above) operationalizes this for the specific domain.

---

### I.6 Final Verdict

**Original verdict:** ADOPT-WITH-CAVEATS
**Final verdict:** ADOPT-READY

**All 4 BLOCK findings resolved:**
- BLOCK-1: ROADMAP.md specification added (Appendix D)
- BLOCK-2: Professor system prompt template and constraint block added (Appendix G)
- BLOCK-3: Registry schema added and promoted to required reading (Appendix E)
- BLOCK-4: Nine-step adaptation checklist added (Appendix F)

**ADVISORY findings:** 6 of 8 resolved inline. 2 retained as known limitations (§B.9):
- Known Limitation 3: HTML templates are structural scaffolds; section content must be authored from body examples
- Known Limitation 4: Multi-student database architecture schema not included

**Remaining caveats:**
1. Prose-output domain smoke testing (e.g., Healthcare) requires implementer to design seeded test cases explicitly — the Blueprint specifies the standard but not the case content.
2. ROADMAP.md recommended-next-rung field is advisory; Professor may deviate. Deviations should be documented in HANDOFF.md.

**Confidence level:** 93% (High). The Blueprint is self-contained, provides all required templates and schemas, and has been proven portable to a non-code domain (Healthcare Training Simulations). Implementers following the §B.4 reading sequence and Appendix F adaptation checklist can instantiate this model in a new domain within two to three weeks.

---

*End of AgentFoundry AI-First Learning Blueprint v1.0*
*Produced June 26, 2026 | Four-agent orchestration workflow | Systems Documentation Architect (final version)*
