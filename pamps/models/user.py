from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from pydantic import BaseModel
from sqlmodel import Field, Relationship, SQLModel

from pamps.security import HashedPassword

if TYPE_CHECKING:
    from post import Post


class User(SQLModel, table=True):
    """Represents the User Model"""

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, nullable=False)
    username: str = Field(unique=True, nullable=False)
    avatar: Optional[str] = None
    bio: Optional[str] = None
    password: HashedPassword = Field(nullable=False)

    # it populates the .user attributes with the Post Model
    posts: List["Post"] = Relationship(back_populates="user")


class UserResponse(BaseModel):
    """Serializer for User response"""

    username: str
    avatar: Optional[str] = None
    bio: Optional[str] = None


class UserRequest(BaseModel):
    """Serializer for User request payload"""

    email: str
    username: str
    password: str
    avatar: Optional[str] = None
    bio: Optional[str] = None


class Social(SQLModel, table=True):
    """Represents the Social Model"""

    id: Optional[int] = Field(default=None, primary_key=True)
    date: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    from_id: Optional[int] = Field(foreign_key="user.id")
    to_id: Optional[int] = Field(foreign_key="user.id")
