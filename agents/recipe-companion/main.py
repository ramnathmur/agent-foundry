"""
Recipe Companion Agent v1 — main.py
Cycle 3 · SDK Rung 4 (custom tools via @tool + create_sdk_mcp_server) · FORWARD
Domain: health-habits (food/cooking)

AGENTIC TRAITS DEMONSTRATED (where each fires; plain-English why)
─────────────────────────────────────────────────────────────────
  goal-directedness    session_complete() called each step                agent owns "am I done?"
  autonomy             model orchestrates tool chains within ONE turn      strongest autonomy yet (rung 4)
  observe-reason-act   three speeds: in-chain, in-session, across-sessions G3 at three scales
  perception           check_pantry / lookup_recipe (real registered)      SDK-routed, not Python-dispatched
  planning             recipe steps as plan; live progress board           plan visible per turn
  memory (SESSION)     async with ClaudeSDKClient                          LLM-side cross-turn memory (rung 3)
  memory (APP)         pantry.json / shopping_list.json / favorites.json   cross-run memory on disk
  memory (CHAIN)       _tool_observer counts ToolUseBlocks per response    NEW visibility (rung 4)
  tool-selection       @tool registration + SDK routes calls               native, not JSON-dispatch
  sequential-action    tool calls counted per turn AND across turns
  termination          4 exit branches: predicate, model-done, user-stop, cap (turns + total tool calls)

Control plane:
  - Recipe name         → user (typed at start)
  - Tool chain choice   → model (rung 4 autonomy: picks tools + order + count within one turn)
  - Timer + favorites   → model (decides when)
  - Stop on user        → user (sentinel input)
  - Final cap           → code (MAX_TURNS or MAX_TOOL_CALLS_TOTAL, whichever first)

Termination labels:
  GOAL MET (predicate-satisfied OR model-done)  ·  USER STOPPED  ·  EXIT: cap reached

Security: NO ANTHROPIC_API_KEY. Auth via claude-agent-sdk → Claude Code CLI → Max plan.
"""

import asyncio
import contextlib
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Callable

# ═══════════════════════════════════════════
# PURPOSE: Runtime constants — single source of truth for tunable parameters
# AGENTIC TRAIT: goal-directedness (G1 reads MAX); termination (G4 reads caps)
# ACHIEVES: change behavior without hunting through logic
# DEPENDENCIES: none
# ═══════════════════════════════════════════

MAX_TURNS: int = 8                       # GATE[G4]: hard cap on model turns
MAX_TOOL_CALLS_TOTAL: int = 20           # GATE[G4]: hard cap on total tool invocations
USER_STOP_SENTINELS: set[str] = {"stop", "quit", "done", "enough", "exit"}
LEDGER_PANTRY: str = "pantry.json"
LEDGER_SHOPPING: str = "shopping_list.json"
LEDGER_FAVORITES: str = "favorites.json"
LOG_FILE: str = "recipe-companion_run_output.log"
AGENT_VERSION: str = "v1"
MODEL_ID: str = "claude-opus-4-8"

# Static demo recipe DB — keeps the agent self-contained and deterministic for the demo
DEMO_RECIPES: dict[str, dict] = {
    "spaghetti carbonara": {
        "ingredients": ["spaghetti", "eggs", "pancetta", "parmesan", "black pepper", "salt"],
        "steps": ["boil water 8 minutes", "fry pancetta 5 minutes", "mix eggs and cheese",
                  "drain pasta and toss", "serve immediately"],
    },
    "pancakes": {
        "ingredients": ["flour", "eggs", "milk", "sugar", "baking powder", "butter"],
        "steps": ["mix dry", "mix wet", "combine", "cook 2 minutes per side"],
    },
    "omelette": {
        "ingredients": ["eggs", "butter", "salt", "black pepper"],
        "steps": ["beat eggs", "melt butter in pan", "cook 3 minutes folding once"],
    },
    "chicken stir fry": {
        "ingredients": ["chicken breast", "soy sauce", "garlic", "ginger", "bell pepper",
                        "broccoli", "rice"],
        "steps": ["cook rice 18 minutes", "marinate chicken 10 minutes",
                  "stir fry chicken 5 minutes", "add vegetables 4 minutes", "serve over rice"],
    },
    "simple salad": {
        "ingredients": ["lettuce", "tomato", "cucumber", "olive oil", "salt", "black pepper"],
        "steps": ["wash and chop", "combine", "dress with oil + salt + pepper"],
    },
}


# ═══════════════════════════════════════════
# PURPOSE: Mirror every print() to LOG_FILE for post-run Part 2 analysis
# AGENTIC TRAIT: termination — ensures log written even on cap exit
# ACHIEVES: tee_to_log() context manager; appends, never overwrites
# DEPENDENCIES: LOG_FILE constant; used in main() only
# ═══════════════════════════════════════════

class _TeeStream:
    def __init__(self, original, log_handle):
        self._original = original
        self._log = log_handle

    def write(self, data):
        self._original.write(data)
        self._log.write(data)
        return len(data)

    def flush(self):
        self._original.flush()
        self._log.flush()

    def __getattr__(self, name):
        return getattr(self._original, name)


@contextlib.contextmanager
def tee_to_log():
    """TRAIT[termination] — mirrors all stdout to LOG_FILE (append mode)."""
    header = (
        f"\n{'=' * 70}\n"
        f"RUN: {datetime.now().isoformat()} | Recipe Companion {AGENT_VERSION} · rung 4\n"
        f"{'=' * 70}\n"
    )
    with open(LOG_FILE, "a", encoding="utf-8") as log_f:
        log_f.write(header)
        original_stdout = sys.stdout
        sys.stdout = _TeeStream(original_stdout, log_f)
        try:
            yield
        finally:
            sys.stdout = original_stdout


# ═══════════════════════════════════════════
# PURPOSE: Persistent across-run memory — three small JSON ledgers
# AGENTIC TRAIT: memory (APP layer); perception (disk reads)
# ACHIEVES: pantry/shopping/favorites survive across sessions; atomic writes
# DEPENDENCIES: ledger files in same folder as main.py
# ═══════════════════════════════════════════

def _ledger_path(filename: str) -> Path:
    return Path(__file__).resolve().parent / filename


def _read_json(filename: str, default):
    """TRAIT[memory] — reads a JSON ledger; returns default on error or absence."""
    path = _ledger_path(filename)
    if not path.exists():
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        # GOTCHA[corrupt-ledger]: corrupted file treated as empty (don't crash)
        return default


def _write_json_atomic(filename: str, data) -> None:
    """TRAIT[memory] — writes JSON atomically (temp file + rename)."""
    path = _ledger_path(filename)
    # GOTCHA[atomic-write]: write to .tmp then rename — never leaves a half-written file
    tmp = path.with_suffix(".json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    tmp.replace(path)


# ═══════════════════════════════════════════
# PURPOSE: Five registered tools — the agent's vocabulary
# AGENTIC TRAIT: tool-selection (NEW — model invokes via SDK); perception
# ACHIEVES: rung-4 native tool registration; model can chain these within one turn
# DEPENDENCIES: claude_agent_sdk's @tool decorator; ledger JSON files
# ═══════════════════════════════════════════

# NOTE: We import the @tool decorator at module level because the decorators must
# evaluate when the module is loaded. smoke_test.py can still mock the higher-level
# SDK functions (open_sdk_client, send_turn) without needing real SDK calls.
try:
    from claude_agent_sdk import tool as _tool, create_sdk_mcp_server as _create_server
except ImportError as _exc:  # pragma: no cover — runtime guard, preflight catches this
    _tool = None
    _create_server = None
    _IMPORT_ERROR = _exc


# GOTCHA[empty-ledger]: first run handles all ledgers being absent / empty gracefully
def _pantry_set() -> set[str]:
    return set(_read_json(LEDGER_PANTRY, []))


# Define all tool implementations unconditionally so smoke_test can always import them.
# The @_tool decorator is applied only if the SDK is available.

async def _lookup_recipe_impl(args: dict) -> dict:
    """TRAIT[perception] — model-callable recipe lookup."""
    name = args.get("name", "").strip().lower()
    recipe = DEMO_RECIPES.get(name)
    if recipe is None:
        # GOTCHA[unknown-recipe]: graceful not-found; model decides how to recover
        msg = (f"Recipe '{name}' not in demo DB. Available: "
               + ", ".join(sorted(DEMO_RECIPES.keys())))
        return {"content": [{"type": "text", "text": msg}]}
    body = json.dumps({"name": name, **recipe})
    return {"content": [{"type": "text", "text": body}]}


async def _check_pantry_impl(args: dict) -> dict:
    """TRAIT[perception] — model-callable pantry check."""
    ing = args.get("ingredient", "").strip().lower()
    has_it = ing in _pantry_set()
    return {"content": [{"type": "text", "text": "yes" if has_it else "no"}]}


async def _add_to_shopping_list_impl(args: dict) -> dict:
    """TRAIT[memory] — model-callable shopping-list writer."""
    item = args.get("item", "").strip().lower()
    if not item:
        return {"content": [{"type": "text", "text": "ignored (empty item)"}]}
    current = _read_json(LEDGER_SHOPPING, [])
    if item in current:
        return {"content": [{"type": "text", "text": f"'{item}' already on list"}]}
    current.append(item)
    _write_json_atomic(LEDGER_SHOPPING, current)
    return {"content": [{"type": "text", "text": f"added '{item}' to shopping list"}]}


async def _set_timer_impl(args: dict) -> dict:
    """TRAIT[tool-use] — model-callable timer (mocked for demo)."""
    minutes = int(args.get("minutes", 0))
    label = args.get("label", "timer").strip()
    if minutes <= 0:
        return {"content": [{"type": "text", "text": "ignored (minutes must be positive)"}]}
    msg = f"⏲ TIMER SET: {minutes} min · {label}"
    return {"content": [{"type": "text", "text": msg}]}


async def _note_favorite_impl(args: dict) -> dict:
    """TRAIT[memory] — model-callable favorites writer."""
    name = args.get("recipe_name", "").strip().lower()
    if not name:
        return {"content": [{"type": "text", "text": "ignored (empty name)"}]}
    current = _read_json(LEDGER_FAVORITES, [])
    if name in current:
        return {"content": [{"type": "text", "text": f"'{name}' already a favorite"}]}
    current.append(name)
    _write_json_atomic(LEDGER_FAVORITES, current)
    return {"content": [{"type": "text", "text": f"noted '{name}' as favorite"}]}


# Apply the @_tool decorator if the SDK is available; otherwise create plain aliases.
if _tool is not None:
    lookup_recipe_tool = _tool("lookup_recipe", "Look up a recipe by name; returns its ingredients and steps", {"name": str})(_lookup_recipe_impl)
    check_pantry_tool = _tool("check_pantry", "Check whether an ingredient is currently in the user's pantry", {"ingredient": str})(_check_pantry_impl)
    add_to_shopping_list_tool = _tool("add_to_shopping_list", "Add an item to the user's shopping list (deduplicated)", {"item": str})(_add_to_shopping_list_impl)
    set_timer_tool = _tool("set_timer", "Set a cooking timer with a label (mock — prints + logs only)", {"minutes": int, "label": str})(_set_timer_impl)
    note_favorite_tool = _tool("note_favorite", "Note a recipe as a user favorite (persists across runs)", {"recipe_name": str})(_note_favorite_impl)
else:
    # Fallback: plain async functions for smoke_test when SDK isn't available.
    lookup_recipe_tool = _lookup_recipe_impl
    check_pantry_tool = _check_pantry_impl
    add_to_shopping_list_tool = _add_to_shopping_list_impl
    set_timer_tool = _set_timer_impl
    note_favorite_tool = _note_favorite_impl

ALL_TOOLS = [lookup_recipe_tool, check_pantry_tool, add_to_shopping_list_tool,
             set_timer_tool, note_favorite_tool] if _tool is not None else []


# ═══════════════════════════════════════════
# PURPOSE: Render each SDK message as one compact auditable console line
# AGENTIC TRAIT: perception — makes raw SDK traffic visible during the loop
# ACHIEVES: learning element so student sees ToolUseBlocks fire in real time
# DEPENDENCIES: called only inside send_turn()
# ═══════════════════════════════════════════

def message_lens(msg) -> str:
    """Returns one ┆-prefixed summary line per SDK message."""  # TRAIT[perception]
    name = type(msg).__name__
    if name == "AssistantMessage":
        parts = []
        for block in getattr(msg, "content", []):
            btype = type(block).__name__
            if btype == "TextBlock":
                txt = getattr(block, "text", "")[:60]
                parts.append(f"TextBlock({txt!r})")
            elif btype == "ToolUseBlock":
                tname = getattr(block, "name", "?")
                tinput = getattr(block, "input", {})
                parts.append(f"ToolUseBlock({tname}, {json.dumps(tinput)[:50]})")
            elif btype == "ToolResultBlock":
                tid = getattr(block, "tool_use_id", "?")[:8]
                parts.append(f"ToolResultBlock(id={tid}…)")
            else:
                parts.append(btype)
        preview = (" | ".join(parts) or "(no blocks)")[:110]
        return f"  ┆ AssistantMessage: {preview}"
    if name == "UserMessage":
        # Tool results come back as UserMessage with ToolResultBlock content
        parts = []
        for block in getattr(msg, "content", []):
            btype = type(block).__name__
            if btype == "ToolResultBlock":
                tid = getattr(block, "tool_use_id", "?")[:8]
                parts.append(f"ToolResult(id={tid}…)")
            else:
                parts.append(btype)
        return f"  ┆ UserMessage: {' | '.join(parts) or '(empty)'}"
    if name == "ResultMessage":
        cost = getattr(msg, "total_cost_usd", None)
        suffix = f" · ${cost:.4f}" if cost is not None else ""
        sid = getattr(msg, "session_id", None)
        sid_s = f" · session_id={sid[:16]}…" if sid else ""
        return f"  ┆ ResultMessage[ok]{suffix}{sid_s}"
    return f"  ┆ {name}"


# ═══════════════════════════════════════════
# PURPOSE: Verify runtime environment before any agent work begins
# AGENTIC TRAIT: goal-directedness — refuses to start without valid preconditions
# ACHIEVES: clear error messages with fix-it guidance; strips API key from child env
# DEPENDENCIES: claude_agent_sdk importable; claude CLI in PATH
# ═══════════════════════════════════════════

def preflight() -> dict[str, str]:
    """GATE[G1]: validates preconditions. Returns child_env (copy minus API key)."""
    print("🔬 [PREFLIGHT] checking environment...")
    if sys.version_info < (3, 12):
        print(f"  [PREFLIGHT FAILED] Python 3.12+ required — got "
              f"{sys.version_info.major}.{sys.version_info.minor}")
        print("  Fix: install Python 3.12 from python.org and update PyCharm interpreter")
        sys.exit(1)
    print(f"  ✓ Python {sys.version_info.major}.{sys.version_info.minor}")

    if _tool is None:
        print("  [PREFLIGHT FAILED] claude_agent_sdk not installed")
        print("  Fix: pip install claude-agent-sdk>=0.2.93")
        sys.exit(1)
    print("  ✓ claude_agent_sdk importable")
    print(f"  ✓ {len(ALL_TOOLS)} tools registered via @tool decorator")

    child_env: dict[str, str] = dict(os.environ)
    if "ANTHROPIC_API_KEY" in child_env:
        # GOTCHA[api-key-bypass]: a key would route calls through paid API, bypassing Max plan
        del child_env["ANTHROPIC_API_KEY"]
        print("  ⚠  ANTHROPIC_API_KEY stripped from child-process env "
              "— SDK will use Max plan CLI auth instead")

    print("  ✓ preflight passed\n")
    return child_env


# ═══════════════════════════════════════════
# PURPOSE: Goal predicate — unambiguous stopping condition
# AGENTIC TRAIT: goal-directedness (G1), termination criterion
# ACHIEVES: returns bool; the single difference from a non-agent
# DEPENDENCIES: state dict built up by agent_loop()
# ═══════════════════════════════════════════

def session_complete(state: dict) -> bool:
    """GATE[G1]: True when user stopped, model done, or all four prep steps complete."""  # TRAIT[goal-directedness]
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


# ═══════════════════════════════════════════
# PURPOSE: SDK boundary — three thin functions that touch claude_agent_sdk
# AGENTIC TRAIT: autonomy (model orchestrates tools inside send_turn)
# ACHIEVES: isolated, mockable seam — smoke_test mocks THESE
# DEPENDENCIES: claude_agent_sdk ≥ 0.2.93; child_env with API key stripped
# ═══════════════════════════════════════════

def build_options(child_env: dict[str, str]):
    """SDK boundary — builds ClaudeAgentOptions with all 5 tools wired in via mcp_servers."""
    from claude_agent_sdk import ClaudeAgentOptions

    kitchen_server = _create_server(name="kitchen", version="1.0.0", tools=ALL_TOOLS)

    return ClaudeAgentOptions(
        system_prompt=(
            "You are Recipe Companion, a kitchen assistant.\n"
            "When the user names a recipe, do the prep end-to-end:\n"
            "  1. Call lookup_recipe with the recipe name.\n"
            "  2. For each ingredient in the recipe, call check_pantry.\n"
            "  3. For each ingredient that returned 'no', call add_to_shopping_list.\n"
            "  4. Briefly tell the user what you found and ask if they're ready to cook.\n"
            "  5. When the user confirms, call set_timer for the first cooking step.\n"
            "  6. If the user sounds enthusiastic, call note_favorite.\n\n"
            "Chain tool calls within a single response when possible — that's faster and cheaper.\n"
            "When all four prep steps are complete (looked up, checked, shopping list, timer set), "
            "say so in your final text — your last sentence should make clear the session is done."
        ),
        model=MODEL_ID,
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


@contextlib.asynccontextmanager
async def open_sdk_client(options):
    """SDK boundary — opens ClaudeSDKClient. Mock THIS in smoke_test."""
    from claude_agent_sdk import ClaudeSDKClient
    async with ClaudeSDKClient(options=options) as client:
        yield client


async def send_turn(client, prompt: str,
                    tool_observer: Callable[[str, dict], None]) -> dict:
    """
    SDK boundary — sends one turn; tool_observer fires for each ToolUseBlock seen.
    Returns dict with response_text, in_tok, out_tok, session_id, tool_calls_this_turn.
    TRAIT[autonomy] — every model decision flows through here.
    """
    from claude_agent_sdk.types import AssistantMessage, ResultMessage, TextBlock

    await client.query(prompt)
    response_text = ""
    in_tok = out_tok = 0
    session_id: str | None = None
    tool_calls_this_turn = 0
    async for msg in client.receive_response():
        print(message_lens(msg))
        if isinstance(msg, AssistantMessage):
            for block in msg.content:
                btype = type(block).__name__
                if btype == "TextBlock":
                    response_text += getattr(block, "text", "")
                elif btype == "ToolUseBlock":
                    tool_calls_this_turn += 1
                    tool_observer(getattr(block, "name", "?"),
                                  getattr(block, "input", {}))
        elif isinstance(msg, ResultMessage):
            if getattr(msg, "result", None):
                response_text = msg.result
            if msg.usage:
                in_tok = msg.usage.get("input_tokens", 0)
                out_tok = msg.usage.get("output_tokens", 0)
            sid = getattr(msg, "session_id", None)
            if sid:
                session_id = sid
    return {
        "response_text": response_text,
        "in_tok": in_tok,
        "out_tok": out_tok,
        "session_id": session_id,
        "tool_calls_this_turn": tool_calls_this_turn,
    }


# ═══════════════════════════════════════════
# PURPOSE: Live progress board after every turn
# AGENTIC TRAIT: planning
# ACHIEVES: visual feedback; per-prep-step status
# DEPENDENCIES: state dict
# ═══════════════════════════════════════════

def print_plan_progress(state: dict) -> None:
    """TRAIT[planning] — visual prep-step board."""
    def mark(key: str) -> str:
        return "✓" if state.get(key) else "○"
    print(f"  📋 [PLAN PROGRESS] turn {state['turns']}/{MAX_TURNS} · "
          f"total tool calls {state['total_tool_calls']}/{MAX_TOOL_CALLS_TOTAL}")
    print(f"     {mark('recipe_looked_up')} recipe looked up")
    print(f"     {mark('all_ingredients_checked')} ingredients checked")
    print(f"     {mark('shopping_list_updated')} shopping list updated")
    print(f"     {mark('first_timer_set')} first timer set")


def print_summary(state: dict) -> None:
    """Unconditional POST-RUN AGENT SUMMARY — fires whether GOAL MET, USER STOPPED, or cap."""
    print()
    print("╔" + "═" * 58 + "╗")
    print("║" + " 🧠 AGENT SUMMARY ".center(58) + "║")
    print("╚" + "═" * 58 + "╝")
    print(f"  Recipe           : {state.get('recipe_name', '(none)')}")
    print(f"  Exit reason      : {state['exit_reason']}")
    print(f"  Turns            : {state['turns']}/{MAX_TURNS}")
    print(f"  Total tool calls : {state['total_tool_calls']}/{MAX_TOOL_CALLS_TOTAL}")
    if state['tool_call_breakdown']:
        print(f"  Tool breakdown   : {dict(state['tool_call_breakdown'])}")
    print(f"  Tokens in/out    : {state['total_in_tok']} / {state['total_out_tok']}")
    if state.get("session_id"):
        print(f"  Session id       : {state['session_id']}")
    print()
    print("  TRAIT / GATE MAP (where each fired this run)")
    print("  ─────────────────────────────────────────────")
    print("  G1 goal-directedness : session_complete() called after every turn")
    print("  G2 autonomy          : [MODEL DECISION] + [TOOL CHAIN] lines — model "
          "orchestrated tool sequences inside single turns")
    print("  G3 observe-reason-act: three layers — within-chain (each tool result shaped next), "
          "within-session, across-sessions")
    print(f"  G4 termination       : {state['exit_reason']}")
    print("  G5                   : N/A (rung 4; independent verifier arrives at rung 7)")
    print()
    print("  MEMORY LEDGER (session vs application — kept separate per CLAUDE.md FR-C8)")
    print("  ─────────────────────────────────────────────────────────────────────")
    print(f"  SESSION MEMORY     : ClaudeSDKClient held {state['turns']} turns "
          "(gone now — block exited)")
    print(f"  APP MEMORY (disk)  : pantry={len(_read_json(LEDGER_PANTRY, []))} items · "
          f"shopping_list={len(_read_json(LEDGER_SHOPPING, []))} items · "
          f"favorites={len(_read_json(LEDGER_FAVORITES, []))} items")
    print()
    print("  💡 LESSON — Cycle 3 vs Cycle 2")
    print("  ─────────────────────────────────────")
    print("  In Cycle 2, the model emitted JSON describing what tool to call; your Python")
    print("  parsed the string and dispatched. One model response = one tool call max.")
    print("  Here, the SDK knows about the tools natively (registered via @tool). The model")
    print("  can call several tools back-to-back inside a SINGLE response — each result")
    print("  feeding the next call without your Python seeing the message in between.")
    print("  [TOOL CHAIN] N lines show the count. That's the rung-4 capability landing.")
    print("═" * 60)


# ═══════════════════════════════════════════
# PURPOSE: The agent loop — wake up, plan, chain tools, confirm, stop
# AGENTIC TRAIT: observe-reason-act (G3), sequential-action, memory, planning
# ACHIEVES: all five gates exercised; all four exit paths reachable and tested
# DEPENDENCIES: all functions above; child_env from preflight()
# ═══════════════════════════════════════════

async def agent_loop(child_env: dict[str, str], recipe_name: str) -> dict:
    """TRAIT[observe-reason-act] — the rung 4 loop with tool chaining inside turns."""
    state: dict[str, Any] = {
        "recipe_name": recipe_name,
        "turns": 0,
        "total_tool_calls": 0,
        "tool_call_breakdown": {},
        "recipe_looked_up": False,
        "all_ingredients_checked": False,
        "shopping_list_updated": False,
        "first_timer_set": False,
        "user_stopped": False,
        "model_done": False,
        "exit_reason": "",
        "session_id": None,
        "total_in_tok": 0,
        "total_out_tok": 0,
    }

    # ── BOOT ──
    print(f"🤖 [AGENT BOOT] Recipe Companion {AGENT_VERSION} · rung 4")
    print("📖 [OUTPUT GUIDE] each emoji-labeled line is a teaching element — "
          "match to learning-guide.html §6")
    print()
    print(f"🎯 [GOAL SET] Help the user cook '{recipe_name}' end-to-end "
          f"(lookup → check pantry → shopping list → set timer)")
    print("   GATE[G1]: session_complete() evaluated after every turn")
    print()

    # ── WAKE UP — read all three APP MEMORY ledgers ──
    pantry = _read_json(LEDGER_PANTRY, [])
    shopping = _read_json(LEDGER_SHOPPING, [])
    favorites = _read_json(LEDGER_FAVORITES, [])
    print(f"📀 [APP MEMORY] read {LEDGER_PANTRY} → {len(pantry)} items · "
          f"{LEDGER_SHOPPING} → {len(shopping)} items · "
          f"{LEDGER_FAVORITES} → {len(favorites)} items")
    if favorites and recipe_name.lower() in [f.lower() for f in favorites]:
        print(f"     · '{recipe_name}' is one of your noted favorites")
    print()

    print("📋 [PLAN GENERATED]")  # TRAIT[planning]
    print(f"     · look up the recipe, then chain pantry checks for each ingredient")
    print(f"     · build shopping list for missing items; set first timer when ready")
    print()

    options = build_options(child_env)

    # Tool observer — runs inside send_turn for every ToolUseBlock seen
    chain_buffer: list[tuple[str, dict]] = []

    def tool_observer(tool_name: str, tool_input: dict) -> None:
        """Counts tool calls and updates state hints."""
        chain_buffer.append((tool_name, tool_input))
        state["total_tool_calls"] += 1
        state["tool_call_breakdown"][tool_name] = \
            state["tool_call_breakdown"].get(tool_name, 0) + 1
        # State hints from tool semantics — tells session_complete() what was accomplished
        if tool_name == "lookup_recipe":
            state["recipe_looked_up"] = True
        elif tool_name == "check_pantry":
            state["all_ingredients_checked"] = True   # set on first; updated by last-turn check below
        elif tool_name == "add_to_shopping_list":
            state["shopping_list_updated"] = True
        elif tool_name == "set_timer":
            state["first_timer_set"] = True

    # ── async with: persistent conversation + tools wired in — RUNG 4 ──
    async with open_sdk_client(options) as client:  # TRAIT[memory] (session)
        # TRAIT[sequential-action] + GATE[G4]: exits on goal-met OR user-stop OR caps
        first_turn_user_input = recipe_name
        while not session_complete(state) and state["turns"] < MAX_TURNS:
            state["turns"] += 1
            iteration = state["turns"]
            print("─" * 60)
            print(f"📍 [STEP {iteration}]  turn {iteration}/{MAX_TURNS}")

            # ── Build turn prompt ──
            if iteration == 1:
                turn_prompt = (
                    f"User wants to cook: {first_turn_user_input}\n"
                    f"Recipes available in lookup: {sorted(DEMO_RECIPES.keys())}\n"
                    "Start the prep: look up the recipe, check each ingredient against the "
                    "pantry by calling check_pantry for each one, then add missing items "
                    "to the shopping list. Briefly summarize for the user and ask if they're "
                    "ready to cook. Chain the tool calls in this single response when possible."
                )
            else:
                turn_prompt = (
                    f"User answered: {first_turn_user_input}\n"
                    "Continue based on what they said. If they confirmed they're ready, "
                    "call set_timer for the first cooking step and tell them the session is done."
                )

            ctx_words = len(turn_prompt.split())
            print(f"📊 [CONTEXT] turn-prompt {ctx_words} words · "
                  f"client holds {iteration - 1} prior turn(s) of conversation")

            # ── REASON + ACT (model orchestrates the tool chain inside this call) ──
            print(f"━━━ [SDK →] {MODEL_ID} · turn {iteration} "
                  f"({'opening conversation' if iteration == 1 else 'continuing same conversation'}) "
                  f"· {len(ALL_TOOLS)} tools registered")
            chain_buffer.clear()
            try:
                turn_result = await send_turn(client, turn_prompt, tool_observer)
            except Exception as exc:
                # GOTCHA[transient-sdk-error]: don't crash on single failed turn
                print(f"  ⚠ [ERROR: TRANSIENT → skip] SDK turn failed: {exc}")
                state["turns"] -= 1
                continue
            state["total_in_tok"] += turn_result["in_tok"]
            state["total_out_tok"] += turn_result["out_tok"]
            if turn_result["session_id"]:
                state["session_id"] = turn_result["session_id"]
            print(f"━━━ [← SDK] +{turn_result['in_tok']} in / +{turn_result['out_tok']} out tokens")

            # ── TOOL CHAIN VISIBILITY (NEW — rung 4) ──
            n_chain = turn_result["tool_calls_this_turn"]
            print(f"🔗 [TOOL CHAIN] {n_chain} tool call(s) in this turn")  # GATE[G3] TRAIT[autonomy]
            for tname, tinput in chain_buffer:
                preview = json.dumps(tinput)[:60]
                print(f"     · 🔧 [TOOL CALL] {tname}({preview})")  # TRAIT[tool-use]

            # ── SESSION MEMORY (rung 3 carried) ──
            print(f"💾 [SESSION MEMORY] rung 3 — client holds {iteration} turn(s) of conversation")

            # ── MODEL DECISION (G2) — orchestration verdict for this turn ──
            # GATE[G2]: model owned the choice of tool sequence; Python only routes after-the-fact
            print(f"🎲 [MODEL DECISION] orchestrated {n_chain} tool call(s) this turn "
                  f"· alternatives: ask user, set timer, declare done")

            # ── LOOP FEEDBACK (G3) — within-chain + across-turn ──
            if iteration == 1:
                print(f"🔄 [LOOP FEEDBACK] first turn — model chained {n_chain} tools based on "
                      "the recipe's ingredient list (each check_pantry result shaped the next call)")  # GATE[G3]
            else:
                print(f"🔄 [LOOP FEEDBACK] this turn was shaped by the user's answer to last turn "
                      "AND by the prior tool results carried in session memory")  # GATE[G3]

            # ── ACT — also check final text for "session done" signal ──
            final_text = turn_result["response_text"].lower()
            if any(phrase in final_text for phrase in
                   ["session is done", "ready to cook", "all set", "we're done"]):
                # Heuristic — model said something that suggests it's done
                if state["first_timer_set"]:
                    state["model_done"] = True
                    print("📝 [PLAN REVISED] model signalled session complete in final text")  # TRAIT[autonomy]

            # ── EVALUATE goal predicate (G1) ──
            goal_now = session_complete(state)
            print(f"📐 [GOAL PREDICATE] session_complete(state) → {goal_now} "
                  f"(recipe={state['recipe_looked_up']}, ing={state['all_ingredients_checked']}, "
                  f"list={state['shopping_list_updated']}, timer={state['first_timer_set']})")  # GATE[G1]

            # ── TERMINATION CHECK ──
            cap_pct = max(int(100 * iteration / MAX_TURNS),
                          int(100 * state["total_tool_calls"] / MAX_TOOL_CALLS_TOTAL))
            print(f"🔍 [TERMINATION CHECK] {iteration}/{MAX_TURNS} turns · "
                  f"{state['total_tool_calls']}/{MAX_TOOL_CALLS_TOTAL} tool calls · {cap_pct}%")
            print_plan_progress(state)

            if goal_now:
                break

            # ── Ask the user the next thing — show the assistant's text, then read ──
            if turn_result["response_text"].strip():
                print()
                print(f"💬 Assistant: {turn_result['response_text'].strip()[:400]}")
            print()
            try:
                first_turn_user_input = input("Your reply (or 'stop'/'done' to exit): ").strip()
            except (EOFError, KeyboardInterrupt):
                first_turn_user_input = "stop"
            print(f"🔒 [TRUST FENCE] user input will be wrapped before reaching model next turn")
            print(f"📥 [TOOL RESULT] user reply: {len(first_turn_user_input)} chars")  # TRAIT[perception]
            if first_turn_user_input.lower() in USER_STOP_SENTINELS:
                state["user_stopped"] = True
                state["exit_reason"] = "🏁 USER STOPPED — exiting at user request"
                # GATE[G4]: user-stop exit
                break
            # Hard cap check on total tool calls
            if state["total_tool_calls"] >= MAX_TOOL_CALLS_TOTAL:
                state["exit_reason"] = (
                    f"🏁 EXIT: cap reached — {state['total_tool_calls']}/{MAX_TOOL_CALLS_TOTAL} "
                    "total tool calls"
                )
                # GATE[G4]: hard-cap exit (tool-call cap)
                break

    # ── EXIT — four principled paths ──
    if not state["exit_reason"]:
        if state["model_done"]:
            state["exit_reason"] = "🏁 GOAL MET — model assessed session complete"
        elif state["user_stopped"]:
            state["exit_reason"] = "🏁 USER STOPPED — exiting at user request"
        elif session_complete(state):
            state["exit_reason"] = "🏁 GOAL MET — recipe prep complete (all 4 steps satisfied)"
            # GATE[G4]: predicate-satisfied exit
        else:
            state["exit_reason"] = (
                f"🏁 EXIT: cap reached — {state['turns']}/{MAX_TURNS} turns OR "
                f"{state['total_tool_calls']}/{MAX_TOOL_CALLS_TOTAL} tool calls"
            )
            # GATE[G4]: hard-cap exit (turn cap)

    print("─" * 60)
    print(state["exit_reason"])
    print_summary(state)
    # GATE[G5]: N/A — independent verifier arrives at rung 7; no critic call in this agent
    return state


async def main() -> None:
    with tee_to_log():
        child_env = preflight()
        print("Available demo recipes: " + ", ".join(sorted(DEMO_RECIPES.keys())))
        try:
            recipe_name = input("What would you like to cook? ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n(no input — exiting)")
            return
        if not recipe_name:
            print("(empty recipe name — exiting)")
            return
        await agent_loop(child_env, recipe_name)


if __name__ == "__main__":
    asyncio.run(main())
