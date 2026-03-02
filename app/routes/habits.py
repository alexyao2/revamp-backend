import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from app.db.database import get_db
from app.middleware.auth import get_current_user
from app.models.models import User, Habit
from app.models.schemas import HabitCreate, HabitUpdate, HabitCheckIn, HabitResponse

router = APIRouter()


@router.post("", response_model=HabitResponse, status_code=201)
def create_habit(
    payload: HabitCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    habit = Habit(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        name=payload.name,
        description=payload.description,
        frequency=payload.frequency,
        note_id=payload.note_id,
    )
    db.add(habit)
    db.commit()
    db.refresh(habit)
    return habit


@router.get("", response_model=List[HabitResponse])
def list_habits(
    active_only: bool = True,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Habit).filter(Habit.user_id == current_user.id)
    if active_only:
        query = query.filter(Habit.is_active == True)
    return query.order_by(Habit.created_at.desc()).all()


@router.post("/{habit_id}/checkin", response_model=HabitResponse)
def check_in_habit(
    habit_id: str,
    payload: HabitCheckIn = HabitCheckIn(),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark a habit as done. Increments streak."""
    habit = db.query(Habit).filter(Habit.id == habit_id, Habit.user_id == current_user.id).first()
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")

    habit.last_checked_in = payload.checked_in_at or datetime.utcnow()
    habit.streak_count += 1
    db.commit()
    db.refresh(habit)
    return habit


@router.patch("/{habit_id}", response_model=HabitResponse)
def update_habit(
    habit_id: str,
    payload: HabitUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    habit = db.query(Habit).filter(Habit.id == habit_id, Habit.user_id == current_user.id).first()
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(habit, field, value)

    db.commit()
    db.refresh(habit)
    return habit


@router.delete("/{habit_id}", status_code=204)
def delete_habit(
    habit_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    habit = db.query(Habit).filter(Habit.id == habit_id, Habit.user_id == current_user.id).first()
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")
    db.delete(habit)
    db.commit()