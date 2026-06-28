# Study Buddy Agent v2 — Blueprint (prompt.md)
# Cycle 2 · Rung 3 · FORWARD (with FOUNDATIONAL flavor)
# Cold-session contract: a Claude session with only this file + CLAUDE.md can regenerate all 7 agent files.

---

## §1 — Candidate Selection Rationale

| | |
|---|---|
| **Agent name** | Study Buddy Agent v2 |
| **Slug** | `study-buddy` |
| **Domain** | learning-research |
| **Locked** | 2026-06-08, Cycle 2 |
| **Learning Position** | FORWARD — introduces rung 3 (`ClaudeSDKClient` + cross-call session memory); foundational flavor — directly addresses Cycle 1's `study-prep` perception/memory gap |

### Gate verdicts

| Gate | Verdict | One-line evidence |
|------|---------|-------------------|
| G1 — Goal predicate | PASS | `session_complete(state) -> bool` — True when ≥`MIN_QUESTIONS` asked AND ledger updated AND no `user_stop` flag |
| G2 — Model decision | PASS | Model picks subtopic, question wording, confidence score, and `done` decision each turn; Python never pre-selects |
| G3 — Loop feedback | PASS | Two layers — within-session: each prompt builds on the model's prior turn via `ClaudeSDKClient`; across-session: ledger from disk shapes turn 1's prompt |
| G4 — Termination | PASS | Three exit paths: predicate (`done` from model), hard cap (`MAX_QUESTIONS=8`), user-stop sentinel (`stop`/`quit`/`done`/`enough`); all three reachable in code and tested |
| G5 — Verifier | N/A | No independent critic at rung 3; annotated in code as N/A (first appears at rung 7) |

### 9-trait scorecard

| Tier | Trait | Present | Evidence |
|------|-------|---------|----------|
| Core | Goal-directedness | ✓ | `session_complete()` + `preflight()` |
| Core | Autonomy | ✓ | Model chooses subtopic + question phrasing + confidence + done-decision each turn |
| Core | Observe–reason–act | ✓ | User answer → model assessment → next question; cross-session: ledger shapes first turn |
| Essential | Perception | ✓ | `ask_question()` reads user input from terminal; `read_weak_spots()` reads disk |
| Essential | Planning | ✓ | Topic + subtopic outline implicit in first-turn ledger summary; live progress board each step |
| Essential | Memory | ✓✓ | **TWO LAYERS** — session (rung 3 `ClaudeSDKClient` carries LLM context) + app (`weak_spots.json` on disk) |
| Essential | Tool selection | ✓ | Model picks between `ask`, `assess+ask`, and `assess+done` per turn |
| Enhancing | Sequential action | ✓ | Question count tracked; loop advances per iteration |
| Enhancing | Termination criterion | ✓ | Triple exit: predicate + hard cap + user-stop |

---

## §2 — SDK Rung Introduced

### Rung 3 — `ClaudeSDKClient` multi-turn + `session_id` capture/resume

`ClaudeSDKClient` is the SDK's stateful client. Unlike `query()` (rung 1) which starts a fresh LLM context every call, `ClaudeSDKClient` opened as an `async with` block holds **one continuous conversation** — every `await client.query(...)` inside the block remembers the prior turns.

**Key API (verified against `/anthropics/claude-agent-sdk-python`):**

```python
from claude_agent_sdk import ClaudeSDKClient
from claude_agent_sdk.types import ClaudeAgentOptions, AssistantMessage, ResultMessage, TextBlock

options = ClaudeAgentOptions(
    system_prompt="...",
    model="claude-opus-4-8",
    max_turns=1,             # max turns PER query() call; total turns bounded by our loop
    permission_mode="bypassPermissions",
    env=child_env,
)

async with ClaudeSDKClient(options=options) as client:
    # Turn 1
    await client.query("Ask the user a question about Python lists.")
    async for msg in client.receive_response():
        ...   # standard message types

    # Turn 2 — SAME conversation, model remembers turn 1
    await client.query("User answered: 'a[0] gets the first element'. Assess + ask next.")
    async for msg in client.receive_response():
        ...
```

**Three things that did NOT exist at rung 1+2:**

1. **`async with` block** — opens one persistent connection
2. **No re-injection of prior state** — turn 2's prompt does NOT need to re-tell the model what turn 1 asked
3. **`session_id` field on `ResultMessage`** — capturable for *cross-run* resume (this agent prints it but does not actively resume; resume becomes a deeper drill in rung 6+)

### Comparison to Cycle 1

| Aspect | Cycle 1 (`query()` — rungs 1+2) | Cycle 2 (`ClaudeSDKClient` — rung 3) |
|---|---|---|
| Where conversation memory lives | In your Python (re-injected every call) | In the LLM client connection itself |
| Lines per prompt | High — must restate prior state | Low — model already knows |
| Token cost per turn (n-th turn) | O(n) — full state re-shoved | O(1) — only delta sent |
| Code complexity | Lower (one function call per step) | Slightly higher (lifecycle management) |
| What it unlocks | Bounded loops with external state | Interactive dialog, Socratic question chains, agents whose value IS memory |

---

## §3 — Goal Predicate

```python
def session_complete(state: dict) -> bool:
    """GATE[G1]: True when (model declared done) OR (min questions asked + ledger written)."""
    if state.get("user_stopped"):
        return True
    if state.get("model_done"):
        return True
    if state.get("questions_asked", 0) >= MIN_QUESTIONS_FOR_AUTO_DONE \
       and state.get("ledger_written", False):
        return True
    return False
```

**Module-level constants:**
```python
TOPIC_FOR_DEMO: str = "python_lists"   # demo topic; production agent would prompt user for topic
MAX_QUESTIONS: int = 8                  # GATE[G4]: hard cap — circuit breaker
MIN_QUESTIONS_FOR_AUTO_DONE: int = 5    # GATE[G1]: minimum work-product before auto-complete
LOG_FILE: str = "study-buddy_run_output.log"
LEDGER_FILE: str = "weak_spots.json"
AGENT_VERSION: str = "v1"
```

---

## §4 — Tools

Three tools — model owns all decisions about when to use them.

### `read_weak_spots(topic: str) -> list[dict]`
Reads `weak_spots.json`. Returns `[{subtopic, last_confidence, last_session_date}, …]` for the topic, or `[]` if topic absent (first-run case).

### `ask_question(question: str, expected_concepts: list[str]) -> str`
Displays the question to the user, reads their typed answer, returns answer text. Sentinel inputs (`stop`/`quit`/`done`/`enough`/`exit`) signal user-stop — caller checks and sets `state["user_stopped"] = True`.

### `update_weak_spots(topic: str, subtopic: str, confidence_0_to_1: float) -> None`
Writes/updates the ledger entry for `(topic, subtopic)` with the new confidence and today's date. Atomic write — write to temp file then rename.

---

## §5 — Memory Design (the pedagogical centerpiece)

**Two layers — each labeled clearly in runtime output:**

### Layer 1 — Session memory (NEW — rung 3, ephemeral)
The LLM-side conversation context. Maintained automatically by `ClaudeSDKClient` for the lifetime of the `async with` block. The model can refer to "what I asked last turn" without our code re-injecting anything.

Runtime label: `💾 [SESSION MEMORY] rung 3 — client holds N turns of conversation`

### Layer 2 — App memory (persistent, on disk)
`weak_spots.json` — a simple JSON file in the agent folder.

```json
{
  "python_lists": [
    {"subtopic": "indexing", "last_confidence": 0.4, "last_session_date": "2026-06-05"},
    {"subtopic": "comprehensions", "last_confidence": 0.9, "last_session_date": "2026-06-05"}
  ],
  "linear_algebra_basics": [
    {"subtopic": "matrix_inversion", "last_confidence": 0.3, "last_session_date": "2026-06-06"}
  ]
}
```

Runtime label: `📀 [APP MEMORY] weak_spots.json updated → subtopic=indexing confidence=0.7`

### The first-vs-second-run demo

- **Run 1** on `python_lists` (empty ledger): the first-turn prompt has no prior weakness data. Model picks subtopics broadly.
- **Run 2** on `python_lists` (ledger now populated by run 1): the first-turn prompt includes `indexing: 0.4` summary; model opens by drilling indexing.

This is the rung 3 demo. The second run gives a *different* lesson with **zero code changes** between runs.

---

## §6 — Termination — three exit paths

| Path | Condition | Exit print | Gate annotation |
|------|-----------|------------|-----------------|
| Goal met (model done) | model returns `{"done": true, ...}` | `🏁 GOAL MET — model assessed session complete` | `# GATE[G4]: model-done exit` |
| User stop | user types `stop`/`quit`/`done`/`enough`/`exit` | `🏁 USER STOPPED — exiting at user request` | `# GATE[G4]: user-stop exit` |
| Cap reached | `questions_asked >= MAX_QUESTIONS` | `🏁 EXIT: cap reached — 8/8 questions asked` | `# GATE[G4]: hard-cap exit` |

All three paths must be exercised in `smoke_test.py`.

---

## §7 — Complications

1. **First-run empty ledger** — `read_weak_spots("python_lists")` returns `[]`. Agent must still produce a coherent first question; ledger summary in first prompt is "no prior data".
2. **Malformed model JSON** — model wraps JSON in markdown fence. `parse_model_response()` strips fences and extracts the first JSON object.
3. **User non-answer** — user types empty string or hits Enter. Treat as low-confidence answer; do not crash.
4. **Confidence out of range** — model returns `confidence: 1.5`. Clamp to `[0.0, 1.0]` before writing to ledger.
5. **Ledger write failure** — disk full / permission denied. Surface as `⚠ [ERROR: STRUCTURAL → log]`, set `state["ledger_written"] = False`, continue loop. Predicate won't auto-trigger but cap will catch.
6. **Cap fires before model done** — print `🏁 EXIT: cap reached` and emphasize in summary that the ledger entries written so far ARE saved (partial work is not lost).

---

## §8 — `call_llm_streamed()` — SDK Boundary Function

Single async function that holds the `ClaudeSDKClient` lifecycle. Mock THIS in `smoke_test.py`.

```python
async def call_llm_streamed(
    options,
    turn_prompts: list[str],
    on_turn_response: Callable[[int, str, dict], None],
    child_env: dict[str, str],
) -> dict:
    """
    TRAIT[autonomy] — single contact point with claude_agent_sdk.ClaudeSDKClient.
    Iterates through turn_prompts, calling on_turn_response(turn_idx, response_text, meta)
    after each turn. Returns dict with session_id, total_in_tok, total_out_tok.
    NOTE: this is a thin streaming wrapper; mock THIS in smoke_test.py.
    """
    from claude_agent_sdk import ClaudeSDKClient
    from claude_agent_sdk.types import AssistantMessage, ResultMessage, TextBlock

    total_in_tok = total_out_tok = 0
    session_id = None

    async with ClaudeSDKClient(options=options) as client:
        for turn_idx, prompt in enumerate(turn_prompts, start=1):
            await client.query(prompt)
            response_text = ""
            async for msg in client.receive_response():
                print(message_lens(msg))
                if isinstance(msg, AssistantMessage):
                    for block in msg.content:
                        if isinstance(block, TextBlock):
                            response_text += block.text
                elif isinstance(msg, ResultMessage):
                    if msg.result:
                        response_text = msg.result
                    if msg.usage:
                        total_in_tok += msg.usage.get("input_tokens", 0)
                        total_out_tok += msg.usage.get("output_tokens", 0)
                    if getattr(msg, "session_id", None):
                        session_id = msg.session_id
            on_turn_response(turn_idx, response_text, {
                "in_tok_running": total_in_tok,
                "out_tok_running": total_out_tok,
                "session_id": session_id,
            })

    return {
        "session_id": session_id,
        "total_in_tok": total_in_tok,
        "total_out_tok": total_out_tok,
    }
```

**Important — but for this agent we don't use this streaming form directly.** Because each turn depends on the user's typed answer (which we can't know in advance), we use the `ClaudeSDKClient` context manager directly in `agent_loop()` rather than the `turn_prompts` list pre-built. The function above shows the streaming form for the cold-session contract — it's the pattern, not what main.py invokes literally.

What main.py actually does:

```python
async with ClaudeSDKClient(options=options) as client:
    while not session_complete(state) and questions_asked < MAX_QUESTIONS:
        prompt = build_turn_prompt(state, user_answer_or_none)
        await client.query(prompt)
        response_text = ""
        async for msg in client.receive_response():
            ...
        # parse, ask user, update ledger, advance state
```

The async-with block IS the rung 3 capability landing.

---

## §9 — Comment Header Format

Every major block gets:
```python
# ═══════════════════════════════════════════
# PURPOSE: one sentence
# AGENTIC TRAIT: trait name
# ACHIEVES: what the agent gains from this block
# DEPENDENCIES: what must exist before this runs
# ═══════════════════════════════════════════
```
Minimum 5 headers. Inline annotations: `# TRAIT[x]`, `# GATE[Gn]`, `# GOTCHA[x]`.

---

## §10 — QA Checklist (run before handover)

```powershell
(Select-String "main.py" -Pattern "TRAIT\[").Count    # >= 5
(Select-String "main.py" -Pattern "GATE\[").Count     # >= 5  (G1..G5 each)
(Select-String "main.py" -Pattern "GOTCHA\[").Count   # >= 1
(Select-String "main.py" -Pattern "═══").Count        # >= 5
(Select-String "main.py" -Pattern "\[AGENT BOOT\]").Count        # >= 1
(Select-String "main.py" -Pattern "\[GOAL SET\]").Count          # >= 1
(Select-String "main.py" -Pattern "\[GOAL PREDICATE\]").Count    # >= 1
(Select-String "main.py" -Pattern "\[MODEL DECISION\]").Count    # >= 1
(Select-String "main.py" -Pattern "\[LOOP FEEDBACK\]").Count     # >= 1
(Select-String "main.py" -Pattern "\[CONTEXT\]").Count           # >= 1
(Select-String "main.py" -Pattern "\[SDK ").Count                # >= 1
(Select-String "main.py" -Pattern "SESSION MEMORY|APP MEMORY").Count   # >= 2 (both layers)
(Select-String "main.py" -Pattern "AGENT SUMMARY").Count          # >= 1
python smoke_test.py                                              # exit 0
```

Gate annotations required: G1 at `session_complete()` call, G2 at parsed model output, G3 at `[LOOP FEEDBACK]` print, G4 at all three exits, G5 as N/A comment.

---

## §11 — PyCharm Run Instructions

1. Open `agents/study-buddy` as project · verify Python 3.12+ interpreter
2. Terminal: `pip install -r requirements.txt`
3. Terminal: `claude auth status` (must show logged in)
4. Right-click `smoke_test.py` → Run (must be green)
5. Right-click `main.py` → Run · **answer the questions in the terminal** (this agent is interactive)
6. Run a SECOND time on the same topic — notice the agent opens by drilling whatever was weakest last time
7. Log file: `study-buddy_run_output.log` (appended each run)

Troubleshooting: `[PREFLIGHT FAILED]` → run `claude auth status` / `claude login`

---

*v1.0 · 2026-06-08 · Cycle 2 · Rung 3 · FORWARD*
