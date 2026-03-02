import json
import httpx
from typing import Optional
from app.core.config import settings


SYSTEM_PROMPT = """
You are a smart note-taking assistant embedded in a personal growth app called Revamp.

Your job is to take an Instagram reel caption or description and convert it into a 
clean, structured, actionable note.

Return ONLY valid JSON (no markdown, no preamble) in this exact format:
{
  "title": "Short, clear title (max 8 words)",
  "body": "Well-formatted note body. Use bullet points (•) for tips/lists. Keep it concise but complete.",
  "tags": ["tag1", "tag2", "tag3"],
  "category": "tip | motivation | habit | recipe | general",
  "key_takeaways": ["One-line takeaway 1", "One-line takeaway 2"]
}

Category rules:
- "tip": How-to content, advice, life hacks, productivity
- "motivation": Quotes, mindset, inspirational content
- "habit": Routines, daily practices, wellness, fitness
- "recipe": Food, drinks, cooking instructions
- "general": Anything that doesn't fit the above

Keep tags lowercase, 1-2 words each, max 5 tags.
Key takeaways should be 2-4 short actionable sentences.
"""


async def parse_caption_to_note(
    caption: str,
    source_url: Optional[str] = None,
    author: Optional[str] = None
) -> dict:
    """
    Send caption to AI and get back structured note data.
    Supports OpenAI (primary) or Anthropic (fallback).
    """
    user_message = f"Instagram caption to convert into a note:\n\n{caption}"
    if author:
        user_message += f"\n\nPosted by: {author}"
    if source_url:
        user_message += f"\nSource: {source_url}"

    # Try OpenAI first
    if settings.OPENAI_API_KEY:
        return await _parse_with_openai(user_message)

    # Fallback to Anthropic
    if settings.ANTHROPIC_API_KEY:
        return await _parse_with_anthropic(user_message)

    # No AI key configured — return a basic note
    return _fallback_parse(caption)


async def _parse_with_openai(user_message: str) -> dict:
    headers = {
        "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "gpt-4o-mini",   # Fast + cheap, great for this use case
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message}
        ],
        "temperature": 0.3,
        "max_tokens": 800
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=payload
        )
        response.raise_for_status()
        raw = response.json()["choices"][0]["message"]["content"]
        return json.loads(raw)


async def _parse_with_anthropic(user_message: str) -> dict:
    headers = {
        "x-api-key": settings.ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "claude-haiku-4-5-20251001",
        "max_tokens": 800,
        "system": SYSTEM_PROMPT,
        "messages": [
            {"role": "user", "content": user_message}
        ]
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            "https://api.anthropic.com/v1/messages",
            headers=headers,
            json=payload
        )
        response.raise_for_status()
        raw = response.json()["content"][0]["text"]
        return json.loads(raw)


def _fallback_parse(caption: str) -> dict:
    """Basic fallback when no AI key is configured."""
    lines = [l.strip() for l in caption.split("\n") if l.strip()]
    title = lines[0][:60] if lines else "Saved Reel"
    return {
        "title": title,
        "body": caption,
        "tags": [],
        "category": "general",
        "key_takeaways": []
    }
