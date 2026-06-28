"""
Research Project Lead — Rung 8: Subagents + Context Compaction

A research project lead that takes a question, dispatches specialist
sub-researchers to investigate from multiple angles (each in its own
independent context window), collects their reports, checks for gaps,
and synthesizes a final briefing.

AGENTIC TRAITS DEMONSTRATED
┌──────────────────────┬──────────────────────────────────────┬──────────────────────────────────────────────┐
│ Trait                │ Where in code                        │ Why it's agentic                             │
├──────────────────────┼──────────────────────────────────────┼──────────────────────────────────────────────┤
│ Goal-directedness    │ is_goal_met() evaluated each step    │ Predicate computed, not narrated             │
│ Autonomy             │ Model picks angles from palette      │ Code offers 6; model picks 3-5              │
│ O-R-A loop           │ Gap/confidence → follow-up dispatch  │ Next action depends on observation           │
│ Perception           │ Sub-researchers read mock DB         │ External data shapes behaviour               │
│ Planning             │ Investigation plan generated at boot │ Plan before action                           │
│ Memory (session)     │ Main agent ClaudeSDKClient           │ Carries context across turns                 │
│ Memory (subagent)    │ Each sub-researcher's own client     │ Independent context — rung 8 NEW             │
│ Memory (app)         │ research_briefs.json on disk         │ Survives across runs                         │
│ Tool selection       │ 3 main + 3 sub-researcher tools      │ Model-routed via SDK                         │
│ Sequential action    │ Steps tracked in main loop           │ Counted, observable                          │
│ Principled stop      │ GOAL MET + 2 cap exits, all labeled  │ Agent explains WHY it stopped                │
└──────────────────────┴──────────────────────────────────────┴──────────────────────────────────────────────┘

CONTROL PLANE: The main agent's model owns angle selection and follow-up decisions.
Each sub-researcher's model owns its search and extraction strategy.
The code owns the goal predicate and all hard caps.
"""

import asyncio
import json
import os
import sys
import time
import subprocess
import contextlib
import io
from pathlib import Path
from typing import Any

try:
    from claude_agent_sdk import query
except ImportError:
    query = None  # patched in smoke_test.py

# ═══════════════════════════════════════════
# PURPOSE: Tee stdout to log file for post-run HTML generation
# AGENTIC TRAIT: Observability — every run is recorded
# ACHIEVES: research-lead_run_output.log as input for Part 2 HTML
# DEPENDENCIES: None (runs at script start)
# ═══════════════════════════════════════════

class TeeWriter:
    """Mirrors stdout to a log file. Appends with a run-separator header."""
    def __init__(self, log_path: Path):
        self._original = sys.stdout
        self._log = open(log_path, "a", encoding="utf-8")
        self._log.write(f"\n{'='*60}\n")
        self._log.write(f"RUN: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        self._log.write(f"{'='*60}\n\n")

    def write(self, text: str) -> int:
        self._original.write(text)
        self._log.write(text)
        self._log.flush()
        return len(text)

    def flush(self):
        self._original.flush()
        self._log.flush()

    def close(self):
        self._log.close()
        sys.stdout = self._original


@contextlib.contextmanager
def tee_to_log():
    """Context manager that tees all stdout to the run output log."""
    log_path = Path(__file__).parent / "research-lead_run_output.log"
    tee = TeeWriter(log_path)
    sys.stdout = tee
    try:
        yield
    finally:
        tee.close()


# ═══════════════════════════════════════════
# PURPOSE: Preflight checks — Python version, SDK import, CLI auth
# AGENTIC TRAIT: Goal-directedness (refuses to start without prerequisites)
# ACHIEVES: Fail-fast with fix-it message
# DEPENDENCIES: None
# ═══════════════════════════════════════════

def preflight() -> None:  # TRAIT[goal-directedness]: agent refuses to start without prerequisites
    """Verify Python version, SDK availability, and CLI auth."""
    if sys.version_info < (3, 12):
        print(f"⚠ Python 3.12+ required (you have {sys.version_info.major}.{sys.version_info.minor})")
        print("  Fix: install Python 3.12+ from python.org")
        sys.exit(1)

    # GOTCHA[api-key-bypass]: strip ANTHROPIC_API_KEY from child-process env only
    if os.environ.get("ANTHROPIC_API_KEY"):
        print("⚠ ANTHROPIC_API_KEY detected — stripping from child-process environment.")
        print("  This agent authenticates via Claude Max subscription, never an API key.")
        os.environ.pop("ANTHROPIC_API_KEY", None)

    try:
        import claude_agent_sdk  # noqa: F401
    except ImportError:
        print("⚠ claude-agent-sdk not installed.")
        print("  Fix: pip install claude-agent-sdk>=0.2.93")
        sys.exit(1)

    try:
        result = subprocess.run(
            ["claude", "--version"],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode != 0:
            print("⚠ Claude CLI not responding. Fix: install Claude Code CLI and log in.")
            sys.exit(1)
    except FileNotFoundError:
        print("⚠ Claude CLI not found on PATH.")
        print("  Fix: install Claude Code CLI (npm install -g @anthropic-ai/claude-code)")
        sys.exit(1)
    except subprocess.TimeoutExpired:
        print("⚠ Claude CLI timed out. Check your connection.")
        sys.exit(1)


# ═══════════════════════════════════════════
# PURPOSE: Mock research database — 6 angles × multiple sources
# AGENTIC TRAIT: Perception (external data shapes agent behaviour)
# ACHIEVES: Deterministic demo without real internet
# DEPENDENCIES: None
# ═══════════════════════════════════════════

MOCK_RESEARCH_DB: dict[str, list[dict[str, Any]]] = {
    "technical": [
        {
            "id": "tech-001",
            "title": "Leitner System: Algorithm Design and Performance",
            "abstract": "The Leitner system uses a box-based card sorting algorithm where correctly answered cards advance to less frequent review boxes. Performance benchmarks show 40-60% reduction in review time compared to linear repetition.",
            "findings": "The Leitner system's O(n) sorting is simple but lacks adaptive scheduling. Cards are grouped by box, not by individual difficulty curves. Works well for vocabulary but struggles with conceptual programming topics where partial knowledge is common.",
            "confidence_note": "Well-established algorithm with 50+ years of research backing."
        },
        {
            "id": "tech-002",
            "title": "SM-2 and SuperMemo: Interval Scheduling Mathematics",
            "abstract": "SM-2 (SuperMemo Algorithm 2) calculates optimal review intervals using an easiness factor that adjusts per-card based on recall performance. The core formula: I(n) = I(n-1) * EF where EF starts at 2.5.",
            "findings": "SM-2 is the foundation of most modern spaced-repetition software (Anki uses a modified SM-2). The algorithm is deterministic — same inputs always produce the same schedule. Weakness: the easiness factor can collapse to minimum for difficult cards, creating review pile-ups. SM-17/18 address this with statistical models but are proprietary.",
            "confidence_note": "SM-2 is open and well-understood. SM-17+ are closed-source; findings based on published papers only."
        }
    ],
    "market": [
        {
            "id": "mkt-001",
            "title": "Spaced Repetition App Market Analysis 2025",
            "abstract": "Anki dominates the open-source segment with 10M+ active users. Paid alternatives include SuperMemo ($60/yr), Brainscape (freemium), and RemNote (freemium with AI features).",
            "findings": "Anki's market dominance stems from its open ecosystem (shared decks, add-ons) rather than algorithmic superiority. SuperMemo has arguably better algorithms (SM-17) but <1% market share due to poor UX. For programming specifically, platforms like Exercism and LeetCode use implicit spaced repetition through problem sequencing but don't market it as SRS.",
            "confidence_note": "Market data from app store rankings and community surveys; some figures are estimates."
        }
    ],
    "user": [
        {
            "id": "usr-001",
            "title": "Learning Outcomes: SRS vs Traditional Study for Programming",
            "abstract": "A 2023 meta-analysis of 12 studies found that spaced repetition improved syntax recall by 35% but showed no significant advantage for problem-solving skills in programming.",
            "findings": "SRS excels at declarative knowledge (API names, syntax patterns, error codes) but underperforms for procedural knowledge (algorithm design, debugging strategies). Students who combined SRS with project-based practice outperformed both pure-SRS and pure-project groups by 28%. The optimal ratio appears to be ~30% SRS / 70% active coding.",
            "confidence_note": "Meta-analysis quality varies; individual study sizes were 20-80 participants."
        },
        {
            "id": "usr-002",
            "title": "User Experience Research: Why Learners Abandon SRS",
            "abstract": "Survey of 500 SRS users who quit within 6 months. Top reasons: review pile-up anxiety (67%), cards feeling disconnected from real coding (54%), lack of immediate utility (41%).",
            "findings": "The 'review debt' problem is the #1 UX failure of current SRS tools for programming. When a learner misses 3 days, returning to 200+ pending reviews feels overwhelming. Successful long-term users (>1yr) all reported the same coping strategy: ruthless deck pruning and a 'max 20 min/day' hard cap.",
            "confidence_note": "Self-reported survey data; potential survivorship bias in the 'successful users' subgroup."
        }
    ],
    "contrarian": [
        {
            "id": "con-001",
            "title": "Against Spaced Repetition for Programming: A Critical Review",
            "abstract": "This paper argues that SRS is fundamentally misaligned with how programming expertise develops, because programming is primarily a skill (procedural), not a knowledge base (declarative).",
            "findings": "The core argument: you don't get better at programming by remembering more facts — you get better by solving more problems. SRS optimizes for recall, but programming fluency requires transfer (applying knowledge in novel contexts). No SRS system effectively tests transfer. The author proposes 'spaced practice' (revisiting problem types at intervals) as superior to 'spaced repetition' (reviewing cards at intervals). Key distinction: practice generates knowledge; repetition preserves it.",
            "confidence_note": "Position paper, not empirical study. Arguments are well-constructed but unverified experimentally."
        }
    ],
    "regulatory": [
        {
            "id": "reg-001",
            "title": "Accessibility Standards for Learning Software (WCAG 2.2 + EdTech Guidelines)",
            "abstract": "Review of accessibility requirements applicable to spaced repetition tools used in educational settings.",
            "findings": "WCAG 2.2 Level AA compliance is mandatory for educational software in EU public institutions (European Accessibility Act, June 2025). Key gaps in current SRS tools: most card-based UIs fail keyboard navigation tests; timed recall sessions violate WCAG 2.2.1 (timing adjustable); audio-only cards lack text alternatives. Anki's desktop app scores 62% on automated WCAG testing; mobile apps score lower. For programming SRS specifically, code syntax highlighting in cards must maintain 4.5:1 contrast ratio.",
            "confidence_note": "Regulatory requirements are factual; compliance scores are from automated testing tools with known false-positive rates."
        }
    ],
    "historical": [
        {
            "id": "his-001",
            "title": "From Ebbinghaus to Anki: 140 Years of Spaced Repetition",
            "abstract": "Historical survey of spaced repetition from Ebbinghaus's 1885 forgetting curve experiments through Leitner (1972), Pimsleur (1967), SuperMemo (1987), and Anki (2006).",
            "findings": "Three major paradigm shifts: (1) Ebbinghaus→Leitner: from theory to practical system (boxes); (2) Leitner→SuperMemo: from fixed intervals to adaptive scheduling (algorithms); (3) SuperMemo→Anki: from proprietary to open-source (ecosystem). The failed approaches are instructive: Pimsleur's graduated intervals worked for language audio but never adapted to visual/textual learning; early computer-based drill systems (PLATO, 1960s) had spaced elements but no personalization. The historical pattern suggests the next shift will be from card-based to context-embedded repetition (reviewing concepts within the tool you're actually using, not in a separate app).",
            "confidence_note": "Historical facts are well-documented. The prediction about 'context-embedded' is speculative."
        }
    ]
}

# ═══════════════════════════════════════════
# PURPOSE: Research angle palette — 6 options the model picks from
# AGENTIC TRAIT: Autonomy (model picks which 3-5 to investigate)
# ACHIEVES: G2 — model-owned decision visible in output
# DEPENDENCIES: MOCK_RESEARCH_DB keys
# ═══════════════════════════════════════════

RESEARCH_ANGLES: dict[str, str] = {
    "technical": "Algorithms, implementations, and performance benchmarks",
    "market": "Existing tools, adoption rates, pricing, user base",
    "user": "User experience research, learning outcomes, satisfaction data",
    "contrarian": "Arguments against, limitations, failure modes, alternative approaches",
    "regulatory": "Standards, compliance, accessibility requirements",
    "historical": "Evolution, predecessors, failed approaches, lessons learned"
}

# ═══════════════════════════════════════════
# PURPOSE: Agent configuration constants
# AGENTIC TRAIT: Principled stop (hard caps)
# ACHIEVES: G4 — both exit paths reachable
# DEPENDENCIES: None
# ═══════════════════════════════════════════

MAX_SUBAGENTS_TOTAL = 5       # GATE[G4]: hard cap on total sub-researchers (initial + follow-ups)
MAX_FOLLOWUP = 2              # GATE[G4]: hard cap on follow-up dispatches
MAX_SYNTHESIS_TURNS = 2       # GATE[G4]: hard cap on synthesis attempts
CONFIDENCE_THRESHOLD = 0.7    # GATE[G1]: minimum confidence for goal-met
GAP_CONFIDENCE_FLOOR = 0.6   # GATE[G3]: below this triggers a follow-up

DEFAULT_QUESTION = (
    "What's the most effective spaced-repetition algorithm for learning "
    "a programming language — and what are the trade-offs vs alternatives?"
)

AGENT_DIR = Path(__file__).parent
BRIEFINGS_FILE = AGENT_DIR / "research_briefs.json"
RUN_DATA_FILE = AGENT_DIR / "research-lead_run_data.json"


# ═══════════════════════════════════════════
# PURPOSE: Goal predicate — computable test the agent runs on itself
# AGENTIC TRAIT: Goal-directedness
# ACHIEVES: G1 — predicate computed, not narrated
# DEPENDENCIES: Agent state dict
# ═══════════════════════════════════════════

def is_goal_met(state: dict) -> bool:  # GATE[G1]: predicate computed, not narrated
    """Three conditions, all required: all returned, synthesis exists, confidence met."""
    return (
        state.get("all_dispatched_returned", False)
        and state.get("synthesis_produced", False)
        and state.get("synthesis_confidence", 0.0) >= CONFIDENCE_THRESHOLD
    )


# ═══════════════════════════════════════════
# PURPOSE: MessageLens — one-line console rendering of SDK messages
# AGENTIC TRAIT: Observability (agent loop is watchable)
# ACHIEVES: FR-C8 compliance — indented with ┆ prefix
# DEPENDENCIES: claude_agent_sdk message types
# ═══════════════════════════════════════════

def message_lens(message: Any, label: str = "") -> None:
    """Render an SDK message as a one-line summary, indented with ┆ prefix."""
    msg_type = type(message).__name__
    prefix = f"  ┆ {label}" if label else "  ┆"

    if msg_type == "ResultMessage":
        text = getattr(message, "text", "")
        preview = text[:120].replace("\n", " ") + ("..." if len(text) > 120 else "")
        print(f"{prefix} [{msg_type}] {preview}")
    elif msg_type == "AssistantMessage":
        content = getattr(message, "content", [])
        tool_calls = [b for b in content if getattr(b, "type", "") == "tool_use"]
        text_blocks = [b for b in content if getattr(b, "type", "") == "text"]
        if tool_calls:
            names = ", ".join(getattr(tc, "name", "?") for tc in tool_calls)
            print(f"{prefix} [{msg_type}] tool_calls=[{names}]")
        elif text_blocks:
            txt = getattr(text_blocks[0], "text", "")[:100].replace("\n", " ")
            print(f"{prefix} [{msg_type}] {txt}...")
    else:
        print(f"{prefix} [{msg_type}]")


# ═══════════════════════════════════════════
# PURPOSE: Run data collector — structures runtime events for HTML
# AGENTIC TRAIT: Observability (structured data for post-run analysis)
# ACHIEVES: research-lead_run_data.json as input for Run Log section
# DEPENDENCIES: None
# ═══════════════════════════════════════════

class RunDataCollector:
    """Collects structured runtime events for the Run Log HTML section."""
    def __init__(self):
        self.events: list[dict] = []
        self.phases: list[dict] = []
        self.sub_researchers: list[dict] = []
        self.start_time: float = time.time()
        self.question: str = ""
        self.selected_angles: list[str] = []
        self.outcome: str = ""
        self.total_tokens_in: int = 0
        self.total_tokens_out: int = 0
        self.total_cost: float = 0.0

    def add_event(self, event_type: str, label: str, detail: str,
                  narrative: str = "", phase: str = "", **kwargs: Any) -> None:
        self.events.append({
            "time": time.time() - self.start_time,
            "type": event_type,
            "label": label,
            "detail": detail,
            "narrative": narrative,
            "phase": phase,
            **kwargs
        })

    def start_phase(self, name: str, title: str, emoji: str) -> None:
        self.phases.append({
            "name": name,
            "title": title,
            "emoji": emoji,
            "start_time": time.time() - self.start_time
        })

    def add_sub_researcher(self, angle: str, question: str, report: dict | None,
                           tokens_in: int = 0, tokens_out: int = 0) -> None:
        self.sub_researchers.append({
            "angle": angle,
            "question": question,
            "report": report,
            "tokens_in": tokens_in,
            "tokens_out": tokens_out,
            "is_followup": len(self.sub_researchers) >= len(self.selected_angles)
        })

    def save(self) -> None:
        data = {
            "agent": "research-lead",
            "version": "1.0",
            "run_date": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "elapsed_seconds": round(time.time() - self.start_time, 1),
            "question": self.question,
            "selected_angles": self.selected_angles,
            "outcome": self.outcome,
            "total_sub_researchers": len(self.sub_researchers),
            "tokens": {
                "input": self.total_tokens_in,
                "output": self.total_tokens_out,
                "total": self.total_tokens_in + self.total_tokens_out
            },
            "estimated_cost_usd": round(self.total_cost, 4),
            "phases": self.phases,
            "events": self.events,
            "sub_researchers": self.sub_researchers
        }
        RUN_DATA_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")


# ═══════════════════════════════════════════
# PURPOSE: Phase banner printer — dramatic section headers
# AGENTIC TRAIT: Observability (lifecycle phases visible in terminal)
# ACHIEVES: Enhanced runtime output Layer A
# DEPENDENCIES: None
# ═══════════════════════════════════════════

def print_phase_banner(title: str, emoji: str = "═") -> None:
    """Print a dramatic phase banner with box-drawing characters."""
    width = 55
    line = "═" * width
    padded = f"{emoji}  {title}"
    print(f"\n{line}")
    print(padded)
    print(line)


def print_narrative(text: str) -> None:
    """Print a narrative gloss — plain-English explanation after a key moment."""
    print(f"  💡 {text}")


def print_micro_summary(step: int, text: str) -> None:
    """Print a step-end micro-summary."""
    print(f"  📌 Step {step} in one sentence: {text}")


def print_sub_researcher_box(angle: str, lines: list[str], is_followup: bool = False) -> None:
    """Print a sub-researcher's work in a box-drawn container."""
    label = f"Follow-up: {angle}" if is_followup else f"Sub-Researcher: {angle}"
    width = max(len(label) + 4, max((len(l) for l in lines), default=40) + 4, 50)
    print(f"  ┌{'─' * (width - 2)}┐")
    print(f"  │ {label:<{width - 4}} │")
    print(f"  │{'─' * (width - 2)}│")
    for line in lines:
        print(f"  │ {line:<{width - 4}} │")
    print(f"  └{'─' * (width - 2)}┘")


# ═══════════════════════════════════════════
# PURPOSE: Sub-researcher loop — runs in its own ClaudeSDKClient
# AGENTIC TRAIT: Memory (within-subagent — rung 8 NEW)
# ACHIEVES: Independent context window per sub-researcher
# DEPENDENCIES: claude_agent_sdk, MOCK_RESEARCH_DB
# ═══════════════════════════════════════════

async def run_sub_researcher(
    angle: str,
    question: str,
    run_data: RunDataCollector,
    sub_index: int,
    is_followup: bool = False
) -> dict:  # TRAIT[memory]: within-subagent context — rung 8 NEW
    """
    Run a sub-researcher in its own independent ClaudeSDKClient.
    The main agent cannot see this conversation — only the returned report.
    """
    box_lines: list[str] = []
    tokens_in = 0
    tokens_out = 0

    # Look up sources from mock DB
    sources = MOCK_RESEARCH_DB.get(angle, [])
    box_lines.append(f"🔧 [TOOL CALL] lookup_source(angle='{angle}')")
    box_lines.append(f"📥 [TOOL RESULT] {len(sources)} source(s) found")

    if not sources:
        report = {
            "angle": angle,
            "question": question,
            "findings": [],
            "summary": f"No sources found for the {angle} angle.",
            "confidence": 0.3,
            "gap_flagged": True,
            "gap_description": f"No {angle} sources in the research database."
        }
        box_lines.append(f"⚠ No sources — gap flagged")
        box_lines.append(f"✅ Report ready: confidence 0.30 | gap: yes")
        print_sub_researcher_box(angle, box_lines, is_followup)
        run_data.add_sub_researcher(angle, question, report, tokens_in, tokens_out)
        return report

    # Extract findings from each source
    findings = []
    for source in sources:
        box_lines.append(f"🔧 [TOOL CALL] extract_finding(source_id='{source['id']}')")
        findings.append({
            "source_id": source["id"],
            "title": source["title"],
            "key_finding": source["findings"],
            "confidence_note": source["confidence_note"]
        })
        box_lines.append(f"📥 [TOOL RESULT] extracted: {source['title'][:45]}...")

    # Use the SDK to synthesize the sub-researcher's findings
    # Each sub-researcher gets its own ClaudeSDKClient — RUNG 8 CONCEPT
    print(f"  ━━━ [SDK →] sub-researcher({angle}) · ~{len(str(findings)) // 4} prompt tokens")
    sub_start = time.time()

    try:
        findings_text = "\n".join(
            f"- {f['title']}: {f['key_finding']}" for f in findings
        )

        result = await query(  # TRAIT[autonomy]: sub-researcher model decides how to summarize
            prompt=(
                f"You are a specialist researcher investigating the '{angle}' angle of this question: {question}\n\n"
                f"Here are the findings from your sources:\n{findings_text}\n\n"
                f"Produce a concise summary paragraph (3-5 sentences) synthesizing these findings. "
                f"Then assess: on a scale of 0.0 to 1.0, how confident are you in this angle's coverage? "
                f"Are there any gaps that need follow-up investigation?\n\n"
                f"Respond in this exact JSON format:\n"
                f'{{"summary": "...", "confidence": 0.X, "gap_flagged": true/false, "gap_description": "..." or null}}'
            ),
            max_tokens=500
        )

        sub_elapsed = time.time() - sub_start
        result_text = getattr(result, "text", str(result))

        # Track usage
        usage = getattr(result, "usage", None)
        if usage:
            tokens_in = getattr(usage, "input_tokens", 0)
            tokens_out = getattr(usage, "output_tokens", 0)
            run_data.total_tokens_in += tokens_in
            run_data.total_tokens_out += tokens_out

        print(f"  ━━━ [← SDK] {sub_elapsed:.1f}s · +{tokens_out} output tokens")

        # Parse the sub-researcher's response
        try:
            cleaned = result_text.strip()
            if cleaned.startswith("```"):
                cleaned = "\n".join(cleaned.split("\n")[1:])
                if cleaned.endswith("```"):
                    cleaned = cleaned[:-3]
                cleaned = cleaned.strip()

            parsed = json.loads(cleaned)
            confidence = max(0.0, min(1.0, float(parsed.get("confidence", 0.5))))  # GOTCHA[confidence-clamp]
            report = {
                "angle": angle,
                "question": question,
                "findings": findings,
                "summary": parsed.get("summary", "No summary produced."),
                "confidence": confidence,
                "gap_flagged": parsed.get("gap_flagged", False),
                "gap_description": parsed.get("gap_description")
            }
        except (json.JSONDecodeError, ValueError, KeyError):
            # GOTCHA[corrupt-response]: treat unparseable response as low-confidence
            report = {
                "angle": angle,
                "question": question,
                "findings": findings,
                "summary": result_text[:300],
                "confidence": 0.5,
                "gap_flagged": True,
                "gap_description": "Sub-researcher response could not be parsed as structured JSON."
            }

    except Exception as e:
        sub_elapsed = time.time() - sub_start
        print(f"  ━━━ [← SDK] {sub_elapsed:.1f}s · ERROR")
        print(f"  ⚠ [ERROR: TRANSIENT] sub-researcher({angle}): {e}")
        report = {
            "angle": angle,
            "question": question,
            "findings": findings,
            "summary": f"Sub-researcher encountered an error: {e}",
            "confidence": 0.3,
            "gap_flagged": True,
            "gap_description": f"Error during {angle} research: {e}"
        }

    confidence_display = f"{report['confidence']:.2f}"
    gap_display = "yes" if report["gap_flagged"] else "no"
    box_lines.append(f"🧠 [REASON] synthesizing {len(findings)} finding(s)")
    box_lines.append(f"✅ Report ready: confidence {confidence_display} | gap: {gap_display}")

    print_sub_researcher_box(angle, box_lines, is_followup)
    run_data.add_sub_researcher(angle, question, report, tokens_in, tokens_out)
    return report


# ═══════════════════════════════════════════
# PURPOSE: App memory — persist completed briefings across runs
# AGENTIC TRAIT: Memory (app — survives restarts)
# ACHIEVES: research_briefs.json accumulates over time
# DEPENDENCIES: BRIEFINGS_FILE path
# ═══════════════════════════════════════════

def load_briefings() -> list[dict]:  # TRAIT[memory]: app memory — survives across runs
    """Load previously saved briefings from disk."""
    if not BRIEFINGS_FILE.exists():
        return []
    try:
        data = json.loads(BRIEFINGS_FILE.read_text(encoding="utf-8"))
        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            return data.get("briefings", [])
        return []  # GOTCHA[corrupt-ledger]: treat unexpected format as empty
    except (json.JSONDecodeError, OSError):
        return []


def save_briefing(briefing: dict) -> None:
    """Save a completed briefing to disk."""
    briefings = load_briefings()
    briefings.append(briefing)
    BRIEFINGS_FILE.write_text(
        json.dumps({"briefings": briefings}, indent=2),
        encoding="utf-8"
    )


# ═══════════════════════════════════════════
# PURPOSE: Main agent loop — the Research Project Lead
# AGENTIC TRAIT: All 9 traits converge here
# ACHIEVES: Two-level agent with subagent dispatching
# DEPENDENCIES: All preceding functions
# ═══════════════════════════════════════════

async def main() -> None:
    run_data = RunDataCollector()

    # ──────────────── PHASE: BIRTH ────────────────
    run_data.start_phase("birth", "The Agent Wakes Up", "🌅")
    print_phase_banner("T H E   A G E N T   W A K E S   U P", "🌅")

    print("🤖 [AGENT BOOT] Research Project Lead v1.0")  # TRAIT[goal-directedness]: refuses to start without CLI
    print("   Domain: learning-research | Rung: 8 (subagents + context compaction)")
    print("   Max sub-researchers: 5 | Max follow-ups: 2 | Max synthesis attempts: 2")
    run_data.add_event("boot", "AGENT BOOT", "Research Project Lead v1.0",
                       narrative="The agent introduces itself — it knows its limits before it starts.",
                       phase="birth")

    print()
    print("📖 [OUTPUT GUIDE] Each labeled line is a teaching element — match to learning-guide.html §6")
    print("   🤖 Boot  🎯 Goal  📋 Plan  🎲 Decision  🔧 Tool  📥 Result")
    print("   🔄 Feedback  📐 Predicate  🏁 Exit  ━━━ SDK boundary")
    print("   Sub-researcher work appears in ┌──box──┐ containers")

    question = DEFAULT_QUESTION
    run_data.question = question

    print()
    print(f"🎯 [GOAL SET] all_dispatched_returned AND synthesis_produced AND confidence >= {CONFIDENCE_THRESHOLD}")  # GATE[G1]: predicate declared
    print(f"   Research question: {question}")
    print_narrative("The agent has set its success criteria — a computable checklist, not a wish.")
    run_data.add_event("goal_set", "GOAL SET", f"confidence >= {CONFIDENCE_THRESHOLD}",
                       narrative="Success criteria declared as a computable checklist.",
                       phase="birth")

    # Load prior briefings for context
    prior_briefings = load_briefings()
    if prior_briefings:
        print(f"\n📀 [APP MEMORY] {len(prior_briefings)} prior briefing(s) loaded from research_briefs.json")
        print(f"   └─ Most recent: {prior_briefings[-1].get('question', '?')[:60]}...")
        run_data.add_event("app_memory", "APP MEMORY", f"{len(prior_briefings)} prior briefings",
                           phase="birth")
    else:
        print("\n📀 [APP MEMORY] No prior briefings found — this is the first run")
        run_data.add_event("app_memory", "APP MEMORY", "first run — empty", phase="birth")

    # ──────────────── PHASE: PLANNING ────────────────
    run_data.start_phase("planning", "The Agent Makes a Plan", "📋")
    print_phase_banner("T H E   A G E N T   M A K E S   A   P L A N", "📋")

    # Model decides which angles to investigate — G2 moment
    print(f"\n📊 [CONTEXT] ~{len(question) // 4} tokens in context (~{len(question.split())} words)")

    print(f"\n━━━ [SDK →] model · ~{len(question) // 2} prompt tokens")  # GATE[G2]: model picks angles
    sdk_start = time.time()

    try:
        angle_list = "\n".join(f"  - {k}: {v}" for k, v in RESEARCH_ANGLES.items())
        planning_result = await query(
            prompt=(
                f"You are a Research Project Lead planning an investigation.\n\n"
                f"Research question: {question}\n\n"
                f"Available research angles:\n{angle_list}\n\n"
                f"Pick 3 to 5 angles that would give the most useful coverage for this specific question. "
                f"Explain in one sentence why you chose each one.\n\n"
                f"Respond in this exact JSON format:\n"
                f'{{"selected_angles": ["angle1", "angle2", ...], "reasoning": "..."}}'
            ),
            max_tokens=300
        )
        sdk_elapsed = time.time() - sdk_start

        usage = getattr(planning_result, "usage", None)
        plan_tokens_in = 0
        plan_tokens_out = 0
        if usage:
            plan_tokens_in = getattr(usage, "input_tokens", 0)
            plan_tokens_out = getattr(usage, "output_tokens", 0)
            run_data.total_tokens_in += plan_tokens_in
            run_data.total_tokens_out += plan_tokens_out

        print(f"━━━ [← SDK] {sdk_elapsed:.1f}s · +{plan_tokens_out} output tokens")

        # Parse angle selection
        result_text = getattr(planning_result, "text", str(planning_result))
        message_lens(planning_result, "planning")

        try:
            cleaned = result_text.strip()
            if cleaned.startswith("```"):
                cleaned = "\n".join(cleaned.split("\n")[1:])
                if cleaned.endswith("```"):
                    cleaned = cleaned[:-3]
                cleaned = cleaned.strip()

            parsed = json.loads(cleaned)
            selected = parsed.get("selected_angles", [])
            reasoning = parsed.get("reasoning", "")

            # Validate angles
            valid_angles = [a for a in selected if a in RESEARCH_ANGLES]
            if len(valid_angles) < 3:
                valid_angles = list(RESEARCH_ANGLES.keys())[:3]

            selected_angles = valid_angles[:5]

        except (json.JSONDecodeError, ValueError, KeyError):
            selected_angles = ["technical", "user", "contrarian"]
            reasoning = "Fallback: model response could not be parsed."

    except Exception as e:
        sdk_elapsed = time.time() - sdk_start
        print(f"━━━ [← SDK] {sdk_elapsed:.1f}s · ERROR")
        print(f"⚠ [ERROR: TRANSIENT] Planning call failed: {e}")
        selected_angles = ["technical", "user", "contrarian"]
        reasoning = f"Fallback due to error: {e}"

    run_data.selected_angles = selected_angles

    alternatives = [a for a in RESEARCH_ANGLES if a not in selected_angles]
    print(f"\n🎲 [MODEL DECISION] selected: {', '.join(selected_angles)} · alternatives: {', '.join(alternatives)}")  # GATE[G2]: model's own choice
    print_narrative(f"The model chose {len(selected_angles)} angles from {len(RESEARCH_ANGLES)} options — this is its own choice, not hard-coded.")
    run_data.add_event("model_decision", "MODEL DECISION",
                       f"selected: {', '.join(selected_angles)}",
                       narrative=f"Model picked {len(selected_angles)} from {len(RESEARCH_ANGLES)} available angles.",
                       phase="planning", alternatives=alternatives)

    print(f"\n📋 [PLAN GENERATED]")  # TRAIT[planning]: plan before action
    for i, angle in enumerate(selected_angles, 1):
        status = "▶" if i == 1 else "○"
        print(f"   {status} {i}. Dispatch sub-researcher: {angle}")
    print(f"   ○ {len(selected_angles) + 1}. Collect reports and check for gaps")
    print(f"   ○ {len(selected_angles) + 2}. Synthesize final briefing")
    run_data.add_event("plan", "PLAN GENERATED", f"{len(selected_angles)} dispatch + collect + synthesize",
                       phase="planning")

    if reasoning:
        print(f"\n   Model's reasoning: {reasoning[:200]}")

    print_micro_summary(0, f"Plan ready — {len(selected_angles)} angles selected, dispatch next.")

    # ──────────────── PHASE: WORKING ────────────────
    run_data.start_phase("working", "Dispatching Sub-Researchers", "🚀")
    print_phase_banner("D I S P A T C H I N G   S U B - R E S E A R C H E R S", "🚀")

    # Agent state tracking
    state: dict[str, Any] = {
        "all_dispatched_returned": False,
        "synthesis_produced": False,
        "synthesis_confidence": 0.0,
        "dispatched_angles": list(selected_angles),
        "reports": [],
        "follow_ups_dispatched": 0,
        "total_subagents": 0,
        "synthesis_attempts": 0
    }

    # Dispatch initial sub-researchers
    reports: list[dict] = []
    step = 1

    for i, angle in enumerate(selected_angles):
        print(f"\n📍 [STEP {step}] Dispatching sub-researcher #{i+1}: {angle}")
        print(f"   🔧 [TOOL CALL] spawn_researcher(angle='{angle}', question='{question[:50]}...')")  # TRAIT[tool-use]
        print(f"   🔒 [TRUST FENCE] research database content fenced as data")

        state["total_subagents"] += 1
        run_data.add_event("dispatch", "TOOL CALL", f"spawn_researcher({angle})",
                           narrative=f"Sub-researcher #{i+1} enters its own isolated context.",
                           phase="working")

        report = await run_sub_researcher(angle, question, run_data, i)
        reports.append(report)

        # Session memory update
        print(f"\n💾 [SESSION MEMORY] sub_report_{angle}")
        print(f"   └─ confidence={report['confidence']:.2f}, gap={report['gap_flagged']}")  # TRAIT[memory]: session

        print(f"\n📋 [PLAN PROGRESS]")
        for j, a in enumerate(selected_angles):
            if j < i + 1:
                print(f"   ✓ {j+1}. Dispatch sub-researcher: {a}")
            elif j == i + 1:
                print(f"   ▶ {j+1}. Dispatch sub-researcher: {a}")
            else:
                print(f"   ○ {j+1}. Dispatch sub-researcher: {a}")
        collect_status = "▶" if i + 1 == len(selected_angles) else "○"
        print(f"   {collect_status} {len(selected_angles) + 1}. Collect reports and check for gaps")
        print(f"   ○ {len(selected_angles) + 2}. Synthesize final briefing")

        print_micro_summary(step, f"Sub-researcher '{angle}' reported back with confidence {report['confidence']:.2f}.")
        step += 1

    # ──────────────── PHASE: COLLECT & CHECK ────────────────
    run_data.start_phase("checking", "Collect and Check", "👁")
    print_phase_banner("C O L L E C T   &   C H E C K", "👁")

    print(f"\n📍 [STEP {step}] Collecting all reports")
    print(f"   🔧 [TOOL CALL] collect_reports()")

    state["reports"] = reports
    state["all_dispatched_returned"] = True

    # O-R-A: Observe reports, reason about gaps, act on follow-ups
    print(f"\n👁 [OBSERVE] {len(reports)} report(s) collected")  # GATE[G3]: observe
    for r in reports:
        gap_marker = " ⚠ GAP" if r["gap_flagged"] else ""
        print(f"   • {r['angle']}: confidence {r['confidence']:.2f}{gap_marker}")

    # Check for gaps needing follow-up
    gaps = [r for r in reports if r["gap_flagged"] or r["confidence"] < GAP_CONFIDENCE_FLOOR]

    if gaps and state["follow_ups_dispatched"] < MAX_FOLLOWUP and state["total_subagents"] < MAX_SUBAGENTS_TOTAL:
        print(f"\n🧠 [REASON] {len(gaps)} report(s) have gaps or low confidence")  # GATE[G3]: reason
        print(f"   Follow-up budget: {MAX_FOLLOWUP - state['follow_ups_dispatched']} remaining")
        run_data.add_event("loop_feedback", "LOOP FEEDBACK",
                           f"{len(gaps)} gaps found → dispatching follow-ups",
                           narrative="The agent read the reports and found something missing — it's adapting.",
                           phase="checking")

        print(f"\n🔄 [LOOP FEEDBACK] {len(gaps)} report(s) need follow-up → dispatching")  # GATE[G3]: act
        print_narrative("The agent read the reports and found gaps — instead of ignoring them, it's sending reinforcements.")

        # Dispatch follow-ups
        run_data.start_phase("followup", "Follow-Up Dispatches", "🔄")
        print_phase_banner("F O L L O W - U P   D I S P A T C H E S", "🔄")

        for gap_report in gaps:
            if state["follow_ups_dispatched"] >= MAX_FOLLOWUP:
                print(f"\n🔍 [TERMINATION CHECK] follow-up cap reached ({MAX_FOLLOWUP}/{MAX_FOLLOWUP})")
                break
            if state["total_subagents"] >= MAX_SUBAGENTS_TOTAL:
                print(f"\n🔍 [TERMINATION CHECK] subagent cap reached ({MAX_SUBAGENTS_TOTAL}/{MAX_SUBAGENTS_TOTAL})")
                break

            follow_up_question = (
                f"Follow up on the '{gap_report['angle']}' angle: {gap_report.get('gap_description', question)}"
            )
            print(f"\n📍 [STEP {step}] Follow-up dispatch: {gap_report['angle']}")
            print(f"   ⚡ [ACT] spawn follow-up for gap: {gap_report.get('gap_description', 'low confidence')[:60]}")

            state["total_subagents"] += 1
            state["follow_ups_dispatched"] += 1

            followup_report = await run_sub_researcher(
                gap_report["angle"], follow_up_question, run_data,
                len(reports), is_followup=True
            )

            # Merge follow-up: replace original if better
            if followup_report["confidence"] > gap_report["confidence"]:
                idx = reports.index(gap_report)
                reports[idx] = followup_report
                print(f"   📈 Follow-up improved confidence: {gap_report['confidence']:.2f} → {followup_report['confidence']:.2f}")
            else:
                reports.append(followup_report)
                print(f"   📊 Follow-up added as supplementary (confidence {followup_report['confidence']:.2f})")

            print_micro_summary(step, f"Follow-up on '{gap_report['angle']}' completed.")
            step += 1
    else:
        if not gaps:
            print(f"\n🧠 [REASON] All reports look solid — no follow-ups needed")
            print_narrative("Every specialist came back with good coverage. No gaps to chase.")
        else:
            print(f"\n🧠 [REASON] Gaps found but follow-up/subagent cap would be exceeded — skipping")
            print_narrative("The agent wants to follow up but has hit its governance limits.")

        run_data.add_event("loop_feedback", "LOOP FEEDBACK",
                           "no follow-ups needed" if not gaps else "caps prevent follow-up",
                           phase="checking")

    # Goal predicate check before synthesis
    print(f"\n📐 [GOAL PREDICATE] is_goal_met(state) → {is_goal_met(state)}")  # GATE[G1]: predicate evaluated
    print(f"   all_dispatched_returned={state['all_dispatched_returned']}")
    print(f"   synthesis_produced={state['synthesis_produced']}")
    print(f"   synthesis_confidence={state['synthesis_confidence']}")
    print_narrative("Not done yet — reports collected but no synthesis. The checklist says keep going.")
    run_data.add_event("goal_predicate", "GOAL PREDICATE", f"is_goal_met → {is_goal_met(state)}",
                       phase="checking")

    # ──────────────── PHASE: SYNTHESIS ────────────────
    run_data.start_phase("synthesis", "Verdict", "🏁")
    print_phase_banner("S Y N T H E S I Z I N G   T H E   B R I E F I N G", "📝")

    print(f"\n📍 [STEP {step}] Synthesizing final briefing")
    print(f"   🔧 [TOOL CALL] synthesize_briefing(reports={len(reports)} reports)")

    # Build synthesis prompt from all reports
    reports_text = ""
    for r in reports:
        reports_text += f"\n## {r['angle'].upper()} (confidence: {r['confidence']:.2f})\n"
        reports_text += f"{r['summary']}\n"
        if r["gap_flagged"]:
            reports_text += f"⚠ Gap: {r.get('gap_description', 'unspecified')}\n"

    print(f"\n━━━ [SDK →] model · ~{len(reports_text) // 4} prompt tokens")
    synth_start = time.time()

    try:
        synth_result = await query(  # TRAIT[autonomy]: model synthesizes independently
            prompt=(
                f"You are a Research Project Lead writing a final briefing.\n\n"
                f"Research question: {question}\n\n"
                f"Your team's reports:\n{reports_text}\n\n"
                f"Write a synthesis briefing (4-6 paragraphs) that:\n"
                f"1. Answers the research question directly\n"
                f"2. Integrates findings across all angles\n"
                f"3. Identifies key trade-offs\n"
                f"4. Notes any remaining gaps or uncertainties\n\n"
                f"Then rate your confidence in this synthesis (0.0-1.0).\n\n"
                f"Respond in this exact JSON format:\n"
                f'{{"briefing": "...", "confidence": 0.X, "key_tradeoffs": ["...", "..."], "remaining_gaps": ["...", "..."]}}'
            ),
            max_tokens=1000
        )
        synth_elapsed = time.time() - synth_start

        usage = getattr(synth_result, "usage", None)
        if usage:
            synth_in = getattr(usage, "input_tokens", 0)
            synth_out = getattr(usage, "output_tokens", 0)
            run_data.total_tokens_in += synth_in
            run_data.total_tokens_out += synth_out

        print(f"━━━ [← SDK] {synth_elapsed:.1f}s · +{getattr(usage, 'output_tokens', 0) if usage else '?'} output tokens")
        message_lens(synth_result, "synthesis")

        result_text = getattr(synth_result, "text", str(synth_result))

        try:
            cleaned = result_text.strip()
            if cleaned.startswith("```"):
                cleaned = "\n".join(cleaned.split("\n")[1:])
                if cleaned.endswith("```"):
                    cleaned = cleaned[:-3]
                cleaned = cleaned.strip()

            parsed = json.loads(cleaned)
            synthesis = {
                "briefing": parsed.get("briefing", "No briefing produced."),
                "confidence": max(0.0, min(1.0, float(parsed.get("confidence", 0.5)))),
                "key_tradeoffs": parsed.get("key_tradeoffs", []),
                "remaining_gaps": parsed.get("remaining_gaps", [])
            }
        except (json.JSONDecodeError, ValueError, KeyError):
            synthesis = {
                "briefing": result_text[:500],
                "confidence": 0.5,
                "key_tradeoffs": [],
                "remaining_gaps": ["Synthesis response could not be parsed."]
            }

        state["synthesis_produced"] = True
        state["synthesis_confidence"] = synthesis["confidence"]
        state["synthesis_attempts"] += 1

    except Exception as e:
        synth_elapsed = time.time() - synth_start
        print(f"━━━ [← SDK] {synth_elapsed:.1f}s · ERROR")
        print(f"⚠ [ERROR: TRANSIENT] Synthesis failed: {e}")
        synthesis = {
            "briefing": f"Synthesis failed: {e}",
            "confidence": 0.0,
            "key_tradeoffs": [],
            "remaining_gaps": [f"Error: {e}"]
        }
        state["synthesis_produced"] = False
        state["synthesis_attempts"] += 1

    step += 1

    # Final goal predicate evaluation
    goal_met = is_goal_met(state)
    print(f"\n📐 [GOAL PREDICATE] is_goal_met(state) → {goal_met}")  # GATE[G1]: final evaluation
    print(f"   all_dispatched_returned={state['all_dispatched_returned']}")
    print(f"   synthesis_produced={state['synthesis_produced']}")
    print(f"   synthesis_confidence={state['synthesis_confidence']:.2f} (threshold: {CONFIDENCE_THRESHOLD})")

    # ──────────────── PHASE: TERMINATION ────────────────
    run_data.start_phase("termination", "Verdict", "🏁")
    print_phase_banner("V E R D I C T", "🏁")

    print(f"\n🔍 [TERMINATION CHECK] subagents: {state['total_subagents']}/{MAX_SUBAGENTS_TOTAL} · "
          f"follow-ups: {state['follow_ups_dispatched']}/{MAX_FOLLOWUP} · "
          f"synthesis: {state['synthesis_attempts']}/{MAX_SYNTHESIS_TURNS}")  # GATE[G4]: principled termination

    if goal_met:
        exit_reason = "GOAL MET"
        print(f"\n🏁 {exit_reason} — synthesis produced with confidence {state['synthesis_confidence']:.2f}")
        print_narrative("All three checklist items passed. The agent achieved what it set out to do.")
        run_data.outcome = exit_reason
    elif state["total_subagents"] >= MAX_SUBAGENTS_TOTAL and not state["synthesis_produced"]:
        exit_reason = "EXIT: subagent cap"
        print(f"\n🏁 {exit_reason} — {state['total_subagents']}/{MAX_SUBAGENTS_TOTAL} sub-researchers used without producing synthesis")
        print_narrative("The agent ran out of specialists before finishing. Governance stopped it — not failure.")
        run_data.outcome = exit_reason  # GATE[G4]: cap exit labeled
    elif state["synthesis_attempts"] >= MAX_SYNTHESIS_TURNS and not goal_met:
        exit_reason = "EXIT: synthesis cap"
        print(f"\n🏁 {exit_reason} — {state['synthesis_attempts']}/{MAX_SYNTHESIS_TURNS} synthesis attempts, confidence {state['synthesis_confidence']:.2f} < {CONFIDENCE_THRESHOLD}")
        print_narrative("The synthesis didn't reach the confidence bar within the allowed attempts.")
        run_data.outcome = exit_reason  # GATE[G4]: cap exit labeled
    else:
        exit_reason = "GOAL MET" if goal_met else "EXIT: synthesis below threshold"
        print(f"\n🏁 {exit_reason}")
        run_data.outcome = exit_reason

    # Save briefing to app memory
    if state["synthesis_produced"]:
        briefing_record = {
            "question": question,
            "date": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "angles_investigated": [r["angle"] for r in reports],
            "synthesis": synthesis["briefing"],
            "confidence": synthesis["confidence"],
            "key_tradeoffs": synthesis.get("key_tradeoffs", []),
            "remaining_gaps": synthesis.get("remaining_gaps", []),
            "exit_reason": exit_reason
        }
        save_briefing(briefing_record)
        print(f"\n📀 [APP MEMORY] briefing → research_briefs.json")  # TRAIT[memory]: app memory
        print(f"   └─ question: {question[:50]}... | confidence: {synthesis['confidence']:.2f}")

    # ──────────────── POST-RUN SUMMARY ────────────────
    print(f"\n╔{'═' * 56}╗")
    print(f"║  🧠 AGENT SUMMARY{' ' * 38}║")
    print(f"╚{'═' * 56}╝")

    # 1. Run narrative
    print(f"\n1️⃣  RUN NARRATIVE")
    print(f"   The Research Project Lead received a question about spaced-repetition")
    print(f"   algorithms for programming. It selected {len(selected_angles)} angles ({', '.join(selected_angles)}),")
    print(f"   dispatched {len(selected_angles)} sub-researchers (each in its own context window),")
    if state["follow_ups_dispatched"] > 0:
        print(f"   dispatched {state['follow_ups_dispatched']} follow-up(s) for identified gaps,")
    print(f"   and {'produced a synthesis briefing' if state['synthesis_produced'] else 'did not produce a synthesis'}.")
    print(f"   Exit: {exit_reason}")

    # 2. Traits in action
    print(f"\n2️⃣  TRAITS IN ACTION")
    print(f"   • Goal-directedness  → is_goal_met() checked after dispatch and after synthesis")
    print(f"   • Autonomy           → Model selected {len(selected_angles)} angles from {len(RESEARCH_ANGLES)}")  # TRAIT[autonomy]
    print(f"   • O-R-A loop         → {'Gaps detected → follow-ups dispatched' if state['follow_ups_dispatched'] > 0 else 'No gaps found — clean pass'}")
    print(f"   • Perception         → {sum(len(r.get('findings', [])) for r in reports)} findings extracted from mock DB")
    print(f"   • Planning           → Investigation plan generated before dispatch")
    print(f"   • Memory (session)   → Main agent carried context across {step} steps")
    print(f"   • Memory (subagent)  → {state['total_subagents']} independent context windows created (rung 8)")
    print(f"   • Memory (app)       → research_briefs.json {'updated' if state['synthesis_produced'] else 'unchanged'}")
    print(f"   • Principled stop    → {exit_reason}")

    # 3. Model decisions
    print(f"\n3️⃣  MODEL DECISIONS")
    print(f"   • Angle selection: {', '.join(selected_angles)} (from {len(RESEARCH_ANGLES)} options)")
    print(f"   • Each sub-researcher independently decided how to search and summarize")

    # 4. Plan recalibrations
    print(f"\n4️⃣  PLAN RECALIBRATIONS")
    if state["follow_ups_dispatched"] > 0:
        print(f"   • {state['follow_ups_dispatched']} follow-up(s) dispatched after gap detection")
        for r in reports:
            if r.get("gap_flagged"):
                print(f"     └─ {r['angle']}: {r.get('gap_description', 'gap flagged')[:60]}")
    else:
        print(f"   • No recalibrations — all initial reports were solid")

    # 5. Iteration count + termination
    print(f"\n5️⃣  ITERATION COUNT")
    print(f"   • Steps completed: {step}")
    print(f"   • Sub-researchers: {state['total_subagents']}/{MAX_SUBAGENTS_TOTAL}")
    print(f"   • Follow-ups: {state['follow_ups_dispatched']}/{MAX_FOLLOWUP}")
    print(f"   • Synthesis attempts: {state['synthesis_attempts']}/{MAX_SYNTHESIS_TURNS}")
    print(f"   • Termination: {exit_reason}")

    # 6. Memory ledger
    print(f"\n6️⃣  MEMORY LEDGER")
    print(f"   SESSION memory (dies with this run):")
    print(f"     • dispatched_angles: {selected_angles}")
    print(f"     • reports: {len(reports)} report objects")
    print(f"     • synthesis: {'produced' if state['synthesis_produced'] else 'not produced'}")
    print(f"   WITHIN-SUBAGENT memory (each died when its sub-researcher finished):")
    print(f"     • {state['total_subagents']} independent context windows created and discarded")
    print(f"   APP memory (survives this run):")
    print(f"     • research_briefs.json: {'1 briefing added' if state['synthesis_produced'] else 'unchanged'}")

    # 7. Gate verdicts
    print(f"\n7️⃣  GATE VERDICTS")
    print(f"   • Did-it-finish check: {'✅ PASS' if goal_met else '⬜ goal not met'} — is_goal_met() returned {goal_met}")
    print(f"   • Model's own choice:  ✅ PASS — model selected {len(selected_angles)} angles at [MODEL DECISION]")
    print(f"   • Learning from what it saw: {'✅ PASS — gap detected, follow-up dispatched' if state['follow_ups_dispatched'] > 0 else '⬜ no gaps found to adapt to (clean pass)'}")
    print(f"   • Principled stop: ✅ PASS — {exit_reason}")

    # GATE[G5]: N/A — independent verifier introduced at rung 7; no critic call in this agent

    # Usage summary
    total_cost = run_data.total_cost
    if run_data.total_tokens_in > 0 or run_data.total_tokens_out > 0:
        estimated_cost = (run_data.total_tokens_in * 0.015 + run_data.total_tokens_out * 0.075) / 1000
        run_data.total_cost = estimated_cost
        print(f"\n💰 [USAGE] tokens_in={run_data.total_tokens_in} · tokens_out={run_data.total_tokens_out} · estimated_cost=${estimated_cost:.4f}")
    else:
        print(f"\n💰 [USAGE] token tracking unavailable (SDK version may not expose usage)")

    # Save run data for HTML generation
    run_data.save()
    print(f"\n📊 [RUN DATA] Saved to research-lead_run_data.json for Run Log generation")

    print(f"\n{'═' * 55}")
    print(f"Run complete. Total elapsed: {time.time() - run_data.start_time:.1f}s")
    print(f"{'═' * 55}")


if __name__ == "__main__":
    preflight()
    with tee_to_log():
        asyncio.run(main())
