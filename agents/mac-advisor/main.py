"""
Mac Advisor Agent v1 — main.py
Cycle 4 · SDK Rung 5 (allowed_tools / disallowed_tools / permission_mode) · FORWARD
Domain: consumer-research

AGENTIC TRAITS DEMONSTRATED
──────────────────────────────────────────────────────────────────────
  goal-directedness    is_research_complete() + is_recommendation_ready() each step
  autonomy             model picks research tools each turn; phase boundary is code-enforced
  observe-reason-act   thermal conflict triggers detect → replan → resolve cycle
  perception           5 mock tools simulate real research sources
  planning             5-step plan tracked across research + synthesis phases
  memory (SESSION)     ClaudeSDKClient per phase (rung 3 carried)
  memory (APP)         research_notes.json persists findings across runs
  memory (CHAIN)       [TOOL CHAIN] N shows multi-tool sequences per response
  tool-selection       @tool + create_sdk_mcp_server (rung 4 carried)
  sequential-action    research steps feed synthesis; each tool result shapes next call
  termination          predicate exits + hard caps on both phases (rung 5 adds phase gates)

Control plane:
  - Which research tool to call next   → model (rung 4/5 autonomy)
  - Phase boundary (research→synthesis) → code (is_research_complete() must be True)
  - Tool palette per phase              → code (allowed_tools + permission_mode; rung 5)
  - Hard cap                            → code (MAX_RESEARCH_TURNS / MAX_SYNTHESIS_TURNS)

Rung 5 key insight: ALL_TOOLS registered in one MCP server; per-phase allowed_tools
restricts which subset the model can call. The model cannot call synthesize_recommendation
during research; cannot call search_specs during synthesis. permission_mode="dontAsk"
enforces this — any tool not in allowed_tools is denied, not just unprompted.

Termination labels:
  GOAL MET (recommendation ready)  ·  EXIT: research cap  ·  EXIT: synthesis cap

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
# AGENTIC TRAIT: goal-directedness (predicates read these); termination (caps)
# ACHIEVES: change behaviour without hunting through logic
# DEPENDENCIES: none
# ═══════════════════════════════════════════
MAX_RESEARCH_TURNS: int = 8
MAX_SYNTHESIS_TURNS: int = 3
MAX_TOOL_CALLS_TOTAL: int = 24
CONFIDENCE_THRESHOLD: float = 0.8
LOG_FILE: str = "mac-advisor_run_output.log"
NOTES_FILE: str = "research_notes.json"
MODEL_ID: str = "claude-opus-4-8"
AGENT_VERSION: str = "v1"

# ═══════════════════════════════════════════
# PURPOSE: Rung 5 — phase-gated tool palettes
# AGENTIC TRAIT: autonomy (model sees only what we allow); tool-selection
# ACHIEVES: enforces workflow ordering at the SDK level, not via system-prompt instructions
# DEPENDENCIES: MCP server name must match ("advisor"); used in build_options()
# ═══════════════════════════════════════════
RESEARCH_ALLOWED: list[str] = [
    "mcp__advisor__search_specs",
    "mcp__advisor__check_price",
    "mcp__advisor__analyze_thermal",
    "mcp__advisor__compare_variants",
]
SYNTHESIS_ALLOWED: list[str] = [
    "mcp__advisor__synthesize_recommendation",
]

# ═══════════════════════════════════════════
# PURPOSE: System prompts per phase — guide the model within its allowed tool set
# AGENTIC TRAIT: goal-directedness (each prompt anchors to the phase's goal)
# ACHIEVES: model knows what to do in each phase; system prompt + allowed_tools work together
# DEPENDENCIES: RESEARCH_ALLOWED / SYNTHESIS_ALLOWED define what the model can actually call
# ═══════════════════════════════════════════
RESEARCH_SYSTEM_PROMPT = (
    "You are Mac Advisor in RESEARCH PHASE.\n"
    "Goal: gather all evidence needed to recommend the best MacBook Pro 16\" M4 variant\n"
    "for a software developer + AI practitioner workload, Indian market.\n\n"
    "Work through these areas using available tools:\n"
    "1. search_specs for M4 Base, M4 Pro (and M4 Max if budget context warrants).\n"
    "2. check_price for key SKUs: m4_base_16gb, m4_pro_24gb.\n"
    "3. analyze_thermal for your leading candidate — test multiple workload parameters\n"
    "   ('general' first, then 'ai_inference') to cross-check sources.\n"
    "4. compare_variants on 'ml_performance' and 'cost_value' dimensions.\n"
    "5. Before finishing: verify price for your top candidate once more.\n\n"
    "Chain multiple tool calls per response when efficient.\n"
    "When you have data across all four areas, say 'RESEARCH COMPLETE' and summarize findings."
)

SYNTHESIS_SYSTEM_PROMPT = (
    "You are Mac Advisor in SYNTHESIS PHASE.\n"
    "Research is complete. You have one tool: synthesize_recommendation(findings, confidence).\n"
    "- findings: a concise summary of specs, pricing, thermal verdict, comparison.\n"
    "- confidence: float 0.0-1.0. Set >= 0.8 only when all four research areas are covered\n"
    "  and any conflicts are resolved.\n\n"
    "Call synthesize_recommendation once with your full findings and confidence score."
)

# ═══════════════════════════════════════════
# PURPOSE: Mock research databases — realistic data for deterministic demo
# AGENTIC TRAIT: perception (what the tools return shapes the agent's reasoning)
# ACHIEVES: self-contained agent; no real HTTP calls needed
# DEPENDENCIES: none
# ═══════════════════════════════════════════
_SPEC_DB: dict = {
    "m4_base": {"cpu_cores": 10, "gpu_cores": 10, "memory_options": ["16GB", "32GB"],
                "benchmark_single": 3864, "benchmark_multi": 15234, "neural_engine_tops": 38,
                "best_for": "light dev, web, docs", "not_ideal_for": "large model training"},
    "m4_pro":  {"cpu_cores": 14, "gpu_cores": 20, "memory_options": ["24GB", "48GB"],
                "benchmark_single": 3941, "benchmark_multi": 19872, "neural_engine_tops": 38,
                "best_for": "software dev, LLM inference, code assistants",
                "not_ideal_for": "8h+ continuous ML training at max throughput"},
    "m4_max":  {"cpu_cores": 16, "gpu_cores": 40, "memory_options": ["48GB", "128GB"],
                "benchmark_single": 3941, "benchmark_multi": 21543, "neural_engine_tops": 38,
                "best_for": "professional ML training, 8K video, large model hosting",
                "not_ideal_for": "budget-conscious buyers"},
}

_PRICE_DB: dict = {
    "m4_base_16gb": {"price_inr": 199900},
    "m4_base_32gb": {"price_inr": 249900},
    "m4_pro_24gb":  {"price_inr": 249900, "drop_price_inr": 229900},  # price drop on 2nd call
    "m4_pro_48gb":  {"price_inr": 299900},
    "m4_max_48gb":  {"price_inr": 449900},
    "m4_max_128gb": {"price_inr": 549900},
}

_THERMAL_DB: dict = {
    "m4_pro": {
        "general":       {"throttling": "none detected",
                          "source": "Apple white paper 2025",
                          "note": "30-min burst tests; standard office workloads only"},
        "ai_inference":  {"throttling": "15-20% under sustained AI inference",
                          "source": "AnandTech independent review 2026-04",
                          "note": "onset after ~45 min continuous LLM inference run"},
        "sustained_load":{"throttling": "15-20% confirmed; intermittent use unaffected",
                          "source": "cross-reference: AnandTech 2026 + Bare Feats 2026",
                          "note": "RESOLVED — two labs agree. Daily dev: unaffected. 8h+ ML: 15-20% reduction."},
    },
    "m4_base": {
        "general":       {"throttling": "none detected", "source": "Apple white paper 2025",
                          "note": "within rated TDP"},
        "ai_inference":  {"throttling": "5% under extended Neural Engine tasks",
                          "source": "PassMark 2026", "note": "smaller die runs cooler"},
    },
    "m4_max": {
        "general":       {"throttling": "none — sustained performance flat",
                          "source": "AnandTech 2026",
                          "note": "higher power envelope prevents throttle"},
        "ai_inference":  {"throttling": "none — flat sustained performance",
                          "source": "AnandTech 2026 + Bare Feats 2026",
                          "note": "best sustained ML throughput; recommended for 8h+ training"},
    },
}

_COMPARE_DB: dict = {
    ("m4_base", "m4_pro", "ml_performance"):
        "M4 Pro is 30% faster multi-core; 2x GPU cores (20 vs 10); handles 13B models locally.",
    ("m4_pro",  "m4_max", "ml_performance"):
        "M4 Max has 2x GPU cores (40 vs 20) and higher memory bandwidth; 25-40% faster on large model inference. Cost premium ~₹2,00,000.",
    ("m4_base", "m4_pro", "cost_value"):
        "₹30,000 premium (base 16GB ₹1,99,900 → pro 24GB ₹2,29,900 at current price) buys 30% more CPU, 2x GPU, 8GB more RAM. Sound value for ML workloads.",
    ("m4_pro",  "m4_max", "cost_value"):
        "M4 Max at ₹4,49,900 vs M4 Pro at ₹2,29,900 — ₹2,20,000 premium. Justified only for daily 8h+ ML training.",
    ("m4_base", "m4_max", "ml_performance"):
        "M4 Max has 4x GPU cores; not a meaningful comparison for the stated budget.",
}

# Module-level mock state — reset before each agent run; updated by tool impls
_mock_state: dict = {}


# ═══════════════════════════════════════════
# PURPOSE: Mirror every print() to LOG_FILE for post-run Part 2 analysis
# AGENTIC TRAIT: termination — log written even on cap exit
# ACHIEVES: append-mode tee; each run has a separator header
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
    """TRAIT[termination] — mirrors stdout to LOG_FILE (append)."""
    header = (f"\n{'=' * 70}\n"
              f"RUN: {datetime.now().isoformat()} | Mac Advisor {AGENT_VERSION} · rung 5\n"
              f"{'=' * 70}\n")
    with open(LOG_FILE, "a", encoding="utf-8") as log_f:
        log_f.write(header)
        original = sys.stdout
        sys.stdout = _TeeStream(original, log_f)
        try:
            yield
        finally:
            sys.stdout = original


# ═══════════════════════════════════════════
# PURPOSE: Persistent APP memory — research_notes.json survives across runs
# AGENTIC TRAIT: memory (APP layer); perception (reads prior findings)
# ACHIEVES: a second run can skip already-completed research areas
# DEPENDENCIES: NOTES_FILE in same folder as main.py
# ═══════════════════════════════════════════
def _notes_path() -> Path:
    return Path(__file__).resolve().parent / NOTES_FILE

def _read_notes() -> dict:
    p = _notes_path()
    if not p.exists():
        return {}
    try:
        with open(p, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}  # GOTCHA[corrupt-ledger]: treat malformed file as empty

def _write_notes_atomic(data: dict) -> None:
    """TRAIT[memory] — atomic write via tmp+rename."""
    p = _notes_path()
    tmp = p.with_suffix(".json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    tmp.replace(p)  # GOTCHA[atomic-write]: never leaves half-written file


# ═══════════════════════════════════════════
# PURPOSE: Five tool implementations — the agent's research vocabulary
# AGENTIC TRAIT: tool-selection (registered via @tool; rung 4 carried)
#                perception (mock databases simulate real sources)
# ACHIEVES: rung-4 native tool registration; rung-5 phase-gated access
# DEPENDENCIES: claude_agent_sdk @tool decorator; mock databases above
# ═══════════════════════════════════════════
try:
    from claude_agent_sdk import tool as _tool, create_sdk_mcp_server as _create_server
    _IMPORT_ERROR = None
except ImportError as _exc:
    _tool = None
    _create_server = None
    _IMPORT_ERROR = _exc


def _inr(n: int) -> str:
    """Format an integer price in Indian number notation (e.g. 249900 → ₹2,49,900)."""
    s = str(n)
    if len(s) <= 3:
        return f"₹{s}"
    last3, rest = s[-3:], s[:-3]
    parts: list[str] = []
    while len(rest) > 2:
        parts.insert(0, rest[-2:])
        rest = rest[:-2]
    if rest:
        parts.insert(0, rest)
    return "₹" + ",".join(parts) + "," + last3


def _normalize_variant(v: str) -> str:
    aliases = {"pro": "m4_pro", "base": "m4_base", "max": "m4_max",
               "m4pro": "m4_pro", "m4base": "m4_base", "m4max": "m4_max"}
    v = v.lower().replace(" ", "_").replace("-", "_")
    return aliases.get(v, v)


async def _search_specs_impl(args: dict) -> dict:
    variant = _normalize_variant(args.get("variant", ""))
    data = _SPEC_DB.get(variant)
    if data is None:
        return {"content": [{"type": "text", "text":
            f"Variant '{variant}' not found. Available: {list(_SPEC_DB.keys())}"}]}
    return {"content": [{"type": "text", "text": json.dumps({"variant": variant, **data})}]}


async def _check_price_impl(args: dict) -> dict:
    variant = args.get("variant", "").lower().replace(" ", "_")
    data = _PRICE_DB.get(variant)
    if data is None:
        return {"content": [{"type": "text", "text":
            f"SKU '{variant}' not found. Available: {list(_PRICE_DB.keys())}"}]}

    key = f"price_calls_{variant}"
    n = _mock_state.get(key, 0) + 1
    _mock_state[key] = n

    # Simulate price drop on second call for m4_pro_24gb
    if n >= 2 and variant == "m4_pro_24gb" and "drop_price_inr" in data:
        drop = data["drop_price_inr"]
        old  = data["price_inr"]
        _mock_state["price_drop_pending"] = {
            "variant": variant, "old": _inr(old), "new": _inr(drop),
            "saving": _inr(old - drop)
        }
        result = {"variant": variant, "market": "India",
                  "current_price": _inr(drop),
                  "alert": f"PRICE DROP: was {_inr(old)}, now {_inr(drop)} — {_inr(old-drop)} reduction"}
    else:
        result = {"variant": variant, "market": "India",
                  "current_price": _inr(data['price_inr'])}
    return {"content": [{"type": "text", "text": json.dumps(result)}]}


async def _analyze_thermal_impl(args: dict) -> dict:
    variant  = _normalize_variant(args.get("variant", ""))
    workload = args.get("workload", "general").lower().replace(" ", "_")

    workload_map = {
        "general": "general", "standard": "general", "office": "general",
        "ai": "ai_inference", "ai_inference": "ai_inference",
        "ml": "ai_inference", "llm": "ai_inference", "inference": "ai_inference",
        "sustained": "sustained_load", "sustained_load": "sustained_load",
        "continuous": "sustained_load", "deep": "sustained_load",
    }
    w_key = workload_map.get(workload, "general")

    variant_data = _THERMAL_DB.get(variant, {})
    result_data  = variant_data.get(w_key, variant_data.get("general", {}))
    if not result_data:
        return {"content": [{"type": "text", "text": f"No thermal data for '{variant}'."}]}

    # Track history for conflict detection
    history = _mock_state.setdefault("thermal_history", {}).setdefault(variant, [])
    new_throttle = result_data.get("throttling", "")

    if history:
        prev_throttle = history[-1]["throttling"]
        is_conflict = ("none" in prev_throttle.lower()) != ("none" in new_throttle.lower())
        if is_conflict and not _mock_state.get("thermal_conflict_pending"):
            _mock_state["thermal_conflict_pending"] = {
                "variant": variant,
                "first":  {"throttling": prev_throttle, "source": history[-1]["source"]},
                "second": {"throttling": new_throttle,  "source": result_data.get("source", "")},
            }

    if w_key == "sustained_load":
        _mock_state["thermal_conflict_resolved"] = True

    history.append({"throttling": new_throttle, "workload": w_key,
                    "source": result_data.get("source", "")})

    return {"content": [{"type": "text", "text":
        json.dumps({"variant": variant, "workload_tested": w_key, **result_data})}]}


async def _compare_variants_impl(args: dict) -> dict:
    a   = _normalize_variant(args.get("variant_a", ""))
    b   = _normalize_variant(args.get("variant_b", ""))
    dim = args.get("dimension", "ml_performance").lower().replace(" ", "_")
    dim_map = {"ml": "ml_performance", "performance": "ml_performance",
               "cost": "cost_value", "value": "cost_value", "price": "cost_value"}
    d = dim_map.get(dim, dim)
    finding = _COMPARE_DB.get((a, b, d)) or _COMPARE_DB.get((b, a, d))
    if not finding:
        finding = f"No comparison data for {a} vs {b} on {d}."
    return {"content": [{"type": "text", "text":
        json.dumps({"variant_a": a, "variant_b": b, "dimension": d, "finding": finding})}]}


async def _synthesize_recommendation_impl(args: dict) -> dict:
    findings   = args.get("findings", "")
    confidence = max(0.0, min(1.0, float(args.get("confidence", 0.0))))

    if confidence < CONFIDENCE_THRESHOLD:
        return {"content": [{"type": "text", "text": json.dumps({
            "status": "insufficient_confidence",
            "confidence": confidence,
            "threshold": CONFIDENCE_THRESHOLD,
            "message": f"Confidence {confidence:.0%} below threshold. More research needed.",
        })}]}

    rec = {
        "status": "recommendation_ready",
        "confidence": confidence,
        "primary_recommendation": "MacBook Pro 16\" M4 Pro 24GB",
        "recommended_sku": "m4_pro_24gb",
        "price": "₹2,29,900",
        "rationale": [
            "30% multi-core advantage over M4 Base at ₹30,000 premium — sound value for ML workloads",
            "24GB unified memory handles 7B–13B local LLM inference without swapping",
            "Thermal throttling (15-20%) under sustained AI inference is acceptable for intermittent use",
            "M4 Max ₹2,20,000 premium only justified for daily 8h+ ML training",
        ],
        "trade_off_accepted": "15-20% sustained-inference throttle; non-issue for daily dev + AI-assisted coding",
        "buy_now_signal": "Price at recent low (₹2,29,900 vs ₹2,49,900 listed). Value window is open.",
    }
    # Store result for goal predicate
    _mock_state["synthesis_result"] = rec
    _mock_state["synthesis_confidence"] = confidence
    return {"content": [{"type": "text", "text": json.dumps(rec)}]}


# Apply @tool decorator if SDK is available; otherwise leave as plain async functions
if _tool is not None:
    search_specs_tool   = _tool("search_specs",   "Get CPU/GPU/memory specs and benchmarks for an M4 variant", {"variant": str})(_search_specs_impl)
    check_price_tool    = _tool("check_price",    "Get current Indian market price for a MacBook SKU",         {"variant": str, "market": str})(_check_price_impl)
    analyze_thermal_tool= _tool("analyze_thermal","Get throttling data for a variant under a workload",        {"variant": str, "workload": str})(_analyze_thermal_impl)
    compare_variants_tool=_tool("compare_variants","Compare two variants on a dimension (ml_performance / cost_value)", {"variant_a": str, "variant_b": str, "dimension": str})(_compare_variants_impl)
    synthesize_recommendation_tool = _tool("synthesize_recommendation", "Produce final recommendation with confidence score", {"findings": str, "confidence": float})(_synthesize_recommendation_impl)
    ALL_TOOLS = [search_specs_tool, check_price_tool, analyze_thermal_tool,
                 compare_variants_tool, synthesize_recommendation_tool]
else:
    search_specs_tool = _search_specs_impl
    check_price_tool  = _check_price_impl
    analyze_thermal_tool = _analyze_thermal_impl
    compare_variants_tool = _compare_variants_impl
    synthesize_recommendation_tool = _synthesize_recommendation_impl
    ALL_TOOLS = []


# ═══════════════════════════════════════════
# PURPOSE: Render each SDK message as one compact auditable console line
# AGENTIC TRAIT: perception — makes raw SDK traffic visible during the loop
# ACHIEVES: learning element so student sees ToolUseBlocks fire in real time
# DEPENDENCIES: called inside send_turn() only
# ═══════════════════════════════════════════
def message_lens(msg) -> str:
    name = type(msg).__name__
    if name == "AssistantMessage":
        parts = []
        for block in getattr(msg, "content", []):
            btype = type(block).__name__
            if btype == "TextBlock":
                parts.append(f"TextBlock({getattr(block,'text','')[:50]!r})")
            elif btype == "ToolUseBlock":
                parts.append(f"ToolUseBlock({getattr(block,'name','?')}, {json.dumps(getattr(block,'input',{}))[:40]})")
            elif btype == "ToolResultBlock":
                parts.append(f"ToolResultBlock(id={getattr(block,'tool_use_id','?')[:8]}…)")
            else:
                parts.append(btype)
        return f"  ┆ AssistantMessage: {(' | '.join(parts) or '(empty)')[:100]}"
    if name == "UserMessage":
        parts = [f"ToolResult(id={getattr(b,'tool_use_id','?')[:8]}…)"
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
# PURPOSE: Verify runtime environment before any agent work begins
# AGENTIC TRAIT: goal-directedness — refuses to start without valid preconditions
# ACHIEVES: clear error messages with fix-it guidance; strips API key from child env
# DEPENDENCIES: claude_agent_sdk importable; claude CLI in PATH
# ═══════════════════════════════════════════
def preflight() -> dict[str, str]:
    """GATE[G1]: validates preconditions; returns child_env (API key stripped)."""
    print("🔬 [PREFLIGHT] checking environment...")
    if sys.version_info < (3, 12):
        print(f"  [PREFLIGHT FAILED] Python 3.12+ required (got {sys.version_info.major}.{sys.version_info.minor})")
        sys.exit(1)
    print(f"  ✓ Python {sys.version_info.major}.{sys.version_info.minor}")

    if _tool is None:
        print(f"  [PREFLIGHT FAILED] claude_agent_sdk not importable: {_IMPORT_ERROR}")
        print("  Fix: pip install claude-agent-sdk>=0.2.93")
        sys.exit(1)
    print(f"  ✓ claude_agent_sdk importable · {len(ALL_TOOLS)} tools registered via @tool")
    print(f"  ✓ Research tools ({len(RESEARCH_ALLOWED)}): {', '.join(t.split('__')[-1] for t in RESEARCH_ALLOWED)}")
    print(f"  ✓ Synthesis tools ({len(SYNTHESIS_ALLOWED)}): {', '.join(t.split('__')[-1] for t in SYNTHESIS_ALLOWED)}")

    child_env = dict(os.environ)
    if "ANTHROPIC_API_KEY" in child_env:
        del child_env["ANTHROPIC_API_KEY"]
        # GOTCHA[api-key-bypass]: key would route calls through paid API, bypassing Max plan
        print("  ⚠  ANTHROPIC_API_KEY stripped from child env — using Max plan CLI auth")
    print("  ✓ preflight passed\n")
    return child_env


# ═══════════════════════════════════════════
# PURPOSE: Goal predicates — two-stage, tool-log-based stopping conditions
# AGENTIC TRAIT: goal-directedness (G1); termination criterion
# ACHIEVES: each predicate trusts tool-call log, not the model's words
#           (see GOTCHA[predicate-vs-signal] — language is unreliable as a completion signal)
# DEPENDENCIES: state dict built up by agent_loop()
# ═══════════════════════════════════════════
def is_research_complete(state: dict) -> bool:
    """GATE[G1a]: True when all four research areas have tool-call evidence."""
    return (
        len(state.get("specs_researched", [])) >= 2           # search_specs called ≥2×
        and len(state.get("prices_checked", [])) >= 1         # check_price called ≥1×
        and state.get("thermal_analyzed", False)              # analyze_thermal called ≥1×
        and state.get("thermal_conflict_resolved", False)     # conflict (if any) resolved
        and state.get("comparison_made", False)               # compare_variants called ≥1×
    )
    # GOTCHA[predicate-vs-signal]: model may say "RESEARCH COMPLETE" before all flags are True.
    # We check that text separately as a hint. It cannot satisfy this predicate — only tool calls can.


def is_recommendation_ready(state: dict) -> bool:
    """GATE[G1b]: True when synthesis tool was called with confidence ≥ threshold."""
    return (                                                   # TRAIT[goal-directedness]
        state.get("recommendation_made", False)
        and state.get("confidence", 0.0) >= CONFIDENCE_THRESHOLD
    )


# ═══════════════════════════════════════════
# PURPOSE: Build ClaudeAgentOptions with phase-specific allowed_tools (RUNG 5 showcase)
# AGENTIC TRAIT: autonomy — model can only call tools we expose per phase
# ACHIEVES: SDK-enforced workflow ordering; system prompt alone is insufficient
# DEPENDENCIES: ALL_TOOLS registered via @tool; RESEARCH_ALLOWED / SYNTHESIS_ALLOWED constants
# ═══════════════════════════════════════════
def build_options(child_env: dict, phase: str) -> Any:
    """
    GATE[rung5]: phase-gated tool palette.
    Research phase → allowed_tools=RESEARCH_ALLOWED + dontAsk → synthesis tool DENIED.
    Synthesis phase → allowed_tools=SYNTHESIS_ALLOWED + disallowed_tools + dontAsk → research tools DENIED.
    """
    from claude_agent_sdk import ClaudeAgentOptions  # TRAIT[tool-selection] rung 5
    server = _create_server(name="advisor", version="1.0.0", tools=ALL_TOOLS)

    if phase == "research":
        return ClaudeAgentOptions(
            system_prompt=RESEARCH_SYSTEM_PROMPT,
            model=MODEL_ID,
            mcp_servers={"advisor": server},
            allowed_tools=RESEARCH_ALLOWED,         # GATE[rung5]: 4 research tools visible
            permission_mode="dontAsk",              # GATE[rung5]: synthesize_recommendation → DENIED
            env=child_env,
        )
    else:  # synthesis
        return ClaudeAgentOptions(
            system_prompt=SYNTHESIS_SYSTEM_PROMPT,
            model=MODEL_ID,
            mcp_servers={"advisor": server},
            allowed_tools=SYNTHESIS_ALLOWED,        # GATE[rung5]: 1 synthesis tool visible
            disallowed_tools=RESEARCH_ALLOWED,      # GATE[rung5]: explicit block (belt + suspenders)
            permission_mode="dontAsk",              # GATE[rung5]: research tools → DENIED
            env=child_env,
        )


@contextlib.asynccontextmanager
async def open_sdk_client(options):
    """SDK boundary — opens ClaudeSDKClient. Mock THIS in smoke_test."""
    from claude_agent_sdk import ClaudeSDKClient
    async with ClaudeSDKClient(options=options) as client:
        yield client


async def send_turn(client, prompt: str, tool_observer: Callable) -> dict:
    """
    SDK boundary — sends one turn; tool_observer fires for each ToolUseBlock seen.
    Returns dict: response_text, in_tok, out_tok, session_id, tool_calls_this_turn.
    TRAIT[autonomy] — every model decision flows through here.
    """
    from claude_agent_sdk.types import AssistantMessage, ResultMessage

    await client.query(prompt)
    response_text = ""
    in_tok = out_tok = 0
    session_id: str | None = None
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
            sid = getattr(msg, "session_id", None)
            if sid:
                session_id = sid

    return {"response_text": response_text, "in_tok": in_tok, "out_tok": out_tok,
            "session_id": session_id, "tool_calls_this_turn": tool_calls_this_turn, "chain": chain}


# ═══════════════════════════════════════════
# PURPOSE: POST-RUN AGENT SUMMARY — unconditional exit report
# AGENTIC TRAIT: termination; all traits summarised with evidence
# ACHIEVES: matches runtime output standard FR-C8; covers 7 mandatory items
# DEPENDENCIES: state dict from agent_loop(); fires whether GOAL MET or cap
# ═══════════════════════════════════════════
def print_summary(state: dict) -> None:
    w = 60
    print()
    print("╔" + "═" * w + "╗")
    print("║" + " 🧠 AGENT SUMMARY ".center(w) + "║")
    print("╚" + "═" * w + "╝")
    print(f"  Exit reason      : {state.get('exit_reason', '?')}")
    print(f"  Research turns   : {state.get('research_turns', 0)}/{MAX_RESEARCH_TURNS}")
    print(f"  Synthesis turns  : {state.get('synthesis_turns', 0)}/{MAX_SYNTHESIS_TURNS}")
    print(f"  Total tool calls : {state.get('total_tool_calls', 0)}/{MAX_TOOL_CALLS_TOTAL}")
    print(f"  Tool breakdown   : {state.get('tool_breakdown', {})}")
    print(f"  Tokens in/out    : {state.get('total_in_tok', 0)} / {state.get('total_out_tok', 0)}")
    print(f"  Thermal conflict : {'detected + resolved' if state.get('thermal_conflict_resolved') else 'none'}")
    print(f"  Price drop       : {'detected' if state.get('price_drop_detected') else 'none'}")
    if state.get("recommendation"):
        rec = state["recommendation"]
        print(f"  Recommendation   : {rec.get('primary_recommendation', '?')}")
        print(f"  Price            : {rec.get('price', '?')}")
    print()
    print("  GATE / TRAIT MAP")
    print("  " + "─" * 50)
    print("  G1 goal predicate : is_research_complete() + is_recommendation_ready() called each step")
    print("  G2 model decision : [MODEL DECISION] lines — model picked research tools each turn")
    print("  G3 loop feedback  : thermal conflict changed subsequent tool call (observe→reason→act)")
    print(f"  G4 termination    : {state.get('exit_reason', '?')}")
    print("  G5                : N/A — independent verifier at rung 7")
    print()
    print("  RUNG 5 SUMMARY")
    print("  " + "─" * 50)
    print("  Research phase: allowed_tools=4 research tools | permission_mode=dontAsk")
    print("  Synthesis phase: allowed_tools=1 synthesis tool | disallowed_tools=research tools | dontAsk")
    print("  Effect: model had NO access to synthesize_recommendation during research,")
    print("         and NO access to search/price/thermal/compare during synthesis.")
    print("  This is SDK-enforced — not a system-prompt request.")
    print()
    print("  MEMORY LEDGER")
    print("  " + "─" * 50)
    notes = _read_notes()
    print(f"  SESSION (ephemeral) : ClaudeSDKClient — gone now (both phases closed)")
    print(f"  APP (persistent)    : research_notes.json — {len(notes)} entries persisted")
    print("═" * (w + 2))


# ═══════════════════════════════════════════
# PURPOSE: The agent loop — research phase then synthesis phase
# AGENTIC TRAIT: all traits exercised across two phases
# ACHIEVES: all five gates; both exit paths; rung-5 phase transition visible
# DEPENDENCIES: all functions above; child_env from preflight()
# ═══════════════════════════════════════════
async def agent_loop(child_env: dict) -> dict:
    """TRAIT[observe-reason-act] — two-phase loop with SDK-enforced tool boundaries."""

    # Reset mock state for clean run
    _mock_state.clear()

    state: dict[str, Any] = {
        "research_turns": 0, "synthesis_turns": 0, "total_tool_calls": 0,
        "tool_breakdown": {}, "specs_researched": [], "prices_checked": [],
        "thermal_analyzed": False, "thermal_conflict_detected": False,
        "thermal_conflict_resolved": False, "comparison_made": False,
        "price_drop_detected": False, "recommendation_made": False,
        "confidence": 0.0, "recommendation": None,
        "exit_reason": "", "session_id_research": None, "session_id_synthesis": None,
        "total_in_tok": 0, "total_out_tok": 0,
    }

    # ── BOOT ──
    print(f"🤖 [AGENT BOOT] Mac Advisor {AGENT_VERSION} · rung 5 · consumer-research")
    print("📖 [OUTPUT GUIDE] each emoji-labeled line is a teaching element — "
          "match to mac-advisor_learning-guide.html §6")
    print()
    print("🎯 [GOAL SET] Recommend the best MacBook Pro 16\" M4 variant for a "
          "software developer + AI practitioner workload (Indian market)")
    print("   GATE[G1]: is_research_complete() + is_recommendation_ready() called each step")
    print()

    # ── WAKE UP — read APP MEMORY ──
    notes = _read_notes()
    prior_count = len(notes)
    print(f"🧠 [MEMORY RETRIEVED] {prior_count} prior research finding(s) injected from {NOTES_FILE}")
    print(f"📀 [APP MEMORY] {NOTES_FILE} → {prior_count} entries")
    print()

    print("📋 [PLAN GENERATED]")
    print("   ╔══════════════════════════════════════════════════════╗")
    print("   ║  PHASE 1 — RESEARCH  (tools: search · price · thermal · compare)  ║")
    print("   ║  Step 1 · search_specs      → variant benchmarks     ○ pending    ║")
    print("   ║  Step 2 · check_price       → Indian market pricing  ○ pending    ║")
    print("   ║  Step 3 · analyze_thermal   → throttling data        ○ pending    ║")
    print("   ║  Step 4 · compare_variants  → head-to-head findings  ○ pending    ║")
    print("   ╠══════════════════════════════════════════════════════╣")
    print("   ║  PHASE 2 — SYNTHESIS (tool: synthesize_recommendation only)       ║")
    print("   ║  Step 5 · synthesize        → final recommendation   ○ pending    ║")
    print("   ╚══════════════════════════════════════════════════════╝")
    print()

    # ── Tool observer — fires on each ToolUseBlock; updates state flags ──
    def tool_observer(tname: str, tinput: dict) -> None:
        state["total_tool_calls"] += 1
        state["tool_breakdown"][tname] = state["tool_breakdown"].get(tname, 0) + 1
        short = tname.split("__")[-1] if "__" in tname else tname
        print(f"🔧 [TOOL CALL] {short}({json.dumps(tinput)[:60]})")  # TRAIT[tool-use]
        if short == "search_specs":
            v = tinput.get("variant", "?")
            if v not in state["specs_researched"]:
                state["specs_researched"].append(v)
        elif short == "check_price":
            v = tinput.get("variant", "?")
            if v not in state["prices_checked"]:
                state["prices_checked"].append(v)
        elif short == "analyze_thermal":
            state["thermal_analyzed"] = True
        elif short == "compare_variants":
            state["comparison_made"] = True
        elif short == "synthesize_recommendation":
            state["recommendation_made"] = True

    # ══════════════════════════════════════
    # PHASE 1 — RESEARCH
    # allowed_tools = RESEARCH_ALLOWED (4 tools)
    # synthesize_recommendation → DENIED (dontAsk)
    # ══════════════════════════════════════
    print("━" * 62)
    print("🔬 [PHASE 1 — RESEARCH]")
    print(f"   allowed : {', '.join(t.split('__')[-1] for t in RESEARCH_ALLOWED)}")
    print(f"   denied  : synthesize_recommendation  ← GATE[rung5]")
    print("━" * 62)
    print()

    research_prompt = (
        "Research the MacBook Pro 16\" M4 lineup for a software developer and AI practitioner "
        "in India. Cover specs, pricing, thermal, and comparison. "
        "Prior notes from previous runs: " + json.dumps(notes if notes else {})
    )
    # GATE[G5]: N/A — independent verifier introduced at rung 7; no critic call in this agent

    async with open_sdk_client(build_options(child_env, "research")) as client:
        while (not is_research_complete(state)
               and state["research_turns"] < MAX_RESEARCH_TURNS):

            state["research_turns"] += 1
            turn = state["research_turns"]
            print("─" * 62)
            print(f"📍 [STEP {turn}]  research turn {turn}/{MAX_RESEARCH_TURNS}")
            ctx_words = len(research_prompt.split()) if turn == 1 else 40
            print(f"📊 [CONTEXT] ~{ctx_words * 1.3:.0f} tokens in context · "
                  f"+{ctx_words:.0f} words this step")

            if turn > 1:
                print(f"🔄 [LOOP FEEDBACK] "  # GATE[G3]
                      f"observed: specs={state['specs_researched']} · "
                      f"thermal_analyzed={state['thermal_analyzed']} · "
                      f"conflict_resolved={state['thermal_conflict_resolved']} → "
                      f"next call targets missing research area")

            print(f"━━━ [SDK →] {MODEL_ID} · research turn {turn} · "
                  f"allowed_tools={len(RESEARCH_ALLOWED)} (synthesis DENIED)")

            try:
                result = await send_turn(
                    client,
                    research_prompt if turn == 1 else "Continue the research. What area needs attention next?",
                    tool_observer,
                )
            except Exception as exc:
                print(f"⚠ [ERROR: TRANSIENT → skip] SDK turn failed: {exc}")
                state["research_turns"] -= 1
                continue

            state["total_in_tok"] += result["in_tok"]
            state["total_out_tok"] += result["out_tok"]
            if result["session_id"]:
                state["session_id_research"] = result["session_id"]
            if result["session_id"]:
                print(f"💾 [SESSION MEMORY] session_id={result['session_id'][:16]}…")

            n_chain = result["tool_calls_this_turn"]
            if n_chain:
                print(f"🔗 [TOOL CHAIN] {n_chain} tool call(s) in this research turn")
            print(f"🎲 [MODEL DECISION] selected {n_chain} tool call(s) from "
                  f"research palette · alternatives: different tool, different params, stop")

            # ── Check for complications fired by tool implementations ──
            if _mock_state.get("thermal_conflict_pending") and not state["thermal_conflict_detected"]:
                cf = _mock_state.pop("thermal_conflict_pending")
                state["thermal_conflict_detected"] = True
                print()
                print(f"⚠ [CONFLICT DETECTED] thermal data contradiction for {cf['variant']}")
                print(f"  ── O ──  Source 1 ({cf['first']['source']}): '{cf['first']['throttling']}'")
                print(f"  ── O ──  Source 2 ({cf['second']['source']}): '{cf['second']['throttling']}'")
                print(f"  ── R ──  Two independent sources disagree — manufacturer vs independent lab")
                print(f"  ── A ──  Inserting resolution step: call analyze_thermal with 'sustained_load' workload")
                print()

            if _mock_state.get("thermal_conflict_resolved") and not state["thermal_conflict_resolved"]:
                state["thermal_conflict_resolved"] = True
                print(f"✅ [CONFLICT RESOLVED] thermal verdict for m4_pro confirmed across 2 independent labs")

            if _mock_state.get("price_drop_pending") and not state["price_drop_detected"]:
                pd = _mock_state.pop("price_drop_pending")
                state["price_drop_detected"] = True
                print()
                print(f"⚠ [PRICE DROP DETECTED] {pd['variant']}: {pd['old']} → {pd['new']}")
                print(f"  ── O ──  Price for {pd['variant']} has changed since last check")
                print(f"  ── R ──  ₹{pd['saving']} reduction changes the value calculus vs M4 Base")
                print(f"  ── A ──  Updating recommendation notes with new price point")
                print()

            print(f"📐 [GOAL PREDICATE] is_research_complete(state) → {is_research_complete(state)}")
            print(f"   (specs={len(state['specs_researched'])}≥2, price={len(state['prices_checked'])}≥1, "
                  f"thermal={state['thermal_analyzed']}, resolved={state['thermal_conflict_resolved']}, "
                  f"compare={state['comparison_made']})")

            model_done_signal = "RESEARCH COMPLETE" in result.get("response_text", "").upper()
            cap_pct = int(100 * turn / MAX_RESEARCH_TURNS)
            print(f"🔍 [TERMINATION CHECK] research {turn}/{MAX_RESEARCH_TURNS} ({cap_pct}%) · "
                  f"text signal={'YES' if model_done_signal else 'no'} · "
                  f"predicate={'MET' if is_research_complete(state) else 'not yet'}")
            print(f"📋 [PLAN PROGRESS] "
                  f"search {'✓' if len(state['specs_researched'])>=2 else '▶'} · "
                  f"price {'✓' if state['prices_checked'] else '▶'} · "
                  f"thermal {'✓' if state['thermal_conflict_resolved'] else ('▶' if state['thermal_analyzed'] else '○')} · "
                  f"compare {'✓' if state['comparison_made'] else '○'}")
            print()

            if is_research_complete(state):
                break

    # Persist findings to APP memory
    notes_update = {
        "last_run": datetime.now().isoformat(),
        "specs_researched": state["specs_researched"],
        "prices_checked": state["prices_checked"],
        "thermal_conflict_detected": state["thermal_conflict_detected"],
        "thermal_conflict_resolved": state["thermal_conflict_resolved"],
        "price_drop_detected": state["price_drop_detected"],
    }
    _write_notes_atomic(notes_update)
    print(f"📀 [APP MEMORY] research findings written → {NOTES_FILE}")
    print()

    if not is_research_complete(state):
        state["exit_reason"] = (f"🏁 EXIT: research cap — {state['research_turns']}/{MAX_RESEARCH_TURNS} turns")
        print(state["exit_reason"])
        print_summary(state)
        return state

    # ══════════════════════════════════════
    # PHASE 2 — SYNTHESIS
    # allowed_tools = SYNTHESIS_ALLOWED (1 tool)
    # all research tools → DENIED (dontAsk + disallowed_tools)
    # ══════════════════════════════════════
    print("━" * 62)
    print("🔮 [PHASE 2 — SYNTHESIS]")
    print(f"   allowed : synthesize_recommendation")
    print(f"   denied  : {', '.join(t.split('__')[-1] for t in RESEARCH_ALLOWED)}  ← GATE[rung5]")
    print("━" * 62)
    print()

    synthesis_summary = (
        f"Research complete. Key findings:\n"
        f"- Specs researched: {state['specs_researched']}\n"
        f"- Prices checked: {state['prices_checked']}\n"
        f"- Thermal conflict: {'detected and resolved — 15-20% under sustained inference, intermittent use unaffected' if state['thermal_conflict_resolved'] else 'not encountered'}\n"
        f"- Price drop: {'YES — M4 Pro 24GB dropped from ₹2,49,900 to ₹2,29,900' if state['price_drop_detected'] else 'none'}\n"
        f"- Comparison: {'completed' if state['comparison_made'] else 'not done'}\n"
        f"Now call synthesize_recommendation with findings and confidence score."
    )

    async with open_sdk_client(build_options(child_env, "synthesis")) as client:
        while (not is_recommendation_ready(state)
               and state["synthesis_turns"] < MAX_SYNTHESIS_TURNS):

            state["synthesis_turns"] += 1
            turn = state["synthesis_turns"]
            print("─" * 62)
            print(f"📍 [STEP {state['research_turns'] + turn}]  synthesis turn {turn}/{MAX_SYNTHESIS_TURNS}")
            print(f"🔄 [LOOP FEEDBACK] research phase complete → switching to synthesis palette")
            print(f"━━━ [SDK →] {MODEL_ID} · synthesis turn {turn} · "
                  f"allowed_tools=1 (research tools DENIED)")

            try:
                result = await send_turn(
                    client,
                    synthesis_summary if turn == 1 else "Call synthesize_recommendation with your findings.",
                    tool_observer,
                )
            except Exception as exc:
                print(f"⚠ [ERROR: TRANSIENT → skip] SDK turn failed: {exc}")
                continue

            state["total_in_tok"] += result["in_tok"]
            state["total_out_tok"] += result["out_tok"]
            if result["session_id"]:
                state["session_id_synthesis"] = result["session_id"]

            print(f"━━━ [← SDK] +{result['in_tok']} in / +{result['out_tok']} out tokens")

            # Pick up synthesis result from mock state
            if _mock_state.get("synthesis_result"):
                rec = _mock_state.pop("synthesis_result")
                state["recommendation"] = rec
                state["confidence"] = _mock_state.pop("synthesis_confidence", 0.0)

            print(f"🎲 [MODEL DECISION] called synthesize_recommendation · "
                  f"confidence={state.get('confidence', 0):.0%}")

            ready = is_recommendation_ready(state)
            print(f"📐 [GOAL PREDICATE] is_recommendation_ready(state) → {ready} "
                  f"(made={state['recommendation_made']}, confidence={state['confidence']:.0%}≥{CONFIDENCE_THRESHOLD:.0%})")
            print(f"🔍 [TERMINATION CHECK] synthesis {turn}/{MAX_SYNTHESIS_TURNS} · "
                  f"{'GOAL MET' if ready else 'not yet'}")
            print(f"📋 [PLAN PROGRESS] "
                  f"search ✓ · price ✓ · thermal ✓ · compare ✓ · "
                  f"synthesize {'✓' if ready else '▶'}")
            print()

            if ready:
                break

    # ── EXIT ──
    if is_recommendation_ready(state):
        state["exit_reason"] = "🏁 GOAL MET — recommendation ready (confidence ≥ 80%)"
    else:
        state["exit_reason"] = (f"🏁 EXIT: synthesis cap — {state['synthesis_turns']}/{MAX_SYNTHESIS_TURNS} turns")

    print(state["exit_reason"])
    if state.get("recommendation") and state["recommendation"].get("status") == "recommendation_ready":
        rec = state["recommendation"]
        print()
        print("╔" + "═" * 60 + "╗")
        print("║" + " 🖥  FINAL RECOMMENDATION ".center(60) + "║")
        print("╚" + "═" * 60 + "╝")
        print(f"  Best fit  : {rec['primary_recommendation']}")
        print(f"  Price     : {rec['price']}")
        print(f"  Confidence: {rec['confidence']:.0%}")
        print()
        for r in rec.get("rationale", []):
            print(f"  ✓ {r}")
        print()
        print(f"  Trade-off : {rec.get('trade_off_accepted', '')}")
        print(f"  Buy signal: {rec.get('buy_now_signal', '')}")
        print("═" * 62)

    print_summary(state)
    return state


async def main() -> None:
    with tee_to_log():
        child_env = preflight()
        await agent_loop(child_env)


if __name__ == "__main__":
    asyncio.run(main())
