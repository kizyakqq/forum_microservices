from typing import Dict
import httpx
import uvicorn
from fastapi import FastAPI, HTTPException
from models import User, UserCreate, UserUpdate, db

app = FastAPI(
    title="User Service",
    description="Микросервис для управления пользователями форума"
)


@app.get("/users/", response_model=Dict[int, User])
def get_users():
    return db["users"]


@app.get("/users/{user_id}", response_model=User)
def get_user(user_id: int):
    if user_id not in db["users"]:
        raise HTTPException(status_code=404, detail="User not found")
    return db["users"][user_id]


@app.get("/users/{user_id}/posts", response_model=Dict[int, Dict])
async def get_user_posts(user_id: int):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"http://localhost:8001/posts/")
            if response.status_code != 200:
                raise HTTPException(
                    status_code=400,
                    detail="Не удалось получить посты пользователя"
                )

            all_posts = response.json()
            user_posts = {
                post_id: post for post_id, post in all_posts.items()
                if post["user_id"] == user_id
            }

            return user_posts

    except httpx.RequestError as e:
        raise HTTPException(
            status_code=503,
            detail=f"Сервис постов недоступен: {e}"
        )


@app.post("/users/", response_model=User, status_code=201)
def create_user(user: UserCreate):
    user_id = db["next_user_id"]
    db["users"][user_id] = User(
        user_id=user_id,
        username=user.username,
        email=user.email,
        password_hash=f"hashed_{user.password}"
    )
    db["next_user_id"] += 1
    return db["users"][user_id]


@app.put("/users/{user_id}", response_model=User)
def update_user(user_id: int, user: UserUpdate):
    if user_id not in db["users"]:
        raise HTTPException(status_code=404, detail="User not found")

    current_user = db["users"][user_id]
    update_data = user.dict(exclude_unset=True)

    if "password" in update_data:
        update_data["password_hash"] = f"hashed_{update_data.pop('password')}"

    updated_user = current_user.copy(update=update_data)
    db["users"][user_id] = updated_user
    return updated_user


@app.delete("/users/{user_id}", status_code=204)
def delete_user(user_id: int):
    if user_id not in db["users"]:
        raise HTTPException(status_code=404, detail="User not found")
    del db["users"][user_id]


if __name__ == "__main__":
    uvicorn.run(app, port=8000)
