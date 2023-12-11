from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import Depends, HTTPException, status
from sqlmodel import Session, select
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import selectinload

from dw_blog.db.db import get_session
from dw_blog.schemas.auth import AuthUser
from dw_blog.exceptions.post import PostNotFound
from dw_blog.exceptions.common import AuthorStatusRequired
from dw_blog.models.post import Post
from dw_blog.models.blog import Blog
from dw_blog.models.user import User
from dw_blog.schemas.post import PostRead
from dw_blog.services.user import UserService
from dw_blog.services.blog import BlogService
from dw_blog.utils.auth import check_if_admin


class PostService:
    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.user_service = UserService(db_session)
        self.blog_service = BlogService(db_session)

    async def create(
        self,
        current_user: AuthUser,
        tags_ids: List[UUID],
        authors_ids: List[UUID],
        blog_id: UUID,
        title: str,
        body: str,
        published: bool,
        bibliography: Optional[List[str]] = None,
        notes: Optional[List[str]] = None,

    ) -> PostRead:
        # TODO: Finish this
        # Check if user that adds post is author/ admin
        await self.blog_service.check_blog_permissions(
            blog_id=blog_id,
            current_user=current_user,
            operation="post addition",
        )
        
        # Get blog with authors and tags
        blog_result = await self.db_session.exec(
            (
                select(Blog)
                .options(selectinload(Blog.authors))
                .options(selectinload(Blog.tags))
                .where(Blog.id == blog_id)
             )
        )
        blog = blog_result.first()

        # Chek if submitted authors are blog authors
        print("++++++++++")
        print(blog.authors)
        authors = []
        for author_id in authors_ids:
            found = False
            for blog_author in blog.authors:
                if author_id == blog_author.id:
                    found = True
                    authors.append(blog_author)
            if found == False:
                raise AuthorStatusRequired(
                    operation="post addition",
                    user_id=author_id,
                    blog_id=blog_id,
                )
        print("++++++++++")
        print("authors", authors)

         # Chek if submitted tags are blog tags



        # try:
        #     post = Post(
        #         text=text,
        #         date_created=datetime.now(),
        #         date_modified=datetime.now(),
        #         published=is_author,
        #         author_id=user.id,
        #         author_nickname=user.nickname,
        #     )
        #     self.db_session.add(post)
        #     await self.db_session.commit()
        #     await self.db_session.refresh(post)
        # except Exception:
        #     raise HTTPException(
        #         status_code=status.HTTP_400_BAD_REQUEST,
        #         detail="Failed to add post!",
        #     )

        # return post

    async def get(
        self,
        post_id: UUID,
    ) -> PostRead:
        q = (
            select(Post)
            .options(
                selectinload(Post.authors),
                selectinload(Post.blog),
                selectinload(Post.tags),
            )
            .where(Post.id == post_id)
        )
        result = await self.db_session.exec(q)

        if not (post := result.first()):
            raise PostNotFound(post_id=post_id)

        return post

async def get_post_service(session: AsyncSession = Depends(get_session)):
    yield PostService(session)
