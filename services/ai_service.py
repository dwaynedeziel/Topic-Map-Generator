import json
import re
import time
from typing import List, Optional

import anthropic

from config.settings import (
    ANTHROPIC_API_KEY,
    CLAUDE_MAX_TOKENS,
    CLAUDE_MODEL,
    CLAUDE_TEMPERATURE,
    SCOPE_FOCUSED,
)
from models.topic_map import validate_topic_map
from prompts.topic_map_prompts import (
    CONTINUATION_PROMPT,
    JSON_FIX_PROMPT,
    TOPIC_MAP_SYSTEM_PROMPT,
    TOPIC_MAP_USER_PROMPT,
)


def _clean_json_response(text: str) -> str:
    """Strip markdown fences and clean common JSON issues from Claude output."""
    text = text.strip()
    # Remove markdown code fences
    text = re.sub(r"^```(?:json)?\s*\n?", "", text)
    text = re.sub(r"\n?```\s*$", "", text)
    text = text.strip()
    # Remove trailing commas before ] or }
    text = re.sub(r",\s*([\]}])", r"\1", text)
    return text


def _parse_json(text: str) -> Optional[List[dict]]:
    """Attempt to parse JSON from text, returning None on failure."""
    cleaned = _clean_json_response(text)
    try:
        data = json.loads(cleaned)
        if isinstance(data, list):
            return data
        return None
    except json.JSONDecodeError:
        return None


def _call_claude(
    system: str,
    user_message: str,
    max_tokens: int = CLAUDE_MAX_TOKENS,
) -> str:
    """Make a single Claude API call with retry on rate limit."""
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    for attempt in range(3):
        try:
            response = client.messages.create(
                model=CLAUDE_MODEL,
                max_tokens=max_tokens,
                temperature=CLAUDE_TEMPERATURE,
                system=system,
                messages=[{"role": "user", "content": user_message}],
            )
            return response.content[0].text
        except anthropic.RateLimitError:
            if attempt < 2:
                wait_time = 2 ** (attempt + 1)
                time.sleep(wait_time)
            else:
                raise
    return ""


def generate_topic_map(
    topic: str,
    scope: str,
    industry: str,
    audience: str,
    geo_focus: str,
    competitors: str,
    existing_content: str,
    compiled_research: str,
) -> List[dict]:
    """Generate a topic map using Claude AI based on research data.

    Returns a list of validated topic map entry dicts.
    Raises ValueError if generation or validation fails.
    """
    if not ANTHROPIC_API_KEY:
        raise ValueError("ANTHROPIC_API_KEY is not configured.")

    topic_count_guidance = "15-25" if scope == SCOPE_FOCUSED else "40-75"

    user_prompt = TOPIC_MAP_USER_PROMPT.format(
        topic=topic,
        scope=scope,
        industry=industry or "Not specified",
        audience=audience or "Not specified",
        geo_focus=geo_focus or "Not specified",
        competitors=competitors or "None provided",
        existing_content=existing_content or "None provided",
        compiled_research=compiled_research,
        topic_count_guidance=topic_count_guidance,
    )

    # First attempt
    raw_response = _call_claude(TOPIC_MAP_SYSTEM_PROMPT, user_prompt)
    entries = _parse_json(raw_response)

    # If JSON parsing failed, retry with fix prompt
    if entries is None:
        try:
            cleaned = _clean_json_response(raw_response)
            json.loads(cleaned)
        except json.JSONDecodeError as e:
            fix_prompt = JSON_FIX_PROMPT.format(
                error=str(e),
                output=raw_response[:8000],
            )
            fix_response = _call_claude(TOPIC_MAP_SYSTEM_PROMPT, fix_prompt)
            entries = _parse_json(fix_response)

    if entries is None:
        raise ValueError(
            "Failed to parse Claude's response as valid JSON after retry. "
            "Please try generating again."
        )

    # Check if the response was truncated (incomplete JSON)
    # If the last entry seems incomplete, try continuation
    if raw_response.rstrip()[-1] != "]":
        last_chunk = raw_response[-500:]
        continuation_prompt = CONTINUATION_PROMPT.format(last_chunk=last_chunk)
        continuation = _call_claude(TOPIC_MAP_SYSTEM_PROMPT, continuation_prompt)
        continuation_entries = _parse_json(continuation)

        if continuation_entries:
            # Merge: raw_response had incomplete JSON, try to salvage
            # Parse what we can from the original, then add continuation
            try:
                # Try to fix truncated JSON by closing the array
                truncated = _clean_json_response(raw_response)
                # Find the last complete object
                last_brace = truncated.rfind("}")
                if last_brace > 0:
                    fixed = truncated[: last_brace + 1] + "]"
                    base_entries = json.loads(fixed)
                    if isinstance(base_entries, list):
                        entries = base_entries + continuation_entries
            except json.JSONDecodeError:
                # If we can't salvage, just use continuation if it's enough
                if len(continuation_entries) > 10:
                    entries = continuation_entries

    if not entries:
        raise ValueError("No topic map entries were generated.")

    # Validate the topic map
    errors = validate_topic_map(entries)
    if errors:
        # Log warnings but don't fail — partial results are still useful
        # Only fail on critical issues
        critical_errors = [e for e in errors if "Missing required field" in e or "Expected exactly 1 Pillar" in e]
        if critical_errors:
            raise ValueError(
                f"Topic map validation failed:\n" + "\n".join(critical_errors[:10])
            )

    return entries
