"""
smoke_test.py — Morning Intel Agent v1
Cycle 7 · Rung 8 · LATERAL-RIGHT

Four tests covering every branch path the main agent can take:
  1. Happy path   — all 3 specialists return high quality → briefing_complete() True
  2. Follow-up    — news returns low quality → re-dispatch → quality improves → goal met
  3. Cap exit     — sub-agent cap reached before goal → briefing_complete() False at exit
  4. Predicate    — unit tests for briefing_complete() logic in isolation

RUNG 8 LESSON — why we patch main.query, not claude_agent_sdk.query:
  When Python resolves `query` inside main.py, it uses the reference bound at import time
  in main's module namespace. Patching the sdk module's original `query` has no effect
  because main.query already points to the original function object.
  Solution: import query at MODULE LEVEL in main.py, then patch 'main.query'.
  This is why main.py uses: try: from claude_agent_sdk import query except ImportError: query = None
"""

import asyncio
import json
import sys
import types
import unittest
from unittest.mock import AsyncMock, patch, MagicMock

# ── ensure the agents/morning-intel directory is importable ──────────────────
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))


# ═══════════════════════════════════════════
# PURPOSE: Mock query factory — builds a deterministic ResultMessage-like object
# ACHIEVES: Lets tests control what each sub-agent "hears back from the model"
# DEPENDENCIES: json standard library
# ═══════════════════════════════════════════

def _make_result(text: str) -> types.SimpleNamespace:
    """Minimal duck-typed ResultMessage — only .text is required by main.py."""
    return types.SimpleNamespace(text=text, type="ResultMessage")


def _weather_response(quality: float = 0.9) -> str:
    return json.dumps({
        "section_type": "weather",
        "content": "Clear skies in Bangalore this morning, 26 C with a mild breeze. Carry an umbrella for afternoon showers.",
        "quality_score": quality,
        "gap_flag": quality < 0.6,
        "notes": "",
    })


def _news_response(quality: float = 0.9) -> str:
    return json.dumps({
        "section_type": "news",
        "content": "The IMF has revised its global growth forecast upward by 0.2 percent for 2026. Markets responded positively.",
        "quality_score": quality,
        "gap_flag": quality < 0.6,
        "notes": "",
    })


def _news_low_quality() -> str:
    return json.dumps({
        "section_type": "news",
        "content": "No headlines available.",
        "quality_score": 0.3,
        "gap_flag": True,
        "notes": "empty source",
    })


def _calendar_response(quality: float = 0.9) -> str:
    return json.dumps({
        "section_type": "calendar",
        "content": "Three high-priority events today, starting with a team standup at 9 AM. Client review at 11 AM is the anchor of your day.",
        "quality_score": quality,
        "gap_flag": quality < 0.6,
        "notes": "",
    })


def _synthesis_response(lead: str = "calendar") -> str:
    return json.dumps({
        "lead_section": lead,
        "alternatives": ["news", "weather"],
        "briefing": (
            f"Your most time-critical item today is the client review at 11 AM ({lead} leads). "
            "Markets are up on IMF growth revisions. Skies are clear this morning with afternoon showers expected."
        ),
    })


# ═══════════════════════════════════════════
# PURPOSE: Test 1 — Happy path
# AGENTIC TRAIT: Goal-directedness (briefing_complete() returns True on clean run)
# ACHIEVES: Verifies all 3 dispatches + synthesis → goal met
# ═══════════════════════════════════════════

class TestHappyPath(unittest.TestCase):
    """All three specialists return high quality → briefing_complete() True."""

    def test_goal_met_on_first_pass(self):
        # Sequence: weather call, news call, calendar call, synthesis call
        call_count = 0

        async def mock_query(prompt: str = "", **kwargs):
            # GOTCHA[query-is-async-generator]: real SDK query() is an async generator.
            # Mocks must yield (not return) so _run_query's `async for msg in query()` works.
            nonlocal call_count
            call_count += 1
            if "WeatherAnalyst" in prompt:
                yield _make_result(_weather_response(0.9))
            elif "NewsScanner" in prompt:
                yield _make_result(_news_response(0.9))
            elif "CalendarPrep" in prompt:
                yield _make_result(_calendar_response(0.9))
            else:
                # Synthesis call
                yield _make_result(_synthesis_response("calendar"))

        with patch("main.query", new=mock_query):
            import main
            main._reset_state()
            asyncio.run(main.main())

        self.assertTrue(
            main.briefing_complete(main._agent_state),
            "briefing_complete() must be True after clean three-specialist run",
        )
        self.assertIsNotNone(main._agent_state["final_briefing"])
        self.assertIsNotNone(main._agent_state["lead_section"])
        # All sections received and quality-passed
        for section_type, report in main._agent_state["sections"].items():
            self.assertIsNotNone(report, f"{section_type} section must not be None")
            self.assertGreaterEqual(
                report["quality_score"], main.MIN_QUALITY,
                f"{section_type} quality_score must be >= {main.MIN_QUALITY}",
            )


# ═══════════════════════════════════════════
# PURPOSE: Test 2 — Follow-up path
# AGENTIC TRAIT: Observe-reason-act (low quality → re-dispatch with new params)
# ACHIEVES: Verifies G3 — the agent detects the gap and corrects it
# ═══════════════════════════════════════════

class TestFollowUpPath(unittest.TestCase):
    """News returns low quality on first call → re-dispatch → quality improves → goal met."""

    def test_followup_on_low_news_quality(self):
        news_call_count = 0

        async def mock_query(prompt: str = "", **kwargs):
            nonlocal news_call_count
            if "WeatherAnalyst" in prompt:
                yield _make_result(_weather_response(0.9))
            elif "NewsScanner" in prompt:
                news_call_count += 1
                if news_call_count == 1:
                    yield _make_result(_news_low_quality())
                else:
                    yield _make_result(_news_response(0.85))
            elif "CalendarPrep" in prompt:
                yield _make_result(_calendar_response(0.9))
            else:
                yield _make_result(_synthesis_response("news"))

        with patch("main.query", new=mock_query):
            import main
            main._reset_state()
            asyncio.run(main.main())

        self.assertTrue(
            main.briefing_complete(main._agent_state),
            "Goal must be met after follow-up corrects low news quality",
        )
        self.assertGreaterEqual(
            news_call_count, 2,
            "NewsScanner must be called at least twice (initial + follow-up)",
        )
        # Agent should have dispatched more than 3 sub-agents (initial 3 + at least 1 follow-up)
        self.assertGreater(
            main._agent_state["sub_agents_dispatched"], 3,
            "sub_agents_dispatched must exceed 3 when a follow-up fires",
        )
        # Follow-up should be recorded in history
        self.assertIn(
            "news", main._agent_state["follow_up_history"],
            "follow_up_history must record the news re-dispatch",
        )


# ═══════════════════════════════════════════
# PURPOSE: Test 3 — Cap exit path
# AGENTIC TRAIT: Principled stop (G4 — both exit paths reachable)
# ACHIEVES: Verifies agent exits cleanly when MAX_SUBAGENTS reached without goal-met
# ═══════════════════════════════════════════

class TestCapExit(unittest.TestCase):
    """Sub-agent cap reached before goal → agent exits without briefing_complete()."""

    def test_cap_exit_when_quality_never_improves(self):
        # Every sub-agent call returns low quality → follow-up loop → cap fires
        async def mock_query(prompt: str = "", **kwargs):
            if "WeatherAnalyst" in prompt:
                yield _make_result(_weather_response(0.4))  # always low
            elif "NewsScanner" in prompt:
                yield _make_result(_news_low_quality())     # always low
            elif "CalendarPrep" in prompt:
                yield _make_result(_calendar_response(0.4)) # always low
            else:
                yield _make_result(_synthesis_response("weather"))

        with patch("main.query", new=mock_query):
            import main
            main._reset_state()
            asyncio.run(main.main())

        # Goal must not be met (all qualities below threshold)
        self.assertFalse(
            main.briefing_complete(main._agent_state),
            "briefing_complete() must remain False when quality never reaches threshold",
        )
        # Cap must have been respected
        self.assertLessEqual(
            main._agent_state["sub_agents_dispatched"], main.MAX_SUBAGENTS,
            "sub_agents_dispatched must not exceed MAX_SUBAGENTS",
        )


# ═══════════════════════════════════════════
# PURPOSE: Test 4 — briefing_complete() predicate unit tests
# AGENTIC TRAIT: Goal-directedness (predicate logic tested in isolation)
# ACHIEVES: Verifies all five arms of the G1 predicate independently
# ═══════════════════════════════════════════

class TestBriefingCompletePredicateUnit(unittest.TestCase):
    """Unit tests for briefing_complete() in isolation — no query() calls."""

    def setUp(self):
        import main
        self.fn = main.briefing_complete
        self.MIN_Q = main.MIN_QUALITY

    def _good_section(self, section_type: str) -> dict:
        return {"section_type": section_type, "content": "...", "quality_score": 0.9, "gap_flag": False, "notes": ""}

    def _low_section(self, section_type: str) -> dict:
        return {"section_type": section_type, "content": "...", "quality_score": 0.4, "gap_flag": True, "notes": ""}

    def test_returns_false_when_no_sections(self):
        state = {"sections": {"weather": None, "news": None, "calendar": None}, "synthesis_produced": False}
        self.assertFalse(self.fn(state))

    def test_returns_false_when_one_section_missing(self):
        state = {
            "sections": {
                "weather": self._good_section("weather"),
                "news": None,
                "calendar": self._good_section("calendar"),
            },
            "synthesis_produced": True,
        }
        self.assertFalse(self.fn(state))

    def test_returns_false_when_section_quality_too_low(self):
        state = {
            "sections": {
                "weather": self._good_section("weather"),
                "news": self._low_section("news"),
                "calendar": self._good_section("calendar"),
            },
            "synthesis_produced": True,
        }
        self.assertFalse(self.fn(state))

    def test_returns_false_when_synthesis_not_produced(self):
        state = {
            "sections": {
                "weather": self._good_section("weather"),
                "news": self._good_section("news"),
                "calendar": self._good_section("calendar"),
            },
            "synthesis_produced": False,
        }
        self.assertFalse(self.fn(state))

    def test_returns_true_when_all_conditions_met(self):
        state = {
            "sections": {
                "weather": self._good_section("weather"),
                "news": self._good_section("news"),
                "calendar": self._good_section("calendar"),
            },
            "synthesis_produced": True,
        }
        self.assertTrue(self.fn(state))

    def test_boundary_quality_exactly_at_threshold(self):
        # quality_score == MIN_QUALITY should pass (>= not >)
        at_threshold = {"section_type": "news", "content": "...", "quality_score": self.MIN_Q, "gap_flag": False, "notes": ""}
        state = {
            "sections": {
                "weather": self._good_section("weather"),
                "news": at_threshold,
                "calendar": self._good_section("calendar"),
            },
            "synthesis_produced": True,
        }
        self.assertTrue(self.fn(state))

    def test_boundary_quality_just_below_threshold(self):
        just_below = {"section_type": "news", "content": "...", "quality_score": self.MIN_Q - 0.01, "gap_flag": True, "notes": ""}
        state = {
            "sections": {
                "weather": self._good_section("weather"),
                "news": just_below,
                "calendar": self._good_section("calendar"),
            },
            "synthesis_produced": True,
        }
        self.assertFalse(self.fn(state))


if __name__ == "__main__":
    unittest.main(verbosity=2)
