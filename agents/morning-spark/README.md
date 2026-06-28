# Morning Spark — Agent Foundry Cycle 6

SDK rung 6: PreToolUse guard + PostToolUse audit + JSONL span trace.
Domain: morning-briefing. Position: FORWARD.

## What it does

Fetches weather, today's date, and a top headline — checks quality —
synthesizes a morning briefing. Two hooks fire on every tool call.

## Prerequisites

- Python 3.12+
- `claude-agent-sdk` installed
- Claude Code CLI logged in (Max plan)

## Setup

```
pip install -r requirements.txt
```

No API key needed. Auth goes through Claude Code CLI.

## Run the smoke test first

```
pytest smoke_test.py -v
```

All tests must pass before running the agent.

## Run the agent

```
python main.py
```

Or open `main.py` in PyCharm and press the green Run button.

## Output files (created on run)

| File | What |
|---|---|
| `morning-spark_run_output.log` | Tee log — every run appended |
| `morning-spark_spans.jsonl` | PostToolUse audit — one line per tool call |
| `briefing_log.json` | App memory — read on next run as cross-day guard |

## Learning guide

Open `morning-spark_learning-guide.html` in a browser before running.
