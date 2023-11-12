from fastapi import FastAPI

from dw_blog.db.db import init_db
from dw_blog.routers.example import router as example_router
from dw_blog.routers.user import router as user_router
from dw_blog.routers.auth import router as auth_router
from dw_blog.routers.post import router as post_router

app = FastAPI()

app.include_router(
    example_router,
    tags=["example"],
    prefix="/example"
)
app.include_router(
    user_router,
    tags=["users"],
    prefix="/users"
)
app.include_router(
    auth_router,
    tags=["auth"],
    prefix="/auth"
)
app.include_router(
    post_router,
    tags=["posts"],
    prefix="/posts"
)

@app.on_event("startup")
async def on_startup():
    await init_db()


@app.get("/")
def read_root():
    return {"Hello": "World"}
