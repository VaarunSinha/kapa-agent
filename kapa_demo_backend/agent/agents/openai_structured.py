"""
Shared OpenAI client and structured-output helpers (JSON schema).
Uses OPENAI_API_KEY from Django settings/env; no-op if not set.
"""
import json
import logging
from typing import Any, Optional

from django.conf import settings

logger = logging.getLogger(__name__)


def get_openai_client():
    """Return OpenAI client if API key is set, else None."""
    import os
    api_key = getattr(settings, "OPENAI_API_KEY", None) or os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return None
    from openai import OpenAI
    return OpenAI(api_key=api_key)


def structured_completion(
    system_prompt: str,
    user_prompt: str,
    json_schema: dict,
    model: str = "gpt-4o",
) -> Optional[dict[str, Any]]:
    """
    Call Chat Completions with response_format json_schema; return parsed JSON or None.
    json_schema must be OpenAI-compatible: "required" must list every key in "properties".
    """
    client = get_openai_client()
    if not client:
        logger.debug("structured_completion: OPENAI_API_KEY not set, skipping")
        return None
    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "response",
                    "strict": True,
                    "schema": json_schema,
                },
            },
        )
        choice = resp.choices[0] if resp.choices else None
        if not choice or not getattr(choice, "message", None):
            return None
        content = choice.message.content
        if not content:
            return None
        return json.loads(content)
    except Exception as e:
        logger.warning("structured_completion failed: %s", e)
        return None
