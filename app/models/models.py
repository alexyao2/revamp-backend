import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Text, Boolean, Integer,
    DateTime, ForeignKey, Enum as SAEnum
)
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
from app.db.database import Base
import enum


class NoteCategory(str, enum.Enum):
    tip = "tip"
    motivation = "motivation"
    habit = "habit"
    recipe = "recipe"
    general = "general"


class HabitFrequency(str, enum.Enum):
    daily = "daily"
    weekly = "weekly"


def generate_uuid():
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=generate_uuid)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    display_name = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    notes = relationship("Note", back_populates="user", cascade="all, delete-orphan")
    habits = relationship("Habit", back_populates="user", cascade="all, delete-orphan")


class Note(Base):
    __tablename__ = "notes"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)

    # Content
    title = Column(String, nullable=False)
    body = Column(Text, nullable=False)
    category = Column(SAEnum(NoteCategory), default=NoteCategory.general, nullable=False)
    tags = Column(String, nullable=True)          # Comma-separated; swap for ARRAY on Postgres
    key_takeaways = Column(Text, nullable=True)   # JSON string list

    # Source metadata (from Instagram reel)
    source_url = Column(String, nullable=True)
    source_author = Column(String, nullable=True)   # @handle
    thumbnail_url = Column(String, nullable=True)
    reel_caption = Column(Text, nullable=True)      # Raw caption for reference

    # State
    is_pinned = Column(Boolean, default=False)
    is_archived = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="notes")
    habit = relationship("Habit", back_populates="source_note", uselist=False)


class Habit(Base):
    __tablename__ = "habits"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    note_id = Column(String, ForeignKey("notes.id"), nullable=True)  # Optional: habit sourced from a note

    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    frequency = Column(SAEnum(HabitFrequency), default=HabitFrequency.daily)
    streak_count = Column(Integer, default=0)
    last_checked_in = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="habits")
    source_note = relationship("Note", back_populates="habit")
