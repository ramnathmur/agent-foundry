"""
smoke_test.py — Recipe Companion Agent v1
All tests mock open_sdk_client() + send_turn() — the isolated SDK boundary.
The five @tool-decorated functions are tested as bare async functions (no SDK).
Run: python smoke_test.py  OR  pytest smoke_test.py -v
"""

import asyncio
import contextlib
import json
import sys
from unittest.mock import patch

import pytest


CHILD_ENV = {"TEST": "1"}


# ────────────────────────────────────────────────────────────────────────────
# Test fixture: redirect ledger paths to temp dir; no real disk writes
# ────────────────────────────────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def isolated_ledgers(tmp_path, monkeypatch):
    """Each test gets its own ledger directory; never touches real files."""
    import main as main_module

    def fake_ledger_path(filename):
        return tmp_path / filename

    monkeypatch.setattr(main_module, "_ledger_path", fake_ledger_path)
    monkeypatch.setattr(main_module, "LOG_FILE", str(tmp_path / "test.log"))
    # Seed a small pantry so demo runs have something to find
    pantry_file = tmp_path / "pantry.json"
    pantry_file.write_text(json.dumps([
        "spaghetti", "eggs", "parmesan", "salt", "black pepper",
        "flour", "milk", "butter", "lettuce", "tomato",
    ]), encoding="utf-8")
    yield tmp_path


# ────────────────────────────────────────────────────────────────────────────
# Pure function tests — no SDK, no async loop
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

    def test_partial_progress_is_false(self):
        from main import session_complete
        assert session_complete({"recipe_looked_up": True,
                                 "all_ingredients_checked": True,
                                 "shopping_list_updated": False,
                                 "first_timer_set": True}) is False

    def test_all_four_steps_true(self):
        from main import session_complete
        assert session_complete({"recipe_looked_up": True,
                                 "all_ingredients_checked": True,
                                 "shopping_list_updated": True,
                                 "first_timer_set": True}) is True


class TestLedgerJSON:
    def test_read_nonexistent_returns_default(self):
        from main import _read_json
        assert _read_json("never_exists.json", []) == []
        assert _read_json("never_exists.json", {}) == {}

    def test_atomic_write_roundtrip(self):
        from main import _write_json_atomic, _read_json
        _write_json_atomic("test_round.json", {"a": 1, "b": [2, 3]})
        assert _read_json("test_round.json", None) == {"a": 1, "b": [2, 3]}

    def test_corrupt_file_returns_default(self, isolated_ledgers):
        from main import _read_json
        (isolated_ledgers / "broken.json").write_text("not valid {{{", encoding="utf-8")
        assert _read_json("broken.json", []) == []


# ────────────────────────────────────────────────────────────────────────────
# Tool tests — call the @tool functions bare; verify they touch ledgers correctly
# ────────────────────────────────────────────────────────────────────────────

class TestRegisteredTools:
    """Tool functions can be called directly. If @tool-decorated, use .handler."""

    def _call_tool(self, tool_obj, args):
        """Call a tool, handling both decorated and plain async functions."""
        if hasattr(tool_obj, 'handler'):
            return asyncio.run(tool_obj.handler(args))
        else:
            return asyncio.run(tool_obj(args))

    def test_lookup_recipe_known(self):
        from main import lookup_recipe_tool, DEMO_RECIPES
        result = self._call_tool(lookup_recipe_tool, {"name": "spaghetti carbonara"})
        text = result["content"][0]["text"]
        assert "spaghetti" in text and "eggs" in text
        assert "pancetta" in text

    def test_lookup_recipe_unknown_lists_available(self):
        from main import lookup_recipe_tool
        result = self._call_tool(lookup_recipe_tool, {"name": "wagyu sashimi"})
        text = result["content"][0]["text"]
        assert "not in demo db" in text.lower() or "available" in text.lower()

    def test_check_pantry_hit_and_miss(self):
        from main import check_pantry_tool
        hit = self._call_tool(check_pantry_tool, {"ingredient": "eggs"})
        miss = self._call_tool(check_pantry_tool, {"ingredient": "wagyu"})
        assert hit["content"][0]["text"] == "yes"
        assert miss["content"][0]["text"] == "no"

    def test_add_to_shopping_list_dedup(self):
        from main import add_to_shopping_list_tool, _read_json, LEDGER_SHOPPING
        self._call_tool(add_to_shopping_list_tool, {"item": "pancetta"})
        result = self._call_tool(add_to_shopping_list_tool, {"item": "pancetta"})
        assert "already" in result["content"][0]["text"].lower()
        items = _read_json(LEDGER_SHOPPING, [])
        assert items.count("pancetta") == 1

    def test_set_timer_valid_and_invalid(self):
        from main import set_timer_tool
        valid = self._call_tool(set_timer_tool, {"minutes": 8, "label": "boil water"})
        assert "TIMER SET" in valid["content"][0]["text"]
        invalid = self._call_tool(set_timer_tool, {"minutes": 0, "label": "x"})
        assert "ignored" in invalid["content"][0]["text"].lower()

    def test_note_favorite_persists_and_dedup(self):
        from main import note_favorite_tool, _read_json, LEDGER_FAVORITES
        self._call_tool(note_favorite_tool, {"recipe_name": "pancakes"})
        result = self._call_tool(note_favorite_tool, {"recipe_name": "pancakes"})
        assert "already" in result["content"][0]["text"].lower()
        assert _read_json(LEDGER_FAVORITES, []).count("pancakes") == 1


# ────────────────────────────────────────────────────────────────────────────
# Integration tests — mock SDK boundary, run full agent_loop
# ────────────────────────────────────────────────────────────────────────────

class _FakeClient:
    """Stands in for ClaudeSDKClient — records prompts, returns scripted turns."""
    def __init__(self, turn_script: list[dict]):
        # Each script entry: {"text": str, "chain": [(tool_name, args), ...]}
        self._script = list(turn_script)
        self.prompts: list[str] = []

    async def query(self, prompt: str):
        self.prompts.append(prompt)


def _make_patched_run(turn_script: list[dict], user_inputs: list[str], recipe: str):
    """Run agent_loop with mocked SDK boundary + scripted user inputs."""
    import main as main_module

    @contextlib.asynccontextmanager
    async def _open(options):
        yield _FakeClient(turn_script)

    script_iter = iter(turn_script)

    async def _send(client, prompt, tool_observer):
        try:
            turn = next(script_iter)
        except StopIteration:
            raise RuntimeError("test script exhausted")
        # Fire the tool observer for each scripted tool call in this turn,
        # AND ACTUALLY CALL the tool function so disk state mutates correctly.
        for tname, targs in turn.get("chain", []):
            tool_observer(tname, targs)
            # Map tool name to implementation function and invoke it.
            # When SDK is available, tools are decorated SdkMcpTool objects with .handler.
            # When SDK is not available, tools are plain async functions.
            tool_map = {
                "lookup_recipe": main_module.lookup_recipe_tool,
                "check_pantry": main_module.check_pantry_tool,
                "add_to_shopping_list": main_module.add_to_shopping_list_tool,
                "set_timer": main_module.set_timer_tool,
                "note_favorite": main_module.note_favorite_tool,
            }
            if tname in tool_map:
                tool_func = tool_map[tname]
                # If it has a .handler attribute (decorated), use that; otherwise use directly.
                if hasattr(tool_func, 'handler'):
                    await tool_func.handler(targs)
                else:
                    await tool_func(targs)
        return {
            "response_text": turn.get("text", ""),
            "in_tok": 100,
            "out_tok": 50,
            "session_id": "fake-session-id-xyz",
            "tool_calls_this_turn": len(turn.get("chain", [])),
        }

    inputs_iter = iter(user_inputs)

    def mock_input(prompt=""):
        try:
            return next(inputs_iter)
        except StopIteration:
            return "stop"

    def mock_build_options(child_env):
        """Mock of build_options that returns a dummy object."""
        class DummyOptions:
            pass
        return DummyOptions()

    async def _run():
        with patch.object(main_module, "open_sdk_client", _open), \
             patch.object(main_module, "send_turn", _send), \
             patch.object(main_module, "build_options", mock_build_options), \
             patch("builtins.input", mock_input):
            return await main_module.agent_loop(CHILD_ENV, recipe)

    return asyncio.run(_run())


def test_predicate_satisfied_path():
    """Turn 1: full prep chain (lookup + 6 pantry checks + 1 shopping list + 1 timer) -> predicate True."""
    script = [{
        "text": "All set — timer for boiling water has been started. Session done.",
        "chain": [
            ("lookup_recipe", {"name": "spaghetti carbonara"}),
            ("check_pantry", {"ingredient": "spaghetti"}),
            ("check_pantry", {"ingredient": "eggs"}),
            ("check_pantry", {"ingredient": "pancetta"}),
            ("check_pantry", {"ingredient": "parmesan"}),
            ("check_pantry", {"ingredient": "black pepper"}),
            ("check_pantry", {"ingredient": "salt"}),
            ("add_to_shopping_list", {"item": "pancetta"}),
            ("set_timer", {"minutes": 8, "label": "boil water"}),
        ],
    }]
    state = _make_patched_run(script, [], "spaghetti carbonara")
    assert "GOAL MET" in state["exit_reason"], f"got: {state['exit_reason']}"
    assert state["recipe_looked_up"] is True
    assert state["all_ingredients_checked"] is True
    assert state["shopping_list_updated"] is True
    assert state["first_timer_set"] is True
    assert state["total_tool_calls"] == 9


def test_user_stop_path():
    """Turn 1: partial chain; user types 'stop' on next prompt."""
    script = [{
        "text": "Found the recipe; checked some ingredients. Want to keep going?",
        "chain": [
            ("lookup_recipe", {"name": "pancakes"}),
            ("check_pantry", {"ingredient": "flour"}),
        ],
    }]
    state = _make_patched_run(script, ["stop"], "pancakes")
    assert "USER STOPPED" in state["exit_reason"], f"got: {state['exit_reason']}"
    assert state["user_stopped"] is True


def test_model_done_path():
    """Model signals done in final text but session predicate not satisfied; still GOAL MET via model_done."""
    # Force first_timer_set so the heuristic ("ready to cook" + timer set) triggers model_done
    script = [{
        "text": "We're done — session is complete and ready to cook.",
        "chain": [
            ("lookup_recipe", {"name": "omelette"}),
            ("set_timer", {"minutes": 3, "label": "cook omelette"}),
        ],
    }]
    state = _make_patched_run(script, [], "omelette")
    assert "GOAL MET" in state["exit_reason"], f"got: {state['exit_reason']}"


def test_cap_reached_path_turn_cap():
    """Model never finishes; cap fires after MAX_TURNS turns with no done signal."""
    import main as main_module
    # MAX_TURNS scripted turns, each with one harmless tool call, no done signal
    script = [
        {"text": "still working", "chain": [("check_pantry", {"ingredient": f"item{i}"})]}
        for i in range(main_module.MAX_TURNS)
    ]
    # User keeps replying with non-stop text
    answers = [f"continue {i}" for i in range(main_module.MAX_TURNS)]
    state = _make_patched_run(script, answers, "spaghetti carbonara")
    assert "cap reached" in state["exit_reason"], f"got: {state['exit_reason']}"
    assert state["turns"] == main_module.MAX_TURNS


def test_cap_reached_path_tool_cap():
    """Total tool calls exceed cap mid-loop; loop exits before turn cap."""
    import main as main_module
    # Single turn with MAX_TOOL_CALLS_TOTAL tool calls
    script = [{
        "text": "many tools fired",
        "chain": [("check_pantry", {"ingredient": f"item{i}"})
                  for i in range(main_module.MAX_TOOL_CALLS_TOTAL)],
    }]
    state = _make_patched_run(script, ["continue"], "spaghetti carbonara")
    # Either tool-cap exit or turn-cap exit — both are valid "cap reached"
    assert "cap reached" in state["exit_reason"], f"got: {state['exit_reason']}"
    assert state["total_tool_calls"] >= main_module.MAX_TOOL_CALLS_TOTAL


def test_tool_chain_count_visible():
    """The [TOOL CHAIN] count should reflect actual tool calls in the response."""
    script = [{
        "text": "did 3 things",
        "chain": [
            ("lookup_recipe", {"name": "simple salad"}),
            ("check_pantry", {"ingredient": "lettuce"}),
            ("check_pantry", {"ingredient": "tomato"}),
        ],
    }]
    state = _make_patched_run(script, ["stop"], "simple salad")
    # After 1 turn with 3 tool calls + a user stop, total should be 3
    assert state["total_tool_calls"] == 3
    assert state["tool_call_breakdown"]["check_pantry"] == 2
    assert state["tool_call_breakdown"]["lookup_recipe"] == 1


def test_unknown_recipe_does_not_crash():
    """Lookup of unknown recipe returns graceful 'not found' — loop continues."""
    script = [{
        "text": "Sorry, I don't know that recipe. Try spaghetti carbonara?",
        "chain": [("lookup_recipe", {"name": "wagyu sashimi"})],
    }]
    state = _make_patched_run(script, ["stop"], "wagyu sashimi")
    assert state["user_stopped"] is True
    # Lookup_recipe was called and the agent didn't crash
    assert state["tool_call_breakdown"]["lookup_recipe"] == 1


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v", "--tb=short"]))
