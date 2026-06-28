# Recipe Companion Agent v1

Cycle 3 · SDK Rung 4 · health-habits (food/cooking) · FORWARD

An interactive kitchen assistant that helps you cook one meal end-to-end — and demonstrates real, model-callable tools that the SDK orchestrates inside a single response.

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

# Step 2 — run the agent
python main.py
```

When prompted, type a recipe name. The demo DB has: `spaghetti carbonara`, `pancakes`, `omelette`, `chicken stir fry`, `simple salad`.

**Try `spaghetti carbonara` first** — it produces the cleanest multi-tool chain in one model turn.

Run log accumulates in `recipe-companion_run_output.log` (appended every run).
Cross-run state lives in `pantry.json`, `shopping_list.json`, `favorites.json`.

## What to look for during the run

The line worth keeping an eye on is **`🔗 [TOOL CHAIN] N tool call(s) in this turn`**. If N is greater than 1 on any turn, the rung-4 capability has landed — the model chained multiple tool calls inside a single response without round-tripping to your Python in between.

## Files

| File | Purpose |
|---|---|
| `main.py` | Agent code — rung 4 (`@tool` + `create_sdk_mcp_server`) |
| `smoke_test.py` | QA tests — mocks SDK boundary, no real API calls |
| `prompt.md` | Design blueprint (cold-session contract) |
| `recipe-companion_learning-guide.html` | Part 1 — read before running |
| `pantry.json` | Cross-session pantry inventory (seeded with ~10 items) |
| `shopping_list.json` | Cross-session shopping list (starts empty) |
| `favorites.json` | Cross-session favorites (starts empty) |
| `requirements.txt` | Dependencies |
| `.env.example` | Auth notes (no key required) |

## Troubleshooting

`[PREFLIGHT FAILED]` → run `claude auth status`, then `claude login`

`ImportError: claude_agent_sdk` → run `pip install claude-agent-sdk>=0.2.93`

`No module named 'pytest'` → run `pip install -r requirements.txt`

## After running

Say **"I ran it"** in the Foundry chat to generate `recipe-companion_learning-insights.html` (Part 2) from your actual run log.
