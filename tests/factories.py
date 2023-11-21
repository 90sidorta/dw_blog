from datetime import datetime, timezone

from dw_blog.models.user import User
from dw_blog.models.common import UserType

import factory.fuzzy

ADMIN_ID = "00000000-0000-0000-0000-000000000001"
ADMIN_EMAIL = "owner@labgears.com"
ADMIN_TOKEN = "0001"


class UserFactory(factory.Factory):
    class Meta:
        model = User

    id = factory.Faker("uuid4")
    nickname = factory.Sequence(lambda n: f"user_nickname_{n}")
    user_type = factory.fuzzy.FuzzyChoice([img_type for img_type in UserType])
    email = factory.Faker("company_email", locale="pl_PL")
    hashed_password = factory.Faker("uuid4")
    description = factory.FuzzyText(prefix='Desc', length=20)
