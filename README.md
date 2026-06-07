<div align="center">

# 🏭 Agent Foundry

[![PRD Version][prd-shield]][prd-link]
[![Python][python-shield]][python-link]
[![Platform][platform-shield]][platform-link]
[![Status][status-shield]][status-link]

_Learn agents by building them — one daily-life idea per session, one runnable Python agent per cycle._

**Agent Foundry is a personal learning system that turns brainstormed ideas into fully annotated, runnable AI agents. Claude Desktop generates the code; PyCharm is where you read and run it. No separate application to install. No API keys. The code is the curriculum.**

</div>

<details>
<summary><kbd>Table of Contents</kbd></summary>

- [What It Is](#-what-it-is)
- [How One Cycle Works](#-how-one-cycle-works)
- [SDK Concept Ladder](#-sdk-concept-ladder)
- [What Each Cycle Produces](#-what-each-cycle-produces)
- [Agency Gates](#-agency-gates-g1g5)
- [Prerequisites](#-prerequisites)
- [Getting Started](#-getting-started)
- [Project Structure](#-project-structure)
- [After Five Cycles](#-after-five-cycles)
- [Honest Caveats](#-honest-caveats)

</details>

---

## 🎯 What It Is

Most learning about AI agents is theoretical — articles, slides, and explanations that describe what agents *should* do. Agent Foundry forces a different approach: you build one, watch it run, and explain from a specific code line or output line exactly why it behaves the way it does.

Every session (one "cycle") follows the same arc:

```
Brainstorm → Lock → Generate 8 files → Read guide → Run in PyCharm → Professor Q&A → Insights
```

Each new agent introduces at least one Claude Agent SDK concept the previous one did not. By cycle 5, you have built five agents across eight SDK rungs and can apply the same acceptance framework to any agent you encounter in the wild.

**The key architectural decision:** Claude Desktop is the Foundry. There is no application to install. All brainstorming, gating, code generation, and QA happen in this chat. PyCharm is exclusively where you read and run generated agents.

<div align="right">

[back to top](#-agent-foundry)

</div>

---

## 🔄 How One Cycle Works

<details>
<summary>Expand to see all eight phases</summary>

### Phase 0 — Session Warm-Up *(mandatory from cycle 2)*
The Professor briefs you on what you built last cycle: report card, complexity arc, active gaps, gotchas you've caught, and what the next SDK rung will unlock. Then 2–3 recall questions anchored to your actual runtime output. No scoring. ≤ 8 minutes. Skip with `skip warm-up`.

### Phase A — Brainstorm
Claude reads your learning state and proposes 3–4 candidates, each with:
- A **Learning Position label** — `FORWARD` (new SDK rung), `FOUNDATIONAL` (targets your weakest gap), `LATERAL-RIGHT` (new domain), `DIAGNOSTIC` (deliberately fails a gate — offered every 2–3 cycles)
- A **G1–G5 Agency Gate verdict**
- A **9-trait scorecard**

You can also shortcut the brainstorm entirely:
- `Others: I want an agent that does X` — Claude gates-checks your idea directly
- `Others: C:\path\to\spec.md` — Claude reads your spec file and runs the gate check

### Phase B — Lock
Type `lock <candidate name>`. Zero files are written before this. Claude shows a one-page mini-spec (goal predicate, tools, loop, termination, SDK rungs) and asks for a second confirmation.

### Phase C — Generate
Claude writes **8 mandated files** into `agents/<slug>/`, runs the smoke test (LLM mocked) in its sandbox, and repairs failures up to 3 times — narrating each fix. Hands over only on green.

### Phase C (ordered) — Read the Learning Guide First
The Part 1 HTML guide is delivered **before** `main.py`. It explains why this agent is an agent, maps each agentic trait to a function, shows annotated expected output, and includes a Python Reading Primer. Read it before opening PyCharm.

### Phase F — Professor Session *(skippable, pre-run)*
A ~10-minute Socratic conversation. The Professor asks 2–3 questions anchored to the code you just read. Probes target mechanism, not recall. One counter-question on a wrong answer, then a targeted explanation pointing to the exact code line.

### Your Run
Open PyCharm. Right-click `main.py` → Run. The agent prints 24+ labeled output lines — every SDK call boundary, every model decision, every goal predicate evaluation. The output is saved automatically to `<slug>_run_output.log`.

### Phase F2 — Post-Run Professor Session *(skippable, triggered by "I ran it")*
The more useful of the two Professor sessions. Every probe starts from a specific line in your runtime log — not the code. You explain real evidence, not recalled definitions.

</details>

<div align="right">

[back to top](#-agent-foundry)

</div>

---

## 🪜 SDK Concept Ladder

Each cycle introduces at least one new rung. Rungs are tracked in the registry so the brainstorm always builds forward.

| Rung | SDK Concept | Enables |
|------|-------------|---------|
| **1** | `query()` + message anatomy (`SystemMessage`, `AssistantMessage`, `ResultMessage`, `usage`) | Basic agent loop; watching the LLM boundary |
| **2** | Goal predicate + agent loop + circuit breaker | G1/G3/G4 in code; principled termination |
| **3** | `ClaudeSDKClient` multi-turn + `session_id` capture/resume | Persistent context across SDK calls |
| **4** | Custom tools (`@tool`) — model-owned tool selection | G2 fully demonstrable; `[MODEL DECISION]` acquires meaning |
| **5** | `allowed_tools` / `permission_mode` | Dialling autonomy precisely; four documented modes |
| **6** | Hooks: `PreToolUse` guard, `PostToolUse` audit + JSONL span trace | Intercept and audit every tool call |
| **7** | Independent verifier — separate critic call, fresh context | G5 satisfied; trust as an architectural concern |
| **8** | Subagents + context compaction | Multiple agents, bounded context, shared goal |

<div align="right">

[back to top](#-agent-foundry)

</div>

---

## 📦 What Each Cycle Produces

Eight files are generated into `agents/<use-case-slug>/`. Nothing is left partial.

| File | Purpose | When |
|------|---------|------|
| `prompt.md` | Blueprint — self-contained spec; a cold session can regenerate the agent from this alone | Before any Python |
| `<slug>_learning-guide.html` | **Part 1** — pre-run reading artifact; 13 sections, MCQs, SVG loop diagram, Python Reading Primer | Before `main.py` |
| `main.py` | Runnable agent — 24-element annotated runtime output | After Part 1 confirmed open |
| `agent.py` | Agent loop / SDK wiring (only if `main.py` > ~150 lines) | With `main.py` |
| `smoke_test.py` | QA tests with mocked LLM — must exit 0 before handover | With `main.py` |
| `requirements.txt` | Pinned, verified-current packages | With `main.py` |
| `README.md` | PyCharm run instructions only (mechanics, no concepts) | With `main.py` |
| `<slug>_run_output.log` | Auto-saved runtime log via `tee_to_log()` — input for Part 2 | On first PyCharm run |
| `<slug>_learning-insights.html` | **Part 2** — post-run reinforcement; 11 sections; agency proved from quoted output lines | After first run |

<div align="right">

[back to top](#-agent-foundry)

</div>

---

## ✅ Agency Gates G1–G5

Every generated agent is accepted or rejected against five formal gates. **G1–G3 are mandatory** — if any fail, the artifact is labeled a workflow and a minimal fix is proposed.

| Gate | Name | Pass Criterion |
|------|------|----------------|
| **G1** | Goal is a predicate | `goal_met(state) -> bool` called in code; verdict computed, not narrated |
| **G2** | Model owns a real decision | At least one branch chosen by the model at run-time, visible in `[MODEL DECISION]` output |
| **G3** | Closed observe→reason→act loop | Agent reads a tool result and a *subsequent* action demonstrably differs — proved by `[LOOP FEEDBACK]` line |
| **G4** | Principled termination | Goal-predicate exit **and** hard cap/budget/timeout; both paths reachable |
| **G5** | Verification is independent | Pass/fail from a deterministic predicate or separate critic call with fresh context *(introduced at rung 7)* |

The gates are the same framework you apply to evaluate any agent you encounter outside this project.

<div align="right">

[back to top](#-agent-foundry)

</div>

---

## 🔧 Prerequisites

- **Claude Desktop** with a [Claude Max plan](https://claude.ai) subscription (no API key — auth is via Claude Code CLI)
- **PyCharm** (Community or Professional) on Windows
- **Python 3.12+**
- **Claude Code CLI** installed and logged in: `claude auth status`

```bash
# Verify your setup before starting cycle 1
claude --version
claude auth status
python --version   # must be 3.12+
```

> [!IMPORTANT]
> This project **never** reads, sets, or asks for `ANTHROPIC_API_KEY`. All LLM calls go through `claude-agent-sdk` → Claude Code CLI → your Max plan subscription. If the key is set in your environment, the generated agent will warn and strip it from the child process — it will never use it.

<div align="right">

[back to top](#-agent-foundry)

</div>

---

## 🚀 Getting Started

**Step 1 — Clone and open in Claude Desktop**

```bash
git clone https://github.com/ramnathmur/agent-foundry.git
```

Open the cloned folder as a project in Claude Desktop. Claude reads the session state files automatically.

**Step 2 — Start the brainstorm**

Say `begin the brainstorm` or `new agent`. Claude reads `HANDOFF.md`, `INSIGHTS.md`, and the registry before responding. On cycle 1 you go straight to brainstorm; from cycle 2, the Professor warm-up fires first.

**Step 3 — Read Part 1, then run in PyCharm**

After Claude hands over the files, double-click `<slug>_learning-guide.html` and read it before opening PyCharm. Then right-click `main.py` → **Run 'main'**. Come back to Claude and say `I ran it`.

> [!NOTE]
> The first run prints 24+ labeled output lines before the agent's actual result appears. This is intentional — each line is a teaching element mapped to a section in the learning guide. Part 1 shows you what to look for.

<div align="right">

[back to top](#-agent-foundry)

</div>

---

## 📁 Project Structure

```
agent-foundry/
├── agents/                          # All generated agents (one folder per cycle)
│   └── <use-case-slug>/
│       ├── prompt.md
│       ├── main.py
│       ├── smoke_test.py
│       ├── requirements.txt
│       ├── README.md
│       ├── <slug>_learning-guide.html
│       ├── <slug>_run_output.log
│       └── <slug>_learning-insights.html
├── reference/
│   ├── agent_traits_chef_guide_v2.html      # 9-trait, 3-tier agentic framework
│   └── Master-Guide-to-Create-Learning-Applications_v3.md
├── CLAUDE.md                        # Operating guide for Claude (session instructions)
├── PRD.md                           # Governing product spec (v9) — PRD wins on conflicts
├── AGENT_LEARNING_AND_AGENCY_GATES.md  # Binding acceptance annex (G1–G5 definitions)
├── HANDOFF.md                       # Session continuity — rewritten every cycle
├── INSIGHTS.md                      # Learning synthesis — regenerated every cycle
├── ROADMAP.md                       # One-line index of all agents built
├── foundry_registry.json            # Structured learning record + cross-cycle state
├── PROJECT.md                       # Machine-readable manifest for AI/tool access
└── AgentFoundry_Project-Overview_v1.html  # Visual project overview (self-contained HTML)
```

<div align="right">

[back to top](#-agent-foundry)

</div>

---

## 📈 After Five Cycles

| After cycle | New SDK rungs | What you can do |
|-------------|---------------|-----------------|
| 1 | 1–2 | Explain the O→R→A loop from a runtime output line; describe what happens between `[SDK →]` and `[← SDK]` |
| 2 | 3 | Contrast stateless `query()` calls vs. persistent session context; explain why `session_id` matters |
| 3 | 4–5 | Point to a `[MODEL DECISION]` line and explain why Python could not have predicted that choice |
| 4 | 6–7 | Design a hook that intercepts tool calls; explain why G5 requires fresh context |
| 5 | 8 | Describe subagent context boundaries; design a multi-agent system from requirements |

By cycle 5 you can read any Python agent and identify — from the code — which Agency Gates it satisfies and why, or why it is actually a workflow.

<div align="right">

[back to top](#-agent-foundry)

</div>

---

## ⚠️ Honest Caveats

- **Not a Python course.** You read code, not write it. The learning guide includes a 5-concept Python Reading Primer. To modify generated agents, you will need Python fundamentals from another source.
- **Not a product for others.** This is designed for one student (Ram), one machine, one learning style. If you adapt it, you are on your own.
- **Claude Max plan required.** No API key option. The agents authenticate via Claude Code CLI and your subscription.
- **Windows + PyCharm only (tested).** The agents are standard `asyncio` Python and would likely work on macOS, but this is not part of the spec.
- **The runtime output is intentionally verbose.** 24 labeled lines per iteration is a teaching instrument, not production logging. Agents built for real use would log differently.
- **Simulation ≠ running.** The smoke test mocks the LLM. The only way to see real model decisions, real `[LOOP FEEDBACK]` deltas, and real goal predicate evaluations is to run `main.py` in PyCharm.

<div align="right">

[back to top](#-agent-foundry)

</div>

---

<div align="center">

**PRD v9 · Python 3.12+ · Claude Max plan · Windows + PyCharm**

Built with [Claude Code](https://claude.ai/code) · 2026

</div>

<!-- Link reference definitions -->
[prd-shield]: https://img.shields.io/badge/PRD-v9-blue?style=flat-square
[prd-link]: ./PRD.md
[python-shield]: https://img.shields.io/badge/Python-3.12%2B-3776ab?style=flat-square&logo=python&logoColor=white
[python-link]: https://www.python.org/downloads/
[platform-shield]: https://img.shields.io/badge/Platform-Windows%20%2B%20PyCharm-0078d4?style=flat-square&logo=windows&logoColor=white
[platform-link]: https://www.jetbrains.com/pycharm/
[status-shield]: https://img.shields.io/badge/Status-Active%20Development-22c55e?style=flat-square
[status-link]: ./ROADMAP.md
