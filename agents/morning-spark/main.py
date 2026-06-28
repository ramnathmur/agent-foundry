"""
Morning Spark Agent v1 — main.py
Cycle 6 · SDK Rung 6 (PreToolUse guard + PostToolUse audit + JSONL span trace) · FORWARD
Domain: morning-briefing

AGENTIC TRAITS DEMONSTRATED
──────────────────────────────────────────────────────────────────────
  goal-directedness   briefing_complete() checked every turn
  autonomy            model selects tool order and headline category
  observe-reason-act  PreToolUse denial observed → model reasons → adapts category (G3)
  perception          5 mock tools simulate real morning data sources
  memory (APP)        briefing_log.json — yesterday's topic informs today's category choice
  memory (SESSION)    ClaudeSDKClient holds context across turns
  tool-selection      @tool + create_sdk_mcp_server (rung 4/5 carried)
  termination         briefing_complete() predicate + MAX_LOOP_TURNS + MAX_TOOL_CALLS caps

Control plane:
  - Which tool to call next        → model (autonomy)
  - Which headline category        → model (autonomy; PreToolUse blocks repeats)
  - Dedup enforcement              → PreToolUse hook (code)
  - Audit record                   → PostToolUse hook (code)
  - Goal check                     → code (briefing_complete())
  - Hard cap                       → code (MAX_LOOP_TURNS / MAX_TOOL_CALLS)

Rung 6 key insight: hooks fire INSIDE the SDK's execution pipeline, not around it.
  PreToolUse: fires before the tool runs — can deny with a reason the model reads.
  PostToolUse: fires after the tool returns — writes a JSONL span to disk.
  State shared between hooks and the loop MUST live at module level.

Security: NO ANTHROPIC_API_KEY. Auth via claude-agent-sdk → Claude Code CLI → Max plan.
"""

import asyncio
import contextlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

# ═══════════════════════════════════════════
# PURPOSE: Runtime constants
# ═══════════════════════════════════════════
MAX_LOOP_TURNS: int = 6
MAX_TOOL_CALLS: int = 12
MODEL_ID: str = "claude-opus-4-8"
AGENT_SLUG: str = "morning-spark"
AGENT_VERSION: str = "v1"
LOG_FILE: str = f"{AGENT_SLUG}_run_output.log"
SPANS_FILE: str = f"{AGENT_SLUG}_spans.jsonl"
BRIEFING_LOG_FILE: str = "briefing_log.json"

# RUNG6[fix]: permission_mode="dontAsk" requires an explicit allowlist — without it
# the SDK denies all MCP tools silently (PreToolUse still says ALLOW, but the tool
# never executes and PostToolUse never fires).
ALL_ALLOWED: list[str] = [
    "mcp__spark__fetch_weather",
    "mcp__spark__fetch_date",
    "mcp__spark__fetch_headline",
    "mcp__spark__check_quality",
    "mcp__spark__synthesize_briefing",
]

# ═══════════════════════════════════════════
# PURPOSE: Module-level agent state — reset before each run; updated by tool impls
# RUNG 6: hooks fire in the SDK's execution path, not in our loop. Shared state
#         MUST live here — local variables inside hook functions are invisible to the loop.
# ═══════════════════════════════════════════
_agent_state: dict = {
    "weather": None,
    "date_info": None,
    "headline": None,
    "headline_category": None,
    "quality_passed": False,
    "quality_issues": [],
    "briefing": None,
}

_hook_state: dict = {
    "calls_made": [],    # list of (tool_name, params_json) tuples seen by PreToolUse
    "spans": [],         # list of PostToolUse span records
    "denied_count": 0,   # how many times PreToolUse fired a denial this run
}


# ═══════════════════════════════════════════
# PURPOSE: Tee stdout to LOG_FILE (append mode, separator header each run)
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
    header = (f"\n{'=' * 70}\n"
              f"RUN: {datetime.now().isoformat()} | {AGENT_SLUG} {AGENT_VERSION} · rung 6\n"
              f"{'=' * 70}\n")
    log_path = Path(__file__).resolve().parent / LOG_FILE
    with open(log_path, "a", encoding="utf-8") as log_f:
        log_f.write(header)
        original = sys.stdout
        sys.stdout = _TeeStream(original, log_f)
        try:
            yield
        finally:
            sys.stdout = original


# ═══════════════════════════════════════════
# PURPOSE: App memory — briefing_log.json persists across runs (cross-day guard)
# ═══════════════════════════════════════════
def _log_path() -> Path:
    return Path(__file__).resolve().parent / BRIEFING_LOG_FILE


def _read_briefing_log() -> dict:
    p = _log_path()
    if not p.exists():
        return {}
    try:
        with open(p, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def _write_briefing_log_atomic(data: dict) -> None:
    p = _log_path()
    tmp = p.with_suffix(".json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    tmp.replace(p)


# ═══════════════════════════════════════════
# PURPOSE: JSONL span write helper (PostToolUse audit)
# ═══════════════════════════════════════════
def _write_span(span: dict) -> None:
    spans_path = Path(__file__).resolve().parent / SPANS_FILE
    with open(spans_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(span) + "\n")


# ═══════════════════════════════════════════
# PURPOSE: Mock data — simulated morning sources (no real HTTP calls)
# ═══════════════════════════════════════════
_MOCK_WEATHER = (
    "Partly cloudy, 26°C. Humidity 72%. Wind NE at 12 km/h. "
    "Expect brief afternoon showers around 3 PM. Morning commute clear."
)

_now = datetime.now()
_MOCK_DATE = f"{_now.strftime('%A, %B')} {_now.day}, {_now.year}"

_MOCK_HEADLINES: dict[str, str] = {
    "general":    "India-EU trade deal reaches final draft; signing ceremony expected next month.",
    "technology": "Anthropic releases Claude 5 with 200K context and improved reasoning benchmarks.",
    "science":    "Researchers confirm first room-temperature superconductor at ambient pressure.",
    "health":     "WHO declares dengue fever 'priority disease' as cases rise 40% in Southeast Asia.",
    "world":      "UN Security Council adopts landmark resolution on deep-sea mining governance.",
    "business":   "Indian startup funding rebounds to $3.2 billion in Q2, led by fintech and SaaS.",
}


# ═══════════════════════════════════════════
# PURPOSE: Tool implementations — morning-spark's five-tool vocabulary
# RUNG 6: every impl updates _agent_state as a side effect; PreToolUse and
#         PostToolUse hooks fire automatically — impls don't need to call them.
# ═══════════════════════════════════════════
try:
    from claude_agent_sdk import tool as _tool, create_sdk_mcp_server as _create_server
    _IMPORT_ERROR = None
except ImportError as _exc:
    _tool = None
    _create_server = None
    _IMPORT_ERROR = _exc


async def _fetch_weather_impl(args: dict) -> dict:
    _agent_state["weather"] = _MOCK_WEATHER
    return {"content": [{"type": "text", "text": _MOCK_WEATHER}]}


async def _fetch_date_impl(args: dict) -> dict:
    _agent_state["date_info"] = _MOCK_DATE
    return {"content": [{"type": "text", "text": _MOCK_DATE}]}


async def _fetch_headline_impl(args: dict) -> dict:
    category = args.get("category", "general").lower().strip()
    if category not in _MOCK_HEADLINES:
        msg = (f"Unknown category '{category}'. "
               f"Valid: {', '.join(_MOCK_HEADLINES.keys())}. Try 'general'.")
        return {"content": [{"type": "text", "text": msg}]}
    headline = _MOCK_HEADLINES[category]
    _agent_state["headline"] = headline
    _agent_state["headline_category"] = category
    return {"content": [{"type": "text", "text": headline}]}


async def _check_quality_impl(args: dict) -> dict:
    issues = []
    if _agent_state["weather"] is None:
        issues.append("weather not fetched")
    if _agent_state["date_info"] is None:
        issues.append("date not fetched")
    if _agent_state["headline"] is None:
        issues.append("headline not fetched")
    passes = len(issues) == 0
    _agent_state["quality_passed"] = passes
    _agent_state["quality_issues"] = issues
    result = {"quality_passes": passes, "issues": issues}
    return {"content": [{"type": "text", "text": json.dumps(result)}]}


async def _synthesize_briefing_impl(args: dict) -> dict:
    if not _agent_state["quality_passed"]:
        return {"content": [{"type": "text", "text": json.dumps({
            "status": "error",
            "message": "Quality check has not passed. Call check_quality first.",
        })}]}

    date_info = _agent_state["date_info"] or "today"
    weather   = _agent_state["weather"] or "(no weather data)"
    headline  = _agent_state["headline"] or "(no headline)"
    category  = _agent_state["headline_category"] or "general"

    briefing = (
        f"Good morning! Here's your briefing for {date_info}.\n\n"
        f"WEATHER: {weather}\n\n"
        f"TOP STORY ({category}): {headline}\n\n"
        f"Have a focused and productive day."
    )
    _agent_state["briefing"] = briefing

    # Write app memory
    log_entry = {
        "last_run": datetime.now(timezone.utc).isoformat(),
        "date": date_info,
        "headline_category": category,
        "headline_preview": headline[:100],
        "briefing_preview": briefing[:150],
    }
    _write_briefing_log_atomic(log_entry)

    return {"content": [{"type": "text", "text": json.dumps({
        "status": "complete",
        "briefing": briefing,
    })}]}


# Register tools with MCP server if SDK is available
if _tool is not None:
    fetch_weather_tool   = _tool("fetch_weather",   "Get today's weather forecast",                              {})(_fetch_weather_impl)
    fetch_date_tool      = _tool("fetch_date",      "Get today's date and day of the week",                     {})(_fetch_date_impl)
    fetch_headline_tool  = _tool("fetch_headline",  "Get the top news headline for a category (general/technology/science/health/world/business)", {"category": str})(_fetch_headline_impl)
    check_quality_tool   = _tool("check_quality",   "Verify all three morning sources are present and complete", {})(_check_quality_impl)
    synthesize_briefing_tool = _tool("synthesize_briefing", "Produce the final morning briefing from all fetched data", {})(_synthesize_briefing_impl)
    ALL_TOOLS = [fetch_weather_tool, fetch_date_tool, fetch_headline_tool,
                 check_quality_tool, synthesize_briefing_tool]
else:
    fetch_weather_tool = _fetch_weather_impl
    fetch_date_tool    = _fetch_date_impl
    fetch_headline_tool = _fetch_headline_impl
    check_quality_tool = _check_quality_impl
    synthesize_briefing_tool = _synthesize_briefing_impl
    ALL_TOOLS = []


# ═══════════════════════════════════════════
# PURPOSE: RUNG 6 — Hook implementations
# PreToolUse: dedup guard (fires before tool; can deny with instruction)
# PostToolUse: JSONL audit (fires after tool; writes span to disk)
# DESIGN: both hooks share _hook_state via module-level dict (see note at top)
# ═══════════════════════════════════════════
def _get_field(obj, field: str, default=None):
    """SDK may pass hook input_data as a dict or as an object — handle both."""
    if isinstance(obj, dict):
        return obj.get(field, default)
    return getattr(obj, field, default)


async def pre_tool_use_guard(input_data, tool_use_id: str, context) -> dict:
    """RUNG6[PreToolUse]: blocks repeated (tool_name, params) pairs; enforces act-strategy variation."""
    tool_name  = _get_field(input_data, "tool_name", "?")
    tool_input = _get_field(input_data, "tool_input", {})
    sig = (tool_name, json.dumps(tool_input, sort_keys=True))

    if sig in _hook_state["calls_made"]:
        _hook_state["denied_count"] += 1
        reason = (
            f"Tool '{tool_name}' with these exact parameters has already been called this run. "
            f"If this is fetch_headline, try a DIFFERENT category "
            f"(general/technology/science/health/world/business). "
            f"If you already have weather, date, and a headline, call check_quality next."
        )
        print(f"🛑 [PRE-TOOL GUARD] DENY · {tool_name}({json.dumps(tool_input)[:40]}) — duplicate detected")
        return {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": reason,
            }
        }

    _hook_state["calls_made"].append(sig)
    print(f"✅ [PRE-TOOL GUARD] ALLOW · {tool_name}({json.dumps(tool_input)[:40]})")
    return {}


async def post_tool_use_audit(input_data, tool_use_id: str, context) -> dict:
    """RUNG6[PostToolUse]: writes a JSONL span for every successful tool execution."""
    tool_name     = _get_field(input_data, "tool_name", "?")
    tool_input    = _get_field(input_data, "tool_input", {})
    tool_response = _get_field(input_data, "tool_response", "")
    result_text   = str(tool_response)

    span = {
        "timestamp":      datetime.now(timezone.utc).isoformat(),
        "tool_name":      tool_name,
        "tool_input":     tool_input,
        "result_length":  len(result_text),
        "result_preview": result_text[:120],
        "tool_use_id":    tool_use_id,
    }
    _hook_state["spans"].append(span)
    _write_span(span)
    print(f"📋 [POST-TOOL AUDIT] span written · {tool_name} · {len(result_text)} chars")
    return {}


# ═══════════════════════════════════════════
# PURPOSE: Goal predicate — single source of truth for "done"
# AGENTIC TRAIT: goal-directedness; checked every turn
# ═══════════════════════════════════════════
def briefing_complete() -> bool:
    return (
        _agent_state.get("weather") is not None
        and _agent_state.get("date_info") is not None
        and _agent_state.get("headline") is not None
        and _agent_state.get("quality_passed", False)
        and _agent_state.get("briefing") is not None
    )


# ═══════════════════════════════════════════
# PURPOSE: Render each SDK message as one compact console line
# ═══════════════════════════════════════════
def message_lens(msg) -> str:
    name = type(msg).__name__
    if name == "AssistantMessage":
        parts = []
        for block in getattr(msg, "content", []):
            btype = type(block).__name__
            if btype == "TextBlock":
                parts.append(f"TextBlock({getattr(block, 'text', '')[:50]!r})")
            elif btype == "ToolUseBlock":
                parts.append(f"ToolUseBlock({getattr(block, 'name', '?')}, {json.dumps(getattr(block, 'input', {}))[:40]})")
            elif btype == "ToolResultBlock":
                parts.append(f"ToolResultBlock(id={getattr(block, 'tool_use_id', '?')[:8]}…)")
            else:
                parts.append(btype)
        return f"  ┆ AssistantMessage: {(' | '.join(parts) or '(empty)')[:120]}"
    if name == "UserMessage":
        parts = [f"ToolResult(id={getattr(b, 'tool_use_id', '?')[:8]}…)"
                 for b in getattr(msg, "content", []) if type(b).__name__ == "ToolResultBlock"]
        return f"  ┆ UserMessage: {' | '.join(parts) or '(empty)'}"
    if name == "ResultMessage":
        cost = getattr(msg, "total_cost_usd", None)
        sid  = getattr(msg, "session_id", None)
        return (f"  ┆ ResultMessage[ok]"
                + (f" · ${cost:.4f}" if cost else "")
                + (f" · session_id={sid[:16]}…" if sid else ""))
    return f"  ┆ {name}"


# ═══════════════════════════════════════════
# PURPOSE: Verify environment before any agent work
# ═══════════════════════════════════════════
def preflight() -> dict:
    print("🔬 [PREFLIGHT] checking environment...")
    if sys.version_info < (3, 12):
        print(f"  [PREFLIGHT FAILED] Python 3.12+ required (got {sys.version_info.major}.{sys.version_info.minor})")
        sys.exit(1)
    print(f"  ✓ Python {sys.version_info.major}.{sys.version_info.minor}")

    if _tool is None:
        print(f"  [PREFLIGHT FAILED] claude_agent_sdk not importable: {_IMPORT_ERROR}")
        print("  Fix: pip install claude-agent-sdk")
        sys.exit(1)
    print(f"  ✓ claude_agent_sdk importable · {len(ALL_TOOLS)} tools registered")

    child_env = dict(os.environ)
    if "ANTHROPIC_API_KEY" in child_env:
        del child_env["ANTHROPIC_API_KEY"]
        print("  ⚠  ANTHROPIC_API_KEY stripped from child env — using Max plan CLI auth")
    print("  ✓ preflight passed\n")
    return child_env


# ═══════════════════════════════════════════
# PURPOSE: Build ClaudeAgentOptions — rung 6 hooks wired here
# ═══════════════════════════════════════════
def build_options(child_env: dict, system_prompt: str) -> Any:
    from claude_agent_sdk import ClaudeAgentOptions, HookMatcher
    server = _create_server(name="spark", version="1.0.0", tools=ALL_TOOLS)
    return ClaudeAgentOptions(
        system_prompt=system_prompt,
        model=MODEL_ID,
        mcp_servers={"spark": server},
        allowed_tools=ALL_ALLOWED,
        permission_mode="dontAsk",
        env=child_env,
        hooks={
            "PreToolUse":  [HookMatcher(matcher=None, hooks=[pre_tool_use_guard])],
            "PostToolUse": [HookMatcher(matcher=None, hooks=[post_tool_use_audit])],
        },
    )


@contextlib.asynccontextmanager
async def open_sdk_client(options):
    """SDK boundary — open ClaudeSDKClient. Mock THIS in smoke_test."""
    from claude_agent_sdk import ClaudeSDKClient
    async with ClaudeSDKClient(options=options) as client:
        yield client


async def send_turn(client, prompt: str, tool_observer: Callable) -> dict:
    """Send one turn; tool_observer fires for each ToolUseBlock seen."""
    from claude_agent_sdk.types import AssistantMessage, ResultMessage

    await client.query(prompt)
    response_text = ""
    in_tok = out_tok = 0
    tool_calls_this_turn = 0
    chain: list[tuple[str, dict]] = []

    async for msg in client.receive_response():
        print(message_lens(msg))
        if isinstance(msg, AssistantMessage):
            for block in msg.content:
                btype = type(block).__name__
                if btype == "TextBlock":
                    response_text += getattr(block, "text", "")
                elif btype == "ToolUseBlock":
                    tool_calls_this_turn += 1
                    tname  = getattr(block, "name", "?")
                    tinput = getattr(block, "input", {})
                    chain.append((tname, tinput))
                    tool_observer(tname, tinput)
        elif isinstance(msg, ResultMessage):
            if getattr(msg, "result", None):
                response_text = msg.result
            if msg.usage:
                in_tok  = msg.usage.get("input_tokens", 0)
                out_tok = msg.usage.get("output_tokens", 0)

    return {
        "response_text": response_text,
        "in_tok": in_tok,
        "out_tok": out_tok,
        "tool_calls_this_turn": tool_calls_this_turn,
        "chain": chain,
    }


# ═══════════════════════════════════════════
# PURPOSE: Print agent summary on exit (both goal-met and cap paths)
# ═══════════════════════════════════════════
def print_summary(state: dict) -> None:
    w = 62
    print()
    print("╔" + "═" * w + "╗")
    print("║" + " AGENT SUMMARY — Morning Spark ".center(w) + "║")
    print("╚" + "═" * w + "╝")
    print(f"  Exit reason      : {state.get('exit_reason', '?')}")
    print(f"  Loop turns       : {state.get('turns', 0)}/{MAX_LOOP_TURNS}")
    print(f"  Tool calls       : {state.get('total_tool_calls', 0)}/{MAX_TOOL_CALLS}")
    print(f"  Hook denials     : {_hook_state['denied_count']} (PreToolUse)")
    print(f"  Spans written    : {len(_hook_state['spans'])} → {SPANS_FILE}")
    print(f"  Tokens in/out    : {state.get('total_in_tok', 0)} / {state.get('total_out_tok', 0)}")
    print()
    if _agent_state.get("briefing"):
        print("  MORNING BRIEFING")
        print("  " + "─" * 56)
        for line in _agent_state["briefing"].splitlines():
            print(f"  {line}")
    print()
    print("  RUNG 6 SUMMARY")
    print("  " + "─" * 56)
    print(f"  PreToolUse guard  : {_hook_state['denied_count']} denial(s) fired")
    print(f"  PostToolUse audit : {len(_hook_state['spans'])} span(s) written to {SPANS_FILE}")
    if _hook_state["denied_count"] > 0:
        print("  Act-strategy gap  : model adapted category after denial (O-R-A demonstrated)")
    print()
    print("  GOAL PREDICATE MAP")
    print("  " + "─" * 56)
    print(f"  weather fetched   : {_agent_state['weather'] is not None}")
    print(f"  date fetched      : {_agent_state['date_info'] is not None}")
    print(f"  headline fetched  : {_agent_state['headline'] is not None} (category: {_agent_state.get('headline_category', '—')})")
    print(f"  quality passed    : {_agent_state['quality_passed']}")
    print(f"  briefing produced : {_agent_state['briefing'] is not None}")
    print(f"  briefing_complete : {briefing_complete()}")
    print()
    print("  MEMORY")
    print("  " + "─" * 56)
    print(f"  APP (briefing_log.json) : {'written' if _agent_state['briefing'] else 'not written (goal not met)'}")
    print(f"  SESSION (ClaudeSDKClient): closed — ephemeral")
    print("═" * (w + 2))


# ═══════════════════════════════════════════
# PURPOSE: The agent loop — all five gates exercised here
# ═══════════════════════════════════════════
async def agent_loop(child_env: dict) -> None:
    # Reset module-level state for clean run
    _agent_state.update({
        "weather": None, "date_info": None, "headline": None,
        "headline_category": None, "quality_passed": False,
        "quality_issues": [], "briefing": None,
    })
    _hook_state.update({"calls_made": [], "spans": [], "denied_count": 0})

    loop_state: dict[str, Any] = {
        "turns": 0, "total_tool_calls": 0,
        "total_in_tok": 0, "total_out_tok": 0,
        "exit_reason": "",
    }

    # ── BOOT ──
    print(f"🤖 [AGENT BOOT] {AGENT_SLUG} {AGENT_VERSION} · rung 6 · morning-briefing")
    print(f"📖 [OUTPUT GUIDE] emoji-labeled lines are teaching elements — "
          f"match to {AGENT_SLUG}_learning-guide.html §11")
    print()

    # ── APP MEMORY — cross-day guard ──
    prior_log = _read_briefing_log()
    yesterday_preview = prior_log.get("headline_preview", "")
    if yesterday_preview:
        print(f"🧠 [APP MEMORY] briefing_log.json found · yesterday's topic: {yesterday_preview[:60]}…")
        cross_day_note = (
            f"Yesterday's top topic: {yesterday_preview}\n"
            f"If today's headline looks similar to yesterday's topic, try a different category."
        )
    else:
        print("🧠 [APP MEMORY] no prior briefing_log.json — first run, no cross-day guard")
        cross_day_note = ""
    print()

    # ── SYSTEM PROMPT ──
    system_prompt = (
        "You are Morning Spark, a morning briefing agent.\n\n"
        "Your goal: produce a complete morning briefing by calling these tools:\n"
        "1. fetch_weather() — get today's weather forecast\n"
        "2. fetch_date() — get today's date and day of the week\n"
        "3. fetch_headline(category) — get a top news headline\n"
        "   Valid categories: general, technology, science, health, world, business\n"
        "4. check_quality() — verify all three sources are present\n"
        "5. synthesize_briefing() — produce the final morning briefing\n\n"
        "You may call multiple tools per turn. Call fetch_weather, fetch_date, and "
        "fetch_headline in any order, then check_quality, then synthesize_briefing.\n\n"
        "If a tool call is denied because you already used those exact parameters, "
        "use a DIFFERENT category for fetch_headline, or move to check_quality "
        "if you already have weather, date, and a headline.\n\n"
        "After synthesize_briefing returns with status 'complete', your task is done."
        + (f"\n\n{cross_day_note}" if cross_day_note else "")
    )

    # ── GOAL PRINT ──
    print("🎯 [GOAL SET] produce morning briefing: weather + date + headline + quality-pass + synthesis")
    print("   Predicate: briefing_complete() = weather ∧ date_info ∧ headline ∧ quality_passed ∧ briefing")
    print()

    # ── RUNG 6 HOOK NOTICE ──
    print("🪝 [RUNG 6 HOOKS REGISTERED]")
    print("   PreToolUse  → pre_tool_use_guard  (fires before every tool; denies repeats)")
    print("   PostToolUse → post_tool_use_audit (fires after every tool; writes JSONL span)")
    print(f"   allowed_tools ({len(ALL_ALLOWED)}): {', '.join(t.split('__')[-1] for t in ALL_ALLOWED)}")
    print()

    # ── FIRST PROMPT ──
    initial_prompt = (
        "Good morning! Please produce my morning briefing. "
        "Fetch the weather, today's date, and a top headline, "
        "then check quality and synthesize the briefing."
    )

    # ── Tool observer — fires on each ToolUseBlock seen; updates loop_state ──
    def tool_observer(tname: str, tinput: dict) -> None:
        loop_state["total_tool_calls"] += 1
        short = tname.split("__")[-1] if "__" in tname else tname
        print(f"🔧 [TOOL CALL] {short}({json.dumps(tinput)[:60]})")

    # ── BUILD OPTIONS (rung 6: hooks wired here) ──
    options = build_options(child_env, system_prompt)

    print(f"🔗 [SDK →] opening ClaudeSDKClient · model={MODEL_ID}")
    print()

    async with open_sdk_client(options) as client:
        prompt = initial_prompt

        while loop_state["turns"] < MAX_LOOP_TURNS:
            if loop_state["total_tool_calls"] >= MAX_TOOL_CALLS:
                loop_state["exit_reason"] = f"cap: MAX_TOOL_CALLS={MAX_TOOL_CALLS} reached"
                print(f"⛔ [CAP HIT] tool call cap reached ({MAX_TOOL_CALLS}). Exiting loop.")
                break

            loop_state["turns"] += 1
            print(f"── TURN {loop_state['turns']} ──────────────────────────────────────────")

            result = await send_turn(client, prompt, tool_observer)
            loop_state["total_in_tok"]  += result["in_tok"]
            loop_state["total_out_tok"] += result["out_tok"]

            goal_met = briefing_complete()
            print(f"🔄 [LOOP FEEDBACK] turn {loop_state['turns']} done · "
                  f"tool_calls={loop_state['total_tool_calls']} · "
                  f"briefing_complete={goal_met}")
            print(f"📊 [GOAL PREDICATE] weather={_agent_state['weather'] is not None} · "
                  f"date={_agent_state['date_info'] is not None} · "
                  f"headline={_agent_state['headline'] is not None} · "
                  f"quality={_agent_state['quality_passed']} · "
                  f"briefing={_agent_state['briefing'] is not None}")

            if goal_met:
                loop_state["exit_reason"] = "GOAL MET — briefing_complete() = True"
                print()
                print("✅ [GOAL MET] briefing_complete() returned True. Exiting loop.")
                break

            if result["tool_calls_this_turn"] == 0 and result["response_text"]:
                print(f"💬 [MODEL DECISION] model produced text only (no tool call this turn)")
                prompt = "Please continue — call the remaining tools to complete the briefing."
            else:
                prompt = "Continue with the next tool if the briefing is not yet complete."

        else:
            loop_state["exit_reason"] = f"cap: MAX_LOOP_TURNS={MAX_LOOP_TURNS} reached"
            print(f"⛔ [CAP HIT] turn cap reached ({MAX_LOOP_TURNS}). Exiting loop.")

    print()
    print_summary(loop_state)


# ═══════════════════════════════════════════
# PURPOSE: Entrypoint
# ═══════════════════════════════════════════
def main() -> None:
    with tee_to_log():
        child_env = preflight()
        asyncio.run(agent_loop(child_env))


if __name__ == "__main__":
    main()
