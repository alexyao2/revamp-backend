import json
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.database import get_db
from app.middleware.auth import get_current_user
from app.models.models import User, Note, NoteCategory
from app.models.schemas import NoteCreate, NoteUpdate, NoteResponse

router = APIRouter()


def note_to_response(note: Note) -> NoteResponse:
    """Convert DB model to response schema."""
    tags = json.loads(note.tags) if note.tags else []
    takeaways = json.loads(note.key_takeaways) if note.key_takeaways else []
    return NoteResponse(
        id=note.id,
        title=note.title,
        body=note.body,
        category=note.category,
        tags=tags,
        key_takeaways=takeaways,
        source_url=note.source_url,
        source_author=note.source_author,
        thumbnail_url=note.thumbnail_url,
        is_pinned=note.is_pinned,
        is_archived=note.is_archived,
        created_at=note.created_at,
        updated_at=note.updated_at,
    )


@router.post("", response_model=NoteResponse, status_code=201)
def create_note(
    payload: NoteCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Save a note (typically after confirming the reel parse preview)."""
    import uuid
    note = Note(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        title=payload.title,
        body=payload.body,
        category=payload.category,
        tags=json.dumps(payload.tags or []),
        key_takeaways=json.dumps(payload.key_takeaways or []),
        source_url=payload.source_url,
        source_author=payload.source_author,
        thumbnail_url=payload.thumbnail_url,
        reel_caption=payload.reel_caption,
    )
    db.add(note)
    db.commit()
    db.refresh(note)
    return note_to_response(note)


@router.get("", response_model=List[NoteResponse])
def list_notes(
    category: Optional[NoteCategory] = None,
    tag: Optional[str] = None,
    search: Optional[str] = None,
    pinned_only: bool = False,
    archived: bool = False,
    limit: int = Query(default=50, le=100),
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all notes for the current user with optional filters."""
    query = db.query(Note).filter(
        Note.user_id == current_user.id,
        Note.is_archived == archived
    )

    if category:
        query = query.filter(Note.category == category)
    if pinned_only:
        query = query.filter(Note.is_pinned == True)
    if search:
        query = query.filter(
            Note.title.ilike(f"%{search}%") | Note.body.ilike(f"%{search}%")
        )
    if tag:
        # Simple tag search in JSON string
        query = query.filter(Note.tags.ilike(f"%{tag}%"))

    notes = query.order_by(Note.is_pinned.desc(), Note.created_at.desc()) \
                 .limit(limit).offset(offset).all()

    return [note_to_response(n) for n in notes]


@router.get("/{note_id}", response_model=NoteResponse)
def get_note(
    note_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    note = db.query(Note).filter(Note.id == note_id, Note.user_id == current_user.id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return note_to_response(note)


@router.patch("/{note_id}", response_model=NoteResponse)
def update_note(
    note_id: str,
    payload: NoteUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    note = db.query(Note).filter(Note.id == note_id, Note.user_id == current_user.id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    updates = payload.model_dump(exclude_unset=True)
    for field, value in updates.items():
        if field == "tags":
            setattr(note, field, json.dumps(value))
        elif field == "key_takeaways":
            setattr(note, "key_takeaways", json.dumps(value))
        else:
            setattr(note, field, value)

    db.commit()
    db.refresh(note)
    return note_to_response(note)


@router.delete("/{note_id}", status_code=204)
def delete_note(
    note_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    note = db.query(Note).filter(Note.id == note_id, Note.user_id == current_user.id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    db.delete(note)
    db.commit()