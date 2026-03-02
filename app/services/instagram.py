import httpx
import re
from typing import Optional
from app.core.config import settings


def extract_reel_id(url: str) -> Optional[str]:
    """Extract the reel shortcode from an Instagram URL."""
    # Matches /reel/ABC123/ or /p/ABC123/
    match = re.search(r"/(?:reel|p)/([A-Za-z0-9_-]+)", url)
    return match.group(1) if match else None


async def fetch_reel_metadata(url: str) -> dict:
    """
    Fetch reel metadata via Instagram oEmbed API.
    Requires a Meta Developer app with instagram_oembed permission.
    Falls back to basic URL parsing if token not configured.

    Docs: https://developers.facebook.com/docs/instagram/oembed
    """
    reel_id = extract_reel_id(url)

    if not settings.INSTAGRAM_ACCESS_TOKEN:
        # No token — return minimal data, let AI work from URL + any caption override
        return {
            "reel_id": reel_id,
            "author": None,
            "caption": None,
            "thumbnail_url": None,
            "raw_url": url,
        }

    oembed_url = (
        f"https://graph.facebook.com/v18.0/instagram_oembed"
        f"?url={url}"
        f"&access_token={settings.INSTAGRAM_ACCESS_TOKEN}"
        f"&fields=author_name,thumbnail_url,title"
    )

    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get(oembed_url)
            response.raise_for_status()
            data = response.json()
            return {
                "reel_id": reel_id,
                "author": data.get("author_name"),
                "caption": data.get("title"),       # oEmbed returns caption as title
                "thumbnail_url": data.get("thumbnail_url"),
                "raw_url": url,
            }
        except httpx.HTTPStatusError as e:
            # Token invalid, rate limited, or private reel
            raise ValueError(f"Instagram API error: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            raise ValueError(f"Failed to fetch reel metadata: {str(e)}")
