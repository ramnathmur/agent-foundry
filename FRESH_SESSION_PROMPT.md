# Fresh Session Starter Prompt
# Paste this as your first message in the new Claude Desktop session.
# Delete this file once used.

---

Agent Foundry — resuming from handoff.

Read SESSION.md first, then HANDOFF.md for detail. Project root:
C:\Claude Cowork\Projects\Agents code practical learning\Agents code practical learning

Context you need before I describe the changes:

- Cycle 1 is complete. All 8 Study Prep Agent files were written and the agent ran.
- The run exited via the G4 circuit breaker (cap reached, 10/10 iterations, 0/3 topics covered).
- Root cause identified: MOCK_SEARCH_DB uses exact key lookup (.get(query.lower().strip(), [])).
  The model's natural-language queries never matched any stored key, so every search returned
  an empty list. The circuit breaker correctly stopped the loop.
- learning-insights.html (Part 2) was generated from the log. Phase F2 probes were not completed.
- The registry learning object and INSIGHTS.md regeneration are pending.

I want to make fundamental changes to the application before continuing. Once you have read
the session files, ask me what changes I have in mind — then we will plan and implement them
together. After the changes are done, we will decide whether to resume Cycle 1 Phase F2 or
start a fresh cycle.

Do not write any files until I have described the changes.
