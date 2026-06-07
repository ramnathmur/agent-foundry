# MacBook Pro Purchase Research Agent — Master Prompt
> Take this entire file to Claude Code Desktop and paste it as your first message.

---

## ROLE

You are a senior AI engineer and pedagogy-focused Python developer. You build clean, well-architected agentic systems using the Anthropic SDK natively. Every code block you write is a teaching artefact — its purpose is to make the reader understand what an agent is doing and why, not just that it works.

---

## CONTEXT

This prompt is for Claude Code Desktop, running inside JetBrains PyCharm. The target is a fully functional, runnable Python implementation of a MacBook Pro purchase research agent — a real-world agentic use case where an AI agent autonomously researches and recommends the best MacBook Pro 16-inch M4 variant for a user's workload.

The agent demonstrates all 9 traits of a real AI agent as defined in the Chef's Kitchen framework:

| # | Trait | What it means in this agent |
|---|-------|----------------------------|
| 1 | **Goal-Directedness** | Anchors every action to the purchase decision goal |
| 2 | **Perception** | Reads web search results, price data, spec sheets |
| 3 | **Planning** | Decomposes the research goal into a sequenced sub-task plan |
| 4 | **Memory** | Accumulates findings across steps and retrieves them for synthesis |
| 5 | **Tool Selection** | Chooses between search, analysis, and synthesis tools per sub-task |
| 6 | **Sequential Action-Taking** | Each step's output feeds the next step's input |
| 7 | **Autonomy** | Self-directs all intermediate steps after the initial goal is set |
| 8 | **Observe–Reason–Act loop** | Detects conflicts mid-research and replans |
| 9 | **Termination Criterion** | Stops when a confident recommendation can be produced |

The implementation uses **only the Anthropic Python SDK** (`anthropic` package). No LangChain, no LangGraph, no AutoGPT. Native `tool_use` via the SDK's `messages.create()` with `tools=[]`. The agent runs as a CLI Python script in PyCharm, printing rich console output that makes the agent's internal state visible at every step.

This is a **learning experience**. The person running this should be able to watch the agent think, plan, use tools, hit a complication, replan, and terminate — all in a single terminal run.

---

## GOAL

Generate a single, complete, runnable Python script implementing the MacBook Pro purchase research agent described above. The script must run without modification in PyCharm using a standard Python virtual environment with only the `anthropic` package installed. Every code block must be annotated with structured comments explaining its purpose, what agentic trait it demonstrates, what it achieves, and what its dependencies are. The code must pass a self-verification loop before being delivered.

---

## CONSTRAINTS

### Architecture

- Use only the `anthropic` Python SDK (`pip install anthropic`). No other AI frameworks.
- Model: `claude-sonnet-4-20250514` throughout. Never claude-opus or claude-haiku.
- Tool use pattern: define tools as JSON schema dicts, pass to `messages.create(tools=[...])`, handle `tool_use` blocks in the response loop.
- Agent loop: implement as an explicit `while` loop with a termination condition — not recursion.
- Memory: implement as a Python dict called `agent_memory` that accumulates findings across steps. Show retrieval events explicitly in console output.
- Plan: implement as a Python list of dicts with keys: `id`, `description`, `status` (`pending` / `active` / `done` / `revised`). Render the plan to console at each step.

### PyCharm / Runtime

- The script must run with: `python macbook_agent.py` from the PyCharm terminal.
- All imports must be from the standard library or the `anthropic` package only.
- API key must be read from environment variable `ANTHROPIC_API_KEY` using `os.environ.get()`. Include a startup check that prints a clear error and exits if the key is missing — never hard-code the key.
- No `async`/`await`. Synchronous SDK calls only (`client.messages.create`, not `client.messages.stream`).
- No external HTTP calls outside the Anthropic SDK. Web search results must be **simulated via mock tool responses** that contain realistic data (real model names, real Indian pricing, real benchmark numbers, real thermal findings). The simulation must be rich enough that the agent's reasoning is genuine, not trivially correct.
- Use `print()` for all console output. No `logging` module, no `rich` library, no `colorama` — plain print with Unicode box-drawing characters and emoji for visual structure.
- Include a `if __name__ == "__main__":` guard.

### Comment Format

Every major code block must carry a structured comment header in this **exact format**:

```python
# ═══════════════════════════════════════════
# PURPOSE: [one sentence — what this block does]
# AGENTIC TRAIT: [which of the 9 traits this code demonstrates]
# ACHIEVES: [what the agent is able to do because of this block]
# DEPENDENCIES: [what this block requires to be already set up]
# ═══════════════════════════════════════════
```

Apply this header to:
- Imports section
- API client initialisation
- Memory initialisation
- Plan initialisation
- Each tool definition
- The main agent loop
- Each loop phase (plan step, tool call, observe, reason, act, termination check)
- The final report renderer

### Pedagogical Requirements

- Print the agent's current **plan** (with status icons) at the start of each loop iteration.
- Print **working memory contents** (key: value) whenever a new entry is added or an existing entry is retrieved.
- Print a clearly labelled `OBSERVE / REASON / ACT` sequence at the loop step where conflicting data is detected and resolved.
- Print a `PLAN REVISED` block when a new step is inserted mid-run, showing the old plan struck through (use a visual equivalent, e.g. `[REMOVED]`) and the new step added.
- Print a `TERMINATION CHECK` block at the end of each loop iteration showing the agent's confidence score and whether the stopping condition is met.
- At script end, print a structured `FINAL RECOMMENDATION` block with: best option, price, key trade-offs, buy-now rationale, and a summary of agent statistics (steps run, tool calls made, memory entries, complications handled).

### Complications to Inject

**Complication 1 — Step 5: Thermal conflict**
- One mock source says no throttling observed
- A second source reports 15–20% throttle under sustained AI inference
- The agent must: detect the conflict, log it as `⚠ CONFLICT DETECTED`, insert a new plan step, resolve it via a targeted follow-up tool call, and update memory with the resolved finding

**Complication 2 — Step 9: Price drop**
- M4 Pro price drops from ₹2,49,900 to ₹2,29,900 mid-run
- The agent must: observe this as `⚠ PRICE DROP DETECTED`, reason that it changes the value calculus, and update the recommendation accordingly

---

## QUALITY ASSURANCE — SELF-VERIFICATION LOOP (mandatory before delivering code)

Before outputting the final script, **internally simulate running the script** by tracing through each check below. If any check fails, fix the issue before outputting. Report the result as a comment block at the top of the script.

| # | Check | What to verify |
|---|-------|---------------|
| 1 | **Import resolution** | Every import exists in stdlib or `anthropic` package |
| 2 | **API call shape** | Every `messages.create()` has valid required fields: `model`, `max_tokens`, `messages`, and `tools` if tool_use is expected |
| 3 | **Tool response loop** | Code handles BOTH response types: `text` stop and `tool_use` stop_reason. Unhandled `tool_use` blocks are the most common PyCharm failure mode |
| 4 | **Memory dict access** | No `KeyError` is possible — all `agent_memory` reads use `.get()` with a default |
| 5 | **Plan list mutations** | Inserting a new step mid-loop does not break the loop index — use index-safe iteration |
| 6 | **Environment variable** | `ANTHROPIC_API_KEY` check runs before any SDK call |
| 7 | **`__main__` guard** | Exists and the script does not execute on import |

Report format at top of script:
```python
# QA SELF-VERIFICATION: PASSED
# Checks: imports ✓ | API shape ✓ | tool loop ✓ | memory safety ✓ | plan mutation ✓ | env var ✓ | main guard ✓
```

---

## OUTPUT FORMAT

Deliver three files:

### 1. `macbook_agent.py`
Complete, self-contained Python script. No placeholders, no TODOs, no "implement this yourself" stubs. Every function fully implemented.

The console output when run must follow this sequence visibly:
```
[AGENT BOOT]
[GOAL SET]
[PLAN GENERATED]
  → loop of:
  [STEP N]
  [TOOL CALL]
  [OBSERVE]
  [REASON]
  [ACT]
  [MEMORY UPDATE]
  [TERMINATION CHECK]
  → at step 5: [⚠ CONFLICT DETECTED] → [PLAN REVISED]
  → at step 9: [⚠ PRICE DROP DETECTED]
[FINAL RECOMMENDATION]
```

### 2. `requirements.txt`
```
anthropic
```

### 3. `SETUP.md`
10 lines max. Exact PyCharm setup steps:
1. Create a virtual environment
2. Install requirements
3. Set `ANTHROPIC_API_KEY` in PyCharm run configuration environment variables
4. Run the script

---

## EXAMPLES

### Correct comment block format

```python
# ═══════════════════════════════════════════
# PURPOSE: Initialise the agent's working memory as an empty dict
# AGENTIC TRAIT: Memory — the agent retains findings across steps rather than restarting from scratch
# ACHIEVES: Allows step 7 to retrieve findings from step 2 without re-running tool calls
# DEPENDENCIES: Must be initialised before the agent loop starts; referenced by all tool handlers
# ═══════════════════════════════════════════
agent_memory = {}
```

### Correct tool_use response handling (the pattern that most often fails in PyCharm)

```python
for block in response.content:
    if block.type == "tool_use":
        tool_result = dispatch_tool(block.name, block.input)
        # append tool_result to messages and continue loop
    elif block.type == "text":
        # handle final text response
        pass
```

---

## TONE

Engineering precision. No padding. Comments teach — they do not narrate. Assume the reader is a senior consultant learning to build agents for the first time: technically literate, impatient with vagueness, wants to understand the **why** behind every design decision. Every `print()` statement is a learning moment, not a log line.
