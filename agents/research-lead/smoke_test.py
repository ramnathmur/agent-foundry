"""
Smoke tests for Research Project Lead (rung 8 — subagents + context compaction).

Mocks the SDK at two levels:
  1. Main agent's query() call (planning/synthesis)
  2. Sub-researcher's query() call (summarization)

Tests both exit paths: GOAL MET and cap exits.
Tests run_data.json output.
Tests goal predicate logic.
Tests app memory (research_briefs.json).
"""

import asyncio
import json
import os
import sys
import types
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio

# Add agent directory to path
AGENT_DIR = Path(__file__).parent
sys.path.insert(0, str(AGENT_DIR))

# ═══════════════════════════════════════════
# PURPOSE: SDK mock factories
# ACHIEVES: Deterministic test fixtures at two agent levels
# ═══════════════════════════════════════════

def make_mock_result(text: str, input_tokens: int = 100, output_tokens: int = 50) -> MagicMock:
    """Create a mock SDK result with usage tracking."""
    result = MagicMock()
    result.text = text
    result.usage = MagicMock()
    result.usage.input_tokens = input_tokens
    result.usage.output_tokens = output_tokens
    return result


def make_planning_response(angles: list[str]) -> str:
    """Create a mock planning response selecting specific angles."""
    return json.dumps({
        "selected_angles": angles,
        "reasoning": f"Selected {', '.join(angles)} for comprehensive coverage."
    })


def make_sub_researcher_response(
    confidence: float = 0.8,
    gap_flagged: bool = False,
    gap_description: str | None = None
) -> str:
    """Create a mock sub-researcher summary response."""
    return json.dumps({
        "summary": "Mock research findings synthesized into a coherent summary.",
        "confidence": confidence,
        "gap_flagged": gap_flagged,
        "gap_description": gap_description
    })


def make_synthesis_response(confidence: float = 0.8) -> str:
    """Create a mock synthesis response."""
    return json.dumps({
        "briefing": "This is the synthesized briefing covering all angles of the research question.",
        "confidence": confidence,
        "key_tradeoffs": ["Speed vs depth", "Breadth vs focus"],
        "remaining_gaps": ["Long-term longitudinal data"]
    })


# ═══════════════════════════════════════════
# PURPOSE: Fixtures
# ACHIEVES: Clean test environment per test
# ═══════════════════════════════════════════

@pytest.fixture(autouse=True)
def clean_env(tmp_path, monkeypatch):
    """Ensure no real SDK calls and clean file state."""
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    # Redirect output files to tmp
    monkeypatch.setattr("main.BRIEFINGS_FILE", tmp_path / "research_briefs.json")
    monkeypatch.setattr("main.RUN_DATA_FILE", tmp_path / "run_data.json")


# ═══════════════════════════════════════════
# PURPOSE: Goal predicate tests
# ACHIEVES: G1 — predicate logic verified in isolation
# ═══════════════════════════════════════════

class TestGoalPredicate:
    """Test is_goal_met() predicate logic."""

    def test_all_conditions_met(self):
        import main
        state = {
            "all_dispatched_returned": True,
            "synthesis_produced": True,
            "synthesis_confidence": 0.8
        }
        assert main.is_goal_met(state) is True

    def test_missing_returns(self):
        import main
        state = {
            "all_dispatched_returned": False,
            "synthesis_produced": True,
            "synthesis_confidence": 0.8
        }
        assert main.is_goal_met(state) is False

    def test_no_synthesis(self):
        import main
        state = {
            "all_dispatched_returned": True,
            "synthesis_produced": False,
            "synthesis_confidence": 0.0
        }
        assert main.is_goal_met(state) is False

    def test_low_confidence(self):
        import main
        state = {
            "all_dispatched_returned": True,
            "synthesis_produced": True,
            "synthesis_confidence": 0.5
        }
        assert main.is_goal_met(state) is False

    def test_exact_threshold(self):
        import main
        state = {
            "all_dispatched_returned": True,
            "synthesis_produced": True,
            "synthesis_confidence": 0.7
        }
        assert main.is_goal_met(state) is True

    def test_empty_state(self):
        import main
        assert main.is_goal_met({}) is False


# ═══════════════════════════════════════════
# PURPOSE: Sub-researcher tests
# ACHIEVES: Rung 8 — independent context verified
# ═══════════════════════════════════════════

class TestSubResearcher:
    """Test sub-researcher function with mocked SDK."""

    @pytest.mark.asyncio
    async def test_successful_research(self):
        import main
        run_data = main.RunDataCollector()

        mock_result = make_mock_result(
            make_sub_researcher_response(confidence=0.85)
        )

        with patch("main.query", new_callable=AsyncMock, return_value=mock_result):
            report = await main.run_sub_researcher(
                "technical", "test question", run_data, 0
            )

        assert report["angle"] == "technical"
        assert report["confidence"] == 0.85
        assert report["gap_flagged"] is False
        assert len(report["findings"]) > 0
        assert len(run_data.sub_researchers) == 1

    @pytest.mark.asyncio
    async def test_gap_flagged(self):
        import main
        run_data = main.RunDataCollector()

        mock_result = make_mock_result(
            make_sub_researcher_response(
                confidence=0.4,
                gap_flagged=True,
                gap_description="Missing recent data"
            )
        )

        with patch("main.query", new_callable=AsyncMock, return_value=mock_result):
            report = await main.run_sub_researcher(
                "user", "test question", run_data, 0
            )

        assert report["gap_flagged"] is True
        assert report["confidence"] == 0.4
        assert "Missing recent data" in report["gap_description"]

    @pytest.mark.asyncio
    async def test_empty_angle(self):
        """Test angle with no sources in mock DB."""
        import main
        run_data = main.RunDataCollector()

        # Use a non-existent angle
        original_db = main.MOCK_RESEARCH_DB.copy()
        try:
            report = await main.run_sub_researcher(
                "nonexistent_angle", "test question", run_data, 0
            )
            assert report["confidence"] == 0.3
            assert report["gap_flagged"] is True
        finally:
            main.MOCK_RESEARCH_DB.update(original_db)

    @pytest.mark.asyncio
    async def test_sdk_error_handling(self):
        """Test graceful handling of SDK errors in sub-researcher."""
        import main
        run_data = main.RunDataCollector()

        with patch("main.query", new_callable=AsyncMock, side_effect=Exception("SDK error")):
            report = await main.run_sub_researcher(
                "technical", "test question", run_data, 0
            )

        assert report["confidence"] == 0.3
        assert report["gap_flagged"] is True
        assert "error" in report["summary"].lower()

    @pytest.mark.asyncio
    async def test_confidence_clamping(self):
        """Test that confidence values are clamped to [0, 1]."""
        import main
        run_data = main.RunDataCollector()

        # Response with confidence > 1.0
        mock_result = make_mock_result(
            json.dumps({
                "summary": "test",
                "confidence": 1.5,
                "gap_flagged": False,
                "gap_description": None
            })
        )

        with patch("main.query", new_callable=AsyncMock, return_value=mock_result):
            report = await main.run_sub_researcher(
                "technical", "test question", run_data, 0
            )

        assert report["confidence"] == 1.0

    @pytest.mark.asyncio
    async def test_markdown_fence_handling(self):
        """Test that markdown-fenced JSON is parsed correctly."""
        import main
        run_data = main.RunDataCollector()

        fenced_response = "```json\n" + make_sub_researcher_response(confidence=0.9) + "\n```"
        mock_result = make_mock_result(fenced_response)

        with patch("main.query", new_callable=AsyncMock, return_value=mock_result):
            report = await main.run_sub_researcher(
                "technical", "test question", run_data, 0
            )

        assert report["confidence"] == 0.9


# ═══════════════════════════════════════════
# PURPOSE: App memory tests
# ACHIEVES: Briefing persistence verified
# ═══════════════════════════════════════════

class TestAppMemory:
    """Test research_briefs.json persistence."""

    def test_load_empty(self, tmp_path, monkeypatch):
        import main
        monkeypatch.setattr("main.BRIEFINGS_FILE", tmp_path / "nonexistent.json")
        assert main.load_briefings() == []

    def test_save_and_load(self, tmp_path, monkeypatch):
        import main
        briefings_file = tmp_path / "briefings.json"
        monkeypatch.setattr("main.BRIEFINGS_FILE", briefings_file)

        briefing = {"question": "test", "confidence": 0.8}
        main.save_briefing(briefing)

        loaded = main.load_briefings()
        assert len(loaded) == 1
        assert loaded[0]["question"] == "test"

    def test_corrupt_file(self, tmp_path, monkeypatch):
        import main
        briefings_file = tmp_path / "briefings.json"
        briefings_file.write_text("not valid json{{{", encoding="utf-8")
        monkeypatch.setattr("main.BRIEFINGS_FILE", briefings_file)

        assert main.load_briefings() == []

    def test_accumulation(self, tmp_path, monkeypatch):
        import main
        briefings_file = tmp_path / "briefings.json"
        monkeypatch.setattr("main.BRIEFINGS_FILE", briefings_file)

        main.save_briefing({"question": "q1", "confidence": 0.7})
        main.save_briefing({"question": "q2", "confidence": 0.9})

        loaded = main.load_briefings()
        assert len(loaded) == 2


# ═══════════════════════════════════════════
# PURPOSE: Run data collector tests
# ACHIEVES: Structured output for HTML generation verified
# ═══════════════════════════════════════════

class TestRunDataCollector:
    """Test the RunDataCollector for run_data.json output."""

    def test_event_collection(self):
        import main
        collector = main.RunDataCollector()
        collector.add_event("boot", "AGENT BOOT", "v1.0", narrative="test", phase="birth")
        assert len(collector.events) == 1
        assert collector.events[0]["type"] == "boot"
        assert collector.events[0]["narrative"] == "test"

    def test_phase_tracking(self):
        import main
        collector = main.RunDataCollector()
        collector.start_phase("birth", "The Agent Wakes Up", "🌅")
        assert len(collector.phases) == 1
        assert collector.phases[0]["name"] == "birth"

    def test_sub_researcher_tracking(self):
        import main
        collector = main.RunDataCollector()
        collector.selected_angles = ["technical", "user"]
        collector.add_sub_researcher("technical", "q", {"confidence": 0.8})
        collector.add_sub_researcher("user", "q", {"confidence": 0.7})
        collector.add_sub_researcher("technical", "follow-up q", {"confidence": 0.9})

        assert len(collector.sub_researchers) == 3
        assert collector.sub_researchers[0]["is_followup"] is False
        assert collector.sub_researchers[2]["is_followup"] is True

    def test_save_json(self, tmp_path):
        import main
        collector = main.RunDataCollector()
        collector.question = "test question"
        collector.selected_angles = ["technical"]
        collector.outcome = "GOAL MET"

        save_path = tmp_path / "run_data.json"
        original_path = main.RUN_DATA_FILE
        main.RUN_DATA_FILE = save_path
        try:
            collector.save()
            assert save_path.exists()
            data = json.loads(save_path.read_text(encoding="utf-8"))
            assert data["agent"] == "research-lead"
            assert data["question"] == "test question"
            assert data["outcome"] == "GOAL MET"
        finally:
            main.RUN_DATA_FILE = original_path


# ═══════════════════════════════════════════
# PURPOSE: Full main() integration test — GOAL MET path
# ACHIEVES: Happy path end-to-end with mocked SDK
# ═══════════════════════════════════════════

class TestMainGoalMet:
    """Test the full agent loop — GOAL MET exit."""

    @pytest.mark.asyncio
    async def test_goal_met_path(self, tmp_path, monkeypatch, capsys):
        import main
        monkeypatch.setattr("main.BRIEFINGS_FILE", tmp_path / "briefings.json")
        monkeypatch.setattr("main.RUN_DATA_FILE", tmp_path / "run_data.json")

        call_count = 0

        async def mock_query(prompt: str, max_tokens: int = 500, **kwargs):
            nonlocal call_count
            call_count += 1

            if "Research Project Lead planning" in prompt:
                return make_mock_result(
                    make_planning_response(["technical", "user", "contrarian"])
                )
            elif "specialist researcher" in prompt:
                return make_mock_result(
                    make_sub_researcher_response(confidence=0.85)
                )
            elif "final briefing" in prompt:
                return make_mock_result(
                    make_synthesis_response(confidence=0.8)
                )
            else:
                return make_mock_result('{"summary": "fallback", "confidence": 0.7, "gap_flagged": false}')

        with patch("main.query", side_effect=mock_query):
            await main.main()

        captured = capsys.readouterr()
        output = captured.out

        # Verify key output elements
        assert "[AGENT BOOT]" in output
        assert "[GOAL SET]" in output
        assert "[MODEL DECISION]" in output
        assert "[GOAL PREDICATE]" in output
        assert "GOAL MET" in output
        assert "AGENT SUMMARY" in output
        assert "[SDK →]" in output
        assert "SESSION MEMORY" in output or "APP MEMORY" in output

        # Verify run_data.json was written
        run_data_file = tmp_path / "run_data.json"
        assert run_data_file.exists()
        run_data = json.loads(run_data_file.read_text(encoding="utf-8"))
        assert run_data["outcome"] == "GOAL MET"

        # Verify briefing was saved
        briefings_file = tmp_path / "briefings.json"
        assert briefings_file.exists()


# ═══════════════════════════════════════════
# PURPOSE: Full main() integration test — CAP EXIT path
# ACHIEVES: Branch reachability for cap exits
# ═══════════════════════════════════════════

class TestMainCapExit:
    """Test cap exit paths are reachable."""

    @pytest.mark.asyncio
    async def test_synthesis_below_threshold(self, tmp_path, monkeypatch, capsys):
        """Synthesis confidence below threshold triggers cap exit."""
        import main
        monkeypatch.setattr("main.BRIEFINGS_FILE", tmp_path / "briefings.json")
        monkeypatch.setattr("main.RUN_DATA_FILE", tmp_path / "run_data.json")
        monkeypatch.setattr("main.MAX_SYNTHESIS_TURNS", 1)

        async def mock_query(prompt: str, max_tokens: int = 500, **kwargs):
            if "planning" in prompt.lower():
                return make_mock_result(
                    make_planning_response(["technical", "user"])
                )
            elif "specialist" in prompt.lower():
                return make_mock_result(
                    make_sub_researcher_response(confidence=0.85)
                )
            elif "final briefing" in prompt.lower() or "synthesis" in prompt.lower():
                return make_mock_result(
                    make_synthesis_response(confidence=0.4)
                )
            else:
                return make_mock_result('{"summary": "fallback", "confidence": 0.7, "gap_flagged": false}')

        with patch("main.query", side_effect=mock_query):
            await main.main()

        captured = capsys.readouterr()
        assert "EXIT:" in captured.out or "synthesis" in captured.out.lower()

    @pytest.mark.asyncio
    async def test_follow_up_path(self, tmp_path, monkeypatch, capsys):
        """Gaps in sub-researcher reports trigger follow-up dispatches."""
        import main
        monkeypatch.setattr("main.BRIEFINGS_FILE", tmp_path / "briefings.json")
        monkeypatch.setattr("main.RUN_DATA_FILE", tmp_path / "run_data.json")

        call_count = 0

        async def mock_query(prompt: str, max_tokens: int = 500, **kwargs):
            nonlocal call_count
            call_count += 1

            if "planning" in prompt.lower():
                return make_mock_result(
                    make_planning_response(["technical", "user"])
                )
            elif "specialist" in prompt.lower() or "follow up" in prompt.lower():
                if call_count <= 3:
                    return make_mock_result(
                        make_sub_researcher_response(
                            confidence=0.4,
                            gap_flagged=True,
                            gap_description="Missing recent data"
                        )
                    )
                else:
                    return make_mock_result(
                        make_sub_researcher_response(confidence=0.85)
                    )
            elif "final briefing" in prompt.lower():
                return make_mock_result(
                    make_synthesis_response(confidence=0.8)
                )
            else:
                return make_mock_result('{"summary": "fallback", "confidence": 0.7, "gap_flagged": false}')

        with patch("main.query", side_effect=mock_query):
            await main.main()

        captured = capsys.readouterr()
        assert "LOOP FEEDBACK" in captured.out
        assert "follow-up" in captured.out.lower() or "Follow-up" in captured.out


# ═══════════════════════════════════════════
# PURPOSE: Grep contract verification
# ACHIEVES: FR-D4 QA contract compliance
# ═══════════════════════════════════════════

class TestGrepContract:
    """Verify the QA grep contract for main.py."""

    @pytest.fixture
    def main_source(self):
        return (AGENT_DIR / "main.py").read_text(encoding="utf-8")

    def test_trait_annotations(self, main_source):
        assert main_source.count("TRAIT[") >= 5

    def test_gate_annotations(self, main_source):
        assert main_source.count("GATE[") >= 5

    def test_gotcha_annotations(self, main_source):
        assert main_source.count("GOTCHA[") >= 1

    def test_agent_boot(self, main_source):
        assert "[AGENT BOOT]" in main_source

    def test_goal_set(self, main_source):
        assert "[GOAL SET]" in main_source

    def test_goal_predicate(self, main_source):
        assert "[GOAL PREDICATE]" in main_source

    def test_model_decision(self, main_source):
        assert "[MODEL DECISION]" in main_source

    def test_loop_feedback(self, main_source):
        assert "[LOOP FEEDBACK]" in main_source

    def test_context_tracker(self, main_source):
        assert "[CONTEXT]" in main_source

    def test_sdk_boundary(self, main_source):
        assert "[SDK →]" in main_source

    def test_memory_labels(self, main_source):
        assert "SESSION MEMORY" in main_source or "APP MEMORY" in main_source

    def test_agent_summary(self, main_source):
        assert "AGENT SUMMARY" in main_source

    def test_structured_headers(self, main_source):
        assert main_source.count("═══") >= 5


# ═══════════════════════════════════════════
# PURPOSE: MessageLens tests
# ACHIEVES: Observability helper verified
# ═══════════════════════════════════════════

class TestMessageLens:
    """Test the MessageLens helper renders correctly."""

    def test_result_message(self, capsys):
        import main
        msg = MagicMock()
        type(msg).__name__ = "ResultMessage"
        msg.text = "Hello world from the model"
        main.message_lens(msg, "test")
        captured = capsys.readouterr()
        assert "┆" in captured.out
        assert "ResultMessage" in captured.out

    def test_assistant_with_tools(self, capsys):
        import main
        msg = MagicMock()
        type(msg).__name__ = "AssistantMessage"
        tool_block = MagicMock()
        tool_block.type = "tool_use"
        tool_block.name = "spawn_researcher"
        msg.content = [tool_block]
        main.message_lens(msg, "test")
        captured = capsys.readouterr()
        assert "spawn_researcher" in captured.out


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
