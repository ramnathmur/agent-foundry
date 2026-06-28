# Research Project Lead

Rung 8 agent: subagents + context compaction.

## Quick start (PyCharm)

1. Open this folder in PyCharm
2. Create a Python 3.12+ interpreter (venv recommended)
3. Install dependencies: `pip install -r requirements.txt`
4. Verify CLI auth: `claude auth status`
5. Right-click `main.py` → Run

## What happens

The agent receives a research question, picks 3–5 investigation angles,
dispatches specialist sub-researchers (each in its own independent context),
collects their reports, checks for gaps, and synthesizes a final briefing.

## Files

| File | Purpose |
|------|---------|
| `prompt.md` | Agent blueprint |
| `main.py` | Entry point — run this |
| `smoke_test.py` | Tests (mocked SDK) |
| `research-lead_learning-guide.html` | Pre-run learning guide (Part 1) |
| `research_briefs.json` | App memory — accumulates across runs |
| `research-lead_run_output.log` | Auto-saved terminal output |
| `research-lead_run_data.json` | Structured run data for Part 2 HTML |

## Smoke test

```bash
pytest smoke_test.py -v
```
