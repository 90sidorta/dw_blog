from datetime import datetime, timezone

import factory.fuzzy

from dw_blog.models.blog import Blog
from dw_blog.models.common import UserType
from dw_blog.models.tag import Tag
from dw_blog.models.user import User
from dw_blog.models.category import Category

ADMIN_ID = "00000000-0000-0000-0000-000000000001"
ADMIN_EMAIL = "owner@labgears.com"
ADMIN_TOKEN = "0001"


class UserFactory(factory.Factory):
    class Meta:
        model = User

    id = factory.Faker("uuid4")
    nickname = factory.Sequence(lambda n: f"user_nickname_{n}")
    user_type = factory.fuzzy.FuzzyChoice([user_type for user_type in UserType])
    email = factory.Faker("company_email", locale="pl_PL")
    password = "$2b$12$oeSFt.wxV0piPYVUiDY.eeBaMfkJHwOt6BZOj4Wsno1kvkee0be6C"
    description = factory.fuzzy.FuzzyText(prefix="Desc", length=20)


class TagFactory(factory.Factory):
    class Meta:
        model = Tag

    id = factory.Faker("uuid4")
    name = factory.Sequence(lambda n: f"#tag_name_{n}")
    blog_id = None


class CategoryFactory(factory.Factory):
    class Meta:
        model = Category

    id = factory.Faker("uuid4")
    name = factory.Sequence(lambda n: f"Category_name_{n}")
    date_created = datetime.now()
    date_modified = datetime.now()
    blogs = []


class BlogFactory(factory.Factory):
    class Meta:
        model = Blog

    id = factory.Faker("uuid4")
    archived = False
    date_created = datetime.now()
    date_modified = datetime.now()
    name = factory.Sequence(lambda n: f"blog_name_{n}")
    authors = factory.List([factory.SubFactory(UserFactory)])
    likers = factory.List([factory.SubFactory(UserFactory)])
    subscribers = factory.List([factory.SubFactory(UserFactory)])
    categories = factory.List([factory.SubFactory(CategoryFactory)])
    tags = []


# factory.fuzzy.FuzzyInteger(1,5)
# factory.fuzzy.FuzzyInteger(1,5)
# factory.fuzzy.FuzzyInteger(1,5)
