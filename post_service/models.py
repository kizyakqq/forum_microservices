from typing import Dict, Optional
from pydantic import BaseModel
from datetime import datetime


class Post(BaseModel):
    post_id: int
    user_id: int
    title: str
    content: str
    created_at: str
    updated_at: Optional[str] = None


class PostCreate(BaseModel):
    user_id: int
    title: str
    content: str


class PostUpdate(BaseModel):
    user_id: Optional[int] = None
    title: Optional[str] = None
    content: Optional[str] = None


db = {
    "posts": {
        1: Post(
            post_id=1,
            user_id=1,
            title="Пост",
            content="Содержание",
            created_at="2025-06-07"
        )
    },
    "next_post_id": 2
}
