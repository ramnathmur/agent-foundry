# mac-advisor — MacBook Pro Research Agent
Cycle 4 · Rung 5 (allowed_tools / disallowed_tools / permission_mode)

## What it does
Researches MacBook Pro M4 variants autonomously and recommends the best fit for
a software developer + AI practitioner workload (Indian market pricing).

## PyCharm setup
1. Create a virtual environment: `python -m venv .venv`
2. Activate it and install: `pip install -r requirements.txt`
3. Confirm Claude Code CLI is logged in: `claude auth status`
4. Run the agent: `python main.py`
5. Run tests: `pytest smoke_test.py -v`

## Auth
Uses Claude Max plan via the `claude-agent-sdk` → Claude Code CLI.
No API key needed. Do NOT set `ANTHROPIC_API_KEY`.

## Output
Console output streams to `mac-advisor_run_output.log` (appended on each run).
Research findings persist to `research_notes.json` across runs.
