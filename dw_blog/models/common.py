from enum import Enum


class UserType(str, Enum):
    author = "author"
    regular = "regular"
