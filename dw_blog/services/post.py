from datetime import datetime
from typing import List, Optional, Union
from uuid import UUID

from fastapi import Depends
from sqlmodel import Session, select
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload


from dw_blog.db.db import get_session
from dw_blog.exceptions.tag import TagNotThisBlog
from dw_blog.queries.post import get_listed_posts_query, get_listed_user_posts_query
from dw_blog.schemas.auth import AuthUser
from dw_blog.exceptions.post import PostAlreadyLiked, PostAlreadyMarked, PostAuthorLike, PostNotFound, PostNotLiked, PostNotMarked, PostTitleDuplicate
from dw_blog.exceptions.common import AuthorStatusRequired, EntityDeleteFail, EntityFailedAdd, EntityUpdateFail, PaginationLimitSurpassed
from dw_blog.models.post import Post
from dw_blog.models.post import Blog
from dw_blog.schemas.common import SortOrder
from dw_blog.schemas.post import BlogInPost, PostRead, AuthorInPost, PostsRead, ShortPostRead, SortPostBy, TagInPost, LikerOfPost
from dw_blog.services.user import UserService
from dw_blog.services.blog import BlogService
from dw_blog.services.tag import TagService


class PostService:
    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.user_service = UserService(db_session)
        self.blog_service = BlogService(db_session)
        self.tag_service = TagService(db_session)

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
        # Check if user that adds post is author/ admin
        await self.blog_service.check_blog_permissions(
            blog_id=blog_id,
            current_user=current_user,
            operation="post addition",
        )

        # Get blog with authors and tags
        blog = await self.blog_service.get(blog_id=blog_id)
        # Get raw blog
        raw_blog = await self.db_session.get(Blog, blog_id)

        # Check if submitted data is valid
        await self.validate(
            blog_id=blog_id,
            authors_ids=authors_ids,
            blog_authors=blog.authors,
            tags_ids=tags_ids,
            blog_tags=blog.tags,
        )

        # Get authors and tags
        authors = await self.user_service.bulk_get(authors_ids)
        tags = await self.tag_service.bulk_get(tags_ids)

        # Create post
        post = Post(
            title=title,
            body=body,
            published=published,
            authors=authors,
            tags=tags,
            blog=raw_blog,
            date_created=datetime.now(),
            date_modified=datetime.now(),
            blog_id=blog_id,
            bibliography=bibliography,
            notes=notes,
        )

        try:
            self.db_session.add(post)
            await self.db_session.commit()
            await self.db_session.refresh(post)
        except IntegrityError:
            raise PostTitleDuplicate(title=title, blog_id=blog_id)
        except Exception:
            raise EntityFailedAdd(entity_name="post")

        return await self.get(post_id=post.id)

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
                selectinload(Post.likers),
                selectinload(Post.favouriters),
            )
            .where(Post.id == post_id)
        )
        result = await self.db_session.exec(q)

        if not (post := result.first()):
            raise PostNotFound(post_id=post_id)

        return post

    async def list(
        self,
        limit: int = 10,
        offset: int = 0,
        published: bool = True,
        blog_id: Optional[UUID] = None,
        authors_ids: Optional[List[UUID]] = None,
        tags_ids: Optional[List[UUID]] = None,
        title_search: Optional[str] = None,
        body_search: Optional[str] = None,
        sort_order: SortOrder = SortOrder.ascending,
        sort_by: SortPostBy = SortPostBy.date_created,
    ):
        # Check limit
        if limit > 20:
            raise PaginationLimitSurpassed()
        
        # Create query
        q_pag, q_all = get_listed_posts_query(
            limit=limit,
            offset=offset,
            published=published,
            blog_id=blog_id,
            authors_ids=authors_ids,
            tags_ids=tags_ids,
            title_search=title_search,
            body_search=body_search,
            sort_order=sort_order,
            sort_by=sort_by,
        )

        # Execute queries with and without limit
        post_results = await self.db_session.exec(q_pag)
        all_result = await self.db_session.exec(q_all)
        posts = post_results.fetchall()
        total = all_result.fetchall()

        data = []
        for post in posts:
            data.append(
                PostsRead(
                    id=post.id,
                    title=post.title,
                    published=post.published,
                    date_created=post.date_created,
                    date_modified=post.date_modified,
                    body=post.body,
                    notes=post.notes,
                    bibliography=post.bibliography,
                    tags=[
                        TagInPost(
                            id=tag_id,
                            name=tag_name,
                        )
                        for tag_id, tag_name in zip(post.tags_ids, post.tags_names)
                    ],
                    authors=[
                        AuthorInPost(
                            id=author_id,
                            nickname=author_nickname,
                        )
                        for author_id, author_nickname in zip(post.authors_ids, post.authors_nicknames)
                    ],
                    likers=[
                        LikerOfPost(
                            id=liker_id,
                            nickname=liker_nickname,
                        )
                        for liker_id, liker_nickname in zip(post.likers_ids, post.likers_nicknames) if liker_id
                    ],
                    blog=BlogInPost(
                        id=post.blog_id,
                        name=post.blog_name,
                    ),
                    likes_count=post.likes_count,
                )
            )
        
        # Return data
        return data, len(total)

    async def update(
        self,
        post_id: UUID,
        current_user: AuthUser,
        title: Optional[str] = None,
        body: Optional[str] = None,
        published: Optional[bool] = None,
        bibliography: Optional[List[str]] = None,
        notes: Optional[List[str]] = None,
        tags_ids: Optional[List[UUID]] = None,
        authors_ids: Optional[List[UUID]] = None,
    ) -> PostRead:
        # Get post
        post = await self.get(post_id=post_id)
        # Get blog with authors and tags
        blog = await self.blog_service.get(blog_id=post.blog_id)

        # Check if user that updates post is author/ admin
        await self.blog_service.check_blog_permissions(
            blog_id=post.blog_id,
            current_user=current_user,
            operation="post update",
        )

        # Check if submitted data is valid
        await self.validate(
            blog_id=post.blog_id,
            authors_ids=authors_ids,
            blog_authors=blog.authors,
            tags_ids=tags_ids,
            blog_tags=blog.tags,
        )

        # Get authors and tags
        if authors_ids:
            authors = await self.user_service.bulk_get(authors_ids)
            post.authors = authors
        if tags_ids:
            tags = await self.tag_service.bulk_get(tags_ids)
            post.tags = tags

        # Update post
        if title:
            post.title = title
        if body:
            post.body = body
        if published is not None:
            post.published = published
        if bibliography:
            post.bibliography = bibliography
        if notes:
            post.notes = notes
        post.date_modified = datetime.now()

        try:
            await self.db_session.commit()
            await self.db_session.refresh(post)
        except IntegrityError:
            raise PostTitleDuplicate(title=title, blog_id=post.blog_id)
        except Exception:
            raise EntityUpdateFail(entity_id=post_id, entity_name="post")

        return await self.get(post_id=post_id)

    async def like(
        self,
        post_id: UUID,
        current_user: AuthUser,
    ):
        # Get post
        post = await self.get(post_id=post_id)

        # Check if user that likes post is not author
        post_authors_ids = [str(author.id) for author in post.authors]
        if str(current_user["user_id"]) in post_authors_ids:
            raise PostAuthorLike(post_id=post_id)
        
        # Check if user already liked post
        post_likers_ids = [str(liker.id) for liker in post.likers]
        if str(current_user["user_id"]) in post_likers_ids:
            raise PostAlreadyLiked(post_id=post_id, user_id=current_user["user_id"])

        # Like post
        liker = await self.user_service.bulk_get(user_ids=[current_user["user_id"]])
        post.likers.append(liker[0])

        # Try to save in the db
        try:
            await self.db_session.commit()
            await self.db_session.refresh(post)
        except Exception:
            raise EntityUpdateFail(entity_id=post_id, entity_name="post")

        return await self.get(post_id=post_id)

    async def unlike(
        self,
        post_id: UUID,
        current_user: AuthUser,
    ):
        # Get post
        post = await self.get(post_id=post_id)

        # Check if user already liked post
        post_likers_ids = [str(liker.id) for liker in post.likers]
        if str(current_user["user_id"]) not in post_likers_ids:
            raise PostNotLiked(post_id=post_id, user_id=current_user["user_id"])

        # Unlike post
        post.likers = [liker for liker in post.likers if str(liker.id) != str(current_user["user_id"])]

        # Try to save in the db
        try:
            await self.db_session.commit()
            await self.db_session.refresh(post)
        except Exception:
            raise EntityUpdateFail(entity_id=post_id, entity_name="post")

        return await self.get(post_id=post_id)

    async def add_favourite(
        self,
        post_id: UUID,
        current_user: AuthUser,
    ):
        # Get post
        post = await self.get(post_id=post_id)

        # Check if user already marked post
        post_favouriters_ids = [str(favouriter.id) for favouriter in post.favouriters]
        if str(current_user["user_id"]) in post_favouriters_ids:
            raise PostAlreadyMarked(post_id=post_id, user_id=current_user["user_id"])

        # Add post to favourites
        favouriter = await self.user_service.bulk_get(user_ids=[current_user["user_id"]])
        post.favouriters.append(favouriter[0])

        # Try to save in the db
        try:
            await self.db_session.commit()
            await self.db_session.refresh(post)
        except Exception:
            raise EntityUpdateFail(entity_id=post_id, entity_name="post")

        return await self.get(post_id=post_id)

    async def remove_favourite(
        self,
        post_id: UUID,
        current_user: AuthUser,
    ):
        # Get post
        post = await self.get(post_id=post_id)

        # Check if user marked the post
        post_favouriters_ids = [str(favouriter.id) for favouriter in post.favouriters]
        if str(current_user["user_id"]) not in post_favouriters_ids:
            raise PostNotMarked(post_id=post_id, user_id=current_user["user_id"])

        # Remove post from favourites
        post.favouriters = [favouriter for favouriter in post.favouriters if str(favouriter.id) != str(current_user["user_id"])]

        # Try to save in the db
        try:
            await self.db_session.commit()
            await self.db_session.refresh(post)
        except Exception:
            raise EntityUpdateFail(entity_id=post_id, entity_name="post")

        return await self.get(post_id=post_id)

    async def list_user_posts(
        self,
        current_user: AuthUser,
        liked: bool = True,
        offset: int = 0,
    ) -> Union[List[ShortPostRead], int]:
        user_id = current_user["user_id"] 
        # Create query
        q_pag, q_all = get_listed_user_posts_query(
            user_id=user_id,
            liked=liked,
            offset=offset,
        )
        
        # Execute queries with and without limit
        post_results = await self.db_session.exec(q_pag)
        all_result = await self.db_session.exec(q_all)
        posts = post_results.fetchall()
        total = all_result.fetchall()
        
        data = []
        for post in posts:
            data.append(
                ShortPostRead(
                    id=post.id,
                    title=post.title,
                    body=post.body[:31].strip() + "...",
                    blog_id=post.blog.id,
                    blog_name=post.blog.name,
                    date_created=post.date_created,
                )
            )

        return data, len(total)

    async def delete(
        self,
        post_id: UUID,
        current_user: AuthUser,
    ):
        # Get post
        post = await self.get(post_id=post_id)

        # Check if user that deletes post is author/ admin
        await self.blog_service.check_blog_permissions(
            blog_id=post.blog_id,
            current_user=current_user,
            operation="post deletion",
        )

        # Delete post
        try:
            self.db_session.delete(post)
            await self.db_session.commit()
        except Exception:
            raise EntityDeleteFail(entity_id=post_id, entity_name="post")

    async def validate(
        self,
        blog_id: UUID,
        authors_ids: Optional[List[UUID]] = None,
        blog_authors: Optional[List[AuthorInPost]] = None,
        tags_ids: Optional[List[UUID]] = None,
        blog_tags: Optional[List[TagInPost]] = None,
    ):
        # Check if submitted authors are blog authors
        if authors_ids:
            blog_authors_id = [author.author_id for author in blog_authors]
            for author_id in authors_ids:
                if author_id not in blog_authors_id:
                    raise AuthorStatusRequired(
                        operation="post addition",
                        user_id=author_id,
                        blog_id=blog_id,
                    )
        
        # Check if submitted tags are blog tags
        if tags_ids:
            blog_tags_id = [tag.tag_id for tag in blog_tags]
            for tag_id in tags_ids:
                if tag_id not in blog_tags_id:
                    raise TagNotThisBlog(
                        tag_id=tag_id,
                        blog_id=blog_id,
                    )

async def get_post_service(session: AsyncSession = Depends(get_session)):
    yield PostService(session)
