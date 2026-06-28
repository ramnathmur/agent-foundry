# Recipe Companion Agent — Blueprint (prompt.md)
# Cycle 3 · Rung 4 · FORWARD
# Cold-session contract: a Claude session with only this file + CLAUDE.md can regenerate all 7 agent files.

---

## §1 — Candidate Selection Rationale

| | |
|---|---|
| **Agent name** | Recipe Companion |
| **Slug** | `recipe-companion` |
| **Domain** | health-habits (food/cooking) |
| **Locked** | 2026-06-08, Cycle 3 |
| **Learning Position** | FORWARD — introduces rung 4 (`@tool` decorator + `create_sdk_mcp_server`); closes a domain-coverage gap (first health-habits agent) |

### Gate verdicts

| Gate | Verdict | One-line evidence |
|------|---------|-------------------|
| G1 — Goal predicate | PASS | `session_complete(state) -> bool` — True when recipe looked up AND ingredients checked AND shopping list updated AND first timer set |
| G2 — Model decision | PASS (deepened) | Model picks which tools to call, in what order, and how many — chained inside a single response; not constrained to one tool per turn |
| G3 — Loop feedback | PASS | Two layers carry forward (within-session via `ClaudeSDKClient`, across-session via JSON ledgers); a NEW third dimension fires within a single turn (each tool result shapes the next tool call inside the same model response) |
| G4 — Termination | PASS | Four exit paths: predicate-satisfied, model-done, user-stop, cap (max 20 tool calls total + max 8 model turns) |
| G5 — Verifier | N/A | rung 4; independent critic first appears at rung 7 |

### 9-trait scorecard

| Tier | Trait | Present | Evidence |
|------|-------|---------|----------|
| Core | Goal-directedness | ✓ | `session_complete()` + `preflight()` |
| Core | Autonomy | ✓✓ | Model picks chains of tool calls within a turn — strongest autonomy display yet |
| Core | Observe–reason–act | ✓✓ | Within-turn (each tool result shapes next call) + across-session (pantry/favorites shape first turn) |
| Essential | Perception | ✓ | `check_pantry()` and `lookup_recipe()` are real SDK-routed perceptions, not Python dispatches |
| Essential | Planning | ✓ | Recipe steps are explicit plan; live progress board per turn |
| Essential | Memory | ✓✓ | THREE LAYERS — session (rung 3 carried), app (JSON ledgers on disk), within-turn chain (NEW visibility) |
| Essential | Tool selection | ✓✓ | NEW — model selects tools via the SDK's native tool-call mechanism, not JSON-dispatch shim |
| Enhancing | Sequential action | ✓ | Tool calls counted per turn AND across turns; cap on both |
| Enhancing | Termination criterion | ✓ | Four exit paths; all tested |

---

## §2 — SDK Rung Introduced

### Rung 4 — Custom tools via `@tool` + `create_sdk_mcp_server`

The SDK now knows about your tools as first-class objects. The model can call them inline as part of its conversation; the SDK runs each tool and feeds the result back into the SAME model turn — no Python parse-and-dispatch shim in between.

**Key API (verified against `/anthropics/claude-agent-sdk-python`):**

```python
from claude_agent_sdk import tool, create_sdk_mcp_server, ClaudeAgentOptions, ClaudeSDKClient

@tool("check_pantry", "Check whether an ingredient is in the pantry", {"ingredient": str})
async def check_pantry_tool(args: dict) -> dict:
    has_it = ingredient_in_pantry(args["ingredient"])
    return {"content": [{"type": "text", "text": "yes" if has_it else "no"}]}

# Register all tools under one "server" (a logical grouping)
kitchen_server = create_sdk_mcp_server(
    name="kitchen",
    version="1.0.0",
    tools=[lookup_recipe_tool, check_pantry_tool, add_to_shopping_list_tool,
           set_timer_tool, note_favorite_tool],
)

# Wire the server into the client; allowed_tools must list each tool by its
# MCP-qualified name: mcp__<server_key>__<tool_name>
options = ClaudeAgentOptions(
    system_prompt="...",
    model="claude-opus-4-8",
    mcp_servers={"kitchen": kitchen_server},
    allowed_tools=[
        "mcp__kitchen__lookup_recipe",
        "mcp__kitchen__check_pantry",
        "mcp__kitchen__add_to_shopping_list",
        "mcp__kitchen__set_timer",
        "mcp__kitchen__note_favorite",
    ],
    permission_mode="bypassPermissions",
    env=child_env,
)

async with ClaudeSDKClient(options=options) as client:
    await client.query("Help me cook spaghetti carbonara")
    async for msg in client.receive_response():
        ...  # tool calls fire INSIDE here — multiple per response possible
```

**Three things that did NOT exist at rung 3:**

1. **`@tool` decorator** — turns an async Python function into a registered SDK tool with a typed schema the model can introspect.
2. **`create_sdk_mcp_server`** — bundles tools into a server the SDK can wire into the client.
3. **Multiple tool calls per response** — the model can call tool A, see the result, call tool B, see that, call tool C, all inside one `receive_response()` cycle. Your code sees one turn; the SDK sees N tool calls.

### Comparison to Cycle 2

| Aspect | Cycle 2 (JSON-dispatch — rung 3) | Cycle 3 (native tools — rung 4) |
|---|---|---|
| Who knows about the tools | Only your Python | The SDK (schema-aware) + the model |
| Where tool calls happen | After model returns; your Python parses JSON and dispatches | Inside `receive_response()`; SDK routes them automatically |
| Tool calls per model turn | One (or zero) | One to many (limited only by the model's reasoning + your cap) |
| Tool failures | Python catches; formats as next user prompt | First-class events the model sees mid-turn and can react to |
| Code shape | Big `parse_model_response()` + `dispatch_tool()` block | `@tool`-decorated async functions + a one-line server registration |

---

## §3 — Goal Predicate

```python
def session_complete(state: dict) -> bool:
    """GATE[G1]: True when recipe end-to-end done OR user stopped OR cap reached."""
    if state.get("user_stopped"):
        return True
    if state.get("model_done"):
        return True
    if (state.get("recipe_looked_up")
        and state.get("all_ingredients_checked")
        and state.get("shopping_list_updated")
        and state.get("first_timer_set")):
        return True
    return False
```

**Module-level constants:**
```python
MAX_TURNS: int = 8                  # GATE[G4]: hard cap on model turns
MAX_TOOL_CALLS_TOTAL: int = 20      # GATE[G4]: hard cap on total tool invocations
LEDGER_PANTRY: str = "pantry.json"
LEDGER_SHOPPING: str = "shopping_list.json"
LEDGER_FAVORITES: str = "favorites.json"
LOG_FILE: str = "recipe-companion_run_output.log"
USER_STOP_SENTINELS: set[str] = {"stop", "quit", "done", "enough", "exit"}
AGENT_VERSION: str = "v1"
MODEL_ID: str = "claude-opus-4-8"
```

---

## §4 — Tools (5, registered via `@tool`)

| Tool | Schema | Returns | What it does |
|---|---|---|---|
| `lookup_recipe` | `{"name": str}` | recipe dict as text | Returns `{name, ingredients[], steps[]}` from a static demo DB |
| `check_pantry` | `{"ingredient": str}` | `"yes"` / `"no"` | Reads `pantry.json`, returns whether ingredient is present |
| `add_to_shopping_list` | `{"item": str}` | confirmation text | Appends to `shopping_list.json` (deduplicated; atomic write) |
| `set_timer` | `{"minutes": int, "label": str}` | confirmation text | Mocks scheduling a timer; prints + logs for the demo |
| `note_favorite` | `{"recipe_name": str}` | confirmation text | Appends to `favorites.json` (deduplicated; atomic write) |

All five tools are async; all return the SDK-required `{"content": [{"type": "text", "text": "..."}]}` shape. All disk writes are atomic (temp file + rename).

---

## §5 — Memory Design (the pedagogical centerpiece — THREE layers)

### Layer 1 — Within-session (rung 3, carried)
`ClaudeSDKClient` holds the conversation across turns. Model remembers what tools it called in earlier turns.

### Layer 2 — Across-session (app, persistent on disk)
Three small JSON ledgers, each managed atomically:
- `pantry.json` — current pantry inventory (list of ingredient names)
- `shopping_list.json` — items the user needs to buy
- `favorites.json` — recipes the model has noted as user favorites

### Layer 3 — Within-turn chain (NEW — rung 4 visibility)
When the model fires multiple tool calls inside a single `receive_response()` cycle, a `[TOOL CHAIN] N tool calls in this turn` line surfaces the count. This is the *visible* proof that the model is orchestrating tool sequences itself, not your Python.

**The rung-4 demo moment:**
- User says: "make spaghetti carbonara"
- Model emits ONE response containing: `lookup_recipe → check_pantry(spaghetti) → check_pantry(eggs) → check_pantry(pancetta) → check_pantry(parmesan) → check_pantry(black pepper) → check_pantry(salt) → add_to_shopping_list(pancetta) → "Here's what I found..."`
- Runtime shows: `[TOOL CHAIN] 8 tool calls in this turn`
- Your Python sees ONE `[SDK →] / [← SDK]` bracket pair around the whole thing.

---

## §6 — Termination — four exit paths

| Path | Condition | Exit print | Gate annotation |
|------|-----------|------------|-----------------|
| Predicate satisfied | recipe done + ingredients checked + shopping list + timer set | `🏁 GOAL MET — recipe session complete` | `# GATE[G4]: predicate-satisfied exit` |
| Model declares done | model returns done marker in final text | `🏁 GOAL MET — model assessed session complete` | `# GATE[G4]: model-done exit` |
| User stop | user types a sentinel | `🏁 USER STOPPED — exiting at user request` | `# GATE[G4]: user-stop exit` |
| Cap reached | turns >= MAX_TURNS OR total tool calls >= MAX_TOOL_CALLS_TOTAL | `🏁 EXIT: cap reached — N turns / M tool calls` | `# GATE[G4]: hard-cap exit` |

All four paths must be exercised in `smoke_test.py`.

---

## §7 — Complications

1. **Empty pantry on first run** — `pantry.json` should ship seeded with 8–10 common items so the demo isn't pathologically empty; if the user has never run the agent before, the seed prevents a "everything is missing" first run.
2. **Model wraps tool args in surrounding prose** — handled by the SDK natively at rung 4 (vs. Cycle 2 where Python had to parse JSON envelopes). No special handling needed in our code.
3. **Tool error during chain** — if `check_pantry` raises, the SDK surfaces a tool-result error block to the model; the model can decide to skip and continue or abort. We catch + log via `[ERROR: STRUCTURAL]` but never crash the loop.
4. **Model never says done AND predicate never satisfied** — cap fires. Same shape as study-buddy.
5. **User types a recipe name we don't have** — `lookup_recipe` returns `{"error": "not found"}`; model is expected to apologize and offer alternatives. Tested in smoke test.
6. **Chain exceeds total tool-call cap mid-turn** — we count tool calls as they fire; if cap hits mid-response, we let the response finish but mark `state["cap_hit"] = True` so the next loop iteration exits. (We don't try to abort an in-flight SDK response — that's brittle.)

---

## §8 — SDK Boundary

Three thin functions are the only ones that touch `claude_agent_sdk`. `smoke_test.py` mocks THESE.

```python
@contextlib.asynccontextmanager
async def open_sdk_client(options):
    """SDK boundary 1 — opens the ClaudeSDKClient. Mock THIS in smoke_test."""
    from claude_agent_sdk import ClaudeSDKClient
    async with ClaudeSDKClient(options=options) as client:
        yield client


async def send_turn(client, prompt: str, tool_observer: Callable) -> dict:
    """
    SDK boundary 2 — sends one turn; tool_observer is called for each ToolUseBlock
    and ToolResultBlock seen. Returns dict with response_text, in_tok, out_tok,
    session_id, tool_calls_this_turn.
    """
    ...


def build_options(child_env: dict) -> "ClaudeAgentOptions":
    """SDK boundary 3 — builds the options object with mcp_servers + allowed_tools."""
    ...
```

The five `@tool`-decorated functions ALSO touch the SDK (the decorator itself is from the SDK), but they're pure data operations otherwise — `smoke_test.py` can call them directly without going through the SDK lifecycle.

---

## §9 — Comment Header Format

Every major block gets:
```python
# ═══════════════════════════════════════════
# PURPOSE: one sentence
# AGENTIC TRAIT: trait name
# ACHIEVES: what the agent gains from this block
# DEPENDENCIES: what must exist before this runs
# ═══════════════════════════════════════════
```
Minimum 5 headers. Inline annotations: `# TRAIT[x]`, `# GATE[Gn]`, `# GOTCHA[x]`.

---

## §10 — QA Checklist (run before handover)

```powershell
(Select-String "main.py" -Pattern "TRAIT\[").Count           # >= 5
(Select-String "main.py" -Pattern "GATE\[").Count            # >= 5 (G1..G5 each)
(Select-String "main.py" -Pattern "GOTCHA\[").Count          # >= 1
(Select-String "main.py" -Pattern "═══").Count               # >= 5
(Select-String "main.py" -Pattern "\[AGENT BOOT\]").Count            # >= 1
(Select-String "main.py" -Pattern "\[GOAL SET\]").Count              # >= 1
(Select-String "main.py" -Pattern "\[GOAL PREDICATE\]").Count        # >= 1
(Select-String "main.py" -Pattern "\[MODEL DECISION\]").Count        # >= 1
(Select-String "main.py" -Pattern "\[LOOP FEEDBACK\]").Count         # >= 1
(Select-String "main.py" -Pattern "\[TOOL CHAIN\]").Count            # >= 1  (NEW for rung 4)
(Select-String "main.py" -Pattern "\[CONTEXT\]").Count               # >= 1
(Select-String "main.py" -Pattern "\[SDK ").Count                    # >= 1
(Select-String "main.py" -Pattern "SESSION MEMORY|APP MEMORY").Count # >= 2
(Select-String "main.py" -Pattern "AGENT SUMMARY").Count             # >= 1
python smoke_test.py                                                 # exit 0
```

Gate annotations required: G1 at `session_complete()`, G2 at the tool-routing locus (the SDK handles this — annotate at the comment explaining it), G3 at `[LOOP FEEDBACK]` AND at the chain visibility print, G4 at all four exits, G5 as N/A comment.

---

## §11 — PyCharm Run Instructions

1. Open `agents/recipe-companion` as project · verify Python 3.12+ interpreter
2. Terminal: `pip install -r requirements.txt`
3. Terminal: `claude auth status` (must show logged in)
4. Right-click `smoke_test.py` → Run (must be green)
5. Right-click `main.py` → Run · the agent will ask you what you want to cook
6. Try `spaghetti carbonara` or `pancakes` or `omelette` (recipes in the demo DB)
7. Watch for the `[TOOL CHAIN] N tool calls in this turn` line — this is the rung-4 capability landing
8. Log file: `recipe-companion_run_output.log` (appended each run)

Troubleshooting: `[PREFLIGHT FAILED]` → run `claude auth status` / `claude login`

---

*v1.0 · 2026-06-08 · Cycle 3 · Rung 4 · FORWARD*
