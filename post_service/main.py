from typing import Dict
import uvicorn
from fastapi import FastAPI, HTTPException
from datetime import datetime
import httpx
from models import Post, PostCreate, PostUpdate, db

app = FastAPI(
    title="Posts Service",
    description="Микросервис для управления постами форума с проверкой пользователей"
)


async def check_user_exists(user_id: int):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"http://localhost:8000/users/{user_id}",
                timeout=5.0
            )

            if response.status_code == 404:
                return None

            return response.json()

    except httpx.RequestError as e:
        print(f"Ошибка соединения с сервисом пользователей: {e}")
        return None


@app.get("/posts/", response_model=Dict[int, Post])
async def get_posts():
    return db["posts"]


@app.get("/posts/{post_id}", response_model=Post)
async def get_post(post_id: int):
    if post_id not in db["posts"]:
        raise HTTPException(status_code=404, detail="Post not found")
    return db["posts"][post_id]


@app.post("/posts/", response_model=Post, status_code=201)
async def create_post(post: PostCreate):
    user_data = await check_user_exists(post.user_id)
    if not user_data:
        raise HTTPException(
            status_code=400,
            detail=f"Пользователь с ID {post.user_id} не существует"
        )

    post_id = db["next_post_id"]
    now = datetime.now().strftime("%Y-%m-%d")
    db["posts"][post_id] = Post(
        post_id=post_id,
        user_id=post.user_id,
        author=user_data["username"],
        title=post.title,
        content=post.content,
        created_at=now
    )
    db["next_post_id"] += 1
    return db["posts"][post_id]


@app.put("/posts/{post_id}", response_model=Post)
async def update_post(post_id: int, post: PostUpdate):
    if post_id not in db["posts"]:
        raise HTTPException(status_code=404, detail="Post not found")

    if post.user_id is not None:
        if not await check_user_exists(post.user_id):
            raise HTTPException(
                status_code=400,
                detail=f"User with ID {post.user_id} does not exist"
            )

    current_post = db["posts"][post_id]
    update_data = post.dict(exclude_unset=True)
    update_data["updated_at"] = datetime.now().strftime("%Y-%m-%d")

    updated_post = current_post.copy(update=update_data)
    db["posts"][post_id] = updated_post
    return updated_post


@app.delete("/posts/{post_id}", status_code=204)
async def delete_post(post_id: int):
    if post_id not in db["posts"]:
        raise HTTPException(status_code=404, detail="Post not found")
    del db["posts"][post_id]


if __name__ == "__main__":
    uvicorn.run(app, port=8001)
