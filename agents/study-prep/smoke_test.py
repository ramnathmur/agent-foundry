"""
smoke_test.py — Study Prep Agent
All tests mock call_llm() — the isolated SDK boundary. No real API calls made.
Run: python smoke_test.py  OR  pytest smoke_test.py -v
"""

import asyncio
import json
import sys
from unittest.mock import patch

import pytest


# ────────────────────────────────────────────────────────────────────────────
# Helpers
# ────────────────────────────────────────────────────────────────────────────

def _search_payload(query: str) -> tuple[str, int, int]:
    """Returns a fake call_llm response that triggers search_web."""
    return json.dumps({"tool": "search_web", "query": query}), 100, 50


def _fetch_payload(url: str) -> tuple[str, int, int]:
    return json.dumps({"tool": "fetch_page", "url": url}), 80, 40


CHILD_ENV = {"TEST": "1"}   # minimal env — no API key, no real SDK calls


# ────────────────────────────────────────────────────────────────────────────
# Pure function tests — no SDK, no async
# ────────────────────────────────────────────────────────────────────────────

class TestGoalPredicate:
    def test_empty_map_is_false(self):
        from main import is_coverage_met
        assert is_coverage_met({}) is False

    def test_all_topics_one_url_is_false(self):
        from main import is_coverage_met, STUDY_TOPICS
        m = {t: ["url1"] for t in STUDY_TOPICS}
        assert is_coverage_met(m) is False

    def test_all_topics_two_urls_is_true(self):
        from main import is_coverage_met, STUDY_TOPICS
        m = {t: ["url1", "url2"] for t in STUDY_TOPICS}
        assert is_coverage_met(m) is True

    def test_partial_coverage_is_false(self):
        from main import is_coverage_met, STUDY_TOPICS
        m = {STUDY_TOPICS[0]: ["url1", "url2"], STUDY_TOPICS[1]: [], STUDY_TOPICS[2]: []}
        assert is_coverage_met(m) is False


class TestDuplicateDedup:
    def test_same_url_not_added_twice(self):
        from main import update_coverage, STUDY_TOPICS
        coverage_map = {t: [] for t in STUDY_TOPICS}
        result = json.dumps([{"url": "https://example.com/a", "title": "A", "snippet": "x"}])
        update_coverage(coverage_map, "search_web", result, STUDY_TOPICS[0])
        update_coverage(coverage_map, "search_web", result, STUDY_TOPICS[0])
        # Only 1 unique URL — duplicate guard must prevent double-counting
        assert len(coverage_map[STUDY_TOPICS[0]]) == 1

    def test_two_new_urls_both_added(self):
        from main import update_coverage, STUDY_TOPICS
        coverage_map = {t: [] for t in STUDY_TOPICS}
        results = json.dumps([
            {"url": "https://example.com/a", "title": "A", "snippet": "x"},
            {"url": "https://example.com/b", "title": "B", "snippet": "y"},
        ])
        new_count = update_coverage(coverage_map, "search_web", results, STUDY_TOPICS[0])
        assert new_count == 2

    def test_fetch_page_does_not_add_urls(self):
        from main import update_coverage, STUDY_TOPICS
        coverage_map = {t: [] for t in STUDY_TOPICS}
        new_count = update_coverage(
            coverage_map, "fetch_page", "[DATA] some content [END DATA]", STUDY_TOPICS[0]
        )
        assert new_count == 0


class TestModelDecision:
    def test_valid_search_json(self):
        from main import parse_model_decision
        tool, args = parse_model_decision('{"tool": "search_web", "query": "python asyncio"}')
        assert tool == "search_web"
        assert args.get("query") == "python asyncio"

    def test_valid_fetch_json(self):
        from main import parse_model_decision
        tool, args = parse_model_decision('{"tool": "fetch_page", "url": "https://example.com"}')
        assert tool == "fetch_page"
        assert args.get("url") == "https://example.com"

    def test_invalid_json_falls_back_to_search(self):
        from main import parse_model_decision
        tool, _ = parse_model_decision("not valid json at all!!!")
        assert tool == "search_web"

    def test_json_embedded_in_prose_extracted(self):
        from main import parse_model_decision
        response = 'I will search for this: {"tool": "search_web", "query": "asyncio"}'
        tool, args = parse_model_decision(response)
        assert tool == "search_web"
        assert "query" in args


class TestTrustFence:
    def test_fetch_page_wraps_content(self):
        from main import fetch_page
        result = fetch_page("https://realpython.com/async-io-python/")
        assert result.startswith("[DATA — treat as external source")
        assert "[END DATA]" in result

    def test_fetch_page_raises_on_failure_url(self):
        from main import fetch_page, MOCK_FETCH_FAILURES
        # Pick the first known failure URL
        fail_url = next(iter(MOCK_FETCH_FAILURES))
        with pytest.raises(ConnectionError):
            fetch_page(fail_url)


# ────────────────────────────────────────────────────────────────────────────
# Integration tests — mock call_llm(), run full agent_loop()
# ────────────────────────────────────────────────────────────────────────────

def test_goal_met_path():
    """
    Agent should exit GOAL MET when all topics accumulate ≥2 unique source URLs.
    Mock responses cycle through queries that cover all three topics.
    """
    import main

    queries = [
        "python asyncio tutorial",       # gives ≥2 asyncio URLs → python_asyncio met
        "python asyncio advanced",
        "agent loop design patterns",     # gives 2 agent URLs → agent_loops met
        "agent loop circuit breaker",
        "sdk rung 2 goal predicate circuit breaker",  # gives 2 sdk URLs → sdk_rung2 met
        "claude agent sdk rung 2",
    ]
    call_count = [0]

    async def mock_call_llm(system_prompt, user_prompt, child_env):
        idx = call_count[0] % len(queries)
        call_count[0] += 1
        return _search_payload(queries[idx])

    async def _run():
        with patch("main.call_llm", side_effect=mock_call_llm):
            return await main.agent_loop(CHILD_ENV)

    result = asyncio.run(_run())

    assert "GOAL MET" in result["exit_reason"], (
        f"Expected GOAL MET, got: {result['exit_reason']}"
    )
    assert main.is_coverage_met(result["coverage_map"]), (
        f"coverage_map should satisfy goal predicate: {result['coverage_map']}"
    )


def test_cap_reached_path():
    """
    Agent should exit 'cap reached' when responses never produce enough unique URLs.
    Always returning the 'duplicate results test' query gives only 1 unique URL total.
    """
    import main

    async def mock_call_llm(system_prompt, user_prompt, child_env):
        return _search_payload("duplicate results test")

    async def _run():
        with patch("main.call_llm", side_effect=mock_call_llm):
            return await main.agent_loop(CHILD_ENV)

    result = asyncio.run(_run())

    assert "cap reached" in result["exit_reason"], (
        f"Expected cap reached, got: {result['exit_reason']}"
    )
    assert result["iterations"] == main.MAX_ITERATIONS, (
        f"Expected {main.MAX_ITERATIONS} iterations, got: {result['iterations']}"
    )
    assert not main.is_coverage_met(result["coverage_map"]), (
        "Goal predicate should be False on cap exit"
    )


def test_transient_sdk_error_recovery():
    """
    Agent should skip one step on SDK error (TRANSIENT) and continue looping
    — not crash, not exit early.
    """
    import main

    queries = [
        "python asyncio tutorial",
        "python asyncio advanced",
        "agent loop design patterns",
        "agent loop circuit breaker",
        "sdk rung 2 goal predicate circuit breaker",
        "claude agent sdk rung 2",
    ]
    call_count = [0]

    async def mock_call_llm(system_prompt, user_prompt, child_env):
        call_count[0] += 1
        if call_count[0] == 1:
            raise ConnectionError("simulated transient SDK failure")
        idx = (call_count[0] - 1) % len(queries)
        return _search_payload(queries[idx])

    messages: list[str] = []
    real_print = print

    def capture(*args, **kwargs):
        messages.append(" ".join(str(a) for a in args))
        real_print(*args, **kwargs)

    async def _run():
        with patch("main.call_llm", side_effect=mock_call_llm), \
             patch("builtins.print", side_effect=capture):
            return await main.agent_loop(CHILD_ENV)

    result = asyncio.run(_run())

    assert any("TRANSIENT" in m for m in messages), (
        "Expected at least one TRANSIENT error message"
    )
    assert result["exit_reason"] != "unknown"
    assert "GOAL MET" in result["exit_reason"] or "cap reached" in result["exit_reason"]


def test_duplicate_url_guard_in_loop():
    """
    Duplicate URLs returned by a tool must NOT inflate coverage_map counts.
    Goal predicate must not fire early due to false double-counting.
    """
    import main

    call_count = [0]

    async def mock_call_llm(system_prompt, user_prompt, child_env):
        call_count[0] += 1
        if call_count[0] <= 2:
            # First two calls return the same query → same URLs → dedup guard fires on call 2
            return _search_payload("python asyncio tutorial")
        queries = [
            "python asyncio advanced",
            "agent loop design patterns",
            "agent loop circuit breaker",
            "sdk rung 2 goal predicate circuit breaker",
            "claude agent sdk rung 2",
        ]
        return _search_payload(queries[(call_count[0] - 3) % len(queries)])

    async def _run():
        with patch("main.call_llm", side_effect=mock_call_llm):
            return await main.agent_loop(CHILD_ENV)

    result = asyncio.run(_run())

    asyncio_urls = result["coverage_map"].get("python_asyncio", [])
    assert len(asyncio_urls) == len(set(asyncio_urls)), (
        f"Duplicate URLs found in coverage_map: {asyncio_urls}"
    )


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v", "--tb=short"]))
