# mac-advisor — Agent Blueprint
Cycle 4 · SDK Rung 5 · FORWARD · consumer-research

## Goal
Research MacBook Pro 16" M4 variants and produce a confident purchase recommendation
for a software developer / AI practitioner workload (Indian market).

## Input
- Variants to evaluate: M4 Base, M4 Pro, M4 Max
- Workload context: software development + LLM inference + occasional ML training
- Market: India (INR pricing)

## Output
A ranked recommendation with: best-fit variant, price, trade-offs accepted,
buy-now rationale, and the evidence trail from research.

## Rung 5 — The Phase-Gated Tool Palette
The agent runs in two phases. The model's callable tool set changes at the phase boundary.
Python enforces this via `allowed_tools` + `permission_mode="dontAsk"`.

### Phase 1 — Research
Allowed tools: search_specs · check_price · analyze_thermal · compare_variants
Denied:        synthesize_recommendation  (model cannot commit yet)

### Phase 2 — Synthesis
Allowed tools: synthesize_recommendation
Denied:        search_specs · check_price · analyze_thermal · compare_variants
               (model cannot keep researching indefinitely)

## Five Tools
| Tool | Phase | What it returns |
|------|-------|-----------------|
| search_specs(variant) | Research | CPU/GPU cores, memory options, benchmark scores |
| check_price(variant, market) | Research | Current INR price; simulates price drop on 2nd call |
| analyze_thermal(variant, workload) | Research | Throttling data; returns conflicting sources intentionally |
| compare_variants(variant_a, variant_b, dimension) | Research | Head-to-head finding |
| synthesize_recommendation(findings, confidence) | Synthesis | Final recommendation or "more research needed" |

## Complications (Scripted)
1. **Thermal conflict** — analyze_thermal("m4_pro", "general") → "no throttling" (manufacturer);
   analyze_thermal("m4_pro", "ai_inference") → "15-20% throttle" (independent review).
   Agent detects conflict, inserts resolution step, calls analyze_thermal("m4_pro", "sustained_load").
2. **Price drop** — second call to check_price("m4_pro_24gb") returns ₹2,29,900 vs ₹2,49,900.
   Agent detects drop, reasons it changes value calculus, updates recommendation.

## Agency Gates
- G1: is_research_complete(state) → bool  +  is_recommendation_ready(state) → bool
- G2: Model picks which research tool to call each step (search vs thermal vs compare)
- G3: Thermal conflict changes the next tool call — agent recalibrates
- G4: Predicate exit + max_research_turns=8 cap + max_synthesis_turns=3 cap
- G5: N/A (rung 5; independent verifier at rung 7)

## Persistent Memory
- research_notes.json — findings persist across runs (APP layer)
- ClaudeSDKClient — conversation context within each phase (SESSION layer)
- [TOOL CHAIN] label — tool sequences within one response (WITHIN-TURN layer)

## Termination Labels
GOAL MET (recommendation ready)  ·  EXIT: research cap  ·  EXIT: synthesis cap
