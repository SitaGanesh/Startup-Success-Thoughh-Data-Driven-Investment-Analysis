"""
nova/ — Amazon Nova AI integration package for StartupOracle
─────────────────────────────────────────────────────────────
Sub-modules:
  client.py   — boto3 Bedrock connection factory + converse / converse_vision
  analyzer.py — deep startup analysis (ML result + Nova explanation)
  chat.py     — conversational startup advisor (multi-turn)
  market.py   — market intelligence reports + document analysis + image vision
  agent.py    — 4-step agentic investment research chain (Agentic AI category)

Usage (from backend/main.py):
    from nova.analyzer import analyze_startup
    from nova.chat     import chat
    from nova.market   import market_intelligence, analyze_document, analyze_document_image
    from nova.agent    import run_investment_agent
"""

from .analyzer import analyze_startup
from .chat import chat
from .market import market_intelligence, analyze_document, analyze_document_image
from .agent import run_investment_agent

__all__ = [
    "analyze_startup",
    "chat",
    "market_intelligence",
    "analyze_document",
    "analyze_document_image",
    "run_investment_agent",
]
