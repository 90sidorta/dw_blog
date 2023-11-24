from fastapi import FastAPI

from dw_blog.db.db import init_db
from dw_blog.routers.user import router as user_router
from dw_blog.routers.auth import router as auth_router
from dw_blog.routers.post import router as post_router
from dw_blog.routers.blog import router as blog_router
from dw_blog.routers.tag import router as tag_router

app = FastAPI()

app.include_router(
    user_router,
    tags=["Users"],
    prefix="/users"
)
app.include_router(
    auth_router,
    tags=["Auth"],
    prefix="/auth"
)
app.include_router(
    post_router,
    tags=["Posts"],
    prefix="/posts"
)
app.include_router(
    blog_router,
    tags=["Blogs"],
    prefix="/blogs"
)
app.include_router(
    tag_router,
    tags=["Tags"],
    prefix="/tags"
)

@app.on_event("startup")
async def on_startup():
    await init_db()


@app.get("/")
def read_root():
    return {"Hello": "World"}
