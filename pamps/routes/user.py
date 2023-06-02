from typing import List

from fastapi import APIRouter, HTTPException
from sqlmodel import Session, select

from pamps.auth import AuthenticatedUser
from pamps.db import ActiveSession
from pamps.models.user import Social, User, UserRequest, UserResponse

router = APIRouter()


@router.get("/", response_model=List[UserResponse])
async def list_users(*, session: Session = ActiveSession):
    """List all users"""
    users = session.exec(select(User)).all()
    return users


@router.get("/{username}/", response_model=UserResponse)
async def get_user_by_username(
        *, session: Session = ActiveSession, username: str
):
    """Get user by username"""
    query = select(User).where(User.username == username)
    user = session.exec(query).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/", response_model=None, status_code=201)
async def create_user(*, session: Session = ActiveSession, user: UserRequest):
    """Creates new user"""
    db_user = User.from_orm(user)  # transform UserRequest in User
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


@router.post(
    "/follow/{user_id}/",
    status_code=204,
)
async def follow_user(
        *,
        session: Session = ActiveSession,
        user: User = AuthenticatedUser,
        user_id: int,
) -> None:
    """Follows new user"""
    if user_id <= 0 or user_id == user.id:
        raise HTTPException(status_code=400, detail="Invalid user_id")

    existing_user = session.get(User, user_id)
    if not existing_user:
        raise HTTPException(status_code=404, detail="User not found")

    existing_relationship = (
        session.query(Social)
        .filter(Social.from_id == user.id, Social.to_id == user_id)
        .first()
    )
    if existing_relationship:
        return

    new_relationship = Social(from_id=user.id, to_id=user_id)
    session.add(new_relationship)
    session.commit()
    return


@router.delete(
    "/follow/{user_id}/",
    status_code=204,
)
async def unfollow_user(
        *,
        session: Session = ActiveSession,
        user: User = AuthenticatedUser,
        user_id: int,
) -> None:
    """Unfollows user"""
    if user_id <= 0 or user_id == user.id:
        raise HTTPException(status_code=400, detail="Invalid user_id")

    existing_user = session.get(User, user_id)
    if not existing_user:
        raise HTTPException(status_code=404, detail="User not found")

    existing_relationship = (
        session.query(Social)
        .filter(Social.from_id == user.id, Social.to_id == user_id)
        .first()
    )
    if not existing_relationship:
        return None

    session.delete(existing_relationship)
    session.commit()
    return None
