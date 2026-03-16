"""
nova/market.py — Market intelligence + document analysis via Amazon Nova Pro
─────────────────────────────────────────────────────────────────────────────
Two entry points:
  market_intelligence(market, context) — full market research report
  analyze_document(text)               — pitch deck / business plan analysis
"""

import os

try:
    from .client import converse, converse_vision, NOVA_LITE
except ImportError:
    # Support direct execution: python market.py
    from client import converse, converse_vision, NOVA_LITE


MARKET_MODEL = os.getenv("NOVA_MARKET_MODEL", NOVA_LITE)
DOCUMENT_MODEL = os.getenv("NOVA_DOCUMENT_MODEL", NOVA_LITE)
VISION_MODEL = os.getenv("NOVA_VISION_MODEL", NOVA_LITE)
MARKET_MAX_TOKENS = int(os.getenv("NOVA_MARKET_MAX_TOKENS", "1200"))
DOCUMENT_MAX_TOKENS = int(os.getenv("NOVA_DOCUMENT_MAX_TOKENS", "1200"))
VISION_MAX_TOKENS = int(os.getenv("NOVA_VISION_MAX_TOKENS", "900"))

# ── System prompts ────────────────────────────────────────────
_MARKET_SYSTEM = """\
You are a senior venture capital market analyst with deep expertise across \
all major startup verticals: SaaS, fintech, healthtech, edtech, e-commerce, \
climate tech, Web3, AI/ML, deep tech, consumer, and more.

Your market intelligence reports are used by investors to make multi-million \
dollar allocation decisions. Be rigorous, cite specific trends and data, \
name real companies and funds where appropriate, and give actionable insight.

FORMATTING RULES:
- Use ## for section headers
- Use - for bullet points
- Use **text** for key terms, company names, and numbers
- Be specific: use growth percentages, market sizes, named examples
"""

_DOCUMENT_SYSTEM = """\
You are a senior investment analyst reviewing startup pitch decks and \
business plans for a top-tier venture capital firm. You have evaluated \
thousands of decks across all stages (pre-seed through Series C).

Your analysis must be thorough, direct, and actionable. Investment committees \
value honesty over polite optimism — if the business plan has holes, name them. \
If it is strong, explain specifically why.

FORMATTING RULES:
- Use ## for section headers
- Use - for bullet points
- Use **text** for emphasis on critical findings
- Be direct: state conclusions clearly, do not hedge everything
"""


def market_intelligence(market: str, context: str | None = None) -> str:
    """
    Generate a comprehensive market intelligence report.

    Parameters
    ----------
    market  : Industry or market name (e.g. "fintech", "healthtech", "SaaS").
    context : Optional extra question or focus area from the user.

    Returns
    -------
    str — Markdown-formatted market report from Nova Pro.
    """
    prompt = f"""\
Generate a comprehensive market intelligence report for the **{market}** \
industry/market as of 2025–2026.

## Market Overview
Current market size (USD), CAGR, and growth trajectory over the next 5 years.

## Key Growth Drivers
Top 3–5 forces driving expansion in this space.

## Competitive Landscape
Major incumbents, rising challengers, market structure (fragmented vs \
consolidated), and key differentiators between leaders.

## Startup Opportunities
Where are the white spaces and underserved problems? What types of startups \
are most likely to break through?

## Investment Signals
VC activity: recent notable funding rounds, hot sub-sectors, valuation \
multiples, and investor sentiment.

## Key Risks
Regulatory, technology, market timing, and competitive execution risks.

## 3-Year Outlook
What will the **{market}** market look like in 2027–2028?
"""

    if context and context.strip():
        prompt += f"\n\n## Specific Question from User\n{context.strip()}"

    return converse(
        messages=[{"role": "user", "content": [{"text": prompt}]}],
        system_prompt=_MARKET_SYSTEM,
        model_id=MARKET_MODEL,
        max_tokens=MARKET_MAX_TOKENS,
        temperature=0.5,
    )


def analyze_document(document_text: str) -> str:
    """
    Analyze a pitch deck or business plan and return an investment verdict.

    Parameters
    ----------
    document_text : The raw pasted text from the pitch deck or plan.
                    Capped at 8 000 chars to control token usage.

    Returns
    -------
    str — Markdown-formatted investment analysis from Nova Pro.
    """
    # Cap input length to avoid hitting context limits
    excerpt = document_text[:8_000]
    truncated = len(document_text) > 8_000
    trunc_note = "\n\n*(Document truncated to first 8,000 characters for analysis.)*" if truncated else ""

    prompt = f"""\
Please analyze the following startup pitch deck / business plan and provide \
a structured investment analysis.

---
{excerpt}
---
{trunc_note}

## One-Line Verdict
Your investment recommendation in a single, direct sentence.

## Business Model Assessment
Is the business model sound, scalable, and defensible?

## Market Opportunity
Is the target market large enough and growing fast enough to support a \
venture-scale outcome?

## Competitive Advantage
What moats, differentiation, or defensible IP exist?

## Team Signals
What does the document reveal about the founding team's capability and \
commitment?

## Financial Analysis
Revenue model clarity, unit economics signals, and burn/runway indicators.

## Red Flags
Critical gaps, unrealistic assumptions, or missing information.

## Investment Recommendation
**Invest / Pass / Conditional** — and the specific reasoning.

## What Would Change My Mind
What milestones, data, or pivots would flip the verdict?
"""

    return converse(
        messages=[{"role": "user", "content": [{"text": prompt}]}],
        system_prompt=_DOCUMENT_SYSTEM,
        model_id=DOCUMENT_MODEL,
        max_tokens=DOCUMENT_MAX_TOKENS,
        temperature=0.5,
    )


def analyze_document_image(
    image_b64: str,
    image_media_type: str = "image/jpeg",
    extra_context: str | None = None,
) -> str:
    """
    Analyze a pitch deck slide or screenshot using Amazon Nova Lite's vision.

    Multimodal entry point — satisfies the "Multimodal Understanding" category.
    Accepts a single image (JPEG/PNG/WebP) and optionally additional text context.

    Parameters
    ----------
    image_b64        : Base-64 encoded image bytes.
    image_media_type : MIME type string, e.g. "image/jpeg" or "image/png".
    extra_context    : Optional extra text question or description from the user.

    Returns
    -------
    str — Markdown-formatted analysis from Amazon Nova Lite (vision).
    """
    text_prompt = """\
You are a senior VC analyst reviewing a startup pitch deck slide or image.
Analyse everything visible in this image:
- Any text, charts, diagrams, screenshots, or tables
- Product UI screenshots if present
- Financial projections or market size claims
- Team bios, logos, or branding

Produce a structured analysis:

## What This Slide Shows
Describe the key content and purpose of this image.

## Key Claims or Metrics
Extract any numbers, metrics, or claims made (verbatim where possible).

## Strengths in This Slide
What does this communicate well to an investor?

## Concerns or Gaps
What is unclear, missing, or raises questions?

## VC Reaction
How would a partner-level VC react to this slide in a pitch meeting?
"""

    if extra_context and extra_context.strip():
        text_prompt += f"\n\n## Additional Context from Founder\n{extra_context.strip()}"

    return converse_vision(
        text=text_prompt,
        image_b64=image_b64,
        image_media_type=image_media_type,
        system_prompt=_DOCUMENT_SYSTEM,
        model_id=VISION_MODEL,
        max_tokens=VISION_MAX_TOKENS,
        temperature=0.5,
    )
