# Morning Intel — run instructions

Cycle 7 · Rung 8 · LATERAL-RIGHT

## Prerequisites

- Python 3.12+
- Claude Code CLI installed and signed in (`claude --version` must return a version)
- claude-agent-sdk installed (`pip install claude-agent-sdk`)

## Install

```
pip install -r requirements.txt
```

## Run the agent

Open the `agents/morning-intel/` folder in PyCharm.
Right-click `main.py` → **Run 'main'**.

Or from a terminal in the `agents/morning-intel/` directory:

```
python main.py
```

Output is printed to the terminal and also appended to `morning-intel_run_output.log`.

## Run the smoke tests

Right-click `smoke_test.py` → **Run 'pytest in smoke_test'**.

Or from a terminal:

```
pytest smoke_test.py -v
```

All four tests must pass before the first real run.

## Files generated at runtime

| File | Created when |
|------|-------------|
| `morning-intel_run_output.log` | Every run (appended) |
| `morning-intel_briefing_log.json` | Goal met — persists lead section for next run |
