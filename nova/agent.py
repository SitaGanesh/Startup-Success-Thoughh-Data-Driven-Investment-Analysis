"""
nova/agent.py — Agentic Investment Research Agent (Amazon Nova)
────────────────────────────────────────────────────────────────
An explicitly multi-step reasoning agent that uses Amazon Nova Pro to:

  Step 1 — Profile Scout     : Extract key signals from startup data + ML result
  Step 2 — Market Researcher : Deep-dive into the target market
  Step 3 — Risk Auditor      : Stress-test the business model
  Step 4 — Investment Verdict: Synthesise all steps → final investment thesis

Each step sees the outputs of all previous steps, building a chain of reasoning.
This is the "Agentic AI" submission showing Nova's reasoning across complex,
multi-step investment analysis problems.

Entry point:
    run_investment_agent(startup_data, ml_result) -> AgentResult
"""

import json
import os
import re
import time
from dataclasses import dataclass, field
from typing import Optional

try:
    from .client import converse, NOVA_PRO, NOVA_LITE
except ImportError:
    # Support direct execution: python agent.py
    from client import converse, NOVA_PRO, NOVA_LITE


STEP_MODEL = os.getenv("NOVA_AGENT_STEP_MODEL", NOVA_LITE)
FINAL_MODEL = os.getenv("NOVA_AGENT_FINAL_MODEL", STEP_MODEL)
STEP_MAX_TOKENS = int(os.getenv("NOVA_AGENT_STEP_MAX_TOKENS", "768"))
FINAL_MAX_TOKENS = int(os.getenv("NOVA_AGENT_FINAL_MAX_TOKENS", "1100"))


# ── Data classes ─────────────────────────────────────────────

@dataclass
class AgentStep:
    name: str
    prompt_summary: str
    output: str
    duration_ms: int


@dataclass
class AgentResult:
    startup_summary:   str
    market_research:   str
    risk_audit:        str
    investment_thesis: str
    final_score:       float          # 0.0 – 1.0 agent confidence
    # {"invest": bool, "stage": str, "conditions": [...]}
    verdicts:          dict
    steps:             list[AgentStep] = field(default_factory=list)
    total_duration_ms: int = 0

    def to_dict(self) -> dict:
        return {
            "startup_summary":   self.startup_summary,
            "market_research":   self.market_research,
            "risk_audit":        self.risk_audit,
            "investment_thesis": self.investment_thesis,
            "final_score":       self.final_score,
            "verdicts":          self.verdicts,
            "steps": [
                {
                    "name":           s.name,
                    "prompt_summary": s.prompt_summary,
                    "output":         s.output,
                    "duration_ms":    s.duration_ms,
                }
                for s in self.steps
            ],
            "total_duration_ms": self.total_duration_ms,
        }


# ── System prompts ────────────────────────────────────────────

_AGENT_SYSTEM = """\
You are an agentic investment research AI powered by Amazon Nova. You operate
as a team of specialist personas combined into one:

1. PROFILE SCOUT — extracts the clearest signals from raw startup data
2. MARKET RESEARCHER — sizes the opportunity and landscape
3. RISK AUDITOR — challenges assumptions and stress-tests business models
4. INVESTMENT STRATEGIST — builds a high-conviction or clear-pass thesis

You think step-by-step. You are rigorous, specific, and direct.
You always reference the data and prior steps explicitly.
Format each output with ## section headers and - bullet points.
"""


# ──────────────────────────────────────────────────────────────
# Step implementations
# ──────────────────────────────────────────────────────────────

def _step_profile_scout(startup_data: dict, ml_result: dict) -> str:
    """Step 1: Extract clean signal profile from raw startup data + ML output."""
    prob_pct = round(ml_result.get("probability", 0) * 100, 1)
    band = ml_result.get("confidence_band", "UNKNOWN")
    verdict = "SUCCESS" if ml_result.get("success", 0) == 1 else "FAILURE"
    model = ml_result.get("best_model_name", "ML Ensemble")

    prompt = f"""\
## AGENT STEP 1 — PROFILE SCOUT

You are acting as the PROFILE SCOUT. Your job is to extract the most
important investment signals from the raw startup data below and the
ML model's prediction.

### Raw Startup Data
{json.dumps(startup_data, indent=2)}

### ML Model Prediction
- Prediction: {verdict}
- Success Probability: {prob_pct}%
- Confidence Band: {band}
- Model: {model} (trained on 49,000+ real startups)

### Your Task
Produce a structured SIGNAL PROFILE with these sections:

## Strongest Positive Signals
What does the data tell you is working well? Cite specific numbers.

## Warning Signals
What data points raise concern? Be specific.

## Data Completeness
Rate the quality and completeness of information provided (A/B/C/D).
What critical information is missing that would change your analysis?

## ML Model Interpretation
Does the {prob_pct}% probability feel appropriate given the data? Why or why not?

Keep each section tight — bullet points only, no fluff.
"""
    return converse(
        messages=[{"role": "user", "content": [{"text": prompt}]}],
        system_prompt=_AGENT_SYSTEM,
        model_id=STEP_MODEL,
        max_tokens=STEP_MAX_TOKENS,
        temperature=0.4,
    )


def _step_market_researcher(startup_data: dict, profile_output: str) -> str:
    """Step 2: Deep market research informed by Step 1 profile."""
    market = startup_data.get("market", "the target market")
    country = startup_data.get("country_code", "global")
    year = startup_data.get("founded_year", "recent")

    prompt = f"""\
## AGENT STEP 2 — MARKET RESEARCHER

You are the MARKET RESEARCHER. You have the profile scout's findings (Step 1)
and must now perform deep market research. Build on the scout's findings —
do not repeat them.

### Profile Scout Output (Step 1)
{profile_output}

### Market Under Analysis
- Industry: **{market}**
- Startup Geography: **{country}**
- Founded: **{year}**

### Your Task
Produce a structured MARKET INTELLIGENCE BRIEF:

## Market Size & Growth
Current TAM/SAM (USD), CAGR, and 3-year growth trajectory.

## Competitive Dynamics
Who are the top 3–5 players? What does market concentration look like?
Is this winner-take-all or fragmented?

## Startup Opportunity Window
Is the timing right for a new entrant in **{market}** in {country}?
What specific niche or wedge can win?

## Funding Climate
Recent VC investment activity in this sector. Are investors bullish or bearish?

## Market Risk Score
RATE: Low / Medium / High / Very High — and justify in 2 sentences.
"""
    return converse(
        messages=[{"role": "user", "content": [{"text": prompt}]}],
        system_prompt=_AGENT_SYSTEM,
        model_id=STEP_MODEL,
        max_tokens=STEP_MAX_TOKENS,
        temperature=0.4,
    )


def _step_risk_auditor(
    startup_data: dict,
    profile_output: str,
    market_output: str,
) -> str:
    """Step 3: Independent risk audit that stress-tests everything found so far."""
    prompt = f"""\
## AGENT STEP 3 — RISK AUDITOR

You are the RISK AUDITOR. Your role is to challenge every assumption,
identify what could go wrong, and stress-test the thesis being built.
Do not simply agree with steps 1 and 2 — push back where warranted.

### Profile Scout Output (Step 1)
{profile_output}

### Market Research Output (Step 2)
{market_output}

### Raw Data Reference
{json.dumps(startup_data, indent=2)}

### Your Task
Produce a structured RISK AUDIT:

## Execution Risks
3–5 specific risks related to building and scaling this business.

## Market Timing Risks
Is the market too early, too late, or too crowded? Evidence?

## Funding Path Risks
Given the current funding profile, what are the likely fundraising obstacles?
What burn rate / runway concerns exist?

## Team & Capability Gaps
What critical capabilities are likely missing based on the data?

## Existential Threats
What single scenario could kill this company in 12 months?

## Risk Summary Score
RATE overall risk: 1 (minimal) – 10 (extreme) with one-line justification.
"""
    return converse(
        messages=[{"role": "user", "content": [{"text": prompt}]}],
        system_prompt=_AGENT_SYSTEM,
        model_id=STEP_MODEL,
        max_tokens=STEP_MAX_TOKENS,
        temperature=0.3,
    )


def _step_investment_verdict(
    startup_data: dict,
    ml_result: dict,
    profile_output: str,
    market_output: str,
    risk_output: str,
) -> tuple[str, float, dict]:
    """
    Step 4: Final synthesis — investment thesis + structured verdict JSON.
    Returns (thesis_text, score_float, verdicts_dict).
    """
    prob_pct = round(ml_result.get("probability", 0) * 100, 1)

    prompt = f"""\
## AGENT STEP 4 — INVESTMENT STRATEGIST (FINAL SYNTHESIS)

You are the INVESTMENT STRATEGIST. You now have three expert reports from
your team. Synthesise everything into a single, high-conviction investment thesis.

### Profile Scout (Step 1)
{profile_output}

### Market Researcher (Step 2)
{market_output}

### Risk Auditor (Step 3)
{risk_output}

### ML Model Probability: {prob_pct}%

### Your Task

## Investment Thesis
2–3 paragraph narrative: why invest or pass, referencing all 3 steps.

## Strategic Recommendations
5 concrete, prioritised actions the founder should take immediately.

## Milestone Gates
What must this startup achieve in the next 6 months to earn the next
funding round? List 3–4 specific, measurable milestones.

## Investment Verdict
Respond with EXACTLY this JSON block at the END of your response
(after all markdown sections):

```json
{{
  "invest": true,
  "recommendation": "Invest / Conditional / Pass",
  "conviction_score": 0.72,
  "ideal_stage": "Seed / Series A / Pre-seed",
  "target_valuation_range": "$Xm – $Ym",
  "key_conditions": ["condition 1", "condition 2", "condition 3"]
}}
```

Replace the values appropriately. conviction_score must be between 0.0 and 1.0.
"""
    raw = converse(
        messages=[{"role": "user", "content": [{"text": prompt}]}],
        system_prompt=_AGENT_SYSTEM,
        model_id=FINAL_MODEL,
        max_tokens=FINAL_MAX_TOKENS,
        temperature=0.4,
    )

    # Extract JSON verdict block (for structured fields) and remove it from
    # displayed markdown so the UI doesn't show raw JSON to users.
    verdicts = {
        "invest": ml_result.get("success", 0) == 1,
        "recommendation": "Conditional",
        "conviction_score": round(ml_result.get("probability", 0.5), 2),
        "ideal_stage": "Seed",
        "target_valuation_range": "To be determined",
        "key_conditions": [],
    }
    score = ml_result.get("probability", 0.5)
    cleaned_text = raw

    try:
        # Find fenced JSON block between ```json ... ``` (case-insensitive)
        match = re.search(
            r"```\s*json\s*(\{[\s\S]*?\})\s*```", raw, re.IGNORECASE)
        if match:
            parsed = json.loads(match.group(1).strip())
            verdicts.update(parsed)
            score = float(parsed.get("conviction_score", score))
            cleaned_text = (raw[:match.start()] + raw[match.end():]).strip()
    except (ValueError, KeyError, json.JSONDecodeError):
        pass  # Use ML-derived defaults

    return cleaned_text, score, verdicts


# ──────────────────────────────────────────────────────────────
# Public entry point
# ──────────────────────────────────────────────────────────────

def run_investment_agent(
    startup_data: dict,
    ml_result: dict,
) -> AgentResult:
    """
    Run the full 4-step investment research agent.

    Parameters
    ----------
    startup_data : Raw input fields (market, funding, country, etc.).
    ml_result    : Prediction output (probability, confidence_band, etc.).

    Returns
    -------
    AgentResult — full agentic analysis with all intermediate steps.
    """
    agent_start = time.time()
    steps: list[AgentStep] = []

    # ── Step 1 ────────────────────────────────────────────────
    t0 = time.time()
    profile = _step_profile_scout(startup_data, ml_result)
    steps.append(AgentStep(
        name="Profile Scout",
        prompt_summary="Signal extraction from startup data + ML prediction",
        output=profile,
        duration_ms=int((time.time() - t0) * 1000),
    ))

    # ── Step 2 ────────────────────────────────────────────────
    t0 = time.time()
    market = _step_market_researcher(startup_data, profile)
    steps.append(AgentStep(
        name="Market Researcher",
        prompt_summary=f"Market intelligence for '{startup_data.get('market', 'target market')}'",
        output=market,
        duration_ms=int((time.time() - t0) * 1000),
    ))

    # ── Step 3 ────────────────────────────────────────────────
    t0 = time.time()
    risks = _step_risk_auditor(startup_data, profile, market)
    steps.append(AgentStep(
        name="Risk Auditor",
        prompt_summary="Independent risk audit and stress-testing",
        output=risks,
        duration_ms=int((time.time() - t0) * 1000),
    ))

    # ── Step 4 ────────────────────────────────────────────────
    t0 = time.time()
    thesis, score, verdicts = _step_investment_verdict(
        startup_data, ml_result, profile, market, risks
    )
    steps.append(AgentStep(
        name="Investment Strategist",
        prompt_summary="Final synthesis → conviction score + structured verdict",
        output=thesis,
        duration_ms=int((time.time() - t0) * 1000),
    ))

    total_ms = int((time.time() - agent_start) * 1000)

    return AgentResult(
        startup_summary=profile,
        market_research=market,
        risk_audit=risks,
        investment_thesis=thesis,
        final_score=score,
        verdicts=verdicts,
        steps=steps,
        total_duration_ms=total_ms,
    )
