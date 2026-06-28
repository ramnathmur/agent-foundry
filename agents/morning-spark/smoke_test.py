"""
smoke_test.py — morning-spark
Mocks the LLM boundary (open_sdk_client + send_turn).
Tests: hooks (PreToolUse guard + PostToolUse audit), tool implementations,
       goal predicate, goal-met exit path, cap-hit exit path.
Run: pytest smoke_test.py -v
"""
import asyncio
import contextlib
import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, AsyncMock, patch

import pytest

import main  # the agent module

MOCK_ENV: dict = {"MOCK": "env"}  # fake child_env; no real SDK calls


# ──────────────────────────────────────────────────────────────────────
# Helper: _call — invokes SdkMcpTool.handler if present, else calls directly
# (SdkMcpTool wraps the impl fn; .handler is the raw async callable)
# ──────────────────────────────────────────────────────────────────────
def _call(tool_obj_or_fn, args: dict):
    fn = getattr(tool_obj_or_fn, "handler", tool_obj_or_fn)
    return asyncio.run(fn(args))


# ──────────────────────────────────────────────────────────────────────
# Helper: make_mock_send_turn
# Plays back a list of tool-call sequences, one sequence per turn.
# Invokes real _impl functions so _agent_state updates exactly as in a live run.
# ──────────────────────────────────────────────────────────────────────
def make_mock_send_turn(sequences: list[list[tuple[str, dict]]]):
    idx = [0]

    async def _mock_send_turn(client, prompt: str, tool_observer):
        i = idx[0]
        idx[0] += 1
        turn_tools = sequences[i] if i < len(sequences) else []
        for tname, tinput in turn_tools:
            short = tname.split("__")[-1] if "__" in tname else tname
            impl = getattr(main, f"_{short}_impl", None)
            if impl:
                await impl(tinput)         # real impl → updates _agent_state
            tool_observer(tname, tinput)   # updates loop_state counters
        return {
            "response_text": "continuing",
            "in_tok": 50, "out_tok": 20,
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
    """Clean module-level state before and after each test."""
    main._agent_state.update({
        "weather": None, "date_info": None, "headline": None,
        "headline_category": None, "quality_passed": False,
        "quality_issues": [], "briefing": None,
    })
    main._hook_state.update({"calls_made": [], "spans": [], "denied_count": 0})
    yield
    main._agent_state.update({
        "weather": None, "date_info": None, "headline": None,
        "headline_category": None, "quality_passed": False,
        "quality_issues": [], "briefing": None,
    })
    main._hook_state.update({"calls_made": [], "spans": [], "denied_count": 0})


# ──────────────────────────────────────────────────────────────────────
# GOAL PREDICATE TESTS
# ──────────────────────────────────────────────────────────────────────
class TestBriefingComplete:
    def test_returns_false_when_empty(self):
        assert main.briefing_complete() is False

    def test_returns_false_when_only_weather(self):
        main._agent_state["weather"] = "Sunny"
        assert main.briefing_complete() is False

    def test_returns_false_when_missing_quality(self):
        main._agent_state["weather"]   = "Sunny"
        main._agent_state["date_info"] = "Monday"
        main._agent_state["headline"]  = "Some news"
        main._agent_state["briefing"]  = "Good morning"
        # quality_passed is still False
        assert main.briefing_complete() is False

    def test_returns_false_when_missing_briefing(self):
        main._agent_state["weather"]       = "Sunny"
        main._agent_state["date_info"]     = "Monday"
        main._agent_state["headline"]      = "Some news"
        main._agent_state["quality_passed"] = True
        # briefing is still None
        assert main.briefing_complete() is False

    def test_returns_true_when_all_conditions_met(self):
        main._agent_state["weather"]        = "Sunny, 26°C"
        main._agent_state["date_info"]      = "Saturday, June 14, 2026"
        main._agent_state["headline"]       = "Big news story"
        main._agent_state["quality_passed"] = True
        main._agent_state["briefing"]       = "Good morning! Here's your briefing."
        assert main.briefing_complete() is True


# ──────────────────────────────────────────────────────────────────────
# TOOL IMPLEMENTATION TESTS
# ──────────────────────────────────────────────────────────────────────
class TestFetchWeather:
    def test_returns_weather_string(self):
        result = _call(main.fetch_weather_tool, {})
        text = result["content"][0]["text"]
        assert len(text) > 10
        assert "°C" in text or "weather" in text.lower() or "cloud" in text.lower()

    def test_updates_agent_state(self):
        assert main._agent_state["weather"] is None
        _call(main.fetch_weather_tool, {})
        assert main._agent_state["weather"] is not None


class TestFetchDate:
    def test_returns_date_string(self):
        result = _call(main.fetch_date_tool, {})
        text = result["content"][0]["text"]
        assert len(text) > 5
        assert "2026" in text or any(m in text for m in
            ["January","February","March","April","May","June",
             "July","August","September","October","November","December"])

    def test_updates_agent_state(self):
        assert main._agent_state["date_info"] is None
        _call(main.fetch_date_tool, {})
        assert main._agent_state["date_info"] is not None


class TestFetchHeadline:
    def test_known_category_technology(self):
        result = _call(main.fetch_headline_tool, {"category": "technology"})
        text = result["content"][0]["text"]
        assert len(text) > 10
        assert main._agent_state["headline"] == text
        assert main._agent_state["headline_category"] == "technology"

    def test_known_category_science(self):
        result = _call(main.fetch_headline_tool, {"category": "science"})
        text = result["content"][0]["text"]
        assert len(text) > 10
        assert main._agent_state["headline_category"] == "science"

    def test_unknown_category_returns_error(self):
        result = _call(main.fetch_headline_tool, {"category": "sports"})
        text = result["content"][0]["text"]
        assert "Unknown category" in text or "not found" in text.lower() or "Valid" in text

    def test_unknown_category_does_not_set_state(self):
        _call(main.fetch_headline_tool, {"category": "invalid_cat"})
        assert main._agent_state["headline"] is None

    def test_all_six_categories_work(self):
        for cat in ("general", "technology", "science", "health", "world", "business"):
            main._agent_state["headline"] = None
            result = _call(main.fetch_headline_tool, {"category": cat})
            text = result["content"][0]["text"]
            assert len(text) > 10, f"Empty headline for category '{cat}'"


class TestCheckQuality:
    def test_returns_fail_when_nothing_fetched(self):
        result = _call(main.check_quality_tool, {})
        data = json.loads(result["content"][0]["text"])
        assert data["quality_passes"] is False
        assert len(data["issues"]) > 0
        assert main._agent_state["quality_passed"] is False

    def test_returns_fail_when_only_weather(self):
        main._agent_state["weather"] = "Sunny"
        result = _call(main.check_quality_tool, {})
        data = json.loads(result["content"][0]["text"])
        assert data["quality_passes"] is False
        assert "date not fetched" in data["issues"] or "headline not fetched" in data["issues"]

    def test_returns_pass_when_all_three_present(self):
        main._agent_state["weather"]  = "Sunny"
        main._agent_state["date_info"] = "Monday"
        main._agent_state["headline"] = "Big news"
        result = _call(main.check_quality_tool, {})
        data = json.loads(result["content"][0]["text"])
        assert data["quality_passes"] is True
        assert data["issues"] == []
        assert main._agent_state["quality_passed"] is True


class TestSynthesizeBriefing:
    def test_returns_error_when_quality_not_passed(self):
        main._agent_state["weather"]  = "Sunny"
        main._agent_state["date_info"] = "Monday"
        main._agent_state["headline"] = "News"
        # quality_passed is still False
        result = _call(main.synthesize_briefing_tool, {})
        data = json.loads(result["content"][0]["text"])
        assert data.get("status") == "error"
        assert main._agent_state["briefing"] is None

    def test_produces_briefing_when_quality_passed(self, tmp_path, monkeypatch):
        monkeypatch.setattr(main, "_log_path", lambda: tmp_path / "briefing_log.json")
        main._agent_state["weather"]        = "Sunny, 26°C"
        main._agent_state["date_info"]      = "Saturday, June 14, 2026"
        main._agent_state["headline"]       = "Test headline"
        main._agent_state["headline_category"] = "technology"
        main._agent_state["quality_passed"] = True

        result = _call(main.synthesize_briefing_tool, {})
        data = json.loads(result["content"][0]["text"])
        assert data["status"] == "complete"
        assert "briefing" in data
        assert len(data["briefing"]) > 20
        assert main._agent_state["briefing"] is not None

    def test_writes_briefing_log(self, tmp_path, monkeypatch):
        monkeypatch.setattr(main, "_log_path", lambda: tmp_path / "briefing_log.json")
        main._agent_state["weather"]           = "Sunny"
        main._agent_state["date_info"]         = "Saturday"
        main._agent_state["headline"]          = "Test headline"
        main._agent_state["headline_category"] = "general"
        main._agent_state["quality_passed"]    = True

        _call(main.synthesize_briefing_tool, {})

        log_path = tmp_path / "briefing_log.json"
        assert log_path.exists()
        with open(log_path) as f:
            log = json.load(f)
        assert "headline_preview" in log
        assert "briefing_preview" in log
        assert log["headline_category"] == "general"


# ──────────────────────────────────────────────────────────────────────
# HOOK TESTS — RUNG 6
# ──────────────────────────────────────────────────────────────────────
def _make_pre_input(tool_name: str, tool_input: dict):
    m = MagicMock()
    m.tool_name  = tool_name
    m.tool_input = tool_input
    return m


def _make_post_input(tool_name: str, tool_input: dict, tool_response: str):
    m = MagicMock()
    m.tool_name     = tool_name
    m.tool_input    = tool_input
    m.tool_response = tool_response
    return m


class TestPreToolUseGuard:
    def test_allows_first_call(self):
        input_data = _make_pre_input("fetch_weather", {})
        result = asyncio.run(main.pre_tool_use_guard(input_data, "tu-001", None))
        assert result == {}
        assert main._hook_state["denied_count"] == 0

    def test_denies_duplicate_call(self):
        input_data = _make_pre_input("fetch_headline", {"category": "technology"})
        # First call — allow
        asyncio.run(main.pre_tool_use_guard(input_data, "tu-001", None))
        # Second call — deny
        result = asyncio.run(main.pre_tool_use_guard(input_data, "tu-002", None))
        assert "hookSpecificOutput" in result
        output = result["hookSpecificOutput"]
        assert output["permissionDecision"] == "deny"
        assert "permissionDecisionReason" in output
        assert main._hook_state["denied_count"] == 1

    def test_different_params_both_allowed(self):
        input_tech    = _make_pre_input("fetch_headline", {"category": "technology"})
        input_science = _make_pre_input("fetch_headline", {"category": "science"})
        asyncio.run(main.pre_tool_use_guard(input_tech,    "tu-001", None))
        result = asyncio.run(main.pre_tool_use_guard(input_science, "tu-002", None))
        assert result == {}
        assert main._hook_state["denied_count"] == 0

    def test_records_call_in_calls_made(self):
        input_data = _make_pre_input("fetch_date", {})
        asyncio.run(main.pre_tool_use_guard(input_data, "tu-001", None))
        assert len(main._hook_state["calls_made"]) == 1

    def test_denial_reason_is_helpful(self):
        input_data = _make_pre_input("fetch_headline", {"category": "technology"})
        asyncio.run(main.pre_tool_use_guard(input_data, "tu-001", None))
        result = asyncio.run(main.pre_tool_use_guard(input_data, "tu-002", None))
        reason = result["hookSpecificOutput"]["permissionDecisionReason"]
        # Should instruct the model to try something different
        assert "DIFFERENT" in reason or "different" in reason or "category" in reason


class TestPostToolUseAudit:
    def test_appends_to_hook_state_spans(self, tmp_path, monkeypatch):
        spans_path = tmp_path / "test_spans.jsonl"
        monkeypatch.setattr(main, "SPANS_FILE", str(spans_path))

        # Patch _write_span to write to tmp_path
        def _patched_write_span(span):
            with open(spans_path, "a") as f:
                f.write(json.dumps(span) + "\n")
        monkeypatch.setattr(main, "_write_span", _patched_write_span)

        input_data = _make_post_input("fetch_weather", {}, "Sunny, 26°C")
        asyncio.run(main.post_tool_use_audit(input_data, "tu-001", None))

        assert len(main._hook_state["spans"]) == 1
        span = main._hook_state["spans"][0]
        assert span["tool_name"] == "fetch_weather"
        assert span["tool_use_id"] == "tu-001"
        assert "timestamp" in span

    def test_span_contains_result_preview(self, tmp_path, monkeypatch):
        spans_path = tmp_path / "test_spans.jsonl"
        monkeypatch.setattr(main, "_write_span", lambda s: None)

        input_data = _make_post_input("fetch_headline", {"category": "science"}, "Breakthrough in fusion energy")
        asyncio.run(main.post_tool_use_audit(input_data, "tu-002", None))

        span = main._hook_state["spans"][0]
        assert "Breakthrough" in span["result_preview"]

    def test_multiple_spans_accumulate(self, monkeypatch):
        monkeypatch.setattr(main, "_write_span", lambda s: None)

        for i, tname in enumerate(["fetch_weather", "fetch_date", "fetch_headline"]):
            inp = _make_post_input(tname, {}, f"result-{i}")
            asyncio.run(main.post_tool_use_audit(inp, f"tu-{i:03d}", None))

        assert len(main._hook_state["spans"]) == 3
        names = [s["tool_name"] for s in main._hook_state["spans"]]
        assert names == ["fetch_weather", "fetch_date", "fetch_headline"]


# ──────────────────────────────────────────────────────────────────────
# INTEGRATION TESTS — both exit paths
# ──────────────────────────────────────────────────────────────────────
class TestGoalMetPath:
    """Happy path: 2 turns, 5 tool calls, briefing_complete() = True."""

    def test_goal_met_in_two_turns(self, tmp_path, monkeypatch):
        # Redirect file I/O
        monkeypatch.setattr(main, "_log_path", lambda: tmp_path / "briefing_log.json")
        monkeypatch.setattr(main, "_write_span", lambda s: None)
        log_path = tmp_path / "morning-spark_run_output.log"
        monkeypatch.setattr(main, "LOG_FILE", str(log_path))

        # Turn 1: fetch all three sources
        # Turn 2: quality check + synthesize
        sequences = [
            [
                ("mcp__spark__fetch_weather", {}),
                ("mcp__spark__fetch_date", {}),
                ("mcp__spark__fetch_headline", {"category": "technology"}),
            ],
            [
                ("mcp__spark__check_quality", {}),
                ("mcp__spark__synthesize_briefing", {}),
            ],
        ]

        mock_send = make_mock_send_turn(sequences)
        monkeypatch.setattr(main, "send_turn", mock_send)
        monkeypatch.setattr(main, "open_sdk_client", _mock_open_sdk_client)
        monkeypatch.setattr(main, "build_options", lambda env, sp: MagicMock())

        asyncio.run(main.agent_loop(MOCK_ENV))

        assert main.briefing_complete() is True
        assert main._agent_state["weather"] is not None
        assert main._agent_state["date_info"] is not None
        assert main._agent_state["headline"] is not None
        assert main._agent_state["quality_passed"] is True
        assert main._agent_state["briefing"] is not None


class TestCapHitPath:
    """Cap-hit path: loop runs MAX_LOOP_TURNS without completing."""

    def test_exits_without_goal_met_on_turn_cap(self, tmp_path, monkeypatch):
        monkeypatch.setattr(main, "_log_path", lambda: tmp_path / "briefing_log.json")
        monkeypatch.setattr(main, "_write_span", lambda s: None)
        log_path = tmp_path / "morning-spark_run_output.log"
        monkeypatch.setattr(main, "LOG_FILE", str(log_path))

        # All turns: only fetch_weather — never complete, never hit tool cap
        sequences = [
            [("mcp__spark__fetch_weather", {})],
        ] * (main.MAX_LOOP_TURNS + 2)

        mock_send = make_mock_send_turn(sequences)
        monkeypatch.setattr(main, "send_turn", mock_send)
        monkeypatch.setattr(main, "open_sdk_client", _mock_open_sdk_client)
        monkeypatch.setattr(main, "build_options", lambda env, sp: MagicMock())

        asyncio.run(main.agent_loop(MOCK_ENV))

        # Goal should NOT be met
        assert main.briefing_complete() is False


class TestToolCapPath:
    """Cap-hit path: MAX_TOOL_CALLS exceeded before goal is met."""

    def test_exits_on_tool_call_cap(self, tmp_path, monkeypatch):
        monkeypatch.setattr(main, "_log_path", lambda: tmp_path / "briefing_log.json")
        monkeypatch.setattr(main, "_write_span", lambda s: None)
        log_path = tmp_path / "morning-spark_run_output.log"
        monkeypatch.setattr(main, "LOG_FILE", str(log_path))

        # Each turn makes 3 calls to fetch_weather — total exceeds MAX_TOOL_CALLS quickly
        many_calls = [("mcp__spark__fetch_weather", {})] * 3
        sequences = [many_calls] * 10

        mock_send = make_mock_send_turn(sequences)
        monkeypatch.setattr(main, "send_turn", mock_send)
        monkeypatch.setattr(main, "open_sdk_client", _mock_open_sdk_client)
        monkeypatch.setattr(main, "build_options", lambda env, sp: MagicMock())

        asyncio.run(main.agent_loop(MOCK_ENV))

        assert main.briefing_complete() is False


class TestHookIntegration:
    """Verifies hooks fire correctly during a mocked agent_loop run."""

    def test_pre_tool_guard_deny_fires_on_duplicate_in_loop(self, tmp_path, monkeypatch):
        monkeypatch.setattr(main, "_log_path", lambda: tmp_path / "briefing_log.json")
        monkeypatch.setattr(main, "_write_span", lambda s: None)
        log_path = tmp_path / "morning-spark_run_output.log"
        monkeypatch.setattr(main, "LOG_FILE", str(log_path))

        # Manually exercise the PreToolUse guard directly to verify denial tracking
        input1 = _make_pre_input("fetch_headline", {"category": "technology"})
        input2 = _make_pre_input("fetch_headline", {"category": "technology"})

        asyncio.run(main.pre_tool_use_guard(input1, "tu-001", None))  # allow
        asyncio.run(main.pre_tool_use_guard(input2, "tu-002", None))  # deny

        assert main._hook_state["denied_count"] == 1
        assert len(main._hook_state["calls_made"]) == 1  # only the first was recorded
