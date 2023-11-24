from typing import Optional, List, Union
from datetime import datetime
from uuid import UUID

from fastapi import Depends
from sqlmodel import Session, select, delete, func
from sqlmodel.ext.asyncio.session import AsyncSession

from dw_blog.db.db import get_session
from dw_blog.models.blog import (
    BlogRead,
    Blog,
    BlogAuthors,
    BlogAuthor,
    BlogTag,
    BlogReadList,
    BlogLikes,
    BlogLiker,
    BlogSubscriber,
    BlogSubscribers,
)
from dw_blog.db.db import get_session
from dw_blog.models.auth import AuthUser
from dw_blog.models.user import User, UserType
from dw_blog.models.tag import Tag
from dw_blog.services.user import UserService
from dw_blog.exceptions.common import ListException, PaginationLimitSurpassed
from dw_blog.exceptions.blog import (
    BlogLimitReached,
    BlogFailedAdd,
    BlogNotFound,
    BlogAuthorsLimitReached,
    BlogAuthorsAddFail,
    BlogAlreadyAuthor,
    BlogNotYours,
    BlogLastAuthor,
    BlogDeleteAuthorFail,
    BlogUpdateFail,
    BlogDeleteFail,
)


UserLiker = User.__table__.alias()
UserSubscriber = User.__table__.alias()

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
            raise BlogFailedAdd()

        # Return created blog
        blog_read = await self.get(blog_id=blog.id)
        return blog_read

    async def get(
        self,
        blog_id: UUID,
    ):
    #  -> BlogRead:
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
                func.array_agg(func.distinct(User.id)).label("author_id"),
                func.array_agg(func.distinct(User.nickname)).label("author_nickname"),
                func.array_agg(func.distinct(Tag.id)).label("tag_id"),
                func.array_agg(func.distinct(Tag.name)).label("tag_name"),
                func.array_agg(func.distinct(UserLiker.c.id)).label("likers_id"),
                func.array_agg(func.distinct(UserLiker.c.nickname)).label("likers_nicknames"),
                func.array_agg(func.distinct(UserSubscriber.c.id)).label("subscriber_id"),
                func.array_agg(func.distinct(UserSubscriber.c.nickname)).label("subscriber_nicknames"),
            )
            .join(BlogAuthors, onclause=Blog.id == BlogAuthors.blog_id, isouter=True)
            .join(User, onclause=BlogAuthors.author_id == User.id, isouter=True)
            .join(BlogLikes, onclause=Blog.id == BlogLikes.blog_id, isouter=True)
            .join(UserLiker, onclause=BlogLikes.liker_id == UserLiker.c.id, isouter=True)
            .join(BlogSubscribers, onclause=Blog.id == BlogSubscribers.blog_id, isouter=True)
            .join(UserSubscriber, onclause=BlogSubscribers.subscriber_id == UserSubscriber.c.id, isouter=True)
            .join(Tag, onclause=Blog.id == Tag.blog_id, isouter=True)
            .where(Blog.id == blog_id)
            .group_by(Blog.id)
        )
        result = await self.db_session.exec(q)
        blog = result.first()

        print("q", q)
        print(blog)

        # If no blog was found raise an exception
        if not blog:
            raise BlogNotFound()


        # Prepare and send response
        return BlogRead(
            id=blog[0],
            name=blog[1],
            date_created=blog[2],
            date_modified=blog[3],
            authors=[
                BlogAuthor(
                    author_id=author_id,
                    nickname=nickname
                ) for author_id, nickname in zip(blog[4], blog[5])
            ],
            tags=[
                BlogTag(
                    tag_id=tag_id,
                    tag_name=tag_name
                ) for tag_id, tag_name in zip(blog[6], blog[7])
            ],
            likers=[
                BlogLiker(
                    liker_id=liker_id,
                    nickname=nickname,
                ) for liker_id, nickname in zip(blog[8], blog[9])
            ],
            subscribers=[
                BlogSubscriber(
                    subscriber_id=subscriber_id,
                    nickname=nickname,
                ) for subscriber_id, nickname in zip(blog[10], blog[11])
            ]
        )

    async def list(
        self,
        limit: int,
        offset: int,
        blog_name: Optional[str] = None,
        author_id: Optional[UUID] = None,
    ) -> List[BlogReadList]:
        """Get listed blogs based - either all or based on authors_name or blog_name
        Args:
            limit [int]: up to how many results per page
            offset [int]: how many records should be skipped
            blog_name (Optional[str], optional): Name of the blog. Defaults to None.
            author_id (Optional[str], optional): Id of the author. Defaults to None.
        Raises:
            BlogNotFound: raised if no blog matching criteria exists
            PaginationLimitSurpassed: raised if limit was suprassed
        Returns:
            List[BlogRead]: List of blogs matching users criteria
        """
        # Check limit
        if limit > 20:
            raise PaginationLimitSurpassed()

        # Create query
        q = select(Blog)
        # Get blogs if user searches them on the basis of blog name
        if blog_name:
            q = q.where(Blog.name.ilike(f"%{blog_name}%"))
        if author_id:
            q = (
                q
                .join(
                    BlogAuthors,
                    onclause=BlogAuthors.blog_id == Blog.id,
                    isouter=True
                )
                .join(
                    User,
                    onclause=User.id == BlogAuthors.author_id,
                    isouter=True
                )
                .where(User.id == author_id)
            )
        # Add pagination to query
        q = q.limit(limit).offset(offset)
        # Execute query
        blogs_result = await self.db_session.exec(q)
        blogs = blogs_result.fetchall()
        
        return blogs

    async def check_blog(
        self,
        blog_id: UUID,
        current_user: AuthUser,
    ):
        """Checks if user trying to modify blog is either
        an author or an admin
        Args:
            blog_id (UUID): blog id
            current_user (AuthUser): current user object
        Raises:
            NotYourBlog: raised if user is not an author/ admin
        """
        # Check if blog exists
        blog = await self.get(blog_id=blog_id)
        # Chek user permissions
        authors_ids = []
        for author in blog.authors:
            authors_ids.append(author.author_id)
        if current_user["user_id"] not in authors_ids and current_user["user_type"] != UserType.admin:
            raise BlogNotYours()

    async def update(
        self,
        blog_id: UUID,
        current_user: AuthUser,
        name: str,
    ) -> BlogRead:
        """Updates blog data
        Args:
            blog_id (UUID): id of blog to be updated
            current_user (AuthUser): current user object
            name (str): new blog name
        Raises:
            BlogUpdateFail: raised if blog update failed
        Returns:
            BlogRead: Read blog with author data
        """
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
        except Exception:
            raise BlogUpdateFail()

        return await self.get(blog_id=blog_id)

    async def is_author_already(
        self,
        blog_id: UUID,
        author_id:UUID,
    ) -> Union[BlogAuthors, None]:
        """Checks if user is already an author of the blog
        Args:
            blog_id (UUID): id of the blog
            author_id (UUID): id of user
        Returns:
            Union[BlogAuthors, None]: either result from Blog
            Authors table or None
        """
        author_already_result = await self.db_session.exec(
            select(BlogAuthors)
            .where(
                BlogAuthors.blog_id == blog_id,
                BlogAuthors.author_id == author_id,
            )
        )
        return author_already_result.first()

    async def add_author_to_blog(
        self,
        blog_id: UUID,
        current_user: AuthUser,
        add_author_ids: List[UUID],
    ) -> BlogRead:
        """This function adds users as authors to the blog
        Args:
            blog_id (UUID): blog id
            current_user (AuthUser): current user data
            add_author_ids (List[UUID]): author id
        Raises:
            AuthorsLimitReached: raised if blog already has 5 authors
            AuthorsAddFail: raised if authors were not added
            ListException: raised if some users were already authors
        Returns:
            BlogRead: Blog data with authors details
        """
        await self.check_blog(
            blog_id=blog_id,
            current_user=current_user,
        )
        # Check if blog already reached limit of five authors
        q = select(BlogAuthors).where(BlogAuthors.blog_id == blog_id)
        blog_authors_result = await self.db_session.exec(q)
        blog_authors = blog_authors_result.fetchall()

        if len(blog_authors) > 5 or \
            (len(blog_authors) + len(add_author_ids) > 5):
            raise BlogAuthorsLimitReached()
        
        # Check if user is already author and if yes, pass this id
        already_authors = []
        add_authors = []
        for author_id in add_author_ids:
            author_already = await self.is_author_already(
                blog_id=blog_id,
                author_id=author_id
            )
            # If user is not already an author, add him/her
            if author_already:
                already_authors.append(BlogAlreadyAuthor(author_id=author_id))
            else:
                add_authors.append(BlogAuthors(blog_id=blog_id, author_id=author_id))

        # Commit changes
        try:
            for blog_author in add_authors:
                self.db_session.add(blog_author)
            await self.db_session.commit()
        except Exception:
            raise BlogAuthorsAddFail()
        
        # Raise exception if some users were already blog authors
        if len(already_authors) > 0:
            raise ListException(detail=already_authors)

        blog_read = await self.get(blog_id=blog_id)
        return blog_read

    async def remove_author_from_blog(
        self,
        blog_id: UUID,
        current_user: AuthUser,
        remove_author_id: UUID,
    ) -> BlogRead:
        """Remove user from blog authors
        Args:
            blog_id (UUID): id of user to be removed from
            authors list
            current_user (AuthUser): current user object
            remove_author_id (UUID): user id to be removed
        Raises:
            BlogLastAuthor: raised if user to be removed
            is blogs last author
            BlogDeleteAuthorFail: raised if blogs author
            removal failed
        Returns:
            BlogRead: blog with authors data
        """
        await self.check_blog(
            blog_id=blog_id,
            current_user=current_user,
        )
        # Check count of authors
        blog = await self.get(blog_id=blog_id)
        if len(blog.authors) == 1:
            raise BlogLastAuthor()

        # Remove author from the blog
        q = delete(BlogAuthors).where(
            (BlogAuthors.author_id == remove_author_id),
            (BlogAuthors.blog_id == blog_id),
        )
        try:
            self.db_session.exec(q)
            self.db_session.commit()
        except Exception:
            raise BlogDeleteAuthorFail()

        return await self.get(blog_id=blog_id) 

    async def delete(
        self,
        blog_id: UUID,
        current_user: AuthUser,
    ):
        """Deletes blog
        Args:
            blog_id (UUID): blog id
            current_user (AuthUser): current user object

        Raises:
            BlogDeleteFail: sed if blog delete fails
        """
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
            raise BlogDeleteFail()

async def get_blog_service(session: AsyncSession = Depends(get_session)):
    yield BlogService(session)
