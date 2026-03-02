from pydantic import BaseModel, HttpUrl
from typing import Optional, List
from datetime import datetime
from app.models.models import NoteCategory, HabitFrequency


# ─── Reel Parsing ────────────────────────────────────────────────────────────

class ReelParseRequest(BaseModel):
    url: str                          # Instagram reel URL from iOS share extension
    caption_override: Optional[str] = None  # If user pastes caption manually

class ParsedReelData(BaseModel):
    reel_id: Optional[str]
    author: Optional[str]
    caption: Optional[str]
    thumbnail_url: Optional[str]

class ParsedNotePreview(BaseModel):
    title: str
    body: str
    tags: List[str]
    category: NoteCategory
    key_takeaways: List[str]

class ReelParseResponse(BaseModel):
    reel: ParsedReelData
    note_preview: ParsedNotePreview   # User confirms before saving


# ─── Notes ───────────────────────────────────────────────────────────────────

class NoteCreate(BaseModel):
    title: str
    body: str
    category: NoteCategory = NoteCategory.general
    tags: Optional[List[str]] = []
    key_takeaways: Optional[List[str]] = []
    source_url: Optional[str] = None
    source_author: Optional[str] = None
    thumbnail_url: Optional[str] = None
    reel_caption: Optional[str] = None

class NoteUpdate(BaseModel):
    title: Optional[str] = None
    body: Optional[str] = None
    category: Optional[NoteCategory] = None
    tags: Optional[List[str]] = None
    key_takeaways: Optional[List[str]] = None
    is_pinned: Optional[bool] = None
    is_archived: Optional[bool] = None

class NoteResponse(BaseModel):
    id: str
    title: str
    body: str
    category: NoteCategory
    tags: List[str]
    key_takeaways: List[str]
    source_url: Optional[str]
    source_author: Optional[str]
    thumbnail_url: Optional[str]
    is_pinned: bool
    is_archived: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ─── Habits ──────────────────────────────────────────────────────────────────

class HabitCreate(BaseModel):
    name: str
    description: Optional[str] = None
    frequency: HabitFrequency = HabitFrequency.daily
    note_id: Optional[str] = None   # Link to source note/reel

class HabitUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    frequency: Optional[HabitFrequency] = None
    is_active: Optional[bool] = None

class HabitCheckIn(BaseModel):
    checked_in_at: Optional[datetime] = None  # Defaults to now

class HabitResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    frequency: HabitFrequency
    streak_count: int
    last_checked_in: Optional[datetime]
    is_active: bool
    note_id: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# ─── Auth ─────────────────────────────────────────────────────────────────────

class UserRegister(BaseModel):
    email: str
    password: str
    display_name: Optional[str] = None

class UserLogin(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
