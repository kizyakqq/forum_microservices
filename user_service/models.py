from typing import Dict, Optional
from pydantic import BaseModel


class User(BaseModel):
    user_id: int
    username: str
    email: str
    password_hash: str


class UserCreate(BaseModel):
    username: str
    email: str
    password: str


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None


db = {
    "users": {
        1: User(user_id=1, username="admin", email="admin@example.com", password_hash="hashed_password"),
    },
    "next_user_id": 2
}
