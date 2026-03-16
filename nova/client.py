"""
nova/client.py — Amazon Bedrock Nova connection (OpenAI-compatible API)
────────────────────────────────────────────────────────────────────────
Uses Amazon Bedrock bearer-token authentication with the OpenAI SDK.

Required environment variables (in .env at project root):
    AWS_BEARER_TOKEN_BEDROCK = bedrock-api-key-...
    AWS_BEDROCK_REGION       = ap-south-1 (or your Bedrock region)

Endpoint format:
    https://bedrock-mantle.<region>.api.aws/v1

Exports:
    converse()        — text conversation
    converse_vision() — multimodal image + text (Nova Lite / Nova 2 Lite)
    NOVA_MICRO, NOVA_LITE, NOVA_PRO
    NOVA_2_LITE, NOVA_2_PRO  (Amazon Nova 2 series)
"""

import os
from typing import Any

_AVAILABLE_MODELS_CACHE: set[str] | None = None

# ── Nova v1 model IDs on Bedrock ─────────────────────────────
NOVA_MICRO = "amazon.nova-micro-v1:0"   # text only, fastest + cheapest
NOVA_LITE = "amazon.nova-lite-v1:0"    # text + images, fast
NOVA_PRO = "amazon.nova-pro-v1:0"     # most capable

# ── Nova 2 model IDs (upgraded series) ───────────────────────
NOVA_2_LITE = "amazon.nova-lite-v2:0"   # Nova 2 Lite: multimodal, fast
NOVA_2_PRO = "amazon.nova-pro-v2:0"    # Nova 2 Pro: highest capability

# Default models used across the app
DEFAULT_FAST_MODEL = NOVA_LITE   # for chat & quick calls
DEFAULT_CAPABLE_MODEL = NOVA_PRO    # for deep analysis


def _clean_env_value(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = value.strip().strip('"').strip("'")
    return cleaned or None


def _first_env(*names: str) -> str | None:
    for name in names:
        value = _clean_env_value(os.getenv(name))
        if value:
            return value
    return None


def _available_model_ids(client: Any) -> set[str]:
    global _AVAILABLE_MODELS_CACHE
    if _AVAILABLE_MODELS_CACHE is not None:
        return _AVAILABLE_MODELS_CACHE

    skip_discovery = (_first_env("BEDROCK_SKIP_MODEL_DISCOVERY", "NOVA_SKIP_MODEL_DISCOVERY") or "1").lower()
    if skip_discovery in {"1", "true", "yes", "on"}:
        _AVAILABLE_MODELS_CACHE = set()
        return _AVAILABLE_MODELS_CACHE

    try:
        models = client.models.list()
        _AVAILABLE_MODELS_CACHE = {m.id for m in models.data}
    except Exception:
        _AVAILABLE_MODELS_CACHE = set()

    return _AVAILABLE_MODELS_CACHE


def _resolve_text_model(client: Any, preferred: str) -> str:
    ids = _available_model_ids(client)
    if not ids or preferred in ids:
        return preferred

    override = _first_env("BEDROCK_MODEL_OVERRIDE", "BEDROCK_TEXT_MODEL")
    if override and override in ids:
        return override

    candidates = [
        NOVA_2_PRO,
        NOVA_PRO,
        NOVA_2_LITE,
        NOVA_LITE,
        "qwen.qwen3-32b",
        "qwen.qwen3-235b-a22b-2507",
        "mistral.ministral-3-14b-instruct",
        "mistral.mistral-large-3-675b-instruct",
        "openai.gpt-oss-120b",
        "openai.gpt-oss-20b",
    ]
    for model in candidates:
        if model in ids:
            return model

    return preferred


def _resolve_vision_model(client: Any, preferred: str) -> str:
    ids = _available_model_ids(client)
    if not ids or preferred in ids:
        return preferred

    override = _first_env("BEDROCK_VISION_MODEL", "BEDROCK_MODEL_OVERRIDE")
    if override and override in ids:
        return override

    candidates = [
        NOVA_2_LITE,
        NOVA_LITE,
        "writer.palmyra-vision-7b",
        "qwen.qwen3-vl-235b-a22b-instruct",
    ]
    for model in candidates:
        if model in ids:
            return model

    return preferred


def _text_retry_candidates(current: str) -> list[str]:
    """Return ordered fallback model candidates for text calls."""
    candidates = [
        _first_env("BEDROCK_MODEL_OVERRIDE", "BEDROCK_TEXT_MODEL"),
        NOVA_2_PRO,
        NOVA_PRO,
        NOVA_2_LITE,
        NOVA_LITE,
        "qwen.qwen3-32b",
        "qwen.qwen3-235b-a22b-2507",
        "mistral.ministral-3-14b-instruct",
        "mistral.mistral-large-3-675b-instruct",
        "openai.gpt-oss-120b",
        "openai.gpt-oss-20b",
    ]
    ordered: list[str] = []
    seen: set[str] = set()
    for c in candidates:
        if not c or c == current or c in seen:
            continue
        seen.add(c)
        ordered.append(c)
    return ordered


def _vision_retry_candidates(current: str) -> list[str]:
    """Return ordered fallback model candidates for vision calls."""
    candidates = [
        _first_env("BEDROCK_VISION_MODEL", "BEDROCK_MODEL_OVERRIDE"),
        NOVA_2_LITE,
        NOVA_LITE,
        "writer.palmyra-vision-7b",
        "qwen.qwen3-vl-235b-a22b-instruct",
    ]
    ordered: list[str] = []
    seen: set[str] = set()
    for c in candidates:
        if not c or c == current or c in seen:
            continue
        seen.add(c)
        ordered.append(c)
    return ordered


def _get_client() -> Any:
    """
    Return an OpenAI client pointed at Bedrock's OpenAI-compatible endpoint.
    """
    try:
        from openai import OpenAI
    except ModuleNotFoundError as e:
        raise RuntimeError(
            "Missing dependency 'openai'. Install it in your active environment: pip install openai"
        ) from e

    api_key = _first_env(
        "AWS_BEARER_TOKEN_BEDROCK",
        "AWS_BEARER_TOKEN",
        "BEDROCK_API_KEY",
        "AWS_BEDROCK_API_KEY",
    )
    region = _first_env("AWS_BEDROCK_REGION", "AWS_REGION") or "ap-south-1"

    if not api_key:
        raise RuntimeError(
            "No Bedrock bearer token found. Set one of: "
            "AWS_BEARER_TOKEN_BEDROCK, AWS_BEARER_TOKEN, BEDROCK_API_KEY, AWS_BEDROCK_API_KEY. "
            "Add it to your .env file at the project root."
        )

    base_url = f"https://bedrock-mantle.{region}.api.aws/v1"

    timeout_raw = _first_env("BEDROCK_TIMEOUT_SECONDS", "NOVA_TIMEOUT_SECONDS") or "30"
    retries_raw = _first_env("BEDROCK_MAX_RETRIES", "NOVA_MAX_RETRIES") or "0"

    try:
        timeout_seconds = float(timeout_raw)
    except ValueError:
        timeout_seconds = 45.0

    try:
        max_retries = int(retries_raw)
    except ValueError:
        max_retries = 1

    return OpenAI(
        api_key=api_key,
        base_url=base_url,
        timeout=timeout_seconds,
        max_retries=max_retries,
    )


def converse(
    messages: list,
    system_prompt: str | None = None,
    model_id: str = NOVA_LITE,
    max_tokens: int = 2048,
    temperature: float = 0.7,
) -> str:
    """
    Send messages to Amazon Nova via the OpenAI-compatible Bedrock endpoint.

    Parameters
    ----------
    messages      : List of {"role": "user"|"assistant",
                             "content": [{"text": "..."}]}   ← boto3 format
                    OR      {"role": ..., "content": "..."}  ← plain string
    system_prompt : Optional system instruction string.
    model_id      : Bedrock model ID (default NOVA_LITE).
    max_tokens    : Maximum tokens in the response.
    temperature   : Sampling temperature (0 = deterministic, 1 = creative).

    Returns
    -------
    str  — The assistant's text response.

    Raises
    ------
    RuntimeError  — wraps API errors with a clear message.
    """
    client = _get_client()

    # Build OpenAI-format message list
    openai_msgs: list[dict] = []

    # System prompt is a separate role in OpenAI format
    if system_prompt:
        openai_msgs.append({"role": "system", "content": system_prompt})

    # Convert from boto3 Converse format (content as list) OR plain strings
    for msg in messages:
        role = msg.get("role", "user")
        content = msg.get("content", "")

        if isinstance(content, list):
            # boto3 format: [{"text": "..."}, ...]
            text = " ".join(
                part.get("text", "") for part in content
                if isinstance(part, dict)
            )
        else:
            text = str(content)

        openai_msgs.append({"role": role, "content": text})

    resolved_model = _resolve_text_model(client, model_id)

    def _call(model: str) -> str:
        completion = client.chat.completions.create(
            model=model,
            messages=openai_msgs,
            max_tokens=max_tokens,
            temperature=temperature,
        )
        return completion.choices[0].message.content or ""

    try:
        return _call(resolved_model)
    except Exception as e:
        msg = str(e).lower()
        if "not_found_error" not in msg and "does not exist" not in msg:
            raise RuntimeError(f"Amazon Nova Bedrock API error: {e}") from e

        last_err = e
        for candidate in _text_retry_candidates(resolved_model):
            try:
                return _call(candidate)
            except Exception as retry_err:
                last_err = retry_err

        raise RuntimeError(f"Amazon Nova Bedrock API error: {last_err}") from last_err


def converse_vision(
    text: str,
    image_b64: str,
    image_media_type: str = "image/jpeg",
    system_prompt: str | None = None,
    model_id: str = NOVA_LITE,
    max_tokens: int = 2048,
    temperature: float = 0.7,
) -> str:
    """
    Send an image + text prompt to Amazon Nova Lite (multimodal).

    Parameters
    ----------
    text             : The text question or instruction to accompany the image.
    image_b64        : Base-64 encoded image bytes (JPEG, PNG, GIF, or WebP).
    image_media_type : MIME type, e.g. "image/jpeg" or "image/png".
    system_prompt    : Optional system instruction.
    model_id         : Must be a vision-capable model (NOVA_LITE or NOVA_2_LITE).
    max_tokens       : Maximum response tokens.
    temperature      : Sampling temperature.

    Returns
    -------
    str  — The assistant's text response.

    Raises
    ------
    RuntimeError  — wraps API errors with a clear message.
    """
    client = _get_client()

    openai_msgs: list[dict] = []

    if system_prompt:
        openai_msgs.append({"role": "system", "content": system_prompt})

    # OpenAI vision format — supported by Bedrock's OpenAI-compatible endpoint
    openai_msgs.append({
        "role": "user",
        "content": [
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:{image_media_type};base64,{image_b64}"
                },
            },
            {"type": "text", "text": text},
        ],
    })

    resolved_model = _resolve_vision_model(client, model_id)

    def _call(model: str) -> str:
        completion = client.chat.completions.create(
            model=model,
            messages=openai_msgs,
            max_tokens=max_tokens,
            temperature=temperature,
        )
        return completion.choices[0].message.content or ""

    try:
        return _call(resolved_model)
    except Exception as e:
        msg = str(e).lower()
        if "not_found_error" not in msg and "does not exist" not in msg:
            raise RuntimeError(f"Amazon Nova vision API error: {e}") from e

        last_err = e
        for candidate in _vision_retry_candidates(resolved_model):
            try:
                return _call(candidate)
            except Exception as retry_err:
                last_err = retry_err

        raise RuntimeError(f"Amazon Nova vision API error: {last_err}") from last_err
