"""
nova/chat.py — Conversational startup advisor using Amazon Nova Lite
────────────────────────────────────────────────────────────────────
Multi-turn conversations about startups, fundraising, strategy, and
market dynamics. Keeps the last N messages for context continuity.
"""

try:
    from .client import converse, NOVA_LITE
except ImportError:
    # Support direct execution: python chat.py
    from client import converse, NOVA_LITE

_SYSTEM = """\
You are StartupOracle AI, a knowledgeable and direct startup advisor. \
You help founders, investors, and researchers understand startup ecosystems, \
fundraising strategies, market dynamics, and what makes companies succeed \
or fail.

Your personality:
- Conversational and approachable while staying professional
- Data-informed: you understand ML signals of startup success
- Honest and direct — you flag risks, not just opportunities
- Concise but complete — 2–4 paragraphs unless depth is asked for
- Use concrete examples, numbers, and named companies when helpful

If asked about a specific startup they're building, ask clarifying questions \
to give better advice. If asked something outside startups/business, politely \
redirect to your area of expertise.
"""

# Maximum messages sent to Nova (keeps context window manageable)
_MAX_HISTORY = 20


def chat(messages: list[dict]) -> str:
    """
    Send a conversation to Nova Lite and return the next response.

    Parameters
    ----------
    messages : List of {"role": "user"|"assistant", "content": "..."}
               The full conversation history up to this point.

    Returns
    -------
    str — The assistant's response text.
    """
    trimmed = messages[-_MAX_HISTORY:] if len(
        messages) > _MAX_HISTORY else messages

    bedrock_msgs = [
        {
            "role":    msg["role"],
            "content": [{"text": msg["content"]}],
        }
        for msg in trimmed
        if msg.get("role") in ("user", "assistant") and msg.get("content", "").strip()
    ]

    if not bedrock_msgs:
        return "Please send a message to get started."

    return converse(
        messages=bedrock_msgs,
        system_prompt=_SYSTEM,
        model_id=NOVA_LITE,
        max_tokens=1024,
        temperature=0.8,
    )
