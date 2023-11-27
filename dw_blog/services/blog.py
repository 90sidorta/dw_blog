from typing import Optional, List, Union
from datetime import datetime
from uuid import UUID

from fastapi import Depends
from sqlmodel import Session, select
from sqlmodel.ext.asyncio.session import AsyncSession

from dw_blog.db.db import get_session
from dw_blog.models.blog import (
    BlogRead,
    Blog,
    BlogAuthors,
    BlogAuthor,
    BlogTag,
    SortBlogBy,
    BlogLikes,
    BlogLiker,
    BlogSubscriber,
    BlogSubscribers,
    BlogReadList,
)
from dw_blog.models.common import SortOrder
from dw_blog.db.db import get_session
from dw_blog.models.auth import AuthUser
from dw_blog.models.user import UserType
from dw_blog.queries.blog import (
    get_single_blog_query,
    get_listed_blogs_query,
    is_author_query,
    delete_author_query,
    check_subscription_query,
    check_like_query,
)
from dw_blog.services.user import UserService
from dw_blog.exceptions.common import ListException, PaginationLimitSurpassed
from dw_blog.exceptions.user import UserNotFound
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
    BlogAlreadySubscribed,
    BlogSubscribtionFail,
    BlogNotSubscribed,
    BlogUnsubscribtionFail,
    BlogAlreadyLiked,
    BlogNotLiked,
    BlogLikeFail,
    BlogUnlikeFail,
    BlogNotAuthor,
)


class BlogService:
    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.user_service = UserService(db_session)

    async def check_author_blogs(
        self,
        user_id: UUID
    ):
        """Checks if user has reachead limit of the blogs
        Args:
            user_id (UUID): id of the user
        Raises:
            BlogLimitReached: raised if user has already 3 blogs
        """
        q = select(BlogAuthors).where(BlogAuthors.author_id == user_id)
        result = await self.db_session.exec(q)
        user_blogs = result.fetchall()
        if len(user_blogs) >= 3:
            raise BlogLimitReached(user_id=user_id)

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
        await self.check_author_blogs(user.id)

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
    )-> BlogRead:
        """Get blog data from database
        Args:
            blog_id (UUID): id of blog to be read
        Raises:
            BlogNotFound: raised if blog does not exist
        Returns:
            BlogRead: Read blog with author data
        """
        # Construct query with joined authors data
        q = get_single_blog_query(blog_id=blog_id)
        result = await self.db_session.exec(q)
        blog = result.first()

        # If no blog was found raise an exception
        if not blog:
            raise BlogNotFound(blog_id=blog_id)

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
        sort_order: SortOrder = SortOrder.ascending,
        sort_by: SortBlogBy = SortBlogBy.date_created,
    ) -> Union[List[BlogReadList], int]:
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
        q_pag, q_all = get_listed_blogs_query(
            limit=limit,
            offset=offset,
            blog_name=blog_name,
            author_id=author_id,
            sort_order=sort_order,
            sort_by=sort_by,
        )
        # Execute queries with and without limit
        blogs_result = await self.db_session.exec(q_pag)
        all_result = await self.db_session.exec(q_all)
        blogs = blogs_result.fetchall()
        total = all_result.fetchall()

        return blogs, len(total)

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
            raise BlogNotYours(blog_id=blog_id)

    async def update(
        self,
        blog_id: UUID,
        current_user: AuthUser,
        name: Optional[str] = None,
        archived: Optional[bool] = None,
    ) -> BlogRead:
        """Updates blog data
        Args:
            blog_id (UUID): id of blog to be updated
            current_user (AuthUser): current user object
            name (str): new blog name
            archived (bool): archive the blog
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
        if archived:
            update_blog.archived = archived
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
        q = is_author_query(
            blog_id=blog_id,
            author_id=author_id,
        )
        author_already_result = await self.db_session.exec(q)
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
            raise BlogAuthorsLimitReached(blog_id=blog_id)
        
        authors_errors = []
        add_authors = []
        for author_id in add_author_ids:
            author_already = await self.is_author_already(
                blog_id=blog_id,
                author_id=author_id
            )
            try:
                # Check if user exists
                await self.user_service.get(user_id=author_id)
                # Check if user already reached the limit of the blogs
                await self.check_author_blogs(author_id)
            except (BlogLimitReached, UserNotFound) as exc:
                authors_errors.append(exc)

            # Check if user is already author of this blog
            if author_already:
                authors_errors.append(BlogAlreadyAuthor(author_id=author_id))
            # If user has less than 3 blogs and is not author of the specified blog
            # add him/her as author
            else:
                add_authors.append(BlogAuthors(blog_id=blog_id, author_id=author_id))

        # Commit changes
        if len(authors_errors) > 0:
            # Raise exception if there are any erros     
            raise ListException(detail=authors_errors)

        try:
            for blog_author in add_authors:
                self.db_session.add(blog_author)
            await self.db_session.commit()
        except Exception:
            raise BlogAuthorsAddFail()

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

        # Raise error if user not an author
        if not await self.is_author_already(
            author_id=remove_author_id,
            blog_id=blog_id
        ):
            raise BlogNotAuthor(
                blog_id=blog_id,
                author_id=remove_author_id,
            )

        # Check count of authors
        blog = await self.get(blog_id=blog_id)
        if len(blog.authors) == 1:
            raise BlogLastAuthor()

        # Remove author from the blog
        q = delete_author_query(
            blog_id=blog_id,
            remove_author_id=remove_author_id
        )
        try:
            await self.db_session.exec(q)
            await self.db_session.commit()
        except Exception:
            raise BlogDeleteAuthorFail()

        return await self.get(blog_id=blog_id) 

    async def check_subscription(
        self,
        blog_id: UUID,
        current_user: AuthUser,
    ) -> Union[BlogSubscribers, None]:
        """Checks if user is a subscriber of blog
        based on blog id and current user id
        Args:
            blog_id (UUID): id of the blog
            current_user (AuthUser): logged user object
        Returns:
            Union[BlogSubscribers, None]: Either there is
            a subscription for this blog and user or not
        """
        q = check_subscription_query(
            blog_id=blog_id,
            current_user=current_user,
        )
        result = await self.db_session.exec(q)
        already_subscribes = result.first()
        return already_subscribes
    
    async def check_like(
        self,
        blog_id: UUID,
        current_user: AuthUser,
    ) -> Union[BlogLikes, None]:
        """Checks if user is a liker of blog
        based on blog id and current user id
        Args:
            blog_id (UUID): id of the blog
            current_user (AuthUser): logged user object
        Returns:
            Union[BlogLikes, None]: Either there is
            a like for this blog and user or not
        """
        q = check_like_query(
            blog_id=blog_id,
            current_user=current_user
        )
        result = await self.db_session.exec(q)
        already_likes = result.first()
        return already_likes

    async def subscribe(
        self,
        blog_id: UUID,
        current_user: AuthUser,
    ) -> BlogRead:
        """This function creates a new subscribe record
        Args:
            blog_id (UUID): id of the blog to be
            subscribed to
            current_user (AuthUser): current user object
        Raises:
            BlogAlreadySubscribed: raised if blog is already
            subscribed by the user
            BlogSubscribtionFail: raised if blog subscription
            failed
        Returns:
            BlogRead: blog data
        """
        # Check if user is not already a subscriber
        already_subscribes = await self.check_subscription(
            blog_id=blog_id,
            current_user=current_user
        )
        if already_subscribes:
            raise BlogAlreadySubscribed()
        
        # Try to add new subscription
        try:
            subscription = BlogSubscribers(
                blog_id=blog_id,
                subscriber_id=current_user["user_id"]
            )
            self.db_session.add(subscription)
            await self.db_session.commit()
            await self.db_session.refresh(subscription)
        except Exception:
            raise BlogSubscribtionFail()
        return await self.get(blog_id=blog_id)

    async def unsubscribe(
        self,
        blog_id: UUID,
        current_user: AuthUser,
    ) -> BlogRead:
        """This function deletes subscription entry
        Args:
            blog_id (UUID): id of the blog to unsubscribe
            current_user (AuthUser): current user object
        Raises:
            BlogNotSubscribed: raised if blog was not
            subscribed by the user
            BlogUnsubscribtionFail: raised if any exception
            occured in the process
        Returns:
            BlogRead: blog data
        """
        # Check if user is not already a subscriber
        already_subscribes = await self.check_subscription(
            blog_id=blog_id,
            current_user=current_user
        )
        if not already_subscribes:
            raise BlogNotSubscribed()
        
        # Delete subscription
        try:
            self.db_session.delete(already_subscribes)
            self.db_session.commit()
        except Exception:
            raise BlogUnsubscribtionFail()
        return await self.get(blog_id=blog_id)

    async def like(
        self,
        blog_id: UUID,
        current_user: AuthUser,
    ) -> BlogRead:
        """This adds like record to the database
        Args:
            blog_id (UUID): id of the blog to be liked
            current_user (AuthUser): current user object
        Raises:
            BlogAlreadyLiked: raised if blog already liked
            BlogLikeFail: raised if operation failed
        Returns:
            BlogRead: blog data
        """
        # Check if user is not already a liker
        already_likes = await self.check_like(
            blog_id=blog_id,
            current_user=current_user
        )
        if already_likes:
            raise BlogAlreadyLiked()
        
        # Try to add new subscription
        try:
            like = BlogLikes(
                blog_id=blog_id,
                subscriber_id=current_user["user_id"]
            )
            self.db_session.add(like)
            await self.db_session.commit()
            await self.db_session.refresh(like)
        except Exception:
            raise BlogLikeFail()
        return await self.get(blog_id=blog_id)

    async def unlike(
        self,
        blog_id: UUID,
        current_user: AuthUser,
    ) -> BlogRead:
        """Deletes like entry from the database
        Args:
            blog_id (UUID): id of the blog to be unliked
            current_user (AuthUser): current user object
        Raises:
            BlogNotLiked: raised if blog was not liked by the user
            BlogUnlikeFail: raised if blog like process failed
        Returns:
            BlogRead: blog data
        """
        # Check if user is not already a subscriber
        already_likes = await self.check_like(
            blog_id=blog_id,
            current_user=current_user
        )
        if not already_likes:
            raise BlogNotLiked()
        
        # Delete subscription
        try:
            self.db_session.delete(already_likes)
            self.db_session.commit()
        except Exception:
            raise BlogUnlikeFail()
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
