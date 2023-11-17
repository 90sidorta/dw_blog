from typing import Optional, List
from datetime import datetime
from uuid import UUID

from fastapi import Depends, HTTPException, status
from sqlmodel import Session, select, delete
from sqlmodel.ext.asyncio.session import AsyncSession

from dw_blog.db.db import get_session
from dw_blog.models.blog import BlogRead, Blog, BlogAuthors, BlogAuthor
from dw_blog.db.db import get_session
from dw_blog.models.auth import AuthUser
from dw_blog.models.user import User, UserType
from dw_blog.services.user import UserService
from dw_blog.exceptions.blog import BlogLimitReached, FailedBlogAdd, BlogNotFound


class BlogService:
    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.user_service = UserService(db_session)

    async def create(
        self,
        current_user: AuthUser,
        name: str,
    ) -> BlogRead:
        """This function creates new blog for authenticated user.
        Args:
            current_user (AuthUser): data of authenticated user.
            name (str): blog name
        Raises:
            BlogLimitReached: raised if user already has 3 blogs
            FailedBlogAdd: raised if blog addition failed
        Returns:
            BlogRead: Created blog with author data
        """
        # Check if user has less than 3 blogs
        user = await self.user_service.get(
            user_id=str(current_user["user_id"])
        )
        q = select(BlogAuthors).where(BlogAuthors.author_id == user.id)
        result = await self.db_session.exec(q)
        user_blogs = result.fetchall()
        if len(user_blogs) >= 3:
            raise BlogLimitReached()

        # Try to add new blog
        try:
            blog = Blog(
                name=name,
                date_created=datetime.now(),
                date_modified=datetime.now(),
                authors=[user]
            )
            self.db_session.add(blog)
            await self.db_session.commit()
            await self.db_session.refresh(blog)
        except Exception:
            raise FailedBlogAdd()

        # Return created blog
        blog_read = await self.get(blog_id=blog.id)
        return blog_read

    async def get(
        self,
        blog_id: UUID,
    ) -> BlogRead:
        """Get blog data from database
        Args:
            blog_id (UUID): id of blog to be read
        Raises:
            BlogNotFound: raised if blog does not exist
        Returns:
            BlogRead: Read blog with author data
        """
        # Construct query with joined authors data
        q = (
            select(
                Blog.id,
                Blog.name,
                Blog.date_created,
                Blog.date_modified,
                User.id.label("author_id"),
                User.nickname.label("author_nickname"),
            )
            .join(BlogAuthors, onclause=Blog.id == BlogAuthors.blog_id, isouter=True)
            .join(User, onclause=BlogAuthors.author_id == User.id, isouter=True)
            .where(Blog.id == blog_id)
        )
        result = await self.db_session.exec(q)
        blogs = result.all()

        # If no blog was found raise an exception
        if len(blogs) == 0:
            raise BlogNotFound()
        
        # Fetch data for authors field
        authors = []
        for blog in blogs:
            authors.append(
                BlogAuthor(
                    author_id=blog.author_id,
                    nickname=blog.author_nickname,
                )
            )

        # Prepare and send response
        blog_read = BlogRead(
            id=blog.id,
            name=blog.name,
            date_created=blog.date_created,
            date_modified=blog.date_modified,
            authors=authors
        )
        return blog_read

    async def list(
        self,
        author_name: Optional[str] = None,
        blog_name: Optional[str] = None,
    ) -> List[BlogRead]:
        """Get listed blogs based - either all or based on authors_name or blog_name
        Args:
            author_name (Optional[str], optional): Name of author of the blog. Defaults to None.
            blog_name (Optional[str], optional): Name of the blog. Defaults to None.
        Raises:
            BlogNotFound: raised if no blog matching criteria exists
        Returns:
            List[BlogRead]: List of blogs matching users criteria
        """
        # Get all blogs if no author_name and no blog_name were provided
        if not blog_name and not author_name:
            blogs_result = await self.db_session.exec(select(Blog))
            blogs = blogs_result.fetchall()
        # Get blogs if user searches them on the basis of blog name
        if blog_name:
            q = select(Blog).where(Blog.name.ilike(f"%{blog_name}%"))
            blogs_name_result = await self.db_session.exec(q)
            blogs = blogs_name_result.fetchall()
        
        # Get blogs if user searches them on the basis of authors name
        if author_name:
            users = await self.user_service.list(nickname=author_name)
            blogs = []

            for user in users:
                user_blogs_results = await self.db_session.exec(
                    select(Blog)
                    .join(BlogAuthors, onclause=Blog.id == BlogAuthors.blog_id, isouter=True)
                    .where(BlogAuthors.author_id == user.id)
                )
                user_blogs = user_blogs_results.fetchall()
                
                for user_blog in user_blogs:
                    blogs.append(user_blog)

        # Raise exception if no blogs were found
        if len(blogs) == 0:
            raise BlogNotFound()

        # Prepare read blog response
        return_blogs = []
        for blog in blogs:
            return_blogs.append(await self.get(blog_id=blog.id))
        
        return return_blogs

    async def check_blog(
        self,
        blog_id: UUID,
        current_user: AuthUser,
    ):
        # Check if blog exists
        blog = await self.get(blog_id=blog_id)
        # Chek user permissions
        authors_ids = []
        for author in blog.authors:
            authors_ids.append(author.author_id)
        if current_user["user_id"] not in authors_ids and current_user["user_type"] != UserType.admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Can't update other user blog!",
            )

    async def update(
        self,
        blog_id: UUID,
        current_user: AuthUser,
        name: str,
    ) -> BlogRead:
        await self.check_blog(
            blog_id=blog_id,
            current_user=current_user,
        )

        # Update blog name
        update_blog = await self.db_session.get(Blog, blog_id)
        if name:
            update_blog.name = name
        try:
            self.db_session.add(update_blog)
            await self.db_session.commit()
        except Exception as exc:
            print(str(exc))
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to update blog!",
            )

        return await self.get(blog_id=blog_id)

    async def add_author_to_blog(
        self,
        blog_id: UUID,
        current_user: AuthUser,
        add_author_ids: List[UUID],
    ) -> BlogRead:
        await self.check_blog(
            blog_id=blog_id,
            current_user=current_user,
        )
        # Check if blog already reached limit of five authors
        q = select(BlogAuthors).where(BlogAuthors.blog_id == blog_id)
        blog_authors_result = self.db_session.exec(q)
        blog_authors = blog_authors_result.fetchall()

        if len(blog_authors) > 5 or (len(blog_authors) + len(add_author_ids) > 5):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Blog can only have 5 authors!",
            )
        
        for author_id in add_author_ids:
            # Check if user is already author and if yes, pass this id
            author_already_result = self.db_session.exec(
                select(BlogAuthors)
                .where(
                    BlogAuthors.blog_id == blog_id,
                    BlogAuthors.author_id == author_id,
                )
            )
            author_already = author_already_result.first()
            # If user is not already an author, add him/her
            if not author_already:
                try:
                    blog_author = BlogAuthors(
                        blog_id=blog_id,
                        author_id=author_id,
                    )
                    self.db_session.add(blog_author)
                    await self.db_session.commit()
                    await self.db_session.refresh(blog_author)
                except Exception:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Failed to add author to blog!",
                    )

        blog_read = await self.get(blog_id=blog_id)
        return blog_read

    async def remove_author_from_blog(
        self,
        blog_id: UUID,
        current_user: AuthUser,
        remove_author_id: UUID,
    ) -> BlogRead:
        await self.check_blog(
            blog_id=blog_id,
            current_user=current_user,
        )
        # Check count of authors
        blog = await self.get(blog_id=blog_id)
        if len(blog.authors) == 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Can't delete the only author!",
            )
        # Remove author from the blog
        q = delete(BlogAuthors).where(
            (BlogAuthors.author_id == remove_author_id),
            (BlogAuthors.blog_id == blog_id),
        )
        try:
            self.db_session.exec(q)
            self.db_session.commit()
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Failed to delete author!",
            )
        return await self.get(blog_id=blog_id) 

    async def delete(
        self,
        blog_id: UUID,
        current_user: AuthUser,
    ):
        await self.check_blog(
            blog_id=blog_id,
            current_user=current_user,
        )
        # Delete blog
        delete_blog = await self.db_session.get(Blog, blog_id)
        try:
            self.db_session.delete(delete_blog)
            self.db_session.commit()
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Failed to delete blog!",
            )

async def get_blog_service(session: AsyncSession = Depends(get_session)):
    yield BlogService(session)
