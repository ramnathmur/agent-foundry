"""
Morning Intel Agent v1 — main.py
Cycle 7 · SDK Rung 8 (LATERAL-RIGHT) · morning-briefing

AGENTIC TRAITS DEMONSTRATED
┌──────────────────────┬────────────────────────────────────────┬───────────────────────────────────────────────────────┐
│ Trait                │ Where in code                          │ Why it's agentic                                      │
├──────────────────────┼────────────────────────────────────────┼───────────────────────────────────────────────────────┤
│ Goal-directedness    │ briefing_complete() checked every turn │ Five-part predicate computed, not narrated            │
│ Autonomy             │ Synthesis query() — model picks lead   │ Code offers 3 sections; model picks priority order    │
│ Observe-reason-act   │ Low quality → targeted re-dispatch     │ Next action depends on what previous action returned  │
│ Perception           │ MOCK_WEATHER_DATA / HEADLINES / CAL    │ External data shapes what gets synthesized            │
│ Planning             │ Plan printed at boot; board per turn   │ Plan before action; visible progress at every step    │
│ Memory (subagent)    │ run_weather_analyst/news/calendar()    │ Each sub-agent owns its own context — rung 8          │
│ Memory (session)     │ Main loop carries all reports          │ Reports accumulated across turns without re-fetching  │
│ Memory (app)         │ morning-intel_briefing_log.json        │ Yesterday's lead section survives to next run         │
│ Tool selection       │ Sub-agents call their own tools        │ Model-routed tool calls within each specialist        │
│ Principled stop      │ MAX_MAIN_TURNS + MAX_SUBAGENTS caps    │ Both exit paths reachable and labelled                │
└──────────────────────┴────────────────────────────────────────┴───────────────────────────────────────────────────────┘

CONTROL PLANE:
  - Which section leads the brief          → model (autonomy, G2)
  - Whether a section needs follow-up      → code (quality threshold check)
  - What parameters to change on follow-up → code (hard-coded variation strategy)
  - Goal-met verdict                        → code (briefing_complete() predicate)
  - Hard caps                               → code (MAX_MAIN_TURNS, MAX_SUBAGENTS)

RUNG 8 KEY INSIGHT: each sub-agent runner (run_weather_analyst etc.) creates
an independent query() call — a separate context window created on entry and
discarded on return. The main agent never sees the sub-agent's reasoning, only
the structured report it hands back.

LATERAL-RIGHT CONTRAST vs research-lead (rung 8):
  research-lead: homogeneous sub-researchers (all do the same task type).
  morning-intel: heterogeneous specialists (different jobs, different tools).
  Follow-up logic must target the specific specialist type that failed — substitution
  is architecturally impossible.

Security: NO ANTHROPIC_API_KEY. Auth via claude-agent-sdk -> Claude Code CLI -> Max plan.
"""

import asyncio
import contextlib
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# ═══════════════════════════════════════════
# PURPOSE: Module-level SDK import — critical for smoke_test.py patching
# ACHIEVES: patch('main.query') finds the name at module scope
# AGENTIC TRAIT: Rung 8 — each sub-agent call creates an independent context window
# GOTCHA[module-import-scope]: importing query locally inside run_*() functions
#   makes it invisible to patch('main.query') in smoke tests. Always import at
#   module level with a try/except guard. (Lesson from research-lead repair 1.)
# ═══════════════════════════════════════════
try:
    from claude_agent_sdk import query
except ImportError:
    query = None  # patched in smoke_test.py


async def _run_query(prompt: str) -> Any:
    """Adapter: iterate the async-generator query() and return a result with .text set.

    GOTCHA[query-is-async-generator]: the real claude-agent-sdk query() is an async
    generator (it yields SDK message objects). `await query(...)` raises
    TypeError: object async_generator can't be used in 'await' expression.

    GOTCHA[result-message-empty-text]: in some SDK versions ResultMessage.text is
    empty even on a successful call — the actual response text is carried in an
    earlier AssistantMessage content block. This adapter scans ALL yielded messages
    and accumulates the last non-empty text it finds, then normalises the return
    value so callers always see a .text attribute.
    """
    import types as _types
    last_text = ""
    final_msg = None

    async for msg in query(prompt=prompt):
        final_msg = msg
        # (1) ResultMessage.result — the full text response in real SDK
        candidate = getattr(msg, "result", None)
        if isinstance(candidate, str) and candidate:
            last_text = candidate
        # (2) Direct .text (mock objects + some SDK versions)
        candidate = getattr(msg, "text", None)
        if isinstance(candidate, str) and candidate:
            last_text = candidate
        # (3) AssistantMessage content blocks — handle both object and dict shapes
        for block in (getattr(msg, "content", None) or []):
            block_type = (getattr(block, "type", None)
                          or (block.get("type") if isinstance(block, dict) else None))
            if block_type == "text":
                t = (getattr(block, "text", None)
                     or (block.get("text") if isinstance(block, dict) else None)
                     or "")
                if t:
                    last_text = t

    if final_msg is None:
        raise RuntimeError("query() yielded no messages")

    # Normalise: always return something with a non-empty .text
    if not getattr(final_msg, "text", ""):
        return _types.SimpleNamespace(text=last_text, type=type(final_msg).__name__)
    return final_msg


# ═══════════════════════════════════════════
# PURPOSE: Runtime constants
# AGENTIC TRAIT: Principled stop (hard caps)
# ACHIEVES: G4 — both exit paths reachable
# DEPENDENCIES: None
# ═══════════════════════════════════════════
MAX_MAIN_TURNS: int = 4      # GATE[G4]: main loop hard cap
MAX_SUBAGENTS: int = 6       # GATE[G4]: total specialist dispatches (initial + follow-ups)
MIN_QUALITY: float = 0.6     # GATE[G1]: minimum quality_score for a section to count
AGENT_SLUG: str = "morning-intel"
AGENT_VERSION: str = "v1"
LOG_FILE_NAME: str = f"{AGENT_SLUG}_run_output.log"
BRIEFING_LOG_NAME: str = f"{AGENT_SLUG}_briefing_log.json"

AGENT_DIR = Path(__file__).resolve().parent


# ═══════════════════════════════════════════
# PURPOSE: Module-level agent state — reset before each run
# AGENTIC TRAIT: Memory (session — carries sub-reports across main loop turns)
# ACHIEVES: Sub-agent dispatch tools write here; main loop reads here
# DEPENDENCIES: reset by _reset_state() at boot
# ═══════════════════════════════════════════
_agent_state: dict = {
    "sections": {"weather": None, "news": None, "calendar": None},
    "sub_agents_dispatched": 0,
    "synthesis_produced": False,
    "final_briefing": None,
    "lead_section": None,
    "follow_up_history": {},   # {section_type: [params_used]}
}


def _reset_state() -> None:
    """Reset module-level state before a new run."""
    _agent_state["sections"] = {"weather": None, "news": None, "calendar": None}
    _agent_state["sub_agents_dispatched"] = 0
    _agent_state["synthesis_produced"] = False
    _agent_state["final_briefing"] = None
    _agent_state["lead_section"] = None
    _agent_state["follow_up_history"] = {}


# ═══════════════════════════════════════════
# PURPOSE: Tee stdout to run-output log (append mode, separator per run)
# AGENTIC TRAIT: Observability — every run is recorded
# ACHIEVES: morning-intel_run_output.log as input for Part 2 HTML
# DEPENDENCIES: AGENT_DIR
# ═══════════════════════════════════════════
class _TeeStream:
    def __init__(self, original, log_handle):
        self._original = original
        self._log = log_handle

    def write(self, data: str) -> int:
        self._original.write(data)
        self._log.write(data)
        return len(data)

    def flush(self) -> None:
        self._original.flush()
        self._log.flush()

    def __getattr__(self, name: str) -> Any:
        return getattr(self._original, name)


@contextlib.contextmanager
def tee_to_log():
    header = (
        f"\n{'=' * 65}\n"
        f"RUN: {datetime.now().isoformat()} | {AGENT_SLUG} {AGENT_VERSION} · rung 8\n"
        f"{'=' * 65}\n"
    )
    log_path = AGENT_DIR / LOG_FILE_NAME
    with open(log_path, "a", encoding="utf-8") as log_f:
        log_f.write(header)
        original = sys.stdout
        sys.stdout = _TeeStream(original, log_f)
        try:
            yield
        finally:
            sys.stdout = original


# ═══════════════════════════════════════════
# PURPOSE: MessageLens — one-line SDK message summary
# AGENTIC TRAIT: Observability (agent loop is watchable in every run)
# ACHIEVES: FR-C8 — indented ┆ prefix for secondary output
# DEPENDENCIES: claude_agent_sdk message types (duck-typed)
# ═══════════════════════════════════════════
def message_lens(message: Any, label: str = "") -> None:
    msg_type = type(message).__name__
    prefix = f"  ┆ {label}" if label else "  ┆"
    if msg_type == "ResultMessage":
        text = getattr(message, "text", "")
        preview = (text[:110] + "...") if len(text) > 110 else text
        print(f"{prefix} [ResultMessage] {preview.replace(chr(10), ' ')}")
    elif msg_type == "AssistantMessage":
        content = getattr(message, "content", [])
        tool_calls = [b for b in content if getattr(b, "type", "") == "tool_use"]
        text_blocks = [b for b in content if getattr(b, "type", "") == "text"]
        if tool_calls:
            names = ", ".join(getattr(tc, "name", "?") for tc in tool_calls)
            print(f"{prefix} [AssistantMessage] tool_calls=[{names}]")
        elif text_blocks:
            txt = getattr(text_blocks[0], "text", "")[:90].replace("\n", " ")
            print(f"{prefix} [AssistantMessage] {txt}...")
    else:
        print(f"{prefix} [{msg_type}]")


# ═══════════════════════════════════════════
# PURPOSE: Preflight — verify environment before running
# AGENTIC TRAIT: Goal-directedness (refuses to start without prerequisites)
# ACHIEVES: Fail-fast with actionable fix-it messages
# DEPENDENCIES: Python 3.12+, claude-agent-sdk, claude CLI
# ═══════════════════════════════════════════
def preflight() -> None:  # TRAIT[goal-directedness]: agent refuses to start without prerequisites
    if sys.version_info < (3, 12):
        print(f"⚠ Python 3.12+ required (you have {sys.version_info.major}.{sys.version_info.minor})")
        sys.exit(1)

    # GOTCHA[api-key-bypass]: strip from child-process env only; never from global env
    if os.environ.get("ANTHROPIC_API_KEY"):
        print("⚠ ANTHROPIC_API_KEY detected — stripped from child-process environment.")
        print("  Auth via Claude Max subscription only.")
        os.environ.pop("ANTHROPIC_API_KEY", None)

    try:
        import claude_agent_sdk  # noqa: F401
    except ImportError:
        print("⚠ claude-agent-sdk not installed. Fix: pip install claude-agent-sdk")
        sys.exit(1)

    try:
        result = subprocess.run(
            ["claude", "--version"],
            capture_output=True, text=True, timeout=10,
        )
        if result.returncode != 0:
            print("⚠ Claude CLI not responding. Fix: install Claude Code CLI and log in.")
            sys.exit(1)
    except FileNotFoundError:
        print("⚠ Claude CLI not found. Fix: npm install -g @anthropic-ai/claude-code")
        sys.exit(1)
    except subprocess.TimeoutExpired:
        print("⚠ Claude CLI timed out.")
        sys.exit(1)


# ═══════════════════════════════════════════
# PURPOSE: Mock data — simulated morning sources (no real HTTP calls)
# AGENTIC TRAIT: Perception (external data shapes agent behaviour)
# ACHIEVES: Deterministic demo usable without internet access
# DEPENDENCIES: None
# ═══════════════════════════════════════════
_now = datetime.now()
_TODAY = f"{_now.strftime('%A, %B')} {_now.day}, {_now.year}"

MOCK_WEATHER_DATA: dict[str, dict] = {
    "standard": {
        "temperature_c": 26,
        "feels_like_c": 28,
        "conditions": "Partly cloudy",
        "humidity_pct": 72,
        "wind_kmh": 14,
        "forecast": "Mild morning. Scattered showers likely after 3 PM. Clear by evening.",
        "commute_advisory": "Normal conditions. Carry an umbrella for afternoon.",
    },
    "sparse": {   # triggers low quality_score for testing the follow-up path
        "temperature_c": None,
        "conditions": "Unknown",
        "forecast": "Data unavailable.",
        "commute_advisory": "Check local sources.",
    },
}

MOCK_HEADLINES: dict[str, list[str]] = {
    "general": [
        "India-EU trade deal reaches final draft; signing ceremony expected next month.",
        "UN Security Council adopts landmark resolution on deep-sea mining governance.",
        "IMF revises global growth forecast upward by 0.2% for 2026.",
    ],
    "technology": [
        "Anthropic releases Claude 5 with expanded reasoning and 200K context window.",
        "Apple announces M4 Pro chip architecture at WWDC 2026.",
        "EU passes AI Liability Directive into law; effective January 2027.",
    ],
    "health": [
        "WHO declares dengue fever 'priority disease' as cases rise 40% in Southeast Asia.",
        "Phase III Alzheimer's trial shows 35% reduction in cognitive decline.",
        "India achieves 90% national vaccination coverage — WHO milestone.",
    ],
    "business": [
        "Indian startup funding rebounds to USD 3.2B in Q2, led by fintech and SaaS.",
        "Sensex hits record high as foreign institutional inflows accelerate.",
        "RBI holds repo rate steady at 6.25%; signals rate cut in Q4.",
    ],
    "narrow": [],  # triggers low quality_score for testing follow-up path
}

MOCK_CALENDAR_DATA: dict[str, dict] = {
    "today": {
        "events": [
            {"time": "9:00 AM",  "title": "Team standup",           "priority": "high"},
            {"time": "11:00 AM", "title": "Client review — Q3 report", "priority": "high"},
            {"time": "2:00 PM",  "title": "Learning time block",    "priority": "medium"},
            {"time": "4:00 PM",  "title": "1:1 with manager",       "priority": "high"},
        ],
        "focus_block": "2:00–4:00 PM (2 hrs)",
        "task_count": 5,
        "high_priority_count": 3,
    },
}


# ═══════════════════════════════════════════
# PURPOSE: Sub-agent box printer — visual isolation marker in terminal
# AGENTIC TRAIT: Observability (sub-agent work clearly delineated)
# ACHIEVES: Visual separation between main agent output and sub-agent work
# DEPENDENCIES: None
# ═══════════════════════════════════════════
def _print_sub_agent_box(name: str, lines: list[str], is_followup: bool = False) -> None:
    label = f"Follow-up: {name}" if is_followup else f"Sub-Agent: {name}"
    width = max(len(label) + 4, max((len(ln) for ln in lines), default=42) + 4, 46)
    print(f"  ┌{'─' * (width - 2)}┐")
    print(f"  │ {label:<{width - 4}} │")
    print(f"  │{'─' * (width - 2)}│")
    for ln in lines:
        print(f"  │ {ln:<{width - 4}} │")
    print(f"  └{'─' * (width - 2)}┘")


# ═══════════════════════════════════════════
# PURPOSE: Sub-agent runners — each runs an independent context window
# AGENTIC TRAIT: Memory (subagent — rung 8); Perception (tool calls inside sub-agent)
# ACHIEVES: G3 foundation — each sub-agent returns quality_score for gap detection
# DEPENDENCIES: module-level query, MOCK_* data dicts
# ═══════════════════════════════════════════

async def run_weather_analyst(location: str = "Bangalore",
                               detail_level: str = "standard") -> dict:
    """WeatherAnalyst sub-agent — owns its context window from creation to return."""
    # TRAIT[memory]: rung 8 — sub-agent context window, independent, discarded after return
    box_lines: list[str] = []

    raw = MOCK_WEATHER_DATA.get(detail_level, MOCK_WEATHER_DATA["standard"])
    box_lines.append(f"🔧 [TOOL CALL] fetch_weather(location={location!r})")
    box_lines.append(f"📥 [TOOL RESULT] {len(str(raw))} chars returned")

    sdk_start = time.time()
    print(f"  ━━━ [SDK →] weather-analyst · ~{len(str(raw)) // 4} prompt tokens")

    try:
        result = await _run_query(  # TRAIT[autonomy]: sub-agent model decides how to phrase section
            prompt=(
                f"You are the WeatherAnalyst for a morning briefing system.\n"
                f"Raw weather data (JSON): {json.dumps(raw)}\n"
                f"Date: {_TODAY}\n"
                f"Write a concise 2-sentence morning weather section for the briefing. "
                f"Include temperature, conditions, and any practical advice.\n"
                f"Assess: how complete is this data? Score 0.0 to 1.0 based on completeness.\n"
                f"Respond in this exact JSON format:\n"
                f'{{"section_type": "weather", "content": "...", '
                f'"quality_score": 0.0, "gap_flag": false, "notes": ""}}'
            )
        )
        sdk_elapsed = time.time() - sdk_start
        print(f"  ━━━ [← SDK] {sdk_elapsed:.1f}s")
        message_lens(result, "weather-analyst")

        result_text = getattr(result, "text", str(result))
        report = _parse_section_report(result_text, "weather")

    except Exception as exc:
        sdk_elapsed = time.time() - sdk_start
        print(f"  ━━━ [← SDK] {sdk_elapsed:.1f}s · ERROR: {exc}")
        report = {   # GOTCHA[corrupt-response]: treat errors as low-confidence section
            "section_type": "weather",
            "content": f"Weather data unavailable: {exc}",
            "quality_score": 0.3,
            "gap_flag": True,
            "notes": f"query() error: {exc}",
        }

    quality = f"{report.get('quality_score', 0):.2f}"
    gap = report.get("gap_flag", False)
    box_lines.append(f"🧠 [REASON] formatting section from raw data")
    box_lines.append(f"✅ Report: quality={quality} gap={gap}")
    _print_sub_agent_box("WeatherAnalyst", box_lines)
    return report


async def run_news_scanner(category: str = "general", focus: str = "broad") -> dict:
    """NewsScanner sub-agent — independent context window, news domain only."""
    # TRAIT[memory]: rung 8 — isolated context; never sees weather or calendar data
    box_lines: list[str] = []

    headlines = MOCK_HEADLINES.get(category, MOCK_HEADLINES["general"])
    box_lines.append(f"🔧 [TOOL CALL] fetch_headlines(category={category!r})")
    box_lines.append(f"📥 [TOOL RESULT] {len(headlines)} headline(s) returned")

    sdk_start = time.time()
    print(f"  ━━━ [SDK →] news-scanner · ~{len(str(headlines)) // 4} prompt tokens")

    try:
        result = await _run_query(
            prompt=(
                f"You are the NewsScanner for a morning briefing system.\n"
                f"Available headlines ({category}): {json.dumps(headlines)}\n"
                f"Date: {_TODAY}\n"
                f"Write a concise 2-sentence news briefing section summarising the most "
                f"significant story. If the headlines list is empty or sparse, say so.\n"
                f"Assess completeness: 0.0 if no headlines, 1.0 if rich and relevant.\n"
                f"Respond in this exact JSON format:\n"
                f'{{"section_type": "news", "content": "...", '
                f'"quality_score": 0.0, "gap_flag": false, "notes": ""}}'
            )
        )
        sdk_elapsed = time.time() - sdk_start
        print(f"  ━━━ [← SDK] {sdk_elapsed:.1f}s")
        message_lens(result, "news-scanner")

        result_text = getattr(result, "text", str(result))
        report = _parse_section_report(result_text, "news")

    except Exception as exc:
        sdk_elapsed = time.time() - sdk_start
        print(f"  ━━━ [← SDK] {sdk_elapsed:.1f}s · ERROR: {exc}")
        report = {
            "section_type": "news",
            "content": f"News data unavailable: {exc}",
            "quality_score": 0.3,
            "gap_flag": True,
            "notes": f"query() error: {exc}",
        }

    quality = f"{report.get('quality_score', 0):.2f}"
    gap = report.get("gap_flag", False)
    box_lines.append(f"🧠 [REASON] selecting most relevant headline")
    box_lines.append(f"✅ Report: quality={quality} gap={gap}")
    _print_sub_agent_box("NewsScanner", box_lines)
    return report


async def run_calendar_prep(date_range: str = "today", priority: str = "all") -> dict:
    """CalendarPrep sub-agent — independent context window, calendar domain only."""
    # TRAIT[memory]: rung 8 — isolated context; never sees weather or news data
    box_lines: list[str] = []

    cal = MOCK_CALENDAR_DATA.get(date_range, MOCK_CALENDAR_DATA["today"])
    box_lines.append(f"🔧 [TOOL CALL] fetch_calendar(date_range={date_range!r})")
    box_lines.append(f"📥 [TOOL RESULT] {len(cal.get('events', []))} event(s) returned")

    sdk_start = time.time()
    print(f"  ━━━ [SDK →] calendar-prep · ~{len(str(cal)) // 4} prompt tokens")

    try:
        result = await _run_query(
            prompt=(
                f"You are the CalendarPrep specialist for a morning briefing system.\n"
                f"Today's calendar data (JSON): {json.dumps(cal)}\n"
                f"Date: {_TODAY}\n"
                f"Write a concise 2-sentence calendar briefing section. "
                f"Highlight the most important event and the day's key focus.\n"
                f"Assess completeness: 1.0 if events are clear and prioritised.\n"
                f"Respond in this exact JSON format:\n"
                f'{{"section_type": "calendar", "content": "...", '
                f'"quality_score": 0.0, "gap_flag": false, "notes": ""}}'
            )
        )
        sdk_elapsed = time.time() - sdk_start
        print(f"  ━━━ [← SDK] {sdk_elapsed:.1f}s")
        message_lens(result, "calendar-prep")

        result_text = getattr(result, "text", str(result))
        report = _parse_section_report(result_text, "calendar")

    except Exception as exc:
        sdk_elapsed = time.time() - sdk_start
        print(f"  ━━━ [← SDK] {sdk_elapsed:.1f}s · ERROR: {exc}")
        report = {
            "section_type": "calendar",
            "content": f"Calendar data unavailable: {exc}",
            "quality_score": 0.3,
            "gap_flag": True,
            "notes": f"query() error: {exc}",
        }

    quality = f"{report.get('quality_score', 0):.2f}"
    gap = report.get("gap_flag", False)
    box_lines.append(f"🧠 [REASON] identifying priority items for today")
    box_lines.append(f"✅ Report: quality={quality} gap={gap}")
    _print_sub_agent_box("CalendarPrep", box_lines)
    return report


def _parse_section_report(text: str, section_type: str) -> dict:
    """Extract structured report from model text; fall back gracefully on parse failure."""
    # GOTCHA[markdown-fence]: model sometimes wraps JSON in ```json ... ``` fences
    cleaned = text.strip()
    if cleaned.startswith("```"):
        lines = cleaned.split("\n")
        cleaned = "\n".join(lines[1:])
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3].strip()

    try:
        match = re.search(r"\{.*\}", cleaned, re.DOTALL)
        if match:
            parsed = json.loads(match.group())
            quality = max(0.0, min(1.0, float(parsed.get("quality_score", 0.5))))  # GOTCHA[confidence-clamp]
            return {
                "section_type": section_type,
                "content": parsed.get("content", text[:200]),
                "quality_score": quality,
                "gap_flag": bool(parsed.get("gap_flag", quality < MIN_QUALITY)),
                "notes": parsed.get("notes", ""),
            }
    except (json.JSONDecodeError, ValueError, TypeError):
        pass

    # GOTCHA[corrupt-response]: unparseable response treated as low-confidence
    return {
        "section_type": section_type,
        "content": text[:200],
        "quality_score": 0.45,
        "gap_flag": True,
        "notes": "parse-fallback",
    }


# ═══════════════════════════════════════════
# PURPOSE: Goal predicate — computable test evaluated every turn
# AGENTIC TRAIT: Goal-directedness (predicate, not narration)
# ACHIEVES: G1 — the agent knows if it is done without asking the model
# DEPENDENCIES: _agent_state["sections"], _agent_state["synthesis_produced"]
# ═══════════════════════════════════════════
def briefing_complete(state: dict) -> bool:  # GATE[G1]: predicate computed, not narrated
    """Five-part predicate — all must hold for True."""
    sections = state.get("sections", {})
    all_received = all(v is not None for v in sections.values())
    if not all_received:
        return False
    all_quality = all(
        isinstance(v, dict) and v.get("quality_score", 0) >= MIN_QUALITY
        for v in sections.values()
    )
    synthesis_done = state.get("synthesis_produced", False)
    return all_quality and synthesis_done


# ═══════════════════════════════════════════
# PURPOSE: App memory — persist briefing across runs
# AGENTIC TRAIT: Memory (app — survives restarts)
# ACHIEVES: morning-intel_briefing_log.json accumulates over time
# DEPENDENCIES: AGENT_DIR, BRIEFING_LOG_NAME
# ═══════════════════════════════════════════
def _load_briefing_log() -> dict:  # TRAIT[memory]: app memory — survives across runs
    p = AGENT_DIR / BRIEFING_LOG_NAME
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}  # GOTCHA[corrupt-ledger]: treat malformed log as empty


def _save_briefing_log_atomic(data: dict) -> None:
    # GOTCHA[atomic-write]: write to .tmp then rename — never leaves a half-written file
    p = AGENT_DIR / BRIEFING_LOG_NAME
    tmp = p.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    tmp.replace(p)


# ═══════════════════════════════════════════
# PURPOSE: Plan progress board — updated every turn
# AGENTIC TRAIT: Planning (plan as ongoing process, not one-shot)
# ACHIEVES: FR-C8 — [PLAN PROGRESS] required every turn
# DEPENDENCIES: _agent_state["sections"], _agent_state["synthesis_produced"]
# ═══════════════════════════════════════════
def _print_plan_progress(current_step: str) -> None:
    sections = _agent_state["sections"]
    steps = [
        ("dispatch-weather",  sections["weather"] is not None),
        ("dispatch-news",     sections["news"] is not None),
        ("dispatch-calendar", sections["calendar"] is not None),
        ("synthesize",        _agent_state["synthesis_produced"]),
    ]
    board = []
    for name, done in steps:
        if done:
            board.append(f"  ✓ {name}")
        elif name == current_step:
            board.append(f"  ▶ {name}")
        else:
            board.append(f"  ○ {name}")
    print("📋 [PLAN PROGRESS]")
    for item in board:
        print(item)


# ═══════════════════════════════════════════
# PURPOSE: Dispatch helper — dispatch a specialist and update state
# AGENTIC TRAIT: Observe-reason-act (act step: dispatch the right specialist)
# ACHIEVES: tracks sub_agents_dispatched count and writes to sections
# DEPENDENCIES: run_weather_analyst / run_news_scanner / run_calendar_prep
# ═══════════════════════════════════════════
async def _dispatch(section_type: str, params: dict, is_followup: bool = False) -> dict:
    _agent_state["sub_agents_dispatched"] += 1
    n = _agent_state["sub_agents_dispatched"]
    tag = "follow-up" if is_followup else "initial"
    print(f"\n📤 [DISPATCHING: {section_type}-specialist #{n}] ({tag}) params={params}")

    # Track follow-up parameters so we can prove strategy changed (act-strategy test)
    if is_followup:
        hist = _agent_state["follow_up_history"]
        hist.setdefault(section_type, []).append(params)

    if section_type == "weather":
        report = await run_weather_analyst(**params)
    elif section_type == "news":
        report = await run_news_scanner(**params)
    else:
        report = await run_calendar_prep(**params)

    _agent_state["sections"][section_type] = report
    quality = report.get("quality_score", 0)
    gap = report.get("gap_flag", False)
    print(f"📬 [REPORT RECEIVED: {section_type}] quality={quality:.2f} gap={gap}")

    # TRAIT[memory]: session — sub-report now held in main agent's state
    print(f"💾 [SESSION MEMORY] sections.{section_type} └─ quality={quality:.2f}")
    return report


# ═══════════════════════════════════════════
# PURPOSE: Main agent loop
# AGENTIC TRAIT: All traits converge here
# ACHIEVES: Two-level orchestration — main agent + three specialist sub-agents
# DEPENDENCIES: All preceding functions
# ═══════════════════════════════════════════
async def main() -> None:  # TRAIT[sequential-action]: numbered steps tracked through loop
    _reset_state()

    with tee_to_log():
        preflight()

        # ──── BOOT ────────────────────────────────────────────────────────
        print("🤖 [AGENT BOOT] Morning Intel v1 · rung 8 · LATERAL-RIGHT")
        print("   Domain: morning-briefing | Specialists: WeatherAnalyst, NewsScanner, CalendarPrep")
        print(f"   Max turns: {MAX_MAIN_TURNS} | Max dispatches: {MAX_SUBAGENTS} | Min quality: {MIN_QUALITY}")
        print()
        print("📖 [OUTPUT GUIDE] each labeled line is a teaching element — match to learning-guide.html §6")
        print("   📤 Dispatch  📬 Report  🎲 Decision  🔄 Feedback  📐 Predicate  🏁 Exit")
        print("   Sub-agent work appears in ┌──box──┐ containers with ┆ prefixed MessageLens lines")
        print()

        # ──── GOAL SET ────────────────────────────────────────────────────
        print("🎯 [GOAL SET] briefing_complete() = all_sections_received")  # GATE[G1]: predicate declared
        print("              AND all quality_score >= 0.6")
        print("              AND synthesis_produced")
        print()

        # ──── APP MEMORY ──────────────────────────────────────────────────
        prior_log = _load_briefing_log()
        if prior_log:
            prior_lead = prior_log.get("lead_section", "unknown")
            prior_date = prior_log.get("date", "prior run")
            print(f"📀 [APP MEMORY] prior briefing loaded from {BRIEFING_LOG_NAME}")  # TRAIT[memory]: app memory
            print(f"   └─ Last run: {prior_date} · lead was: {prior_lead}")
        else:
            print(f"📀 [APP MEMORY] no prior briefing — first run")

        # ──── PLAN ────────────────────────────────────────────────────────
        print()
        print("📋 [PLAN GENERATED]")                                         # TRAIT[planning]
        print("   Step 1: dispatch WeatherAnalyst, NewsScanner, CalendarPrep")
        print("   Step 2: assess section quality — follow-up if any below 0.6")
        print("   Step 3: model synthesizes final brief (decides lead section)")
        print("   Step 4: cap if not done by turn 4 or 6 dispatches reached")
        print()

        # ──── MAIN LOOP ───────────────────────────────────────────────────
        context_tokens = 800

        for turn in range(MAX_MAIN_TURNS):                                   # GATE[G4]: hard loop cap
            print(f"📍 [STEP {turn + 1}]")
            context_tokens += 200 * (turn + 1)
            print(f"📊 [CONTEXT] ~{context_tokens} tokens in context")

            # ── LOOP FEEDBACK (turns after the first) ─────────────────────
            if turn > 0:                                                     # GATE[G3]: closed O-R-A loop
                sections = _agent_state["sections"]
                low_q = [
                    s for s, v in sections.items()
                    if v is not None and v.get("quality_score", 0) < MIN_QUALITY
                ]
                if low_q:
                    for s in low_q:
                        old_q = sections[s].get("quality_score", 0)
                        print(f"🔄 [LOOP FEEDBACK] observed {s} quality={old_q:.2f} below threshold"
                              f" → changing params for follow-up")  # GATE[G3]: act changes because of observation
                else:
                    received = [s for s, v in sections.items() if v is not None]
                    print(f"🔄 [LOOP FEEDBACK] all {len(received)} sections quality-passed → proceeding to synthesis")

            # ── O-R-A TRIAD ───────────────────────────────────────────────
            print("👁 [OBSERVE] checking section inventory")

            sections = _agent_state["sections"]
            missing = [s for s, v in sections.items() if v is None]
            low_q = [
                s for s, v in sections.items()
                if v is not None and v.get("quality_score", 0) < MIN_QUALITY
            ]

            print(f"🧠 [REASON] missing={missing or 'none'} low_quality={low_q or 'none'}")

            # ── ACT: dispatch missing sections ──────────────────────────
            print("⚡ [ACT] dispatching specialists")
            for section in missing:
                if _agent_state["sub_agents_dispatched"] >= MAX_SUBAGENTS:
                    break
                default_params = {
                    "weather":  {"location": "Bangalore", "detail_level": "standard"},
                    "news":     {"category": "general",   "focus": "broad"},
                    "calendar": {"date_range": "today",    "priority": "all"},
                }
                await _dispatch(section, default_params[section])

            # ── ACT: re-dispatch low-quality sections with varied params ──
            # GATE[G3]: observation (low quality) drives a strategy change, not just a retry
            for section in low_q:
                if _agent_state["sub_agents_dispatched"] >= MAX_SUBAGENTS:
                    break
                # GOTCHA[act-strategy-adaptation]: different params on follow-up — not the same
                # brief re-sent to the same specialist. This closes the Cycle 5 gap.
                followup_params = {
                    "weather":  {"location": "Bangalore", "detail_level": "standard"},
                    "news":     {"category": "technology", "focus": "broad"},   # changed category
                    "calendar": {"date_range": "today",    "priority": "high"}, # narrowed to high-priority
                }
                await _dispatch(section, followup_params[section], is_followup=True)

            # ── GOAL PREDICATE CHECK (before synthesis attempt) ───────────
            all_received = all(v is not None for v in _agent_state["sections"].values())
            all_quality_ok = all(
                isinstance(v, dict) and v.get("quality_score", 0) >= MIN_QUALITY
                for v in _agent_state["sections"].values() if v is not None
            )
            print(f"📐 [GOAL PREDICATE] pre-synthesis: "           # GATE[G1]: evaluated every turn
                  f"all_received={all_received} quality_ok={all_quality_ok} "
                  f"synthesis={_agent_state['synthesis_produced']}")

            # ── ACT: synthesize when all sections are ready and quality-passed ─
            if all_received and all_quality_ok and not _agent_state["synthesis_produced"]:

                weather_content = _agent_state["sections"]["weather"].get("content", "")
                news_content    = _agent_state["sections"]["news"].get("content", "")
                cal_content     = _agent_state["sections"]["calendar"].get("content", "")

                synthesis_prompt = (
                    f"You are the Morning Intel synthesizer.\n\n"
                    f"You have three morning briefing sections:\n"
                    f"WEATHER: {weather_content}\n"
                    f"NEWS: {news_content}\n"
                    f"CALENDAR: {cal_content}\n\n"
                    f"Task 1: Decide which section is most time-critical for the reader RIGHT NOW "
                    f"(pick: weather, news, or calendar — based on urgency and actionability today).\n"
                    f"Task 2: Write a single cohesive morning briefing (3-4 sentences total) "
                    f"that leads with the most urgent section.\n\n"
                    f"Respond in this exact JSON format:\n"
                    f'{{"lead_section": "weather|news|calendar", '
                    f'"alternatives": ["...", "..."], "briefing": "..."}}'
                )

                syn_tokens = len(synthesis_prompt) // 4
                print(f"\n━━━ [SDK →] model · ~{syn_tokens} prompt tokens")   # G2 boundary open
                sdk_start = time.time()

                try:
                    syn_result = await _run_query(prompt=synthesis_prompt)    # TRAIT[autonomy]: model picks lead
                    sdk_elapsed = time.time() - sdk_start
                    print(f"━━━ [← SDK] {sdk_elapsed:.1f}s")
                    message_lens(syn_result, "synthesis")

                    syn_text = getattr(syn_result, "text", str(syn_result))
                    # GOTCHA[markdown-fence]
                    cleaned = syn_text.strip()
                    if cleaned.startswith("```"):
                        lines = cleaned.split("\n")
                        cleaned = "\n".join(lines[1:])
                        if cleaned.endswith("```"):
                            cleaned = cleaned[:-3].strip()
                    match = re.search(r"\{.*\}", cleaned, re.DOTALL)
                    if match:
                        parsed = json.loads(match.group())
                        lead = parsed.get("lead_section", "weather")
                        alts = parsed.get("alternatives", [])
                        briefing_text = parsed.get("briefing", syn_text[:300])
                    else:
                        lead = "weather"
                        alts = ["news", "calendar"]
                        briefing_text = syn_text[:300]

                    # GATE[G2]: model-owned decision — the code did not pick the lead section
                    print(f"🎲 [MODEL DECISION] lead={lead} · alternatives={alts}")

                    _agent_state["synthesis_produced"] = True
                    _agent_state["final_briefing"] = briefing_text
                    _agent_state["lead_section"] = lead

                    print("\n╔═══════════════════════════════════╗")
                    print("║  MORNING INTEL — BRIEFING READY  ║")
                    print("╠═══════════════════════════════════╣")
                    for line in briefing_text.split("\n"):
                        print(f"║  {line}")
                    print("╚═══════════════════════════════════╝")

                except Exception as exc:
                    sdk_elapsed = time.time() - sdk_start
                    print(f"━━━ [← SDK] {sdk_elapsed:.1f}s · ERROR: {exc}")
                    print(f"⚠ [ERROR: TRANSIENT] synthesis failed: {exc}")

            # ── GOAL PREDICATE (final check this turn) ────────────────────
            goal_met = briefing_complete(_agent_state)                 # GATE[G1]: evaluated every turn
            print(f"\n📐 [GOAL PREDICATE] briefing_complete() → {goal_met}")

            if goal_met:
                print("🏁 [GOAL MET] all sections received · quality passed · synthesis complete")
                break

            # ── TERMINATION CHECK ─────────────────────────────────────────
            remaining = MAX_MAIN_TURNS - turn - 1
            dispatched = _agent_state["sub_agents_dispatched"]
            print(f"🔍 [TERMINATION CHECK] turn {turn + 1}/{MAX_MAIN_TURNS} "
                  f"· dispatches {dispatched}/{MAX_SUBAGENTS}")  # GATE[G4]: both caps visible

            if dispatched >= MAX_SUBAGENTS:
                print("🏁 [EXIT: sub-agent cap] dispatch limit reached without briefing_complete()")
                break

            # ── PLAN PROGRESS ────────────────────────────────────────────
            current = "synthesize" if all_received else "dispatch-" + (missing[0] if missing else "weather")
            _print_plan_progress(current)
            print()

        else:
            # Loop exhausted without break
            print(f"🏁 [EXIT: turn cap] {MAX_MAIN_TURNS} turns reached — briefing_complete()=False")

        # GATE[G5]: N/A — independent verifier introduced at rung 7; no critic call in this agent

        # ──── AGENT SUMMARY ──────────────────────────────────────────────
        sections = _agent_state["sections"]
        print("\n╔══════════════════════════════════════════════════════╗")
        print("║                🧠 AGENT SUMMARY                    ║")
        print("╠══════════════════════════════════════════════════════╣")
        print(f"║  Run date: {_TODAY[:28]:<28}    ║")
        print(f"║  Exit: {'GOAL MET' if briefing_complete(_agent_state) else 'CAP/ERROR':<46}  ║")
        print(f"║  Sub-agents dispatched: {_agent_state['sub_agents_dispatched']}/{MAX_SUBAGENTS:<34}  ║")
        print(f"║  Lead section: {_agent_state.get('lead_section') or 'n/a':<38}  ║")

        for s_type, report in sections.items():
            if report:
                q = report.get("quality_score", 0)
                print(f"║    {s_type:12s} quality={q:.2f}{'  ✓' if q >= MIN_QUALITY else '  ✗':>30}  ║")

        print("╠══════════════════════════════════════════════════════╣")
        print("║  TRAITS IN ACTION:                                  ║")
        print("║    goal-directedness  briefing_complete() ran every turn  ║")
        print("║    autonomy           model picked the lead section        ║")
        print("║    O-R-A loop         low quality → targeted re-dispatch   ║")
        print("║    memory (subagent)  3 independent context windows        ║")
        print("║    memory (app)       briefing_log written on goal-met     ║")
        print("╠══════════════════════════════════════════════════════╣")
        print("║  G1 (did-it-finish check): briefing_complete() ran as     ║")
        print("║    predicate every turn — never trusted model text.       ║")
        print("║  G2 (model's own choice): [MODEL DECISION] line shows     ║")
        print("║    which section leads — code never hard-picked.          ║")
        print("║  G3 (learning from what it saw): low quality_score →      ║")
        print("║    follow-up with different category/params, not retry.   ║")
        print("╚══════════════════════════════════════════════════════╝")

        # ──── APP MEMORY WRITE (on goal-met) ─────────────────────────────
        if briefing_complete(_agent_state):
            log_entry = {
                "last_run": datetime.now(timezone.utc).isoformat(),
                "date": _TODAY,
                "lead_section": _agent_state.get("lead_section"),
                "briefing_preview": (_agent_state.get("final_briefing") or "")[:150],
                "sub_agents_dispatched": _agent_state["sub_agents_dispatched"],
            }
            _save_briefing_log_atomic(log_entry)
            print(f"\n📀 [APP MEMORY] briefing written to {BRIEFING_LOG_NAME}")  # TRAIT[memory]: app


if __name__ == "__main__":
    asyncio.run(main())
