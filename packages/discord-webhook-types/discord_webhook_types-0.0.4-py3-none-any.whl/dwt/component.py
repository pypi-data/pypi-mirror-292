from enum import IntEnum
from typing import NotRequired, TypedDict


# TODO: all of this


class ComponentType(IntEnum):
    ActionRow = 1
    Button = 2
    StringSelect = 3
    TextInput = 4
    UserSelect = 5
    RoleSelect = 6
    MentionableSelect = 7
    ChannelSelect = 8


class Component(TypedDict):
    pass
