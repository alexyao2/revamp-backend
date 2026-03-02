from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.middleware.auth import get_current_user
from app.models.models import User
from app.models.schemas import ReelParseRequest, ReelParseResponse, ParsedReelData, ParsedNotePreview
from app.services.instagram import fetch_reel_metadata
from app.services.ai_parser import parse_caption_to_note

router = APIRouter()


@router.post("/parse", response_model=ReelParseResponse)
async def parse_reel(
    payload: ReelParseRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Core endpoint — called by iOS Share Extension when user shares a reel.
    
    Flow:
    1. Fetch reel metadata from Instagram oEmbed
    2. Use caption (or caption_override) to generate structured note via AI
    3. Return preview — user confirms before saving via POST /api/notes
    """

    # Step 1: Fetch metadata from Instagram
    try:
        reel_data = await fetch_reel_metadata(payload.url)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    # Step 2: Determine what text to parse
    caption = payload.caption_override or reel_data.get("caption")
    if not caption:
        raise HTTPException(
            status_code=422,
            detail="Could not retrieve reel caption. Try pasting the caption manually using caption_override."
        )

    # Step 3: AI parses caption into structured note
    try:
        parsed = await parse_caption_to_note(
            caption=caption,
            source_url=payload.url,
            author=reel_data.get("author")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI parsing failed: {str(e)}")

    return ReelParseResponse(
        reel=ParsedReelData(
            reel_id=reel_data.get("reel_id"),
            author=reel_data.get("author"),
            caption=caption,
            thumbnail_url=reel_data.get("thumbnail_url"),
        ),
        note_preview=ParsedNotePreview(
            title=parsed.get("title", "Saved Reel"),
            body=parsed.get("body", caption),
            tags=parsed.get("tags", []),
            category=parsed.get("category", "general"),
            key_takeaways=parsed.get("key_takeaways", []),
        )
    )
