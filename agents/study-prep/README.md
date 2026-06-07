# Study Prep Agent

Cycle 1 · SDK Rungs 1+2 · learning-research · FORWARD

## Requirements

- Python 3.12+
- Claude Code CLI installed and logged in
- Claude Max plan subscription (no API key needed)

## Setup

```powershell
pip install -r requirements.txt
claude auth status
```

If `auth status` shows logged out, run `claude login`.

## Run

```powershell
# Step 1 — verify tests pass
python smoke_test.py

# Step 2 — run the agent
python main.py
```

Log file appended after each run: `study-prep_run_output.log`

## Files

| File | Purpose |
|---|---|
| `main.py` | Agent code — rungs 1+2 |
| `smoke_test.py` | Tests — mocks `call_llm()`, no API calls |
| `prompt.md` | Design blueprint |
| `study-prep_learning-guide.html` | Part 1 — read before running |
| `requirements.txt` | Dependencies |
| `.env.example` | Auth notes |

## Troubleshooting

`[PREFLIGHT FAILED]` → run `claude auth status`, then `claude login`

`ImportError: claude_agent_sdk` → run `pip install claude-agent-sdk>=0.2.93`

## After running

Say **"I ran it"** to generate `study-prep_learning-insights.html` (Part 2 from the log).
