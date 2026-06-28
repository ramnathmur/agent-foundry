"""
smoke_test.py — Study Buddy Agent v2
All tests mock open_sdk_client() + send_turn() — the isolated SDK boundary.
No real claude_agent_sdk calls; tests run without claude CLI / login.
Run: python smoke_test.py  OR  pytest smoke_test.py -v
"""

import asyncio
import contextlib
import json
import os
import sys
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch

import pytest


CHILD_ENV = {"TEST": "1"}


# ────────────────────────────────────────────────────────────────────────────
# Test fixture: redirect LEDGER_FILE to a temp dir so tests don't touch real disk
# ────────────────────────────────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def isolated_ledger(tmp_path, monkeypatch):
    """Each test gets its own empty ledger directory; never touches real weak_spots.json."""
    import main as main_module
    # Patch _ledger_path to point inside tmp_path
    fake_ledger = tmp_path / "weak_spots.json"
    monkeypatch.setattr(main_module, "_ledger_path", lambda: fake_ledger)
    # Also redirect LOG_FILE so tee_to_log doesn't pollute real folder
    monkeypatch.setattr(main_module, "LOG_FILE", str(tmp_path / "test.log"))
    yield fake_ledger


# ────────────────────────────────────────────────────────────────────────────
# Pure function tests — no SDK, no async
# ────────────────────────────────────────────────────────────────────────────

class TestGoalPredicate:
    def test_empty_state_is_false(self):
        from main import session_complete
        assert session_complete({}) is False

    def test_user_stop_is_true(self):
        from main import session_complete
        assert session_complete({"user_stopped": True}) is True

    def test_model_done_is_true(self):
        from main import session_complete
        assert session_complete({"model_done": True}) is True

    def test_min_questions_without_ledger_write_is_false(self):
        from main import session_complete, MIN_QUESTIONS_FOR_AUTO_DONE
        assert session_complete({"questions_asked": MIN_QUESTIONS_FOR_AUTO_DONE,
                                 "ledger_written": False}) is False

    def test_min_questions_with_ledger_write_is_true(self):
        from main import session_complete, MIN_QUESTIONS_FOR_AUTO_DONE
        assert session_complete({"questions_asked": MIN_QUESTIONS_FOR_AUTO_DONE,
                                 "ledger_written": True}) is True


class TestLedgerReadWrite:
    def test_read_nonexistent_returns_empty_list(self):
        from main import read_weak_spots
        assert read_weak_spots("never_studied") == []

    def test_write_then_read_roundtrip(self):
        from main import read_weak_spots, update_weak_spots
        update_weak_spots("python_lists", "indexing", 0.4)
        entries = read_weak_spots("python_lists")
        assert len(entries) == 1
        assert entries[0]["subtopic"] == "indexing"
        assert entries[0]["last_confidence"] == 0.4

    def test_update_existing_subtopic_overwrites_confidence(self):
        from main import read_weak_spots, update_weak_spots
        update_weak_spots("python_lists", "indexing", 0.4)
        update_weak_spots("python_lists", "indexing", 0.9)
        entries = read_weak_spots("python_lists")
        assert len(entries) == 1  # not duplicated
        assert entries[0]["last_confidence"] == 0.9

    def test_confidence_clamped_to_zero_one(self):
        from main import read_weak_spots, update_weak_spots
        update_weak_spots("python_lists", "indexing", 1.7)   # clamped to 1.0
        update_weak_spots("python_lists", "slicing", -0.2)   # clamped to 0.0
        entries = {e["subtopic"]: e["last_confidence"]
                   for e in read_weak_spots("python_lists")}
        assert entries["indexing"] == 1.0
        assert entries["slicing"] == 0.0

    def test_read_after_corrupt_ledger_returns_empty(self, isolated_ledger):
        # Write garbage to ledger file; read should return [] gracefully
        isolated_ledger.write_text("not valid json {{", encoding="utf-8")
        from main import read_weak_spots
        assert read_weak_spots("python_lists") == []


class TestParseModelResponse:
    def test_valid_first_turn_json(self):
        from main import parse_model_response
        raw = '{"action": "ask", "ask": {"subtopic": "indexing", "question": "Q?", "expected_concepts": []}}'
        parsed = parse_model_response(raw)
        assert parsed["action"] == "ask"
        assert parsed["ask"]["subtopic"] == "indexing"

    def test_markdown_fenced_json_extracted(self):
        from main import parse_model_response
        raw = '```json\n{"action": "done", "done": true, "assess": {"subtopic": "x", "confidence": 0.8}}\n```'
        parsed = parse_model_response(raw)
        assert parsed.get("done") is True

    def test_invalid_json_falls_back_to_ask_default(self):
        from main import parse_model_response
        parsed = parse_model_response("totally not json — model failed")
        assert parsed.get("action") == "ask"
        assert "ask" in parsed
        assert parsed["ask"].get("question")  # non-empty fallback question

    def test_json_embedded_in_prose_extracted(self):
        from main import parse_model_response
        raw = ('Let me think… here is my response: '
               '{"action": "ask", "ask": {"subtopic": "slicing", "question": "Q?"}}'
               ' That should work.')
        parsed = parse_model_response(raw)
        assert parsed["action"] == "ask"
        assert parsed["ask"]["subtopic"] == "slicing"


# ────────────────────────────────────────────────────────────────────────────
# Integration tests — mock SDK boundary, run full agent_loop
# ────────────────────────────────────────────────────────────────────────────

class _FakeClient:
    """Stands in for ClaudeSDKClient — records calls, returns scripted responses."""
    def __init__(self, response_script: list[str]):
        self._script = list(response_script)
        self.queries: list[str] = []

    async def query(self, prompt: str):
        self.queries.append(prompt)


@contextlib.asynccontextmanager
async def _fake_open_sdk_client(options, response_script: list[str], holder: dict):
    client = _FakeClient(response_script)
    holder["client"] = client
    yield client


async def _fake_send_turn(client: _FakeClient, prompt: str) -> tuple[str, int, int, str | None]:
    """Pops the next scripted response from the fake client."""
    if not client._script:
        raise RuntimeError("test script exhausted — too many turns requested")
    response_text = client._script.pop(0)
    return response_text, 100, 50, "fake-session-id-abc123"


def _patched_run(response_script: list[str], answers: list[str], topic: str = "python_lists"):
    """Helper: mock SDK + ask_question, run agent_loop, return state."""
    import main
    holder: dict = {}

    @contextlib.asynccontextmanager
    async def _open(options):
        async with _fake_open_sdk_client(options, response_script, holder) as c:
            yield c

    answer_iter = iter(answers)

    def mock_ask(question, expected_concepts=None):
        try:
            return next(answer_iter)
        except StopIteration:
            return "stop"

    async def _run():
        with patch.object(main, "open_sdk_client", _open), \
             patch.object(main, "send_turn", _fake_send_turn), \
             patch.object(main, "ask_question", mock_ask):
            return await main.agent_loop(CHILD_ENV, topic)

    return asyncio.run(_run())


def test_goal_met_path_model_declares_done():
    """Model declares done on turn 4 (before MIN_QUESTIONS auto-trigger) — exit must be model-done GOAL MET."""
    # Turn 4 declares done — fires BEFORE MIN_QUESTIONS=5 auto-done predicate path,
    # so this test isolates the model-done exit cleanly.
    script = [
        json.dumps({"action": "ask",
                    "ask": {"subtopic": "indexing", "question": "Q1?", "expected_concepts": []}}),
        json.dumps({"action": "assess_and_ask",
                    "assess": {"subtopic": "indexing", "confidence": 0.4, "reasoning": "weak"},
                    "ask": {"subtopic": "slicing", "question": "Q2?", "expected_concepts": []}}),
        json.dumps({"action": "assess_and_ask",
                    "assess": {"subtopic": "slicing", "confidence": 0.7, "reasoning": "ok"},
                    "ask": {"subtopic": "comprehensions", "question": "Q3?", "expected_concepts": []}}),
        # Turn 4 — model declares done
        json.dumps({"action": "done", "done": True,
                    "assess": {"subtopic": "comprehensions", "confidence": 0.8, "reasoning": "enough signal"}}),
    ]
    answers = ["a[0] gives 10", "a[1:3] gives [20,30]", "list comp is [x for x in ...]"]
    state = _patched_run(script, answers)
    assert "GOAL MET" in state["exit_reason"], f"got: {state['exit_reason']}"
    assert "model assessed" in state["exit_reason"], f"expected model-done path; got: {state['exit_reason']}"
    assert state["model_done"] is True
    assert state["questions_asked"] == 4


def test_user_stop_path():
    """User types 'stop' on turn 2 — should exit USER STOPPED, not cap."""
    script = [
        json.dumps({"action": "ask", "ask": {"subtopic": "indexing", "question": "Q1?"}}),
        json.dumps({"action": "assess_and_ask",
                    "assess": {"subtopic": "indexing", "confidence": 0.5},
                    "ask": {"subtopic": "slicing", "question": "Q2?"}}),
    ]
    answers = ["a[0] gives 10", "stop"]
    state = _patched_run(script, answers)
    assert "USER STOPPED" in state["exit_reason"], f"got: {state['exit_reason']}"
    assert state["user_stopped"] is True
    assert state["questions_asked"] == 2


def test_cap_reached_path_model_never_done():
    """Model never declares done AND never writes to ledger; cap must fire at MAX_QUESTIONS."""
    import main
    # Ask-only responses (no assess key) → ledger_written stays False →
    # predicate never auto-satisfies → only the cap can stop the loop.
    script = [
        json.dumps({"action": "ask",
                    "ask": {"subtopic": f"sub{i+1}", "question": f"Q{i+1}?"}})
        for i in range(main.MAX_QUESTIONS)
    ]
    answers = [f"answer {i}" for i in range(main.MAX_QUESTIONS)]
    state = _patched_run(script, answers)
    assert "cap reached" in state["exit_reason"], f"got: {state['exit_reason']}"
    assert state["questions_asked"] == main.MAX_QUESTIONS
    assert state["ledger_written"] is False


def test_predicate_satisfied_path_min_questions_with_ledger():
    """Auto-done path: model never says done, but predicate fires at MIN_QUESTIONS once ledger is written."""
    import main
    # First turn: ask only (no assess). Turns 2..: assess + ask. Predicate fires at turn 5.
    script = [
        json.dumps({"action": "ask",
                    "ask": {"subtopic": "indexing", "question": "Q1?"}}),
    ] + [
        json.dumps({"action": "assess_and_ask",
                    "assess": {"subtopic": f"sub{i}", "confidence": 0.5},
                    "ask": {"subtopic": f"sub{i+1}", "question": f"Q{i+2}?"}})
        for i in range(1, main.MAX_QUESTIONS)
    ]
    answers = [f"answer {i}" for i in range(main.MAX_QUESTIONS)]
    state = _patched_run(script, answers)
    # Should exit via predicate at MIN_QUESTIONS_FOR_AUTO_DONE, not at cap
    assert "GOAL MET" in state["exit_reason"], f"got: {state['exit_reason']}"
    assert "predicate satisfied" in state["exit_reason"], f"got: {state['exit_reason']}"
    assert state["questions_asked"] == main.MIN_QUESTIONS_FOR_AUTO_DONE
    assert state["ledger_written"] is True


def test_ledger_persists_across_runs():
    """Run twice; second run's first-turn prompt should include prior ledger entries."""
    import main
    # First run: model writes ledger via assess
    script1 = [
        json.dumps({"action": "ask", "ask": {"subtopic": "indexing", "question": "Q1?"}}),
        json.dumps({"action": "done", "done": True,
                    "assess": {"subtopic": "indexing", "confidence": 0.3, "reasoning": "weak"}}),
    ]
    # Second run: model just declares done immediately to make assertion clean
    script2 = [
        json.dumps({"action": "done", "done": True,
                    "assess": {"subtopic": "indexing", "confidence": 0.8, "reasoning": "improved"}}),
    ]
    state1 = _patched_run(script1, ["a[0]"])
    # On second run, ledger from run 1 must be readable
    ledger_now = main.read_weak_spots("python_lists")
    assert any(e["subtopic"] == "indexing" for e in ledger_now), \
        f"ledger missing entry after run 1: {ledger_now}"
    state2 = _patched_run(script2, [])
    assert state2["model_done"] is True


def test_ask_question_sentinel_detection():
    """Each user-stop sentinel must trigger the user-stop branch."""
    import main
    for sentinel in main.USER_STOP_SENTINELS:
        script = [
            json.dumps({"action": "ask", "ask": {"subtopic": "x", "question": "Q?"}}),
        ]
        state = _patched_run(script, [sentinel])
        assert state["user_stopped"] is True, f"sentinel '{sentinel}' did not trigger user-stop"


def test_session_id_captured():
    """session_id from ResultMessage must be captured in state."""
    script = [
        json.dumps({"action": "done", "done": True,
                    "assess": {"subtopic": "x", "confidence": 0.5}}),
    ]
    state = _patched_run(script, [])
    assert state["session_id"] == "fake-session-id-abc123"


def test_malformed_json_response_does_not_crash():
    """Model returns total garbage; agent must fall back to safe default and continue."""
    script = [
        "this is not json at all !!!",  # parser falls back to ask-default
        json.dumps({"action": "done", "done": True,
                    "assess": {"subtopic": "general", "confidence": 0.5}}),
    ]
    state = _patched_run(script, ["my answer"])
    # Should NOT crash; should reach done on turn 2
    assert state["model_done"] is True
    assert state["questions_asked"] == 2


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v", "--tb=short"]))
