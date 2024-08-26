from enum import Enum
from typing import Literal, NotRequired, TypedDict

AllowedMentionType = Literal["roles", "users", "everyone"]


class AllowedMention(TypedDict):
    parse: list[AllowedMentionType]
    roles: list[int]
    users: list[int]
    replied_user: bool
