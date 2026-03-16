"""
nova/analyzer.py — Deep startup analysis using Amazon Nova Pro
──────────────────────────────────────────────────────────────
Combines the ML prediction result with Nova's reasoning to produce
a structured investment analysis report in markdown format.
"""

import os

try:
    from .client import converse, NOVA_LITE
except ImportError:
    # Support direct execution: python analyzer.py
    from client import converse, NOVA_LITE


ANALYZE_MODEL = os.getenv("NOVA_ANALYZE_MODEL", NOVA_LITE)
ANALYZE_MAX_TOKENS = int(os.getenv("NOVA_ANALYZE_MAX_TOKENS", "1200"))

# ── System prompt —————————————————————————————————————————————
_SYSTEM = """\
You are StartupOracle, an expert startup analyst and venture capital advisor \
with 20+ years of experience evaluating early-stage companies across every \
major market sector.

You combine data-driven machine learning results with deep market knowledge \
to produce actionable, honest analysis. Your reports are professional, \
structured, and directly useful to founders, investors, and accelerator teams.

FORMATTING RULES:
- Use ## for section headers (exactly as shown in the task prompt)
- Use - for bullet points
- Use **text** for emphasis on key terms or numbers
- Keep each section focused and specific — no fluff
- Reference the actual numbers and data provided
"""


def analyze_startup(startup_data: dict, ml_result: dict) -> str:
    """
    Generate a full startup analysis report.

    Parameters
    ----------
    startup_data : Raw input fields (market, funding, country, etc.).
    ml_result    : Prediction output (probability, confidence_band, etc.).

    Returns
    -------
    str — Markdown-formatted analysis report from Amazon Nova Pro.
    """
    prob_pct = round(ml_result.get("probability", 0) * 100, 1)
    band = ml_result.get("confidence_band", "UNKNOWN")
    model = ml_result.get("best_model_name", "ML Ensemble")
    verdict = "SUCCESS" if ml_result.get("success", 0) == 1 else "FAILURE"

    startup_desc = _format_startup_data(startup_data)
    market_name = startup_data.get("market", "the target market")

    prompt = f"""\
I need a comprehensive investment analysis for the following startup.

## STARTUP PROFILE
{startup_desc}

## ML PREDICTION RESULT
- **Prediction:** {verdict}
- **Success Probability:** {prob_pct}%
- **Confidence Band:** {band}
- **Model Used:** {model} (trained on 49,000+ real startups)

## YOUR TASK
Write a structured investment analysis with these exact sections.
Reference the startup data and ML numbers throughout.

## Executive Summary
2–3 sentence verdict combining the ML prediction with your analysis.

## Strengths
3–5 specific strengths based on the data provided above.

## Risk Factors
3–5 specific risks and concerns given this startup's profile.

## Market Assessment
Brief analysis of the **{market_name}** market opportunity and \
competitive landscape.

## Strategic Recommendations
4–6 concrete, actionable steps this founder should take to improve \
their odds of success.

## Investment Verdict
Clear statement: would you invest? What valuation range makes sense? \
What conditions or milestones would change your view?
"""

    return converse(
        messages=[{"role": "user", "content": [{"text": prompt}]}],
        system_prompt=_SYSTEM,
        model_id=ANALYZE_MODEL,
        max_tokens=ANALYZE_MAX_TOKENS,
        temperature=0.6,
    )


# ── Internal helpers ──────────────────────────────────────────
def _format_startup_data(data: dict) -> str:
    lines = []

    if data.get("market"):
        lines.append(f"- **Market/Industry:** {data['market']}")
    if data.get("country_code"):
        lines.append(f"- **Country:** {data['country_code']}")

    loc_parts = [data.get("city"), data.get("region")]
    loc = ", ".join(p for p in loc_parts if p)
    if loc:
        lines.append(f"- **Location:** {loc}")

    if data.get("founded_year"):
        lines.append(f"- **Founded:** {data['founded_year']}")

    usd = data.get("funding_total_usd")
    if usd:
        label = f"${usd / 1_000_000:.1f}M" if usd >= 1_000_000 else f"${usd:,.0f}"
        lines.append(f"- **Total Funding:** {label}")

    if data.get("funding_rounds"):
        lines.append(f"- **Funding Rounds:** {data['funding_rounds']}")

    stages = []
    if data.get("seed"):
        stages.append("Seed")
    if data.get("angel"):
        stages.append("Angel")
    if data.get("venture"):
        stages.append("Venture")
    if data.get("round_A"):
        stages.append("Series A")
    if data.get("round_B"):
        stages.append("Series B")
    if data.get("round_C"):
        stages.append("Series C")
    if stages:
        lines.append(f"- **Funding Types:** {', '.join(stages)}")

    if data.get("employee_count"):
        lines.append(f"- **Employees:** ~{int(data['employee_count'])}")
    if data.get("angellist_signal"):
        lines.append(f"- **AngelList Signal:** {data['angellist_signal']}/5.0")

    return "\n".join(lines) if lines else "No specific details provided."
