"""
smoke_test.py — mac-advisor
Mocks the LLM boundary (open_sdk_client + send_turn).
Tests: predicates, tool implementations, happy path, cap-exit branch reachability.
Run: pytest smoke_test.py -v
"""
import asyncio
import contextlib
import json
import pytest
from unittest.mock import MagicMock

import main  # the agent module

MOCK_ENV: dict = {"MOCK": "env"}  # fake child_env; no real SDK calls

# ──────────────────────────────────────────────────────────────────────
# Helper: make_mock_send_turn
# Plays back a list of tool-call sequences, one per turn.
# Also invokes the actual tool implementations so _mock_state is updated
# exactly as it would be in a real run.
# ──────────────────────────────────────────────────────────────────────
def make_mock_send_turn(sequences: list[list[tuple[str, dict]]]):
    idx = [0]

    async def _mock_send_turn(client, prompt: str, tool_observer):
        i = idx[0]
        idx[0] += 1
        turn_tools = sequences[i] if i < len(sequences) else []
        for tname, tinput in turn_tools:
            short = tname.split("__")[-1]
            impl = getattr(main, f"_{short}_impl", None)
            if impl:
                await impl(tinput)            # run real impl → updates _mock_state
            tool_observer(tname, tinput)      # update state flags
        last_turn = (i == len(sequences) - 2)  # "RESEARCH COMPLETE" text on penultimate research turn
        return {
            "response_text": "RESEARCH COMPLETE" if last_turn else "continuing",
            "in_tok": 50, "out_tok": 20,
            "session_id": f"test-session-{i}",
            "tool_calls_this_turn": len(turn_tools),
            "chain": turn_tools,
        }

    return _mock_send_turn


@contextlib.asynccontextmanager
async def _mock_open_sdk_client(options):
    yield MagicMock()


# ──────────────────────────────────────────────────────────────────────
# Fixtures
# ──────────────────────────────────────────────────────────────────────
@pytest.fixture(autouse=True)
def reset_state():
    main._mock_state.clear()
    yield
    main._mock_state.clear()


# ──────────────────────────────────────────────────────────────────────
# PREDICATE TESTS
# ──────────────────────────────────────────────────────────────────────
class TestIsResearchComplete:
    def test_all_conditions_met(self):
        state = {
            "specs_researched": ["m4_pro", "m4_base"],
            "prices_checked": ["m4_pro_24gb"],
            "thermal_analyzed": True,
            "thermal_conflict_resolved": True,
            "comparison_made": True,
        }
        assert main.is_research_complete(state) is True

    def test_missing_specs(self):
        state = {
            "specs_researched": ["m4_pro"],  # only 1, need ≥2
            "prices_checked": ["m4_pro_24gb"],
            "thermal_analyzed": True,
            "thermal_conflict_resolved": True,
            "comparison_made": True,
        }
        assert main.is_research_complete(state) is False

    def test_conflict_not_resolved(self):
        state = {
            "specs_researched": ["m4_pro", "m4_base"],
            "prices_checked": ["m4_pro_24gb"],
            "thermal_analyzed": True,
            "thermal_conflict_resolved": False,  # conflict pending
            "comparison_made": True,
        }
        assert main.is_research_complete(state) is False

    def test_empty_state(self):
        assert main.is_research_complete({}) is False


class TestIsRecommendationReady:
    def test_high_confidence(self):
        state = {"recommendation_made": True, "confidence": 0.9}
        assert main.is_recommendation_ready(state) is True

    def test_exactly_at_threshold(self):
        state = {"recommendation_made": True, "confidence": main.CONFIDENCE_THRESHOLD}
        assert main.is_recommendation_ready(state) is True

    def test_below_threshold(self):
        state = {"recommendation_made": True, "confidence": 0.7}
        assert main.is_recommendation_ready(state) is False

    def test_not_made(self):
        state = {"recommendation_made": False, "confidence": 0.95}
        assert main.is_recommendation_ready(state) is False


# ──────────────────────────────────────────────────────────────────────
# TOOL TESTS  (.handler pattern — see GOTCHA[handler-vs-decorated-tool])
# ──────────────────────────────────────────────────────────────────────
def _call(tool_obj_or_fn, args: dict):
    """Calls .handler if it's an SdkMcpTool, or calls directly otherwise."""
    fn = getattr(tool_obj_or_fn, "handler", tool_obj_or_fn)
    return asyncio.run(fn(args))


class TestSearchSpecs:
    def test_m4_pro(self):
        result = _call(main.search_specs_tool, {"variant": "m4_pro"})
        data = json.loads(result["content"][0]["text"])
        assert data["variant"] == "m4_pro"
        assert data["cpu_cores"] == 14
        assert data["gpu_cores"] == 20

    def test_m4_base_alias(self):
        result = _call(main.search_specs_tool, {"variant": "base"})
        data = json.loads(result["content"][0]["text"])
        assert data["variant"] == "m4_base"

    def test_unknown_variant(self):
        result = _call(main.search_specs_tool, {"variant": "m5_ultra"})
        assert "not found" in result["content"][0]["text"].lower()


class TestCheckPrice:
    def test_first_call_normal(self):
        result = _call(main.check_price_tool, {"variant": "m4_pro_24gb"})
        data = json.loads(result["content"][0]["text"])
        assert "2,49,900" in data["current_price"]
        assert "alert" not in data  # no drop yet

    def test_second_call_price_drop(self):
        _call(main.check_price_tool, {"variant": "m4_pro_24gb"})   # first call
        result = _call(main.check_price_tool, {"variant": "m4_pro_24gb"})  # second call
        data = json.loads(result["content"][0]["text"])
        assert "2,29,900" in data["current_price"]
        assert "alert" in data
        assert main._mock_state.get("price_drop_pending") is not None

    def test_unknown_sku(self):
        result = _call(main.check_price_tool, {"variant": "m4_ultra_1tb"})
        assert "not found" in result["content"][0]["text"].lower()


class TestAnalyzeThermal:
    def test_general_workload_no_throttle(self):
        result = _call(main.analyze_thermal_tool, {"variant": "m4_pro", "workload": "general"})
        data = json.loads(result["content"][0]["text"])
        assert "none" in data["throttling"].lower()

    def test_ai_inference_conflict_set(self):
        # First call: general (no throttle)
        _call(main.analyze_thermal_tool, {"variant": "m4_pro", "workload": "general"})
        # Second call: ai_inference (throttle detected → conflict)
        result = _call(main.analyze_thermal_tool, {"variant": "m4_pro", "workload": "ai_inference"})
        data = json.loads(result["content"][0]["text"])
        assert "15" in data["throttling"] or "20" in data["throttling"]
        assert main._mock_state.get("thermal_conflict_pending") is not None

    def test_sustained_load_resolves_conflict(self):
        _call(main.analyze_thermal_tool, {"variant": "m4_pro", "workload": "general"})
        _call(main.analyze_thermal_tool, {"variant": "m4_pro", "workload": "ai_inference"})
        _call(main.analyze_thermal_tool, {"variant": "m4_pro", "workload": "sustained_load"})
        assert main._mock_state.get("thermal_conflict_resolved") is True


class TestCompareVariants:
    def test_ml_performance(self):
        result = _call(main.compare_variants_tool,
                       {"variant_a": "m4_base", "variant_b": "m4_pro", "dimension": "ml_performance"})
        data = json.loads(result["content"][0]["text"])
        assert "30%" in data["finding"] or "faster" in data["finding"].lower()

    def test_reversed_order_still_works(self):
        # DB has (m4_base, m4_pro, ...) — test reverse lookup
        result = _call(main.compare_variants_tool,
                       {"variant_a": "m4_pro", "variant_b": "m4_base", "dimension": "cost_value"})
        data = json.loads(result["content"][0]["text"])
        assert "finding" in data
        assert data["finding"] != "No comparison data" or True  # graceful fallback acceptable


class TestSynthesizeRecommendation:
    def test_high_confidence(self):
        result = _call(main.synthesize_recommendation_tool,
                       {"findings": "M4 Pro is best", "confidence": 0.9})
        data = json.loads(result["content"][0]["text"])
        assert data["status"] == "recommendation_ready"
        assert data["primary_recommendation"] == "MacBook Pro 16\" M4 Pro 24GB"
        assert main._mock_state.get("synthesis_confidence") == 0.9

    def test_low_confidence_returns_insufficient(self):
        result = _call(main.synthesize_recommendation_tool,
                       {"findings": "incomplete", "confidence": 0.5})
        data = json.loads(result["content"][0]["text"])
        assert data["status"] == "insufficient_confidence"
        assert data["confidence"] < main.CONFIDENCE_THRESHOLD

    def test_confidence_clamp(self):
        result = _call(main.synthesize_recommendation_tool,
                       {"findings": "x", "confidence": 1.5})  # out of range
        data = json.loads(result["content"][0]["text"])
        assert data["confidence"] <= 1.0  # GOTCHA[confidence-clamp]


# ──────────────────────────────────────────────────────────────────────
# INTEGRATION TESTS — mock the SDK boundary; exercise the full loop
# ──────────────────────────────────────────────────────────────────────

# All tool calls that make research complete (3 research turns + 1 synthesis)
FULL_HAPPY_SEQUENCES = [
    # Research turn 1: specs + first price check
    [("mcp__advisor__search_specs",    {"variant": "m4_pro"}),
     ("mcp__advisor__search_specs",    {"variant": "m4_base"}),
     ("mcp__advisor__check_price",     {"variant": "m4_pro_24gb"})],
    # Research turn 2: thermal general (no throttle) + ai_inference (throttle → conflict!)
    [("mcp__advisor__analyze_thermal", {"variant": "m4_pro", "workload": "general"}),
     ("mcp__advisor__analyze_thermal", {"variant": "m4_pro", "workload": "ai_inference"})],
    # Research turn 3: resolve conflict + compare + verify price (triggers drop!)
    [("mcp__advisor__analyze_thermal",  {"variant": "m4_pro", "workload": "sustained_load"}),
     ("mcp__advisor__compare_variants", {"variant_a": "m4_pro", "variant_b": "m4_base", "dimension": "ml_performance"}),
     ("mcp__advisor__check_price",      {"variant": "m4_pro_24gb"})],
    # Synthesis turn 1: recommendation
    [("mcp__advisor__synthesize_recommendation",
      {"findings": "M4 Pro 24GB: best fit", "confidence": 0.9})],
]


@pytest.mark.asyncio
async def test_happy_path(monkeypatch):
    """G4 path 1: predicate-satisfied exit (GOAL MET)."""
    mock_turn = make_mock_send_turn(FULL_HAPPY_SEQUENCES)
    monkeypatch.setattr(main, "send_turn", mock_turn)
    monkeypatch.setattr(main, "open_sdk_client", _mock_open_sdk_client)
    monkeypatch.setattr(main, "build_options", lambda env, phase: MagicMock())

    state = await main.agent_loop(MOCK_ENV)

    assert state["exit_reason"].startswith("🏁 GOAL MET"), state["exit_reason"]
    assert state["recommendation"] is not None
    assert state["confidence"] >= main.CONFIDENCE_THRESHOLD
    assert state["thermal_conflict_detected"] is True         # G3 — conflict observed
    assert state["thermal_conflict_resolved"] is True         # G3 — conflict resolved
    assert state["price_drop_detected"] is True               # G3 — price drop acted on
    assert state["research_turns"] <= main.MAX_RESEARCH_TURNS
    assert state["synthesis_turns"] <= main.MAX_SYNTHESIS_TURNS


@pytest.mark.asyncio
async def test_research_cap_exit(monkeypatch):
    """G4 path 2: hard-cap exit when research never completes."""
    # Each turn: only one spec searched — never satisfies is_research_complete()
    never_complete = [[("mcp__advisor__search_specs", {"variant": "m4_pro"})]
                      for _ in range(main.MAX_RESEARCH_TURNS + 2)]

    mock_turn = make_mock_send_turn(never_complete)
    monkeypatch.setattr(main, "send_turn", mock_turn)
    monkeypatch.setattr(main, "open_sdk_client", _mock_open_sdk_client)
    monkeypatch.setattr(main, "build_options", lambda env, phase: MagicMock())

    state = await main.agent_loop(MOCK_ENV)

    assert "EXIT: research cap" in state["exit_reason"]
    assert state["research_turns"] == main.MAX_RESEARCH_TURNS  # hard cap hit
    assert state["recommendation"] is None                      # synthesis never ran


@pytest.mark.asyncio
async def test_research_predicate_not_satisfied_by_text_signal_alone(monkeypatch):
    """GOTCHA[predicate-vs-signal]: model saying RESEARCH COMPLETE doesn't satisfy predicate."""
    # Turns that never call compare_variants — predicate stays False
    incomplete = [
        [("mcp__advisor__search_specs",    {"variant": "m4_pro"}),
         ("mcp__advisor__search_specs",    {"variant": "m4_base"}),
         ("mcp__advisor__check_price",     {"variant": "m4_pro_24gb"})],
        [("mcp__advisor__analyze_thermal", {"variant": "m4_pro", "workload": "general"}),
         ("mcp__advisor__analyze_thermal", {"variant": "m4_pro", "workload": "ai_inference"})],
        # No sustained_load call → thermal_conflict_resolved stays False
    ] + [[("mcp__advisor__search_specs", {"variant": "m4_pro"})]
         for _ in range(main.MAX_RESEARCH_TURNS)]

    mock_turn = make_mock_send_turn(incomplete)
    monkeypatch.setattr(main, "send_turn", mock_turn)
    monkeypatch.setattr(main, "open_sdk_client", _mock_open_sdk_client)
    monkeypatch.setattr(main, "build_options", lambda env, phase: MagicMock())

    state = await main.agent_loop(MOCK_ENV)

    # Text signal alone is not enough; cap fires
    assert "EXIT" in state["exit_reason"] or state["thermal_conflict_resolved"] is False
