# Study Buddy Agent v2

Cycle 2 · SDK Rung 3 · learning-research · FORWARD

An interactive Socratic study agent that remembers what tripped you up last time.

## Requirements

- Python 3.12+
- Claude Code CLI installed and logged in (`claude auth status`)
- Claude Max plan subscription (no API key needed)

## Setup

```powershell
pip install -r requirements.txt
claude auth status
```

If `auth status` shows logged out, run `claude login`.

## Run

```powershell
# Step 1 — verify smoke tests pass
python smoke_test.py

# Step 2 — run the agent (interactive — you'll type answers)
python main.py

# Step 3 — run it AGAIN on the same topic to see the cross-session memory demo
python main.py
```

Run log accumulates in `study-buddy_run_output.log` (appended every run).
Cross-run memory ledger lives in `weak_spots.json` (auto-created on first run).

## What to do during the run

The agent will ask you questions in the terminal — type your answers.
To exit early, type any of: `stop`, `quit`, `done`, `enough`, `exit`.
Otherwise, the agent stops on its own when it has enough signal, or at the
safety cap of 8 questions.

## Files

| File | Purpose |
|---|---|
| `main.py` | Agent code — rung 3 (`ClaudeSDKClient` multi-turn) |
| `smoke_test.py` | QA tests — mocks SDK boundary, no API calls |
| `prompt.md` | Design blueprint (cold-session contract) |
| `study-buddy_learning-guide.html` | Part 1 — read before running |
| `weak_spots.json` | Cross-session memory ledger (auto-managed) |
| `requirements.txt` | Dependencies |
| `.env.example` | Auth notes (no key required) |

## Troubleshooting

`[PREFLIGHT FAILED]` → run `claude auth status`, then `claude login`

`ImportError: claude_agent_sdk` → run `pip install claude-agent-sdk>=0.2.93`

`No module named 'pytest'` → run `pip install -r requirements.txt`

## After running

Say **"I ran it"** in the Foundry chat to generate `study-buddy_learning-insights.html` (Part 2) from your actual run log.
